import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_token():
    res = client.post("/api/auth/login", json={
        "email": "student@learnforge.ai",
        "password": "password123"
    })
    return res.json()["access_token"]

def test_dashboard_metrics():
    token = get_auth_token()
    res = client.get("/api/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["total_materials_uploaded"] >= 2
    assert data["total_tests_completed"] >= 1
    assert "weekly_performance" in data
    assert "daily_challenge" in data

def test_document_listing_and_summary():
    token = get_auth_token()
    res = client.get("/api/documents", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) >= 1
    doc_id = docs[0]["id"]

    sum_res = client.get(f"/api/documents/{doc_id}/summary", headers={"Authorization": f"Bearer {token}"})
    assert sum_res.status_code == 200
    sum_data = sum_res.json()
    assert "summary_text" in sum_data
    assert "key_concepts" in sum_data

def test_generate_test_and_exam_flow():
    token = get_auth_token()
    docs = client.get("/api/documents", headers={"Authorization": f"Bearer {token}"}).json()
    doc_id = docs[0]["id"]

    # 1. Generate test
    gen_res = client.post("/api/tests/generate", json={
        "document_ids": [doc_id],
        "title": "Automated Test Run Assessment",
        "question_count": 3,
        "difficulty": "medium",
        "test_type": "timed_exam",
        "time_limit_minutes": 15,
        "negative_marking": True,
        "negative_mark_value": 0.25
    }, headers={"Authorization": f"Bearer {token}"})
    assert gen_res.status_code == 200
    test_data = gen_res.json()
    test_id = test_data["id"]
    assert len(test_data["questions"]) == 3

    # Verify answers are masked in question options
    for q in test_data["questions"]:
        for opt in q["options"]:
            assert "is_correct" not in opt

    # 2. Start exam
    start_res = client.post(f"/api/tests/{test_id}/start", headers={"Authorization": f"Bearer {token}"})
    assert start_res.status_code == 200
    attempt_data = start_res.json()
    attempt_id = attempt_data["attempt_id"]
    assert "server_deadline" in attempt_data

    # 3. Autosave answer for Q0
    first_q_id = test_data["questions"][0]["id"]
    save_res = client.put(f"/api/attempts/{attempt_id}/answers/{first_q_id}", json={
        "selected_option_key": "A",
        "is_marked_for_review": False
    }, headers={"Authorization": f"Bearer {token}"})
    assert save_res.status_code == 200
    assert save_res.json()["selected_option_key"] == "A"

    # 4. Submit exam
    submit_res = client.post(f"/api/attempts/{attempt_id}/submit", json={
        "answers": {str(first_q_id): "A"}
    }, headers={"Authorization": f"Bearer {token}"})
    assert submit_res.status_code == 200
    result_data = submit_res.json()
    assert result_data["status"] == "submitted"
    assert result_data["grade"] in ["S", "A", "B", "C", "D", "F"]
    assert "ai_summary_feedback" in result_data
    assert len(result_data["question_results"]) == 3

    # Check 7-step AI feedback is present for any mistake
    for qr in result_data["question_results"]:
        if not qr["is_correct"] and qr["ai_feedback"]:
            fb = qr["ai_feedback"]
            assert "what_correct_answer_is" in fb
            assert "why_selected_incorrect" in fb
            assert "underlying_concept" in fb

def test_doubt_solver():
    token = get_auth_token()
    res = client.post("/api/doubts/ask", json={
        "query": "What is the role of randomized election timeouts?"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "response_text" in data
    assert len(data["citations"]) >= 1
    assert data["citations"][0]["document_title"] is not None

def test_pdf_export():
    token = get_auth_token()
    # List attempts
    attempts = client.get("/api/attempts", headers={"Authorization": f"Bearer {token}"}).json()
    assert len(attempts) >= 1
    attempt_id = attempts[0]["id"]

    pdf_res = client.get(f"/api/export/attempts/{attempt_id}/pdf", headers={"Authorization": f"Bearer {token}"})
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000  # Non-trivial PDF generated
