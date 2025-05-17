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
import requests
from app.db.scenario_repository import ScenarioRepository
from app.db.agent_repository import AgentRepository

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
    
    def __init__(self,
                 scenario_repo: ScenarioRepository,
                 agent_repo: AgentRepository,
                 api_base_url: str = "http://localhost:8000"):
        """
        Инициализация исполнителя сценариев
        
        Args:
            scenario_repo: Репозиторий для доступа к сценариям.
            agent_repo: Репозиторий для доступа к агентам.
            api_base_url: Базовый URL API для доступа к коллекциям и интеграциям.
        """
        self.scenario_repo = scenario_repo
        self.agent_repo = agent_repo
        self.api_base_url = api_base_url
        self.step_handlers = {}
        self.plugins = []
        
        # Инициализация обработчиков стандартных типов шагов
        self._register_default_handlers()
        
        # Инициализация и регистрация плагинов
        self._init_plugins()

        # Регистрация обработчика для под-сценариев
        self.step_handlers["execute_sub_scenario"] = self._handle_execute_sub_scenario
        
        logger.info("ScenarioExecutor инициализирован")
    
    def _register_default_handlers(self):
        """Регистрация обработчиков для стандартных типов шагов"""
        self.step_handlers["message"] = self.handle_message
        self.step_handlers["input"] = self.handle_input
        self.step_handlers["branch"] = self.handle_branch
        self.step_handlers["rag_search"] = self.handle_rag_search
        self.step_handlers["telegram_message"] = self.handle_telegram_message
        # Добавляем обработчики для шагов типа 'action' и 'end'
        self.step_handlers["action"] = self.handle_action
        self.step_handlers["start"] = self.handle_start
        self.step_handlers["end"] = self.handle_end
        
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
        
        # --- Проверка наличия chat_id ---
        if not chat_id or chat_id in (None, "", "{chat_id}"):
            logger.error(f"[CRITICAL] chat_id отсутствует или некорректен перед отправкой в Telegram! Этап: telegram_message, context: {context}")
            context[output_var] = {"error": "chat_id отсутствует или некорректен на этапе telegram_message", "context": context}
            return context
        # --- Конец проверки ---
        # --- Расширенное логирование для отладки chat_id ---
        logger.info(f"[DEBUG] Перед отправкой в Telegram: chat_id={chat_id!r}, message={message!r}, context={context}")
        # --- Конец блока логирования ---
        try:
            result = await self.telegram_plugin.send_message(chat_id, message)
            context[output_var] = result
            logger.info(f"Отправлено сообщение в Telegram: chat_id={chat_id}, длина сообщения={len(message)}")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в Telegram: {e}")
            context[output_var] = {"error": str(e)}
        
        return context
    
    async def handle_action(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обрабатывает шаг типа action: выполнение действия через плагины
        
        Args:
            step_data: Данные шага
            context: Контекст выполнения
            
        Returns:
            Dict[str, Any]: Обновленный контекст
        """
        try:
            # Получаем тип действия и его параметры
            action_type = step_data.get("action_type")
            params = step_data.get("params", {})
            
            if not action_type:
                logger.warning("Шаг action не содержит тип действия")
                return context
            
            # Если action_type совпадает с telegram_message, используем соответствующий обработчик
            if action_type == "telegram_message" or action_type == "send_message":
                # Передаем параметры в формате, ожидаемом handle_telegram_message
                telegram_step = {
                    "chat_id": params.get("chat_id") or context.get("chat_id"),
                    "text": params.get("text") or ""
                }
                return await self.handle_telegram_message(telegram_step, context)
            
            # Для других типов действий логируем и просто возвращаем контекст
            logger.info(f"Выполнение действия типа {action_type}")
            return context
                
        except Exception as e:
            logger.error(f"Ошибка при обработке шага action: {e}")
            context["__step_error__"] = str(e) # Добавляем информацию об ошибке в контекст
            return context
    
    async def handle_start(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обрабатывает шаг типа start: начало сценария
        
        Args:
            step_data: Данные шага
            context: Контекст выполнения
            
        Returns:
            Dict[str, Any]: Обновленный контекст
        """
        logger.info("Начало выполнения сценария")
        # Можно добавить инициализацию начальных значений контекста
        return context
    
    async def handle_end(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обрабатывает шаг типа end: завершение сценария
        
        Args:
            step_data: Данные шага
            context: Контекст выполнения
            
        Returns:
            Dict[str, Any]: Обновленный контекст
        """
        logger.info("Завершение выполнения сценария")
        # Можно добавить специальную обработку при завершении сценария
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

    async def _handle_execute_sub_scenario(self, step_data: Dict[str, Any], parent_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик для шага типа 'execute_sub_scenario'.
        Запускает указанный под-сценарий, передает ему часть родительского контекста (input_mapping)
        и возвращает результаты из контекста под-сценария в родительский (output_mapping).
        """
        sub_scenario_id = step_data.get("sub_scenario_id")
        if not sub_scenario_id:
            error_msg = "Шаг 'execute_sub_scenario' не содержит обязательного поля 'sub_scenario_id'"
            logger.error(error_msg)
            parent_context["__step_error__"] = error_msg
            return parent_context

        logger.info(f"Запуск под-сценария: ID='{sub_scenario_id}' из родительского шага '{step_data.get('id', 'N/A')}'.")

        try:
            sub_scenario_model = await self.scenario_repo.get_by_id(sub_scenario_id)
            if not sub_scenario_model:
                error_msg = f"Под-сценарий с ID '{sub_scenario_id}' не найден."
                logger.error(error_msg)
                parent_context["__step_error__"] = error_msg
                return parent_context
            
            sub_scenario_dict = sub_scenario_model.model_dump(exclude_none=True)

            # 1. Инициализация начального контекста для под-сценария
            sub_context_initial = {}
            input_mapping = step_data.get("input_mapping", {})
            logger.debug(f"Input mapping для под-сценария '{sub_scenario_id}': {input_mapping}")
            for sub_key, parent_key_or_value in input_mapping.items():
                if isinstance(parent_key_or_value, str) and parent_key_or_value in parent_context:
                    sub_context_initial[sub_key] = parent_context[parent_key_or_value]
                    logger.debug(f"  Mapping: sub_context['{sub_key}'] = parent_context['{parent_key_or_value}'] (value: {parent_context[parent_key_or_value]})")
                else: # Если это не ключ из родительского контекста или не строка, считаем это литеральным значением
                    sub_context_initial[sub_key] = parent_key_or_value
                    logger.debug(f"  Mapping: sub_context['{sub_key}'] = literal_value (value: {parent_key_or_value})")
            
            logger.info(f"Начальный контекст для под-сценария '{sub_scenario_id}': {sub_context_initial}")

            # 2. Выполнение под-сценария
            # Важно: передаем копию, чтобы изменения в sub_context_initial не повлияли на input_mapping в будущем
            final_sub_context = await self.execute_scenario(sub_scenario_dict, sub_context_initial.copy())
            
            logger.info(f"Под-сценарий '{sub_scenario_id}' завершен. Финальный контекст под-сценария: {final_sub_context}")
            
            if "__scenario_error__" in final_sub_context:
                error_detail = final_sub_context['__scenario_error__']
                logger.warning(f"Под-сценарий '{sub_scenario_id}' завершился с ошибкой: {error_detail}")
                parent_context["__step_error__"] = f"Ошибка в под-сценарии '{sub_scenario_id}': {error_detail}"
                # В случае ошибки в под-сценарии, не применяем output_mapping и возвращаем родительский контекст с ошибкой
                return parent_context

        except Exception as e:
            error_msg = f"Критическая ошибка во время выполнения под-сценария '{sub_scenario_id}': {str(e)}"
            logger.exception(error_msg) # Используем logger.exception для полного трейсбека
            parent_context["__step_error__"] = error_msg
            return parent_context

        # 3. Маппинг результатов из контекста под-сценария в родительский контекст
        output_mapping = step_data.get("output_mapping", {})
        logger.debug(f"Output mapping для под-сценария '{sub_scenario_id}': {output_mapping}")
        for parent_key, sub_key_or_value in output_mapping.items():
            if isinstance(sub_key_or_value, str) and sub_key_or_value in final_sub_context:
                parent_context[parent_key] = final_sub_context[sub_key_or_value]
                logger.debug(f"  Mapping: parent_context['{parent_key}'] = final_sub_context['{sub_key_or_value}'] (value: {final_sub_context[sub_key_or_value]})")
            elif not isinstance(sub_key_or_value, str): # Если это не строка, то это литеральное значение
                 parent_context[parent_key] = sub_key_or_value
                 logger.debug(f"  Mapping: parent_context['{parent_key}'] = literal_value (value: {sub_key_or_value})")
            else: # Ключ не найден в контексте под-сценария
                logger.warning(f"Ключ '{sub_key_or_value}' не найден в финальном контексте под-сценария '{sub_scenario_id}' для output mapping. Поле '{parent_key}' не будет установлено или будет None.")
                parent_context[parent_key] = None # Или можно не устанавливать, или установить специальное значение

        logger.info(f"Завершено выполнение шага execute_sub_scenario для '{sub_scenario_id}'. Обновленный родительский контекст: {parent_context}")
        return parent_context 