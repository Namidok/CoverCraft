"""
PDF Generator — ATS-friendly CVs matching Srikar's original format.
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

    name_style = ParagraphStyle("Name", parent=styles["Normal"],
        fontSize=16, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a1a"), spaceAfter=2)
    contact_style = ParagraphStyle("Contact", parent=styles["Normal"],
        fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#555555"), spaceAfter=2)
    label_style = ParagraphStyle("Label", parent=styles["Normal"],
        fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#888888"), spaceAfter=12)
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=11, fontName="Helvetica",
        textColor=colors.HexColor("#1a1a1a"), leading=18, spaceAfter=12)

    story = []
    story.append(Paragraph("Srikar Kodi", name_style))
    story.append(Paragraph("kodisrikar@gmail.com · +49-1634218928 · Berlin, Germany", contact_style))
    story.append(Paragraph("linkedin.com/in/srikar-kodi-046a631b2/ · github.com/Namidok", contact_style))
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(f"Cover Letter — {role} at {company}", label_style))

    for para in text.strip().split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip().replace("\n", " "), body_style))

    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("Best regards,", body_style))
    story.append(Paragraph("<b>Srikar Kodi</b>", body_style))

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

    # Fixed header — always lines 0-3
    # Line 0: Name
    # Line 1: Title
    # Line 2: Contact line 1
    # Line 3: Contact line 2

    # Header block — forced separate lines
    header_items = []
    if len(lines) >= 1:
        header_items.append(Paragraph(lines[0].strip(), name_style))
    if len(lines) >= 2:
        header_items.append(Paragraph(lines[1].strip(), title_style))
    if len(lines) >= 3:
        header_items.append(Paragraph(lines[2].strip(), contact_style))
    if len(lines) >= 4:
        header_items.append(Paragraph(lines[3].strip(), contact_style))
    story.append(KeepTogether(header_items))
    story.append(Spacer(1, 2*mm))

    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=0.8,
        color=colors.HexColor("#1a1a1a"), spaceAfter=4))

    # Process rest of lines
    i = 4
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # Section headers — ALL CAPS, short
        if line.isupper() and 2 < len(line) < 30:
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph(line, section_style))
            story.append(HRFlowable(width="100%", thickness=0.5,
                color=colors.HexColor("#cccccc"), spaceAfter=3))
            i += 1
            continue

        # Bullet points
        if line.startswith("- ") or line.startswith("• "):
            story.append(Paragraph("• " + line[2:].strip(), bullet_style))
            i += 1
            continue

        # Job title / education lines with | separator
        if "|" in line and "@" not in line:
            story.append(Paragraph(line, job_title_style))
            i += 1
            continue

        # Stack lines under projects
        if line.lower().startswith("stack:"):
            story.append(Paragraph(line, body_style))
            i += 1
            continue

        # Project names / education degree lines (no | and not all caps)
        if not line.isupper() and len(line) > 5:
            story.append(Paragraph(line, body_style))
            i += 1
            continue

        story.append(Paragraph(line, body_style))
        i += 1

    doc.build(story)
    return buffer.getvalue()
