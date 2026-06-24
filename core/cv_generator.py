"""
ATS-Friendly CV Generator — uses user's uploaded CV from ChromaDB.
"""
import os
import re
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from core.rag import get_jd_context, get_cv_context
from core.skill_gap import extract_skills

load_dotenv(Path(__file__).parent.parent / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def clean_context(text: str) -> str:
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'<\|.*?\|>', '', text)
    return text[:4000]


def generate_custom_cv(company: str, role: str, jd_text: str, user_id: str = "default") -> str:
    cv_chunks = get_cv_context("experience education skills projects", n=8, user_id=user_id)
    jd_chunks = get_jd_context(company, "requirements skills responsibilities", n=5, user_id=user_id)

    cv_context = clean_context("\n".join(cv_chunks)) if cv_chunks else ""
    jd_context = clean_context("\n".join(jd_chunks)) if jd_chunks else jd_text[:1500]
    jd_skills = extract_skills(jd_text)

    if not cv_context:
        return "Please upload your CV first before generating a tailored CV."

    prompt = f"""You are an expert ATS optimization specialist. Rewrite the candidate's CV to be perfectly tailored for this specific role.

CANDIDATE CV CONTENT:
{cv_context}

JOB DESCRIPTION CONTEXT:
{jd_context}

KEY SKILLS FROM JD: {", ".join(jd_skills)}

COMPANY: {company}
ROLE: {role}

Rewrite the CV following these rules:

1. HEADER — Keep the candidate's name and contact details exactly as they appear in their CV
2. SUMMARY — Add a 2-line professional summary targeting this specific role at {company}
3. SKILLS — Reorder skills to prioritise ones mentioned in the JD. Group by category if possible (e.g., "Languages & Frameworks: Python, FastAPI...")
4. EXPERIENCE — Format each entry STRICTLY like this:
   Job Title | Month Year – Month Year
   Company, Location
   • Bullet point in Google XYZ format: "Accomplished [X] as measured by [Y] by doing [Z]"
   • Inject relevant JD keywords naturally
   • Keep all real metrics from the original CV
   • Every bullet must start with a strong action verb
5. PROJECTS — Format each entry STRICTLY like this:
   Project Name | Year – Year
   Description / Link
   • Bullet point...
6. EDUCATION — Format each entry STRICTLY like this:
   Degree Name | Start Year – End Year
   Institution, Location
   • Relevant coursework bullet (optional)

CRITICAL FORMATTING RULES:
- Standard section headers in ALL CAPS: SUMMARY, EXPERIENCE, PROJECTS, EDUCATION, SKILLS
- Job title and dates MUST be on the SAME line separated by " | "
- Company/institution MUST be on the line immediately after the title+dates line
- NEVER put dates on separate lines from the job title
- No tables, no columns, no special characters except bullets (-)
- NEVER spell out numbers — always use digits and % symbol
- NEVER add skills the candidate does not have
- Plain text format only

Output the complete rewritten CV. Nothing else."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.4,
    )
    return response.choices[0].message.content
