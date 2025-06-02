#!/usr/bin/env python3
"""
👤 USER SIMULATOR
Простая симуляция поведения пользователей для автотестов OntoBot

Возможности:
- Симуляция различных типов пользователей
- Автоматические ответы на вопросы
- Имитация реального поведения с задержками
"""

import asyncio
import random
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import aiohttp
from loguru import logger

# Настройка логирования
logger.add(
    "logs/user_simulator.log",
    rotation="10 MB",
    retention="7 days",
    compression="gz",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | USER | {message}",
    level="DEBUG"
)

@dataclass
class UserProfile:
    """Профиль тестового пользователя."""
    user_id: int
    first_name: str
    last_name: str = ""
    username: str = ""
    age: int = 30
    profession: str = "Менеджер"
    personality: str = "активный"  # активный, осторожный, любопытный
    response_speed: str = "normal"  # fast, normal, slow

class UserSimulator:
    """
    Симулятор поведения пользователей.
    
    Может имитировать:
    - Разные типы личности
    - Различную скорость ответов
    - Реалистичные ответы на вопросы
    """
    
    def __init__(self, mock_server_url: str = "http://localhost:8082"):
        self.mock_server_url = mock_server_url
        self.users: Dict[int, UserProfile] = {}
        
        # Готовые ответы для разных типов вопросов
        self.response_templates = {
            "name": [
                "Александр", "Мария", "Дмитрий", "Анна", "Сергей", 
                "Елена", "Андрей", "Ольга", "Михаил", "Татьяна"
            ],
            "age": [
                "25", "28", "32", "35", "29", "31", "27", "33", "30", "26"
            ],
            "profession": [
                "Менеджер по продажам", "IT-специалист", "Маркетолог",
                "Предприниматель", "Консультант", "Дизайнер",
                "Аналитик", "Руководитель проекта", "Психолог", "Тренер"
            ],
            "goals": [
                "Хочу развиваться профессионально и найти свое призвание",
                "Стремлюсь к финансовой независимости и стабильности",
                "Хочу улучшить отношения с близкими людьми",
                "Мечтаю о карьерном росте и признании",
                "Хочу найти баланс между работой и личной жизнью"
            ],
            "challenges": [
                "Часто сомневаюсь в себе и своих решениях",
                "Трудно концентрироваться и доводить дела до конца",
                "Боюсь перемен и выхода из зоны комфорта",
                "Сложно говорить 'нет' и отстаивать границы",
                "Переживаю из-за мнения окружающих"
            ],
            "motivation": [
                "Желание стать лучшей версией себя",
                "Стремление к свободе и независимости",
                "Хочу быть примером для своих детей",
                "Мечтаю изменить мир к лучшему",
                "Хочу жить полной и осмысленной жизнью"
            ]
        }
        
        logger.info("👤 User Simulator инициализирован")
    
    def create_user(self, user_id: int, personality: str = "активный") -> UserProfile:
        """Создает нового тестового пользователя."""
        
        profile = UserProfile(
            user_id=user_id,
            first_name=random.choice(self.response_templates["name"]),
            last_name=random.choice(["Иванов", "Петров", "Сидоров", "Козлов", "Новиков"]),
            username=f"test_user_{user_id}",
            age=random.randint(25, 45),
            profession=random.choice(self.response_templates["profession"]),
            personality=personality,
            response_speed="normal"
        )
        
        self.users[user_id] = profile
        
        logger.info(f"👤 Создан пользователь {profile.first_name} (ID: {user_id}, тип: {personality})")
        
        return profile
    
    async def send_message(self, user_id: int, text: str) -> Dict[str, Any]:
        """Отправляет сообщение от имени пользователя."""
        
        if user_id not in self.users:
            self.create_user(user_id)
        
        user = self.users[user_id]
        
        # Имитируем задержку набора текста
        await self._simulate_typing_delay(text, user.response_speed)
        
        payload = {
            "user_id": user_id,
            "chat_id": user_id,
            "text": text,
            "first_name": user.first_name,
            "username": user.username
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mock_server_url}/mock/simulate_user_message",
                    json=payload
                ) as response:
                    result = await response.json()
                    
                    logger.info(f"💬 {user.first_name}: {text}")
                    return result
                    
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения: {e}")
            return {"ok": False, "error": str(e)}
    
    async def click_button(self, user_id: int, callback_data: str, message_id: int = None) -> Dict[str, Any]:
        """Нажимает кнопку от имени пользователя."""
        
        if user_id not in self.users:
            self.create_user(user_id)
        
        user = self.users[user_id]
        
        # Имитируем задержку принятия решения
        await self._simulate_decision_delay(user.personality)
        
        payload = {
            "user_id": user_id,
            "chat_id": user_id,
            "callback_data": callback_data,
            "message_id": message_id or 1,
            "first_name": user.first_name,
            "username": user.username
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mock_server_url}/mock/simulate_callback_query",
                    json=payload
                ) as response:
                    result = await response.json()
                    
                    logger.info(f"🔘 {user.first_name} нажал: {callback_data}")
                    return result
                    
        except Exception as e:
            logger.error(f"❌ Ошибка нажатия кнопки: {e}")
            return {"ok": False, "error": str(e)}
    
    def get_smart_response(self, user_id: int, question_type: str) -> str:
        """Генерирует умный ответ на основе типа вопроса и личности пользователя."""
        
        if user_id not in self.users:
            self.create_user(user_id)
        
        user = self.users[user_id]
        
        # Базовые ответы по типам
        if question_type in self.response_templates:
            base_responses = self.response_templates[question_type]
            response = random.choice(base_responses)
        else:
            response = "Это интересный вопрос, дайте подумать..."
        
        # Модификация ответа в зависимости от личности
        if user.personality == "активный":
            if question_type == "goals":
                response = f"Я очень амбициозен! {response} И хочу достичь этого как можно быстрее!"
        elif user.personality == "осторожный":
            if question_type == "challenges":
                response = f"Честно говоря, {response.lower()} Это моя главная проблема."
        elif user.personality == "любопытный":
            response = f"{response} А что вы об этом думаете?"
        
        return response
    
    async def _simulate_typing_delay(self, text: str, speed: str):
        """Имитирует задержку набора текста."""
        
        base_delay = len(text) * 0.05  # 50мс на символ
        
        if speed == "fast":
            delay = base_delay * 0.5
        elif speed == "slow":
            delay = base_delay * 2.0
        else:  # normal
            delay = base_delay
        
        # Добавляем случайность
        delay += random.uniform(0.1, 0.5)
        
        await asyncio.sleep(delay)
    
    async def _simulate_decision_delay(self, personality: str):
        """Имитирует задержку принятия решения."""
        
        if personality == "активный":
            delay = random.uniform(0.2, 0.8)
        elif personality == "осторожный":
            delay = random.uniform(1.0, 3.0)
        else:  # любопытный или normal
            delay = random.uniform(0.5, 1.5)
        
        await asyncio.sleep(delay)

