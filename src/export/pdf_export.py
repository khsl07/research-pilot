import io
import re
from typing import Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from src.schemas.verification import FinalResearchReport, CitationAuditReport
from src.schemas.conflict import ConflictReport

def generate_pdf_bytes(
    report: FinalResearchReport,
    conflict_report: Optional[ConflictReport] = None,
    audit_report: Optional[CitationAuditReport] = None,
) -> bytes:
    """Generate professional executive PDF report using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=10,
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569'),
    )

    h1_style = ParagraphStyle(
        'Heading1Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=14,
        spaceAfter=6,
    )

    h2_style = ParagraphStyle(
        'Heading2Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#2563eb'),
        spaceBefore=10,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4,
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#1e293b'),
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0f172a'),
    )

    elements = []

    # Title & Metadata Header
    elements.append(Paragraph(report.title, title_style))
    status_text = "<b>Status:</b> Approved by Human Reviewer" if report.approved_by_user else "<b>Status:</b> Draft (Pending Review)"
    time_str = report.approval_timestamp or "Not signed"
    meta_text = f"{status_text} | <b>Topic:</b> {report.topic} | <b>Timestamp:</b> {time_str}"
    elements.append(Paragraph(meta_text, meta_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3b82f6'), spaceAfter=15))

    # Parse markdown lines into PDF flowables
    lines = report.full_markdown.split("\n")
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            continue  # Already in header
        elif stripped.startswith("## "):
            elements.append(Paragraph(stripped[3:], h1_style))
        elif stripped.startswith("### "):
            elements.append(Paragraph(stripped[4:], h2_style))
        elif stripped.startswith("- "):
            clean_b = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', stripped[2:])
            elements.append(Paragraph(f"&bull; {clean_b}", bullet_style))
        elif stripped.startswith("---"):
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=8, spaceBefore=8))
        else:
            clean_p = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', stripped)
            elements.append(Paragraph(clean_p, body_style))

    # Citation Verification Appendix Table
    if audit_report and audit_report.items:
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("Appendix: Citation & Fact-Checking Audit", h1_style))
        audit_meta = f"Fidelity Score: <b>{audit_report.fidelity_score}%</b> | Verdict: <b>{audit_report.verdict}</b> | Audited Claims: <b>{audit_report.total_claims_checked}</b>"
        elements.append(Paragraph(audit_meta, meta_style))
        elements.append(Spacer(1, 8))

        table_data = [
            [Paragraph("Claim Excerpt", table_header),
             Paragraph("Ref", table_header),
             Paragraph("Status", table_header),
             Paragraph("Confidence", table_header),
             Paragraph("Audit Flag / Warning", table_header)]
        ]

        for item in audit_report.items[:12]:
            warn = item.flag_warning or "Supported by evidence"
            exc = item.claim_text.replace("\n", " ")[:60] + "..."
            table_data.append([
                Paragraph(exc, table_cell),
                Paragraph(f"[{item.citation_index}]", table_cell),
                Paragraph(f"<b>{item.status}</b>", table_cell),
                Paragraph(f"{int(item.confidence_score*100)}%", table_cell),
                Paragraph(warn, table_cell),
            ])

        t = Table(table_data, colWidths=[160, 35, 75, 55, 195])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
