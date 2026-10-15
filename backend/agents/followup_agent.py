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
    - If answer is less than 2 sentences: YES
    - If answer uses vague words like "some", "a few", "things", "stuff" without details: YES
    - If answer mentions something specific but doesn't explain HOW or WHY: YES
    - If answer is more than 4 sentences AND covers the how/why/what: NO
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

if __name__ == "__main__":
    print("=== FOLLOWUP AGENT TEST ===\n")

    # Test 1 — vague answer, should trigger followup
    q1 = "Tell me about your RepoMind project."
    a1 = "I built RepoMind using LangChain and it helps with code understanding."

    needs_followup = should_followup(q1, a1)
    print(f"Answer: '{a1}'")
    print(f"Needs followup: {needs_followup}")
    if needs_followup:
        followup = generate_followup_question(q1, a1)
        print(f"Follow-up: {followup}\n")

    # Test 2 — detailed answer, should NOT trigger followup
    q2 = "Explain how RAG works."
    a2 = """RAG stands for Retrieval Augmented Generation. It works by first converting 
    documents into vector embeddings using a model like BGE or E5. These embeddings are 
    stored in a vector database like ChromaDB. When a user asks a question, the query is 
    also embedded and similarity search finds the most relevant chunks. These chunks are 
    injected into the LLM prompt as context, so the model generates answers grounded in 
    real data rather than hallucinating."""

    print(len(a2.split()))

    needs_followup = should_followup(q2, a2)
    print(f"Word count: {len(a2.strip().split())}")
    print(f"Needs followup: {needs_followup}")

    # Test 3 — candidate mentions something interesting
    q3 = "What challenge did you face in RepoMind?"
    a3 = "I had issues with the embedding retrieval and had to fix a bug in ChromaDB."

    needs_followup = should_followup(q3, a3)
    print(f"Answer: '{a3}'")
    print(f"Needs followup: {needs_followup}")
    if needs_followup:
        followup = generate_followup_question(q3, a3)
        print(f"Follow-up: {followup}\n")