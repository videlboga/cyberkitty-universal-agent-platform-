import os
import json
import asyncio
from typing import Dict, Any, Optional, List, Callable
from loguru import logger
from datetime import datetime
from app.core.state_machine import ScenarioStateMachine
from app.plugins.rag_plugin import RAGPlugin
from app.plugins.telegram_plugin import TelegramPlugin
from app.plugins.llm_plugin import LLMPlugin
from app.plugins.mongo_storage_plugin import MongoStoragePlugin
from app.plugins.scheduling_plugin import SchedulingPlugin
from telegram.ext import Application
import requests
from app.db.scenario_repository import ScenarioRepository
from app.db.agent_repository import AgentRepository

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/scenario_executor.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

# Получаем токен из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Утилита для подстановки значений, если еще не импортирована или не определена выше
# Если она уже есть в mongo_storage_plugin, лучше импортировать оттуда или вынести в общие utils
# Для простоты пока определим здесь, если ее нет глобально в этом файле.
# Предполагаем, что _resolve_value_from_context доступна или будет импортирована.
# Если она в mongo_storage_plugin, то from app.plugins.mongo_storage_plugin import _resolve_value_from_context
# По коду mongo_storage_plugin она там есть, но не факт, что видна здесь без явного импорта из модуля.
# Для безопасности, предположим, что она нужна и определим ее или обеспечим импорт.
# Проверил код MongoStoragePlugin - она там внутренняя. Скопируем ее сюда для использования.

def _resolve_value_from_context(value: Any, context: Dict[str, Any], depth=0, max_depth=10) -> Any:
    if depth > max_depth:
        logger.warning(f"Max recursion depth reached in _resolve_value_from_context for value: {value}")
        return value

    if isinstance(value, str):
        # Пытаемся разрешить как полный плейсхолдер {key} или {obj.key}
        if value.startswith("{") and value.endswith("}"):
            key_path = value[1:-1]
            parts = key_path.split('.')
            current_value = context
            resolved_successfully = True
            for part in parts:
                if isinstance(current_value, dict) and part in current_value:
                    current_value = current_value[part]
                elif isinstance(current_value, list): # Попытка доступа по индексу для списков
                    try:
                        idx = int(part)
                        if 0 <= idx < len(current_value):
                            current_value = current_value[idx]
                        else:
                            resolved_successfully = False
                            break
                    except ValueError:
                        resolved_successfully = False
                        break
                else:
                    resolved_successfully = False
                    break
            
            if resolved_successfully:
                # Если результат - строка, которая сама является плейсхолдером, разрешаем ее дальше
                if isinstance(current_value, str) and current_value.startswith("{") and current_value.endswith("}") and current_value != value:
                    return _resolve_value_from_context(current_value, context, depth + 1, max_depth)
                return current_value
            else: # Если не смогли разрешить как полный ключ, проверяем частичную подстановку
                # Это для строк типа "Hello {name}, your age is {age}"
                # Используем простой f-string like replacement, но безопасный
                # Обновлено: более простой вариант, не используем format, так как он может вызвать ошибки с лишними {}
                # Вместо этого, ищем {key} и заменяем.
                # Эта логика перенесена в resolve_string_template
                return resolve_string_template(value, context)
        else:
            # Если строка не является полным плейсхолдером, все равно пытаемся подставить в нее значения
            return resolve_string_template(value, context)

    elif isinstance(value, dict):
        return {k: _resolve_value_from_context(v, context, depth + 1, max_depth) for k, v in value.items()}
    elif isinstance(value, list):
        return [_resolve_value_from_context(item, context, depth + 1, max_depth) for item in value]
    return value

