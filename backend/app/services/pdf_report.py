"""
Generates a clinical PDF report from a Prediction + Xray + Report record.
Uses ReportLab (pure Python, no external binary dependency).
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.core.config import settings


def build_report_pdf(
    output_path: str,
    patient_name: str,
    patient_age,
    patient_gender,
    xray_image_path: str,
    heatmap_image_path: str,
    disease: str,
    confidence: float,
    severity: str,
    recommendations: list,
    ai_explanation: str,
    doctor_comment: str = None,
    approved: bool = False,
) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    disclaimer_style = ParagraphStyle(
        "disclaimer", parent=styles["Normal"], textColor=colors.red, fontSize=9, spaceBefore=10
    )

    story = []
    story.append(Paragraph("AI-Assisted Chest X-ray Diagnosis Report", styles["Title"]))
    story.append(Spacer(1, 8))

    patient_table = Table(
        [
            ["Patient Name:", patient_name or "N/A"],
            ["Age:", str(patient_age) if patient_age is not None else "N/A"],
            ["Gender:", patient_gender or "N/A"],
            ["Report Status:", "Approved by Doctor" if approved else "Pending Doctor Review"],
        ],
        colWidths=[120, 300],
    )
    patient_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 12))

    # Images side by side
    img_row = []
    if xray_image_path and os.path.exists(xray_image_path):
        img_row.append(Image(xray_image_path, width=200, height=200))
    if heatmap_image_path and os.path.exists(heatmap_image_path):
        img_row.append(Image(heatmap_image_path, width=200, height=200))
    if img_row:
        img_table = Table([img_row])
        story.append(img_table)
        story.append(Spacer(1, 8))
        story.append(Paragraph("Left: Original X-ray | Right: Grad-CAM Heatmap Overlay", styles["Italic"]))
        story.append(Spacer(1, 12))

    story.append(Paragraph("AI Prediction Summary", styles["Heading2"]))
    story.append(Paragraph(f"<b>Predicted Finding:</b> {disease}", styles["Normal"]))
    story.append(Paragraph(f"<b>Confidence Score:</b> {confidence * 100:.1f}%", styles["Normal"]))
    story.append(Paragraph(f"<b>Severity:</b> {severity}", styles["Normal"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("AI Explanation", styles["Heading2"]))
    story.append(Paragraph(ai_explanation or "No explanation available.", styles["Normal"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Clinical Recommendations", styles["Heading2"]))
    for rec in recommendations or []:
        story.append(Paragraph(f"• {rec}", styles["Normal"]))
    story.append(Spacer(1, 8))

    if doctor_comment:
        story.append(Paragraph("Doctor's Comment", styles["Heading2"]))
        story.append(Paragraph(doctor_comment, styles["Normal"]))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Disclaimer", styles["Heading2"]))
    story.append(Paragraph(settings.DISCLAIMER, disclaimer_style))

    doc.build(story)
    return output_path
