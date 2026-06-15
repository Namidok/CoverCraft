import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from core.rag import get_cv_context, get_jd_context

load_dotenv(Path(__file__).parent.parent / ".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SRIKAR_PROFILE = """
Name: Srikar Kodi
Email: kodisrikar@gmail.com
Phone: +49-1634218928
Location: Berlin, Germany
LinkedIn: linkedin.com/in/srikar-kodi-046a631b2/
GitHub: github.com/Namidok

Education:
- MSc Computer Science (Big Data & AI), SRH University of Applied Sciences, Berlin (Oct 2025 - Present)
- Bachelor in Electronics & Communication, MVGR College of Engineering (2016-2020)

Experience:
- Application Developer, Vavili Technologies (05/2023 - 08/2025)
  - Reduced page load time by 40% rebuilding 12 microservices for templeswiki.com
  - Increased user engagement by 35% with NLP chatbot reducing support queries by 50%
  - Accelerated content translation by 60% with Python ETL pipeline for 5 languages
  - Improved release quality by 45% leading 4-person QA team with 300+ test cases

- Trainee Software Engineer, ValueLabs (01/2022 - 02/2023)
  - Improved application performance by 25% resolving 60+ bugs across 3 modules
  - Increased test coverage by 30% with 150+ manual test cases

Skills:
Python, FastAPI, React, LangChain, RAG, ChromaDB, Docker, AWS (EC2, S3, ECR, ECS),
PostgreSQL, NLP, PyTorch, TensorFlow, Pandas, PySpark, GitHub Actions, Nginx
"""


def generate_cover_letter(company: str, role: str, jd_text: str) -> str:
    """Generate a tailored cover letter using RAG context."""

    cv_chunks = get_cv_context(
        f"experience skills relevant to {role} at {company}", n=4
    )
    jd_chunks = get_jd_context(company, f"requirements skills responsibilities", n=4)

    cv_context = "\n".join(cv_chunks) if cv_chunks else SRIKAR_PROFILE
    jd_context = "\n".join(jd_chunks) if jd_chunks else jd_text[:1000]

    prompt = f"""You are an expert career coach writing a cover letter for Srikar Kodi.

CANDIDATE PROFILE:
{SRIKAR_PROFILE}

ADDITIONAL CV CONTEXT (from RAG):
{cv_context}

JOB DESCRIPTION CONTEXT:
{jd_context}

COMPANY: {company}
ROLE: {role}

Write a tailored, professional cover letter that:
1. Opens with a strong hook specific to {company} and why Srikar is excited about this role
2. Highlights 2-3 most relevant experiences using specific metrics from his background
3. Connects his skills directly to what {company} is looking for in this JD
4. Mentions his availability (October 2026 internship/thesis)
5. Closes with a confident call to action

RULES:
- Maximum 4 paragraphs
- No generic phrases like "I am writing to apply"
- Use specific numbers and achievements
- ATS-friendly language — use keywords from the JD naturally
- Professional but not robotic
- Do NOT include address headers or date — just the body paragraphs
- Write in first person as Srikar

Output only the cover letter body. No subject line, no headers."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.7,
    )

    return response.choices[0].message.content