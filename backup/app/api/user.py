from fastapi import APIRouter, HTTPException, Depends, status
from app.models.user import User
from app.db.user_repository import UserRepository
from loguru import logger
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os

router = APIRouter(prefix="/users", tags=["users"])

# Подключение к MongoDB (можно вынести в отдельный модуль)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/universal_agent")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()
user_repo = UserRepository(db)

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    """Создать нового пользователя."""
    existing = await user_repo.get_by_email(user.email)
    if existing:
        logger.warning(f"Попытка создать дубликат пользователя: {user.email}")
        raise HTTPException(status_code=409, detail="User with this email already exists")
    created = await user_repo.create(user)
    logger.info(f"Пользователь создан: {created.email}")
    return created

@router.get("/", response_model=List[User])
async def list_users(skip: int = 0, limit: int = 100):
    """Получить список пользователей."""
    users = await user_repo.get(skip=skip, limit=limit)
    logger.info(f"Запрошен список пользователей: {len(users)} найдено")
    return users

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Получить пользователя по ID."""
    user = await user_repo.get_by_id(user_id)
    if not user:
        logger.warning(f"Пользователь не найден: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Пользователь найден: {user_id}")
    return user

@router.patch("/{user_id}", response_model=User)
async def update_user(user_id: str, data: dict):
    """Обновить пользователя по ID."""
    user = await user_repo.get_by_id(user_id)
    if not user:
        logger.warning(f"Пользователь не найден для обновления: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    updated = await user_repo.update(user_id, data)
    logger.info(f"Пользователь обновлён: {user_id}")
    return updated

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    """Удалить пользователя по ID."""
    user = await user_repo.get_by_id(user_id)
    if not user:
        logger.warning(f"Пользователь не найден для удаления: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    await user_repo.delete(user_id)
    logger.info(f"Пользователь удалён: {user_id}")
    return None 