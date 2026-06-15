import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from core.rag import get_jd_context
from core.skill_gap import extract_skills

load_dotenv(Path(__file__).parent.parent / ".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BASE_CV = """
SRIKAR KODI
Python Developer & AI/ML Engineer
kodisrikar@gmail.com | +49-1634218928 | Berlin, Germany
linkedin.com/in/srikar-kodi-046a631b2/ | github.com/Namidok

EDUCATION
MSc Computer Science — Big Data & Artificial Intelligence
SRH University of Applied Sciences, Berlin | Oct 2025 - Present

Bachelor in Electronics and Communication
MVGR College of Engineering, Hyderabad | 2016 - 2020

EXPERIENCE
Application Developer | Vavili Technologies | 05/2023 - 08/2025 | Hyderabad
- Reduced page load time by 40% by rebuilding 12 microservices for templeswiki.com as Full Stack Developer, improving user retention across 100K+ monthly visitors
- Increased user engagement by 35% by developing NLP-powered chatbot that automated customer interactions and reduced support queries by 50%
- Accelerated content translation by 60% by building Python ETL pipeline generating multi-language labels across 5 languages for 200K+ dataset entries
- Improved release quality by 45% by leading 4-person QA team designing test plans covering 300+ test cases and building in-house attendance tool

Trainee Software Engineer | ValueLabs | 01/2022 - 02/2023 | Hyderabad
- Improved application performance by 25% by identifying and resolving 60+ bugs across 3 software modules in close collaboration with cross-functional teams
- Increased test coverage by 30% by designing and executing detailed test plans covering 150+ manual test cases across core application functionalities

PROJECTS
SkillSync — AI-powered job application tracker
Stack: Python, FastAPI, React, Tailwind CSS, NLP, AWS EC2, Nginx
- Built NLP skill extractor covering 60+ tech skills from job descriptions
- Implemented session-based data isolation via UUID headers on FastAPI backend
- Deployed on AWS EC2 with Nginx reverse proxy and systemd process management

CoverCraft — RAG-powered cover letter and CV generator
Stack: LangChain, ChromaDB, FastAPI, Groq API, AWS EC2
- Built RAG pipeline with ChromaDB vector store and HuggingFace embeddings
- Generates ATS-optimised CVs and tailored cover letters per job description

SKILLS
Languages: Python, JavaScript, SQL, HTML, CSS, Node.js
AI/ML: NLP, PyTorch, TensorFlow, LangChain, RAG, Embeddings, ChromaDB, Pandas, NumPy, PySpark
Frameworks: FastAPI, Flask, Django, React JS
Cloud & DevOps: AWS (EC2, S3, Lambda, ECR, ECS), Docker, Nginx, GitHub Actions
Databases: PostgreSQL, ChromaDB, Redis
Languages: English (Fluent), German A2 (Learning B2)
"""


def generate_custom_cv(company: str, role: str, jd_text: str) -> str:
    """
    Generate an ATS-optimised CV tailored to a specific JD.
    Rewrites experience bullets in Google XYZ format with JD keywords.
    """
    jd_chunks = get_jd_context(company, "requirements skills responsibilities", n=5)
    jd_context = "\n".join(jd_chunks) if jd_chunks else jd_text[:1500]
    jd_skills = extract_skills(jd_text)

    prompt = f"""You are an expert ATS optimization specialist. Rewrite Srikar Kodi's CV to be perfectly tailored for this specific role.

BASE CV:
{BASE_CV}

JOB DESCRIPTION CONTEXT:
{jd_context}

KEY SKILLS FROM JD: {", ".join(jd_skills)}

COMPANY: {company}
ROLE: {role}

Rewrite the CV following these rules:

1. HEADER — Keep name, contact details exactly as is
2. SUMMARY — Add a 2-line professional summary at the top targeting this specific role at {company}
3. SKILLS — Reorder skills to prioritise ones mentioned in the JD. Add any JD keywords Srikar genuinely has.
4. EXPERIENCE — Rewrite ALL bullet points in strict Google XYZ format:
   "Accomplished [X] as measured by [Y] by doing [Z]"
   - Inject relevant JD keywords naturally into bullets
   - Keep all real metrics (40%, 35%, 60%, 45%, 25%, 30%)
   - Every bullet must start with a strong action verb
5. PROJECTS — Reorder to put most relevant project first. Add JD keywords to descriptions.
6. EDUCATION — Keep exactly as is

ATS RULES:
- Use standard section headers: SUMMARY, EXPERIENCE, EDUCATION, SKILLS, PROJECTS
- No tables, no columns, no special characters except bullets (-)
- NEVER spell out numbers — always use digits and % symbol (e.g. "40%", "60%", "12 microservices")
- NEVER expand common tech abbreviations like UUID, EC2, AWS, API, CI/CD, NLP, RAG, ETL
- Use RAG not "Retrieval Augmented Generation", use CI/CD not "Continuous Integration..."
- Include exact keyword phrases from the JD naturally
- Plain text format only
- Keep bullet points concise — max 2 lines each

Output the complete rewritten CV. Nothing else."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.4,
    )

    return response.choices[0].message.content