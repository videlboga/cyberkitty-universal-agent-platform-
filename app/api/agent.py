from fastapi import APIRouter, HTTPException, status
from app.models.agent import Agent
from app.db.agent_repository import AgentRepository
from loguru import logger
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
import os

router = APIRouter(prefix="/agents", tags=["agents"])

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/universal_agent")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()
agent_repo = AgentRepository(db)

@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(agent: Agent):
    created = await agent_repo.create(agent)
    logger.info(f"Агент создан: {created.name}")
    return created

@router.get("/", response_model=List[Agent])
async def list_agents(skip: int = 0, limit: int = 100):
    agents = await agent_repo.get(skip=skip, limit=limit)
    logger.info(f"Запрошен список агентов: {len(agents)} найдено")
    return agents

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    agent = await agent_repo.get_by_id(agent_id)
    if not agent:
        logger.warning(f"Агент не найден: {agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")
    logger.info(f"Агент найден: {agent_id}")
    return agent

@router.patch("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, data: dict):
    agent = await agent_repo.get_by_id(agent_id)
    if not agent:
        logger.warning(f"Агент не найден для обновления: {agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")
    updated = await agent_repo.update(agent_id, data)
    logger.info(f"Агент обновлён: {agent_id}")
    return updated

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str):
    agent = await agent_repo.get_by_id(agent_id)
    if not agent:
        logger.warning(f"Агент не найден для удаления: {agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")
    await agent_repo.delete(agent_id)
    logger.info(f"Агент удалён: {agent_id}")
    return None 