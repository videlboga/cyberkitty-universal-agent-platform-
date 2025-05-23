import json
import requests
from typing import Dict, Any, Optional, List
from loguru import logger
import os
from datetime import datetime

class UserProfileManager:
    """
    Класс для управления профилями пользователей.
    Хранит профили в коллекции users.
    """
    def __init__(self, api_base_url: str = None):
        """
        Инициализация менеджера пользовательских профилей
        
        Args:
            api_base_url: Базовый URL API для работы с коллекциями
        """
        self.api_base_url = api_base_url or "http://app:8000"
        self.collection_name = "users"
        logger.info("UserProfileManager инициализирован")
        
    async def get_profile(self, user_id: int) -> dict:
        """
        Получить профиль пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            dict: Профиль пользователя или новый профиль, если не найден
        """
        try:
            # Поиск профиля по user_id
            response = requests.get(
                f"{self.api_base_url}/db/collections/{self.collection_name}/items", 
                params={"filter": json.dumps({"user_id": user_id})}
            )
            
            if response.status_code == 200:
                items = response.json()
                if items and len(items) > 0:
                    logger.info(f"Получен профиль пользователя {user_id}")
                    return items[0]
            
            # Профиль не найден, создаем новый
            logger.info(f"Профиль пользователя {user_id} не найден")
            return {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "first_name": None,
                "last_name": None,
                "username": None,
                "interests": [],
                "experience_level": None,
                "learning_goals": [],
                "preferred_learning_style": None,
                "available_time_per_week": None,
                "notifications_enabled": True,
                "daily_notification_time": "09:00",
                "weekly_notification_day": "monday",
                "weekly_notification_time": "10:00"
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении профиля пользователя: {e}")
            # Возвращаем дефолтный профиль при ошибке
            return {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
    
    async def save_profile(self, profile: Dict[str, Any]) -> bool:
        """
        Сохранить профиль пользователя
        
        Args:
            profile: Словарь с профилем пользователя (должен содержать user_id)
            
        Returns:
            bool: True если сохранение успешно, иначе False
        """
        if "user_id" not in profile:
            logger.error("Ошибка: profile должен содержать user_id")
            return False
            
        user_id = profile["user_id"]
        profile["updated_at"] = datetime.now().isoformat()
        
        try:
            # Проверяем, существует ли уже профиль для этого пользователя
            response = requests.get(
                f"{self.api_base_url}/db/collections/{self.collection_name}/items", 
                params={"filter": json.dumps({"user_id": user_id})}
            )
            
            if response.status_code == 200:
                items = response.json()
                if items and len(items) > 0:
                    # Обновляем существующий профиль
                    item_id = items[0]["_id"]
                    update_response = requests.patch(
                        f"{self.api_base_url}/db/collections/{self.collection_name}/items/{item_id}",
                        json=profile
                    )
                    success = update_response.status_code == 200
                    logger.info(f"Обновление профиля пользователя {user_id}: {'успешно' if success else 'ошибка'}")
                    return success
            
            # Создаем новый профиль
            if "created_at" not in profile:
                profile["created_at"] = datetime.now().isoformat()
                
            create_response = requests.post(
                f"{self.api_base_url}/db/collections/{self.collection_name}/items",
                json=profile
            )
            success = create_response.status_code == 201
            logger.info(f"Создание профиля пользователя {user_id}: {'успешно' if success else 'ошибка'}")
            return success
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении профиля пользователя: {e}")
            return False
    
    async def update_profile(self, user_id: int, data: Dict[str, Any]) -> bool:
        """
        Обновить поля профиля пользователя
        
        Args:
            user_id: ID пользователя
            data: Словарь с полями для обновления
            
        Returns:
            bool: True если обновление успешно, иначе False
        """
        try:
            profile = await self.get_profile(user_id)
            profile.update(data)
            profile["updated_at"] = datetime.now().isoformat()
            return await self.save_profile(profile)
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении профиля пользователя: {e}")
            return False
    
    async def save_user_telegram_info(self, user_id: int, first_name: str, last_name: str = None, username: str = None) -> bool:
        """
        Сохранить информацию о пользователе из Telegram
        
        Args:
            user_id: ID пользователя в Telegram
            first_name: Имя пользователя
            last_name: Фамилия пользователя (опционально)
            username: Username пользователя (опционально)
            
        Returns:
            bool: True если сохранение успешно, иначе False
        """
        try:
            profile = await self.get_profile(user_id)
            profile["first_name"] = first_name
            
            if last_name:
                profile["last_name"] = last_name
                
            if username:
                profile["username"] = username
                
            return await self.save_profile(profile)
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении информации о пользователе из Telegram: {e}")
            return False 