import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from langchain_groq import ChatGroq
from rag.retriever import retrieve_context
from dotenv import load_dotenv

load_dotenv()

def generate_technical_question(
        interview_plan : dict,
        vectorstore,
        conversation_history : list,
        answer_scores: list
) ->str:
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)

    context = retrieve_context(vectorstore, "technical skills projects experience" )

    if len(answer_scores)>= 2:
        recent_avg = sum(answer_scores[-2:]) / 2
        if recent_avg >= 7.5:
            difficulty = "Hard"
        elif recent_avg >= 5:
            difficulty = "Medium"
        else:
            difficulty = "Easy"
    else:
        difficulty = interview_plan.get("difficulty", "medium")

    asked_questions =[
        m["content"] for m in conversation_history if m["role"] == "assistant"
    ]

    prompt = f"""
    You are a strict but fair technical interviewer at a top AI company.
    
    Candidate background from resume:
    {context}
    
    Interview focus areas: {interview_plan.get('focus_areas', [])}
    Strong skills: {interview_plan.get('strong_skills', [])}
    Weak/missing skills: {interview_plan.get('missing_skills', [])}
    Relevant projects: {interview_plan.get('relevant_projects', [])}
    
    Current difficulty level: {difficulty}
    Questions already asked: {asked_questions}
    
    Rules:
    - Ask ONE question only
    - Ask a question that is relevant to the candidate's resume and the interview focus areas
    - Do not ask two question by combining two topics into one
    - Never repeat a question already asked
    - If difficulty is easy: ask concept definitions
    - If difficulty is medium: ask how something works or how they used it
    - If difficulty is hard: ask about internals, tradeoffs, or edge cases
    - Make it specific to their resume — mention their actual projects or skills
    - Do NOT say "Great question" or give any feedback
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

    # Setup
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

    print("=== TECHNICAL AGENT TEST ===\n")

    for i in range(3):
        question = generate_technical_question(
            interview_plan, vectorstore, history, scores
        )
        print(f"Q{i+1}: {question}\n")

        # Simulate answer + score
        fake_answer = "I used ChromaDB with BGE embeddings for semantic search."
        history.append({"role": "assistant", "content": question})
        history.append({"role": "user", "content": fake_answer})

        # Simulate increasing scores to test adaptive difficulty
        scores.append(4 + i * 2)  # 4, 6, 8