import os
import json
import asyncio
import inspect
import time # ДОБАВЛЕН ИМПОРТ
from typing import Dict, Any, Optional, List, Callable, Union, TYPE_CHECKING # <--- Добавляем TYPE_CHECKING
from loguru import logger
from datetime import datetime
from app.core.state_machine import ScenarioStateMachine
from app.plugins.rag_plugin import RAGPlugin
from app.plugins.telegram_plugin import TelegramPlugin
# Удаляем прямой импорт LLMPlugin, чтобы избежать потенциального цикла, если LLMPlugin когда-то захочет импортировать что-то из executor
# from app.plugins.llm_plugin import LLMPlugin 
# Вместо этого, тип LLMPlugin будет использоваться только в аннотациях и через TYPE_CHECKING, если понадобится
from app.plugins.mongo_storage_plugin import MongoStoragePlugin
from app.plugins.scheduling_plugin import SchedulingPlugin
from telegram.ext import Application
import requests
from app.db.scenario_repository import ScenarioRepository
from app.db.agent_repository import AgentRepository
from app.models.scenario import Scenario
from app.core.utils import _resolve_value_from_context, resolve_string_template # <-- ДОБАВЛЕН ИМПОРТ

# Для разрешения циклических зависимостей при аннотации типов
if TYPE_CHECKING:
    from app.plugins.llm_plugin import LLMPlugin # <--- Импорт LLMPlugin для аннотаций

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/scenario_executor.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip", serialize=True) # Уровень INFO изменен на DEBUG

# Получаем токен из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

