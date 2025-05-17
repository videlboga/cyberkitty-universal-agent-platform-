from fastapi import APIRouter, HTTPException, status, Body
from app.models.scenario import Scenario
from app.db.scenario_repository import ScenarioRepository
from loguru import logger
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
import os

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/universal_agent")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()
scenario_repo = ScenarioRepository(db)

@router.post("/", response_model=Scenario, status_code=status.HTTP_201_CREATED)
async def create_scenario(scenario: Scenario):
    try:
        created = await scenario_repo.create(scenario)
        logger.info(f"Сценарий создан: {created.name} с ID {created.id}")
        return created
            
    except Exception as e:
        import traceback
        logger.error(f"Ошибка при создании сценария: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error: {e}")

@router.get("/", response_model=List[Scenario])
async def list_scenarios(skip: int = 0, limit: int = 100):
    scenarios = await scenario_repo.get(skip=skip, limit=limit)
    logger.info(f"Запрошен список сценариев: {len(scenarios)} найдено")
    return scenarios

@router.get("/{scenario_id}", response_model=Scenario)
async def get_scenario(scenario_id: str):
    scenario = await scenario_repo.get_by_id(scenario_id)
    if not scenario:
        logger.warning(f"Сценарий не найден: {scenario_id}")
        raise HTTPException(status_code=404, detail="Scenario not found")
    logger.info(f"Сценарий найден: {scenario_id}")
    return scenario

@router.patch("/{scenario_id}", response_model=Scenario)
async def update_scenario(scenario_id: str, data: dict = Body(...)):
    scenario = await scenario_repo.get_by_id(scenario_id)
    if not scenario:
        logger.warning(f"Сценарий не найден для обновления: {scenario_id}")
        raise HTTPException(status_code=404, detail="Scenario not found")
    updated = await scenario_repo.update(scenario_id, data)
    logger.info(f"Сценарий обновлён: {scenario_id}")
    return updated

@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(scenario_id: str):
    scenario = await scenario_repo.get_by_id(scenario_id)
    if not scenario:
        logger.warning(f"Сценарий не найден для удаления: {scenario_id}")
        raise HTTPException(status_code=404, detail="Scenario not found")
    await scenario_repo.delete(scenario_id)
    logger.info(f"Сценарий удалён: {scenario_id}")
    return None 