import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

def generate_report(
    candidate_name: str,
    target_role: str,
    experience_level: str,
    interview_plan: dict,
    conversation_history: list,
    answer_scores: list,
    output_path: str = "interview_report.pdf"
):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Custom styles ──
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        fontSize=22,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=4,
        alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        spaceAfter=2,
        alignment=TA_CENTER
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontSize=13,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=16,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        spaceAfter=4,
        leading=16
    )
    tag_good = ParagraphStyle(
        "TagGood",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#1a7a4a"),
        fontName="Helvetica-Bold"
    )
    tag_weak = ParagraphStyle(
        "TagWeak",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#b85c00"),
        fontName="Helvetica-Bold"
    )

    # ── Header ──
    story.append(Paragraph("AI Interview Simulator", title_style))
    story.append(Paragraph("Interview Performance Report", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dddddd")))
    story.append(Spacer(1, 10))

    # ── Candidate info ──
    date_str = datetime.now().strftime("%B %d, %Y")
    info_data = [
        ["Candidate", candidate_name, "Date", date_str],
        ["Target Role", target_role, "Level", experience_level.title()],
    ]
    info_table = Table(info_data, colWidths=[1.2*inch, 2.5*inch, 1*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#333333")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#eeeeee")))

    # ── Overall score ──
    if answer_scores:
        avg = sum(s.get("overall_score", 0) for s in answer_scores) / len(answer_scores)
        if avg >= 7.5:
            grade, grade_color = "Excellent", "#1a7a4a"
        elif avg >= 6:
            grade, grade_color = "Good", "#2e6da4"
        elif avg >= 4:
            grade, grade_color = "Average", "#b85c00"
        else:
            grade, grade_color = "Needs Improvement", "#c0392b"

        story.append(Paragraph("Overall Performance", section_style))

        score_data = [[
            Paragraph(f"<font size='28' color='#1a1a2e'><b>{avg:.1f}</b></font><font size='14' color='#888888'>/10</font>", styles["Normal"]),
            Paragraph(f"<font size='14' color='{grade_color}'><b>{grade}</b></font><br/><font size='9' color='#888888'>{len(answer_scores)} questions evaluated</font>", styles["Normal"]),
        ]]
        score_table = Table(score_data, colWidths=[1.5*inch, 5.2*inch])
        score_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), colors.HexColor("#f5f5f5")),
            ("ALIGN", (0,0), (0,0), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ROUNDEDCORNERS", [8,8,8,8]),
            ("BOTTOMPADDING", (0,0), (-1,-1), 12),
            ("TOPPADDING", (0,0), (-1,-1), 12),
            ("LEFTPADDING", (0,0), (-1,-1), 16),
        ]))
        story.append(score_table)

    # ── Score breakdown ──
    story.append(Paragraph("Score Breakdown", section_style))

    tech_scores = [s for s, h in zip(answer_scores, 
        [m for m in conversation_history if m["role"] == "assistant"])
        if s.get("overall_score") is not None]

    breakdown_data = [["Metric", "Score", "Rating"]]
    metrics = ["technical_accuracy", "depth", "clarity", "confidence"]
    labels = ["Technical Accuracy", "Answer Depth", "Communication Clarity", "Confidence"]

    for metric, label in zip(metrics, labels):
        vals = [s.get(metric, 0) for s in answer_scores if s.get(metric)]
        if vals:
            avg_metric = sum(vals) / len(vals)
            bar = "█" * int(avg_metric) + "░" * (10 - int(avg_metric))
            rating = "Strong" if avg_metric >= 7 else "Average" if avg_metric >= 5 else "Weak"
            breakdown_data.append([label, f"{avg_metric:.1f}/10  {bar}", rating])

    if len(breakdown_data) > 1:
        breakdown_table = Table(breakdown_data, colWidths=[2*inch, 3.2*inch, 1.5*inch])
        breakdown_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f9f9f9"), colors.white]),
            ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#dddddd")),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
        ]))
        story.append(breakdown_table)

    # ── Strengths and gaps ──
    strong = interview_plan.get("strong_skills", [])
    missing = interview_plan.get("missing_skills", [])

    if strong or missing:
        story.append(Paragraph("Strengths & Gaps", section_style))
        sw_data = [
            [Paragraph("<b>✓ Strengths</b>", tag_good),
             Paragraph("<b>⚠ Gaps to Close</b>", tag_weak)],
            [Paragraph("<br/>".join(f"• {s}" for s in strong), body_style),
             Paragraph("<br/>".join(f"• {s}" for s in missing) if missing else "None identified", body_style)]
        ]
        sw_table = Table(sw_data, colWidths=[3.3*inch, 3.4*inch])
        sw_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), colors.HexColor("#eaf5ee")),
            ("BACKGROUND", (1,0), (1,0), colors.HexColor("#fdf3e7")),
            ("BACKGROUND", (0,1), (0,1), colors.HexColor("#f9fdf9")),
            ("BACKGROUND", (1,1), (1,1), colors.HexColor("#fffdf7")),
            ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#dddddd")),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
            ("TOPPADDING", (0,0), (-1,-1), 10),
            ("LEFTPADDING", (0,0), (-1,-1), 12),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        story.append(sw_table)

    # ── Question by question review ──
    story.append(Paragraph("Question-by-Question Review", section_style))

    questions = [m["content"] for m in conversation_history if m["role"] == "assistant"]
    answers = [m["content"] for m in conversation_history if m["role"] == "user"]

    for i, (q, a, s) in enumerate(zip(questions, answers, answer_scores)):
        score_val = s.get("overall_score", 0)
        feedback = s.get("feedback", "")
        improvement = s.get("improvement", "")

        if score_val >= 7:
            score_color = "#1a7a4a"
        elif score_val >= 5:
            score_color = "#b85c00"
        else:
            score_color = "#c0392b"

        q_data = [[
            Paragraph(f"<font color='#888888' size='8'>Q{i+1}</font>  <b>{q[:120]}{'...' if len(q)>120 else ''}</b>", body_style),
            Paragraph(f"<font color='{score_color}'><b>{score_val}/10</b></font>", body_style)
        ]]
        q_table = Table(q_data, colWidths=[5.8*inch, 0.9*inch])
        q_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#f9f9f9")),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (0,-1), 10),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        story.append(q_table)

        if feedback:
            story.append(Paragraph(f"<font color='#1a7a4a'>✓</font> {feedback}", body_style))
        if improvement:
            story.append(Paragraph(f"<font color='#b85c00'>→</font> {improvement}", body_style))
        story.append(Spacer(1, 6))

    # ── Recommended topics ──
    focus = interview_plan.get("focus_areas", [])
    missing_skills = interview_plan.get("missing_skills", [])
    topics = list(set(focus + missing_skills))

    if topics:
        story.append(Paragraph("Recommended Study Topics", section_style))
        topic_text = "   ".join(f"[ {t} ]" for t in topics)
        story.append(Paragraph(topic_text, body_style))

    # ── Footer ──
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#eeeeee")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Generated by AI Interview Simulator • {date_str}",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8,
                      textColor=colors.HexColor("#aaaaaa"), alignment=TA_CENTER)
    ))

    doc.build(story)
    print(f"\n[REPORT] PDF saved to: {output_path}")
    return output_path
