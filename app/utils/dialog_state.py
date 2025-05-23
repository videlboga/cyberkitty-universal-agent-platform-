import json
import requests
from typing import Dict, Any, Optional, List
from loguru import logger
import os

class DialogStateManager:
    """
    Класс для управления состоянием диалога пользователя.
    Хранит состояние в коллекции dialog_states.
    """
    def __init__(self, api_base_url: str = None):
        """
        Инициализация менеджера диалоговых состояний
        
        Args:
            api_base_url: Базовый URL API для работы с коллекциями
        """
        self.api_base_url = api_base_url or "http://app:8000"
        self.collection_name = "dialog_states"
        logger.info("DialogStateManager инициализирован")
        
    async def get_state(self, user_id: int) -> dict:
        """
        Получить текущее состояние диалога пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            dict: Состояние диалога или пустой словарь, если состояние не найдено
        """
        try:
            # Поиск состояния по user_id
            response = requests.get(
                f"{self.api_base_url}/db/collections/{self.collection_name}/items", 
                params={"filter": json.dumps({"user_id": user_id})}
            )
            
            if response.status_code == 200:
                items = response.json()
                if items and len(items) > 0:
                    logger.info(f"Получено состояние диалога для пользователя {user_id}")
                    return items[0]
            
            # Состояние не найдено, создаем новое
            logger.info(f"Состояние диалога для пользователя {user_id} не найдено")
            default_state = {
                "user_id": user_id,
                "current_agent": None,
                "onboarding_completed": False,
                "current_step": "start",
                "dialog_history": [],
                "context": {},
                "learning_plan_id": None
            }
            return default_state
            
        except Exception as e:
            logger.error(f"Ошибка при получении состояния диалога: {e}")
            # Возвращаем дефолтное состояние при ошибке
            return {
                "user_id": user_id,
                "current_agent": None,
                "onboarding_completed": False,
                "current_step": "start",
                "dialog_history": [],
                "context": {},
                "learning_plan_id": None
            }
    
    async def save_state(self, state: Dict[str, Any]) -> bool:
        """
        Сохранить состояние диалога пользователя
        
        Args:
            state: Словарь с состоянием диалога (должен содержать user_id)
            
        Returns:
            bool: True если сохранение успешно, иначе False
        """
        if "user_id" not in state:
            logger.error("Ошибка: state должен содержать user_id")
            return False
            
        user_id = state["user_id"]
        
        try:
            # Проверяем, существует ли уже запись для этого пользователя
            response = requests.get(
                f"{self.api_base_url}/db/collections/{self.collection_name}/items", 
                params={"filter": json.dumps({"user_id": user_id})}
            )
            
            if response.status_code == 200:
                items = response.json()
                if items and len(items) > 0:
                    # Обновляем существующую запись
                    item_id = items[0]["_id"]
                    update_response = requests.patch(
                        f"{self.api_base_url}/db/collections/{self.collection_name}/items/{item_id}",
                        json=state
                    )
                    success = update_response.status_code == 200
                    logger.info(f"Обновление состояния диалога для пользователя {user_id}: {'успешно' if success else 'ошибка'}")
                    return success
            
            # Создаем новую запись
            create_response = requests.post(
                f"{self.api_base_url}/db/collections/{self.collection_name}/items",
                json=state
            )
            success = create_response.status_code == 201
            logger.info(f"Создание состояния диалога для пользователя {user_id}: {'успешно' if success else 'ошибка'}")
            return success
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении состояния диалога: {e}")
            return False
    
    async def update_step(self, user_id: int, step: str, context: Dict[str, Any] = None) -> bool:
        """
        Обновить текущий шаг и контекст диалога
        
        Args:
            user_id: ID пользователя
            step: Новый шаг диалога
            context: Новый или дополнительный контекст
            
        Returns:
            bool: True если обновление успешно, иначе False
        """
        try:
            state = await self.get_state(user_id)
            state["current_step"] = step
            
            if context:
                if "context" not in state:
                    state["context"] = {}
                state["context"].update(context)
                
            return await self.save_state(state)
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении шага диалога: {e}")
            return False
    
    async def add_to_history(self, user_id: int, message: Dict[str, Any]) -> bool:
        """
        Добавить сообщение в историю диалога
        
        Args:
            user_id: ID пользователя
            message: Словарь с информацией о сообщении
            
        Returns:
            bool: True если добавление успешно, иначе False
        """
        try:
            state = await self.get_state(user_id)
            
            if "dialog_history" not in state:
                state["dialog_history"] = []
                
            state["dialog_history"].append(message)
            
            # Ограничиваем размер истории
            if len(state["dialog_history"]) > 50:
                state["dialog_history"] = state["dialog_history"][-50:]
                
            return await self.save_state(state)
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении в историю диалога: {e}")
            return False
    
    async def set_current_agent(self, user_id: int, agent: str) -> bool:
        """
        Установить текущего агента для пользователя
        
        Args:
            user_id: ID пользователя
            agent: Название агента
            
        Returns:
            bool: True если установка успешна, иначе False
        """
        try:
            state = await self.get_state(user_id)
            state["current_agent"] = agent
            return await self.save_state(state)
            
        except Exception as e:
            logger.error(f"Ошибка при установке текущего агента: {e}")
            return False
    
    async def mark_onboarding_completed(self, user_id: int, learning_plan_id: str = None) -> bool:
        """
        Отметить, что пользователь завершил первоначальный опрос
        
        Args:
            user_id: ID пользователя
            learning_plan_id: ID созданного плана обучения
            
        Returns:
            bool: True если операция успешна, иначе False
        """
        try:
            state = await self.get_state(user_id)
            state["onboarding_completed"] = True
            
            if learning_plan_id:
                state["learning_plan_id"] = learning_plan_id
                
            return await self.save_state(state)
            
        except Exception as e:
            logger.error(f"Ошибка при отметке завершения onboarding: {e}")
            return False 