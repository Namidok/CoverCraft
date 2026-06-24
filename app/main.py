"""
CoverCraft API — FastAPI backend
Per-user CV storage in Supabase + ChromaDB
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path
from supabase import create_client

load_dotenv(Path(__file__).parent.parent / ".env")

from core.rag import add_cv, add_jd, get_cv_context
from core.cover_letter import generate_cover_letter
from core.cv_generator import generate_custom_cv
from core.skill_gap import analyse_gap
from core.ats_scorer import calculate_ats_score
from core.jd_parser import parse_jd
from core.pdf_generator import generate_cover_letter_pdf, generate_cv_pdf

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

app = FastAPI(title="CoverCraft API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory JD cache
jd_cache = {}


def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def get_user_id(authorization: str = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.replace("Bearer ", "")
    try:
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        client = create_client(SUPABASE_URL, anon_key)
        user = client.auth.get_user(token)
        return user.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


class JDRequest(BaseModel):
    company: str
    role: str
    jd_text: str

class GenerateRequest(BaseModel):
    company: str
    role: str
    jd_text: str


def get_user_cv(user_id: str) -> str:
    """Fetch user's CV text from Supabase."""
    try:
        client = get_supabase()
        res = client.table("user_profiles").select("cv_text").eq("id", user_id).single().execute()
        return res.data.get("cv_text", "") if res.data else ""
    except:
        return ""


def save_user_cv(user_id: str, cv_text: str, filename: str = ""):
    """Save user's CV text to Supabase."""
    client = get_supabase()
    existing = client.table("user_profiles").select("id").eq("id", user_id).execute()
    if existing.data:
        client.table("user_profiles").update({
            "cv_text": cv_text,
            "cv_filename": filename,
            "cv_uploaded": True,
        }).eq("id", user_id).execute()
    else:
        client.table("user_profiles").insert({
            "id": user_id,
            "cv_text": cv_text,
            "cv_filename": filename,
            "cv_uploaded": True,
        }).execute()


def save_document(user_id: str, company: str, role: str, cover_letter: str, cv_text: str, ats_score: dict, jd_text: str = ""):
    """Save generated documents to Supabase."""
    try:
        client = get_supabase()
        client.table("documents").insert({
            "user_id": user_id,
            "company": company,
            "role": role,
            "cover_letter": cover_letter,
            "cv_text": cv_text,
            "ats_score": ats_score,
            "jd_text": jd_text,
        }).execute()
    except Exception as e:
        print(f"Failed to save document: {e}")


@app.post("/upload-cv-pdf")
async def upload_cv_pdf(
    file: UploadFile = File(...),
    authorization: str = Header(default=None)
):
    user_id = get_user_id(authorization)
    import fitz
    import re
    content = await file.read()
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text")
        doc.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read PDF: {str(e)}")

    # Clean text
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'[^\x20-\x7e\n\r\t\u00c0-\u024f]', '', text)
    clean_lines = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        printable = sum(1 for c in line if c.isprintable())
        if printable / len(line) > 0.85:
            clean_lines.append(line)
    text = '\n'.join(clean_lines).strip()

    if not text or len(text) < 100:
        raise HTTPException(status_code=400, detail="Could not extract readable text from PDF.")

    # Save to Supabase
    save_user_cv(user_id, text, file.filename)

    # Index into ChromaDB with user-specific collection
    chunks = add_cv(text, user_id=user_id)
    return {"message": f"CV uploaded and indexed into {chunks} chunks.", "preview": text[:200]}


@app.post("/upload-cv-text")
async def upload_cv_text(
    payload: dict,
    authorization: str = Header(default=None)
):
    user_id = get_user_id(authorization)
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    save_user_cv(user_id, text)
    chunks = add_cv(text, user_id=user_id)
    return {"message": f"CV indexed into {chunks} chunks."}


