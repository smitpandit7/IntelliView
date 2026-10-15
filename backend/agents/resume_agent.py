import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def run_resume_agent(resume_json: dict, jd_json: dict, experience_level: str) -> dict:
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3)

    prompt = f"""
    You are an expert interview planner

    Candiate Profile:
    - Name: {resume_json.get('name', 'N/A')}
    - Skills: {', '.join(resume_json.get('skills', []))}
    - Projects: {', '.join([proj['name'] for proj in resume_json.get('projects', [])])}
    - Experience: {', '.join([exp['role'] for exp in resume_json.get('experience', [])])}
    - Level: {experience_level}

    Job Description:
    - Required Skills: {', '.join(jd_json.get('required_skills', []))}
    - Nice to Have: {', '.join(jd_json.get('nice_to_have', []))}
    - Role: {jd_json.get('role', 'N/A')}
    - Experience Level: {experience_level}

    Your job:
    1. Find which required skills the candidate HAS
    2. Find which required skills the candidate is MISSING
    3. Identify which projects are most relevant to this JD
    4. Create an interview plan

    Return ONLY valid JSON:
    {{
      "candidate_name": "",
      "strong_skills": [],
      "weak_skills": [],
      "missing_skills": [],
      "relevant_projects": [],
      "focus_areas": [],
      "difficulty": "",
      "question_plan": {{
        "technical_count": 6,
        "hr_count": 3,
        "start_with": "technical"
      }},
      "opening_message": "Hi [name], welcome to your interview for [role]. Let's get started."
    }}
    """

    response = llm.invoke(prompt)

    try:
        return json.loads(response.content)
    except:
        import re
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        return json.loads(match.group(0)) if match else {}
    
# Test it
if __name__ == "__main__":
    from parsers.resume_parser import parse_resume, extract_text_from_pdf
    from parsers.jd_parser import parse_jd

    resume_json = parse_resume("sample_resume.pdf")
    
    jd_text = """
    We are looking for an AI Engineer with experience in:
    - LangChain, LangGraph
    - RAG pipelines
    - Vector databases (Qdrant, ChromaDB)
    - FastAPI
    - LLM fine-tuning (LoRA, QLoRA)
    - AWS or GCP deployment
    """
    
    jd_json = parse_jd(jd_text)
    
    plan = run_resume_agent(resume_json, jd_json, "Fresher")
    print(json.dumps(plan, indent=2))
