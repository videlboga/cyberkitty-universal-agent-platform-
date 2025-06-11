import pytest
from fastapi.testclient import TestClient
from app.main import app
from loguru import logger
import os

os.makedirs("logs", exist_ok=True)
logger.add("logs/unit_tests.log", format="{time} {level} {message}", level="INFO", rotation="5 MB", compression="zip", serialize=True)

client = TestClient(app)

def test_llm_query():
    payload = {"prompt": "Hello, LLM!"}
    response = client.post("/integration/llm/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "LLM mock response"
    assert data["input"] == payload
    logger.info("test_llm_query: success")

def test_rag_query():
    payload = {"query": "Find info"}
    response = client.post("/integration/rag/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "RAG mock response" in data["result"]
    assert data["input"] == payload
    logger.info("test_rag_query: success")

def test_crm_query():
    payload = {"action": "create_lead", "data": {"name": "Test"}}
    response = client.post("/integration/crm/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "CRM mock response"
    assert data["input"] == payload
    logger.info("test_crm_query: success") 