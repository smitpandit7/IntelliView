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
    current_question_type: str

    # Scoring
    answer_scores: List[dict]
    question_count: int
    followup_count: int  # max 1 followup per question

    # Control
    is_complete: bool
    final_report: Optional[dict]