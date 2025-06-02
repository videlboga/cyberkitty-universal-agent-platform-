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
from .yaml_scenario_loader import yaml_loader
from app.core.template_resolver import template_resolver

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
            "input_text": self._handle_input_text,
            "input_button": self._handle_input_button,
            "input": self._handle_input,
            "branch": self._handle_branch,
            "conditional_execute": self._handle_conditional_execute,
            "switch_scenario": self._handle_switch_scenario,
            "log_message": self._handle_log_message,
            
            # === TELEGRAM ИНТЕГРАЦИЯ ===
            "channel_action": self._handle_channel_action,
            "extract_telegram_context": self._handle_extract_telegram_context,
            
            # === ВАЛИДАЦИЯ И УТИЛИТЫ ===
            "validate_field": self._handle_validate_field,
            "increment": self._handle_increment,
            "save_to_object": self._handle_save_to_object,
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
            "execution_started": True
        }
        
        # ИСПРАВЛЕНИЕ: НЕ перезаписываем current_step если он уже есть!
        if "current_step" not in execution_context or execution_context["current_step"] is None:
            execution_context["current_step"] = None
        
        try:
            # УЛУЧШЕННАЯ ЛОГИКА: Ищем первый шаг или продолжаем с конкретного
            if execution_context.get("current_step"):
                # Продолжаем с указанного шага
                target_step_id = execution_context["current_step"]
                current_step = None
                for step in steps:
                    if step.get("id") == target_step_id:
                        current_step = step
                        break
                        
                if not current_step:
                    self.logger.warning(f"⚠️ Не найден шаг {target_step_id}, начинаю с первого")
                    current_step = self._find_first_step(steps)
                else:
                    self.logger.info(f"📍 Продолжаю выполнение с шага: {target_step_id}")
            else:
                # Ищем первый шаг (обычно type="start")
                current_step = self._find_first_step(steps)
            
            if not current_step:
                raise ValueError(f"Не найден первый шаг в сценарии {scenario_id}")
                
            # Выполняем шаги последовательно
            while current_step:
                execution_context["current_step"] = current_step.get("id")
                
                try:
                    # Выполняем текущий шаг
                    step_result = await self.execute_step(current_step, execution_context)
                    
                    # Обновляем контекст результатом
                    execution_context.update(step_result)
                    
                    # ПРОВЕРЯЕМ ПЕРЕКЛЮЧЕНИЕ СЦЕНАРИЯ
                    if execution_context.get("scenario_switched"):
                        new_scenario_id = execution_context.get("switched_to")
                        if new_scenario_id and new_scenario_id != scenario_id:
                            self.logger.info(f"🔄 Переключаюсь с {scenario_id} на {new_scenario_id}")
                            
                            try:
                                # Рекурсивно выполняем новый сценарий
                                return await self.execute_scenario(new_scenario_id, execution_context)
                            except StopExecution as stop_e:
                                # Новый сценарий ожидает ввод - это нормально!
                                self.logger.info(f"⏱️ Переключенный сценарий ожидает ввод: {stop_e}")
                                execution_context["execution_stopped"] = True
                                execution_context["stop_reason"] = str(stop_e)
                                execution_context["waiting_for_input"] = True
                                return execution_context
                    
                    # Находим следующий шаг
                    current_step = self._find_next_step(steps, current_step, execution_context)
                    
                except StopExecution as e:
                    # НОРМАЛЬНОЕ ожидание ввода - НЕ ошибка!
                    self.logger.info(f"⏱️ Выполнение остановлено для ожидания ввода: {e}")
                    execution_context["execution_stopped"] = True
                    execution_context["stop_reason"] = str(e)
                    execution_context["waiting_for_input"] = True
                    return execution_context
            
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
            
        # === УНИВЕРСАЛЬНАЯ ПОДСТАНОВКА ПАРАМЕТРОВ ===
        # Создаем копию шага с разрешенными параметрами
        resolved_step = step.copy()
        if "params" in resolved_step:
            original_params = resolved_step["params"]
            
            # МАКСИМАЛЬНО ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ
            logger.info(f"🔍 НАЧИНАЮ ПОДСТАНОВКУ для шага {step_id} (тип: {step_type})")
            logger.info(f"🔍 original_params: {original_params}")
            logger.info(f"🔍 template_resolver объект: {template_resolver}")
            logger.info(f"🔍 контекст ключи: {list(context.keys())}")
            
            # СПЕЦИАЛЬНОЕ ЛОГИРОВАНИЕ для contact переменной
            contact_value = context.get('contact')
            if contact_value:
                logger.info(f"🔍 CONTACT В КОНТЕКСТЕ: {contact_value}")
            else:
                logger.info(f"🔍 CONTACT НЕ НАЙДЕН В КОНТЕКСТЕ!")
            
            try:
                resolved_step["params"] = template_resolver.resolve_deep(resolved_step["params"], context)
                logger.info(f"🔍 resolve_deep ВЫПОЛНЕН успешно")
                logger.info(f"🔍 resolved_params: {resolved_step['params']}")
            except Exception as e:
                logger.error(f"🚨 ОШИБКА в resolve_deep: {e}")
                logger.error(f"🚨 Тип ошибки: {type(e).__name__}")
                import traceback
                logger.error(f"🚨 Stack trace: {traceback.format_exc()}")
            
            # ОТЛАДОЧНОЕ ЛОГИРОВАНИЕ для диагностики подстановки переменных  
            # ВРЕМЕННО: логируем ВСЕ шаги для диагностики
            if original_params != resolved_step['params']:
                logger.info(f"🔍 ОТЛАДКА подстановки переменных в шаге {step_id} (тип: {step_type}):")
                logger.info(f"   До:     {original_params}")
                logger.info(f"   После:  {resolved_step['params']}")
                logger.info(f"   Контекст доступен: telegram_first_name={context.get('telegram_first_name')}, contact.phone_number={context.get('contact', {}).get('phone_number')}")
                logger.info(f"   ПОЛНЫЙ КОНТЕКСТ CONTACT: {context.get('contact')}")
                logger.info(f"   ВСЕ КЛЮЧИ КОНТЕКСТА: {list(context.keys())}")
                logger.info(f"   💾 ЕСТЬ ЛИ contact В КОРНЕ? {'contact' in context}")
                logger.info(f"   💾 ТИП context: {type(context)}")
                logger.info(f"   💾 LEN context: {len(context)}")
                # Проверим каждый ключ содержащий contact
                contact_related_keys = [k for k in context.keys() if 'contact' in str(k).lower()]
                logger.info(f"   💾 КЛЮЧИ С contact: {contact_related_keys}")
                logger.info(f"   Равны:  {original_params == resolved_step['params']}")
            else:
                logger.info(f"🔍 Параметры НЕ ИЗМЕНИЛИСЬ в шаге {step_id}")
            
        self.logger.debug(
            f"Параметры шага {step_id} после подстановки",
            original_params=step.get("params", {}),
            resolved_params=resolved_step.get("params", {})
        )
            
        handler = self.step_handlers[step_type]
        
        try:
            # Выполняем обработчик с разрешенными параметрами
            result = await handler(resolved_step, context)
            
            self.logger.info(
                f"Шаг {step_id} выполнен успешно",
                step_id=step_id,
                step_type=step_type
            )
            
            return result if result else context
            
        except StopExecution as e:
            # СПЕЦИАЛЬНАЯ обработка ожидания ввода - НЕ ошибка!
            self.logger.info(
                f"⏱️ Шаг {step_id} остановлен для ожидания ввода: {e}",
                step_id=step_id,
                step_type=step_type
            )
            # Пробрасываем StopExecution дальше для обработки в execute_scenario
            raise
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
        
        # Очищаем данные ввода в конце сценария
        context.pop("callback_data", None)
        context.pop("user_input", None)
        context.pop("waiting_for_input", None)
        context.pop("input_step_id", None)
        self.logger.info("🧹 Очистил данные ввода в конце сценария")
        
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
        
    async def _handle_input_text(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага 'input_text' - ожидание ТЕКСТОВОГО ввода пользователя.
        
        КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Сначала проверяем данные, потом очищаем!
        """
        self.logger.info("Обрабатываю шаг input_text (только текст)", step_id=step.get("id"))
        
        params = step.get("params", {})
        variable = params.get("variable")  # Переменная для сохранения ввода
        current_step_id = step.get("id")
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Сначала ищем текстовые данные БЕЗ очистки
        text_input = None
        
        # Проверяем user_input (приоритет)
        if context.get("user_input") and not context["user_input"].startswith("/"):
            text_input = context["user_input"]
            self.logger.info(f"✅ Найден user_input: {text_input}")
        
        # Проверяем message_text (если нет user_input)
        elif (context.get("message_text") and 
              not context["message_text"].startswith("/") and
              context["message_text"] != "/start"):
            text_input = context["message_text"]
            self.logger.info(f"✅ Найден message_text: {text_input}")
        
        if text_input:
            # ЕСТЬ ТЕКСТОВЫЕ ДАННЫЕ - обрабатываем
            # Сохраняем текст в переменную
            if variable:
                context[variable] = text_input
                self.logger.info(f"💾 Сохранил текст в {variable}: {text_input}")
            
            # Теперь очищаем использованные данные
            context.pop("user_input", None)
            context.pop("message_text", None)
            context["waiting_for_input"] = False
            context.pop("input_step_id", None)
            
            self.logger.info(f"✅ input_text шаг {current_step_id} завершен с текстом: {text_input}")
            return context
        else:
            # НЕТ ТЕКСТОВЫХ ДАННЫХ - ждём ввода
            # Очищаем старые данные только если это ДРУГОЙ шаг
            current_input_step = context.get("input_step_id")
            if current_input_step and current_input_step != current_step_id:
                self.logger.info(f"🧹 Переключение с шага {current_input_step} на {current_step_id} - очищаю старые данные")
                context.pop("user_input", None)
                context.pop("callback_data", None)
                context.pop("message_text", None)
            
            self.logger.info(f"⏱️ input_text ждёт текстовый ввод на шаге {current_step_id}")
            
            context["waiting_for_input"] = True
            context["input_step_id"] = current_step_id
            
            raise StopExecution(f"Ожидание текстового ввода на шаге {current_step_id}")
        
    async def _handle_input_button(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага 'input_button' - ожидание нажатия кнопки (callback_query).
        """
        self.logger.info("Обрабатываю шаг input_button (только кнопки)", step_id=step.get("id"))
        
        params = step.get("params", {})
        variable = params.get("variable")  # Переменная для сохранения ввода
        
        # 🔍 ОТЛАДОЧНОЕ ЛОГИРОВАНИЕ КОНТЕКСТА
        self.logger.info(f"🔍 ПОЛНЫЙ КОНТЕКСТ input_button: {context}")
        self.logger.info(f"🔍 CALLBACK_DATA в контексте: {context.get('callback_data')}")
        self.logger.info(f"🔍 EVENT_TYPE в контексте: {context.get('event_type')}")
        
        # ИСПРАВЛЕНО: Не очищаем данные если у нас уже есть callback_data для этого шага
        current_input_step = context.get("input_step_id")
        step_id = step.get("id")
        has_callback_data = context.get("callback_data")
        
        # Очищаем старые данные ТОЛЬКО если это действительно новый шаг И нет актуальных данных
        if current_input_step != step_id and not has_callback_data:
            self.logger.info(f"🧹 Новый input_button шаг - очищаю данные")
            context.pop("user_input", None)
            context.pop("callback_data", None)
            context.pop("message_text", None)
        
        # Ищем ТОЛЬКО callback_data
        button_data = context.get("callback_data")
        
        if button_data:
            # Сохраняем данные кнопки в переменную
            if variable:
                context[variable] = button_data
                self.logger.info(f"💾 Сохранил callback_data в {variable}: {button_data}")
            
            # Очищаем использованные данные
            context.pop("callback_data", None)
            context["waiting_for_input"] = False
            context.pop("input_step_id", None)
            
            self.logger.info(f"✅ input_button шаг {step_id} завершен с кнопкой: {button_data}")
            return context
        else:
            # Нет данных кнопки - ждём
            self.logger.info(f"⏱️ input_button ждёт нажатие кнопки на шаге {step_id}")
            
            context["waiting_for_input"] = True
            context["input_step_id"] = step_id
            
            raise StopExecution(f"Ожидание нажатия кнопки на шаге {step_id}")
        
    async def _handle_input(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага 'input' - ожидание ввода пользователя.
        
        КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Проверка данных ДО их очистки!
        """
        self.logger.info("Обрабатываю шаг input", step_id=step.get("id"))
        
        params = step.get("params", {})
        waiting_for = params.get("waiting_for", "any")
        expected_values = params.get("expected_values", [])  # для валидации callback
        variable = params.get("variable")  # Переменная для сохранения ввода
        
        # 🔍 ОТЛАДОЧНОЕ ЛОГИРОВАНИЕ КОНТЕКСТА
        self.logger.info(f"🔍 ПОЛНЫЙ КОНТЕКСТ: {context}")
        self.logger.info(f"🔍 WAITING_FOR: {waiting_for}")
        self.logger.info(f"🔍 EXPECTED_VALUES: {expected_values}")
        self.logger.info(f"🔍 CALLBACK_DATA в контексте: {context.get('callback_data')}")
        self.logger.info(f"🔍 EVENT_TYPE в контексте: {context.get('event_type')}")
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: СНАЧАЛА проверяем есть ли актуальные данные для этого шага
        has_callback = "callback_data" in context and context["callback_data"]
        has_message = "user_input" in context and context["user_input"]
        # ИСПРАВЛЕНИЕ: /start НЕ является валидным вводом для input шагов
        has_text = ("message_text" in context and context["message_text"] and 
                   context["message_text"] != "/start" and 
                   not context["message_text"].startswith("/"))
        has_contact = "contact" in context and context["contact"]
        
        input_available = False
        input_value = None
        
        if waiting_for == "callback_query" and has_callback:
            callback_value = context["callback_data"]
            # Проверяем expected_values если указаны
            if expected_values and callback_value not in expected_values:
                self.logger.info(f"⚠️ Callback {callback_value} не в списке ожидаемых {expected_values}")
                # Если callback не подходит, продолжаем ожидание
            else:
                input_available = True
                input_value = callback_value
                self.logger.info(f"✅ Callback данные доступны: {input_value}")
        elif waiting_for == "contact" and has_contact:
            input_available = True
            input_value = context["contact"]
            self.logger.info(f"✅ Контакт доступен: {input_value}")
        elif waiting_for == "text" and (has_message or has_text):
            input_available = True
            input_value = context.get("user_input") or context.get("message_text")
            self.logger.info(f"✅ Текстовые данные доступны: {input_value}")
        elif waiting_for == "message" and (has_message or has_text):
            input_available = True
            input_value = context.get("user_input") or context.get("message_text")
            self.logger.info(f"✅ Текстовые данные доступны: {input_value}")
        elif waiting_for == "any" and (has_callback or has_message or has_text or has_contact):
            input_available = True
            input_value = context.get("callback_data") or context.get("user_input") or context.get("message_text") or context.get("contact")
            self.logger.info(f"✅ Входные данные доступны: {input_value}")
        
        if input_available and input_value and (not isinstance(input_value, str) or not input_value.startswith("/")):
            # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: команды не являются валидным вводом (только для строк)
            # Сохраняем ввод в указанную переменную
            if variable:
                context[variable] = input_value
                self.logger.info(f"💾 Сохранил ввод в переменную {variable}: {input_value}")
            
            # ИСПРАВЛЕНИЕ: НЕ удаляем callback_data сразу - он может понадобиться для branch шагов
            # Очищаем только некритичные данные ввода
            context.pop("user_input", None)
            # НЕ удаляем callback_data! context.pop("callback_data", None) 
            
            # КРИТИЧНО: ВСЕГДА сохраняем contact данные если они есть!
            # ОТЛАДОЧНОЕ ЛОГИРОВАНИЕ
            self.logger.info(f"🔍 WAITING_FOR ПАРАМЕТР: {waiting_for}")
            self.logger.info(f"🔍 INPUT_VALUE ТИП: {type(input_value)}")
            self.logger.info(f"🔍 INPUT_VALUE: {input_value}")
            
            if waiting_for == "contact" and isinstance(input_value, dict) and "contact" in context:
                # Сохраняем contact в корневом контексте для доступа через {contact.phone_number}
                contact_data = context["contact"]
                # НЕ удаляем! context.pop("contact", None)
                self.logger.info(f"💾 УСЛОВИЕ waiting_for=contact ВЫПОЛНЕНО - сохраняю contact: {contact_data}")
            elif isinstance(input_value, dict) and input_value.get("phone_number"):
                # ИСПРАВЛЕНИЕ: Если input_value сам является контактом, сохраняем его как contact
                context["contact"] = input_value
                self.logger.info(f"💾 СОХРАНЯЮ input_value как contact: {input_value}")
            
            if context.get("message_text") != "/start":
                context.pop("message_text", None)
            
            context["waiting_for_input"] = False
            context.pop("input_step_id", None)
            
            self.logger.info(f"✅ Input шаг {step.get('id')} завершен с вводом: {input_value}")
            self.logger.info(f"🔍 callback_data сохранён для последующих шагов: {context.get('callback_data')}")
            if "contact" in context:
                self.logger.info(f"🔍 contact сохранён в контексте: {context.get('contact')}")
            else:
                self.logger.info(f"🚨 contact НЕ НАЙДЕН в контексте после обработки!")
            return context
        else:
            # Данных нет - очищаем старые данные ТОЛЬКО если это новый input шаг
            current_input_step = context.get("input_step_id")
            if current_input_step != step.get("id"):
                # Это новый input шаг - очищаем старые данные
                self.logger.info(f"🧹 Очищаю старые данные ввода для нового шага {step.get('id')}")
                context.pop("user_input", None)
                # НЕ удаляем callback_data! context.pop("callback_data", None)
                context.pop("contact", None)
                # ИСПРАВЛЕНИЕ: /start НЕ является валидным вводом для input шагов
                if context.get("message_text") != "/start":
                    context.pop("message_text", None)
            
            # Останавливаем выполнение для ожидания ввода
            self.logger.info(f"⏱️ Останавливаю выполнение - ожидание ввода на шаге {step.get('id')}")
            self.logger.info(f"🔍 Доступные данные: callback={has_callback}, message={has_message}, text={has_text}, contact={has_contact}")
            
            context["waiting_for_input"] = True
            context["input_step_id"] = step.get("id")
            
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
        default_next_step_id = params.get("default_next_step")
        
        # 🔍 ОТЛАДОЧНОЕ ЛОГИРОВАНИЕ ВСЕГО МАССИВА
        self.logger.info(f"🔍 ВЕСЬ МАССИВ CONDITIONS: {conditions}")
        self.logger.info(f"🔍 КОЛИЧЕСТВО CONDITIONS: {len(conditions)}")
        self.logger.info(f"🔍 DEFAULT_NEXT_STEP: {default_next_step_id}")
        
        # Проверяем условия по порядку
        for condition_data in conditions:
            condition = condition_data.get("condition", "")
            next_step_id = condition_data.get("next_step")
            
            # 🔍 ОТЛАДОЧНОЕ ЛОГИРОВАНИЕ
            self.logger.info(f"🔍 УСЛОВИЕ: {condition}")
            self.logger.info(f"🔍 NEXT_STEP: {next_step_id}")
            self.logger.info(f"🔍 RAW_CONDITION_DATA: {condition_data}")
            
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
            condition: Условие для оценки (например: "callback_data == 'value'" или "context.counter > 10")
            context: Контекст выполнения
            
        Returns:
            bool: Результат оценки условия
        """
        if not condition:
            return False
        
        try:
            # ОТЛАДКА: Логируем исходные данные
            self.logger.info(f"🔍 EVALUATE CONDITION: {condition}")
            self.logger.info(f"🔍 CONTEXT KEYS: {list(context.keys())}")
            if "callback_data" in context:
                self.logger.info(f"🔍 CALLBACK_DATA VALUE: {context['callback_data']}")
            
            # Заменяем переменные на значения из контекста
            resolved_condition = condition
            
            # 1. Сначала заменяем context.field на значения
            import re
            context_refs = re.findall(r'context\\.(\w+)', condition)
            for field in context_refs:
                if field in context:
                    value = context[field]
                    if isinstance(value, str):
                        resolved_condition = resolved_condition.replace(f'context.{field}', f"'{value}'")
                    else:
                        resolved_condition = resolved_condition.replace(f'context.{field}', str(value))
            
            # 2. ИСПРАВЛЕНИЕ: Заменяем простые переменные (например callback_data, user_input)
            # Находим все простые идентификаторы (не context.field)
            simple_vars = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', resolved_condition)
            self.logger.info(f"🔍 SIMPLE VARS FOUND: {simple_vars}")
            
            for var in simple_vars:
                # Пропускаем служебные слова Python
                if var in ['True', 'False', 'None', 'and', 'or', 'not', 'in', 'is']:
                    continue
                    
                # Заменяем на значение из контекста
                if var in context:
                    value = context[var]
                    self.logger.info(f"🔍 REPLACING {var} WITH {repr(value)}")
                    if isinstance(value, str):
                        # Используем repr для корректного экранирования кавычек
                        resolved_condition = re.sub(rf'\b{var}\b', repr(value), resolved_condition)
                    else:
                        resolved_condition = re.sub(rf'\b{var}\b', str(value), resolved_condition)
                else:
                    self.logger.warning(f"🔍 VARIABLE {var} NOT FOUND IN CONTEXT")
            
            self.logger.info(f"🔍 RESOLVED CONDITION: {resolved_condition}")
            
            # ИСПРАВЛЕНИЕ: Выполняем условие БЕЗ дополнительных переменных
            # Все переменные уже заменены на литеральные значения
            result = eval(resolved_condition, {"__builtins__": {}}, {})
            self.logger.debug(f"Условие '{condition}' -> '{resolved_condition}' -> {result}")
            self.logger.info(f"🔍 CONDITION RESULT: {result}")
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Ошибка оценки условия '{condition}': {e}")
            return False
    
    async def _handle_switch_scenario(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик переключения сценариев.
        
        ИСПРАВЛЕНО: Реально выполняет новый сценарий!
        """
        self.logger.info("Обрабатываю переключение сценария", step_id=step.get("id"))
        
        resolved_scenario_id = None
        
        try:
            params = step.get("params", {})
            scenario_id = params.get("scenario_id")
            preserve_context = params.get("preserve_context", True)
            context_mapping = params.get("context_mapping", {})
            
            if not scenario_id:
                raise ValueError("Не указан scenario_id для переключения")
            
            # Подставляем переменные в scenario_id
            resolved_scenario_id = self._resolve_template(scenario_id, context)
            
            self.logger.info(f"🔄 Переключаю на сценарий: {resolved_scenario_id}")
            
            # Подготавливаем контекст для нового сценария
            if preserve_context:
                # СОХРАНЯЕМ ВЕСЬ КОНТЕКСТ
                new_context = context.copy()
                
                # КРИТИЧНО: Очищаем старые данные ввода при переключении сценария
                new_context.pop("user_input", None)
                new_context.pop("callback_data", None)
                new_context.pop("waiting_for_input", None)
                new_context.pop("input_step_id", None)
                # ИСПРАВЛЕНИЕ: /start НЕ является валидным вводом для input шагов
                if new_context.get("message_text") != "/start":
                    new_context.pop("message_text", None)
                
                self.logger.info("🧹 Очистил старые данные ввода при переключении сценария")
            else:
                # Копируем только базовые поля
                new_context = {}
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
                
            # Добавляем информацию о переключении
            new_context.update({
                "switched_from_scenario": context.get("scenario_id"),
                "switch_reason": "engine_switch",
                "scenario_switched": True,
                "switched_to": resolved_scenario_id,
                "switch_successful": True,
            })
            
            # 🔥 КРИТИЧНО: РЕАЛЬНО ВЫПОЛНЯЕМ НОВЫЙ СЦЕНАРИЙ!
            self.logger.info(f"🚀 ЗАПУСКАЮ НОВЫЙ СЦЕНАРИЙ: {resolved_scenario_id}")
            final_context = await self.execute_scenario(resolved_scenario_id, new_context)
            
            self.logger.info(f"✅ Сценарий {resolved_scenario_id} выполнен после переключения")
            
            return final_context
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка переключения сценария на {resolved_scenario_id}: {e}")
            context.update({
                "scenario_switched": False,
                "switch_error": str(e),
                "switch_successful": False
            })
            return context
    
    def _resolve_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        УЛУЧШЕННАЯ подстановка переменных с поддержкой всех современных форматов.
        
        Поддерживает:
        - {variable} - простые переменные
        - {{variable}} - Django/Jinja2 стиль
        - {user.name} - вложенные объекты
        - {items[0]} - элементы массивов
        - {current_timestamp} - специальные переменные
        """
        return template_resolver.resolve(template, context)
        
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
    
    # === СПЕЦИФИЧНЫЕ ХЕНДЛЕРЫ ДЛЯ СИСТЕМЫ ПОЛЬЗОВАТЕЛЕЙ ===
    
    async def _handle_extract_telegram_context(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает данные из Telegram update."""
        try:
            telegram_update = context.get("telegram_update", {})
            
            # Извлекаем основные данные
            telegram_data = {
                "type": "unknown",
                "user_id": None,
                "chat_id": None,
                "username": None,
                "first_name": None,
                "last_name": None,
                "text": None,
                "callback_data": None
            }
            
            # Обработка сообщения
            if "message" in telegram_update:
                message = telegram_update["message"]
                telegram_data["type"] = "message"
                telegram_data["text"] = message.get("text", "")
                
                if "from" in message:
                    user = message["from"]
                    telegram_data["user_id"] = str(user.get("id", ""))
                    telegram_data["username"] = user.get("username", "")
                    telegram_data["first_name"] = user.get("first_name", "")
                    telegram_data["last_name"] = user.get("last_name", "")
                
                if "chat" in message:
                    telegram_data["chat_id"] = str(message["chat"].get("id", ""))
            
            # Обработка callback query
            elif "callback_query" in telegram_update:
                callback = telegram_update["callback_query"]
                telegram_data["type"] = "callback_query"
                telegram_data["callback_data"] = callback.get("data", "")
                
                if "from" in callback:
                    user = callback["from"]
                    telegram_data["user_id"] = str(user.get("id", ""))
                    telegram_data["username"] = user.get("username", "")
                    telegram_data["first_name"] = user.get("first_name", "")
                    telegram_data["last_name"] = user.get("last_name", "")
                
                if "message" in callback and "chat" in callback["message"]:
                    telegram_data["chat_id"] = str(callback["message"]["chat"].get("id", ""))
            
            # Сохраняем результат
            output_var = step.get("params", {}).get("output_var", "telegram_data")
            context[output_var] = telegram_data
            
            self.logger.info(f"✅ Telegram контекст извлечен: {telegram_data['type']}")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка extract_telegram_context: {e}")
            context["__step_error__"] = str(e)
            return context
    
    async def _handle_validate_field(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Валидирует поле пользователя."""
        try:
            params = step.get("params", {})
            field = params.get("field", "")
            value = params.get("value", "")
            validation = params.get("validation", "required")
            
            result = {"valid": True, "error": ""}
            
            # Базовая валидация
            if validation == "required" and not value.strip():
                result = {"valid": False, "error": "Поле обязательно для заполнения"}
            
            elif validation == "phone":
                import re
                phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
                if not re.match(phone_pattern, value.replace(" ", "").replace("-", "")):
                    result = {"valid": False, "error": "Неверный формат номера телефона"}
            
            elif validation == "email":
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, value):
                    result = {"valid": False, "error": "Неверный формат email"}
            
            elif validation == "optional":
                result = {"valid": True, "error": ""}
            
            # Сохраняем результат
            output_var = params.get("output_var", "validation_result")
            context[output_var] = result
            
            self.logger.info(f"✅ Валидация поля {field}: {result['valid']}")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка validate_field: {e}")
            context["__step_error__"] = str(e)
            return context
    
    async def _handle_increment(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Увеличивает значение переменной на 1."""
        try:
            params = step.get("params", {})
            variable = params.get("variable", "")
            
            if variable in context:
                current_value = context[variable]
                if isinstance(current_value, (int, float)):
                    new_value = current_value + 1
                else:
                    new_value = 1
            else:
                new_value = 1
            
            context[variable] = new_value
            
            # Сохраняем результат в output_var если указан
            output_var = params.get("output_var")
            if output_var:
                context[output_var] = new_value
            
            self.logger.info(f"✅ Переменная {variable} увеличена до {new_value}")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка increment: {e}")
            context["__step_error__"] = str(e)
            return context
    
    async def _handle_save_to_object(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Сохраняет значение в объект."""
        try:
            params = step.get("params", {})
            object_name = params.get("object", "")
            key = params.get("key", "")
            value = params.get("value", "")
            
            # Инициализируем объект если его нет
            if object_name not in context:
                context[object_name] = {}
            
            # Сохраняем значение
            context[object_name][key] = value
            
            # Сохраняем результат в output_var если указан
            output_var = params.get("output_var")
            if output_var:
                context[output_var] = {"success": True}
            
            self.logger.info(f"✅ Значение сохранено в {object_name}.{key}")
            return context
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка save_to_object: {e}")
            context["__step_error__"] = str(e)
            return context

    async def _handle_channel_action(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Универсальный обработчик действий с каналами.
        
        НОВАЯ АРХИТЕКТУРА: Напрямую вызывает ChannelManager!
        
        Поддерживаемые действия:
        - send_message: отправка сообщения
        - send_buttons: отправка сообщения с кнопками  
        - edit_message: редактирование сообщения
        
        Пример шага:
        {
            "type": "channel_action",
            "params": {
                "action": "send_message",
                "chat_id": "{chat_id}",
                "text": "Привет!",
                "parse_mode": "HTML"
            }
        }
        """
        try:
            params = step.get("params", {})
            action = params.get("action", "")
            
            if not action:
                raise ValueError("Не указано действие (action) для channel_action")
            
            # Получаем channel_id из контекста
            channel_id = context.get("channel_id")
            if not channel_id:
                raise ValueError("Не указан channel_id в контексте")
            
            # Получаем ChannelManager из глобального состояния
            from app.simple_main import get_channel_manager
            channel_manager = get_channel_manager()
            
            if not channel_manager:
                raise ValueError("ChannelManager не инициализирован")
            
            # Подставляем переменные в параметры
            resolved_params = {}
            for key, value in params.items():
                if key != "action":  # action не подставляем
                    if isinstance(value, str):
                        resolved_params[key] = self._resolve_template(value, context)
                    else:
                        resolved_params[key] = value
            
            # Выполняем действие через ChannelManager
            result = None
            
            if action == "send_message":
                chat_id = resolved_params.get("chat_id")
                text = resolved_params.get("text")
                if not chat_id or not text:
                    raise ValueError("Для send_message требуются chat_id и text")
                
                # Подготавливаем дополнительные параметры
                kwargs = {k: v for k, v in resolved_params.items() 
                         if k not in ["chat_id", "text"]}
                
                # Используем обычный метод - паузы теперь автоматические
                result = await channel_manager.send_message(channel_id, chat_id, text, **kwargs)
                
            elif action == "send_buttons":
                chat_id = resolved_params.get("chat_id")
                text = resolved_params.get("text")
                buttons = resolved_params.get("buttons")
                if not chat_id or not text or not buttons:
                    raise ValueError("Для send_buttons требуются chat_id, text и buttons")
                
                # Подготавливаем дополнительные параметры
                kwargs = {k: v for k, v in resolved_params.items() 
                         if k not in ["chat_id", "text", "buttons"]}
                
                # Используем обычный метод - паузы теперь автоматические
                result = await channel_manager.send_buttons(channel_id, chat_id, text, buttons, **kwargs)
                
            elif action == "edit_message":
                chat_id = resolved_params.get("chat_id")
                message_id = resolved_params.get("message_id")
                text = resolved_params.get("text")
                if not chat_id or not message_id or not text:
                    raise ValueError("Для edit_message требуются chat_id, message_id и text")
                
                # Подготавливаем дополнительные параметры
                kwargs = {k: v for k, v in resolved_params.items() 
                         if k not in ["chat_id", "message_id", "text"]}
                
                result = await channel_manager.edit_message(channel_id, chat_id, int(message_id), text, **kwargs)
                
            elif action == "forward_message":
                from_chat_id = resolved_params.get("from_chat_id")
                to_chat_id = resolved_params.get("to_chat_id") or resolved_params.get("chat_id")
                message_id = resolved_params.get("message_id")
                if not from_chat_id or not to_chat_id or not message_id:
                    raise ValueError("Для forward_message требуются from_chat_id, to_chat_id и message_id")
                
                # Подготавливаем дополнительные параметры
                kwargs = {k: v for k, v in resolved_params.items() 
                         if k not in ["from_chat_id", "to_chat_id", "chat_id", "message_id"]}
                
                result = await channel_manager.forward_message(channel_id, to_chat_id, from_chat_id, int(message_id), **kwargs)
                
            elif action == "copy_message":
                from_chat_id = resolved_params.get("from_chat_id")
                to_chat_id = resolved_params.get("to_chat_id") or resolved_params.get("chat_id")
                message_id = resolved_params.get("message_id")
                if not from_chat_id or not to_chat_id or not message_id:
                    raise ValueError("Для copy_message требуются from_chat_id, to_chat_id и message_id")
                
                # Подготавливаем дополнительные параметры
                kwargs = {k: v for k, v in resolved_params.items() 
                         if k not in ["from_chat_id", "to_chat_id", "chat_id", "message_id"]}
                
                # Используем метод с автоматической паузой для лучшего UX (особенно важно для видео)
                delay_seconds = kwargs.pop("delay_seconds", 1.0)  # по умолчанию 1 секунда для видео  
                result = await channel_manager.copy_message(channel_id, to_chat_id, from_chat_id, message_id, **kwargs)
                
            elif action == "send_document":
                chat_id = resolved_params.get("chat_id")
                document_path = resolved_params.get("document_path")
                if not chat_id or not document_path:
                    raise ValueError("Для send_document требуются chat_id и document_path")
                
                # Подготавливаем дополнительные параметры
                kwargs = {k: v for k, v in resolved_params.items() 
                         if k not in ["chat_id", "document_path"]}
                
                result = await channel_manager.send_document(channel_id, chat_id, document_path, **kwargs)
                
            elif action == "edit_message":
                chat_id = resolved_params.get("chat_id")
                message_id = resolved_params.get("message_id")
                text = resolved_params.get("text")
                if not chat_id or not message_id or not text:
                    raise ValueError("Для edit_message требуются chat_id, message_id и text")
                
                # Подготавливаем дополнительные параметры
                kwargs = {k: v for k, v in resolved_params.items() 
                         if k not in ["chat_id", "message_id", "text"]}
                
                result = await channel_manager.edit_message(channel_id, chat_id, message_id, text, **kwargs)
            
            else:
                raise ValueError(f"Неподдерживаемое действие: {action}")
            
            # Сохраняем результат в контекст
            context["channel_action_result"] = result
            context["channel_action_success"] = result.get("success", False)
            
            return context

        except Exception as e:
            logger.error(f"❌ Ошибка выполнения channel_action: {e}")
            context["channel_action_result"] = {"success": False, "error": str(e)}
            context["channel_action_success"] = False
            return context

    async def _handle_conditional_execute(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Условное выполнение шага на основе заданных условий.
        
        Args:
            step: Данные шага с параметрами:
                - condition: Условие для проверки
                - true_action: Шаг для выполнения если условие истинно
                - false_action: Шаг для выполнения если условие ложно
            context: Контекст выполнения
            
        Returns:
            Dict[str, Any]: Результат выполнения выбранного действия
        """
        params = step.get("params", {})
        condition = params.get("condition", "")
        true_action = params.get("true_action")
        false_action = params.get("false_action")
        
        # Оцениваем условие
        condition_result = self._evaluate_branch_condition(condition, context)
        self.logger.info(f"🔍 Условие '{condition}' = {condition_result}")
        
        # Выбираем действие для выполнения
        if condition_result and true_action:
            self.logger.info("✅ Выполняю действие для истинного условия")
            selected_action = true_action
        elif not condition_result and false_action:
            self.logger.info("❌ Выполняю действие для ложного условия")
            selected_action = false_action
        else:
            self.logger.warning("⚠️ Нет подходящего действия для условия")
            return context
        
        # Выполняем выбранное действие
        if isinstance(selected_action, dict):
            # Выполняем встроенный шаг
            return await self.execute_step(selected_action, context)
        elif isinstance(selected_action, str):
            # Ищем шаг по ID
            scenario_data = context.get("_scenario_data", {})
            steps = scenario_data.get("steps", [])
            
            target_step = None
            for s in steps:
                if s.get("id") == selected_action:
                    target_step = s
                    break
                    
            if target_step:
                return await self.execute_step(target_step, context)
            else:
                self.logger.error(f"❌ Шаг '{selected_action}' не найден")
                return context
        else:
            self.logger.error(f"❌ Неверный формат действия: {selected_action}")
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
    
    НОВАЯ АРХИТЕКТУРА: Каждый вызов создает НОВЫЙ движок!
    Это позволяет каждому каналу иметь свой изолированный движок.
    
    Returns:
        SimpleScenarioEngine: Настроенный движок с плагинами
    """
    from loguru import logger
    
    logger.info("🔧 Создание нового SimpleScenarioEngine...")
    
    # Создаем НОВЫЙ движок для каждого вызова
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
    
    # TELEGRAM ПЛАГИН УДАЛЕН - НЕ РЕГИСТРИРУЕМ АВТОМАТИЧЕСКИ!
    # Telegram интеграция должна быть опциональной и настраиваться через API
    
    try:
        # 2. LLM Plugin - для работы с языковыми моделями
        logger.info("📦 Регистрация SimpleLLM Plugin...")
        from app.plugins.simple_llm_plugin import SimpleLLMPlugin
        llm_plugin = SimpleLLMPlugin()
        engine.register_plugin(llm_plugin)
        plugins_to_initialize.append(llm_plugin)
        logger.info("✅ SimpleLLM Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleLLM Plugin недоступен: {e}")
    
    try:
        # 3. RAG Plugin - для работы с базой знаний
        logger.info("📦 Регистрация SimpleRAG Plugin...")
        from app.plugins.simple_rag_plugin import SimpleRAGPlugin
        rag_plugin = SimpleRAGPlugin()
        engine.register_plugin(rag_plugin)
        plugins_to_initialize.append(rag_plugin)
        logger.info("✅ SimpleRAG Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleRAG Plugin недоступен: {e}")
    
    try:
        # 4. Scheduler Plugin - для отложенного выполнения задач
        logger.info("📦 Регистрация SimpleScheduler Plugin...")
        from app.plugins.simple_scheduler_plugin import SimpleSchedulerPlugin
        scheduler_plugin = SimpleSchedulerPlugin()
        engine.register_plugin(scheduler_plugin)
        plugins_to_initialize.append(scheduler_plugin)
        logger.info("✅ SimpleScheduler Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleScheduler Plugin недоступен: {e}")
    
    try:
        # 5. HTTP Plugin - для внешних HTTP запросов
        logger.info("📦 Регистрация SimpleHTTP Plugin...")
        from app.plugins.simple_http_plugin import SimpleHTTPPlugin
        http_plugin = SimpleHTTPPlugin()
        engine.register_plugin(http_plugin)
        plugins_to_initialize.append(http_plugin)
        logger.info("✅ SimpleHTTP Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleHTTP Plugin недоступен: {e}")
    
    try:
        # 6. AmoCRM Plugin - для интеграции с AmoCRM
        logger.info("📦 Регистрация SimpleAmoCRM Plugin...")
        from app.plugins.simple_amocrm_plugin import SimpleAmoCRMPlugin
        amocrm_plugin = SimpleAmoCRMPlugin()
        engine.register_plugin(amocrm_plugin)
        plugins_to_initialize.append(amocrm_plugin)
        logger.info("✅ SimpleAmoCRM Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleAmoCRM Plugin недоступен: {e}")
    
    try:
        # 7. AmoCRM Companies Plugin - для работы с компаниями
        logger.info("📦 Регистрация SimpleAmoCRM Companies Plugin...")
        from app.plugins.simple_amocrm_companies import SimpleAmoCRMCompaniesPlugin
        amocrm_companies_plugin = SimpleAmoCRMCompaniesPlugin()
        engine.register_plugin(amocrm_companies_plugin)
        plugins_to_initialize.append(amocrm_companies_plugin)
        logger.info("✅ SimpleAmoCRM Companies Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleAmoCRM Companies Plugin недоступен: {e}")
    
    try:
        # 8. AmoCRM Tasks Plugin - для работы с задачами и событиями
        logger.info("📦 Регистрация SimpleAmoCRM Tasks Plugin...")
        from app.plugins.simple_amocrm_tasks import SimpleAmoCRMTasksPlugin
        amocrm_tasks_plugin = SimpleAmoCRMTasksPlugin()
        engine.register_plugin(amocrm_tasks_plugin)
        plugins_to_initialize.append(amocrm_tasks_plugin)
        logger.info("✅ SimpleAmoCRM Tasks Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleAmoCRM Tasks Plugin недоступен: {e}")
    
    try:
        # 9. AmoCRM Advanced Plugin - для продвинутых операций
        logger.info("📦 Регистрация SimpleAmoCRM Advanced Plugin...")
        from app.plugins.simple_amocrm_advanced import SimpleAmoCRMAdvancedPlugin
        amocrm_advanced_plugin = SimpleAmoCRMAdvancedPlugin()
        engine.register_plugin(amocrm_advanced_plugin)
        plugins_to_initialize.append(amocrm_advanced_plugin)
        logger.info("✅ SimpleAmoCRM Advanced Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleAmoCRM Advanced Plugin недоступен: {e}")
    
    try:
        # 10. AmoCRM Admin Plugin - для административных операций
        logger.info("📦 Регистрация SimpleAmoCRM Admin Plugin...")
        from app.plugins.simple_amocrm_admin import SimpleAmoCRMAdminPlugin
        amocrm_admin_plugin = SimpleAmoCRMAdminPlugin()
        engine.register_plugin(amocrm_admin_plugin)
        plugins_to_initialize.append(amocrm_admin_plugin)
        logger.info("✅ SimpleAmoCRM Admin Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleAmoCRM Admin Plugin недоступен: {e}")
    
    try:
        # 11. PDF Plugin - для генерации PDF документов
        logger.info("📦 Регистрация SimplePDF Plugin...")
        from app.plugins.simple_pdf_plugin import SimplePDFPlugin
        pdf_plugin = SimplePDFPlugin()
        engine.register_plugin(pdf_plugin)
        plugins_to_initialize.append(pdf_plugin)
        logger.info("✅ SimplePDF Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimplePDF Plugin недоступен: {e}")
    
    try:
        # 12. Routing Plugin - для универсальной маршрутизации
        logger.info("📦 Регистрация SimpleRouting Plugin...")
        from app.plugins.simple_routing_plugin import SimpleRoutingPlugin
        routing_plugin = SimpleRoutingPlugin()
        engine.register_plugin(routing_plugin)
        plugins_to_initialize.append(routing_plugin)
        logger.info("✅ SimpleRouting Plugin зарегистрирован")
    except Exception as e:
        logger.warning(f"⚠️ SimpleRouting Plugin недоступен: {e}")
    
    # === ИНИЦИАЛИЗАЦИЯ ПЛАГИНОВ (ПОСЛЕ РЕГИСТРАЦИИ) ===
    
    logger.info("🔧 Инициализация зарегистрированных плагинов...")
    
    for plugin in plugins_to_initialize:
        try:
            logger.info(f"🚀 Инициализация {plugin.name}...")
            await plugin.initialize()
            logger.info(f"✅ {plugin.name} инициализирован")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка инициализации {plugin.name}: {e}")
    
    # === ИНИЦИАЛИЗАЦИЯ CHANNEL MANAGER ===
    
    logger.info("🔧 Движок готов БЕЗ привязки к каналам (правильная архитектура)")
    
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