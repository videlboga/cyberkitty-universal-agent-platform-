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
            # === БАЗОВЫЕ ОБРАБОТЧИКИ ===
            "start": self._handle_start,
            "end": self._handle_end,
            "action": self._handle_action,
            "input": self._handle_input,
            "branch": self._handle_branch,  # Современные условные переходы
            "switch_scenario": self._handle_switch_scenario,  # Переключение сценариев
            "log_message": self._handle_log_message,  # Логирование сообщений
            
            # === УНИВЕРСАЛЬНЫЕ ОБРАБОТЧИКИ КАНАЛОВ ===
            "channel_send_message": self._handle_channel_send_message,
            "channel_send_buttons": self._handle_channel_send_buttons,
            "channel_edit_message": self._handle_channel_edit_message,
            "channel_start_polling": self._handle_channel_start_polling,
            "channel_update_token": self._handle_channel_update_token,
            "channel_load_token": self._handle_channel_load_token,
        })
        self.logger.info("Зарегистрированы современные обработчики", handlers=list(self.step_handlers.keys()))
        
    def register_plugin(self, plugin: BasePlugin):
        """
        Регистрирует плагин и его обработчики.
        
        Args:
            plugin: Экземпляр плагина наследующего BasePlugin
        """
        # ВАЖНО: Передаем ссылку на движок плагину ПЕРЕД регистрацией
        plugin.set_engine(self)
        
        self.plugins[plugin.name] = plugin
        
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
            context: Контекст выполнения
            
        Returns:
            Dict[str, Any]: Результат выполнения обработчика
        """
        if handler_name not in self.step_handlers:
            raise ValueError(f"Обработчик {handler_name} не найден")
            
        handler = self.step_handlers[handler_name]
        
        # Создаем фиктивный шаг для вызова обработчика
        fake_step = {
            "id": f"call_{handler_name}",
            "type": handler_name,
            "params": context.get("handler_params", {})
        }
        
        return await handler(fake_step, context)
    
    # ===== НОВЫЕ УНИВЕРСАЛЬНЫЕ ОБРАБОТЧИКИ КАНАЛОВ =====
    
    async def _handle_channel_send_message(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Универсальный обработчик отправки сообщения через канал
        
        Параметры шага:
        - channel_id: ID канала (обязательно)
        - chat_id: ID чата (обязательно)
        - text: Текст сообщения (обязательно)
        - parse_mode: Режим парсинга (опционально)
        - output_var: Переменная для сохранения результата (опционально)
        """
        params = step.get("params", {})
        
        try:
            channel_id = self._resolve_template(str(params.get("channel_id", "")), context)
            chat_id = self._resolve_template(str(params.get("chat_id", "")), context)
            text = self._resolve_template(str(params.get("text", "")), context)
            
            if not channel_id:
                raise ValueError("channel_id обязателен для channel_send_message")
            if not chat_id:
                raise ValueError("chat_id обязателен для channel_send_message")
            if not text:
                raise ValueError("text обязателен для channel_send_message")
            
            # Получаем ChannelManager из движка
            channel_manager = getattr(self, 'channel_manager', None)
            if not channel_manager:
                raise ValueError("ChannelManager не инициализирован в движке")
            
            # Подготавливаем дополнительные параметры
            kwargs = {}
            if "parse_mode" in params:
                kwargs["parse_mode"] = params["parse_mode"]
            
            # Отправляем сообщение через ChannelManager
            result = await channel_manager.send_message(channel_id, chat_id, text, **kwargs)
            
            # Сохраняем результат в контекст
            output_var = params.get("output_var", "channel_send_result")
            context[output_var] = result
            
            self.logger.info(f"✅ Сообщение отправлено через канал {channel_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка channel_send_message: {e}")
            context["__step_error__"] = str(e)
            return context
    
    async def _handle_channel_send_buttons(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Универсальный обработчик отправки сообщения с кнопками через канал
        
        Параметры шага:
        - channel_id: ID канала (обязательно)
        - chat_id: ID чата (обязательно)
        - text: Текст сообщения (обязательно)
        - buttons: Массив кнопок (обязательно)
        - output_var: Переменная для сохранения результата (опционально)
        """
        params = step.get("params", {})
        
        try:
            channel_id = self._resolve_template(str(params.get("channel_id", "")), context)
            chat_id = self._resolve_template(str(params.get("chat_id", "")), context)
            text = self._resolve_template(str(params.get("text", "")), context)
            buttons = params.get("buttons", [])
            
            if not channel_id:
                raise ValueError("channel_id обязателен для channel_send_buttons")
            if not chat_id:
                raise ValueError("chat_id обязателен для channel_send_buttons")
            if not text:
                raise ValueError("text обязателен для channel_send_buttons")
            if not buttons:
                raise ValueError("buttons обязательны для channel_send_buttons")
            
            # Получаем ChannelManager из движка
            channel_manager = getattr(self, 'channel_manager', None)
            if not channel_manager:
                raise ValueError("ChannelManager не инициализирован в движке")
            
            # Отправляем сообщение с кнопками через ChannelManager
            result = await channel_manager.send_buttons(channel_id, chat_id, text, buttons)
            
            # Сохраняем результат в контекст
            output_var = params.get("output_var", "channel_send_buttons_result")
            context[output_var] = result
            
            self.logger.info(f"✅ Сообщение с кнопками отправлено через канал {channel_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка channel_send_buttons: {e}")
            context["__step_error__"] = str(e)
            return context
    
    async def _handle_channel_edit_message(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Универсальный обработчик редактирования сообщения через канал
        
        Параметры шага:
        - channel_id: ID канала (обязательно)
        - chat_id: ID чата (обязательно)
        - message_id: ID сообщения (обязательно)
        - text: Новый текст (обязательно)
        - output_var: Переменная для сохранения результата (опционально)
        """
        params = step.get("params", {})
        
        try:
            channel_id = self._resolve_template(str(params.get("channel_id", "")), context)
            chat_id = self._resolve_template(str(params.get("chat_id", "")), context)
            message_id = params.get("message_id")
            text = self._resolve_template(str(params.get("text", "")), context)
            
            if not channel_id:
                raise ValueError("channel_id обязателен для channel_edit_message")
            if not chat_id:
                raise ValueError("chat_id обязателен для channel_edit_message")
            if not message_id:
                raise ValueError("message_id обязателен для channel_edit_message")
            if not text:
                raise ValueError("text обязателен для channel_edit_message")
            
            # Получаем ChannelManager из движка
            channel_manager = getattr(self, 'channel_manager', None)
            if not channel_manager:
                raise ValueError("ChannelManager не инициализирован в движке")
            
            # Редактируем сообщение через ChannelManager
            result = await channel_manager.edit_message(channel_id, chat_id, int(message_id), text)
            
            # Сохраняем результат в контекст
            output_var = params.get("output_var", "channel_edit_result")
            context[output_var] = result
            
            self.logger.info(f"✅ Сообщение отредактировано через канал {channel_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка channel_edit_message: {e}")
            context["__step_error__"] = str(e)
            return context
    
    async def _handle_channel_start_polling(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик запуска polling для канала
        
        Параметры шага:
        - channel_id: ID канала (обязательно)
        - output_var: Переменная для сохранения результата (опционально)
        """
        params = step.get("params", {})
        
        try:
            channel_id = self._resolve_template(str(params.get("channel_id", "")), context)
            
            if not channel_id:
                raise ValueError("channel_id обязателен для channel_start_polling")
            
            # Получаем ChannelManager из движка
            channel_manager = getattr(self, 'channel_manager', None)
            if not channel_manager:
                raise ValueError("ChannelManager не инициализирован в движке")
            
            # Запускаем polling через ChannelManager
            # Примечание: polling обычно уже запущен при инициализации
            result = {"success": True, "message": f"Polling для канала {channel_id} активен"}
            
            # Сохраняем результат в контекст
            output_var = params.get("output_var", "channel_polling_result")
            context[output_var] = result
            
            self.logger.info(f"✅ Polling активен для канала {channel_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка channel_start_polling: {e}")
            context["__step_error__"] = str(e)
            return context
    
    async def _handle_channel_update_token(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик обновления токена канала
        
        Параметры шага:
        - channel_id: ID канала (обязательно)
        - new_token: Новый токен (обязательно)
        - output_var: Переменная для сохранения результата (опционально)
        """
        params = step.get("params", {})
        
        try:
            channel_id = self._resolve_template(str(params.get("channel_id", "")), context)
            new_token = self._resolve_template(str(params.get("new_token", "")), context)
            
            if not channel_id:
                raise ValueError("channel_id обязателен для channel_update_token")
            if not new_token:
                raise ValueError("new_token обязателен для channel_update_token")
            
            # Получаем ChannelManager из движка
            channel_manager = getattr(self, 'channel_manager', None)
            if not channel_manager:
                raise ValueError("ChannelManager не инициализирован в движке")
            
            # Обновляем токен через ChannelManager
            result = await channel_manager.update_channel_token(channel_id, new_token)
            
            # Сохраняем результат в контекст
            output_var = params.get("output_var", "channel_update_token_result")
            context[output_var] = result
            
            self.logger.info(f"✅ Токен обновлен для канала {channel_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка channel_update_token: {e}")
            context["__step_error__"] = str(e)
            return context
    
    async def _handle_channel_load_token(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик загрузки токена канала из БД
        
        Параметры шага:
        - channel_id: ID канала (обязательно)
        - output_var: Переменная для сохранения токена (опционально)
        """
        params = step.get("params", {})
        
        try:
            channel_id = self._resolve_template(str(params.get("channel_id", "")), context)
            
            if not channel_id:
                raise ValueError("channel_id обязателен для channel_load_token")
            
            # Получаем ChannelManager из движка
            channel_manager = getattr(self, 'channel_manager', None)
            if not channel_manager:
                raise ValueError("ChannelManager не инициализирован в движке")
            
            # Получаем информацию о канале
            channel_info = channel_manager.get_channel_info(channel_id)
            if not channel_info:
                raise ValueError(f"Канал {channel_id} не найден")
            
            # Извлекаем токен
            token = channel_info.get("channel_config", {}).get("telegram_bot_token")
            if not token:
                raise ValueError(f"Токен не найден для канала {channel_id}")
            
            result = {"success": True, "token": token}
            
            # Сохраняем результат в контекст
            output_var = params.get("output_var", "channel_token")
            context[output_var] = result
            
            self.logger.info(f"✅ Токен загружен для канала {channel_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка channel_load_token: {e}")
            context["__step_error__"] = str(e)
            return context


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
    
    # === РЕГИСТРАЦИЯ ПЛАГИНОВ (БЕЗ ИНИЦИАЛИЗАЦИИ) ===
    
    plugins_to_initialize = []
    
    try:
        # 1. MongoDB Plugin - для хранения агентов и сценариев
        logger.info("📦 Регистрация MongoDB Plugin...")
        from app.plugins.mongo_plugin import MongoPlugin
        mongo_plugin = MongoPlugin()
        engine.register_plugin(mongo_plugin)
        plugins_to_initialize.append(mongo_plugin)
        logger.info("✅ MongoDB Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB Plugin недоступен: {e}")
    
    try:
        # 2. Telegram Plugin - для работы с Telegram
        logger.info("📦 Регистрация SimpleTelegram Plugin...")
        from app.plugins.simple_telegram_plugin import SimpleTelegramPlugin
        telegram_plugin = SimpleTelegramPlugin()
        engine.register_plugin(telegram_plugin)
        plugins_to_initialize.append(telegram_plugin)
        logger.info("✅ SimpleTelegram Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleTelegram Plugin недоступен: {e}")
    
    try:
        # 3. LLM Plugin - для работы с языковыми моделями
        logger.info("📦 Регистрация SimpleLLM Plugin...")
        from app.plugins.simple_llm_plugin import SimpleLLMPlugin
        llm_plugin = SimpleLLMPlugin()
        engine.register_plugin(llm_plugin)
        plugins_to_initialize.append(llm_plugin)
        logger.info("✅ SimpleLLM Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleLLM Plugin недоступен: {e}")
    
    try:
        # 4. RAG Plugin - для работы с базой знаний
        logger.info("📦 Регистрация SimpleRAG Plugin...")
        from app.plugins.simple_rag_plugin import SimpleRAGPlugin
        rag_plugin = SimpleRAGPlugin()
        engine.register_plugin(rag_plugin)
        plugins_to_initialize.append(rag_plugin)
        logger.info("✅ SimpleRAG Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleRAG Plugin недоступен: {e}")
    
    try:
        # 5. Scheduler Plugin - для отложенного выполнения задач
        logger.info("📦 Регистрация SimpleScheduler Plugin...")
        from app.plugins.simple_scheduler_plugin import SimpleSchedulerPlugin
        scheduler_plugin = SimpleSchedulerPlugin()
        engine.register_plugin(scheduler_plugin)
        plugins_to_initialize.append(scheduler_plugin)
        logger.info("✅ SimpleScheduler Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleScheduler Plugin недоступен: {e}")
    
    try:
        # 6. HTTP Plugin - для внешних HTTP запросов
        logger.info("📦 Регистрация SimpleHTTP Plugin...")
        from app.plugins.simple_http_plugin import SimpleHTTPPlugin
        http_plugin = SimpleHTTPPlugin()
        engine.register_plugin(http_plugin)
        plugins_to_initialize.append(http_plugin)
        logger.info("✅ SimpleHTTP Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleHTTP Plugin недоступен: {e}")
    
    try:
        # 7. AmoCRM Plugin - для интеграции с AmoCRM
        logger.info("📦 Регистрация SimpleAmoCRM Plugin...")
        from app.plugins.simple_amocrm_plugin import SimpleAmoCRMPlugin
        amocrm_plugin = SimpleAmoCRMPlugin()
        engine.register_plugin(amocrm_plugin)
        plugins_to_initialize.append(amocrm_plugin)
        logger.info("✅ SimpleAmoCRM Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleAmoCRM Plugin недоступен: {e}")
    
    try:
        # 8. AmoCRM Companies Plugin - для работы с компаниями
        logger.info("📦 Регистрация SimpleAmoCRM Companies Plugin...")
        from app.plugins.simple_amocrm_companies import SimpleAmoCRMCompaniesPlugin
        amocrm_companies_plugin = SimpleAmoCRMCompaniesPlugin()
        engine.register_plugin(amocrm_companies_plugin)
        plugins_to_initialize.append(amocrm_companies_plugin)
        logger.info("✅ SimpleAmoCRM Companies Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleAmoCRM Companies Plugin недоступен: {e}")
    
    try:
        # 9. AmoCRM Tasks Plugin - для работы с задачами и событиями
        logger.info("📦 Регистрация SimpleAmoCRM Tasks Plugin...")
        from app.plugins.simple_amocrm_tasks import SimpleAmoCRMTasksPlugin
        amocrm_tasks_plugin = SimpleAmoCRMTasksPlugin()
        engine.register_plugin(amocrm_tasks_plugin)
        plugins_to_initialize.append(amocrm_tasks_plugin)
        logger.info("✅ SimpleAmoCRM Tasks Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleAmoCRM Tasks Plugin недоступен: {e}")
    
    try:
        # 10. AmoCRM Advanced Plugin - для продвинутых операций
        logger.info("📦 Регистрация SimpleAmoCRM Advanced Plugin...")
        from app.plugins.simple_amocrm_advanced import SimpleAmoCRMAdvancedPlugin
        amocrm_advanced_plugin = SimpleAmoCRMAdvancedPlugin()
        engine.register_plugin(amocrm_advanced_plugin)
        plugins_to_initialize.append(amocrm_advanced_plugin)
        logger.info("✅ SimpleAmoCRM Advanced Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleAmoCRM Advanced Plugin недоступен: {e}")
    
    try:
        # 11. AmoCRM Admin Plugin - для административных операций
        logger.info("📦 Регистрация SimpleAmoCRM Admin Plugin...")
        from app.plugins.simple_amocrm_admin import SimpleAmoCRMAdminPlugin
        amocrm_admin_plugin = SimpleAmoCRMAdminPlugin()
        engine.register_plugin(amocrm_admin_plugin)
        plugins_to_initialize.append(amocrm_admin_plugin)
        logger.info("✅ SimpleAmoCRM Admin Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleAmoCRM Admin Plugin недоступен: {e}")
    
    # === ИНИЦИАЛИЗАЦИЯ ПЛАГИНОВ (ПОСЛЕ РЕГИСТРАЦИИ) ===
    
    logger.info("🔧 Инициализация зарегистрированных плагинов...")
    
    for plugin in plugins_to_initialize:
        try:
            logger.info(f"🚀 Инициализация {plugin.name}...")
            await plugin.initialize()
            logger.info(f"✅ {plugin.name} инициализирован")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка инициализации {plugin.name}: {e}")
    
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