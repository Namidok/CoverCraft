import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from io import BytesIO


def generate_cover_letter_pdf(text: str, company: str, role: str) -> bytes:
    """Generate a clean ATS-friendly cover letter PDF."""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=25*mm,
        leftMargin=25*mm,
        topMargin=25*mm,
        bottomMargin=25*mm,
    )

    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        "Header",
        parent=styles["Normal"],
        fontSize=16,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=4,
    )

    subheader_style = ParagraphStyle(
        "SubHeader",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#555555"),
        spaceAfter=2,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica",
        textColor=colors.HexColor("#1a1a1a"),
        leading=18,
        spaceAfter=12,
    )

    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica",
        textColor=colors.HexColor("#888888"),
        spaceAfter=16,
    )

    story = []

    # Header
    story.append(Paragraph("Srikar Kodi", header_style))
    story.append(Paragraph("kodisrikar@gmail.com · +49-1634218928 · Berlin, Germany", subheader_style))
    story.append(Paragraph("linkedin.com/in/srikar-kodi-046a631b2/ · github.com/Namidok", subheader_style))
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 4*mm))

    # Label
    story.append(Paragraph(f"Cover Letter — {role} at {company}", label_style))

    # Body paragraphs
    paragraphs = text.strip().split("\n\n")
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip().replace("\n", " "), body_style))

    # Signature
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Best regards,", body_style))
    story.append(Paragraph("<b>Srikar Kodi</b>", body_style))

    doc.build(story)
    return buffer.getvalue()


def generate_cv_pdf(text: str) -> bytes:
    """Generate a clean ATS-friendly CV PDF."""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
    )

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        "Name",
        parent=styles["Normal"],
        fontSize=20,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=2,
    )

    contact_style = ParagraphStyle(
        "Contact",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica",
        textColor=colors.HexColor("#555555"),
        spaceAfter=8,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a1a"),
        spaceBefore=10,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#1a1a1a"),
        leading=14,
        spaceAfter=4,
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#333333"),
        leading=14,
        leftIndent=12,
        spaceAfter=3,
    )

    story = []
    lines = text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 2*mm))
            continue

        # Name line (first line)
        if lines.index(line) == 0 or (len(line) < 30 and line.isupper() and lines.index(line) == 0):
            story.append(Paragraph(line, name_style))

        # Section headers (all caps)
        elif line.isupper() and len(line) < 30:
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceBefore=4))
            story.append(Paragraph(line, section_style))

        # Bullet points
        elif line.startswith("- "):
            story.append(Paragraph("• " + line[2:], bullet_style))

        # Contact info / role lines (short, contains | or @)
        elif "|" in line or "@" in line or "github" in line.lower() or "linkedin" in line.lower():
            story.append(Paragraph(line, contact_style))

        # Regular body
        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)
    return buffer.getvalue()