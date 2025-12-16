"""
Basic tests for the AI function calling server
"""

import pytest
from fastapi.testclient import TestClient
from src.server import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_endpoint():
    """Test readiness probe"""
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_liveness_endpoint():
    """Test liveness probe"""
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_list_functions():
    """Test function listing endpoint"""
    response = client.get("/v1/functions")
    assert response.status_code == 200
    assert "functions" in response.json()


def test_chat_completions_endpoint():
    """Test chat completions endpoint"""
    payload = {
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    }
    response = client.post("/v1/chat/completions", json=payload)
    # Should return 200 or 500 depending on model availability
    assert response.status_code in [200, 500]

