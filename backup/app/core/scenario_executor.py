import os
import json
import asyncio
from typing import Dict, Any, Optional, List, Callable
from loguru import logger
from datetime import datetime
from app.core.state_machine import ScenarioStateMachine
from app.plugins.rag_plugin import RAGPlugin
from app.plugins.telegram_plugin import TelegramPlugin
from app.plugins.learning_plan_plugin import LearningPlanPlugin
from app.plugins.agent_manager_plugin import AgentManagerPlugin
from app.plugins.llm_plugin import LLMPlugin
from telegram.ext import Application

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/scenario_executor.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

# Получаем токен из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

class ScenarioExecutor:
    """
    Исполнитель сценариев с поддержкой плагинов и произвольных типов шагов.
    
    Функциональность:
    - Регистрация обработчиков для различных типов шагов
    - Выполнение шагов сценария через плагины и обработчики
    - Обработка контекста и состояния сценария
    - Поддержка асинхронного выполнения
    """
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Инициализация исполнителя сценариев
        
        Args:
            api_base_url: Базовый URL API для доступа к коллекциям и интеграциям
        """
        self.api_base_url = api_base_url
        self.step_handlers = {}
        
        # Инициализация обработчиков стандартных типов шагов
        self._register_default_handlers()
        
        # Инициализация и регистрация плагинов
        self._init_plugins()
        
        logger.info("ScenarioExecutor инициализирован")
    
    def _register_default_handlers(self):
        """Регистрация обработчиков для стандартных типов шагов"""
        self.step_handlers["message"] = self.handle_message
        self.step_handlers["input"] = self.handle_input
        self.step_handlers["branch"] = self.handle_branch
        self.step_handlers["rag_search"] = self.handle_rag_search
        self.step_handlers["telegram_message"] = self.handle_telegram_message
        
        logger.info("Зарегистрированы обработчики для стандартных типов шагов")
    
    def _init_plugins(self):
        """Инициализация плагинов и регистрация их обработчиков"""
        self.rag_plugin = RAGPlugin()
        
        # Используем реальный токен из переменных окружения
        if not TELEGRAM_BOT_TOKEN:
            logger.warning("TELEGRAM_BOT_TOKEN не найден в переменных окружения. Telegram интеграция не будет работать.")
            telegram_token = "dummy_token"
        else:
            telegram_token = TELEGRAM_BOT_TOKEN
            logger.info(f"Используем токен Telegram из переменных окружения: {telegram_token[:6]}...{telegram_token[-6:] if len(telegram_token) > 12 else ''}")
        
        telegram_app = Application.builder().token(telegram_token).build()
        self.telegram_plugin = TelegramPlugin(telegram_app)
        
        self.learning_plan_plugin = LearningPlanPlugin(api_base_url=self.api_base_url)
        self.agent_manager_plugin = AgentManagerPlugin(api_base_url=self.api_base_url)
        self.llm_plugin = LLMPlugin()
        
        # Регистрация обработчиков из плагинов
        self.learning_plan_plugin.register_step_handlers(self.step_handlers)
        self.agent_manager_plugin.register_step_handlers(self.step_handlers)
        self.llm_plugin.register_step_handlers(self.step_handlers)
        
        logger.info("Инициализированы плагины и их обработчики")
    
    async def handle_message(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага типа message - простое сообщение пользователю
        
        Args:
            step_data: Данные шага (тип, текст, ...)
            context: Контекст сценария
            
        Returns:
            Dict: Обновленный контекст
        """
        # Здесь только возвращаем контекст без изменений
        # Логика отображения сообщения реализуется во фронтенде
        return context
    
    async def handle_input(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага типа input - ожидание ввода от пользователя
        
        Args:
            step_data: Данные шага (тип, текст, ...)
            context: Контекст сценария
            
        Returns:
            Dict: Обновленный контекст
        """
        # Здесь только возвращаем контекст без изменений
        # Логика отображения поля ввода и получения данных реализуется во фронтенде
        return context
    
    async def handle_branch(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага типа branch - ветвление на основе условия
        
        Args:
            step_data: Данные шага (тип, condition, branches)
            context: Контекст сценария
            
        Returns:
            Dict: Обновленный контекст
        """
        # Обработка условия и ветвления реализована в ScenarioStateMachine
        # Здесь только возвращаем контекст без изменений
        return context
    
    async def handle_rag_search(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага типа rag_search - поиск по базе знаний через RAG
        
        Args:
            step_data: Данные шага (тип, query, collection_name, output_var)
            context: Контекст сценария
            
        Returns:
            Dict: Обновленный контекст с результатами RAG
        """
        query = step_data.get("query", "")
        
        # Подстановка переменных из контекста в запрос
        if isinstance(query, str) and "{" in query and "}" in query:
            for key, value in context.items():
                placeholder = "{" + key + "}"
                if placeholder in query:
                    query = query.replace(placeholder, str(value))
        
        collection_name = step_data.get("collection_name", "default")
        output_var = step_data.get("output_var", "rag_results")
        
        try:
            results = await self.rag_plugin.search(query, collection_name)
            context[output_var] = results
            logger.info(f"RAG поиск выполнен: коллекция={collection_name}, запрос={query}, найдено={len(results) if results else 0}")
        except Exception as e:
            logger.error(f"Ошибка при RAG поиске: {e}")
            context[output_var] = {"error": str(e)}
        
        return context
    
    async def handle_telegram_message(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага типа telegram_message - отправка сообщения через Telegram
        
        Args:
            step_data: Данные шага (тип, chat_id, message, ...)
            context: Контекст сценария
            
        Returns:
            Dict: Обновленный контекст
        """
        chat_id = step_data.get("chat_id")
        message = step_data.get("message", "")
        
        # Если chat_id не указан явно, ищем его в контексте
        if not chat_id and "chat_id" in context:
            chat_id = context.get("chat_id")
        
        # Подстановка переменных из контекста в сообщение
        if isinstance(message, str) and "{" in message and "}" in message:
            for key, value in context.items():
                placeholder = "{" + key + "}"
                if placeholder in message:
                    message = message.replace(placeholder, str(value))
        
        output_var = step_data.get("output_var", "telegram_result")
        
        try:
            if not chat_id:
                raise ValueError("Не указан chat_id для отправки сообщения в Telegram")
                
            result = await self.telegram_plugin.send_message(chat_id, message)
            context[output_var] = result
            logger.info(f"Отправлено сообщение в Telegram: chat_id={chat_id}, длина сообщения={len(message)}")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в Telegram: {e}")
            context[output_var] = {"error": str(e)}
        
        return context
    
    async def execute_step(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполнение одного шага сценария
        
        Args:
            step_data: Данные шага (тип, текст, ...)
            context: Контекст сценария
            
        Returns:
            Dict: Обновленный контекст
        """
        step_type = step_data.get("type", "unknown")
        
        # Логирование начала выполнения шага
        logger.info(f"Начало выполнения шага: тип={step_type}")
        
        # Проверка наличия обработчика для данного типа шага
        if step_type not in self.step_handlers:
            logger.warning(f"Неизвестный тип шага: {step_type}")
            return context
        
        try:
            # Вызов соответствующего обработчика
            handler = self.step_handlers[step_type]
            updated_context = await handler(step_data, context)
            
            # Логирование успешного выполнения шага
            logger.info(f"Шаг выполнен успешно: тип={step_type}")
            
            return updated_context
        except Exception as e:
            # Логирование ошибки при выполнении шага
            logger.error(f"Ошибка при выполнении шага {step_type}: {e}")
            return context
    
    async def execute_scenario(self, scenario: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Выполнение всего сценария целиком
        
        Args:
            scenario: Данные сценария (steps, name, ...)
            context: Исходный контекст (опционально)
            
        Returns:
            Dict: Финальный контекст после выполнения всех шагов
        """
        if context is None:
            context = {}
        
        state_machine = ScenarioStateMachine(scenario, context=context)
        step = state_machine.current_step()
        
        logger.info(f"Начало выполнения сценария: {scenario.get('name', 'unnamed')}")
        
        while step:
            # Выполнение текущего шага
            context = await self.execute_step(step, state_machine.context)
            
            # Обновление контекста в state machine
            state_machine.context = context
            
            # Переход к следующему шагу
            step = state_machine.next_step()
        
        logger.info(f"Сценарий выполнен: {scenario.get('name', 'unnamed')}")
        
        return context 