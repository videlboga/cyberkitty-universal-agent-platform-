import pytest
from unittest.mock import AsyncMock, MagicMock
from app.db.agent_repository import AgentRepository
from app.models.agent import Agent
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
async def test_create_agent(mock_db):
    db, collection = mock_db
    repo = AgentRepository(db)
    agent = Agent(name="Test Agent", config={"role": "assistant"})
    collection.insert_one.return_value.inserted_id = "123"
    result = await repo.create(agent)
    assert result.id == "123"
    logger.info("test_create_agent: success")

@pytest.mark.asyncio
async def test_get_agents(mock_db):
    db, collection = mock_db
    repo = AgentRepository(db)
    agent1 = {"_id": "507f1f77bcf86cd799439011", "name": "A", "config": {}}
    agent2 = {"_id": "507f1f77bcf86cd799439012", "name": "B", "config": {}}
    to_list_mock = AsyncMock(return_value=[agent1, agent2])
    limit_mock = MagicMock()
    limit_mock.to_list = to_list_mock
    skip_mock = MagicMock()
    skip_mock.limit.return_value = limit_mock
    find_mock = MagicMock()
    find_mock.skip.return_value = skip_mock
    collection.find.return_value = find_mock
    agents = [Agent.model_validate(agent1), Agent.model_validate(agent2)]
    assert len(agents) == 2
    assert agents[0].id == "507f1f77bcf86cd799439011"
    assert agents[1].id == "507f1f77bcf86cd799439012"
    logger.info("test_get_agents: success")

@pytest.mark.asyncio
async def test_get_by_id(mock_db):
    db, collection = mock_db
    repo = AgentRepository(db)
    oid = "507f1f77bcf86cd799439011"
    agent_dict = {"_id": oid, "name": "A", "config": {}}
    collection.find_one.return_value = agent_dict
    agent = Agent.model_validate(agent_dict)
    assert agent.id == oid
    assert agent.name == "A"
    logger.info("test_get_by_id: success")

@pytest.mark.asyncio
async def test_update_agent(mock_db):
    db, collection = mock_db
    repo = AgentRepository(db)
    oid = "507f1f77bcf86cd799439011"
    collection.update_one.return_value = MagicMock()
    agent_dict = {"_id": oid, "name": "A", "config": {}}
    agent = Agent.model_validate(agent_dict)
    repo.get_by_id = AsyncMock(return_value=agent)
    agent = await repo.update(oid, {"name": "A"})
    assert agent.id == oid
    logger.info("test_update_agent: success")

@pytest.mark.asyncio
async def test_delete_agent(mock_db):
    db, collection = mock_db
    repo = AgentRepository(db)
    oid = ObjectId("507f1f77bcf86cd799439011")
    delete_result = MagicMock()
    delete_result.deleted_count = 1
    collection.delete_one.return_value = delete_result
    result = await repo.delete(str(oid))
    assert result is True
    logger.info("test_delete_agent: success") 