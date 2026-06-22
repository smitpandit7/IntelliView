import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END
from graph.state import InterviewState
from agents.resume_agent import run_resume_agent
from agents.technical_agent import generate_technical_question
from agents.hr_agent import generate_HR_question
from agents.followup_agent import should_followup, generate_followup_question
from evaluation.judge import judge_answer
from parsers.resume_parser import extract_text_from_pdf, parse_resume_text
from parsers.jd_parser import parse_jd
from rag.chunker import chunk_resume
from rag.embedder import build_vectorstore

_vectorstore_cache = {}

# --- Node 1 : Parse Resume + JD, Build RAG, Create Interview Plan ---
def setup_node(state: InterviewState) -> InterviewState:
    print("\n[SETUP] Parsing resume and JD...")
    
    resume_json = parse_resume_text(state["resume_text"])
    jd_json = parse_jd(state["jd_text"])

    print("\n[SETUP] RAG...")

    chunks = chunk_resume(state["resume_text"])
    vector_store = build_vectorstore(chunks)
    _vectorstore_cache["store"] = vector_store

    print("\n[SETUP] Creating interview plan...")
    interview_plan = run_resume_agent(
        resume_json,
        jd_json,
        state["experience_level"]
    )

    print(f"[SETUP] Interview plan created for {interview_plan.get('candidate_name')}")
    print(f"[SETUP] Opening: {interview_plan.get('opening_message')}")

    return {
        **state,
        "resume_json": resume_json,
        "jd_json": jd_json,
        "interview_plan": interview_plan,
        "conversation_history": [],
        "answer_scores": [],
        "question_count": 0,
        "followup_count": 0,
        "is_complete": False
    }

# --- Node 2 : Generate Technical Question ---


def technical_node(state: InterviewState) -> InterviewState:

    print("\n[TECHNICAL NODE] Generating technical question...")

    question = generate_technical_question(
        state["interview_plan"],
        _vectorstore_cache["store"],
         state["conversation_history"],
        [s["overall_score"] for s in state["answer_scores"]]
    )

    print(f"[TECHNICAL AGENT] Q: {question}")

    return {
        **state,
        "current_question": question,
        "current_question_type": "technical",
        "followup_count": 0
    }

# --- Node 3 : Generate Technical Question ---

def hr_node(state: InterviewState) -> InterviewState:
    print("\n[HR NODE] Generating HR question...")

    question = generate_HR_question(
        state["interview_plan"],
        _vectorstore_cache["store"],
        state["conversation_history"],
        state["answer_scores"],
    )

    print(f"[HR AGENT] Q: {question}")

    return{
        **state,
        "current_question" : question,
        "current_question_type": "hr",
        "followup_count": 0
    }

# ── Node 4: Evaluate answer ──

def evaluate_node(state: InterviewState) -> InterviewState:
    print("\n[JUDGE] Evaluating Answers...")

    score = judge_answer(
        state["current_question"],
        state["current_answer"],
        state["current_question_type"]
    )

    print(f"[JUDGE] Score: {score.get('overall_score')}/10")
    print(f"[JUDGE] Feedback: {score.get('feedback')}")

    new_history = state["conversation_history"] + [
        {"role": "assistant", "content": state["current_question"]},
        {"role": "user", "content": state["current_answer"]}
    ]

    return {
        **state,
        "conversation_history": new_history,
        "answer_scores": state["answer_scores"] + [score],
        "question_count": state["question_count"] + 1
    }

# ── Node 5: Generate followup ──

def followup_node(state: InterviewState) -> InterviewState:
    print("\n[FOLLOWUP AGENT] Generating follow-up...")

    followup = generate_followup_question(
        state["current_question"],
        state["current_answer"],
    )

    print(f"[FOLLOWUP AGENT] Q: {followup}")

    return {
        **state,
        "current_question": followup,
        "followup_count": state["followup_count"] + 1
    }

# ── Router: After evaluation, where to go next? ──

def should_continue(state: InterviewState) -> str:
    plan = state["interview_plan"]
    total_technical = plan.get("question_plan", {}).get("technical_count", 6)
    total_hr = plan.get("question_plan", {}).get("hr_count", 3)
    total_questions = total_technical + total_hr

    # End interview
    if state["question_count"] >= total_questions:
        return "end"
    
    # Check if last answer needs followup (max 1 per question)
    if state["followup_count"] == 0:
        needs_followup = should_followup(
            state["current_question"],
            state["current_answer"]
        )
        if needs_followup:
            return "followup"
        
    # Alternate between technical and HR
    technical_done = sum(
        1 for h in state["conversation_history"]
        if h["role"] == "assistant" and
        state.get("current_question_type") == "technical"
    )

    # Every 3rd question is HR
    if state["question_count"] % 3 == 2:
        return "hr"

    return "technical"

# --- Build the graph

def build_interview_graph():
    graph = StateGraph(InterviewState)

    graph.add_node("setup", setup_node)
    graph.add_node("technical", technical_node)
    graph.add_node("hr", hr_node)
    graph.add_node("evaluate", evaluate_node)
    graph.add_node("followup", followup_node)

    graph.set_entry_point("setup")

    graph.add_edge("setup","technical")
    graph.add_edge("technical","evaluate")
    graph.add_edge("hr","evaluate")
    graph.add_edge("followup","evaluate")

    graph.add_conditional_edges("evaluate", should_continue,{
        "technical": "technical",
        "hr" : "hr",
        "followup" :"followup",
        "end" : END
    })

    return graph.compile()

if __name__ == "__main__":
    from parsers.resume_parser import extract_text_from_pdf

    resume_text = extract_text_from_pdf("sample_resume.pdf")

    jd_text = """
    AI Engineer role requiring LangChain, RAG, Vector DBs, FastAPI, LLM fine-tuning.
    """

    # Build graph
    app = build_interview_graph()

    # Initial state
    initial_state = InterviewState(
        resume_text=resume_text,
        jd_text=jd_text,
        target_role="AI Engineer",
        experience_level="fresher",
        resume_json={},
        jd_json={},
        vectorstore=None,
        interview_plan={},
        conversation_history=[],
        current_question="",
        current_answer="",
        current_question_type="technical",
        answer_scores=[],
        question_count=0,
        followup_count=0,
        is_complete=False,
        final_report=None
    )

    print("=== INTERVIEW SIMULATION ===\n")
    print("NOTE: In production the answer comes from voice/text input.")
    print("For testing we simulate answers.\n")

    # Simulate one full turn manually
    state = app.invoke(initial_state)

    print("\n[GRAPH] First question generated:")
    print(f"Q: {state['current_question']}")

    # Simulate candidate answering
    state["current_answer"] = "I used ChromaDB with BGE embeddings to store resume chunks and retrieve relevant context for each interview question."

    # Continue graph from evaluate node
    state = app.invoke(state)  

    print(f"\n[GRAPH] Questions asked so far: {state['question_count']}")
    print(f"[GRAPH] Scores so far: {[s['overall_score'] for s in state['answer_scores']]}")