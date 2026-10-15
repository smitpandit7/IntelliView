import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

# ── Color palette ──
C_DARK      = colors.HexColor("#1a1a2e")
C_GREEN     = colors.HexColor("#1a7a4a")
C_GREEN_BG  = colors.HexColor("#eaf5ee")
C_AMBER     = colors.HexColor("#b85c00")
C_AMBER_BG  = colors.HexColor("#fdf3e7")
C_RED       = colors.HexColor("#c0392b")
C_RED_BG    = colors.HexColor("#fceaea")
C_BLUE      = colors.HexColor("#2e6da4")
C_BLUE_BG   = colors.HexColor("#e8f0fa")
C_GRAY      = colors.HexColor("#888888")
C_LIGHT     = colors.HexColor("#f5f5f5")
C_BORDER    = colors.HexColor("#dddddd")
C_WHITE     = colors.white

def score_color(score):
    if score >= 7:   return C_GREEN
    if score >= 5:   return C_AMBER
    return C_RED

def score_bg(score):
    if score >= 7:   return C_GREEN_BG
    if score >= 5:   return C_AMBER_BG
    return C_RED_BG

def score_label(score):
    if score >= 8.5: return "Excellent"
    if score >= 7:   return "Good"
    if score >= 5:   return "Average"
    if score >= 3:   return "Below Average"
    return "Needs Improvement"

