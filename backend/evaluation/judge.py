import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import re
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def judge_answer(question:str, answer:str , question_type: str = "technical") -> str:
    """
    question_type: "technical" or "hr"
    """
    llm = ChatGroq(model = "llama-3.1-8b-instant", temperature=0)

    if question_type == "technical":
        criteria = """
        - technical_accuracy (0-10): Is the answer technically correct?
        - depth (0-10): Did they explain HOW and WHY, not just WHAT?
        - clarity (0-10): Was the explanation clear and structured?
        - confidence (0-10): Did the answer sound confident and certain?
        """
    else:
        criteria = """
        - relevance (0-10): Did they answer what was actually asked?
        - communication (0-10): Was it clear, structured, easy to follow?
        - depth (0-10): Did they give specific examples or stay generic?
        - confidence (0-10): Did the answer sound confident and certain?
        """
    
    prompt = f"""
    You are an expert interview evaluator.

    Question type: {question_type}
    Question: {question}
    Candidate answer: {answer}

    Evaluate the answer on these criteria:
    {criteria}

    Also give:
    - overall_score (0-10): weighted average of above scores
    - feedback: one sentence on what was good
    - improvement: one sentence on what was missing or could be better

    Return ONLY valid JSON, no extra text:
    {{
        "technical_accuracy": 0,
        "depth": 0,
        "clarity": 0,
        "confidence": 0,
        "overall_score": 0,
        "feedback": "",
        "improvement": ""
    }}
    """

    response = llm.invoke(prompt)

    try:
        return json.loads(response.content)
    except:
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        return json.loads(match.group(0)) if match else {}
    

if __name__ == "__main__":
    print("=== JUDGE TEST ===\n")

    # Test 1 — strong technical answer
    q1 = "Explain how RAG reduces hallucinations."
    a1 = """RAG works by retrieving relevant chunks from a vector database and injecting 
    them into the LLM prompt as context. This grounds the model's response in actual data 
    rather than relying purely on parametric memory. The model generates answers based on 
    retrieved evidence, which significantly reduces hallucinations because it has factual 
    context to reference."""

    result1 = judge_answer(q1, a1, "technical")
    print(f"Q: {q1}")
    print(f"Score: {result1.get('overall_score')}/10")
    print(f"Feedback: {result1.get('feedback')}")
    print(f"Improvement: {result1.get('improvement')}\n")

    # Test 2 — weak technical answer
    q2 = "What is the difference between similarity search and hybrid search?"
    a2 = "Similarity search finds similar things and hybrid search combines different methods."

    result2 = judge_answer(q2, a2, "technical")
    print(f"Q: {q2}")
    print(f"Score: {result2.get('overall_score')}/10")
    print(f"Feedback: {result2.get('feedback')}")
    print(f"Improvement: {result2.get('improvement')}\n")

    # Test 3 — HR answer
    q3 = "Tell me about a time you faced a challenge in a team project."
    a3 = "During RepoMind I had a disagreement with my teammate about the chunking strategy. I listened to their approach, explained my reasoning, and we tested both. Mine performed better so we went with it but I made sure they understood why."

    result3 = judge_answer(q3, a3, "hr")
    print(f"Q: {q3}")
    print(f"Score: {result3.get('overall_score')}/10")
    print(f"Feedback: {result3.get('feedback')}")
    print(f"Improvement: {result3.get('improvement')}\n")