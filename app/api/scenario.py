from fastapi import APIRouter, HTTPException, status, Body, Response
from app.models.scenario import Scenario
from app.db.scenario_repository import ScenarioRepository, get_scenario_repository
from loguru import logger
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
from app.utils.id_helper import build_id_query
from fastapi import Depends
from app.db.database import get_database

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017/universal_agent_platform")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "universal_agent_platform")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGODB_DATABASE_NAME]
scenario_repo = ScenarioRepository(db)

@router.post("/", response_model=Scenario, status_code=status.HTTP_201_CREATED)
async def upsert_scenario(
    scenario_payload: Scenario,
    response: Response,
    scenario_repo: ScenarioRepository = Depends(get_scenario_repository)
):
    logger.info(f"Upsert scenario: payload.scenario_id = '{scenario_payload.scenario_id}'")

    existing_scenario = await scenario_repo.get_by_id(scenario_payload.scenario_id)

    if existing_scenario:
        logger.info(f"Updating scenario with scenario_id: {existing_scenario.scenario_id} (ObjectId: {existing_scenario.id})")
        update_data = scenario_payload.model_dump(exclude_unset=True, exclude={"id", "_id", "scenario_id", "created_at"})

        updated_scenario = await scenario_repo.update(existing_scenario.scenario_id, update_data)
        
        if updated_scenario:
            response.status_code = status.HTTP_200_OK
            return updated_scenario
        else:
            logger.error(f"Failed to update scenario with scenario_id: {scenario_payload.scenario_id}. Update method returned None.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update scenario with scenario_id {scenario_payload.scenario_id} after finding it.")
    else:
        logger.info(f"Creating new scenario with scenario_id: {scenario_payload.scenario_id}")
        created_scenario = await scenario_repo.create(scenario_payload)
        response.status_code = status.HTTP_201_CREATED
        return created_scenario

@router.get("/", response_model=List[Scenario])
async def get_scenarios(
    skip: int = 0, 
    limit: int = 100, 
    scenario_repo: ScenarioRepository = Depends(get_scenario_repository)
):
    scenarios = await scenario_repo.get_all(skip=skip, limit=limit)
    return scenarios

@router.get("/{scenario_id_value}", response_model=Scenario)
async def get_scenario_by_id(
    scenario_id_value: str, 
    scenario_repo: ScenarioRepository = Depends(get_scenario_repository)
):
    logger.debug(f"API: get_scenario_by_id - scenario_id_value: {scenario_id_value}")
    scenario = await scenario_repo.get_by_id(scenario_id_value)
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
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

@router.delete("/{scenario_id_value}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    scenario_id_value: str, 
    scenario_repo: ScenarioRepository = Depends(get_scenario_repository)
):
    logger.info(f"Deleting scenario with ID: {scenario_id_value}")
    deleted = await scenario_repo.delete(scenario_id_value)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT) 