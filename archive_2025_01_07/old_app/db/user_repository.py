from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import User
from typing import Optional, List
from bson import ObjectId
from app.utils.id_helper import ensure_mongo_id, sanitize_id, build_id_query, find_one_by_id_flexible
from fastapi import Depends
from app.db.database import get_database

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def create(self, user: User) -> User:
        user_dict = user.model_dump(by_alias=True, exclude_none=True)
        user_dict = ensure_mongo_id(user_dict)
        result = await self.collection.insert_one(user_dict)
        
        created_user_doc = await self.collection.find_one({"_id": result.inserted_id})
        if created_user_doc:
            return User(**sanitize_id(created_user_doc))
        return user

    async def get(self, skip: int = 0, limit: int = 100) -> List[User]:
        users_cursor = self.collection.find().skip(skip).limit(limit)
        result = []
        async for user_doc in users_cursor:
            result.append(User(**sanitize_id(user_doc)))
        return result

    async def get_by_id(self, user_id_value: str) -> Optional[User]:
        user_doc = await find_one_by_id_flexible(user_id_value, self.collection, target_field_name=None)
        if user_doc:
            return User(**sanitize_id(user_doc))
        return None

    async def get_by_email(self, email: str) -> Optional[User]:
        user_doc = await self.collection.find_one({"email": email})
        if user_doc:
            return User(**sanitize_id(user_doc))
        return None

    async def update(self, user_id_value: str, data: dict) -> Optional[User]:
        query = build_id_query(user_id_value, target_field_name=None, collection_name_for_guess=self.collection.name)
        if not query:
            return None

        data_to_set = {k: v for k, v in data.items() if k not in ["_id", "id", "email"]}
        
        if not data_to_set:
            return await self.get_by_id(user_id_value)

        result = await self.collection.update_one(query, {"$set": data_to_set})
        if result.matched_count > 0:
            return await self.get_by_id(user_id_value)
        return None

    async def delete(self, user_id_value: str) -> bool:
        query = build_id_query(user_id_value, target_field_name=None, collection_name_for_guess=self.collection.name)
        if not query:
            return False
            
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0

async def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> UserRepository:
    return UserRepository(db) 