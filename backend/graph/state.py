from typing import TypedDict, List, Optional

class InterviewState(TypedDict):
    # Input Data
    resume_text: str
    jd_text: str
    target_role: str
    experience_level : str


    # Parsed + structured data
    resume_json: dict
    jd_json: dict

    # RAG
    vector_store: object

    # Interview Plan from resume agent
    interview_plan: dict

    # Conversation 
    conversation_history: List[dict]
    current_question: str
    current_answer: str

    # Scoring
    answer_score: List[dict]
    question_count : int
    current_phase: str

    # Final
    final_score: Optional[float]