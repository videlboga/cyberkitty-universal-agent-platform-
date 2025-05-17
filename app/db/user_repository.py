from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import User
from typing import Optional, List
from bson import ObjectId
from app.utils.id_helper import ensure_mongo_id, sanitize_id, handle_id_query

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def create(self, user: User) -> User:
        user_dict = user.dict(by_alias=True, exclude_none=True)
        user_dict = ensure_mongo_id(user_dict)
        result = await self.collection.insert_one(user_dict)
        user.id = str(result.inserted_id)
        return user

    async def get(self, skip: int = 0, limit: int = 100) -> List[User]:
        users = await self.collection.find().skip(skip).limit(limit).to_list(length=limit)
        result = []
        for u in users:
            user_dict = sanitize_id(u)
            result.append(User(**user_dict))
        return result

    async def get_by_id(self, user_id: str) -> Optional[User]:
        query = handle_id_query(user_id, self.collection)
        user = await self.collection.find_one(query)
        if user:
            user_dict = sanitize_id(user)
            return User(**user_dict)
        return None

    async def get_by_email(self, email: str) -> Optional[User]:
        user = await self.collection.find_one({"email": email})
        if user:
            user_dict = sanitize_id(user)
            return User(**user_dict)
        return None

    async def update(self, user_id: str, data: dict) -> Optional[User]:
        query = handle_id_query(user_id, self.collection)
        data_to_set = {k: v for k, v in data.items() if k != "_id" and k != "id"}
        
        result = await self.collection.update_one(query, {"$set": data_to_set})
        if result.matched_count > 0:
            return await self.get_by_id(user_id)
        return None

    async def delete(self, user_id: str) -> bool:
        query = handle_id_query(user_id, self.collection)
        result = await self.collection.delete_one(query)
        return result.deleted_count == 1 