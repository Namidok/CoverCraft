"""
PDF Generator — ATS-friendly CVs and cover letters.
Uses the generated text directly without hardcoded personal info.
"""
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether, Table, TableStyle
)
from reportlab.lib.enums import TA_RIGHT
from io import BytesIO


# ────────────────────────────────
# Cover Letter (unchanged layout)
# ────────────────────────────────

def generate_cover_letter_pdf(text: str, company: str, role: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=25*mm, leftMargin=25*mm,
        topMargin=25*mm, bottomMargin=25*mm
    )

    styles = getSampleStyleSheet()

    label_style = ParagraphStyle(
        "Label", parent=styles["Normal"],
        fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#888888"), spaceAfter=12
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=11, fontName="Helvetica",
        textColor=colors.HexColor("#1a1a1a"), leading=18, spaceAfter=12
    )

    story = []
    story.append(Paragraph(f"Cover Letter — {role} at {company}", label_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=12))

    for para in text.strip().split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip().replace("\n", " "), body_style))

    doc.build(story)
    return buffer.getvalue()


# ────────────────────────────────
# CV — Matches SrikarKodi.pdf style
# ────────────────────────────────

# Regex for detecting dates in a line
DATE_RE = re.compile(
    r'(?:\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\b[\s.]+\d{4})'
    r'|(?:\b(?:Present|Now|Current|Ongoing)\b)'
    r'|(?:\b20\d{2}\b)',
    re.IGNORECASE
)

CONTACT_MARKERS = ["@", "linkedin", "github", "gmail", "phone", "tel", "+", "http", "www", ".com", ".dev", "location", "email", "contact"]
SECTION_HEADERS = {"profile", "summary", "experience", "work", "employment", "projects", "education", "skills", "certifications", "languages"}


def _has_date(line: str) -> bool:
    return bool(DATE_RE.search(line))


def _is_contact_line(line: str) -> bool:
    lower = line.lower()
    return any(m in lower for m in CONTACT_MARKERS) or "|" in line and any(m in lower for m in ["linkedin", "github", "email", "phone"])


def _is_section_header(line: str) -> bool:
    clean = line.strip().lower().rstrip(":")
    if clean in SECTION_HEADERS:
        return True
    if line.isupper() and 2 < len(line) < 35 and not line.endswith((".", ",", ";")):
        return True
    return False


def _is_date_only_line(line: str) -> bool:
    """True if the line is basically just a date (or two dates with a dash)."""
    if not line:
        return False
    # Strip common separators and see if what's left is mostly date-like
    stripped = re.sub(r'[\s–—\-|–—-]', ' ', line).strip()
    # If it has a date and is short, it's probably a date-only line
    return _has_date(line) and len(line) < 60


def _extract_dates(line: str) -> list:
    """Extract all date strings from a line."""
    return DATE_RE.findall(line)


def _combine_dates(date1: str, date2: str) -> str:
    """Combine two dates into a range. Try to put the earlier one first."""
    # Very simple heuristic: if one contains "Present", it's the end date
    d1_lower = date1.lower()
    d2_lower = date2.lower()
    if "present" in d2_lower or "current" in d2_lower or "now" in d2_lower or "ongoing" in d2_lower:
        return f"{date1} – {date2}"
    if "present" in d1_lower or "current" in d1_lower or "now" in d1_lower or "ongoing" in d1_lower:
        return f"{date2} – {date1}"
    # If both are years, try to order by year
    y1 = re.search(r'(\d{4})', date1)
    y2 = re.search(r'(\d{4})', date2)
    if y1 and y2:
        y1v = int(y1.group(1))
        y2v = int(y2.group(1))
        if y1v <= y2v:
            return f"{date1} – {date2}"
        else:
            return f"{date2} – {date1}"
    return f"{date1} – {date2}"


