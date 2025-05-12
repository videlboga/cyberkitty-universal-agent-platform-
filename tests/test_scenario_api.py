import pytest
from fastapi.testclient import TestClient
from app.main import app
from loguru import logger
import os
from pymongo import MongoClient

os.makedirs("logs", exist_ok=True)
logger.add("logs/unit_tests.log", format="{time} {level} {message}", level="INFO", rotation="5 MB", compression="zip", serialize=True)

client = TestClient(app)

def clear_scenario(name):
    client_db = MongoClient("mongodb://localhost:27017/")
    db = client_db["universal_agent"]
    db["scenarios"].delete_many({"name": name})

def test_create_scenario():
    clear_scenario("Test Scenario")
    payload = {"name": "Test Scenario", "steps": [{"type": "message", "text": "Hello"}]}
    response = client.post("/scenarios/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Scenario"
    logger.info("test_create_scenario: success") 