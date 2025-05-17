from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.agent import Agent
from typing import Optional, List
from bson import ObjectId
from app.utils.id_helper import to_object_id, sanitize_id, handle_id_query, ensure_mongo_id

class AgentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["agents"]

    async def create(self, agent: Agent) -> Agent:
        agent_dict = agent.dict(by_alias=True, exclude_none=True)
        agent_dict = ensure_mongo_id(agent_dict)
        result = await self.collection.insert_one(agent_dict)
        agent.id = str(result.inserted_id)
        return agent

    async def get(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        agents = await self.collection.find().skip(skip).limit(limit).to_list(length=limit)
        result = []
        for a in agents:
            agent_dict = sanitize_id(a)
            result.append(Agent(**agent_dict))
        return result

    async def get_by_id(self, agent_id: str) -> Optional[Agent]:
        query = handle_id_query(agent_id, self.collection)
        agent = await self.collection.find_one(query)
        if agent:
            agent_dict = sanitize_id(agent)
            return Agent(**agent_dict)
        return None

    async def update(self, agent_id: str, data: dict) -> Optional[Agent]:
        query = handle_id_query(agent_id, self.collection)
        data_to_set = {k: v for k, v in data.items() if k != "_id" and k != "id"}

        result = await self.collection.update_one(query, {"$set": data_to_set})
        if result.matched_count > 0:
            return await self.get_by_id(agent_id)
        return None

    async def delete(self, agent_id: str) -> bool:
        query = handle_id_query(agent_id, self.collection)
        result = await self.collection.delete_one(query)
        return result.deleted_count == 1 