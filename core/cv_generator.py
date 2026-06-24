"""
ATS-Friendly CV Generator — European format matching SrikarKodi.pdf style
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


def generate_custom_cv(company: str, role: str, jd_text: str, user_id: str = "default", lang: str = "en") -> str:
    cv_chunks = get_cv_context("experience education skills projects summary", n=8, user_id=user_id)
    jd_chunks = get_jd_context(company, "requirements skills responsibilities", n=5, user_id=user_id)

    cv_context = clean_context("\n".join(cv_chunks)) if cv_chunks else ""
    jd_context = clean_context("\n".join(jd_chunks)) if jd_chunks else jd_text[:1500]
    jd_skills = extract_skills(jd_text)

    if not cv_context:
        return "Please upload your CV first before generating a tailored CV."

    cv_lang_instruction = "Write the ENTIRE CV in German (Deutsch). ALL section headers (PROFIL, ERFAHRUNG, PROJEKTE, AUSBILDUNG, FÄHIGKEITEN), bullet points and descriptions MUST be in German." if lang == "de" else "Write in English."

    prompt = f"""You are a professional European CV writer. Rewrite this candidate's CV tailored for {role} at {company}.

CANDIDATE CV:
{cv_context}

JOB REQUIREMENTS:
{jd_context}

KEY SKILLS FROM JD: {", ".join(jd_skills[:15])}

OUTPUT THE CV IN EXACTLY THIS FORMAT — no deviations:

[FULL NAME FROM CV]
[Professional Title] • [Specialty] • [Specialty]
[email] | [phone] | [City, Country]
[linkedin url] | [github url]

PROFILE
[3-4 sentences. Mention {company} specifically. Use keywords from JD. Reference real projects from CV. No generic phrases.]

EXPERIENCE

[Job Title] [Mon YYYY – Mon YYYY]
[Company Name] [City, Country]
- [Strong action verb + specific achievement + metric]
- [Strong action verb + specific achievement + metric]
- [Strong action verb + specific achievement + metric]

[Job Title] [Mon YYYY – Mon YYYY]
[Company Name] [City, Country]
- [Achievement with metric]
- [Achievement with metric]

PROJECTS

[Project Name] – [Short Description] [YYYY – Present]
[URL] | Live in Production
- [What it does, tech stack used]
- [Key metric or real-world impact]

EDUCATION

[Degree Name] [Mon YYYY – Mon YYYY]
[University Name] [City, Country]
- [Relevant coursework if applicable]

[Degree Name] [YYYY – YYYY]
[University Name] [Country]

SKILLS

Languages & Frameworks: [comma separated from CV, prioritise JD matches]
AI & ML: [comma separated from CV]
Infrastructure: [comma separated from CV]
Languages: [spoken languages from CV with levels]

STRICT RULES:
- Use ONLY real information from the candidate's CV — never invent
- Job title and date on SAME LINE separated by spaces (no pipe separator between them)
- Company name and location on the line BELOW the job title
- Dates format: Mon YYYY – Mon YYYY (e.g. May 2023 – Aug 2025) or YYYY – YYYY for education
- Every bullet starts with a past tense action verb
- Every bullet has a specific number, %, or metric
- NEVER use "responsible for", "helped with", "assisted in"
- NEVER add skills the candidate does not have
- No photo, age, nationality, marital status (European ATS standard)
- Skills section at the BOTTOM
- Output ONLY the CV. No explanation, no preamble."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.3,
    )
    result = response.choices[0].message.content
    print("=== RAW CV OUTPUT ===\n" + result + "\n=== END ===")
    return result
