import fitz
import json
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def parse_resume(pdf_path: str) -> dict:
    raw_text = extract_text_from_pdf(pdf_path)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

    prompt = f"""
    Extract structured information from this resume.
    Return ONLY valid JSON, no extra text.
    
    {{
      "name": "",
      "skills": [],
      "projects": [
        {{
          "name": "",
          "description": "",
          "tech_stack": []
        }}
      ],
      "experience": [
        {{
          "company": "",
          "role": "",
          "duration": ""
        }}
      ],
      "education": ""
    }}
    
    Resume:
    {raw_text}
    """

    response = llm.invoke(prompt)

    try:
        return json.loads(response.content)
    except:
        import re
        match = re.search(r'\{.*\}', response.content, re.DOTALL)
        return json.loads(match.group(0)) if match else {} 
    
# Quick test
if __name__ == "__main__":
    result = parse_resume("sample_resume.pdf")
    print(json.dumps(result, indent=2))