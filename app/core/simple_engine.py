"""
🔧 ПРОСТАЯ STATE MACHINE - РАБОЧИЙ ПРОТОТИП
Демонстрация того, как может выглядеть упрощенная система
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union, List, Callable
from datetime import datetime
import json
from loguru import logger
import asyncio
from .base_plugin import BasePlugin

# ===== ТИПЫ ДАННЫХ =====

@dataclass
class Event:
    """Событие от пользователя"""
    type: str           # "callback", "text", "start"  
    data: Any           # callback_data, text, etc.
    telegram_data: Dict = field(default_factory=dict) # chat_id, message_id, etc.

@dataclass
class StepResult:
    """Результат выполнения шага"""
    response: Optional[str] = None      # Ответ пользователю
    next_step: Optional[str] = None     # Следующий шаг
    update_context: Dict = field(default_factory=dict)  # Обновления контекста
    buttons: List[Dict] = field(default_factory=list)   # Кнопки для Telegram

@dataclass 
class UserState:
    """Состояние пользователя"""
    user_id: str
    scenario_id: str
    current_step: str
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

# ===== БАЗОВЫЕ КЛАССЫ =====

class BaseStep:
    """Базовый класс для всех типов шагов"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    async def execute(self, event: Event, state: UserState) -> StepResult:
        """Выполнить шаг. Должен быть переопределен в наследниках"""
        raise NotImplementedError

    def resolve_template(self, template: str, context: Dict[str, Any]) -> str:
        """Простая подстановка переменных {var}"""
        result = template
        for key, value in context.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

# ===== АТОМАРНЫЕ ШАГИ =====

class MenuStep(BaseStep):
    """Шаг отображения меню с кнопками"""
    
    async def execute(self, event: Event, state: UserState) -> StepResult:
        # Если это не callback - показываем меню
        if event.type != "callback":
            text = self.resolve_template(self.config["text"], state.context)
            buttons = []
            
            for choice_key, choice_config in self.config["choices"].items():
                buttons.append({
                    "text": choice_config.get("text", choice_key),
                    "callback_data": choice_key
                })
            
            return StepResult(
                response=text,
                buttons=buttons,
                next_step=state.current_step  # Остаемся тут, ждем выбор
            )
        
        # Обрабатываем выбор
        choice = event.data
        if choice not in self.config["choices"]:
            return StepResult(
                response="❌ Неверный выбор. Попробуйте снова.",
                next_step=state.current_step
            )
        
        choice_config = self.config["choices"][choice]
        next_step = choice_config.get("next_step")
        
        return StepResult(
            response=None,  # Не отвечаем, просто переходим
            next_step=next_step,
            update_context={"last_choice": choice, "last_choice_text": choice_config.get("text", choice)}
        )

class MessageStep(BaseStep):
    """Шаг отправки простого сообщения"""
    
    async def execute(self, event: Event, state: UserState) -> StepResult:
        text = self.resolve_template(self.config["text"], state.context)
        next_step = self.config.get("next_step")
        
        return StepResult(
            response=text,
            next_step=next_step
        )

class LLMStep(BaseStep):
    """Шаг запроса к LLM"""
    
    async def execute(self, event: Event, state: UserState) -> StepResult:
        # Симуляция LLM запроса
        prompt = self.resolve_template(self.config.get("prompt", "Привет!"), state.context)
        
        # TODO: Здесь будет настоящий вызов LLM API
        llm_response = f"🤖 LLM ответ на: '{prompt}'"
        
        return StepResult(
            response=llm_response,
            next_step=self.config.get("next_step"),
            update_context={"last_llm_response": llm_response}
        )

class EndStep(BaseStep):
    """Шаг завершения сценария"""
    
    async def execute(self, event: Event, state: UserState) -> StepResult:
        text = self.resolve_template(
            self.config.get("text", "✅ Сценарий завершен!"), 
            state.context
        )
        
        return StepResult(
            response=text,
            next_step=None  # None означает конец
        )

# ===== ПРОСТОЙ ENGINE =====

