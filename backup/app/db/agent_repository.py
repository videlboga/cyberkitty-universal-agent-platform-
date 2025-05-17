from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.agent import Agent
from typing import Optional, List
from bson import ObjectId
from app.utils.id_helper import to_object_id, sanitize_id, handle_id_query

class AgentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["agents"]

    async def create(self, agent: Agent) -> Agent:
        agent_dict = agent.dict(by_alias=True, exclude={"id"}, exclude_none=True)
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
        obj_id = to_object_id(agent_id)
        if obj_id:
            await self.collection.update_one({"_id": obj_id}, {"$set": data})
        else:
            await self.collection.update_one({"name": agent_id}, {"$set": data})
        return await self.get_by_id(agent_id)

    async def delete(self, agent_id: str) -> bool:
        obj_id = to_object_id(agent_id)
        if obj_id:
            result = await self.collection.delete_one({"_id": obj_id})
        else:
            result = await self.collection.delete_one({"name": agent_id})
        return result.deleted_count == 1 