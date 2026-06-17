import json
from langchain_groq import ChatGroq

def parse_jd(jd_text: str) -> dict:
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

    prompt = f"""
    Extract structured information from this job description.
    Return ONLY valid JSON.
    {{
      "role": "",
      "required_skills": [],
      "nice_to_have": [],
      "responsibilities": [],
      "experience_required": ""
    }}
    
    Job Description:
    {jd_text}
    """

    response = llm.invoke(prompt)

    try:
        return json.loads(response.content)
    except:
        import re
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        return json.loads(match.group(0)) if match else {}