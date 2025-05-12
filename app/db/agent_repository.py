from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.agent import Agent
from typing import Optional, List
from bson import ObjectId

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
            agent_dict = dict(a)
            agent_dict["id"] = str(agent_dict.pop("_id"))
            result.append(Agent(**agent_dict))
        return result

    async def get_by_id(self, agent_id: str) -> Optional[Agent]:
        agent = await self.collection.find_one({"_id": ObjectId(agent_id)})
        if agent:
            agent_dict = dict(agent)
            agent_dict["id"] = str(agent_dict.pop("_id"))
            return Agent(**agent_dict)
        return None

    async def update(self, agent_id: str, data: dict) -> Optional[Agent]:
        await self.collection.update_one({"_id": ObjectId(agent_id)}, {"$set": data})
        return await self.get_by_id(agent_id)

    async def delete(self, agent_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(agent_id)})
        return result.deleted_count == 1 