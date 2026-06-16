"""
ATS Score Calculator v2 — scores against structured JD requirements.
Shows clear before/after improvement.
"""
import re
from typing import Dict, List


STRONG_ACTION_VERBS = [
    "accomplished", "achieved", "accelerated", "built", "created", "decreased",
    "delivered", "deployed", "designed", "developed", "drove", "eliminated",
    "enhanced", "exceeded", "generated", "grew", "implemented", "improved",
    "increased", "launched", "led", "managed", "optimised", "optimized",
    "reduced", "resolved", "scaled", "shipped", "streamlined", "transformed",
]

STANDARD_SECTIONS = ["experience", "education", "skills", "summary", "projects"]

YOUR_BASE_SKILLS = [
    "python", "javascript", "sql", "html", "css", "node.js",
    "nlp", "pytorch", "tensorflow", "langchain", "rag", "embeddings",
    "chromadb", "pandas", "numpy", "pyspark", "fastapi", "flask",
    "django", "react", "aws", "ec2", "s3", "lambda", "ecr", "ecs",
    "docker", "nginx", "github actions", "postgresql", "redis", "spacy",
    "etl", "rest api", "agile", "scrum",
]


def check_skill_in_cv(skill: str, cv_text: str) -> bool:
    cv_lower = cv_text.lower()
    pattern = r'\b' + re.escape(skill.lower()) + r'\b'
    return bool(re.search(pattern, cv_lower))


def score_required_skills(cv_text: str, required_skills: List[str]) -> Dict:
    matched = []
    missing = []
    for skill in required_skills:
        if check_skill_in_cv(skill, cv_text):
            matched.append(skill)
        else:
            missing.append(skill)
    total = len(required_skills)
    score = round(len(matched) / total * 100) if total else 100
    return {
        "score": score,
        "matched": matched,
        "missing": missing,
        "total": total,
        "matched_count": len(matched),
    }


def score_preferred_skills(cv_text: str, preferred_skills: List[str]) -> Dict:
    matched = []
    missing = []
    for skill in preferred_skills:
        if check_skill_in_cv(skill, cv_text):
            matched.append(skill)
        else:
            missing.append(skill)
    total = len(preferred_skills)
    score = round(len(matched) / total * 100) if total else 100
    return {
        "score": score,
        "matched": matched,
        "missing": missing,
        "total": total,
        "matched_count": len(matched),
    }


def score_sections(cv_text: str) -> Dict:
    cv_lower = cv_text.lower()
    found = [s for s in STANDARD_SECTIONS if s in cv_lower]
    score = round(len(found) / len(STANDARD_SECTIONS) * 100)
    return {
        "score": min(score, 100),
        "found": found,
        "missing": [s for s in STANDARD_SECTIONS if s not in cv_lower],
    }


def score_action_verbs(cv_text: str) -> Dict:
    cv_lower = cv_text.lower()
    found = [v for v in STRONG_ACTION_VERBS if v in cv_lower]
    score = min(len(found) * 10, 100)
    return {
        "score": score,
        "found": found[:8],
    }


def score_format(cv_text: str) -> Dict:
    issues = []
    if "\\|" in cv_text:
        issues.append("table separators")
    if len(cv_text.split("\n")) < 20:
        issues.append("too few lines — may be too short")
    score = 100 if not issues else 80
    return {"score": score, "issues": issues}


def score_length(cv_text: str) -> Dict:
    words = len(cv_text.split())
    if 400 <= words <= 900:
        score = 100
        note = f"Ideal length ({words} words)"
    elif words < 400:
        score = 65
        note = f"Too short ({words} words). Aim for 400-900."
    else:
        score = 85
        note = f"Slightly long ({words} words)."
    return {"score": score, "word_count": words, "note": note}


def calculate_base_score(jd_parsed: Dict) -> Dict:
    """Score your BASE CV (before optimisation) against JD requirements."""
    base_cv_text = " ".join(YOUR_BASE_SKILLS)

    required = score_required_skills(base_cv_text, jd_parsed.get("required_skills", []))
    preferred = score_preferred_skills(base_cv_text, jd_parsed.get("preferred_skills", []))

    overall = round(
        required["score"] * 0.60 +
        preferred["score"] * 0.20 +
        80 * 0.10 +  # assume decent sections
        80 * 0.10    # assume decent format
    )

    return {
        "overall": overall,
        "required_skills": required,
        "preferred_skills": preferred,
        "label": "Base CV Score",
    }


def calculate_ats_score(cv_text: str, jd_text: str, jd_parsed: Dict = None) -> Dict:
    """
    Calculate ATS score for optimised CV against structured JD requirements.
    """
    if not jd_parsed:
        from core.skill_gap import extract_skills
        skills = extract_skills(jd_text)
        jd_parsed = {
            "required_skills": skills[:10],
            "preferred_skills": skills[10:15],
        }

    required = score_required_skills(cv_text, jd_parsed.get("required_skills", []))
    preferred = score_preferred_skills(cv_text, jd_parsed.get("preferred_skills", []))
    sections = score_sections(cv_text)
    verbs = score_action_verbs(cv_text)
    fmt = score_format(cv_text)
    length = score_length(cv_text)

    overall = round(
        required["score"] * 0.45 +
        preferred["score"] * 0.15 +
        sections["score"] * 0.15 +
        verbs["score"] * 0.15 +
        fmt["score"] * 0.05 +
        length["score"] * 0.05
    )

    grade = "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 55 else "D"

    # Calculate base score for comparison
    base = calculate_base_score(jd_parsed)
    improvement = overall - base["overall"]

    improvements = []
    if required["missing"]:
        improvements.append(f"Missing required skills: {', '.join(required['missing'][:5])}")
    if preferred["missing"]:
        improvements.append(f"Missing preferred skills: {', '.join(preferred['missing'][:4])}")
    if sections["score"] < 80:
        improvements.append(f"Add missing sections: {', '.join(sections['missing'])}")
    if verbs["score"] < 70:
        improvements.append("Use more strong action verbs in bullet points")
    if length["score"] < 100:
        improvements.append(length["note"])

    return {
        "overall": overall,
        "grade": grade,
        "improvement": improvement,
        "base_score": base["overall"],
        "breakdown": {
            "required_skills": required,
            "preferred_skills": preferred,
            "sections": sections,
            "action_verbs": verbs,
            "format": fmt,
            "length": length,
        },
        "improvements": improvements,
    }
