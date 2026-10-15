import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "LearnForge" in data["app"]

def test_login_demo_user():
    response = client.post("/api/auth/login", json={
        "email": "student@learnforge.ai",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["email"] == "student@learnforge.ai"
    assert data["role"] == "student"

def test_login_invalid_credentials():
    response = client.post("/api/auth/login", json={
        "email": "student@learnforge.ai",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_me_authenticated():
    login_res = client.post("/api/auth/login", json={
        "email": "student@learnforge.ai",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "student@learnforge.ai"
    assert data["full_name"] == "Alex Rivera"

def test_register_new_student():
    import uuid
    random_email = f"student_{uuid.uuid4().hex[:6]}@learnforge.ai"
    res = client.post("/api/auth/register", json={
        "email": random_email,
        "password": "strongPassword!123",
        "full_name": "Jordan Lee",
        "academic_level": "Graduate Student",
        "learning_goals": "Prepare for GRE and technical interviews"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == random_email
    assert "access_token" in data
