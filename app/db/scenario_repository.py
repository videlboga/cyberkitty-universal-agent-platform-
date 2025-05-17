from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.scenario import Scenario
from typing import Optional, List
from bson import ObjectId
from app.utils.id_helper import to_object_id, sanitize_id, handle_id_query, ensure_mongo_id

class ScenarioRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["scenarios"]

    async def create(self, scenario: Scenario) -> Scenario:
        scenario_dict = scenario.dict(by_alias=True, exclude_none=True)
        scenario_dict = ensure_mongo_id(scenario_dict)
        result = await self.collection.insert_one(scenario_dict)
        scenario.id = str(result.inserted_id)
        return scenario

    async def get(self, skip: int = 0, limit: int = 100) -> List[Scenario]:
        scenarios = await self.collection.find().skip(skip).limit(limit).to_list(length=limit)
        result = []
        for s in scenarios:
            scenario_dict = sanitize_id(s)
            result.append(Scenario(**scenario_dict))
        return result

    async def get_by_id(self, scenario_id: str) -> Optional[Scenario]:
        query = handle_id_query(scenario_id, self.collection)
        scenario = await self.collection.find_one(query)
        if scenario:
            scenario_dict = sanitize_id(scenario)
            return Scenario(**scenario_dict)
        return None

    async def find(self, query: dict) -> List[Scenario]:
        scenarios = await self.collection.find(query).to_list(length=100)
        result = []
        for s in scenarios:
            scenario_dict = sanitize_id(s)
            result.append(Scenario(**scenario_dict))
        return result

    async def update(self, scenario_id: str, data: dict) -> Optional[Scenario]:
        query = handle_id_query(scenario_id)
        data_to_set = {k: v for k, v in data.items() if k != "_id" and k != "id"}
        
        result = await self.collection.update_one(query, {"$set": data_to_set})
        if result.matched_count > 0:
            return await self.get_by_id(scenario_id)
        return None

    async def delete(self, scenario_id: str) -> bool:
        query = handle_id_query(scenario_id)
        result = await self.collection.delete_one(query)
        return result.deleted_count == 1 