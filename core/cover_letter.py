"""
Cover Letter Generator — RAG + Groq LLM
Uses user's uploaded CV as context.
"""
import os
import re
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from core.rag import get_cv_context, get_jd_context

load_dotenv(Path(__file__).parent.parent / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def clean_context(text: str) -> str:
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'<\|.*?\|>', '', text)
    return text[:3000]


def generate_cover_letter(company: str, role: str, jd_text: str, user_id: str = "default", lang: str = "en") -> str:
    cv_chunks = get_cv_context(f"experience skills relevant to {role} at {company}", n=5, user_id=user_id)
    jd_chunks = get_jd_context(company, "requirements skills responsibilities", n=4, user_id=user_id)

    cv_context = clean_context("\n".join(cv_chunks)) if cv_chunks else ""
    jd_context = clean_context("\n".join(jd_chunks)) if jd_chunks else jd_text[:1500]

    if not cv_context:
        return "Please upload your CV first before generating a cover letter."

    lang_instruction = "Write the ENTIRE cover letter in German (Deutsch). Use formal Sie form and professional German business language." if lang == "de" else "Write in English."

    prompt = f"""You are an expert career coach writing a tailored cover letter.

CANDIDATE CV CONTEXT:
{cv_context}

JOB DESCRIPTION CONTEXT:
{jd_context}

COMPANY: {company}
ROLE: {role}

Write a tailored, professional cover letter that:
1. Opens with a strong hook specific to {company} and this role
2. Highlights 2-3 most relevant experiences with specific metrics from the CV
3. Connects their skills directly to what {company} is looking for
4. Closes with a confident call to action

RULES:
- Maximum 4 paragraphs
- No generic phrases like "I am writing to apply"
- Use specific numbers and achievements from the CV
- ATS-friendly — use keywords from the JD naturally
- Professional but not robotic
- Do NOT include address headers, date, or placeholders like [Your Name]
- Write in first person
- Output only the cover letter body. Nothing else.
- LANGUAGE: {lang_instruction}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content
