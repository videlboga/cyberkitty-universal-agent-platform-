from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.scenario import Scenario
from typing import Optional, List
from bson import ObjectId
from app.utils.id_helper import sanitize_id, ensure_mongo_id, build_id_query, find_one_by_id_flexible
from fastapi import Depends
from app.db.database import get_database
from loguru import logger
import json

class ScenarioRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["scenarios"]

    async def create(self, scenario: Scenario) -> Scenario:
        scenario_dict = scenario.model_dump(by_alias=True, exclude_none=True)
        scenario_dict = ensure_mongo_id(scenario_dict)
        logger.critical(f"[ScenarioRepository CREATE CRITICAL] Документ для ЗАПИСИ в БД (insert_one): {json.dumps(scenario_dict, indent=2, default=str)}")
        result = await self.collection.insert_one(scenario_dict)
        created_scenario_doc = await self.collection.find_one({"_id": result.inserted_id})
        if created_scenario_doc:
            return Scenario(**sanitize_id(created_scenario_doc))
        return scenario

    async def get(self, skip: int = 0, limit: int = 100) -> List[Scenario]:
        scenarios_cursor = self.collection.find().skip(skip).limit(limit)
        result = []
        async for scenario_doc in scenarios_cursor:
            result.append(Scenario(**sanitize_id(scenario_doc)))
        return result

    async def get_by_id(self, scenario_id_value: str) -> Optional[Scenario]:
        scenario_doc = await find_one_by_id_flexible(scenario_id_value, self.collection, target_field_name="scenario_id")
        if scenario_doc:
            logger.critical(f"[ScenarioRepository CRITICAL] Загружен документ из БД: {json.dumps(scenario_doc, indent=2, default=str)}")
            return Scenario(**sanitize_id(scenario_doc))
        logger.critical(f"[ScenarioRepository CRITICAL] Сценарий не найден в БД по scenario_id_value: {scenario_id_value}")
        return None

    async def find_one(self, query: dict) -> Optional[Scenario]:
        scenario_doc = await self.collection.find_one(query)
        if scenario_doc:
            return Scenario(**sanitize_id(scenario_doc))
        return None

    async def find_many(self, query: dict, limit: int = 100) -> List[Scenario]:
        scenarios_cursor = self.collection.find(query).limit(limit)
        result = []
        async for scenario_doc in scenarios_cursor:
            result.append(Scenario(**sanitize_id(scenario_doc)))
        return result

    async def update(self, scenario_id_value: str, data: dict) -> Optional[Scenario]:
        query = build_id_query(scenario_id_value, target_field_name="scenario_id", collection_name_for_guess=self.collection.name)
        if not query:
            return None
            
        data_to_set = {k: v for k, v in data.items() if k not in ["_id", "id", "scenario_id"]}
        logger.critical(f"[ScenarioRepository UPDATE CRITICAL] Данные для ОБНОВЛЕНИЯ в БД (update_one, $set): {json.dumps(data_to_set, indent=2, default=str)}")
        
        result = await self.collection.update_one(query, {"$set": data_to_set})
        if result.matched_count > 0:
            return await self.get_by_id(scenario_id_value)
        return None

    async def delete(self, scenario_id_value: str) -> bool:
        query = build_id_query(scenario_id_value, target_field_name="scenario_id", collection_name_for_guess=self.collection.name)
        if not query:
            return False
            
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0

async def get_scenario_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> ScenarioRepository:
    return ScenarioRepository(db) 