def score_bar(score, width=20):
    filled = int((score / 10) * width)
    return "█" * filled + "░" * (width - filled)

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
        rightMargin=0.65*inch,
        leftMargin=0.65*inch,
        topMargin=0.65*inch,
        bottomMargin=0.65*inch
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Styles ──
    def S(name, **kwargs):
        return ParagraphStyle(name, parent=styles["Normal"], **kwargs)

    s_title     = S("t", fontSize=24, fontName="Helvetica-Bold", textColor=C_DARK, alignment=TA_CENTER, spaceAfter=2)
    s_sub       = S("s", fontSize=10, textColor=C_GRAY, alignment=TA_CENTER, spaceAfter=2)
    s_section   = S("sec", fontSize=13, fontName="Helvetica-Bold", textColor=C_DARK, spaceBefore=18, spaceAfter=8)
    s_body      = S("b", fontSize=9.5, textColor=colors.HexColor("#333333"), leading=15, spaceAfter=3)
    s_small     = S("sm", fontSize=8.5, textColor=C_GRAY, leading=13)
    s_center    = S("c", fontSize=9.5, textColor=colors.HexColor("#333333"), alignment=TA_CENTER)
    s_green     = S("g", fontSize=9, textColor=C_GREEN, fontName="Helvetica-Bold")
    s_amber     = S("a", fontSize=9, textColor=C_AMBER, fontName="Helvetica-Bold")
    s_red_s     = S("r", fontSize=9, textColor=C_RED,   fontName="Helvetica-Bold")

    date_str = datetime.now().strftime("%B %d, %Y")

    # ════════════════════════════════════════
    # SECTION 1 — HEADER
    # ════════════════════════════════════════
    story.append(Paragraph("AI Interview Simulator", s_title))
    story.append(Paragraph("Candidate Performance Report", s_sub))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=2, color=C_DARK))
    story.append(Spacer(1, 10))

    info = [
        ["Candidate Name", candidate_name,  "Date",             date_str],
        ["Target Role",    target_role,      "Experience Level", experience_level.title()],
    ]
    info_t = Table(info, colWidths=[1.3*inch, 2.4*inch, 1.3*inch, 2.2*inch])
    info_t.setStyle(TableStyle([
        ("FONTNAME",    (0,0), (-1,-1), "Helvetica"),
        ("FONTNAME",    (0,0), (0,-1),  "Helvetica-Bold"),
        ("FONTNAME",    (2,0), (2,-1),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9.5),
        ("TEXTCOLOR",   (0,0), (-1,-1), colors.HexColor("#333333")),
        ("TEXTCOLOR",   (0,0), (0,-1),  C_DARK),
        ("TEXTCOLOR",   (2,0), (2,-1),  C_DARK),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("TOPPADDING",  (0,0), (-1,-1), 6),
    ]))
    story.append(info_t)
    story.append(Spacer(1, 12))

    # ════════════════════════════════════════
    # SECTION 2 — OVERALL SCORE
    # ════════════════════════════════════════
    if answer_scores:
        valid = [s for s in answer_scores if s.get("overall_score") is not None]
        avg   = sum(s["overall_score"] for s in valid) / len(valid) if valid else 0
        label = score_label(avg)
        col   = score_color(avg)
        bg    = score_bg(avg)

        story.append(Paragraph("Overall Performance", s_section))

        overall_data = [[
            Paragraph(
                f"<font size='30' color='#1a1a2e'><b>{avg:.1f}</b></font>"
                f"<font size='13' color='#888888'> / 10</font>",
                s_center
            ),
            Paragraph(
                f"<font size='15' color='{col.hexval()}'><b>{label}</b></font><br/><br/>"
                f"<font size='9' color='#888888'>{len(valid)} questions evaluated  •  "
                f"Target Role: {target_role}  •  Level: {experience_level.title()}</font>",
                s_body
            ),
            Paragraph(
                f"<font size='9' color='#555555'>"
                f"<b>Score distribution</b><br/>"
                f"8-10 (Excellent): {sum(1 for s in valid if s['overall_score']>=8)}<br/>"
                f"6-8  (Good):      {sum(1 for s in valid if 6<=s['overall_score']<8)}<br/>"
                f"4-6  (Average):   {sum(1 for s in valid if 4<=s['overall_score']<6)}<br/>"
                f"0-4  (Weak):      {sum(1 for s in valid if s['overall_score']<4)}"
                f"</font>",
                s_body
            )
        ]]
        overall_t = Table(overall_data, colWidths=[1.3*inch, 3.2*inch, 2.7*inch])
        overall_t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (0,0), bg),
            ("BACKGROUND",   (1,0), (1,0), C_LIGHT),
            ("BACKGROUND",   (2,0), (2,0), colors.HexColor("#f0f4ff")),
            ("ALIGN",        (0,0), (0,0), "CENTER"),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("BOTTOMPADDING",(0,0), (-1,-1), 14),
            ("TOPPADDING",   (0,0), (-1,-1), 14),
            ("LEFTPADDING",  (0,0), (-1,-1), 14),
            ("GRID",         (0,0), (-1,-1), 0.5, C_BORDER),
        ]))
        story.append(overall_t)

    # ════════════════════════════════════════
    # SECTION 3 — SCORE BREAKDOWN BY METRIC
    # ════════════════════════════════════════
    story.append(Paragraph("Score Breakdown by Metric", s_section))

    metrics = [
        ("technical_accuracy", "Technical Accuracy",
         "Correctness of technical answers, terminology, and concepts"),
        ("depth",              "Answer Depth",
         "How deeply the candidate explained reasoning, trade-offs, and specifics"),
        ("clarity",            "Communication Clarity",
         "Structure, articulation, and ease of understanding"),
        ("confidence",         "Confidence Level",
         "How assured and decisive the candidate sounded in responses"),
    ]

    breakdown_data = [["Metric", "Avg Score", "Visual Bar", "Rating", "What This Means"]]
    for key, label, meaning in metrics:
        vals = [s.get(key, 0) for s in answer_scores if s.get(key) is not None]
        if not vals:
            continue
        avg_m  = sum(vals) / len(vals)
        col    = score_color(avg_m)
        rating = "Strong" if avg_m >= 7 else "Average" if avg_m >= 5 else "Weak"
        breakdown_data.append([
            Paragraph(f"<b>{label}</b>", s_body),
            Paragraph(f"<font color='{col.hexval()}'><b>{avg_m:.1f}</b></font>", s_center),
            Paragraph(f"<font size='8' color='{col.hexval()}'>{score_bar(avg_m, 15)}</font>", s_body),
            Paragraph(f"<font color='{col.hexval()}'>{rating}</font>", s_center),
            Paragraph(f"<font size='8' color='#666666'>{meaning}</font>", s_body),
        ])

    if len(breakdown_data) > 1:
        bd_t = Table(breakdown_data,
                     colWidths=[1.5*inch, 0.75*inch, 1.3*inch, 0.75*inch, 2.9*inch])
        bd_t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0),  C_DARK),
            ("TEXTCOLOR",     (0,0), (-1,0),  C_WHITE),
            ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,0),  9),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [C_LIGHT, C_WHITE]),
            ("GRID",          (0,0), (-1,-1), 0.3, C_BORDER),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ]))
        story.append(bd_t)

    # ════════════════════════════════════════
    # SECTION 4 — SKILL ANALYSIS
    # ════════════════════════════════════════
    story.append(Paragraph("Skill-by-Skill Analysis", s_section))

    strong   = interview_plan.get("strong_skills",   [])
    weak     = interview_plan.get("weak_skills",     [])
    missing  = interview_plan.get("missing_skills",  [])
    focus    = interview_plan.get("focus_areas",     [])

    skill_data = [[
        Paragraph("<b>✓ Strong Skills</b><br/>"
                  "<font size='8' color='#555555'>Candidate demonstrated solid knowledge</font>",
                  s_green),
        Paragraph("<b>⚠ Needs Improvement</b><br/>"
                  "<font size='8' color='#555555'>Present but answers lacked depth</font>",
                  s_amber),
        Paragraph("<b>✗ Missing Skills</b><br/>"
                  "<font size='8' color='#555555'>Not demonstrated or absent from resume</font>",
                  s_red_s),
    ],[
        Paragraph("\n".join(f"• {s}" for s in strong)  if strong  else "None identified", s_body),
        Paragraph("\n".join(f"• {s}" for s in weak)    if weak    else "None identified", s_body),
        Paragraph("\n".join(f"• {s}" for s in missing) if missing else "None identified", s_body),
    ]]

    skill_t = Table(skill_data, colWidths=[2.35*inch, 2.35*inch, 2.35*inch])
    skill_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,-1), C_GREEN_BG),
        ("BACKGROUND",    (1,0), (1,-1), C_AMBER_BG),
        ("BACKGROUND",    (2,0), (2,-1), C_RED_BG),
        ("GRID",          (0,0), (-1,-1), 0.3, C_BORDER),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    story.append(skill_t)

    # ════════════════════════════════════════
    # SECTION 5 — QUESTION BY QUESTION REVIEW
    # ════════════════════════════════════════
    story.append(Paragraph("Question-by-Question Review", s_section))

    questions = [m["content"] for m in conversation_history if m["role"] == "assistant"]
    answers   = [m["content"] for m in conversation_history if m["role"] == "user"]

    for i, (q, a, sc) in enumerate(zip(questions, answers, answer_scores)):
        sv  = sc.get("overall_score", 0)
        col = score_color(sv)
        bg  = score_bg(sv)
        fb  = sc.get("feedback",    "")
        imp = sc.get("improvement", "")

        q_short = q[:140] + ("..." if len(q) > 140 else "")
        a_short = a[:200] + ("..." if len(a) > 200 else "")

        block = [
            # Header row
            [
                Paragraph(f"<font color='#888888' size='8'><b>Q{i+1}</b></font>  "
                          f"<font size='9.5'><b>{q_short}</b></font>", s_body),
                Paragraph(
                    f"<font size='16' color='{col.hexval()}'><b>{sv}</b></font>"
                    f"<font size='9' color='#888888'>/10</font><br/>"
                    f"<font size='8' color='{col.hexval()}'>{score_label(sv)}</font>",
                    s_center
                )
            ],
            # Answer row
            [
                Paragraph(f"<font size='8' color='#555555'><b>Answer: </b>{a_short}</font>", s_small),
                Paragraph("", s_small)
            ],
            # Feedback row
            [
                Paragraph(
                    f"<font size='8.5' color='#1a7a4a'>✓ {fb}</font><br/>"
                    f"<font size='8.5' color='#b85c00'>→ {imp}</font>",
                    s_body
                ),
                Paragraph("", s_body)
            ]
        ]

        q_t = Table(block, colWidths=[5.7*inch, 1.1*inch])
        q_t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), C_LIGHT),
            ("BACKGROUND",    (1,0), (1,0),  bg),
            ("BACKGROUND",    (0,1), (-1,1), C_WHITE),
            ("BACKGROUND",    (0,2), (-1,2), colors.HexColor("#fafafa")),
            ("GRID",          (0,0), (-1,-1), 0.3, C_BORDER),
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
            ("ALIGN",         (1,0), (1,0),   "CENTER"),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("TOPPADDING",    (0,0), (-1,-1), 7),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("SPAN",          (0,1), (1,1)),
            ("SPAN",          (0,2), (1,2)),
        ]))
        story.append(KeepTogether(q_t))
        story.append(Spacer(1, 6))

    # ════════════════════════════════════════
    # SECTION 6 — WHAT TO STUDY NEXT (DETAILED)
    # ════════════════════════════════════════
    story.append(Paragraph("Personalised Study Roadmap", s_section))

    # Topic → resource mapping
    study_map = {
        "RAG":                  ("Retrieval-Augmented Generation",    "LangChain RAG docs, Pinecone learning center, 'RAG vs Fine-tuning' papers on arXiv"),
        "LangChain":            ("LangChain Framework",               "LangChain official docs, LangChain cookbook on GitHub, Greg Kamradt tutorials"),
        "LangGraph":            ("LangGraph Multi-Agent",             "LangGraph docs, LangChain blog on agent patterns, 'Building agents with LangGraph' YouTube series"),
        "Vector DBs":           ("Vector Database Internals",         "Qdrant docs, FAISS GitHub, 'HNSW algorithm' paper, Weaviate blog on indexing"),
        "LLM fine-tuning":      ("LoRA / QLoRA Fine-tuning",          "Unsloth GitHub, HuggingFace PEFT docs, 'LoRA paper' on arXiv, Tim Dettmers QLoRA blog"),
        "FastAPI":              ("FastAPI & Async Python",            "FastAPI official docs, 'Full Stack FastAPI' template, TestDriven.io FastAPI course"),
        "AWS deployment":       ("Cloud Deployment",                  "AWS EC2 + Docker tutorial, 'Deploying FastAPI on AWS' blog, Render.com for quick hosting"),
        "ChromaDB":             ("ChromaDB & Vector Storage",         "ChromaDB docs, 'Building a RAG app with Chroma' tutorial, embedding model comparisons"),
        "Prompt Engineering":   ("Advanced Prompt Engineering",       "OpenAI prompt engineering guide, 'Prompt Engineering Guide' by DAIR.AI on GitHub"),
        "Docker":               ("Docker & Containerisation",         "Docker official getting started, 'Docker for Python devs' tutorial, DockerHub"),
    }

    topics_to_study = list(set(focus + missing + weak))

    if topics_to_study:
        study_data = [["#", "Topic", "Why You Need This", "Where to Study"]]
        for idx, topic in enumerate(topics_to_study, 1):
            matched_key = next((k for k in study_map if k.lower() in topic.lower()
                               or topic.lower() in k.lower()), None)
            if matched_key:
                full_name, resources = study_map[matched_key]
            else:
                full_name  = topic
                resources  = "Search official docs and recent blog posts for this topic"

            study_data.append([
                Paragraph(f"<b>{idx}</b>", s_center),
                Paragraph(f"<b>{full_name}</b>", s_body),
                Paragraph(
                    f"Appeared as a gap in your interview. "
                    f"Questions on this topic scored below average.",
                    s_small
                ),
                Paragraph(f"<font size='8'>{resources}</font>", s_small),
            ])

        study_t = Table(study_data, colWidths=[0.3*inch, 1.4*inch, 1.8*inch, 3.7*inch])
        study_t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0),  C_DARK),
            ("TEXTCOLOR",     (0,0), (-1,0),  C_WHITE),
            ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,0),  9),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [C_LIGHT, C_WHITE]),
            ("GRID",          (0,0), (-1,-1), 0.3, C_BORDER),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ]))
        story.append(study_t)

    # ════════════════════════════════════════
    # SECTION 7 — INTERVIEW SUMMARY & NEXT STEPS
    # ════════════════════════════════════════
    story.append(Paragraph("Summary & Next Steps", s_section))

    avg_final = sum(s.get("overall_score", 0) for s in answer_scores) / len(answer_scores) if answer_scores else 0

    if avg_final >= 7:
        summary = (
            f"{candidate_name} performed strongly in this interview for the {target_role} role. "
            f"Technical knowledge was clearly demonstrated across most topics. "
            f"Focus on deepening the missing skills listed above before the real interview."
        )
        action = "Schedule a mock panel interview. Practice system design questions. Review missing skills once."
    elif avg_final >= 5:
        summary = (
            f"{candidate_name} showed a reasonable foundation for the {target_role} role but "
            f"answers lacked depth and specific technical detail in several areas. "
            f"The candidate knows the concepts but struggles to articulate them precisely."
        )
        action = ("Revise all weak skill areas listed above. Practice explaining concepts out loud. "
                  "Do 2-3 more mock interviews before applying.")
    else:
        summary = (
            f"{candidate_name} needs significant preparation before interviewing for the {target_role} role. "
            f"Many answers were too vague or off-topic. Core concepts in the required skill areas "
            f"need to be studied and practiced with real project experience."
        )
        action = ("Study each topic in the roadmap above systematically. Build 1-2 small projects "
                  "using the missing skills. Re-attempt this simulator after 2 weeks of focused prep.")

    summary_data = [
        [Paragraph("<b>Assessment</b>", s_body),  Paragraph(summary, s_body)],
        [Paragraph("<b>Action Plan</b>", s_body), Paragraph(action,  s_body)],
        [Paragraph("<b>Re-attempt</b>", s_body),
         Paragraph(f"Recommended after {'1 week' if avg_final>=7 else '2 weeks' if avg_final>=5 else '3-4 weeks'} "
                   f"of focused study on the topics above.", s_body)],
    ]
    sum_t = Table(summary_data, colWidths=[1.1*inch, 6.1*inch])
    sum_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,-1), C_LIGHT),
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("GRID",          (0,0), (-1,-1), 0.3, C_BORDER),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    story.append(sum_t)

    # ── Footer ──
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"AI Interview Simulator  •  Confidential Report  •  {date_str}",
        S("ft", fontSize=8, textColor=C_GRAY, alignment=TA_CENTER)
    ))

    doc.build(story)
    print(f"\n[REPORT] PDF saved: {output_path}")
    return output_path


