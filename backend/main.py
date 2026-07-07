import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import tempfile

from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver

from graph.interview_graph import build_interview_graph
from graph.state import InterviewState
from parsers.resume_parser import extract_text_from_pdf
from report.generator import generate_report

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from voice.tts import text_to_speech_bytes
from voice.stt import transcribe_audio

app = FastAPI(title="AI Interview Simulator", version="1.0.0")

# ── CORS — allows React frontend to call this API ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory session store ──
# Stores: thread_id → { graph_app, config, interview_plan, last_question }
sessions = {}

# ── Request/Response models ──
class StartResponse(BaseModel):
    session_id: str
    opening_message: str
    question: str
    question_type: str
    question_number: int

class AnswerRequest(BaseModel):
    session_id: str
    answer: str

class AnswerResponse(BaseModel):
    question: str
    question_type: str
    question_number: int
    last_score: float
    last_feedback: str
    is_complete: bool

class ReportResponse(BaseModel):
    session_id: str
    candidate_name: str
    average_score: float
    total_questions: int
    report_path: str


# ── Route 1: Start interview ──
@app.post("/interview/start", response_model=StartResponse)
async def start_interview(
    resume: UploadFile = File(...),
    jd_text: str = Form(...),
    target_role: str = Form(...),
    experience_level: str = Form(...)
):
    # Save uploaded PDF to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await resume.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        resume_text = extract_text_from_pdf(tmp_path)
    finally:
        os.unlink(tmp_path)  # delete temp file

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from resume PDF.")

    # Create unique session
    session_id = str(uuid.uuid4())
    thread_id = f"interview_{session_id}"
    config = {"configurable": {"thread_id": thread_id}}

    # Build graph with checkpointer
    graph_app = build_interview_graph()

    initial_state = InterviewState(
        resume_text=resume_text,
        jd_text=jd_text,
        target_role=target_role,
        experience_level=experience_level,
        resume_json={},
        jd_json={},
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

    # Run graph until first interrupt
    result = graph_app.invoke(initial_state, config=config)

    if "__interrupt__" not in result:
        raise HTTPException(status_code=500, detail="Graph did not pause at expected interrupt point.")

    interrupt_data = result["__interrupt__"][0].value

    # Store session
    sessions[session_id] = {
        "graph_app": graph_app,
        "config": config,
        "interview_plan": {},  # will be populated after setup node
        "candidate_name": "Candidate",
        "target_role": target_role,
        "experience_level": experience_level,
        "resume_text": resume_text,
        "last_result": result
    }

    return StartResponse(
        session_id=session_id,
        opening_message=f"Welcome to your {target_role} interview. Let's get started.",
        question=interrupt_data["question"],
        question_type=interrupt_data["question_type"],
        question_number=interrupt_data["question_count"] + 1
    )


# ── Route 2: Submit answer, get next question ──
@app.post("/interview/answer", response_model=AnswerResponse)
async def submit_answer(body: AnswerRequest):
    session = sessions.get(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    graph_app = session["graph_app"]
    config = session["config"]

    # Resume graph with candidate's answer
    result = graph_app.invoke(
        Command(resume=body.answer),
        config=config
    )
    if "interview_plan" in result and result["interview_plan"]:
        plan = result["interview_plan"]
        sessions[body.session_id]["candidate_name"] = plan.get("candidate_name", "Candidate")
        sessions[body.session_id]["interview_plan"] = plan

    # Check if interview is complete
    if "__interrupt__" not in result:
        # Graph reached END
        sessions[body.session_id]["last_result"] = result
        sessions[body.session_id]["final_state"] = result

        scores = result.get("answer_scores", [])
        last_score = scores[-1].get("overall_score", 0) if scores else 0
        last_feedback = scores[-1].get("feedback", "") if scores else ""

        return AnswerResponse(
            question="",
            question_type="",
            question_number=result.get("question_count", 0),
            last_score=last_score,
            last_feedback=last_feedback,
            is_complete=True
        )

    # Interview still going — return next question
    interrupt_data = result["__interrupt__"][0].value
    sessions[body.session_id]["last_result"] = result

    scores = result.get("answer_scores", [])
    last_score = scores[-1].get("overall_score", 0) if scores else 0
    last_feedback = scores[-1].get("feedback", "") if scores else ""

    return AnswerResponse(
        question=interrupt_data["question"],
        question_type=interrupt_data["question_type"],
        question_number=interrupt_data["question_count"] + 1,
        last_score=last_score,
        last_feedback=last_feedback,
        is_complete=False
    )


# ── Route 3: Generate PDF report ──
@app.get("/interview/report/{session_id}")
async def get_report(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    final_state = session.get("final_state")
    if not final_state:
        raise HTTPException(status_code=400, detail="Interview not complete yet.")

    scores = final_state.get("answer_scores", [])
    avg = sum(s.get("overall_score", 0) for s in scores) / len(scores) if scores else 0

    report_path = f"reports/report_{session_id}.pdf"
    os.makedirs("reports", exist_ok=True)

    generate_report(
        candidate_name=session.get("candidate_name", "Candidate"),
        target_role=session.get("target_role", ""),
        experience_level=session.get("experience_level", ""),
        interview_plan=final_state.get("interview_plan", {}),
        conversation_history=final_state.get("conversation_history", []),
        answer_scores=scores,
        output_path=report_path
    )

    return ReportResponse(
        session_id=session_id,
        candidate_name=session.get("candidate_name", "Candidate"),
        average_score=round(avg, 2),
        total_questions=final_state.get("question_count", 0),
        report_path=report_path
    )


# ── Route 4: Get session status ──
@app.get("/interview/status/{session_id}")
async def get_status(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    last_result = session.get("last_result", {})
    scores = last_result.get("answer_scores", [])
    avg = sum(s.get("overall_score", 0) for s in scores) / len(scores) if scores else 0

    return {
        "session_id": session_id,
        "question_count": last_result.get("question_count", 0),
        "average_score": round(avg, 2),
        "is_complete": "final_state" in session,
        "scores": [s.get("overall_score") for s in scores]
    }

# ── Route 5: TTS — convert question text to audio ──
@app.post("/voice/speak")
async def speak_question(body: dict):
    """FrontEnd calls this to get audio for a question."""
    text = body.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="NO Text Provided")
    
    try:
        audio_bytes = text_to_speech_bytes(text)
        return Response(
            content=audio_bytes,
            media_type="audio.mpeg",
            headers={"Content-Disposition": "inline; filename=question.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")
    
@app.post("/voice/transcribe")
async def transcribe_answer(audio: UploadFile = File(...)):
    """Frontend sends recorded audio, gets back transcript."""
    audio_bytes = await audio.read()
    filename    = audio.filename or "audio.webm"
    fmt         = filename.split(".")[-1] if "." in filename else "webm"

    try:
        transcript = transcribe_audio(audio_bytes, format=fmt)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT failed: {str(e)}")

# ── Health check ──
@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI Interview Simulator"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)