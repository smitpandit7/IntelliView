import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def should_followup(question: str, answer: str) -> bool:
    
    # Clean whitespace before counting
    word_count = len(answer.strip().split())
    if word_count > 60:
        return False

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

    prompt = f"""
    You are evaluating whether an interview answer needs a follow-up question.

    Question: {question}
    Answer: {answer}

    Scoring criteria:
    - If answer is less than 1 sentences: YES
    - If answer uses vague words like "some", "a few", "things", "stuff" without details: YES
    - If answer mentions something specific but doesn't explain HOW or WHY: YES
    - If answer is more than 2 sentences AND covers the how/why/what: NO
    - If answer gives a clear technical explanation with steps or examples: NO

    Reply with ONLY one word: YES or NO
    """

    response = llm.invoke(prompt)
    return response.content.strip().upper() == "YES"

def generate_followup_question(question: str, answer: str) -> str:
    """Generate a follow-up based on what the candidate actually said."""
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)

    prompt = f"""
    You are an interviewer conducting a follow-up.
    
    Original question: {question}
    Candidate's answer: {answer}
    
    Generate ONE follow-up question that:
    - Digs deeper into something specific the candidate mentioned
    - Asks them to elaborate on a vague point
    - Challenges them to give a concrete example if they spoke generally
    - Feels natural, like a real human interviewer would ask
    
    Rules:
    - ONE question only
    - Reference something the candidate actually said
    - Do not ask two question by combining two topics into one
    - Do not repeat the original question
    - Do not give feedback or preamble
    - Just ask the question
    """
    response = llm.invoke(prompt)
    return response.content.strip()