class ScenarioExecutor:
    def __init__(self,
                 scenario_repo: ScenarioRepository,
                 agent_repo: AgentRepository,
                 api_base_url: str = "http://localhost:8000",
                 telegram_plugin: Optional[TelegramPlugin] = None,
                 mongo_storage_plugin: Optional[MongoStoragePlugin] = None,
                 scheduling_plugin: Optional[SchedulingPlugin] = None,
                 rag_plugin: Optional[RAGPlugin] = None,
                 llm_plugin: Optional['LLMPlugin'] = None): # <--- LLMPlugin теперь в кавычках как Forward Reference
        self.scenario_repo = scenario_repo
        self.agent_repo = agent_repo
        self.api_base_url = api_base_url
        self.step_handlers = {}
        self._plugins: tuple = tuple() 
        self._plugins_initialized_flag = False
        self.waiting_for_input_events = {} 
        self.paused_scenarios = {} 
        
        temp_plugins_list = []
        if telegram_plugin: temp_plugins_list.append(telegram_plugin)
        if mongo_storage_plugin: temp_plugins_list.append(mongo_storage_plugin)
        if scheduling_plugin: temp_plugins_list.append(scheduling_plugin)
        if rag_plugin: temp_plugins_list.append(rag_plugin)
        if llm_plugin: temp_plugins_list.append(llm_plugin)
        
        self._plugins = tuple(temp_plugins_list) 
        self._plugins_initialized_flag = True

        logger.info(f"[SCENARIO_EXECUTOR __init__] Initial self._plugins (tuple): {self._plugins}")
        self._register_default_handlers()
        self._init_plugins()
        self.step_handlers["execute_sub_scenario"] = self._handle_execute_sub_scenario
        logger.info("ScenarioExecutor инициализирован")
        logger.info(f"[SCENARIO_EXECUTOR __init__ END] id(self): {id(self)}, id(self._plugins): {id(self._plugins)}, self._plugins: {self._plugins}")

    @property
    def plugins(self) -> tuple:
        logger.debug(f"[SCENARIO_EXECUTOR .plugins GETTER] id(self): {id(self)}, Reading self._plugins: {self._plugins}")
        return self._plugins

    @plugins.setter
    def plugins(self, value: tuple):
        logger.warning(f"[SCENARIO_EXECUTOR .plugins SETTER ATTEMPT] id(self): {id(self)}, Attempting to set self.plugins to: {value}.")
        if not self._plugins_initialized_flag:
            self._plugins = value
            logger.info(f"[SCENARIO_EXECUTOR .plugins SETTER] self._plugins set to: {self._plugins} during initial setup.")
        else:
            logger.error(f"[SCENARIO_EXECUTOR .plugins SETTER] CRITICAL: Attempt to modify self.plugins after initialization!")

    def _register_default_handlers(self):
        self.step_handlers["message"] = self.handle_message
        self.step_handlers["input"] = self.handle_input
        self.step_handlers["branch"] = self.handle_branch
        self.step_handlers["rag_search"] = self.handle_rag_search # Предполагая, что RAGPlugin будет передан и инициализирован
        self.step_handlers["action"] = self.handle_action
        self.step_handlers["start"] = self.handle_start
        self.step_handlers["end"] = self.handle_end
        self.step_handlers["execute_code"] = self.handle_execute_code
        self.step_handlers["log_message"] = self.handle_log_message
        self.step_handlers["telegram_send_message"] = self.telegram_send_message
        self.step_handlers["telegram_edit_message"] = self.telegram_edit_message
        logger.info("Зарегистрированы обработчики для стандартных типов шагов.")
    
    def _init_plugins(self):
        logger.info(f"[SCENARIO_EXECUTOR _init_plugins START] self.plugins: {[p.__class__.__name__ for p in self.plugins]}")
        for plugin in self.plugins:
            plugin_name = plugin.__class__.__name__
            if hasattr(plugin, 'register_step_handlers') and callable(plugin.register_step_handlers):
                try:
                    plugin.register_step_handlers(self.step_handlers)
                    logger.info(f"Обработчики {plugin_name} зарегистрированы. Keys: {list(self.step_handlers.keys())}")
                except Exception as e:
                    logger.error(f"Ошибка при регистрации обработчиков для {plugin_name}: {e}")
            else:
                logger.warning(f"Плагин {plugin_name} не имеет метода register_step_handlers.")
        logger.info(f"[SCENARIO_EXECUTOR _init_plugins END] Final step_handlers keys: {list(self.step_handlers.keys())}")

    async def handle_message(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        message_text = step_data.get("params", {}).get("text", "(пустое сообщение)")
        resolved_message = _resolve_value_from_context(message_text, context)
        logger.info(f"Обработчик handle_message: {resolved_message}")
        return context
    
    async def handle_input(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Any:
        step_params = step_data.get("params", {})
        input_type = step_params.get("input_type")
        step_id = step_data.get("step_id_for_log", "unknown_input_step")

        if input_type == "callback_query":
            output_var = step_params.get("output_var")
            if output_var and output_var in context and context[output_var] is not None:
                logger.info(f"Шаг input ({step_id}) типа 'callback_query': Ввод уже предоставлен. Продолжаем.")
                return context 

            logger.info(f"Шаг input ({step_id}) типа 'callback_query'. Ввод еще не предоставлен. Регистрация ожидания.")
            chat_id = context.get("telegram_chat_id") or context.get("chat_id")
            user_id = context.get("user_id")
            scenario_id = context.get("__current_scenario_id__") # Это должно быть установлено в execute_scenario
            
            if not chat_id or not user_id or not scenario_id:
                err_msg = f"Input step ({step_id}): Missing data for scenario_instance_id (chat_id, user_id, scenario_id)"
                logger.error(err_msg)
                context["__step_error__"] = err_msg
                return context

            scenario_instance_id = context.get("__scenario_instance_id__")
            if not scenario_instance_id: # Должен быть создан в execute_scenario
                scenario_instance_id = f"{scenario_id}_{user_id}_{chat_id}_{datetime.now().timestamp()}"
                context["__scenario_instance_id__"] = scenario_instance_id 
                logger.warning(f"Шаг input ({step_id}): __scenario_instance_id__ не был в контексте, сгенерирован новый: {scenario_instance_id}")

            message_id_with_buttons = context.get("message_id_with_buttons") # Это поле должно устанавливаться telegram_send_message
            if not message_id_with_buttons:
                logger.warning(f"Шаг input ({step_id}) 'callback_query' не нашел 'message_id_with_buttons' в контексте.")

            self.waiting_for_input_events[scenario_instance_id] = {
                "message_id": message_id_with_buttons, "output_var": output_var,
                "expected_callback_data_pattern": step_params.get("expected_callback_data"),
                "scenario_id": scenario_id, "step_id": step_id, "chat_id": chat_id, "user_id": user_id,
                "status": "waiting", "timestamp": datetime.now().isoformat()
            }
            logger.info(f"Шаг input ({step_id}): Зарегистрировано ожидание для instance_id='{scenario_instance_id}'.")
            return "PAUSED_WAITING_FOR_CALLBACK"
            
        logger.warning(f"Шаг input ({step_id}) с неизвестным input_type='{input_type}' или не указан. Возвращаем контекст.")
        return context
    
    async def handle_branch(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return context # Логика в ScenarioStateMachine
    
    async def handle_rag_search(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        rag_plugin = self.get_plugin_by_type("RAGPlugin")
        if not rag_plugin:
            logger.error("RAGPlugin не найден в ScenarioExecutor для шага rag_search.")
            context["__step_error__"] = "RAGPlugin not found"
            return context
        
        params = step_data.get("params", {})
        query_template = params.get("query", "")
        query = _resolve_value_from_context(query_template, context)
        collection_name = _resolve_value_from_context(params.get("collection_name", "default"), context)
        output_var = params.get("output_var", "rag_results")
        
        try:
            results = await rag_plugin.search(query, collection_name)
            context[output_var] = results
            logger.info(f"RAG поиск: колл='{collection_name}', запрос='{query}', найдено={len(results) if results else 0}")
        except Exception as e:
            logger.error(f"Ошибка RAG поиска: {e}")
            context[output_var] = {"error": str(e)}
        return context
    
    async def _update_context_from_updates(self, updates: Dict[str, Any], context: Dict[str, Any], scenario_id: str, step_id: str) -> Dict[str, Any]:
        logger.debug(f"[_update_context_from_updates SCENARIO_ID:{scenario_id} STEP_ID:{step_id}] Original context ID: {id(context)}, Context BEFORE updates: {json.dumps(context, indent=2, default=str, ensure_ascii=False)}")
        processed_updates_log = {}
        for key, value_template in updates.items():
            resolved_value = _resolve_value_from_context(value_template, context)
            keys = key.split('.')
            temp_context_target = context 
            
            logger.debug(f"[_update_context_from_updates] Processing update: key='{key}', value_template='{value_template}', resolved_value='{resolved_value}'")
            logger.debug(f"[_update_context_from_updates]   Initial temp_context_target ID: {id(temp_context_target)}")

            for i, k_part in enumerate(keys[:-1]):
                logger.debug(f"[_update_context_from_updates]     Navigating/creating part: '{k_part}' (part {i+1} of {len(keys)-1}) in temp_context_target (ID: {id(temp_context_target)})")
                if k_part not in temp_context_target or not isinstance(temp_context_target[k_part], dict):
                    logger.debug(f"[_update_context_from_updates]       Part '{k_part}' not found or not a dict. Creating new dict.")
                    temp_context_target[k_part] = {}
                temp_context_target = temp_context_target[k_part] 
                logger.debug(f"[_update_context_from_updates]     temp_context_target is now (ID: {id(temp_context_target)}): {json.dumps(temp_context_target, indent=2, default=str, ensure_ascii=False)}")

            final_key_part = keys[-1]
            logger.debug(f"[_update_context_from_updates]   Setting final_key_part='{final_key_part}' in temp_context_target (ID: {id(temp_context_target)}) to resolved_value='{resolved_value}'")
            temp_context_target[final_key_part] = resolved_value
            
            logger.debug(f"[_update_context_from_updates]   Context (original ref ID: {id(context)}) AFTER update for key '{key}': {json.dumps(context, indent=2, default=str, ensure_ascii=False)}")
            processed_updates_log[key] = resolved_value

        logger.info(f"[_update_context_from_updates SCENARIO_ID:{scenario_id} STEP_ID:{step_id}] Successfully updated context (processed_updates_log): {processed_updates_log}")
        logger.debug(f"[_update_context_from_updates] Final context ID: {id(context)}, Context AFTER all updates: {json.dumps(context, indent=2, default=str, ensure_ascii=False)}")
        return context

    async def handle_action(self, step_data: Dict[str, Any], state_machine_obj: ScenarioStateMachine) -> Dict[str, Any]: # Принимает state_machine
        context = state_machine_obj.context # Работаем с контекстом из state_machine
        step_params = step_data.get("params", {})
        action_type = step_params.get("action_type")
        scenario_id_for_log = state_machine_obj.scenario_id
        step_id_for_log = step_data.get('id', 'unknown_action_step')

        logger.debug(f"[handle_action SCENARIO_ID:{scenario_id_for_log} STEP_ID:{step_id_for_log}] Received action_type: {action_type}, params: {step_params}")

        if not action_type:
            logger.warning(f"[handle_action] Шаг action (ID: {step_id_for_log}) не содержит action_type.")
            context["__step_error__"] = "Шаг action не содержит action_type"
            return context
            
        if action_type == "update_context":
            updates = step_params.get("updates", {})
            # _update_context_from_updates теперь изменяет 'context' (который state_machine_obj.context) по ссылке
            await self._update_context_from_updates(
                updates, 
                context, # Это state_machine_obj.context
                scenario_id=scenario_id_for_log, 
                step_id=step_id_for_log
            )
            # state_machine_obj.context уже обновлен.
            logger.info(f"[handle_action ID: {step_id_for_log}] action 'update_context' executed. SM context should be updated.")
        
        elif action_type == "execute_code":
            code_to_execute = step_params.get("code")
            if not code_to_execute:
                logger.warning(f"[handle_action ID: {step_id_for_log}] Шаг execute_code не содержит кода для выполнения.")
                context["__step_error__"] = "Шаг execute_code: отсутствует параметр 'code'."
            else:
                try:
                    execution_globals = {"context": context, "logger": logger, "datetime": datetime, "os": os, "json": json, "time": time}
                    logger.debug(f"[handle_action ID: {step_id_for_log}] Перед выполнением execute_code. Контекст: {context}")
                    exec(code_to_execute, execution_globals) # context изменяется по ссылке
                    logger.info(f"[handle_action ID: {step_id_for_log}] Шаг execute_code успешно выполнил код: {code_to_execute[:100]}...")
                except Exception as e:
                    error_msg = f"Ошибка при выполнении кода в шаге execute_code (ID: {step_id_for_log}): {e}"
                    logger.error(error_msg, exc_info=True)
                    context["__step_error__"] = error_msg
        else:
            err_msg = f"Неизвестный action_type '{action_type}' в шаге 'action' (ID: {step_id_for_log})."
            logger.warning(err_msg)
            context["__step_error__"] = err_msg
        
        return context # Возвращаем измененный context (который state_machine_obj.context)

    async def handle_start(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Обработчик handle_start: Начало сценария '{context.get('__current_scenario_id__', 'N/A')}'")
        return context
    
    async def handle_end(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Обработчик handle_end: Завершение сценария '{context.get('__current_scenario_id__', 'N/A')}'")
        return context
    
    async def handle_execute_code(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # Этот обработчик вызывается, если тип шага "execute_code", а не "action" с "action_type: execute_code"
        params = step_data.get("params", {})
        code_to_execute = params.get("code")
        step_id = step_data.get("step_id_for_log", "unknown_execute_code_step")
        logger.debug(f"[handle_execute_code STEP_ID:{step_id}] Direct execution.")

        if not code_to_execute:
            logger.warning(f"Шаг execute_code (ID:{step_id}) не содержит кода для выполнения.")
            context["__step_error__"] = f"Шаг execute_code (ID:{step_id}): отсутствует параметр 'code'."
            return context
        try:
            execution_globals = {"context": context, "logger": logger, "datetime": datetime, "os": os, "json": json, "time": time}
            exec(code_to_execute, execution_globals)
            logger.info(f"Шаг execute_code (ID:{step_id}) успешно выполнил код: {code_to_execute[:100]}...")
        except Exception as e:
            error_msg = f"Ошибка при выполнении кода в шаге execute_code (ID:{step_id}): {e}"
            logger.error(error_msg, exc_info=True)
            context["__step_error__"] = error_msg
        return context
    
    async def handle_log_message(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        params = step_data.get("params", {}) # Изменено с config на params для единообразия
        message_template = params.get("message", "")
        level = params.get("level", "INFO").upper()
        resolved_message = _resolve_value_from_context(message_template, context)
        
        if level == "DEBUG": logger.debug(resolved_message)
        elif level == "INFO": logger.info(resolved_message)
        elif level == "WARNING": logger.warning(resolved_message)
        elif level == "ERROR": logger.error(resolved_message)
        elif level == "CRITICAL": logger.critical(resolved_message)
        else: logger.info(f"({level}) {resolved_message}")
        return context

    async def execute_step(self, step_data: Dict[str, Any], state_machine: ScenarioStateMachine, scenario_id_for_log: str) -> Optional[str]:
        step_type = step_data.get("type")
        step_id = step_data.get('id', 'UNKNOWN_STEP')
        step_data["step_id_for_log"] = step_id # Добавляем для использования в обработчиках, если нужно

        logger.debug(f"[execute_step SCENARIO_ID:{scenario_id_for_log} STEP_ID:{step_id}] Type:'{step_type}'. Initial SM context ID: {id(state_machine.context)}")
        
        # Разрешаем плейсхолдеры во всем step_data перед передачей в обработчик
        # Это гарантирует, что обработчик получает уже разрезолвенные параметры
        current_step_data_for_handler = _resolve_value_from_context(step_data.copy(), state_machine.context)
        logger.debug(f"[execute_step SCENARIO_ID:{scenario_id_for_log} STEP_ID:{step_id}] Resolved step_data_for_handler: {json.dumps(current_step_data_for_handler, indent=2, default=str, ensure_ascii=False)}")

        handler_result = None
        try:
            if step_type not in self.step_handlers:
                raise ValueError(f"Обработчик для типа шага '{step_type}' не зарегистрирован.")

            handler_fn = self.step_handlers[step_type]
            sig = inspect.signature(handler_fn)
            
            # Изменение: все обработчики теперь принимают (step_data, state_machine_object) или (step_data, context_dict)
            # Для handle_action передаем state_machine_object, для остальных - context dict
            if step_type == "action": # Особый случай для handle_action
                 if asyncio.iscoroutinefunction(handler_fn):
                    handler_result = await handler_fn(current_step_data_for_handler, state_machine)
                 else:
                    handler_result = handler_fn(current_step_data_for_handler, state_machine)
            else: # Для остальных обработчиков
                if asyncio.iscoroutinefunction(handler_fn):
                    handler_result = await handler_fn(current_step_data_for_handler, state_machine.context)
                else:
                    handler_result = handler_fn(current_step_data_for_handler, state_machine.context)

            # После вызова обработчика, state_machine.context мог быть изменен НАПРЯМУЮ обработчиком (особенно handle_action)
            # Если обработчик вернул словарь, это И ЕСТЬ обновленный контекст, который нужно присвоить state_machine.context.
            # Если обработчик (кроме handle_action) изменяет контекст по ссылке и возвращает его же, это тоже ок.

            if isinstance(handler_result, str) and handler_result.startswith("PAUSED_WAITING_FOR_"):
                logger.info(f"[execute_step SCENARIO_ID:{scenario_id_for_log} STEP_ID:{step_id}] Шаг вернул маркер паузы: {handler_result}")
                return handler_result 
            
            # ИСПРАВЛЕНИЕ: Как обрабатывать результат от плагина
            if handler_result is not None: # Если плагин что-то вернул (не None)
                output_var_name = current_step_data_for_handler.get("params", {}).get("output_var")
                if output_var_name:
                    # Кладём результат плагина в контекст под именем из output_var
                    state_machine.context[output_var_name] = handler_result 
                    logger.debug(f"[execute_step SCENARIO_ID:{scenario_id_for_log} STEP_ID:{step_id}] Plugin returned a result. Stored in context['{output_var_name}']. Context updated.")
                else:
                    # Если output_var не указан, но плагин вернул что-то (кроме None),
                    # это может быть неожиданным. Просто логируем.
                    # Если это был dict, и мы хотели бы его смержить, нужна доп. логика.
                    logger.warning(f"[execute_step SCENARIO_ID:{scenario_id_for_log} STEP_ID:{step_id}] Plugin returned a result, but no 'output_var' specified in step params. Result: {handler_result}. Context NOT automatically updated with this result unless done by plugin itself.")
            
            # Если __step_error__ уже в контексте (установлен обработчиком), то он там и останется.
            if state_machine.context.get("__step_error__"):
                 logger.warning(f"[execute_step SCENARIO_ID:{scenario_id_for_log} STEP_ID:{step_id}] Ошибка в контексте после выполнения обработчика: {state_machine.context['__step_error__']}")
            else:
                logger.info(f"[execute_step SCENARIO_ID:{scenario_id_for_log} STEP_ID:{step_id}] Шаг '{step_type}' успешно выполнен (или обработчик не вернул ошибку явно).")
            
            return None # Успешное выполнение (или ошибка записана в контекст)

        except Exception as e:
            logger.error(f"[execute_step SCENARIO_ID:{scenario_id_for_log} STEP_ID:{step_id}] Ошибка при вызове/выполнении обработчика: {e}", exc_info=True)
            state_machine.context["__step_error__"] = f"Критическая ошибка на шаге {step_id}: {str(e)}"
            return None 
        
    async def execute_scenario(self, scenario_doc: Union[Dict[str, Any], Scenario], initial_context_from_runner: Optional[Dict[str, Any]] = None, agent_id_from_runner: Optional[str] = None) -> Dict[str, Any]:
        if isinstance(scenario_doc, Scenario): # Если это Pydantic модель
            scenario_data = scenario_doc.model_dump(exclude_none=True)
        elif isinstance(scenario_doc, dict):
            scenario_data = scenario_doc
        else:
            logger.error(f"execute_scenario: scenario_doc должен быть dict или Scenario, получено {type(scenario_doc)}")
            return {"status": "error", "message": "Invalid scenario_doc type."}

        scenario_id = scenario_data.get("scenario_id", "unknown_scenario")
        scenario_name = scenario_data.get("name", scenario_id)
        logger.info(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] Starting execution. Agent ID from runner: {agent_id_from_runner}")
        logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] Initial context from runner: {json.dumps(initial_context_from_runner, indent=2, default=str, ensure_ascii=False)}")

        # 1. Формирование начального контекста для StateMachine
        effective_sm_context = {}
        logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] 1.0 effective_sm_context after init: {json.dumps(effective_sm_context, indent=2, default=str, ensure_ascii=False)}")

        # 1.1 Контекст из самого документа сценария (самый низкий приоритет)
        if scenario_data.get("initial_context"):
            effective_sm_context.update(scenario_data["initial_context"])
        logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] 1.1 effective_sm_context after scenario_data['initial_context']: {json.dumps(effective_sm_context, indent=2, default=str, ensure_ascii=False)}")
        
        # 1.2 Контекст из настроек агента (если agent_id известен)
        current_agent_id = agent_id_from_runner or (initial_context_from_runner.get("agent_id") if initial_context_from_runner else None)
        if current_agent_id:
            agent_doc = await self.agent_repo.get_by_id(current_agent_id)
            if agent_doc: # Агент найден
                if agent_doc.initial_context:
                    effective_sm_context.update(agent_doc.initial_context)
                    logger.info(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] Loaded initial_context from agent '{current_agent_id}'.")
                logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] 1.2a effective_sm_context after agent_doc.initial_context: {json.dumps(effective_sm_context, indent=2, default=str, ensure_ascii=False)}")
                
                logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] Agent settings dump: {agent_doc.settings}")
                agent_default_chat_id = agent_doc.settings.get("default_telegram_chat_id") if agent_doc.settings else None
                logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] Extracted agent_default_chat_id: {agent_default_chat_id}")
                logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] current effective_sm_context.get('telegram_chat_id'): {effective_sm_context.get('telegram_chat_id')}")

                if agent_default_chat_id and not effective_sm_context.get("telegram_chat_id"):
                    effective_sm_context["telegram_chat_id"] = agent_default_chat_id
                    logger.info(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] Set 'telegram_chat_id' from agent settings: {agent_default_chat_id}")
                    if not effective_sm_context.get("user_id"):
                        effective_sm_context["user_id"] = str(agent_default_chat_id) 
                        logger.info(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] Set 'user_id' from agent's default_telegram_chat_id: {agent_default_chat_id}")
                else:
                    logger.info(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] 'telegram_chat_id' NOT set from agent settings. Reason: agent_default_chat_id is '{agent_default_chat_id}' OR effective_sm_context already has telegram_chat_id '{effective_sm_context.get('telegram_chat_id')}'")
                logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] 1.2b effective_sm_context after agent_settings (chat_id/user_id): {json.dumps(effective_sm_context, indent=2, default=str, ensure_ascii=False)}")

        # 1.3 Контекст, переданный при вызове /run или /execute (самый высокий приоритет)
        if initial_context_from_runner:
            effective_sm_context.update(initial_context_from_runner)
        logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] 1.3 effective_sm_context after initial_context_from_runner: {json.dumps(effective_sm_context, indent=2, default=str, ensure_ascii=False)}")
        
        # 1.4 Системные переменные (перезаписывают все предыдущие, если есть коллизии)
        effective_sm_context["__current_scenario_id__"] = scenario_id
        if current_agent_id: # Убедимся, что agent_id есть
            effective_sm_context["agent_id"] = current_agent_id # Это основной ключ для использования в сценариях
            effective_sm_context["__current_agent_id__"] = current_agent_id # Системный, для внутренних нужд
        logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] 1.4 effective_sm_context after system vars: {json.dumps(effective_sm_context, indent=2, default=str, ensure_ascii=False)}")

        if "__scenario_instance_id__" not in effective_sm_context: # Генерируем, если не пришел (не возобновление)
            user_id_for_instance = effective_sm_context.get("user_id", "system")
            chat_id_val = effective_sm_context.get("chat_id", effective_sm_context.get("telegram_chat_id", "no_chat"))
            timestamp_for_id = time.time()
            effective_sm_context["__scenario_instance_id__"] = f"{scenario_id}_{user_id_for_instance}_{chat_id_val}_{timestamp_for_id}"
            logger.info(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] Generated new __scenario_instance_id__: {effective_sm_context['__scenario_instance_id__']}")
        
        logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] Effective initial context for SM: {json.dumps(effective_sm_context, indent=2, default=str, ensure_ascii=False)}")

        sm = ScenarioStateMachine(
            scenario=scenario_data, 
            context=effective_sm_context.copy(), # Передаем копию, чтобы SM имел свой собственный экземпляр
            executor=self
        )
        logger.info(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] StateMachine initialized. Initial current_step_index: {sm.current_step_index}, initial context ID: {id(sm.context)}")

        execution_successful = True
        error_message = None
        
        current_step_details = sm.current_step() 
        while current_step_details:
            step_id_for_log = current_step_details.get('id', sm.current_step_index)
            step_type_for_log = current_step_details.get('type', "N/A")
            logger.info(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id} STEP_ID:{step_id_for_log}] Executing Type:'{step_type_for_log}'. SM context ID: {id(sm.context)}")
            
            try:
                result_after_step_execution = await self.execute_step(current_step_details, sm, scenario_id)

                if sm.context.get("__step_error__"):
                    error_message = sm.context["__step_error__"]
                    logger.error(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id} STEP_ID:{step_id_for_log}] Error in context after step: {error_message}")
                    execution_successful = False
                    break 

                if result_after_step_execution == "PAUSED_WAITING_FOR_CALLBACK":
                    scenario_instance_id = sm.context.get("__scenario_instance_id__")
                    if scenario_instance_id:
                        self.paused_scenarios[scenario_instance_id] = {
                            "scenario_doc": scenario_data, "state_machine": sm, 
                            "last_step_id_before_pause": step_id_for_log,
                            "status": "paused", "timestamp": datetime.now().isoformat()
                        }
                        logger.info(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id} INSTANCE_ID:{scenario_instance_id}] Paused at step '{step_id_for_log}'.")
                        final_context = sm.context.copy()
                        final_context.update({
                            "status": "paused", 
                            "message": f"Scenario paused at step {step_id_for_log}, waiting for callback.",
                            "scenario_instance_id": scenario_instance_id
                        })
                        return final_context
                    else: # Это не должно произойти, т.к. instance_id генерируется выше
                        error_message = "Internal error: __scenario_instance_id__ missing on pause."
                        logger.error(error_message)
                        sm.context["__step_error__"] = error_message
                        execution_successful = False
                        break
                
                elif result_after_step_execution is not None: # execute_step должен вернуть None или маркер паузы
                    error_message = f"Internal logic error: execute_step returned unexpected value: '{result_after_step_execution}'."
                    logger.error(error_message)
                    sm.context["__step_error__"] = error_message
                    execution_successful = False
                    break
            
            except Exception as e_outer:
                logger.error(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id} STEP_ID:{step_id_for_log}] Outer loop exception: {e_outer}", exc_info=True)
                error_message = f"Outer-loop execution error at step {step_id_for_log}: {str(e_outer)}"
                sm.context["__step_error__"] = error_message # Записываем ошибку в контекст SM
                execution_successful = False
                break
            
            # Переход к следующему шагу. Контекст SM мог быть изменен в execute_step.
            current_step_details = sm.next_step() # sm.next_step() использует sm.context
            
            if not current_step_details and not sm.is_finished():
                if not sm.context.get("__step_error__"): 
                    error_message = f"Failed to determine next step after '{step_id_for_log}' during resume. Scenario '{scenario_name}' ended unexpectedly."
                    logger.error(error_message)
                    sm.context["__step_error__"] = error_message
                execution_successful = False # Явно указываем на неудачу
                break

        # Формирование финального ответа
        final_context_to_return = sm.context.copy() # Берем актуальный контекст из SM
        final_context_to_return["scenario_id"] = scenario_id # Убедимся, что ID сценария есть
        if current_agent_id:
            final_context_to_return["agent_id"] = current_agent_id

        if execution_successful and sm.is_finished():
            final_context_to_return["success"] = True
            final_context_to_return["message"] = f"Scenario '{scenario_name}' executed successfully."
            logger.info(final_context_to_return["message"])
        else: # Если была ошибка или сценарий не завершился корректно
            final_context_to_return["success"] = False
            # error_message уже содержит ошибку с шага, или __step_error__ из контекста, или общее сообщение
            error_key_to_check = "__step_error__" if "__step_error__" in sm.context else "_step_error"
            raw_error = error_message or sm.context.get(error_key_to_check) or "Unknown execution error or scenario did not finish."
            
            # Упрощаем ошибку, если она является словарем (возможно, копией контекста)
            if isinstance(raw_error, dict):
                simplified_error = raw_error.get(error_key_to_check, str(raw_error)) # Пытаемся извлечь текстовое сообщение
                if isinstance(simplified_error, dict): # Если все еще словарь, просто преобразуем в строку
                    simplified_error = f"Complex error object: {list(simplified_error.keys())}"
            else:
                simplified_error = str(raw_error)

            final_context_to_return["error"] = simplified_error
            final_context_to_return["message"] = f"Scenario '{scenario_name}' execution failed or did not finish. Error: {simplified_error}"
            logger.error(final_context_to_return["message"])
        
        # Очищаем потенциально проблемные ключи из основного уровня возвращаемого контекста
        # Ключи, которые содержали копии контекста или сложные объекты и могли вызывать RecursionError
        keys_to_remove_if_exist = ["start_confirmation_cb", "q1_callback_data", "q2_callback_data", "q3_callback_data", "llm_pizza_response"]
        for key_to_remove in keys_to_remove_if_exist:
            if key_to_remove in final_context_to_return:
                # Вместо полного удаления, можно оставить маркер или упрощенное значение, если нужно
                # final_context_to_return[key_to_remove] = f"<data_omitted_for_key_{key_to_remove}>"
                del final_context_to_return[key_to_remove]

        # Также удаляем внутренние ошибки _step_error и __step_error__ из верхнего уровня, т.к. они уже учтены в final_context_to_return["error"]
        if "_step_error" in final_context_to_return:
            del final_context_to_return["_step_error"]
        if "__step_error__" in final_context_to_return:
            del final_context_to_return["__step_error__"]
            
        return final_context_to_return

    async def _handle_execute_sub_scenario(self, step_data: Dict[str, Any], parent_sm_context: Dict[str, Any]) -> Dict[str, Any]:
        params = step_data.get("params", {})
        sub_scenario_id = params.get("sub_scenario_id")
        input_mapping = params.get("input_mapping", {})
        output_mapping = params.get("output_mapping", {})
        # sub_scenario_agent_id = params.get("sub_scenario_agent_id") # Пока не используется, но может понадобиться

        parent_step_id = step_data.get('id', 'unknown_parent_step')
        logger.info(f"[_handle_execute_sub_scenario PARENT_STEP_ID:{parent_step_id}] sub_scenario_id: {sub_scenario_id}")

        if not sub_scenario_id:
            err_msg = "Шаг 'execute_sub_scenario' не содержит 'sub_scenario_id'."
            logger.error(err_msg)
            parent_sm_context["__step_error__"] = err_msg
            return parent_sm_context

        try:
            sub_scenario_model = await self.scenario_repo.get_by_id(sub_scenario_id)
            if not sub_scenario_model:
                err_msg = f"Под-сценарий с ID '{sub_scenario_id}' не найден."
                logger.error(err_msg)
                parent_sm_context["__step_error__"] = err_msg
                return parent_sm_context
            
            sub_context_initial = {}
            for sub_key, parent_key_or_value_template in input_mapping.items():
                # Разрешаем значение из родительского контекста, если это плейсхолдер
                resolved_parent_value = _resolve_value_from_context(parent_key_or_value_template, parent_sm_context)
                sub_context_initial[sub_key] = resolved_parent_value
            logger.debug(f"Начальный контекст для под-сценария '{sub_scenario_id}': {sub_context_initial}")

            # Определяем agent_id для под-сценария. По умолчанию берем из родительского контекста.
            agent_id_for_sub_scenario = parent_sm_context.get("agent_id")

            final_sub_context_result = await self.execute_scenario(
                scenario_doc=sub_scenario_model, # Передаем модель Pydantic
                initial_context_from_runner=sub_context_initial.copy(),
                agent_id_from_runner=agent_id_for_sub_scenario 
            )
            
            logger.info(f"Под-сценарий '{sub_scenario_id}' завершен. Результат: {final_sub_context_result.get('message')}")
            
            if not final_sub_context_result.get("success", False):
                error_detail = final_sub_context_result.get('error', 'Unknown error in sub-scenario')
                logger.warning(f"Под-сценарий '{sub_scenario_id}' завершился с ошибкой: {error_detail}")
                parent_sm_context["__step_error__"] = f"Ошибка в под-сценарии '{sub_scenario_id}': {error_detail}"
                return parent_sm_context

            # Маппинг результатов. final_sub_context_result это полный результат от execute_scenario,
            # из него нужен сам финальный контекст, который обычно лежит в том же словаре.
            actual_final_sub_context = final_sub_context_result # Так как execute_scenario возвращает сам финальный контекст

            for parent_key, sub_key_or_value_template in output_mapping.items():
                # Разрешаем значение из контекста под-сценария
                resolved_sub_value = _resolve_value_from_context(sub_key_or_value_template, actual_final_sub_context)
                parent_sm_context[parent_key] = resolved_sub_value
            logger.debug(f"Output mapping для под-сценария '{sub_scenario_id}' применен.")

        except Exception as e:
            err_msg = f"Критическая ошибка при выполнении под-сценария '{sub_scenario_id}': {str(e)}"
            logger.error(err_msg, exc_info=True)
            parent_sm_context["__step_error__"] = err_msg
        
        return parent_sm_context

    async def run_scenario_by_id(self, scenario_id: str, initial_context: Optional[Dict[str, Any]] = None, agent_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        logger.info(f"Запрос на выполнение сценария по ID: '{scenario_id}'. Agent ID: {agent_id}")
        initial_context = initial_context or {}
        
        try:
            scenario_model = await self.scenario_repo.get_by_id(scenario_id)
            if not scenario_model:
                logger.error(f"Сценарий с ID '{scenario_id}' не найден.")
                return {"status": "error", "message": f"Scenario with ID '{scenario_id}' not found.", "success": False}
            
            return await self.execute_scenario(
                scenario_doc=scenario_model, 
                initial_context_from_runner=initial_context,
                agent_id_from_runner=agent_id
            )
        except Exception as e:
            logger.error(f"Критическая ошибка при run_scenario_by_id '{scenario_id}': {e}", exc_info=True)
            return {"status": "error", "message": f"Critical error running scenario by ID '{scenario_id}': {str(e)}", "success": False}

    async def resume_scenario(self, scenario_instance_id: str, received_input_data: Any) -> Optional[Dict[str, Any]]:
        logger.info(f"Попытка возобновления сценария. Instance ID: '{scenario_instance_id}', Входные данные: '{received_input_data}'")
        paused_info = self.paused_scenarios.get(scenario_instance_id)
        if not paused_info:
            logger.error(f"Не найден приостановленный сценарий для instance_id: {scenario_instance_id}")
            return {"status": "error", "message": "Paused scenario not found", "success": False}

        waiting_event_info = self.waiting_for_input_events.get(scenario_instance_id)
        if not waiting_event_info: # Может быть уже обработан или удален
            logger.warning(f"Нет информации об ожидаемом событии для instance_id: {scenario_instance_id} при возобновлении. Возможно, дублирующийся callback.")
            # Если сценарий еще числится как paused, но нет waiting_event, это странно. Удалим из paused.
            if scenario_instance_id in self.paused_scenarios: del self.paused_scenarios[scenario_instance_id]
            return {"status": "error", "message": "Waiting event info not found for scenario. Possible duplicate callback.", "success": False}

        sm = paused_info.get("state_machine")
        output_var = waiting_event_info.get("output_var")
        
        if not sm or not output_var:
            logger.error(f"Неполные данные для возобновления {scenario_instance_id}. Очистка.")
            if scenario_instance_id in self.waiting_for_input_events: del self.waiting_for_input_events[scenario_instance_id]
            if scenario_instance_id in self.paused_scenarios: del self.paused_scenarios[scenario_instance_id]
            return {"status": "error", "message": "Incomplete data for resuming", "success": False}

        logger.info(f"Возобновление '{sm.scenario_name}' (instance: {scenario_instance_id}).")
        sm.context[output_var] = received_input_data # Обновляем контекст в SM
        sm.context["__last_input_received__"] = received_input_data # Дополнительно для отладки
        
        del self.waiting_for_input_events[scenario_instance_id]
        del self.paused_scenarios[scenario_instance_id]
        
        # Продолжаем выполнение из цикла execute_scenario, но с существующей SM
        # Это похоже на execute_scenario, но начинается не с начала, а с текущего шага SM.
        # Вместо полного копирования логики execute_scenario, мы вызовем его внутренний цикл.
        # Для этого нужно реструктурировать execute_scenario или создать новую функцию _continue_scenario_execution(sm)
        # Пока что для простоты скопируем и адаптируем цикл:

        current_step_details = sm.current_step() # Это должен быть тот самый 'input' шаг
        execution_successful = True
        error_message = None
        scenario_id = sm.scenario_id # Получаем из SM
        scenario_name = sm.scenario_name

        logger.info(f"[RESUME_LOOP SCENARIO_ID:{scenario_id} INSTANCE_ID:{scenario_instance_id}] Starting loop from step: {current_step_details.get('id') if current_step_details else 'N/A'}")

        while current_step_details:
            step_id_for_log = current_step_details.get('id', sm.current_step_index)
            step_type_for_log = current_step_details.get('type', "N/A")
            logger.info(f"[RESUME_LOOP SCENARIO_ID:{scenario_id} STEP_ID:{step_id_for_log}] Executing Type:'{step_type_for_log}'.")
            
            try:
                result_after_step_execution = await self.execute_step(current_step_details, sm, scenario_id)

                if sm.context.get("__step_error__"):
                    error_message = sm.context["__step_error__"]
                    logger.error(f"[RESUME_LOOP SCENARIO_ID:{scenario_id} STEP_ID:{step_id_for_log}] Error in context: {error_message}")
                    execution_successful = False
                    break 

                if result_after_step_execution == "PAUSED_WAITING_FOR_CALLBACK":
                    logger.error(f"[RESUME_LOOP SCENARIO_ID:{scenario_id} STEP_ID:{step_id_for_log}] Scenario requested PAUSE again immediately after resume! Logic error.")
                    error_message = "Logic error: Scenario requested pause immediately after resume."
                    sm.context["__step_error__"] = error_message
                    # Снова регистрируем паузу, чтобы не потерять состояние, но это индикатор проблемы
                    self.paused_scenarios[scenario_instance_id] = {"scenario_doc": sm.scenario_data, "state_machine": sm, "last_step_id_before_pause": step_id_for_log, "status": "error_re_paused"}
                    self.waiting_for_input_events[scenario_instance_id] = waiting_event_info # Восстанавливаем
                    execution_successful = False
                    break
                
                elif result_after_step_execution is not None:
                    error_message = f"Internal logic error: execute_step returned unexpected value during resume: '{result_after_step_execution}'."
                    logger.error(error_message)
                    sm.context["__step_error__"] = error_message
                    execution_successful = False
                    break
            
            except Exception as e_outer:
                logger.error(f"[RESUME_LOOP SCENARIO_ID:{scenario_id} STEP_ID:{step_id_for_log}] Outer loop exception: {e_outer}", exc_info=True)
                error_message = f"Outer-loop resume error at step {step_id_for_log}: {str(e_outer)}"
                sm.context["__step_error__"] = error_message
                execution_successful = False
                break
            
            current_step_details = sm.next_step()
            
            if not current_step_details and not sm.is_finished():
                if not sm.context.get("__step_error__"): 
                    error_message = f"Failed to determine next step after '{step_id_for_log}' during resume. Scenario '{scenario_name}' ended unexpectedly."
                    logger.error(error_message)
                    sm.context["__step_error__"] = error_message
                execution_successful = False
                break
        
        final_context_to_return = sm.context.copy()
        final_context_to_return["scenario_id"] = scenario_id
        final_context_to_return["agent_id"] = sm.context.get("agent_id") # agent_id должен быть в контексте SM
        final_context_to_return["scenario_instance_id"] = scenario_instance_id


        if execution_successful and sm.is_finished():
            final_context_to_return["success"] = True
            final_context_to_return["message"] = f"Scenario '{scenario_name}' (instance: {scenario_instance_id}) resumed and completed successfully."
            logger.info(final_context_to_return["message"])
        else:
            final_context_to_return["success"] = False
            final_context_to_return["error"] = error_message or sm.context.get("__step_error__") or "Unknown resume error or scenario did not finish."
            final_context_to_return["message"] = f"Scenario '{scenario_name}' (instance: {scenario_instance_id}) resumption failed or did not finish. Error: {final_context_to_return['error']}"
            logger.error(final_context_to_return["message"])
            
        return final_context_to_return

    async def telegram_send_message(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        step_id = step_data.get("step_id_for_log", "unknown_telegram_send_step")
        params = step_data.get("params", {})
        # Сначала пытаемся взять chat_id из параметров шага, затем из контекста (telegram_chat_id или chat_id)
        chat_id_template = params.get("chat_id", context.get("telegram_chat_id", context.get("chat_id")))
        text_template = params.get("text")
        # inline_keyboard из параметров шага (должен быть уже в правильном формате списка списков)
        inline_keyboard_template = params.get("inline_keyboard") 

        if not chat_id_template or not text_template:
            err_msg = f"Шаг {step_id} (telegram_send_message): Не указан chat_id или text."
            logger.error(err_msg)
            context["__step_error__"] = err_msg
            return context

        chat_id = str(_resolve_value_from_context(chat_id_template, context))
        resolved_text = str(_resolve_value_from_context(text_template, context))
        resolved_inline_keyboard = _resolve_value_from_context(inline_keyboard_template, context) if inline_keyboard_template else None
        
        telegram_plugin = self.get_plugin_by_type("TelegramPlugin")
        if not telegram_plugin:
            err_msg = f"Шаг {step_id}: TelegramPlugin не найден в ScenarioExecutor."
            logger.error(err_msg)
            context["__step_error__"] = err_msg
            return context
        
        logger.debug(f"[telegram_send_message STEP_ID:{step_id}] Chat ID: {chat_id}, Text: '{resolved_text}', Keyboard: {resolved_inline_keyboard}")
        
        try:
            # TelegramPlugin.send_message ожидает inline_keyboard как список списков словарей
            message_receipt = await telegram_plugin.send_message(
                chat_id=chat_id,
                text=resolved_text,
                buttons_data=resolved_inline_keyboard # buttons_data это inline_keyboard для плагина
            )
            
            if message_receipt and hasattr(message_receipt, 'message_id'):
                 # Сохраняем ID сообщения, которое содержит кнопки, для возможного использования в input шаге
                 # или для редактирования сообщения в будущем
                 context["message_id_with_buttons"] = message_receipt.message_id 
                 context[f"__last_message_id_{step_id}"] = message_receipt.message_id # Для специфичного отслеживания
                 context["__last_message_id"] = message_receipt.message_id # Общий последний ID
                 logger.info(f"[telegram_send_message STEP_ID:{step_id}] Message ID {message_receipt.message_id} сохранен в контекст (message_id_with_buttons).")
            elif message_receipt:
                logger.warning(f"[telegram_send_message STEP_ID:{step_id}] telegram_plugin.send_message вернул ответ, но без message_id: {message_receipt}")
            else: # Если send_message вернул None (например, из-за ошибки внутри плагина, которая не вызвала исключение)
                logger.warning(f"[telegram_send_message STEP_ID:{step_id}] telegram_plugin.send_message не вернул результат (None).")
                if "__plugin_error__" not in context: # Если плагин сам не установил ошибку
                     context["__step_error__"] = "telegram_plugin.send_message did not return a message receipt."

        except Exception as e:
            logger.error(f"[telegram_send_message STEP_ID:{step_id}] ОШИБКА: {e}", exc_info=True)
            context["__step_error__"] = f"Error in telegram_plugin.send_message: {str(e)}"
        return context

    async def telegram_edit_message(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: Реализовать логику редактирования сообщения
        logger.warning("Обработчик telegram_edit_message еще не реализован.")
        return context

    def get_plugin_by_type(self, plugin_type_name: str) -> Optional[Any]:
        logger.debug(f"[GET_PLUGIN_BY_TYPE] Searching for '{plugin_type_name}'. Available: {[p.__class__.__name__ for p in self.plugins]}")
        for plugin in self.plugins:
            if plugin.__class__.__name__ == plugin_type_name:
                return plugin
        logger.warning(f"Плагин '{plugin_type_name}' не найден.")
        return None