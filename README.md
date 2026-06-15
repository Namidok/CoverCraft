# CoverCraft

AI-powered cover letter and CV generator. Paste a job description, get a tailored cover letter and ATS-optimised CV in seconds.

Built with a RAG pipeline — your CV is the knowledge base, the JD is the query. Every output is specific to the company and role.

---

## What it does

- **Skill gap analysis** — extracts tech skills from the JD and shows exactly what you match and what you're missing
- **Tailored cover letter** — generated using RAG context from your CV and the JD. Company-specific, not generic
- **ATS-optimised CV** — rewrites your CV with JD keywords injected naturally. Experience in Google XYZ format with real metrics
- **ATS score** — scores the generated CV across 5 dimensions: keywords, sections, action verbs, format, length
- **PDF download** — clean, ATS-friendly PDFs for both documents

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| RAG | LangChain, ChromaDB |
| Embeddings | HuggingFace sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Groq API + Llama 3.3 70B |
| Frontend | React, Vite, Tailwind CSS |
| PDF Generation | ReportLab |
| Deployment | AWS EC2, Docker |

---

## How it works

```
User pastes JD →
  FastAPI indexes JD into ChromaDB →
    Skill gap analysis runs against your profile →
      User clicks Generate →
        RAG retrieves relevant CV + JD chunks →
          Groq generates cover letter + ATS CV →
            ATS scorer evaluates the CV →
              PDFs generated and ready to download
```

---

## Running locally

### Backend

```bash
git clone https://github.com/Namidok/CoverCraft.git
cd CoverCraft

/opt/homebrew/bin/python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

Start the backend:
```bash
GROQ_API_KEY=your_key uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3001`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/add-jd` | Index JD + return skill gap |
| POST | `/generate-all` | Generate cover letter + CV + ATS score |
| POST | `/generate-cover-letter` | Cover letter only |
| POST | `/generate-cv` | ATS CV only |
| POST | `/download-cover-letter-pdf` | Cover letter as PDF |
| POST | `/download-cv-pdf` | ATS CV as PDF |
| POST | `/skill-gap` | Skill gap analysis only |
| POST | `/ats-score` | ATS score only |
| GET | `/health` | Health check |

---

## ATS Scoring

The ATS scorer evaluates the generated CV across 5 dimensions:

| Dimension | Weight | What it checks |
|-----------|--------|----------------|
| Keywords | 40% | Tech skills from JD present in CV |
| Sections | 20% | Standard headers (Summary, Experience, Education, Skills) |
| Action Verbs | 20% | Strong verbs starting bullet points |
| Format | 10% | No ATS-killing elements (tables, special chars) |
| Length | 10% | 400-900 words optimal |

Scores 85+ = Grade A, 70+ = Grade B, 55+ = Grade C

---

## Project Structure

```
CoverCraft/
├── app/
│   └── main.py              FastAPI routes
├── core/
│   ├── rag.py               ChromaDB vector store + HuggingFace embeddings
│   ├── cover_letter.py      RAG-powered cover letter generator
│   ├── cv_generator.py      ATS-optimised CV generator
│   ├── skill_gap.py         Tech skill extractor + gap analysis
│   ├── ats_scorer.py        ATS score calculator
│   └── pdf_generator.py     ReportLab PDF renderer
├── frontend/
│   ├── src/
│   │   ├── components/      StepIndicator, SkillBadge
│   │   ├── steps/           Step1-4 wizard components
│   │   └── hooks/           useCoverCraft
│   └── vite.config.js
├── data/
│   └── chromadb/            Persistent vector store
├── requirements.txt
└── .env                     GROQ_API_KEY (never push to GitHub)
```

---

*Built by Srikar Kodi · 2026*
