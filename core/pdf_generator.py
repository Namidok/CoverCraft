"""
PDF Generator — matches SrikarKodi.pdf exactly
"""
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_RIGHT
from io import BytesIO

DATE_RE = re.compile(
    r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}'
    r'|\d{4}\s*[–—-]\s*(?:\d{4}|Present|Current|Now|Ongoing)'
    r'|(?:Present|Current|Now|Ongoing)',
    re.IGNORECASE
)

SECTION_KEYWORDS = {
    "profile", "summary", "experience", "work experience",
    "projects", "education", "skills", "certifications",
    "achievements", "languages", "employment"
}


def _is_section(line: str) -> bool:
    c = line.strip().rstrip(":").lower()
    if c in SECTION_KEYWORDS:
        return True
    if line.strip().isupper() and 2 < len(line.strip()) < 40 and not any(ch in line for ch in ["@", "+", "."]):
        return True
    return False


def _has_date(s: str) -> bool:
    return bool(DATE_RE.search(s))


def _extract_date(s: str):
    """Returns (text_without_date, date_string) or (s, '')"""
    m = re.search(
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[–—-]\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?\d{4}'
        r'|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[–—-]\s*(?:Present|Current|Now|Ongoing)'
        r'|\d{4}\s*[–—-]\s*(?:\d{4}|Present|Current|Now|Ongoing))',
        s, re.IGNORECASE
    )
    if m:
        date = m.group(0).strip()
        rest = (s[:m.start()] + s[m.end():]).strip().rstrip("–—-|•").strip()
        return rest, date
    return s, ""


def _is_contact(s: str) -> bool:
    l = s.lower()
    return any(x in l for x in ["@", "linkedin", "github", "+", ".com", ".dev", "http", "www"])


def generate_cover_letter_pdf(text: str, company: str, role: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=25*mm, leftMargin=25*mm,
        topMargin=25*mm, bottomMargin=25*mm)
    styles = getSampleStyleSheet()
    label_style = ParagraphStyle("Label", parent=styles["Normal"],
        fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#888888"), spaceAfter=10)
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=11, fontName="Helvetica",
        textColor=colors.HexColor("#1a1a1a"), leading=18, spaceAfter=12)
    story = []
    story.append(Paragraph(f"Cover Letter — {role} at {company}", label_style))
    story.append(HRFlowable(width="100%", thickness=0.5,
        color=colors.HexColor("#cccccc"), spaceAfter=12))
    for para in text.strip().split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip().replace("\n", " "), body_style))
    doc.build(story)
    return buffer.getvalue()


