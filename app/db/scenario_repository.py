from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.scenario import Scenario
from typing import Optional, List
from bson import ObjectId

class ScenarioRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["scenarios"]

    async def create(self, scenario: Scenario) -> Scenario:
        scenario_dict = scenario.dict(by_alias=True, exclude={"id"}, exclude_none=True)
        result = await self.collection.insert_one(scenario_dict)
        scenario.id = str(result.inserted_id)
        return scenario

    async def get(self, skip: int = 0, limit: int = 100) -> List[Scenario]:
        scenarios = await self.collection.find().skip(skip).limit(limit).to_list(length=limit)
        result = []
        for s in scenarios:
            scenario_dict = dict(s)
            scenario_dict["id"] = str(scenario_dict.pop("_id"))
            result.append(Scenario(**scenario_dict))
        return result

    async def get_by_id(self, scenario_id: str) -> Optional[Scenario]:
        scenario = await self.collection.find_one({"_id": ObjectId(scenario_id)})
        if scenario:
            scenario_dict = dict(scenario)
            scenario_dict["id"] = str(scenario_dict.pop("_id"))
            return Scenario(**scenario_dict)
        return None

    async def update(self, scenario_id: str, data: dict) -> Optional[Scenario]:
        await self.collection.update_one({"_id": ObjectId(scenario_id)}, {"$set": data})
        return await self.get_by_id(scenario_id)

    async def delete(self, scenario_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(scenario_id)})
        return result.deleted_count == 1 