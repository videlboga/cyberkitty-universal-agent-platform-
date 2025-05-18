from fastapi import APIRouter, HTTPException, status, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.core.scenario_executor import ScenarioExecutor
from app.db.scenario_repository import ScenarioRepository
from app.db.agent_repository import AgentRepository
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json

# Импортируем telegram_plugin из integration.py
from app.api.integration import telegram_plugin

router = APIRouter(prefix="/learning", tags=["learning"])

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/learning_api.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

# Инициализация подключения к MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/universal_agent")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()
scenario_repo = ScenarioRepository(db)
agent_repo = AgentRepository(db)

# Инициализация исполнителя сценариев, передавая telegram_plugin
scenario_executor = ScenarioExecutor(
    scenario_repo=scenario_repo, 
    agent_repo=agent_repo,
    telegram_plugin=telegram_plugin
)

# Модели данных
class UserProfile(BaseModel):
    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    experience_level: str = "начинающий"
    interests: List[str] = Field(default_factory=list)
    learning_goals: List[str] = Field(default_factory=list)
    preferred_learning_style: str = "смешанный"
    available_time_per_week: str = "5-10 часов"
    notifications_enabled: bool = True
    notification_frequency: str = "on_demand"

class OnboardingRequest(BaseModel):
    user_id: str
    chat_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language: str = "ru"

@router.post("/onboard", status_code=status.HTTP_200_OK)
async def start_onboarding(request: OnboardingRequest = Body(...)):
    """
    Запускает сценарий онбординга для пользователя 
    и отправляет первое сообщение через Telegram
    
    Args:
        request: Данные пользователя для старта онбординга
        
    Returns:
        dict: Результат запуска сценария
    """
    try:
        # Поиск сценария по имени
        scenarios = await scenario_repo.find({"name": "Онбординг пользователя"})
        
        if not scenarios or len(scenarios) == 0:
            # Если сценарий не найден, попробуем загрузить его из JSON
            try:
                with open("docs/examples/onboarding_scenario.json", "r", encoding="utf-8") as f:
                    scenario_data = json.load(f)
                    # Сохраняем сценарий в базу данных
                    scenario_id = await scenario_repo.create(scenario_data)
                    scenario = await scenario_repo.get_by_id(scenario_id)
                    logger.info(f"Сценарий онбординга загружен из JSON и сохранен с ID: {scenario_id}")
            except Exception as e:
                logger.error(f"Ошибка при загрузке сценария из JSON: {e}")
                raise HTTPException(
                    status_code=404,
                    detail="Сценарий онбординга не найден, и не удалось загрузить его из JSON"
                )
        else:
            scenario = scenarios[0]
        
        # Подготавливаем контекст для запуска сценария
        context = {
            "user_id": request.user_id,
            "chat_id": request.chat_id,
            "language": request.language,
        }
        
        # Добавляем дополнительные данные пользователя, если они есть
        if request.first_name:
            context["first_name"] = request.first_name
        if request.last_name:
            context["last_name"] = request.last_name
        if request.username:
            context["username"] = request.username
        
        # Запускаем сценарий через исполнитель
        result = await scenario_executor.execute_scenario(scenario.model_dump(), context)
        
        logger.info(f"Сценарий онбординга запущен для пользователя: {request.user_id}")
        return {
            "success": True,
            "user_id": request.user_id,
            "scenario_id": str(scenario.id),
            "message": "Сценарий онбординга успешно запущен"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при запуске сценария онбординга: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при запуске сценария онбординга: {str(e)}"
        )

@router.get("/profiles/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_profile(user_id: str):
    """
    Получает профиль пользователя из коллекции user_profiles
    
    Args:
        user_id: ID пользователя
        
    Returns:
        dict: Профиль пользователя
    """
    try:
        # Создаем запрос к коллекции user_profiles
        user_profiles = db["user_profiles"]
        profile = await user_profiles.find_one({"user_id": user_id})
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Профиль пользователя с ID {user_id} не найден"
            )
        
        # Преобразуем ObjectId в строку для корректной сериализации
        profile["_id"] = str(profile["_id"])
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении профиля пользователя: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении профиля пользователя: {str(e)}"
        )

@router.get("/plans/{user_id}", status_code=status.HTTP_200_OK)
async def get_learning_plan(user_id: str):
    """
    Получает план обучения пользователя из коллекции learning_plans
    
    Args:
        user_id: ID пользователя
        
    Returns:
        dict: План обучения пользователя
    """
    try:
        # Создаем запрос к коллекции learning_plans
        learning_plans = db["learning_plans"]
        plan = await learning_plans.find_one({"user_id": user_id})
        
        if not plan:
            raise HTTPException(
                status_code=404,
                detail=f"План обучения для пользователя с ID {user_id} не найден"
            )
        
        # Преобразуем ObjectId в строку для корректной сериализации
        plan["_id"] = str(plan["_id"])
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении плана обучения: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении плана обучения: {str(e)}"
        ) 