@app.post("/add-jd")
async def add_job_description(
    request: JDRequest,
    authorization: str = Header(default=None)
):
    user_id = get_user_id(authorization)

    # If CV not in ChromaDB yet, reload from Supabase
    cv_text = get_user_cv(user_id)
    if cv_text:
        add_cv(cv_text, user_id=user_id)

    chunks = add_jd(request.jd_text, request.company, request.role, user_id=user_id)
    jd_parsed = parse_jd(request.jd_text, request.company, request.role)
    cache_key = f"{user_id}_{request.company}_{request.role}"
    jd_cache[cache_key] = jd_parsed
    gap = analyse_gap(request.jd_text)

    return {
        "message": f"JD indexed into {chunks} chunks.",
        "skill_gap": gap,
        "jd_parsed": jd_parsed,
    }


@app.post("/generate-all")
async def generate_all(
    request: GenerateRequest,
    authorization: str = Header(default=None)
):
    user_id = get_user_id(authorization)

    # Reload CV from Supabase if needed
    cv_text = get_user_cv(user_id)
    if cv_text:
        add_cv(cv_text, user_id=user_id)

    cover_letter = generate_cover_letter(
        company=request.company,
        role=request.role,
        jd_text=request.jd_text,
        user_id=user_id,
    )
    custom_cv = generate_custom_cv(
        company=request.company,
        role=request.role,
        jd_text=request.jd_text,
        user_id=user_id,
    )
    gap = analyse_gap(request.jd_text)
    cache_key = f"{user_id}_{request.company}_{request.role}"
    jd_parsed = jd_cache.get(cache_key)
    ats = calculate_ats_score(custom_cv, request.jd_text, jd_parsed)

    # Save to Supabase
    save_document(user_id, request.company, request.role, cover_letter, custom_cv, ats, request.jd_text)

    return {
        "cover_letter": cover_letter,
        "cv": custom_cv,
        "skill_gap": gap,
        "ats_score": ats,
        "jd_parsed": jd_parsed,
    }


@app.post("/download-cover-letter-pdf")
async def download_cover_letter_pdf(
    request: GenerateRequest,
    authorization: str = Header(default=None)
):
    user_id = get_user_id(authorization)
    cv_text = get_user_cv(user_id)
    if cv_text:
        add_cv(cv_text, user_id=user_id)

    text = generate_cover_letter(
        company=request.company,
        role=request.role,
        jd_text=request.jd_text,
        user_id=user_id,
    )
    pdf_bytes = generate_cover_letter_pdf(text, request.company, request.role)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=cover_letter_{request.company}.pdf"},
    )


@app.post("/download-cv-pdf")
async def download_cv_pdf(
    request: GenerateRequest,
    authorization: str = Header(default=None)
):
    user_id = get_user_id(authorization)
    cv_text = get_user_cv(user_id)
    if cv_text:
        add_cv(cv_text, user_id=user_id)

    text = generate_custom_cv(
        company=request.company,
        role=request.role,
        jd_text=request.jd_text,
        user_id=user_id,
    )
    pdf_bytes = generate_cv_pdf(text)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=cv_{request.company}.pdf"},
    )


@app.post("/skill-gap")
async def skill_gap_endpoint(request: GenerateRequest):
    return analyse_gap(request.jd_text)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "CoverCraft"}


@app.post("/download-cover-letter-pdf-de")
async def download_cover_letter_pdf_de(
    request: GenerateRequest,
    authorization: str = Header(default=None)
):
    user_id = get_user_id(authorization)
    cv_text = get_user_cv(user_id)
    if cv_text:
        add_cv(cv_text, user_id=user_id)

    text = generate_cover_letter(
        company=request.company,
        role=request.role,
        jd_text=request.jd_text,
        user_id=user_id,
        lang="de",
    )
    pdf_bytes = generate_cover_letter_pdf(text, request.company, request.role)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=cover_letter_{request.company}_DE.pdf"},
    )


@app.post("/download-cv-pdf-de")
async def download_cv_pdf_de(
    request: GenerateRequest,
    authorization: str = Header(default=None)
):
    user_id = get_user_id(authorization)
    cv_text = get_user_cv(user_id)
    if cv_text:
        add_cv(cv_text, user_id=user_id)

    text = generate_custom_cv(
        company=request.company,
        role=request.role,
        jd_text=request.jd_text,
        user_id=user_id,
        lang="de",
    )
    pdf_bytes = generate_cv_pdf(text)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=cv_{request.company}_DE.pdf"},
    )
