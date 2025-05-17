from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import User
from typing import Optional, List
from bson import ObjectId

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def create(self, user: User) -> User:
        user_dict = user.dict(by_alias=True, exclude={"id"}, exclude_none=True)
        result = await self.collection.insert_one(user_dict)
        user.id = str(result.inserted_id)
        return user

    async def get(self, skip: int = 0, limit: int = 100) -> List[User]:
        users = await self.collection.find().skip(skip).limit(limit).to_list(length=limit)
        result = []
        for u in users:
            user_dict = dict(u)
            user_dict["id"] = str(user_dict.pop("_id"))
            result.append(User(**user_dict))
        return result

    async def get_by_id(self, user_id: str) -> Optional[User]:
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user_dict = dict(user)
            user_dict["id"] = str(user_dict.pop("_id"))
            return User(**user_dict)
        return None

    async def get_by_email(self, email: str) -> Optional[User]:
        user = await self.collection.find_one({"email": email})
        if user:
            user_dict = dict(user)
            user_dict["id"] = str(user_dict.pop("_id"))
            return User(**user_dict)
        return None

    async def update(self, user_id: str, data: dict) -> Optional[User]:
        await self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
        return await self.get_by_id(user_id)

    async def delete(self, user_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count == 1 