def _split_title_and_date(line: str) -> tuple:
    """Try to split a line like 'Job Title | May 2023 – Aug 2025' into (title, date)."""
    # Try common separators
    for sep in [" | ", " — ", " – ", " - ", "  "]:
        if sep in line:
            parts = line.rsplit(sep, 1)
            if len(parts) == 2 and _has_date(parts[1]):
                return parts[0].strip(), parts[1].strip()
    return line, ""


# ────────────────────────────────
# Smart line parser for CV text
# ────────────────────────────────

def _parse_cv_lines(text: str) -> list:
    """
    Parse raw CV text into a structured list of dicts.
    Handles both correct and incorrect LLM formatting.
    """
    raw_lines = [l.rstrip() for l in text.strip().split("\n")]
    parsed = []

    for line in raw_lines:
        stripped = line.strip()
        if not stripped:
            parsed.append({"type": "blank"})
            continue
        if line.startswith("- ") or line.startswith("• "):
            parsed.append({"type": "bullet", "text": stripped[2:].strip()})
            continue
        if _is_section_header(stripped):
            parsed.append({"type": "section", "text": stripped.rstrip(":").upper()})
            continue
        parsed.append({"type": "text", "text": stripped})

    # ── Second pass: fix date lines that are split across multiple lines ──
    fixed = []
    i = 0
    while i < len(parsed):
        p = parsed[i]

        # Detect pattern: title → date-only → date-only → company
        if p["type"] == "text" and not _is_date_only_line(p["text"]):
            # Look ahead: are the next 1-2 lines date-only?
            dates = []
            j = i + 1
            while j < len(parsed) and parsed[j]["type"] == "text" and _is_date_only_line(parsed[j]["text"]):
                dates.append(parsed[j]["text"])
                j += 1

            if len(dates) >= 2:
                # Combine all dates into one range
                combined = dates[0]
                for d in dates[1:]:
                    combined = _combine_dates(combined, d)
                # Check if the next line after dates is a company line (no bullet, not section, not date-only)
                company_line = None
                if j < len(parsed) and parsed[j]["type"] == "text" and not _is_date_only_line(parsed[j]["text"]):
                    company_line = parsed[j]["text"]
                    j += 1

                # Replace with: title + date on one line, then company
                title = p["text"]
                # Check if title already has a date
                t_part, existing_date = _split_title_and_date(title)
                if existing_date:
                    combined = existing_date
                    title = t_part

                fixed.append({"type": "job_header", "title": title, "date": combined})
                if company_line:
                    fixed.append({"type": "company", "text": company_line})
                i = j
                continue

            elif len(dates) == 1:
                # Single date on next line: combine with title
                date_line = dates[0]
                title = p["text"]
                t_part, existing_date = _split_title_and_date(title)
                if existing_date:
                    date_line = existing_date
                    title = t_part

                company_line = None
                if j < len(parsed) and parsed[j]["type"] == "text" and not _is_date_only_line(parsed[j]["text"]):
                    company_line = parsed[j]["text"]
                    j += 1

                fixed.append({"type": "job_header", "title": title, "date": date_line})
                if company_line:
                    fixed.append({"type": "company", "text": company_line})
                i = j
                continue

        # Also detect: title → company+date (next line has date)
        if p["type"] == "text" and not _is_date_only_line(p["text"]) and i + 1 < len(parsed):
            next_p = parsed[i + 1]
            if next_p["type"] == "text" and _has_date(next_p["text"]) and not _is_date_only_line(next_p["text"]):
                # Next line might be "Company | Date" or "Company, Date"
                company_text = next_p["text"]
                company_part, date_part = _split_title_and_date(company_text)
                if date_part:
                    fixed.append({"type": "job_header", "title": p["text"], "date": date_part})
                    fixed.append({"type": "company", "text": company_part})
                    i += 2
                    continue

        # Also detect: title already has date on same line (correct format)
        if p["type"] == "text" and _has_date(p["text"]) and not _is_date_only_line(p["text"]):
            title, date = _split_title_and_date(p["text"])
            if date:
                fixed.append({"type": "job_header", "title": title, "date": date})
                i += 1
                continue

        fixed.append(p)
        i += 1

    return fixed


