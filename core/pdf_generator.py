"""
PDF Generator — ATS-friendly CVs and cover letters.
Uses the generated text directly without hardcoded personal info.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
from io import BytesIO


def generate_cover_letter_pdf(text: str, company: str, role: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=25*mm, leftMargin=25*mm,
        topMargin=25*mm, bottomMargin=25*mm)

    styles = getSampleStyleSheet()

    label_style = ParagraphStyle("Label", parent=styles["Normal"],
        fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#888888"), spaceAfter=12)
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=11, fontName="Helvetica",
        textColor=colors.HexColor("#1a1a1a"), leading=18, spaceAfter=12)

    story = []
    story.append(Paragraph(f"Cover Letter — {role} at {company}", label_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=12))

    for para in text.strip().split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip().replace("\n", " "), body_style))

    doc.build(story)
    return buffer.getvalue()


def generate_cv_pdf(text: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm)

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle("Name", parent=styles["Normal"],
        fontSize=16, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a1a"), spaceAfter=6)
    title_style = ParagraphStyle("Title", parent=styles["Normal"],
        fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#444444"), spaceAfter=6)
    contact_style = ParagraphStyle("Contact", parent=styles["Normal"],
        fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#555555"), spaceAfter=1)
    section_style = ParagraphStyle("Section", parent=styles["Normal"],
        fontSize=10, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a1a"),
        spaceBefore=6, spaceAfter=3)
    job_title_style = ParagraphStyle("JobTitle", parent=styles["Normal"],
        fontSize=10, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a1a"), spaceAfter=2)
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=9.5, fontName="Helvetica",
        textColor=colors.HexColor("#222222"), leading=14, spaceAfter=3)
    bullet_style = ParagraphStyle("Bullet", parent=styles["Normal"],
        fontSize=9.5, fontName="Helvetica",
        textColor=colors.HexColor("#333333"),
        leading=14, leftIndent=10, spaceAfter=2)

    story = []
    lines = text.strip().split("\n")

    i = 0
    header_done = False

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # Name — first line
        if i == 0:
            story.append(Paragraph(line, name_style))
            i += 1
            continue

        # Title line — second line if not contact
        if i == 1 and "@" not in line and "|" not in line and len(line) < 60:
            story.append(Paragraph(line, title_style))
            i += 1
            continue

        # Contact lines
        if not header_done and ("@" in line or "linkedin" in line.lower() or "github" in line.lower() or "+" in line):
            story.append(Paragraph(line, contact_style))
            i += 1
            if i < len(lines) and ("@" in lines[i] or "linkedin" in lines[i].lower() or "github" in lines[i].lower()):
                story.append(Paragraph(lines[i].strip(), contact_style))
                i += 1
            story.append(Spacer(1, 2*mm))
            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#1a1a1a"), spaceAfter=4))
            header_done = True
            continue

        # Section headers
        if line.isupper() and 2 < len(line) < 30:
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph(line, section_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=3))
            i += 1
            continue

        # Bullet points
        if line.startswith("- ") or line.startswith("• "):
            story.append(Paragraph("• " + line[2:].strip(), bullet_style))
            i += 1
            continue

        # Job title lines with |
        if "|" in line and "@" not in line:
            story.append(Paragraph(line, job_title_style))
            i += 1
            continue

        story.append(Paragraph(line, body_style))
        i += 1

    doc.build(story)
    return buffer.getvalue()
