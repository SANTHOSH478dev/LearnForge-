import io
import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_exam_report_pdf(attempt_data: Dict[str, Any], student_name: str) -> io.BytesIO:
    """Generate a clean, high-contrast PDF assessment report using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1e1b4b"), # Deep Indigo
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#6366f1"),
        spaceAfter=14
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#312e81"),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1f2937")
    )
    badge_style = ParagraphStyle(
        'BadgeText',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )

    story = []

    # Header
    story.append(Paragraph("LearnForge AI — Performance & Assessment Report", title_style))
    story.append(Paragraph(f"Turn Every Page Into Progress | Student: <b>{student_name}</b> | Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#818cf8"), spaceAfter=14))

    # Top Metrics Table
    grade_color = colors.HexColor("#10b981") if attempt_data.get("grade") in ["S", "A"] else (colors.HexColor("#f59e0b") if attempt_data.get("grade") in ["B", "C"] else colors.HexColor("#ef4444"))
    
    metrics_data = [
        [
            Paragraph("<b>Assessment Title</b>", body_style),
            Paragraph(str(attempt_data.get("test_title", "Assessment")), body_style),
            Paragraph("<b>Overall Grade</b>", body_style),
            Paragraph(f"<b>{attempt_data.get('grade', 'N/A')}</b> ({attempt_data.get('percentage', 0)}%)", body_style)
        ],
        [
            Paragraph("<b>Score Achieved</b>", body_style),
            Paragraph(f"{attempt_data.get('total_score', 0)} / {attempt_data.get('max_possible_score', 0)}", body_style),
            Paragraph("<b>Time Taken</b>", body_style),
            Paragraph(f"{attempt_data.get('time_taken_seconds', 0) // 60}m {attempt_data.get('time_taken_seconds', 0) % 60}s", body_style)
        ],
        [
            Paragraph("<b>Accuracy Ratio</b>", body_style),
            Paragraph(f"Correct: {attempt_data.get('correct_count', 0)} | Incorrect: {attempt_data.get('incorrect_count', 0)} | Skipped: {attempt_data.get('unanswered_count', 0)}", body_style),
            Paragraph("<b>Status</b>", body_style),
            Paragraph(str(attempt_data.get("status", "submitted")).upper(), body_style)
        ]
    ]

    t_metrics = Table(metrics_data, colWidths=[110, 160, 100, 170])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 14))

    # AI Executive Summary
    story.append(Paragraph("AI Feedback Coach — Executive Insights", section_heading))
    summary_text = attempt_data.get("ai_summary_feedback") or "Good overall conceptual adherence with room for targeted revision."
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 6))

    plan_text = attempt_data.get("ai_study_plan_recommendation") or "Review key definitions and retake practice sets."
    story.append(Paragraph(f"<b>Recommended Study Plan:</b> {plan_text}", body_style))
    story.append(Spacer(1, 14))

    # Question Breakdown Table
    story.append(Paragraph("Question-Level Performance & Source Citations", section_heading))
    q_table_data = [
        [
            Paragraph("<b>#</b>", body_style),
            Paragraph("<b>Question</b>", body_style),
            Paragraph("<b>Your Ans</b>", body_style),
            Paragraph("<b>Correct</b>", body_style),
            Paragraph("<b>Result</b>", body_style),
            Paragraph("<b>Source</b>", body_style)
        ]
    ]

    q_results = attempt_data.get("question_results", [])
    for idx, qr in enumerate(q_results[:15], 1):  # Cap at 15 for concise multi-page report
        res_str = "CORRECT" if qr.get("is_correct") else ("SKIPPED" if qr.get("is_unanswered") else "INCORRECT")
        res_color = "#059669" if qr.get("is_correct") else ("#d97706" if qr.get("is_unanswered") else "#dc2626")
        
        src = qr.get("source_citation") or {}
        src_label = f"P.{src.get('page_number', 1)}" if src.get("page_number") else "Notes"

        q_table_data.append([
            Paragraph(str(idx), body_style),
            Paragraph(qr.get("question_text", "")[:80] + "...", body_style),
            Paragraph(str(qr.get("user_answer") or "-"), body_style),
            Paragraph(str(qr.get("correct_answer") or "-")[:20], body_style),
            Paragraph(f"<font color='{res_color}'><b>{res_str}</b></font>", body_style),
            Paragraph(src_label, body_style)
        ])

    t_questions = Table(q_table_data, colWidths=[24, 210, 60, 110, 75, 60])
    t_questions.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e0e7ff")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_questions)
    story.append(Spacer(1, 14))

    # Footer note
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceBefore=10, spaceAfter=8))
    story.append(Paragraph("LearnForge AI • Deterministic Server-Side Scoring & Verified Grounded Passages", subtitle_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
