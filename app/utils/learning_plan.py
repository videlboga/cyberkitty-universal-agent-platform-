import json
import requests
from typing import Dict, Any, Optional, List
from loguru import logger
import os
from datetime import datetime

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/learning_plan.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

class LearningPlanManager:
    """
    Класс для управления планами обучения пользователей.
    Хранит планы в коллекции learning_plans.
    """
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Инициализация менеджера планов обучения
        
        Args:
            api_base_url: Базовый URL API для работы с коллекциями
        """
        self.api_base_url = api_base_url
        self.collection_name = "learning_plans"
        logger.info("LearningPlanManager инициализирован")
        
    async def get_plan(self, plan_id: str) -> dict:
        """
        Получить план обучения по ID
        
        Args:
            plan_id: ID плана обучения
            
        Returns:
            dict: План обучения или пустой словарь, если план не найден
        """
        try:
            response = requests.get(
                f"{self.api_base_url}/db/collections/{self.collection_name}/items/{plan_id}"
            )
            
            if response.status_code == 200:
                plan = response.json()
                logger.info(f"Получен план обучения {plan_id}")
                return plan
                
            logger.warning(f"План обучения {plan_id} не найден")
            return {}
            
        except Exception as e:
            logger.error(f"Ошибка при получении плана обучения: {e}")
            return {}
    
    async def get_plan_by_user(self, user_id: int) -> dict:
        """
        Получить план обучения по ID пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            dict: План обучения или пустой словарь, если план не найден
        """
        try:
            response = requests.get(
                f"{self.api_base_url}/db/collections/{self.collection_name}/items", 
                params={"filter": json.dumps({"user_id": user_id})}
            )
            
            if response.status_code == 200:
                items = response.json()
                if items and len(items) > 0:
                    # Берем самый последний план
                    plan = sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)[0]
                    logger.info(f"Получен план обучения для пользователя {user_id}")
                    return plan
                    
            logger.warning(f"План обучения для пользователя {user_id} не найден")
            return {}
            
        except Exception as e:
            logger.error(f"Ошибка при получении плана обучения по пользователю: {e}")
            return {}
    
    async def create_plan(self, user_id: int, plan_data: Dict[str, Any]) -> str:
        """
        Создать новый план обучения
        
        Args:
            user_id: ID пользователя
            plan_data: Данные плана обучения
            
        Returns:
            str: ID созданного плана или пустая строка в случае ошибки
        """
        try:
            # Добавляем базовые поля к плану
            plan = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "active"
            }
            plan.update(plan_data)
            
            response = requests.post(
                f"{self.api_base_url}/db/collections/{self.collection_name}/items",
                json=plan
            )
            
            if response.status_code == 201:
                result = response.json()
                plan_id = result.get("_id", "")
                logger.info(f"Создан план обучения {plan_id} для пользователя {user_id}")
                return plan_id
                
            logger.error(f"Ошибка при создании плана обучения: {response.status_code} {response.text}")
            return ""
            
        except Exception as e:
            logger.error(f"Ошибка при создании плана обучения: {e}")
            return ""
    
    async def update_plan(self, plan_id: str, plan_data: Dict[str, Any]) -> bool:
        """
        Обновить план обучения
        
        Args:
            plan_id: ID плана обучения
            plan_data: Новые данные плана
            
        Returns:
            bool: True если обновление успешно, иначе False
        """
        try:
            plan_data["updated_at"] = datetime.now().isoformat()
            
            response = requests.patch(
                f"{self.api_base_url}/db/collections/{self.collection_name}/items/{plan_id}",
                json=plan_data
            )
            
            success = response.status_code == 200
            logger.info(f"Обновление плана обучения {plan_id}: {'успешно' if success else 'ошибка'}")
            return success
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении плана обучения: {e}")
            return False
    
    async def mark_completed(self, plan_id: str) -> bool:
        """
        Отметить план как завершенный
        
        Args:
            plan_id: ID плана обучения
            
        Returns:
            bool: True если обновление успешно, иначе False
        """
        try:
            return await self.update_plan(plan_id, {"status": "completed"})
            
        except Exception as e:
            logger.error(f"Ошибка при отметке завершения плана: {e}")
            return False
    
    async def generate_plan(self, user_id: int, user_profile: dict, rag_plugin) -> str:
        """
        Генерирует план обучения на основе профиля пользователя с использованием RAG
        
        Args:
            user_id: ID пользователя
            user_profile: Профиль пользователя
            rag_plugin: Экземпляр RAG плагина для генерации контента
            
        Returns:
            str: ID созданного плана или пустая строка в случае ошибки
        """
        try:
            # Формируем запрос к RAG на основе профиля пользователя
            interests = user_profile.get("interests", [])
            learning_goals = user_profile.get("learning_goals", [])
            experience_level = user_profile.get("experience_level", "начинающий")
            learning_style = user_profile.get("preferred_learning_style", "смешанный")
            available_time = user_profile.get("available_time_per_week", "5-10 часов")
            
            query = f"""
            Сгенерируй подробный план обучения по нейросетям для пользователя со следующими параметрами:
            - Интересы: {', '.join(interests)}
            - Цели обучения: {', '.join(learning_goals)}
            - Уровень опыта: {experience_level}
            - Предпочитаемый стиль обучения: {learning_style}
            - Доступное время в неделю: {available_time}
            
            План должен содержать:
            1. Краткое описание
            2. Ожидаемые результаты
            3. Список модулей (5-7 модулей)
            4. Для каждого модуля - название, описание, ключевые темы, основные навыки, примерное время на изучение
            5. Рекомендуемые ресурсы и материалы
            """
            
            # Получаем ответ от RAG
            plan_text = rag_plugin.search(query)
            logger.info(f"Сгенерирован план обучения для пользователя {user_id}")
            
            # Преобразуем текстовый план в структуру
            plan_data = {
                "title": "Индивидуальный план обучения по нейросетям",
                "description": "План создан на основе ваших интересов и целей обучения",
                "raw_text": plan_text,
                "modules": self._extract_modules_from_text(plan_text),
                "interests": interests,
                "learning_goals": learning_goals,
                "experience_level": experience_level,
                "preferred_learning_style": learning_style,
                "available_time_per_week": available_time
            }
            
            # Создаем план в базе
            return await self.create_plan(user_id, plan_data)
            
        except Exception as e:
            logger.error(f"Ошибка при генерации плана обучения: {e}")
            return ""
    
    def _extract_modules_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Извлекает структуру модулей из текстового плана
        
        Args:
            text: Текст плана обучения
            
        Returns:
            List[Dict[str, Any]]: Список модулей в структурированном виде
        """
        try:
            # Упрощенная логика извлечения модулей, 
            # в реальном приложении здесь должен быть более сложный парсинг
            modules = []
            lines = text.strip().split('\n')
            current_module = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if "Модуль" in line and ":" in line:
                    # Новый модуль
                    if current_module and "title" in current_module:
                        modules.append(current_module)
                    current_module = {"title": line.split(":", 1)[1].strip()}
                elif "Описание" in line and ":" in line and current_module:
                    current_module["description"] = line.split(":", 1)[1].strip()
                elif "Ключевые темы" in line and ":" in line and current_module:
                    topics_str = line.split(":", 1)[1].strip()
                    current_module["topics"] = [t.strip() for t in topics_str.split(",")]
                elif "Время" in line and ":" in line and current_module:
                    current_module["estimated_time"] = line.split(":", 1)[1].strip()
            
            # Добавляем последний модуль
            if current_module and "title" in current_module:
                modules.append(current_module)
                
            # Если не удалось извлечь модули, создаем заглушку
            if not modules:
                modules = [
                    {
                        "title": "Введение в нейросети",
                        "description": "Базовые концепции и принципы работы",
                        "topics": ["Основы ИИ", "Типы нейросетей", "Области применения"],
                        "estimated_time": "1-2 недели"
                    }
                ]
                
            return modules
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении модулей из плана: {e}")
            return [
                {
                    "title": "Модуль 1: Введение в нейросети",
                    "description": "Не удалось правильно распарсить план",
                    "topics": ["Основы ИИ"],
                    "estimated_time": "1-2 недели"
                }
            ] 