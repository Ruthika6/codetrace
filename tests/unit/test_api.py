"""Unit tests for FastAPI REST Gateway layer."""

import pytest
from fastapi.testclient import TestClient
from codetrace.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_api_search():
    response = client.post(
        "/api/search",
        json={"query": "authenticate_user", "top_k": 2, "mode": "hybrid_rerank"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


def test_api_investigate():
    response = client.post(
        "/api/investigate",
        json={
            "query": "Why does login fail?",
            "stack_trace": "Traceback (most recent call last):\n  File \"auth.py\", line 42, in auth\nExpiredSignatureError",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "markdown_report" in data
    assert data["confidence_score"] > 0.0
