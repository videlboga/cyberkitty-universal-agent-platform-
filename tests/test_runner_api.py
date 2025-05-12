import pytest
from fastapi.testclient import TestClient
from app.main import app
from pymongo import MongoClient
import os
from loguru import logger

os.makedirs("logs", exist_ok=True)
logger.add("logs/unit_tests.log", format="{time} {level} {message}", level="INFO", rotation="5 MB", compression="zip", serialize=True)

client = TestClient(app)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "universal_agent"

def setup_agent_and_scenario():
    mongo = MongoClient(MONGO_URI)
    db = mongo[DB_NAME]
    db["agents"].delete_many({"name": "Test Runner Agent"})
    db["scenarios"].delete_many({"name": "Test Runner Scenario"})
    scenario = {"name": "Test Runner Scenario", "steps": [{"type": "message", "text": "Step 1"}]}
    scenario_id = str(db["scenarios"].insert_one(scenario).inserted_id)
    agent = {"name": "Test Runner Agent", "config": {"scenario_id": scenario_id}}
    agent_id = str(db["agents"].insert_one(agent).inserted_id)
    return agent_id, scenario_id

def teardown_agent_and_scenario():
    mongo = MongoClient(MONGO_URI)
    db = mongo[DB_NAME]
    db["agents"].delete_many({"name": "Test Runner Agent"})
    db["scenarios"].delete_many({"name": "Test Runner Scenario"})

def test_run_agent():
    agent_id, scenario_id = setup_agent_and_scenario()
    payload = {"input": {"user_message": "Привет!"}}
    response = client.post(f"/agents/{agent_id}/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == agent_id
    assert data["scenario_id"] == scenario_id
    assert data["step"]["text"] == "Step 1"
    teardown_agent_and_scenario()
    logger.info("test_run_agent: success")

def setup_branching_agent_and_scenario():
    mongo = MongoClient(MONGO_URI)
    db = mongo[DB_NAME]
    db["agents"].delete_many({"name": "Test Branch Agent"})
    db["scenarios"].delete_many({"name": "Test Branch Scenario"})
    scenario = {
        "name": "Test Branch Scenario",
        "steps": [
            {"type": "input", "text": "Введите число", "next_step": 1},
            {"type": "branch", "condition": "context['x'] > 0", "branches": {"if": 2, "else": 3}, "text": "Проверка x"},
            {"type": "message", "text": "x положительное"},
            {"type": "message", "text": "x не положительное"}
        ]
    }
    scenario_id = str(db["scenarios"].insert_one(scenario).inserted_id)
    agent = {"name": "Test Branch Agent", "config": {"scenario_id": scenario_id}}
    agent_id = str(db["agents"].insert_one(agent).inserted_id)
    return agent_id, scenario_id

def teardown_branching_agent_and_scenario():
    mongo = MongoClient(MONGO_URI)
    db = mongo[DB_NAME]
    db["agents"].delete_many({"name": "Test Branch Agent"})
    db["scenarios"].delete_many({"name": "Test Branch Scenario"})

def test_agent_next_step_if():
    agent_id, scenario_id = setup_branching_agent_and_scenario()
    # Стартуем сценарий (step_index=0)
    client.post(f"/agents/{agent_id}/run", json={"input": {"user_message": "Старт"}})
    # Переход по ветке if (x > 0)
    payload = {
        "input_data": {"x": 5},
        "state": {"step_index": 1},
        "context": {"x": 5}
    }
    response = client.post(f"/agents/{agent_id}/step", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["step"]["text"] == "x положительное"
    teardown_branching_agent_and_scenario()
    logger.info("test_agent_next_step_if: success")

def test_agent_next_step_else():
    agent_id, scenario_id = setup_branching_agent_and_scenario()
    client.post(f"/agents/{agent_id}/run", json={"input": {"user_message": "Старт"}})
    # Переход по ветке else (x <= 0)
    payload = {
        "input_data": {"x": -2},
        "state": {"step_index": 1},
        "context": {"x": -2}
    }
    response = client.post(f"/agents/{agent_id}/step", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["step"]["text"] == "x не положительное"
    teardown_branching_agent_and_scenario()
    logger.info("test_agent_next_step_else: success")

def test_agent_not_found():
    response = client.post(f"/agents/000000000000000000000000/run", json={"input": {"user_message": "Старт"}})
    assert response.status_code == 404
    logger.info("test_agent_not_found: success")

def test_invalid_input():
    agent_id, scenario_id = setup_agent_and_scenario()
    # Отправляем невалидный state (например, несуществующий step_index)
    payload = {
        "input_data": {},
        "state": {"step_index": 99},
        "context": {}
    }
    response = client.post(f"/agents/{agent_id}/step", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["step"] is None  # Нет такого шага
    teardown_agent_and_scenario()
    logger.info("test_invalid_input: success") 