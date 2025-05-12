from fastapi import APIRouter, HTTPException, status
from app.db.agent_repository import AgentRepository
from app.db.scenario_repository import ScenarioRepository
from app.core.state_machine import ScenarioStateMachine
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
import os

router = APIRouter(prefix="/agent-actions", tags=["runner"])

os.makedirs("logs", exist_ok=True)
logger.add("logs/agent_launch.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/universal_agent")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()
agent_repo = AgentRepository(db)
scenario_repo = ScenarioRepository(db)

@router.post("/{agent_id}/run", status_code=status.HTTP_200_OK)
async def run_agent(agent_id: str, input_data: dict = None):
    agent = await agent_repo.get_by_id(agent_id)
    if not agent:
        logger.warning(f"Агент не найден: {agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")
    scenario_id = agent.config.get("scenario_id") if agent.config else None
    if not scenario_id:
        logger.warning(f"У агента нет сценария: {agent_id}")
        raise HTTPException(status_code=400, detail="Agent has no scenario_id in config")
    scenario = await scenario_repo.get_by_id(scenario_id)
    if not scenario:
        logger.warning(f"Сценарий не найден: {scenario_id}")
        raise HTTPException(status_code=404, detail="Scenario not found")
    sm = ScenarioStateMachine(scenario.model_dump())
    step = sm.current_step()
    logger.info({"event": "agent_launch", "agent_id": agent_id, "scenario_id": scenario_id, "step": step, "input": input_data})
    return {"agent_id": agent_id, "scenario_id": scenario_id, "step": step, "state": sm.state}

@router.post("/{agent_id}/step", status_code=status.HTTP_200_OK)
async def agent_next_step(agent_id: str, input_data: dict = None, state: dict = None, context: dict = None):
    agent = await agent_repo.get_by_id(agent_id)
    if not agent:
        logger.warning(f"Агент не найден: {agent_id}")
        raise HTTPException(status_code=404, detail="Agent not found")
    scenario_id = agent.config.get("scenario_id") if agent.config else None
    if not scenario_id:
        logger.warning(f"У агента нет сценария: {agent_id}")
        raise HTTPException(status_code=400, detail="Agent has no scenario_id in config")
    scenario = await scenario_repo.get_by_id(scenario_id)
    if not scenario:
        logger.warning(f"Сценарий не найден: {scenario_id}")
        raise HTTPException(status_code=404, detail="Scenario not found")
    sm = ScenarioStateMachine(scenario.model_dump(), state, context)
    next_step = sm.next_step(input_data)
    logger.info({"event": "agent_next_step", "agent_id": agent_id, "scenario_id": scenario_id, "input": input_data, "state": sm.state, "context": sm.context, "step": next_step})
    return {"agent_id": agent_id, "scenario_id": scenario_id, "step": next_step, "state": sm.state, "context": sm.context} 