import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


class PDFCertificateGenerator:
    """Service responsible for rendering professional PDF certificates using ReportLab."""

    @staticmethod
    def generate_certificate(
        recipient_name: str,
        event_name: str,
        event_date: str,
        certificate_number: str,
        output_file_path: str,
        organization_name: str = "AEREO ACADEMY",
    ) -> str:
        """Generates a high-quality landscape PDF certificate and saves it to output_file_path."""
        output_path = Path(output_file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Landscape A4 size: 841.89 x 595.27 points
        page_width, page_height = landscape(A4)

        def draw_background(c: canvas.Canvas, doc):
            c.saveState()

            # Outer border (Navy Accent)
            c.setStrokeColor(colors.HexColor("#0F172A"))  # Slate 900 / Navy
            c.setLineWidth(4)
            c.rect(20, 20, page_width - 40, page_height - 40)

            # Inner Golden Accent Border
            c.setStrokeColor(colors.HexColor("#D97706"))  # Amber / Gold accent
            c.setLineWidth(1.5)
            c.rect(26, 26, page_width - 52, page_height - 52)

            # Corner decorative accents
            accent_color = colors.HexColor("#2563EB")  # Professional Blue
            c.setFillColor(accent_color)
            c.circle(35, page_height - 35, 5, fill=1, stroke=0)
            c.circle(page_width - 35, page_height - 35, 5, fill=1, stroke=0)
            c.circle(35, 35, 5, fill=1, stroke=0)
            c.circle(page_width - 35, 35, 5, fill=1, stroke=0)

            # Watermark / Subtle Header Bar
            c.setFillColor(colors.HexColor("#F8FAFC"))
            c.rect(28, page_height - 90, page_width - 56, 60, fill=1, stroke=0)

            c.restoreState()

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=landscape(A4),
            leftMargin=40,
            rightMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()

        # Custom typography styles
        org_style = ParagraphStyle(
            "OrgStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1E3A8A"),  # Deep Navy Blue
            spaceAfter=15,
        )

        title_style = ParagraphStyle(
            "CertTitleStyle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=34,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=15,
        )

        subtitle_style = ParagraphStyle(
            "SubTitleStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=13,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#475569"),
            spaceAfter=20,
        )

        name_style = ParagraphStyle(
            "NameStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=32,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#2563EB"),  # Royal Blue Accent
            spaceAfter=20,
        )

        reason_style = ParagraphStyle(
            "ReasonStyle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#334155"),
            spaceAfter=25,
        )

        meta_label_style = ParagraphStyle(
            "MetaLabel",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#64748B"),
        )

        meta_val_style = ParagraphStyle(
            "MetaVal",
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0F172A"),
        )

        story = []

        # Organization Banner
        story.append(Paragraph(organization_name.upper(), org_style))
        story.append(Spacer(1, 10))

        # Certificate Main Title
        story.append(Paragraph("CERTIFICATE OF PARTICIPATION", title_style))
        story.append(Spacer(1, 5))

        story.append(Paragraph("This is proudly presented to", subtitle_style))
        story.append(Spacer(1, 5))

        # Recipient Name
        story.append(Paragraph(recipient_name, name_style))
        story.append(Spacer(1, 5))

        # Description / Reason
        reason_text = (
            f"for successfully participating in <b>{event_name}</b> "
            f"conducted on <b>{event_date}</b>."
        )
        story.append(Paragraph(reason_text, reason_style))
        story.append(Spacer(1, 25))

        # Footer Meta (Certificate Number, Date, Signatures)
        issue_date = datetime.now().strftime("%B %d, %Y")

        footer_data = [
            [
                Paragraph("<b>ISSUED ON</b>", meta_label_style),
                Paragraph("<b>CERTIFICATE ID</b>", meta_label_style),
                Paragraph("<b>AUTHORIZED SIGNATURE</b>", meta_label_style),
            ],
            [
                Paragraph(issue_date, meta_val_style),
                Paragraph(certificate_number, meta_val_style),
                Paragraph("_____________________<br/>Program Director", meta_val_style),
            ],
        ]

        footer_table = Table(footer_data, colWidths=[240, 240, 240])
        footer_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        story.append(footer_table)

        doc.build(story, onFirstPage=draw_background)
        return str(output_path)
