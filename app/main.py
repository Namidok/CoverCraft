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
from core.pdf_generator import generate_cover_letter_pdf, generate_cv_pdf

app = FastAPI(title="CoverCraft API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class JDRequest(BaseModel):
    company: str
    role: str
    jd_text: str

class GenerateRequest(BaseModel):
    company: str
    role: str
    jd_text: str


@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8")
    chunks = add_cv(text)
    return {"message": f"CV uploaded and indexed into {chunks} chunks."}


@app.post("/upload-cv-text")
async def upload_cv_text(payload: dict):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    chunks = add_cv(text)
    return {"message": f"CV indexed into {chunks} chunks."}


@app.post("/add-jd")
async def add_job_description(request: JDRequest):
    chunks = add_jd(request.jd_text, request.company, request.role)
    gap = analyse_gap(request.jd_text)
    return {
        "message": f"JD indexed into {chunks} chunks.",
        "skill_gap": gap,
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
    ats = calculate_ats_score(text, request.jd_text)
    return {"cv": text, "ats_score": ats}


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
    ats = calculate_ats_score(custom_cv, request.jd_text)

    return {
        "cover_letter": cover_letter,
        "cv": custom_cv,
        "skill_gap": gap,
        "ats_score": ats,
    }


@app.post("/ats-score")
async def ats_score_endpoint(request: GenerateRequest):
    cv_text = generate_custom_cv(
        company=request.company,
        role=request.role,
        jd_text=request.jd_text,
    )
    ats = calculate_ats_score(cv_text, request.jd_text)
    return {"ats_score": ats, "cv": cv_text}


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
    gap = analyse_gap(request.jd_text)
    return gap


@app.get("/health")
async def health():
    return {"status": "ok", "service": "CoverCraft"}
