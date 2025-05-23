import json
import requests
from typing import Dict, Any, Optional, List
from loguru import logger
import os
from datetime import datetime

class ProgressTracker:
    """
    Класс для отслеживания прогресса пользователя по плану обучения.
    Хранит информацию о прогрессе в коллекции progress_tracking.
    """
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Инициализация трекера прогресса
        
        Args:
            api_base_url: Базовый URL API для работы с коллекциями
        """
        self.api_base_url = api_base_url
        self.collection_name = "progress_tracking"
        logger.info("ProgressTracker инициализирован")
        
    async def get_progress(self, user_id: int, learning_plan_id: str) -> dict:
        """
        Получить прогресс пользователя по плану обучения
        
        Args:
            user_id: ID пользователя
            learning_plan_id: ID плана обучения
            
        Returns:
            dict: Прогресс пользователя или пустой прогресс, если не найден
        """
        try:
            # Поиск прогресса по user_id и learning_plan_id
            response = requests.get(
                f"{self.api_base_url}/db/collections/{self.collection_name}/items", 
                params={"filter": json.dumps({
                    "user_id": user_id,
                    "learning_plan_id": learning_plan_id
                })}
            )
            
            if response.status_code == 200:
                items = response.json()
                if items and len(items) > 0:
                    logger.info(f"Получен прогресс для пользователя {user_id} по плану {learning_plan_id}")
                    return items[0]
            
            # Прогресс не найден, создаем новый
            logger.info(f"Прогресс для пользователя {user_id} по плану {learning_plan_id} не найден")
            return {
                "user_id": user_id,
                "learning_plan_id": learning_plan_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "completed_modules": [],
                "module_progress": {},
                "overall_progress": 0,
                "last_activity": None,
                "reflections": []
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении прогресса: {e}")
            # Возвращаем дефолтный прогресс при ошибке
            return {
                "user_id": user_id,
                "learning_plan_id": learning_plan_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "completed_modules": [],
                "module_progress": {},
                "overall_progress": 0
            }
    
    async def save_progress(self, progress: Dict[str, Any]) -> bool:
        """
        Сохранить прогресс пользователя
        
        Args:
            progress: Словарь с прогрессом (должен содержать user_id и learning_plan_id)
            
        Returns:
            bool: True если сохранение успешно, иначе False
        """
        if "user_id" not in progress or "learning_plan_id" not in progress:
            logger.error("Ошибка: progress должен содержать user_id и learning_plan_id")
            return False
            
        user_id = progress["user_id"]
        learning_plan_id = progress["learning_plan_id"]
        progress["updated_at"] = datetime.now().isoformat()
        
        try:
            # Проверяем, существует ли уже запись для этого пользователя и плана
            response = requests.get(
                f"{self.api_base_url}/db/collections/{self.collection_name}/items", 
                params={"filter": json.dumps({
                    "user_id": user_id,
                    "learning_plan_id": learning_plan_id
                })}
            )
            
            if response.status_code == 200:
                items = response.json()
                if items and len(items) > 0:
                    # Обновляем существующую запись
                    item_id = items[0]["_id"]
                    update_response = requests.patch(
                        f"{self.api_base_url}/db/collections/{self.collection_name}/items/{item_id}",
                        json=progress
                    )
                    success = update_response.status_code == 200
                    logger.info(f"Обновление прогресса для пользователя {user_id} по плану {learning_plan_id}: {'успешно' if success else 'ошибка'}")
                    return success
            
            # Создаем новую запись
            if "created_at" not in progress:
                progress["created_at"] = datetime.now().isoformat()
                
            create_response = requests.post(
                f"{self.api_base_url}/db/collections/{self.collection_name}/items",
                json=progress
            )
            success = create_response.status_code == 201
            logger.info(f"Создание прогресса для пользователя {user_id} по плану {learning_plan_id}: {'успешно' if success else 'ошибка'}")
            return success
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении прогресса: {e}")
            return False
    
    async def mark_module_completed(self, user_id: int, learning_plan_id: str, module_index: int) -> bool:
        """
        Отметить модуль как завершенный
        
        Args:
            user_id: ID пользователя
            learning_plan_id: ID плана обучения
            module_index: Индекс завершенного модуля
            
        Returns:
            bool: True если обновление успешно, иначе False
        """
        try:
            progress = await self.get_progress(user_id, learning_plan_id)
            
            if "completed_modules" not in progress:
                progress["completed_modules"] = []
                
            if module_index not in progress["completed_modules"]:
                progress["completed_modules"].append(module_index)
                
            # Обновляем общий прогресс (здесь должна быть логика расчета прогресса)
            # Для простоты считаем, что всего 5 модулей
            progress["overall_progress"] = len(progress["completed_modules"]) / 5 * 100
            progress["last_activity"] = datetime.now().isoformat()
            
            return await self.save_progress(progress)
            
        except Exception as e:
            logger.error(f"Ошибка при отметке завершения модуля: {e}")
            return False
    
    async def add_reflection(self, user_id: int, learning_plan_id: str, reflection_text: str) -> bool:
        """
        Добавить рефлексию пользователя
        
        Args:
            user_id: ID пользователя
            learning_plan_id: ID плана обучения
            reflection_text: Текст рефлексии
            
        Returns:
            bool: True если добавление успешно, иначе False
        """
        try:
            progress = await self.get_progress(user_id, learning_plan_id)
            
            if "reflections" not in progress:
                progress["reflections"] = []
                
            reflection = {
                "date": datetime.now().isoformat(),
                "text": reflection_text
            }
            
            progress["reflections"].append(reflection)
            progress["last_activity"] = datetime.now().isoformat()
            
            return await self.save_progress(progress)
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении рефлексии: {e}")
            return False
    
    async def update_module_progress(self, user_id: int, learning_plan_id: str, module_index: int, percentage: float) -> bool:
        """
        Обновить прогресс по конкретному модулю
        
        Args:
            user_id: ID пользователя
            learning_plan_id: ID плана обучения
            module_index: Индекс модуля
            percentage: Процент выполнения модуля (0-100)
            
        Returns:
            bool: True если обновление успешно, иначе False
        """
        try:
            progress = await self.get_progress(user_id, learning_plan_id)
            
            if "module_progress" not in progress:
                progress["module_progress"] = {}
                
            progress["module_progress"][str(module_index)] = percentage
            
            # Пересчитываем общий прогресс
            total_percentage = 0
            module_count = 0
            
            for _, module_percentage in progress["module_progress"].items():
                total_percentage += module_percentage
                module_count += 1
                
            if module_count > 0:
                progress["overall_progress"] = total_percentage / module_count
                
            progress["last_activity"] = datetime.now().isoformat()
            
            # Если модуль завершен на 100%, добавляем его в completed_modules
            if percentage >= 100 and module_index not in progress.get("completed_modules", []):
                if "completed_modules" not in progress:
                    progress["completed_modules"] = []
                progress["completed_modules"].append(module_index)
                
            return await self.save_progress(progress)
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении прогресса модуля: {e}")
            return False 