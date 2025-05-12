import pytest
from fastapi.testclient import TestClient
from app.main import app
from loguru import logger
import os
from pymongo import MongoClient

# Настройка логирования тестов
os.makedirs("logs", exist_ok=True)
logger.add("logs/unit_tests.log", format="{time} {level} {message}", level="INFO", rotation="5 MB", compression="zip", serialize=True)

client = TestClient(app)

def clear_user(email):
    client_db = MongoClient("mongodb://localhost:27017/")
    db = client_db["universal_agent"]
    db["users"].delete_many({"email": email})

def test_create_user():
    clear_user("testuser@example.com")
    payload = {"name": "Test User", "email": "testuser@example.com"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    logger.info("test_create_user: success")

def test_get_user():
    clear_user("getuser@example.com")
    payload = {"name": "Get User", "email": "getuser@example.com"}
    create_resp = client.post("/users/", json=payload)
    user_id = create_resp.json()["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "getuser@example.com"
    logger.info("test_get_user: success")

def test_delete_user():
    clear_user("deleteuser@example.com")
    payload = {"name": "Delete User", "email": "deleteuser@example.com"}
    create_resp = client.post("/users/", json=payload)
    user_id = create_resp.json()["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204
    logger.info("test_delete_user: success")
