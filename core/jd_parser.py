"""
JD Parser — extracts structured requirements from job descriptions.
Uses Groq to intelligently parse required vs preferred skills.
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def parse_jd(jd_text: str, company: str, role: str) -> dict:
    """
    Parse a JD into structured requirements using LLM.
    Returns required skills, preferred skills, job title, seniority.
    """
    prompt = f"""You are a technical recruiter. Parse this job description and extract structured requirements.

JOB DESCRIPTION:
{jd_text}

Extract and return ONLY a valid JSON object with this exact structure:
{{
  "job_title": "exact job title from JD",
  "seniority": "intern/junior/mid/senior",
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1", "skill2"],
  "key_responsibilities": ["responsibility1", "responsibility2"],
  "education_required": "degree requirement if mentioned",
  "languages_required": ["language1"]
}}

RULES:
- required_skills: only hard technical skills explicitly marked as required/must have
- preferred_skills: skills marked as nice to have, plus or preferred
- Keep skills as short lowercase terms: "python" not "Python programming language"
- Maximum 15 required skills, 10 preferred skills
- Only include real tech skills, tools, frameworks — not soft skills
- Return ONLY the JSON, no other text"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()

    try:
        # Clean up common LLM JSON formatting issues
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw.strip())
        parsed["company"] = company
        parsed["role"] = role
        return parsed
    except Exception as e:
        # Fallback to basic extraction
        from core.skill_gap import extract_skills
        skills = extract_skills(jd_text)
        return {
            "job_title": role,
            "seniority": "intern",
            "required_skills": skills[:10],
            "preferred_skills": skills[10:15],
            "key_responsibilities": [],
            "education_required": "",
            "languages_required": [],
            "company": company,
            "role": role,
        }
