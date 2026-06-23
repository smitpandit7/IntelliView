# test_api.py — run this from backend folder
import requests
import os

BASE_URL = "http://localhost:8000"

def test_interview():
    print("=== TESTING INTERVIEW API ===\n")

    # Step 1 — Start interview
    resume_path = "SmitPandit_Resume.pdf"
    
    with open(resume_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/interview/start",
            files={"resume": ("resume.pdf", f, "application/pdf")},
            data={
                "jd_text": "AI Engineer role requiring LangChain, RAG, Vector DBs, FastAPI, LLM fine-tuning.",
                "target_role": "AI Engineer",
                "experience_level": "fresher"
            }
        )

    if response.status_code != 200:
        print(f"Error starting interview: {response.text}")
        return

    data = response.json()
    session_id = data["session_id"]
    
    print(f"Session ID: {session_id}")
    print(f"Opening: {data['opening_message']}\n")

    # Step 2 — Interview loop
    question = data["question"]
    q_type = data["question_type"]
    q_num = data["question_number"]
    is_complete = False

    while not is_complete:
        print(f"\n[Q{q_num} - {q_type.upper()}]")
        print(f"{question}")
        print("-" * 60)

        # Real human input
        answer = input("Your answer: ").strip()
        if answer.lower() in ["quit", "exit"]:
            print("Exiting early.")
            break

        # Submit answer
        response = requests.post(
            f"{BASE_URL}/interview/answer",
            json={
                "session_id": session_id,
                "answer": answer
            }
        )

        if response.status_code != 200:
            print(f"Error submitting answer: {response.text}")
            break

        data = response.json()
        is_complete = data["is_complete"]

        if data.get("last_score") is not None:
            print(f"\n✓ Score: {data['last_score']}/10")
            print(f"✓ Feedback: {data['last_feedback']}")

        if not is_complete:
            question = data["question"]
            q_type = data["question_type"]
            q_num = data["question_number"]
        else:
            print("\n=== INTERVIEW COMPLETE ===")

    # Step 3 — Generate report
    print("\nGenerating report...")
    response = requests.get(f"{BASE_URL}/interview/report/{session_id}")
    
    if response.status_code == 200:
        report = response.json()
        print(f"Average Score: {report['average_score']}/10")
        print(f"Total Questions: {report['total_questions']}")
        print(f"Report saved to: {report['report_path']}")
    else:
        print(f"Report error: {response.text}")

if __name__ == "__main__":
    test_interview()