# ────────────────────────────────
# Main PDF builder
# ────────────────────────────────

def generate_cv_pdf(text: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )

    # ── Styles ──
    name_style = ParagraphStyle(
        "Name",
        fontSize=18, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=2, leading=22
    )
    role_style = ParagraphStyle(
        "Role",
        fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#444444"),
        spaceAfter=3, leading=14
    )
    contact_style = ParagraphStyle(
        "Contact",
        fontSize=8, fontName="Helvetica",
        textColor=colors.HexColor("#555555"),
        spaceAfter=1, leading=11
    )
    section_style = ParagraphStyle(
        "Section",
        fontSize=10, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a1a"),
        spaceBefore=8, spaceAfter=2, leading=14
    )
    job_title_style = ParagraphStyle(
        "JobTitle",
        fontSize=10, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=0, leading=14
    )
    job_date_style = ParagraphStyle(
        "JobDate",
        fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#555555"),
        alignment=TA_RIGHT, spaceAfter=0, leading=14
    )
    company_style = ParagraphStyle(
        "Company",
        fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#555555"),
        spaceAfter=2, leading=12
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#333333"),
        leading=12, leftIndent=10, spaceAfter=2
    )
    body_style = ParagraphStyle(
        "Body",
        fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#333333"),
        leading=12, spaceAfter=2
    )
    skill_label_style = ParagraphStyle(
        "SkillLabel",
        fontSize=9, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=1, leading=12
    )
    skill_value_style = ParagraphStyle(
        "SkillValue",
        fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#333333"),
        spaceAfter=3, leading=12
    )

    story = []

    # ── Parse ──
    parsed = _parse_cv_lines(text)

    # ── Find first section ──
    first_section_idx = None
    for i, p in enumerate(parsed):
        if p["type"] == "section":
            first_section_idx = i
            break

    # ── Render header ──
    header_lines = parsed[:first_section_idx] if first_section_idx is not None else parsed
    name_rendered = False
    for p in header_lines:
        if p["type"] == "blank":
            continue
        txt = p["text"]
        if not name_rendered:
            story.append(Paragraph(txt, name_style))
            name_rendered = True
        elif _is_contact_line(txt):
            story.append(Paragraph(txt, contact_style))
        else:
            story.append(Paragraph(txt, role_style))

    # Thick rule after header
    story.append(Spacer(1, 1*mm))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#1a1a1a"), spaceAfter=4))

    # ── Render body ──
    body = parsed[first_section_idx:] if first_section_idx is not None else []

    for p in body:
        if p["type"] == "blank":
            continue

        if p["type"] == "section":
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph(p["text"], section_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=3))
            continue

        if p["type"] == "bullet":
            story.append(Paragraph("• " + p["text"], bullet_style))
            continue

        if p["type"] == "job_header":
            tbl = Table(
                [[Paragraph(p["title"], job_title_style), Paragraph(p["date"], job_date_style)]],
                colWidths=[135*mm, 45*mm]
            )
            tbl.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
            ]))
            story.append(tbl)
            continue

        if p["type"] == "company":
            story.append(Paragraph(p["text"], company_style))
            continue

        # Skills format: "Category: value" or "Category — value"
        txt = p["text"]
        for sep in [":", " — ", " – "]:
            if sep in txt:
                parts = txt.split(sep, 1)
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    label = parts[0].strip()
                    value = parts[1].strip()
                    if len(label) < 50 and not label.endswith("."):
                        story.append(Paragraph(f"<b>{label}</b>", skill_label_style))
                        story.append(Paragraph(value, skill_value_style))
                        break
        else:
            story.append(Paragraph(txt, body_style))

    doc.build(story)
    return buffer.getvalue()