# === ГОТОВЫЕ ПОЛЬЗОВАТЕЛИ ===

class OntoTestUsers:
    """Готовые профили пользователей для тестирования OntoBot."""
    
    @staticmethod
    def get_active_user() -> UserProfile:
        """Активный пользователь - быстро отвечает, амбициозный."""
        return UserProfile(
            user_id=1001,
            first_name="Александр",
            last_name="Активный",
            username="active_alex",
            age=28,
            profession="Предприниматель",
            personality="активный",
            response_speed="fast"
        )
    
    @staticmethod
    def get_cautious_user() -> UserProfile:
        """Осторожный пользователь - медленно принимает решения."""
        return UserProfile(
            user_id=1002,
            first_name="Мария",
            last_name="Осторожная",
            username="careful_maria",
            age=35,
            profession="Аналитик",
            personality="осторожный",
            response_speed="slow"
        )
    
    @staticmethod
    def get_curious_user() -> UserProfile:
        """Любопытный пользователь - задает много вопросов."""
        return UserProfile(
            user_id=1003,
            first_name="Дмитрий",
            last_name="Любопытный",
            username="curious_dmitry",
            age=31,
            profession="Консультант",
            personality="любопытный",
            response_speed="normal"
        )

if __name__ == "__main__":
    # Простой тест симулятора
    async def test_simulator():
        simulator = UserSimulator()
        
        # Создаем тестового пользователя
        user = simulator.create_user(12345, "активный")
        
        # Отправляем сообщение
        await simulator.send_message(12345, "/start")
        await asyncio.sleep(1)
        
        # Нажимаем кнопку
        await simulator.click_button(12345, "begin_diagnostic")
        
        logger.info("✅ Тест симулятора завершен")
    
    asyncio.run(test_simulator()) 