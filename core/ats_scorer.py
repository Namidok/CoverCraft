"""
ATS Score Calculator — scores a CV against a JD.
Focuses on real tech skills and job-specific terms only.
"""
import re
from typing import Dict, List
from core.skill_gap import SKILL_PATTERNS, extract_skills

STANDARD_SECTIONS = [
    "experience", "education", "skills", "projects",
    "summary", "objective",
]

STRONG_ACTION_VERBS = [
    "accomplished", "achieved", "accelerated", "built", "created", "decreased",
    "delivered", "deployed", "designed", "developed", "drove", "eliminated",
    "enhanced", "exceeded", "generated", "grew", "implemented", "improved",
    "increased", "launched", "led", "managed", "optimised", "optimized",
    "reduced", "resolved", "scaled", "shipped", "streamlined", "transformed",
]

# Job-specific terms worth matching (beyond tech skills)
JOB_TERMS = [
    "machine learning", "deep learning", "neural network", "computer vision",
    "natural language", "data pipeline", "data engineering", "data science",
    "software engineering", "backend", "frontend", "full stack", "fullstack",
    "microservices", "api", "rest", "graphql", "cloud native", "serverless",
    "distributed systems", "scalable", "production", "deployment", "mlops",
    "devops", "agile", "scrum", "ci/cd", "test driven", "object oriented",
    "functional programming", "system design", "architecture",
]


def score_keywords(cv_text: str, jd_text: str) -> Dict:
    """
    Score keyword match using only real tech skills and job terms.
    Not generic English words.
    """
    # Extract real tech skills from JD
    jd_skills = set(extract_skills(jd_text))

    # Extract job-specific terms from JD
    jd_lower = jd_text.lower()
    jd_terms = set()
    for term in JOB_TERMS:
        if term in jd_lower:
            jd_terms.add(term)

    # Combine — only real meaningful keywords
    all_jd_keywords = jd_skills | jd_terms

    if not all_jd_keywords:
        return {
            "score": 85,
            "matched_count": 0,
            "total_jd_words": 0,
            "top_missing": [],
            "note": "No specific tech keywords detected in JD"
        }

    # Check which ones are in CV
    cv_lower = cv_text.lower()
    matched = set()
    missing = set()

    for kw in all_jd_keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, cv_lower):
            matched.add(kw)
        else:
            missing.add(kw)

    score = round(len(matched) / len(all_jd_keywords) * 100) if all_jd_keywords else 85

    return {
        "score": min(score, 100),
        "matched_count": len(matched),
        "total_jd_words": len(all_jd_keywords),
        "matched_keywords": sorted(matched),
        "top_missing": sorted(missing)[:8],
    }


def score_sections(cv_text: str) -> Dict:
    cv_lower = cv_text.lower()
    found = [s for s in STANDARD_SECTIONS if s in cv_lower]
    score = round(len(found) / 4 * 100)
    return {
        "score": min(score, 100),
        "found_sections": found,
        "missing_sections": [s for s in ["experience", "education", "skills", "summary"]
                             if s not in cv_lower],
    }


def score_action_verbs(cv_text: str) -> Dict:
    cv_lower = cv_text.lower()
    found = [v for v in STRONG_ACTION_VERBS if v in cv_lower]
    score = min(len(found) * 10, 100)
    return {
        "score": score,
        "found_verbs": found[:8],
        "suggestion": "Add more action verbs" if score < 70 else "Good use of action verbs",
    }


def score_format(cv_text: str) -> Dict:
    issues = []
    if "\\|" in cv_text:
        issues.append("table separators detected")
    if "colspan" in cv_text.lower() or "rowspan" in cv_text.lower():
        issues.append("HTML table elements detected")
    score = 100 if not issues else max(0, 100 - len(issues) * 20)
    return {
        "score": score,
        "issues": issues,
        "suggestion": "Format is ATS-friendly" if not issues else "Issues: " + ", ".join(issues),
    }


def score_length(cv_text: str) -> Dict:
    words = len(cv_text.split())
    if 400 <= words <= 900:
        score = 100
        suggestion = "Ideal length"
    elif words < 400:
        score = 70
        suggestion = f"Too short ({words} words). Aim for 400-900 words."
    else:
        score = 85
        suggestion = f"Slightly long ({words} words). Consider trimming."
    return {"score": score, "word_count": words, "suggestion": suggestion}


def calculate_ats_score(cv_text: str, jd_text: str) -> Dict:
    keywords = score_keywords(cv_text, jd_text)
    sections = score_sections(cv_text)
    verbs = score_action_verbs(cv_text)
    format_score = score_format(cv_text)
    length = score_length(cv_text)

    overall = round(
        keywords["score"] * 0.40 +
        sections["score"] * 0.20 +
        verbs["score"] * 0.20 +
        format_score["score"] * 0.10 +
        length["score"] * 0.10
    )

    grade = "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 55 else "D"

    improvements = []
    if keywords["score"] < 80 and keywords.get("top_missing"):
        improvements.append(f"Add these tech keywords from the JD: {', '.join(keywords['top_missing'][:5])}")
    if sections["score"] < 80:
        improvements.append(f"Add missing sections: {', '.join(sections['missing_sections'])}")
    if verbs["score"] < 70:
        improvements.append("Start more bullet points with strong action verbs")
    if format_score["score"] < 100:
        improvements.append(format_score["suggestion"])
    if length["score"] < 100:
        improvements.append(length["suggestion"])

    return {
        "overall": overall,
        "grade": grade,
        "breakdown": {
            "keywords": keywords,
            "sections": sections,
            "action_verbs": verbs,
            "format": format_score,
            "length": length,
        },
        "improvements": improvements,
    }
