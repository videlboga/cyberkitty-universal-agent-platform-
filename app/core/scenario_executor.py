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
# from app.plugins.scheduling_plugin import SchedulingPlugin
from telegram.ext import Application
import requests
from app.db.scenario_repository import ScenarioRepository
from app.db.agent_repository import AgentRepository
from app.models.scenario import Scenario, ScenarioStep, PluginActionStep, BranchStep, LogStep, StartStep, EndStep, SwitchScenarioStep
from app.core.utils import _resolve_value_from_context, resolve_string_template # <-- ДОБАВЛЕН ИМПОРТ

# Для разрешения циклических зависимостей при аннотации типов
if TYPE_CHECKING:
    from app.plugins.llm_plugin import LLMPlugin # <--- Импорт LLMPlugin для аннотаций

# Получаем токен из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

class ScenarioExecutor:
    # Константы для типов шагов
    AUTO_EXECUTABLE_STEP_TYPES = ["action", "branch", "log_message", "start", "end"]
    
    def __init__(self, plugins: List[Any], scenario_repo: Optional[Any] = None):
        self.plugins = {p.__class__.__name__: p for p in plugins}
        self.scenario_repo = scenario_repo
        logger.info(f"[ScenarioExecutor] Инициализирован с плагинами: {list(self.plugins.keys())}")
        
        # Инициализируем словарь обработчиков шагов
        self.step_handlers: Dict[str, Callable] = {}
        self.waiting_for_input_events: Dict[str, Any] = {}
        self.paused_scenarios: Dict[str, Any] = {}
        
        # Регистрируем базовые обработчики из самого executor
        self._register_core_handlers()
        
        # Регистрируем обработчики из плагинов
        self._register_plugin_handlers()
        
        logger.info(f"[ScenarioExecutor] Инициализация завершена. Зарегистрировано обработчиков: {len(self.step_handlers)}")
        logger.debug(f"[ScenarioExecutor] Список обработчиков: {list(self.step_handlers.keys())}")
    
    def _register_core_handlers(self):
        """Регистрирует базовые обработчики шагов"""
        self.step_handlers.update({
            "action": self.handle_action,
            "branch": self.handle_branch,
            "log_message": self.handle_log_message,
            "log": self.handle_log_message,  # Алиас для log_message
            "start": self.handle_start,
            "end": self.handle_end,
            "message": self.handle_message,
            "input": self.handle_input,
            "execute_code": self.handle_execute_code,
        })
        logger.info(f"[ScenarioExecutor] Зарегистрированы базовые обработчики: {list(self.step_handlers.keys())}")
    
    def _register_plugin_handlers(self):
        """Регистрирует обработчики шагов из плагинов"""
        for plugin_name, plugin in self.plugins.items():
            try:
                if hasattr(plugin, 'register_step_handlers'):
                    plugin.register_step_handlers(self.step_handlers)
                    logger.info(f"[ScenarioExecutor] Обработчики от плагина '{plugin_name}' зарегистрированы")
                else:
                    logger.warning(f"[ScenarioExecutor] Плагин '{plugin_name}' не имеет метода register_step_handlers")
            except Exception as e:
                logger.error(f"[ScenarioExecutor] Ошибка регистрации обработчиков от плагина '{plugin_name}': {e}")

    def get_plugin(self, name: str):
        plugin = self.plugins.get(name)
        if not plugin:
            logger.error(f"[ScenarioExecutor] Плагин '{name}' не найден!")
        return plugin

    async def execute_scenario(self, scenario: Scenario, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context.copy() if context else {}
        steps = scenario.steps
        step_idx = 0
        step_id_map = {step.id: idx for idx, step in enumerate(steps)}
        logger.info(f"[ScenarioExecutor] Запуск сценария '{scenario.name}' ({scenario.scenario_id})")
        while step_idx < len(steps):
            step = steps[step_idx]
            logger.info(f"[ScenarioExecutor] Шаг {step.id} ({step.type})")
            try:
                if isinstance(step, PluginActionStep):
                    plugin = self.get_plugin(step.plugin)
                    if not plugin:
                        raise Exception(f"Плагин '{step.plugin}' не найден")
                    params = {k: _resolve_value_from_context(v, context) for k, v in step.params.items()}
                    result = await plugin.execute_action(step.action, params, context)
                    context[step.result_var] = result
                    logger.info(f"[ScenarioExecutor] Результат шага '{step.id}' сохранён в '{step.result_var}': {result}")
                    next_step = step.next_step
                elif isinstance(step, BranchStep):
                    cond = _resolve_value_from_context(step.condition, context)
                    logger.info(f"[ScenarioExecutor] Ветвление: условие '{step.condition}' => {cond}")
                    next_step = step.true_next if cond else step.false_next
                elif isinstance(step, LogStep):
                    msg = _resolve_value_from_context(step.params.get("message", ""), context)
                    level = step.params.get("level", "INFO").upper()
                    getattr(logger, level.lower(), logger.info)(f"[ScenarioExecutor][LOG] {msg}")
                    next_step = step.next_step
                elif isinstance(step, SwitchScenarioStep):
                    new_scenario_id = _resolve_value_from_context(step.params.get("new_scenario_id"), context)
                    logger.info(f"[ScenarioExecutor] Переключение на сценарий '{new_scenario_id}'")
                    return {"switch_scenario": new_scenario_id, "context": context}
                elif isinstance(step, EndStep):
                    logger.info(f"[ScenarioExecutor] Сценарий завершён на шаге '{step.id}'")
                    break
                else:
                    raise Exception(f"Неизвестный тип шага: {step.type}")

                # Переход к следующему шагу
                if next_step:
                    if next_step in step_id_map:
                        step_idx = step_id_map[next_step]
                    else:
                        logger.error(f"[ScenarioExecutor] Не найден шаг с id '{next_step}'")
                        break
                else:
                    step_idx += 1
            except Exception as e:
                logger.error(f"[ScenarioExecutor] Ошибка на шаге '{step.id}': {e}")
                context["__step_error__"] = str(e)
                break
        return context

    async def handle_message(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        message_text = step_data.get("params", {}).get("text", "(пустое сообщение)")
        resolved_message = _resolve_value_from_context(message_text, context)
        logger.info(f"Обработчик handle_message: {resolved_message}")
        return None  # Возвращаем None для завершенных шагов
    
    async def handle_input(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Any:
        step_params = step_data.get("params", {})
        input_type = step_params.get("input_type")
        step_id = step_data.get("step_id_for_log", "unknown_input_step")

        if input_type == "callback_query":
            output_var = step_params.get("output_var")
            if output_var and output_var in context and context[output_var] is not None:
                logger.info(f"Шаг input ({step_id}) типа 'callback_query': Ввод уже предоставлен. Продолжаем.")
                return None  # Возвращаем None вместо context для продолжения

            logger.info(f"Шаг input ({step_id}) типа 'callback_query'. Ввод еще не предоставлен. Регистрация ожидания.")
            chat_id = context.get("telegram_chat_id") or context.get("chat_id")
            user_id = context.get("user_id")
            scenario_id = context.get("__current_scenario_id__") # Это должно быть установлено в execute_scenario
            
            if not chat_id or not user_id or not scenario_id:
                err_msg = f"Input step ({step_id}): Missing data for scenario_instance_id (chat_id, user_id, scenario_id)"
                logger.error(err_msg)
                context["__step_error__"] = err_msg
                return None  # Возвращаем None для завершенных шагов

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
        return None  # Возвращаем None для завершенных шагов
    
    async def handle_branch(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        return None # Логика в ScenarioStateMachine
    
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

    async def handle_start(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        logger.info(f"Обработчик handle_start: Начало сценария '{context.get('__current_scenario_id__', 'N/A')}'")
        return None
    
    async def handle_end(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        logger.info(f"Обработчик handle_end: Завершение сценария '{context.get('__current_scenario_id__', 'N/A')}'")
        return None
    
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
    
    async def handle_log_message(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
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
        return None  # Возвращаем None для завершенных шагов

    async def execute_step(self, step_data: Dict[str, Any], state_machine: ScenarioStateMachine, scenario_id_for_log: str) -> Optional[str]:
        step_type = step_data.get("type")
        handler = self.step_handlers.get(step_type)
        logger.info(f"[DEBUG] execute_step: step_type={step_type}, handler type={type(handler)}, handler value={handler}")
        if not handler:
            logger.error(f"Нет обработчика для типа шага: {step_type}. Проверьте, что нужный плагин зарегистрирован.")
            raise Exception(f"No handler for step type: {step_type}")
        
        # Проверяем сигнатуру handler чтобы понять какие параметры передавать
        import inspect
        sig = inspect.signature(handler)
        param_names = list(sig.parameters.keys())
        
        # Если handler принимает state_machine (как handle_action), передаем его
        if len(param_names) >= 2 and 'state_machine' in param_names[1] or 'state_machine_obj' in param_names[1]:
            return await handler(step_data, state_machine)
        else:
            # Обычные обработчики получают только context
            return await handler(step_data, state_machine.context)

    async def execute_scenario(self, scenario_doc: Union[Dict[str, Any], Scenario], initial_context_from_runner: Optional[Dict[str, Any]] = None, agent_id_from_runner: Optional[str] = None) -> Dict[str, Any]:
        logger.critical(f"[EXECUTE_SCENARIO_ENTRY] scenario_doc type: {type(scenario_doc)}, initial_context_from_runner type: {type(initial_context_from_runner)}, agent_id_from_runner: {agent_id_from_runner}")

        if isinstance(scenario_doc, Scenario): # Если это Pydantic модель
            try:
                scenario_data = scenario_doc.model_dump(exclude_none=True)
            except Exception as e_dump:
                logger.critical(f"[EXECUTE_SCENARIO_CRITICAL_ERROR] Error during scenario_doc.model_dump(): {e_dump}", exc_info=True)
                return {"status": "error", "message": f"Error dumping scenario model: {e_dump}"}
        elif isinstance(scenario_doc, dict):
            scenario_data = scenario_doc
        else:
            logger.error(f"execute_scenario: scenario_doc должен быть dict или Scenario, получено {type(scenario_doc)}")
            logger.critical(f"[EXECUTE_SCENARIO_CRITICAL_ERROR] Invalid scenario_doc type: {type(scenario_doc)}")
            return {"status": "error", "message": "Invalid scenario_doc type."}

        if not isinstance(scenario_data, dict):
            err_msg = f"Internal error: scenario_data is not a dict after processing scenario_doc. Type: {type(scenario_data)}"
            logger.critical(f"[EXECUTE_SCENARIO_CRITICAL_ERROR] {err_msg}")
            return {"status": "error", "message": err_msg}

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
        # УДАЛЕНО: if current_agent_id: ... agent_doc = await self.agent_repo.get_by_id(current_agent_id) ...
        # Теперь executor не обращается к репозиторию агентов, а работает только с тем, что пришло в initial_context_from_runner
        logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] 1.2a effective_sm_context after initial_context_from_runner: {json.dumps(effective_sm_context, indent=2, default=str, ensure_ascii=False)}")
        
        # 1.3 Контекст, переданный при вызове /run или /execute (самый высокий приоритет)
        if initial_context_from_runner:
            effective_sm_context.update(initial_context_from_runner)
        logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] 1.3 effective_sm_context after initial_context_from_runner: {json.dumps(effective_sm_context, indent=2, default=str, ensure_ascii=False)}")
        
        # 1.4 Системные переменные (перезаписывают все предыдущие, если есть коллизии)
        effective_sm_context["__current_scenario_id__"] = scenario_id
        if agent_id_from_runner: # Убедимся, что agent_id есть
            effective_sm_context["agent_id"] = agent_id_from_runner # Это основной ключ для использования в сценариях
            effective_sm_context["__current_agent_id__"] = agent_id_from_runner # Системный, для внутренних нужд
        logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] 1.4 effective_sm_context after system vars: {json.dumps(effective_sm_context, indent=2, default=str, ensure_ascii=False)}")

        if "__scenario_instance_id__" not in effective_sm_context: # Генерируем, если не пришел (не возобновление)
            user_id_for_instance = effective_sm_context.get("user_id", "system")
            chat_id_val = effective_sm_context.get("chat_id", effective_sm_context.get("telegram_chat_id", "no_chat"))
            timestamp_for_id = time.time()
            effective_sm_context["__scenario_instance_id__"] = f"{scenario_id}_{user_id_for_instance}_{chat_id_val}_{timestamp_for_id}"
            logger.info(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] Generated new __scenario_instance_id__: {effective_sm_context['__scenario_instance_id__']}")
        
        logger.debug(f"[EXECUTE_SCENARIO SCENARIO_ID:{scenario_id}] Effective initial context for SM: {json.dumps(effective_sm_context, indent=2, default=str, ensure_ascii=False)}")

        logger.critical(f"[EXECUTE_SCENARIO PRE-SM-INIT DUMP SCENARIO_ID:{scenario_id}] scenario_data: {json.dumps(scenario_data, indent=2, default=str, ensure_ascii=False)}")
        logger.critical(f"[EXECUTE_SCENARIO PRE-SM-INIT DUMP SCENARIO_ID:{scenario_id}] effective_sm_context: {json.dumps(effective_sm_context, indent=2, default=str, ensure_ascii=False)}")

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
            
            logger.critical(f"[EXECUTE_SCENARIO LOOP SCENARIO_ID:{scenario_id} STEP_ID:{step_id_for_log}] current_step_details: {json.dumps(current_step_details, indent=2, default=str, ensure_ascii=False)}")
            logger.critical(f"[EXECUTE_SCENARIO LOOP SCENARIO_ID:{scenario_id} STEP_ID:{step_id_for_log}] sm.context BEFORE execute_step: {json.dumps(sm.context, indent=2, default=str, ensure_ascii=False)}")
            
            try:
                result_after_step_execution = await self.execute_step(current_step_details, sm, scenario_id)
                logger.info(f"[DEBUG] result_after_step_execution: type={type(result_after_step_execution)}, value={result_after_step_execution}")

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
                
                elif result_after_step_execution is not None:
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
            
            if not current_step_details and not sm.is_finished:
                if not sm.context.get("__step_error__"): 
                    error_message = f"Failed to determine next step after '{step_id_for_log}' during resume. Scenario '{scenario_name}' ended unexpectedly."
                    logger.error(error_message)
                    sm.context["__step_error__"] = error_message
                execution_successful = False # Явно указываем на неудачу
                break

        # Формирование финального ответа
        final_context_to_return = sm.context.copy() # Берем актуальный контекст из SM
        final_context_to_return["scenario_id"] = scenario_id # Убедимся, что ID сценария есть
        if agent_id_from_runner:
            final_context_to_return["agent_id"] = agent_id_from_runner

        if execution_successful and sm.is_finished:
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
        
        # Добавляем детальное логирование перед возвратом
        logger.critical(f"[EXECUTE_SCENARIO_RETURN] final_context_to_return keys: {list(final_context_to_return.keys())}")
        for key, value in final_context_to_return.items():
            logger.critical(f"[EXECUTE_SCENARIO_RETURN] {key}: type={type(value)}, value={str(value)[:100]}...")
            
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
                logger.info(f"[DEBUG] result_after_step_execution: type={type(result_after_step_execution)}, value={result_after_step_execution}")

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
            
            if not current_step_details and not sm.is_finished:
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


        if execution_successful and sm.is_finished:
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
        buttons_layout_template = params.get("buttons_layout")

        if not chat_id_template or not text_template:
            err_msg = f"Шаг {step_id} (telegram_send_message): Не указан chat_id или text."
            logger.error(err_msg)
            context["__step_error__"] = err_msg
            return context

        chat_id = _resolve_value_from_context(chat_id_template, context)
        text = str(_resolve_value_from_context(text_template, context))
        
        # Параметры для кнопок
        buttons_data_template = params.get("buttons_data") # Используем buttons_data из сценария
        buttons_layout_template = params.get("buttons_layout")

        buttons_data_resolved = None
        if buttons_data_template:
            if isinstance(buttons_data_template, list):
                buttons_data_resolved = []
                for button_template_item in buttons_data_template:
                    if isinstance(button_template_item, dict):
                        resolved_button_item = {}
                        for k, v_template in button_template_item.items():
                            resolved_button_item[k] = _resolve_value_from_context(v_template, context)
                        buttons_data_resolved.append(resolved_button_item)
                    else:
                        buttons_data_resolved.append(button_template_item) 
            else:
                buttons_data_resolved = _resolve_value_from_context(buttons_data_template, context)
        
        buttons_layout_resolved = _resolve_value_from_context(buttons_layout_template, context) if buttons_layout_template else None
        
        logger.debug(f"[TELEGRAM_SEND_MESSAGE_EXECUTOR] chat_id:'{chat_id}', text:'{text}', resolved_buttons_data:'{buttons_data_resolved}', resolved_buttons_layout:'{buttons_layout_resolved}'")

        telegram_plugin = self.get_plugin("TelegramPlugin")
        if not telegram_plugin:
            err_msg = f"Шаг {step_id}: TelegramPlugin не найден в ScenarioExecutor."
            logger.error(err_msg)
            context["__step_error__"] = err_msg
            return context
        
        logger.debug(f"[telegram_send_message STEP_ID:{step_id}] Chat ID: {chat_id}, Text: '{text}', Keyboard: {buttons_data_resolved}")
        
        try:
            response = await telegram_plugin.send_message(
                chat_id=str(chat_id),
                text=text,
                buttons_data=buttons_data_resolved, # Передаем resolved buttons_data
                buttons_layout=buttons_layout_resolved # Передаем resolved buttons_layout
            )
            
            if response and hasattr(response, 'message_id'):
                 # Сохраняем ID сообщения, которое содержит кнопки, для возможного использования в input шаге
                 # или для редактирования сообщения в будущем
                 context["message_id_with_buttons"] = response.message_id 
                 context[f"__last_message_id_{step_id}"] = response.message_id # Для специфичного отслеживания
                 context["__last_message_id"] = response.message_id # Общий последний ID
                 logger.info(f"[telegram_send_message STEP_ID:{step_id}] Message ID {response.message_id} сохранен в контекст (message_id_with_buttons).")
            elif response:
                logger.warning(f"[telegram_send_message STEP_ID:{step_id}] telegram_plugin.send_message вернул ответ, но без message_id: {response}")
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
        logger.debug(f"[GET_PLUGIN_BY_TYPE] Searching for '{plugin_type_name}'. Available: {[p.__class__.__name__ for p in self.plugins.values()]}")
        for plugin in self.plugins.values():
            if plugin.__class__.__name__ == plugin_type_name:
                return plugin
        logger.warning(f"Плагин '{plugin_type_name}' не найден.")
        return None