class SimpleScenarioEngine:
    """
    Простой и надежный движок выполнения сценариев.
    
    Основные принципы:
    1. Один движок для всех сценариев
    2. Простая регистрация плагинов
    3. Явная передача контекста
    4. Предсказуемое поведение
    5. Легкая отладка
    """
    
    def __init__(self):
        self.step_handlers: Dict[str, Callable] = {}
        self.plugins: Dict[str, BasePlugin] = {}
        self.logger = logger.bind(component="SimpleScenarioEngine")
        
        # Регистрируем базовые обработчики
        self._register_core_handlers()
        
    def _register_core_handlers(self):
        """Регистрирует базовые обработчики шагов."""
        self.step_handlers.update({
            "start": self._handle_start,
            "end": self._handle_end,
            "action": self._handle_action,
            "input": self._handle_input,
            "conditional_execute": self._handle_conditional_execute,
            "switch_scenario": self._handle_switch_scenario,  # Переключение сценариев
            "log_message": self._handle_log_message,  # Логирование сообщений
            "branch": self._handle_branch,  # Условные переходы
        })
        self.logger.info("Зарегистрированы базовые обработчики", handlers=list(self.step_handlers.keys()))
        
    def register_plugin(self, plugin: BasePlugin):
        """
        Регистрирует плагин и его обработчики.
        
        Args:
            plugin: Экземпляр плагина наследующего BasePlugin
        """
        self.plugins[plugin.name] = plugin
        
        # ВАЖНО: Передаем ссылку на движок плагину
        plugin.engine = self
        
        # Регистрируем обработчики плагина
        plugin_handlers = plugin.register_handlers()
        self.step_handlers.update(plugin_handlers)
        
        self.logger.info(
            f"Плагин {plugin.name} зарегистрирован", 
            plugin=plugin.name,
            new_handlers=list(plugin_handlers.keys())
        )
        
    async def healthcheck(self) -> Dict[str, bool]:
        """
        Проверяет здоровье движка и всех плагинов.
        
        Returns:
            Dict[str, bool]: Состояние движка и каждого плагина
        """
        health = {"engine": True}
        
        for plugin_name, plugin in self.plugins.items():
            try:
                health[plugin_name] = await plugin.healthcheck()
            except Exception as e:
                self.logger.error(f"Ошибка healthcheck плагина {plugin_name}: {e}")
                health[plugin_name] = False
                
        self.logger.info("Healthcheck завершен", health=health)
        return health
        
    async def execute_scenario(self, scenario: Union[str, Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполняет сценарий от начала до конца.
        
        Args:
            scenario: Данные сценария (объект) или scenario_id (строка)
            context: Начальный контекст выполнения
            
        Returns:
            Dict[str, Any]: Финальный контекст после выполнения
        """
        # Если передан scenario_id как строка, загружаем сценарий из MongoDB
        if isinstance(scenario, str):
            scenario_id = scenario
            # Загружаем сценарий через MongoDB плагин
            get_scenario_step = {
                "id": "load_scenario",
                "type": "mongo_get_scenario",
                "params": {
                    "scenario_id": scenario_id,
                    "output_var": "loaded_scenario"
                }
            }
            
            temp_context = {}
            await self.execute_step(get_scenario_step, temp_context)
            
            if "loaded_scenario" not in temp_context or not temp_context["loaded_scenario"].get("success"):
                raise ValueError(f"Не удалось загрузить сценарий {scenario_id}")
                
            scenario = temp_context["loaded_scenario"]["scenario"]
        
        scenario_id = scenario.get("scenario_id", "unknown")
        steps_data = scenario.get("steps", [])
        
        # Поддерживаем как объект, так и массив шагов
        if isinstance(steps_data, dict):
            # Если steps - объект, конвертируем в список
            steps = list(steps_data.values())
        else:
            # Если steps - уже список
            steps = steps_data
        
        self.logger.info(
            f"Начинаю выполнение сценария {scenario_id}",
            scenario_id=scenario_id,
            steps_count=len(steps),
            initial_context=context
        )
        
        # Инициализируем контекст
        execution_context = {
            **context,
            "scenario_id": scenario_id,
            "current_step": None,
            "execution_started": True
        }
        
        try:
            # Ищем первый шаг (обычно type="start")
            current_step = self._find_first_step(steps)
            
            if not current_step:
                raise ValueError(f"Не найден первый шаг в сценарии {scenario_id}")
                
            # Выполняем шаги последовательно
            while current_step:
                execution_context["current_step"] = current_step.get("id")
                
                # Выполняем текущий шаг
                step_result = await self.execute_step(current_step, execution_context)
                
                # Обновляем контекст результатом
                execution_context.update(step_result)
                
                # Находим следующий шаг
                current_step = self._find_next_step(steps, current_step, execution_context)
                
            self.logger.info(
                f"Сценарий {scenario_id} выполнен успешно",
                scenario_id=scenario_id,
                final_context=execution_context
            )
            
            return execution_context
            
        except Exception as e:
            self.logger.error(
                f"Ошибка выполнения сценария {scenario_id}: {e}",
                scenario_id=scenario_id,
                current_step=execution_context.get("current_step"),
                error=str(e)
            )
            raise
            
    async def execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполняет один шаг сценария.
        
        Args:
            step: Данные шага из сценария
            context: Контекст выполнения
            
        Returns:
            Dict[str, Any]: Обновленный контекст
        """
        step_id = step.get("id", "unknown")
        step_type = step.get("type", "unknown")
        
        self.logger.info(
            f"Выполняю шаг {step_id}",
            step_id=step_id,
            step_type=step_type,
            step=step
        )
        
        # Проверяем есть ли обработчик для типа шага
        if step_type not in self.step_handlers:
            raise ValueError(f"Неизвестный тип шага: {step_type}")
            
        handler = self.step_handlers[step_type]
        
        try:
            # Выполняем обработчик
            result = await handler(step, context)
            
            self.logger.info(
                f"Шаг {step_id} выполнен успешно",
                step_id=step_id,
                step_type=step_type
            )
            
            return result if result else context
            
        except Exception as e:
            self.logger.error(
                f"Ошибка выполнения шага {step_id}: {e}",
                step_id=step_id,
                step_type=step_type,
                error=str(e)
            )
            raise
            
    def _find_first_step(self, steps: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Находит первый шаг сценария."""
        # Ищем шаг с типом "start"
        for step in steps:
            if step.get("type") == "start":
                return step
                
        # Если нет start, берем первый шаг
        return steps[0] if steps else None
        
    def _find_next_step(self, steps: List[Dict[str, Any]], current_step: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Находит следующий шаг для выполнения.
        
        Args:
            steps: Все шаги сценария
            current_step: Текущий шаг
            context: Контекст выполнения
            
        Returns:
            Optional[Dict[str, Any]]: Следующий шаг или None если сценарий завершен
        """
        # Проверяем переопределение следующего шага (для условных переходов)
        next_step_id = context.get("next_step_override") or current_step.get("next_step_id") or current_step.get("next_step")
        
        # Очищаем переопределение после использования
        if "next_step_override" in context:
            del context["next_step_override"]
        
        if not next_step_id:
            # Нет следующего шага - сценарий завершен
            return None
            
        # Ищем шаг по ID
        for step in steps:
            if step.get("id") == next_step_id:
                return step
                
        self.logger.warning(f"Не найден следующий шаг с ID: {next_step_id}")
        return None
        
    # === БАЗОВЫЕ ОБРАБОТЧИКИ ===
    
    async def _handle_start(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик шага 'start'."""
        self.logger.info("Обрабатываю шаг start", step_id=step.get("id"))
        return context
        
    async def _handle_end(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик шага 'end'.""" 
        self.logger.info("Обрабатываю шаг end", step_id=step.get("id"))
        context["execution_completed"] = True
        return context
        
    async def _handle_action(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик шага 'action'."""
        self.logger.info("Обрабатываю шаг action", step_id=step.get("id"))
        
        params = step.get("params", {})
        action = params.get("action")
        action_type = params.get("action_type")
        
        # Обрабатываем встроенные типы действий
        if action_type == "update_context":
            updates = params.get("updates", {})
            for key, value in updates.items():
                # Подставляем переменные в значения
                if isinstance(value, str):
                    resolved_value = self._resolve_template(value, context)
                    # Пытаемся преобразовать в число если это возможно
                    if resolved_value.isdigit():
                        resolved_value = int(resolved_value)
                    context[key] = resolved_value
                else:
                    context[key] = value
            
            self.logger.info(f"✅ Контекст обновлен: {updates}")
            return context
        
        if action:
            # Если указано действие, вызываем соответствующий обработчик плагина
            self.logger.info(f"Вызываю обработчик действия: {action}")
            
            # Подготавливаем контекст для обработчика
            handler_context = context.copy()
            
            # Добавляем параметры из шага в контекст
            for key, value in params.items():
                if key != "action":  # action не передаем как параметр
                    # Подставляем переменные в значения
                    if isinstance(value, str):
                        resolved_value = self._resolve_template(value, context)
                        handler_context[key] = resolved_value
                    else:
                        handler_context[key] = value
            
            # Вызываем обработчик
            if action in self.step_handlers:
                handler = self.step_handlers[action]
                try:
                    # Создаем step для обработчика с правильной сигнатурой
                    action_step = {
                        "id": f"action_{action}",
                        "type": action,
                        "params": params
                    }
                    result = await handler(action_step, context)
                    
                    # Обновляем контекст результатом
                    if isinstance(result, dict):
                        # Сохраняем результат в переменную, если указана
                        context_key = params.get("context_key")
                        if context_key:
                            context[context_key] = result
                        else:
                            # Иначе обновляем весь контекст
                            context.update(result)
                    
                    self.logger.info(f"✅ Действие {action} выполнено успешно")
                    
                except Exception as e:
                    self.logger.error(f"❌ Ошибка выполнения действия {action}: {e}")
                    context["action_error"] = str(e)
                    context["action_success"] = False
            else:
                self.logger.error(f"❌ Обработчик для действия '{action}' не найден")
                context["action_error"] = f"Handler for action '{action}' not found"
                context["action_success"] = False
        else:
            # Если действие не указано, просто копируем параметры в контекст
            if params:
                context.update(params)
                self.logger.info(f"Добавлены параметры в контекст: {params}")
        
        return context
        
    async def _handle_input(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага 'input' - ожидание ввода пользователя.
        
        При достижении input шага выполнение останавливается.
        Продолжение происходит через callback или новый запрос.
        """
        self.logger.info("Обрабатываю шаг input - останавливаю выполнение", step_id=step.get("id"))
        
        context["waiting_for_input"] = True
        context["input_step_id"] = step.get("id")
        
        # Останавливаем выполнение - следующий шаг будет выполнен при получении ввода
        raise StopExecution(f"Ожидание ввода на шаге {step.get('id')}")
        
    async def _handle_conditional_execute(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Универсальный обработчик условного выполнения.
        
        Поддерживает:
        1. Простые условия: "exists:user_data.documents"
        2. Сравнения: "equals:user_role:admin"
        3. Python выражения: "len(user_data.get('documents', [])) > 0"
        
        Примеры:
        {
            "type": "conditional_execute",
            "params": {
                "condition": "exists:user_data.documents",
                "true_step": "user_exists",
                "false_step": "create_user"
            }
        }
        
        {
            "type": "conditional_execute", 
            "params": {
                "condition": "equals:telegram_bot_token_available:true",
                "true_step": "start_polling",
                "false_step": "no_token"
            }
        }
        """
        self.logger.info("Обрабатываю шаг conditional_execute", step_id=step.get("id"))
        
        params = step.get("params", {})
        condition = params.get("condition")
        true_step = params.get("true_step")
        false_step = params.get("false_step")
        
        result = False
        
        try:
            result = self._evaluate_condition(condition, context)
            
            if result:
                context["next_step_override"] = true_step
                self.logger.info(f"Условие '{condition}' истинно, переход к {true_step}")
            else:
                context["next_step_override"] = false_step
                self.logger.info(f"Условие '{condition}' ложно, переход к {false_step}")
                
        except Exception as e:
            self.logger.error(f"Ошибка оценки условия '{condition}': {e}")
            context["next_step_override"] = false_step
            context["condition_error"] = str(e)
                
        context["condition_result"] = result
        return context
        
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Универсальная оценка условий.
        
        Поддерживаемые форматы:
        1. exists:path.to.field - проверяет существование поля
        2. equals:field:value - проверяет равенство
        3. not_empty:field - проверяет что поле не пустое
        4. Python выражение - eval() для сложных условий
        """
        if not condition:
            return False
            
        # Простые условия
        if ":" in condition:
            parts = condition.split(":", 2)
            condition_type = parts[0]
            
            if condition_type == "exists":
                # exists:user_data.documents
                field_path = parts[1]
                return self._check_field_exists(field_path, context)
                
            elif condition_type == "equals":
                # equals:telegram_bot_token_available:true
                field_name = parts[1]
                expected_value = parts[2]
                actual_value = context.get(field_name)
                
                # Преобразуем строковые значения
                if expected_value.lower() == "true":
                    expected_value = True
                elif expected_value.lower() == "false":
                    expected_value = False
                elif expected_value.isdigit():
                    expected_value = int(expected_value)
                    
                return actual_value == expected_value
                
            elif condition_type == "not_empty":
                # not_empty:user_data.documents
                field_path = parts[1]
                value = self._get_field_value(field_path, context)
                if isinstance(value, (list, dict, str)):
                    return len(value) > 0
                return value is not None
                
        # Fallback: Python выражение
        try:
            resolved_condition = self._resolve_condition(condition, context)
            return bool(eval(resolved_condition))
        except Exception as e:
            self.logger.warning(f"Не удалось оценить условие '{condition}': {e}")
            return False
            
    def _check_field_exists(self, field_path: str, context: Dict[str, Any]) -> bool:
        """Проверяет существование поля по пути (например: user_data.documents)"""
        try:
            value = self._get_field_value(field_path, context)
            return value is not None
        except:
            return False
            
    def _get_field_value(self, field_path: str, context: Dict[str, Any]) -> Any:
        """Получает значение поля по пути (например: user_data.documents)"""
        parts = field_path.split(".")
        current = context
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
                
        return current
        
    async def _handle_switch_scenario(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик переключения сценариев.
        
        Пример шага:
        {
            "id": "switch1",
            "type": "switch_scenario",
            "params": {
                "scenario_id": "new_scenario",
                "context_mapping": {
                    "user_id": "{user_id}",
                    "chat_id": "{chat_id}"
                }
            }
        }
        """
        self.logger.info("Обрабатываю переключение сценария", step_id=step.get("id"))
        
        try:
            params = step.get("params", {})
            scenario_id = params.get("scenario_id")
            context_mapping = params.get("context_mapping", {})
            
            if not scenario_id:
                raise ValueError("Не указан scenario_id для переключения")
            
            # Подставляем переменные в scenario_id
            resolved_scenario_id = self._resolve_template(scenario_id, context)
            
            # Подготавливаем контекст для нового сценария
            new_context = {}
            
            # Копируем базовые поля (включая None значения)
            base_fields = ["user_id", "chat_id", "agent_id", "channel_id"]
            for field in base_fields:
                if field in context:
                    new_context[field] = context[field]
                    
            # Если user_id отсутствует, но есть chat_id, используем chat_id как user_id
            if "user_id" not in new_context or new_context.get("user_id") is None:
                if "chat_id" in new_context and new_context["chat_id"] is not None:
                    new_context["user_id"] = new_context["chat_id"]
                    
            # Применяем mapping
            for target_key, source_template in context_mapping.items():
                resolved_value = self._resolve_template(str(source_template), context)
                new_context[target_key] = resolved_value
                
            # Добавляем информацию о переключении (без циклических ссылок)
            new_context.update({
                "switched_from_scenario": context.get("scenario_id"),
                "switch_reason": "engine_switch"
            })
            
            self.logger.info(f"Переключаюсь на сценарий: {resolved_scenario_id}")
            
            # ВЫПОЛНЯЕМ НОВЫЙ СЦЕНАРИЙ ПРЯМО ЗДЕСЬ
            switched_context = await self.execute_scenario(resolved_scenario_id, new_context)
            
            # Обновляем текущий контекст результатом переключения (без циклических ссылок)
            context.update({
                "scenario_switched": True,
                "switched_to": resolved_scenario_id,
                "switch_successful": True
            })
            
            self.logger.info(f"✅ Успешно переключился на сценарий {resolved_scenario_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка переключения сценария: {e}")
            context.update({
                "scenario_switched": False,
                "switch_error": str(e),
                "switch_successful": False
            })
            return context
    

    
    def _resolve_template(self, template: str, context: Dict[str, Any]) -> str:
        """Простая подстановка переменных {var} в строке."""
        if not isinstance(template, str):
            return str(template)
            
        result = template
        
        # Специальные переменные
        special_vars = {
            "current_timestamp": datetime.now().isoformat(),
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "current_time": datetime.now().strftime("%H:%M:%S"),
            "current_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Подставляем специальные переменные
        for key, value in special_vars.items():
            result = result.replace(f"{{{key}}}", str(value))
        
        # Подставляем переменные из контекста
        for key, value in context.items():
            result = result.replace(f"{{{key}}}", str(value))
            
        return result
        
    def _resolve_condition(self, condition: str, context: Dict[str, Any]) -> str:
        """Простая подстановка переменных в условии."""
        if not condition:
            return "False"
            
        result = condition
        for key, value in context.items():
            if isinstance(value, str):
                result = result.replace(key, f"'{value}'")
            else:
                result = result.replace(key, str(value))
                
        return result
    
    async def _handle_log_message(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик для логирования сообщений.
        
        Args:
            step: Данные шага
            context: Контекст выполнения
            
        Returns:
            Dict[str, Any]: Обновленный контекст
        """
        params = step.get("params", {})
        message_template = params.get("message", "")
        level = params.get("level", "INFO").upper()
        
        # Разрешаем шаблон сообщения
        resolved_message = self._resolve_template(message_template, context)
        
        # Логируем с соответствующим уровнем
        if level == "DEBUG":
            self.logger.debug(resolved_message)
        elif level == "INFO":
            self.logger.info(resolved_message)
        elif level == "WARNING":
            self.logger.warning(resolved_message)
        elif level == "ERROR":
            self.logger.error(resolved_message)
        elif level == "CRITICAL":
            self.logger.critical(resolved_message)
        else:
            self.logger.info(f"({level}) {resolved_message}")
            
        return context
    
    async def _handle_branch(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик условных переходов.
        
        Args:
            step: Данные шага
            context: Контекст выполнения
            
        Returns:
            Dict[str, Any]: Обновленный контекст
        """
        params = step.get("params", {})
        conditions = params.get("conditions", [])
        default_next_step_id = params.get("default_next_step_id")
        
        # Проверяем условия по порядку
        for condition_data in conditions:
            condition = condition_data.get("condition", "")
            next_step_id = condition_data.get("next_step_id")
            
            try:
                # Простая оценка условия
                if self._evaluate_branch_condition(condition, context):
                    context["next_step_override"] = next_step_id
                    self.logger.info(f"Условие '{condition}' истинно, переход к {next_step_id}")
                    return context
            except Exception as e:
                self.logger.error(f"Ошибка оценки условия '{condition}': {e}")
                continue
        
        # Если ни одно условие не сработало, используем default
        if default_next_step_id:
            context["next_step_override"] = default_next_step_id
            self.logger.info(f"Все условия ложны, переход к default: {default_next_step_id}")
        
        return context
    
    def _evaluate_branch_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Оценивает условие для branch шага.
        
        Args:
            condition: Условие для оценки (например: "context.counter > 10")
            context: Контекст выполнения
            
        Returns:
            bool: Результат оценки условия
        """
        if not condition:
            return False
        
        try:
            # Заменяем context.field на значения из контекста
            resolved_condition = condition
            
            # Простая замена context.field на значения
            import re
            context_refs = re.findall(r'context\.(\w+)', condition)
            for field in context_refs:
                if field in context:
                    value = context[field]
                    if isinstance(value, str):
                        resolved_condition = resolved_condition.replace(f"context.{field}", f"'{value}'")
                    else:
                        resolved_condition = resolved_condition.replace(f"context.{field}", str(value))
                else:
                    # Если поле не найдено, заменяем на None
                    resolved_condition = resolved_condition.replace(f"context.{field}", "None")
            
            # Выполняем условие
            result = eval(resolved_condition)
            self.logger.debug(f"Условие '{condition}' -> '{resolved_condition}' -> {result}")
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Ошибка оценки условия '{condition}': {e}")
            return False
        
    def get_registered_handlers(self) -> List[str]:
        """Возвращает список всех зарегистрированных обработчиков."""
        return list(self.step_handlers.keys())
        
    def get_registered_plugins(self) -> List[str]:
        """Возвращает список зарегистрированных плагинов."""
        return list(self.plugins.keys())
    
    async def call_handler(self, handler_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Вызывает обработчик по имени.
        
        Args:
            handler_name: Имя обработчика
            context: Контекст для передачи обработчику
            
        Returns:
            Dict[str, Any]: Результат выполнения обработчика
        """
        if handler_name not in self.step_handlers:
            self.logger.error(f"Обработчик '{handler_name}' не найден", available=list(self.step_handlers.keys()))
            return {"success": False, "error": f"Handler '{handler_name}' not found"}
        
        try:
            handler = self.step_handlers[handler_name]
            result = await handler(context)
            
            # Если результат не содержит success, добавляем его
            if isinstance(result, dict) and "success" not in result:
                result["success"] = True
                
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения обработчика '{handler_name}': {e}")
            return {"success": False, "error": str(e)}


class StopExecution(Exception):
    """
    Исключение для остановки выполнения сценария.
    
    Используется когда нужно остановить выполнение и дождаться 
    пользовательского ввода (например, на шаге 'input').
    """
    pass

# ===== ДЕМО СЦЕНАРИЙ =====

DEMO_SCENARIO = {
    "scenario_id": "demo_test",
    "name": "Демо-тест простой системы",
    "steps": {
        "start": {
            "type": "menu",
            "text": "🎯 **Демо простой системы**\n\nВыберите тест:",
            "choices": {
                "test_message": {
                    "text": "📝 Простое сообщение",
                    "next_step": "show_message"
                },
                "test_llm": {
                    "text": "🤖 Тест LLM",
                    "next_step": "llm_request"
                },
                "test_context": {
                    "text": "📊 Тест контекста",
                    "next_step": "context_demo"
                },
                "exit": {
                    "text": "🚪 Выход",
                    "next_step": "end"
                }
            }
        },
        "show_message": {
            "type": "message",
            "text": "✅ Это простое сообщение!\n\nВаш выбор был: {last_choice_text}",
            "next_step": "back_to_menu"
        },
        "llm_request": {
            "type": "llm",
            "prompt": "Пользователь выбрал тест LLM. Скажи что-то умное!",
            "next_step": "back_to_menu"
        },
        "context_demo": {
            "type": "message", 
            "text": "📊 **Контекст пользователя:**\n\nUser ID: {user_id}\nТекущий шаг: {current_step}\nПоследний выбор: {last_choice}",
            "next_step": "back_to_menu"
        },
        "back_to_menu": {
            "type": "menu",
            "text": "Хотите продолжить?",
            "choices": {
                "back": {
                    "text": "🔙 Назад в меню",
                    "next_step": "start"
                },
                "exit": {
                    "text": "🚪 Завершить",
                    "next_step": "end"
                }
            }
        },
        "end": {
            "type": "end",
            "text": "👋 До свидания! Спасибо за тестирование простой системы."
        }
    }
}

# ===== ДЕМО ИСПОЛЬЗОВАНИЕ =====

async def demo():
    """Демонстрация работы простой системы"""
    engine = SimpleScenarioEngine()
    engine.load_scenario("demo_test", DEMO_SCENARIO)
    
    # Симуляция событий от пользователя
    user_id = "demo_user"
    scenario_id = "demo_test"  # Исправлено: используем правильный ID
    
    # Запуск сценария
    result = await engine.process_event(user_id, Event("start", ""), scenario_id)
    print(f"1. {result.response}")
    print(f"   Кнопки: {[b['text'] for b in result.buttons]}")
    
    # Выбор LLM теста
    result = await engine.process_event(user_id, Event("callback", "test_llm"), scenario_id)
    print(f"2. {result.response}")
    
    # Возврат в меню
    result = await engine.process_event(user_id, Event("callback", "back"), scenario_id)
    print(f"3. {result.response}")
    print(f"   Кнопки: {[b['text'] for b in result.buttons]}")
    
    # Завершение
    result = await engine.process_event(user_id, Event("callback", "exit"), scenario_id)
    print(f"4. {result.response}")


# ===== СОЗДАНИЕ ДВИЖКА С ПЛАГИНАМИ =====

async def create_engine() -> SimpleScenarioEngine:
    """
    Создаёт и настраивает SimpleScenarioEngine с плагинами.
    
    Заменяет simple_dependencies.get_simple_engine() для явной инициализации.
    Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО - никаких синглтонов!
    
    Returns:
        SimpleScenarioEngine: Настроенный движок с плагинами
    """
    from loguru import logger
    
    logger.info("🔧 Создание SimpleScenarioEngine...")
    
    # Создаем движок
    engine = SimpleScenarioEngine()
    
    # === ИНИЦИАЛИЗАЦИЯ ПЛАГИНОВ ===
    
    try:
        # 1. MongoDB Plugin - для хранения агентов и сценариев
        logger.info("📦 Инициализация MongoDB Plugin...")
        from app.plugins.mongo_plugin import MongoPlugin
        mongo_plugin = MongoPlugin()
        await mongo_plugin.initialize()
        engine.register_plugin(mongo_plugin)
        logger.info("✅ MongoDB Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB Plugin недоступен: {e}")
    
    try:
        # 2. Telegram Plugin - для работы с Telegram
        logger.info("📦 Инициализация SimpleTelegram Plugin...")
        from app.plugins.simple_telegram_plugin import SimpleTelegramPlugin
        telegram_plugin = SimpleTelegramPlugin()
        await telegram_plugin.initialize()
        engine.register_plugin(telegram_plugin)
        logger.info("✅ SimpleTelegram Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleTelegram Plugin недоступен: {e}")
    
    try:
        # 3. LLM Plugin - для работы с языковыми моделями
        logger.info("📦 Инициализация SimpleLLM Plugin...")
        from app.plugins.simple_llm_plugin import SimpleLLMPlugin
        llm_plugin = SimpleLLMPlugin()
        await llm_plugin.initialize()
        engine.register_plugin(llm_plugin)
        logger.info("✅ SimpleLLM Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleLLM Plugin недоступен: {e}")
    
    try:
        # 4. RAG Plugin - для работы с базой знаний
        logger.info("📦 Инициализация SimpleRAG Plugin...")
        from app.plugins.simple_rag_plugin import SimpleRAGPlugin
        rag_plugin = SimpleRAGPlugin()
        await rag_plugin.initialize()
        engine.register_plugin(rag_plugin)
        logger.info("✅ SimpleRAG Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleRAG Plugin недоступен: {e}")
    
    try:
        # 5. Scheduler Plugin - для отложенного выполнения задач
        logger.info("📦 Инициализация SimpleScheduler Plugin...")
        from app.plugins.simple_scheduler_plugin import SimpleSchedulerPlugin
        scheduler_plugin = SimpleSchedulerPlugin()
        await scheduler_plugin.initialize()
        engine.register_plugin(scheduler_plugin)
        logger.info("✅ SimpleScheduler Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleScheduler Plugin недоступен: {e}")
    
    # === ФИНАЛИЗАЦИЯ ===
    
    logger.info("🎯 SimpleScenarioEngine настроен")
    logger.info(f"📋 Зарегистрированные плагины: {engine.get_registered_plugins()}")
    logger.info(f"🔧 Доступные обработчики: {len(engine.get_registered_handlers())}")
    
    # Проверяем здоровье всех плагинов
    health = await engine.healthcheck()
    if health:
        logger.info("✅ Все плагины здоровы")
    else:
        logger.info("⚠️ Некоторые плагины работают в ограниченном режиме")
    
    return engine


if __name__ == "__main__":
    asyncio.run(demo()) 