"""
CoverCraft API — FastAPI backend
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

from core.rag import add_cv, add_jd
from core.cover_letter import generate_cover_letter
from core.cv_generator import generate_custom_cv
from core.skill_gap import analyse_gap
from core.ats_scorer import calculate_ats_score
from core.jd_parser import parse_jd
from core.pdf_generator import generate_cover_letter_pdf, generate_cv_pdf

app = FastAPI(title="CoverCraft API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory JD cache per session
jd_cache = {}

class JDRequest(BaseModel):
    company: str
    role: str
    jd_text: str

class GenerateRequest(BaseModel):
    company: str
    role: str
    jd_text: str


@app.post("/upload-cv-text")
async def upload_cv_text(payload: dict):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    chunks = add_cv(text)
    return {"message": f"CV indexed into {chunks} chunks."}


@app.post("/add-jd")
async def add_job_description(request: JDRequest):
    # Index into ChromaDB
    chunks = add_jd(request.jd_text, request.company, request.role)

    # Parse JD structure with LLM
    jd_parsed = parse_jd(request.jd_text, request.company, request.role)

    # Cache parsed JD
    cache_key = f"{request.company}_{request.role}"
    jd_cache[cache_key] = jd_parsed

    # Basic skill gap
    gap = analyse_gap(request.jd_text)

    return {
        "message": f"JD indexed into {chunks} chunks.",
        "skill_gap": gap,
        "jd_parsed": jd_parsed,
    }


@app.post("/generate-all")
async def generate_all(request: GenerateRequest):
    cover_letter = generate_cover_letter(
        company=request.company,
        role=request.role,
        jd_text=request.jd_text,
    )
    custom_cv = generate_custom_cv(
        company=request.company,
        role=request.role,
        jd_text=request.jd_text,
    )
    gap = analyse_gap(request.jd_text)

    # Get cached parsed JD or parse now
    cache_key = f"{request.company}_{request.role}"
    jd_parsed = jd_cache.get(cache_key)
    if not jd_parsed:
        jd_parsed = parse_jd(request.jd_text, request.company, request.role)
        jd_cache[cache_key] = jd_parsed

    ats = calculate_ats_score(custom_cv, request.jd_text, jd_parsed)

    return {
        "cover_letter": cover_letter,
        "cv": custom_cv,
        "skill_gap": gap,
        "ats_score": ats,
        "jd_parsed": jd_parsed,
    }


@app.post("/generate-cover-letter")
async def generate_cover_letter_endpoint(request: GenerateRequest):
    text = generate_cover_letter(
        company=request.company,
        role=request.role,
        jd_text=request.jd_text,
    )
    return {"cover_letter": text}


@app.post("/generate-cv")
async def generate_cv_endpoint(request: GenerateRequest):
    text = generate_custom_cv(
        company=request.company,
        role=request.role,
        jd_text=request.jd_text,
    )
    cache_key = f"{request.company}_{request.role}"
    jd_parsed = jd_cache.get(cache_key)
    ats = calculate_ats_score(text, request.jd_text, jd_parsed)
    return {"cv": text, "ats_score": ats}


@app.post("/download-cover-letter-pdf")
async def download_cover_letter_pdf(request: GenerateRequest):
    text = generate_cover_letter(
        company=request.company,
        role=request.role,
        jd_text=request.jd_text,
    )
    pdf_bytes = generate_cover_letter_pdf(text, request.company, request.role)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=cover_letter_{request.company}.pdf"},
    )


@app.post("/download-cv-pdf")
async def download_cv_pdf(request: GenerateRequest):
    text = generate_custom_cv(
        company=request.company,
        role=request.role,
        jd_text=request.jd_text,
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


@app.post("/upload-cv-pdf")
async def upload_cv_pdf(file: UploadFile = File(...)):
    """Upload CV as PDF — extracts text using PyMuPDF."""
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
    
    # Clean the extracted text
    # Remove non-printable characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    # Remove any remaining binary garbage
    text = re.sub(r'[^\x20-\x7e\n\r\t\u00c0-\u024f]', '', text)
    # Remove lines with too many special characters
    clean_lines = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        printable = sum(1 for c in line if c.isprintable())
        if len(line) == 0 or printable / len(line) > 0.85:
            clean_lines.append(line)
    text = '\n'.join(clean_lines).strip()
    
    if not text or len(text) < 100:
        raise HTTPException(status_code=400, detail="Could not extract readable text from PDF. Please try paste text mode.")
    
    chunks = add_cv(text)
    return {"message": f"CV extracted and indexed into {chunks} chunks.", "preview": text[:300]}
