import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from langchain_groq import ChatGroq
from rag.retriever import retrieve_context
from dotenv import load_dotenv

load_dotenv()

def generate_HR_question(
        interview_plan : dict,
        vectorstore,
        conversation_history : list,
        answer_scores: list
) -> str:
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)
    context = retrieve_context(vectorstore, "education background work experience achievements goals" )

    asked_questions =[
        m["content"] for m in conversation_history if m["role"] == "assistant"
    ]
    
    if len(asked_questions) == 0:
        difficulty = "easy"
    elif len(asked_questions) <= 2:
        difficulty = "medium"
    else:
        difficulty = "hard"

    prompt = f"""
You are an HR interviewer, NOT a technical interviewer.

Candidate background:
{context}

Current difficulty: {difficulty}
Interview focus areas: {interview_plan.get('focus_areas', [])}
Experience Level: {interview_plan.get('experience_level', 'Mid-Level')}
Questions already asked: {asked_questions}

Rules:
- Ask ONE question only
- NEVER ask about code, architecture, tools, or technical implementation
- NEVER mention LangChain, RAG, FastAPI, or any technology by name
- Focus ONLY on: background, motivation, teamwork, communication, goals, challenges
- If difficulty is easy: ask about their background, why they chose this field, career goals
- If difficulty is medium: ask about teamwork, handling pressure, learning from failure
- If difficulty is hard: ask about leadership, conflict resolution, decision making
- Do NOT give feedback or say anything before the question
- Just ask the question, nothing else
"""
    response = llm.invoke(prompt)
    return response.content.strip()

if __name__ == "__main__":
    from parsers.resume_parser import parse_resume, extract_text_from_pdf
    from parsers.jd_parser import parse_jd
    from rag.chunker import chunk_resume
    from rag.embedder import build_vectorstore
    from agents.resume_agent import run_resume_agent

    #setup
    resume_json = parse_resume("sample_resume.pdf")
    resume_text = extract_text_from_pdf("sample_resume.pdf")
    chunks = chunk_resume(resume_text)
    vectorstore = build_vectorstore(chunks)

    jd_text = """
    AI Engineer role requiring LangChain, RAG, Vector DBs, FastAPI, LLM fine-tuning.
    """
    jd_json = parse_jd(jd_text)
    interview_plan = run_resume_agent(resume_json, jd_json, "Mid-Level")

    # Simulate 3 questions with increasing scores
    history = []
    scores = []

    print("=== HR AGENT TEST ===\n")

    for i in range(3):
        question = generate_HR_question(
            interview_plan, vectorstore, history, scores
        )
        print(f"Q{i+1}: {question}\n")

        # Simulate answer + score
        fake_answer = "Im a great learner and have experience in weoking as a developer and have worked on many projects"
        history.append({"role": "assistant", "content": question})
        history.append({"role": "user", "content": fake_answer})

        # Simulate increasing scores to test adaptive difficulty
        scores.append(4 + i * 2)  # 4, 6, 8