def generate_cv_pdf(text: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=15*mm, bottomMargin=15*mm)

    W = 170  # usable width in mm

    # Styles
    name_s = ParagraphStyle("N", fontSize=20, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0a0a0a"), spaceAfter=1, leading=24)
    subtitle_s = ParagraphStyle("ST", fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#444444"), spaceAfter=2, leading=14)
    contact_s = ParagraphStyle("C", fontSize=8.5, fontName="Helvetica",
        textColor=colors.HexColor("#555555"), spaceAfter=1, leading=12)
    section_s = ParagraphStyle("SEC", fontSize=10, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0a0a0a"), spaceBefore=5, spaceAfter=2, leading=14)
    profile_s = ParagraphStyle("PRO", fontSize=9.5, fontName="Helvetica",
        textColor=colors.HexColor("#222222"), leading=14, spaceAfter=3)
    job_title_s = ParagraphStyle("JT", fontSize=10, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0a0a0a"), spaceAfter=0, leading=14)
    job_date_s = ParagraphStyle("JD", fontSize=9.5, fontName="Helvetica",
        textColor=colors.HexColor("#0a0a0a"), alignment=TA_RIGHT, spaceAfter=0, leading=14)
    company_s = ParagraphStyle("CO", fontSize=9.5, fontName="Helvetica",
        textColor=colors.HexColor("#555555"), spaceAfter=3, leading=13)
    bullet_s = ParagraphStyle("BU", fontSize=9.5, fontName="Helvetica",
        textColor=colors.HexColor("#222222"), leading=13, leftIndent=10, spaceAfter=2)
    edu_deg_s = ParagraphStyle("ED", fontSize=10, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0a0a0a"), spaceAfter=0, leading=14)
    edu_uni_s = ParagraphStyle("EU", fontSize=9.5, fontName="Helvetica",
        textColor=colors.HexColor("#555555"), spaceAfter=3, leading=13)
    skill_s = ParagraphStyle("SK", fontSize=9.5, fontName="Helvetica",
        textColor=colors.HexColor("#222222"), leading=13, spaceAfter=4)
    body_s = ParagraphStyle("BO", fontSize=9.5, fontName="Helvetica",
        textColor=colors.HexColor("#333333"), leading=13, spaceAfter=2)

    def date_row(left_text, date_text, left_style, date_style):
        tbl = Table(
            [[Paragraph(left_text, left_style), Paragraph(date_text, date_style)]],
            colWidths=[130*mm, 40*mm]
        )
        tbl.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
            ("TOPPADDING", (0,0), (-1,-1), 0),
            ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ]))
        return tbl

    story = []
    lines = [l.rstrip() for l in text.strip().split("\n")]

    # ── Header ──
    name_done = False
    subtitle_done = False
    body_start = 0

    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue
        if _is_section(s):
            body_start = i
            break
        if not name_done:
            story.append(Paragraph(s, name_s))
            name_done = True
        elif not subtitle_done and not _is_contact(s):
            story.append(Paragraph(s, subtitle_s))
            subtitle_done = True
        elif _is_contact(s):
            story.append(Paragraph(s, contact_s))

    story.append(Spacer(1, 2*mm))
    story.append(HRFlowable(width="100%", thickness=1.5,
        color=colors.HexColor("#0a0a0a"), spaceAfter=4))

    # ── Body ──
    i = body_start
    current_section = ""

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        if not s:
            i += 1
            continue

        if _is_section(s):
            current_section = s.upper().rstrip(":")
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph(current_section, section_s))
            story.append(HRFlowable(width="100%", thickness=0.5,
                color=colors.HexColor("#cccccc"), spaceAfter=4))
            i += 1
            continue

        # Bullets
        if s.startswith(("- ", "• ")):
            story.append(Paragraph("• " + s[2:].strip(), bullet_s))
            i += 1
            continue

        # ── SKILLS ──
        if current_section == "SKILLS":
            # Format: "Label: values" or "Label & Label: values"
            # Also handle label on one line, values on next
            for sep in [": ", " — ", " – "]:
                if sep in s:
                    parts = s.split(sep, 1)
                    if len(parts) == 2 and len(parts[0]) < 60 and not _has_date(parts[0]):
                        label = f"<b>{parts[0].strip()}</b>"
                        story.append(Paragraph(f"{label}: {parts[1].strip()}", skill_s))
                        i += 1
                        break
            else:
                # Check next line — might be values for this label
                if i + 1 < len(lines):
                    next_s = lines[i+1].strip()
                    if next_s and not _is_section(next_s) and not next_s.startswith(("- ", "• ")) and not _has_date(next_s) and not any(sep in s for sep in [": ", " — ", " – "]):
                        story.append(Paragraph(f"<b>{s}</b>: {next_s}", skill_s))
                        i += 2
                    else:
                        story.append(Paragraph(s, skill_s))
                        i += 1
                else:
                    story.append(Paragraph(s, skill_s))
                    i += 1
            continue

        # ── EDUCATION ──
        if current_section == "EDUCATION":
            if _has_date(s):
                rest, date = _extract_date(s)
                if date and rest:
                    story.append(date_row(rest, date, edu_deg_s, job_date_s))
                else:
                    story.append(Paragraph(s, edu_deg_s))
                # Next line: university + location — keep on ONE line
                if i + 1 < len(lines):
                    next_s = lines[i+1].strip()
                    if next_s and not _is_section(next_s) and not _has_date(next_s) and not next_s.startswith(("- ", "• ")):
                        # Peek at line after to see if it's a location
                        if i + 2 < len(lines):
                            next2 = lines[i+2].strip()
                            if next2 and not _is_section(next2) and not _has_date(next2) and not next2.startswith(("- ", "• ")) and len(next2) < 40:
                                # Combine university and location
                                story.append(Paragraph(f"{next_s}, {next2}", edu_uni_s))
                                i += 3
                                continue
                        story.append(Paragraph(next_s, edu_uni_s))
                        i += 2
                        continue
            else:
                # Could be university line without date above
                # Check if next line is a location
                if i + 1 < len(lines):
                    next_s = lines[i+1].strip()
                    if next_s and not _is_section(next_s) and not _has_date(next_s) and not next_s.startswith(("- ", "• ")) and len(next_s) < 40:
                        story.append(Paragraph(f"{s}, {next_s}", edu_uni_s))
                        i += 2
                        continue
                story.append(Paragraph(s, edu_uni_s))
            i += 1
            continue

        # ── EXPERIENCE / PROJECTS ──
        if current_section in ("EXPERIENCE", "WORK EXPERIENCE", "PROJECTS", "EMPLOYMENT"):
            if _has_date(s):
                rest, date = _extract_date(s)
                if date and rest:
                    story.append(date_row(rest, date, job_title_s, job_date_s))
                else:
                    story.append(Paragraph(s, job_title_s))
                # Next line: company + location — combine if split
                if i + 1 < len(lines):
                    next_s = lines[i+1].strip()
                    if next_s and not _is_section(next_s) and not _has_date(next_s) and not next_s.startswith(("- ", "• ")):
                        if i + 2 < len(lines):
                            next2 = lines[i+2].strip()
                            if next2 and not _is_section(next2) and not _has_date(next2) and not next2.startswith(("- ", "• ")) and len(next2) < 40:
                                story.append(Paragraph(f"{next_s}, {next2}", company_s))
                                i += 3
                                continue
                        story.append(Paragraph(next_s, company_s))
                        i += 2
                        continue
                i += 1
                continue
            else:
                # Company/project line with | separator
                if "|" in s:
                    story.append(Paragraph(s, company_s))
                else:
                    story.append(Paragraph(s, company_s))
                i += 1
                continue

        # ── PROFILE / SUMMARY ──
        if current_section in ("PROFILE", "SUMMARY"):
            story.append(Paragraph(s, profile_s))
            i += 1
            continue

        story.append(Paragraph(s, body_s))
        i += 1

    doc.build(story)
    return buffer.getvalue()