def resolve_string_template(template_str: str, ctx: Dict[str, Any]) -> str:
    """
    Разрешает плейсхолдеры вида {key} или {obj.key.subkey} в строке.
    Не использует eval или format во избежание ошибок безопасности и форматирования.
    """
    import re
    # Находим все плейсхолдеры вида {key} или {obj.key...}
    # Этот паттерн более гибкий, чем просто \\{([^\\}]+)\\}
    placeholders = re.findall(r"\\{([^{}]+)\\}", template_str)

    resolved_str = template_str
    for placeholder in placeholders:
        key_path = placeholder
        parts = key_path.split('.')
        current_value = ctx
        resolved_successfully = True
        for part in parts:
            if isinstance(current_value, dict) and part in current_value:
                current_value = current_value[part]
            elif isinstance(current_value, list):
                try:
                    idx = int(part)
                    if 0 <= idx < len(current_value):
                        current_value = current_value[idx]
                    else:
                        resolved_successfully = False
                        break
                except ValueError:
                    resolved_successfully = False
                    break
            else:
                resolved_successfully = False
                break
        
        if resolved_successfully:
            # Преобразуем значение в строку для подстановки
            # Если значение - словарь или список, его строковое представление будет подставлено
            replacement_value = str(current_value)
            resolved_str = resolved_str.replace(f"{{{placeholder}}}", replacement_value)
        # Если плейсхолдер не найден в контексте, он остается без изменений в строке
        # else:
        #     logger.debug(f"Placeholder '{{{placeholder}}}' not found in context or path invalid.")

    return resolved_str

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
                 api_base_url: str = "http://localhost:8000",
                 telegram_plugin: Optional[TelegramPlugin] = None,
                 mongo_storage_plugin: Optional[MongoStoragePlugin] = None,
                 scheduling_plugin: Optional[SchedulingPlugin] = None):
        """
        Инициализация исполнителя сценариев
        
        Args:
            scenario_repo: Репозиторий для доступа к сценариям.
            agent_repo: Репозиторий для доступа к агентам.
            api_base_url: Базовый URL API для доступа к коллекциям и интеграциям.
            telegram_plugin: Опциональный экземпляр TelegramPlugin.
            mongo_storage_plugin: Опциональный экземпляр MongoStoragePlugin.
            scheduling_plugin: Опциональный экземпляр SchedulingPlugin.
        """
        self.scenario_repo = scenario_repo
        self.agent_repo = agent_repo
        self.api_base_url = api_base_url
        self.telegram_plugin = telegram_plugin
        self.mongo_storage_plugin = mongo_storage_plugin
        self.scheduling_plugin = scheduling_plugin
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
        self.step_handlers["action"] = self.handle_action
        self.step_handlers["start"] = self.handle_start
        self.step_handlers["end"] = self.handle_end
        self.step_handlers["execute_code"] = self.handle_execute_code
        self.step_handlers["log_message"] = self.handle_log_message
        
        logger.info("Зарегистрированы обработчики для стандартных типов шагов, включая execute_code и log_message")
    
    def _init_plugins(self):
        """Инициализация плагинов и регистрация их обработчиков"""
        self.rag_plugin = RAGPlugin()
        
        self.llm_plugin = LLMPlugin()
        
        # Регистрация обработчиков из плагинов
        self.llm_plugin.register_step_handlers(self.step_handlers)
        
        if self.telegram_plugin:
            self.telegram_plugin.register_step_handlers(self.step_handlers)
            logger.info("Обработчики TelegramPlugin зарегистрированы.")
        else:
            logger.warning("TelegramPlugin не был предоставлен ScenarioExecutor, интеграция с Telegram через ScenarioExecutor не будет работать для обработчиков шагов.")
            
        if self.mongo_storage_plugin:
            self.mongo_storage_plugin.register_step_handlers(self.step_handlers)
            logger.info("Обработчики MongoStoragePlugin зарегистрированы.")
        else:
            logger.warning("MongoStoragePlugin не был предоставлен ScenarioExecutor.")
            
        if self.scheduling_plugin:
            self.scheduling_plugin.register_step_handlers(self.step_handlers)
            logger.info("Обработчики SchedulingPlugin зарегистрированы.")
            # # Добавим лог для проверки, что именно зарегистрировано (ВРЕМЕННО ОТКЛЮЧЕНО ИЗ-ЗА ОШИБКИ)
            # for step_type, handler_func in self.scheduling_plugin.get_step_handlers().items():
            #     logger.info(f"SchedulingPlugin: зарегистрирован '{step_type}' -> {handler_func.__name__} из {handler_func.__self__.__class__.__name__}")
        else:
            logger.warning("SchedulingPlugin не был предоставлен ScenarioExecutor.")
            
        logger.info("Инициализированы плагины и их обработчики (кроме Telegram и MongoStorage, если не были предоставлены).")
    
    async def handle_message(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага типа message - простое сообщение пользователю
        (Это может быть переименовано/объединено с log_message, если функционал дублируется)
        """
        # Логика отображения сообщения реализуется во фронтенде или через другие плагины (напр. Telegram)
        # Здесь просто логируем факт вызова этого шага, если он используется
        message_text = step_data.get("params", {}).get("text", "(пустое сообщение)")
        resolved_message = _resolve_value_from_context(message_text, context)
        logger.info(f"Обработчик handle_message: {resolved_message}")
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
            action_type = step_data.get("action_type")
            params = step_data.get("params", {}) # Это параметры для действия
            # step_data может содержать и другие поля, специфичные для шага "action", 
            # но не являющиеся параметрами самого действия (например, output_var)
            
            if not action_type:
                logger.warning("Шаг action не содержит тип действия (action_type)")
                context["__step_error__"] = "Шаг action не содержит action_type"
                return context
            
            # Если action_type совпадает с telegram_send_message, используем соответствующий обработчик из TelegramPlugin
            if action_type == "telegram_send_message":
                # Параметры для telegram_send_message должны быть внутри params
                # step_data для handle_step_send_message это и есть params в данном случае
                logger.info(f"Шаг action вызывает telegram_send_message с параметрами: {{params}}")
                # Убедимся, что chat_id передается, если он есть в общем контексте и не указан в params
                if "chat_id" not in params and "chat_id" in context:
                    params["chat_id"] = context["chat_id"]

                if self.telegram_plugin: # Проверяем наличие плагина перед вызовом
                    return await self.telegram_plugin.handle_step_send_message(params, context)
                else:
                    logger.error("Попытка выполнить telegram_send_message, но TelegramPlugin не инициализирован в ScenarioExecutor.")
                    context["__step_error__"] = "TelegramPlugin не инициализирован."
                    return context
            
            # Для других типов действий можно также проверять наличие зарегистрированных обработчиков
            # или использовать общую логику, если предполагается, что action_type - это имя метода в каком-либо плагине.
            # Пока что, для неизвестных action_type, логируем и возвращаем контекст.
            # Эта логика может быть расширена для поддержки большего количества generic actions.
            
            logger.info(f"Выполнение общего действия типа '{action_type}' не реализовано напрямую в handle_action. Проверьте тип шага.")
            # Если предполагается, что action_type - это какой-то другой зарегистрированный тип шага,
            # то сценарий должен использовать 'type: action_type' вместо 'type: action, action_type: action_type'
            
            # Если есть другие плагины, которые регистрируют действия под своими именами,
            # они должны регистрировать их в self.step_handlers, и тогда шаг должен быть type: plugin_action_name
            
            # По умолчанию, если action_type не telegram_send_message и не другой специальный, считаем ошибкой конфигурации шага
            context["__step_error__"] = f"Неизвестный action_type '{action_type}' в шаге 'action'. Зарегистрируйте его или используйте соответствующий 'type'."
            logger.warning(context["__step_error__"])
            return context
                
        except Exception as e:
            logger.error(f"Ошибка при обработке шага action (action_type: {step_data.get('action_type')}): {e}", exc_info=True)
            context["__step_error__"] = str(e)
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
    
    async def handle_execute_code(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик для шага execute_code."""
        params = step_data.get("params", {})
        code_to_execute = params.get("code")

        if not code_to_execute:
            logger.warning("Шаг execute_code не содержит кода для выполнения.")
            context["__step_error__"] = "Шаг execute_code: отсутствует параметр 'code'."
            return context

        try:
            # Подготовка локального словаря для exec, чтобы код имел доступ к 'context'
            # и мог изменять его. Также можно передать 'logger' или другие утилиты.
            execution_globals = {"context": context, "logger": logger, "datetime": datetime, "os": os, "json": json}
            # logger.debug(f"Перед выполнением execute_code. Контекст: {context}")
            exec(code_to_execute, execution_globals)
            # logger.debug(f"После выполнения execute_code. Контекст: {context}")
            # Контекст изменяется напрямую, так как он передается по ссылке в execution_globals
            logger.info(f"Шаг execute_code успешно выполнил код: {code_to_execute[:100]}...")

        except Exception as e:
            error_msg = f"Ошибка при выполнении кода в шаге execute_code: {e}"
            logger.error(error_msg, exc_info=True)
            context["__step_error__"] = error_msg
        
        return context
    
    async def handle_log_message(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага типа log_message.
        Логирует сообщение с возможностью подстановки переменных из контекста.
        """
        step_config = step_data.get("config", {})

        message_template = step_config.get("message", "")

        level = step_config.get("level", "INFO").upper()
        
        if isinstance(message_template, str) and "{" in message_template and "}" in message_template:
            # Пытаемся разрешить плейсхолдеры
            try:
                resolved_message = _resolve_value_from_context(message_template, context)

            except KeyError as e:
                logger.warning(f"Ошибка подстановки в log_message (KeyError: {{e}}). Исходное сообщение: '{{message_template}}'")
                resolved_message = f"[Ошибка форматирования: {{e}}] {{message_template}}"
            except Exception as e:
                logger.error(f"Непредвиденная ошибка при форматировании log_message: {{e}}. Исходное сообщение: '{{message_template}}'")
                resolved_message = f"[Непредвиденная ошибка форматирования: {{e}}] {{message_template}}"
        else:
            resolved_message = message_template # Если нет плейсхолдеров, используем как есть
            
        # Логируем сообщение с использованием стандартного логгера (loguru)
        # logger.log(level, resolved_message) # Старый вариант с logger.log
        
        # Используем методы info, warning, error и т.д. в зависимости от уровня
        if level == "DEBUG":
            logger.debug(resolved_message)
        elif level == "INFO":
            logger.info(resolved_message)
        elif level == "WARNING":
            logger.warning(resolved_message)
        elif level == "ERROR":
            logger.error(resolved_message)
        elif level == "CRITICAL":
            logger.critical(resolved_message)
        else: # По умолчанию INFO, если уровень неизвестен
            logger.info(f"({level}) {resolved_message}")

        return context

    async def execute_step(self, step_id: str, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        step_type = step_data.get("type")
        logger.info(f"Выполнение шага: ID='{step_id}', Тип='{step_type}'")
        step_data["step_id_for_log"] = step_id # Для логгера в handle_log_message

        resolved_params = {}
        if "params" in step_data and isinstance(step_data["params"], dict):
            resolved_params = _resolve_value_from_context(step_data["params"], context)
        
        handler_method = self.step_handlers.get(step_type)
        
        if handler_method:
            try:
                # === НАЧАЛО ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===
                copied_context_for_handler = context.copy()

                # === КОНЕЦ ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===

                import inspect
                sig = inspect.signature(handler_method)
                num_expected_params = len(sig.parameters)
                
                updated_context_from_handler = None # Инициализируем
                if num_expected_params == 3: 
                    updated_context_from_handler = await handler_method(step_data, copied_context_for_handler, self) # Используем step_data и copied_context_for_handler
                elif num_expected_params == 2: 
                    updated_context_from_handler = await handler_method(step_data, copied_context_for_handler) # Используем step_data и copied_context_for_handler
                elif num_expected_params == 1: 
                     handler_result = await handler_method(resolved_params) # Оставляем resolved_params для одноаргументных, т.к. они могут ожидать именно "params"
                     # Если хендлер вернул словарь, считаем это обновлением контекста
                     if isinstance(handler_result, dict):
                         updated_context_from_handler = handler_result
                     # Иначе, контекст не меняется этим шагом (или меняется побочным эффектом, что не рекомендуется)
                else:
                    logger.error(f"Обработчик для {step_type} имеет неизвестную сигнатуру: {sig}")
                    context["__step_error__"] = f"Неверная сигнатура обработчика для {step_type}"
                    # Не возвращаем context здесь, чтобы дать блоку finally обновить его __step_error__
                
                # Хендлер должен вернуть словарь, которым будет обновлен текущий контекст.
                # Если хендлер ничего не вернул (None), то контекст не меняется.
                if isinstance(updated_context_from_handler, dict):
                    context.update(updated_context_from_handler)
                elif updated_context_from_handler is not None: # Вернул что-то, но не словарь
                    logger.warning(f"Обработчик {step_type} для шага '{step_id}' вернул не словарь ({type(updated_context_from_handler)}). Контекст не будет обновлен этим результатом напрямую.")
                    # Можно положить результат в специальный ключ, если это нужно
                    # context[f"__raw_output_{step_id}"] = updated_context_from_handler


            except Exception as e:
                logger.error(f"Ошибка при выполнении шага '{step_id}' (тип: {step_type}): {e}")
                logger.exception(e) # Логируем полный трейсбек
                context["__step_error__"] = f"Ошибка на шаге {step_id}: {str(e)}"
        else:
            logger.warning(f"Не найден обработчик для типа шага: {step_type} (ID: {step_id})")
            context["__step_error__"] = f"Неизвестный тип шага: {step_type}"
            
        return context

    async def execute_scenario(self, scenario_doc: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Выполняет сценарий, используя ScenarioStateMachine для управления состоянием и переходами.

        Args:
            scenario_doc: Документ сценария из БД (словарь).
            context: Начальный контекст выполнения (опционально).

        Returns:
            Словарь с результатом выполнения, включая финальный контекст.
        """
        agent_id = context.get("agent_id") if context else None
        if not agent_id:
            logger.warning("agent_id не предоставлен в начальном контексте для execute_scenario.")
            # agent_id = scenario_doc.get("meta", {}).get("created_by_agent_id") 

        # Инициализация начального контекста
        initial_context_from_doc = scenario_doc.get("initial_context")
        if isinstance(initial_context_from_doc, dict):
            current_context = initial_context_from_doc.copy()
        else:
            current_context = {}
        
        logger.info(f"[SCENARIO_EXECUTOR DEBUG] initial_context_from_doc type: {type(initial_context_from_doc)}")
        logger.info(f"[SCENARIO_EXECUTOR DEBUG] initial_context_from_doc content: {json.dumps(initial_context_from_doc, indent=2, default=str)}")
        logger.info(f"[SCENARIO_EXECUTOR DEBUG] current_context (после .copy() или {{}}): {json.dumps(current_context, indent=2, default=str)}")

        if context: # Это context, переданный в execute_scenario
            current_context.update(context)
            # logger.info(f"[SCENARIO_EXECUTOR DEBUG] После current_context.update(context): {json.dumps(current_context, indent=2, default=str)}") # Старый лог

        # Добавляем системные переменные в контекст
        if "__current_scenario_id__" not in current_context:
            current_context["__current_scenario_id__"] = str(scenario_doc.get("_id", scenario_doc.get("id")))
        if "__current_agent_id__" not in current_context and agent_id:
            current_context["__current_agent_id__"] = agent_id
        
        # Гарантируем наличие current_datetime, если он не был передан или не был в initial_context
        if "current_datetime" not in current_context:
            current_context["current_datetime"] = datetime.now().isoformat()
        elif not current_context.get("current_datetime"): # Если ключ есть, но значение пустое/None
            current_context["current_datetime"] = datetime.now().isoformat()

        # === НАЧАЛО ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===
        logger.info(f"[SCENARIO_EXECUTOR DEBUG] current_context ПЕРЕД logger.info(Начало выполнения...): {json.dumps(current_context, indent=2, default=str)}")
        # === КОНЕЦ ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===

        logger.info(f"Начало выполнения сценария: {scenario_doc.get('name', scenario_doc.get('_id'))} с контекстом: {current_context}")

        try:
            # Передаем копию контекста в state_machine, чтобы она могла его использовать для условий
            # и не изменять оригинальный current_context напрямую во время своей работы.
            state_machine = ScenarioStateMachine(
                scenario=scenario_doc, 
                context=current_context.copy(),
                executor=self
            )
        except Exception as e:
            logger.error(f"Ошибка инициализации ScenarioStateMachine: {e}", exc_info=True)
            return {
                "agent_id": agent_id,
                "scenario_id": str(scenario_doc.get("_id", scenario_doc.get("id"))),
                "success": False,
                "error": f"Ошибка инициализации ScenarioStateMachine: {str(e)}",
                "context": current_context,
            }

        execution_successful = True
        error_message = None
        
        # Получаем первый шаг
        current_step_details = state_machine.current_step() 

        while current_step_details:
            step_id_for_log = current_step_details.get('id', state_machine.current_step_index if hasattr(state_machine, 'current_step_index') else "N/A")
            step_type_for_log = current_step_details.get('type', "N/A")
            logger.info(f"Выполнение шага: ID='{step_id_for_log}', Type='{step_type_for_log}'")
            logger.debug(f"Данные шага: {current_step_details}")
            logger.debug(f"Контекст перед шагом '{step_id_for_log}': {current_context}")
            
            try:
                # Выполняем шаг с помощью метода execute_step самого ScenarioExecutor
                # execute_step уже содержит логику разрешения плейсхолдеров в step_data и вызова обработчика
                updated_context_after_step = await self.execute_step(step_id_for_log, current_step_details, current_context)
                current_context.update(updated_context_after_step) # Обновляем основной контекст

                # Проверка на ошибки выполнения шага, установленные в self.execute_step или обработчиках
                if "__step_error__" in current_context:
                    error_message = current_context["__step_error__"]
                    logger.error(f"Ошибка выполнения шага {step_id_for_log}: {error_message}")
                    # Удаляем ошибку из контекста, чтобы она не переносилась дальше как переменная
                    del current_context["__step_error__"]
                    execution_successful = False
                    break 
                
                # Проверка на критические ошибки сценария
                if "__scenario_error__" in current_context:
                    error_message = current_context["__scenario_error__"]
                    logger.error(f"Критическая ошибка сценария на шаге {step_id_for_log}: {error_message}")
                    del current_context["__scenario_error__"]
                    execution_successful = False
                    break

                # Передаем обновленный основной контекст в state_machine (копию).
                # Это нужно, чтобы state_machine мог использовать актуальные значения для вычисления условий перехода.
                state_machine.context = current_context.copy() 
                
                # Переход к следующему шагу. state_machine.next_step() обновит свое внутреннее состояние 
                # (например, self.state["step_index"]) и вернет данные следующего шага.
                current_step_details = state_machine.next_step() 
                
                if not current_step_details:
                    logger.info(f"Сценарий '{scenario_doc.get('name', scenario_doc.get('_id'))}' успешно завершен после шага {step_id_for_log}.")
                    break

            except Exception as e:
                logger.error(f"Непредвиденная ошибка при выполнении цикла для шага {step_id_for_log}: {e}", exc_info=True)
                error_message = f"Непредвиденная ошибка в цикле выполнения: {str(e)}"
                execution_successful = False
                break
        
        final_status_message = f"Scenario '{scenario_doc.get('name', scenario_doc.get('_id'))}' execution "
        if execution_successful and not error_message:
            final_status_message += "completed successfully."
        else:
            final_status_message += f"failed. Error: {error_message if error_message else 'Unknown error'}"
        
        logger.info(final_status_message)

        return {
            "agent_id": agent_id,
            "scenario_id": str(scenario_doc.get("_id", scenario_doc.get("id"))),
            "success": execution_successful and not error_message,
            "error": error_message, # Будет None если ошибок не было
            "message": final_status_message,
            "context": current_context,
        }

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

    async def run_scenario_by_id(self, scenario_id: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Загружает сценарий по ID из репозитория и выполняет его.
        
        Args:
            scenario_id: ID сценария для загрузки и выполнения.
            context: Исходный контекст (опционально).
            
        Returns:
            Финальный контекст после выполнения всех шагов, или None в случае ошибки загрузки сценария.
        """
        logger.info(f"Запрос на выполнение сценария по ID: '{scenario_id}'")
        if context is None:
            context = {} # Инициализируем пустой контекст, если не предоставлен

        # Добавляем scenario_id в контекст, если его там нет, или если он отличается
        # Это может быть полезно для логирования или внутренней логики
        if context.get("scenario_id") != scenario_id:
            context["scenario_id"] = scenario_id # Может перезаписать, если уже был другой

        try:
            scenario_model = await self.scenario_repo.get_by_id(scenario_id)
            if not scenario_model:
                logger.error(f"Сценарий с ID '{scenario_id}' не найден в репозитории.")
                # В этом случае, возможно, стоит вернуть ошибку в контексте или возбудить исключение,
                # чтобы вызывающий код мог это обработать.
                # Пока просто возвращаем None, указывая на неудачу запуска.
                # Вызывающий код в TelegramPlugin должен будет это проверить.
                return None 
            
            scenario_dict = scenario_model.model_dump(exclude_none=True)
            
            # Перед выполнением, убедимся, что критически важные данные для Telegram есть в контексте, если они нужны
            # Например, user_id и chat_id. Они должны были быть добавлены вызывающим кодом (TelegramPlugin).
            if "user_id" not in context or "chat_id" not in context:
                logger.warning(f"При запуске сценария '{scenario_id}' в контексте отсутствуют 'user_id' или 'chat_id'. Контекст: {context}")
                # Это не обязательно фатальная ошибка для самого executor, но может быть проблемой для шагов сценария
            
            logger.info(f"Сценарий '{scenario_id}' (Имя: {scenario_dict.get('name', 'N/A')}) загружен. Начальный контекст: {context}")
            
            return await self.execute_scenario(scenario_dict, context)
        except Exception as e:
            logger.error(f"Критическая ошибка во время загрузки или выполнения сценария по ID '{scenario_id}': {e}", exc_info=True)
            # Также возвращаем None или обрабатываем ошибку иначе
            return None 