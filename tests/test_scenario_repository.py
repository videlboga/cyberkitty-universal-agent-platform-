import pytest
from unittest.mock import AsyncMock, MagicMock
from app.db.scenario_repository import ScenarioRepository
from app.models.scenario import Scenario
from loguru import logger
import os
from bson import ObjectId

os.makedirs("logs", exist_ok=True)
logger.add("logs/unit_tests.log", format="{time} {level} {message}", level="INFO", rotation="5 MB", compression="zip", serialize=True)

@pytest.fixture
def mock_db():
    collection = AsyncMock()
    db = MagicMock()
    db.__getitem__.return_value = collection
    return db, collection

@pytest.mark.asyncio
async def test_create_scenario(mock_db):
    db, collection = mock_db
    repo = ScenarioRepository(db)
    scenario = Scenario(name="Test Scenario", steps=[{"type": "message", "text": "Hello"}])
    collection.insert_one.return_value.inserted_id = "123"
    result = await repo.create(scenario)
    assert result.id == "123"
    logger.info("test_create_scenario: success")

@pytest.mark.asyncio
async def test_get_scenarios(mock_db):
    db, collection = mock_db
    repo = ScenarioRepository(db)
    scenario1 = {"_id": "507f1f77bcf86cd799439011", "name": "A", "steps": []}
    scenario2 = {"_id": "507f1f77bcf86cd799439012", "name": "B", "steps": []}
    to_list_mock = AsyncMock(return_value=[scenario1, scenario2])
    limit_mock = MagicMock()
    limit_mock.to_list = to_list_mock
    skip_mock = MagicMock()
    skip_mock.limit.return_value = limit_mock
    find_mock = MagicMock()
    find_mock.skip.return_value = skip_mock
    collection.find.return_value = find_mock
    scenarios = [Scenario.model_validate(scenario1), Scenario.model_validate(scenario2)]
    assert len(scenarios) == 2
    assert scenarios[0].id == "507f1f77bcf86cd799439011"
    assert scenarios[1].id == "507f1f77bcf86cd799439012"
    logger.info("test_get_scenarios: success")

@pytest.mark.asyncio
async def test_get_by_id(mock_db):
    db, collection = mock_db
    repo = ScenarioRepository(db)
    oid = "507f1f77bcf86cd799439011"
    scenario_dict = {"_id": oid, "name": "A", "steps": []}
    collection.find_one.return_value = scenario_dict
    scenario = Scenario.model_validate(scenario_dict)
    assert scenario.id == oid
    assert scenario.name == "A"
    logger.info("test_get_by_id: success")

@pytest.mark.asyncio
async def test_update_scenario(mock_db):
    db, collection = mock_db
    repo = ScenarioRepository(db)
    oid = "507f1f77bcf86cd799439011"
    collection.update_one.return_value = MagicMock()
    scenario_dict = {"_id": oid, "name": "A", "steps": []}
    scenario = Scenario.model_validate(scenario_dict)
    repo.get_by_id = AsyncMock(return_value=scenario)
    scenario = await repo.update(oid, {"name": "A"})
    assert scenario.id == oid
    logger.info("test_update_scenario: success")

@pytest.mark.asyncio
async def test_delete_scenario(mock_db):
    db, collection = mock_db
    repo = ScenarioRepository(db)
    oid = ObjectId("507f1f77bcf86cd799439011")
    delete_result = MagicMock()
    delete_result.deleted_count = 1
    collection.delete_one.return_value = delete_result
    result = await repo.delete(str(oid))
    assert result is True
    logger.info("test_delete_scenario: success") 