if __name__ == "__main__":
    sample_plan = {
        "candidate_name": "Smit Pandit",
        "strong_skills":  ["LangChain", "RAG pipelines", "FastAPI", "ChromaDB"],
        "weak_skills":    ["Prompt Engineering", "Docker"],
        "missing_skills": ["LLM fine-tuning (LoRA)", "AWS deployment"],
        "focus_areas":    ["RAG", "Vector DBs", "LangGraph"],
    }
    sample_history = [
        {"role": "assistant", "content": "Explain how RAG reduces hallucinations."},
        {"role": "user",      "content": "RAG retrieves relevant chunks and injects them as context so the model answers from facts not memory."},
        {"role": "assistant", "content": "What chunking strategy did you use in RepoMind?"},
        {"role": "user",      "content": "I used RecursiveCharacterTextSplitter with 500 token chunks and 50 token overlap."},
        {"role": "assistant", "content": "Tell me about a challenge you faced in a team project."},
        {"role": "user",      "content": "We disagreed on architecture but resolved it by testing both approaches and picking the better one."},
        {"role": "assistant", "content": "How would you deploy a FastAPI app at scale?"},
        {"role": "user",      "content": "Docker + Kubernetes with a load balancer, JWT auth, Prometheus for monitoring."},
        {"role": "assistant", "content": "Describe a time you learned from failure."},
        {"role": "user",      "content": "I rushed a feature without proper testing, it broke in production. After that I always write tests first."},
    ]
    sample_scores = [
        {"overall_score": 8.2, "technical_accuracy": 8, "depth": 8, "clarity": 9, "confidence": 8,
         "feedback": "Strong answer covering key RAG concepts clearly.", "improvement": "Could also mention reranking strategies."},
        {"overall_score": 7.5, "technical_accuracy": 8, "depth": 7, "clarity": 8, "confidence": 7,
         "feedback": "Specific answer with exact numbers — very good.", "improvement": "Mention why overlap size matters for retrieval."},
        {"overall_score": 6.0, "technical_accuracy": 0, "depth": 6, "clarity": 7, "confidence": 6,
         "feedback": "Clear structure and good communication.", "improvement": "Give more specific detail about your personal contribution."},
        {"overall_score": 7.8, "technical_accuracy": 8, "depth": 8, "clarity": 7, "confidence": 8,
         "feedback": "Solid deployment knowledge demonstrated.", "improvement": "Mention CI/CD pipeline and auto-scaling policies."},
        {"overall_score": 7.0, "technical_accuracy": 6, "depth": 7, "clarity": 8, "confidence": 7,
         "feedback": "Good self-awareness and clear lesson learned.", "improvement": "Could quantify the impact of the failure more specifically."},
    ]

    generate_report(
        candidate_name   = "Smit Pandit",
        target_role      = "AI Engineer",
        experience_level = "fresher",
        interview_plan   = sample_plan,
        conversation_history = sample_history,
        answer_scores    = sample_scores,
        output_path      = "test_report_v2.pdf"
    )