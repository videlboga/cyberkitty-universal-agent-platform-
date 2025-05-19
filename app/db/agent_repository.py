from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.agent import Agent
from typing import Optional, List
from bson import ObjectId
from app.utils.id_helper import sanitize_id, ensure_mongo_id, build_id_query, find_one_by_id_flexible
from fastapi import Depends
from app.db.database import get_database # Предполагаем, что get_database находится здесь

class AgentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["agents"]

    async def create(self, agent: Agent) -> Agent:
        agent_dict = agent.model_dump(by_alias=True, exclude_none=True)
        agent_dict = ensure_mongo_id(agent_dict)
        result = await self.collection.insert_one(agent_dict)
        created_agent_doc = await self.collection.find_one({"_id": result.inserted_id})
        if created_agent_doc:
            return Agent(**sanitize_id(created_agent_doc))
        return agent

    async def get(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        agents_cursor = self.collection.find().skip(skip).limit(limit)
        result = []
        async for agent_doc in agents_cursor:
            result.append(Agent(**sanitize_id(agent_doc)))
        return result

    async def get_by_id(self, agent_id_value: str) -> Optional[Agent]:
        agent_doc = await find_one_by_id_flexible(agent_id_value, self.collection, target_field_name="agent_id")
        if agent_doc:
            return Agent(**sanitize_id(agent_doc))
        return None

    async def update(self, agent_id_value: str, data: dict) -> Optional[Agent]:
        query = build_id_query(agent_id_value, target_field_name="agent_id", collection_name_for_guess=self.collection.name)
        if not query:
            return None
            
        data_to_set = {k: v for k, v in data.items() if k not in ["_id", "id", "agent_id"]}

        result = await self.collection.update_one(query, {"$set": data_to_set})
        if result.matched_count > 0:
            return await self.get_by_id(agent_id_value)
        return None

    async def delete(self, agent_id_value: str) -> bool:
        query = build_id_query(agent_id_value, target_field_name="agent_id", collection_name_for_guess=self.collection.name)
        if not query:
            return False
            
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0

async def get_agent_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> AgentRepository:
    return AgentRepository(db) 