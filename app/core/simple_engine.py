#!/usr/bin/env python3
"""
🚀 SIMPLE SCENARIO ENGINE - Современная версия
Единственный движок выполнения сценариев в KittyCore

Принципы:
- Простота превыше всего
- Один движок для всех сценариев  
- Система плагинов через BasePlugin
- Явная передача контекста
- Поддержка human-in-the-loop
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Callable
from loguru import logger

from .base_plugin import BasePlugin

# === ИСКЛЮЧЕНИЯ ===

class StopExecution(Exception):
    """
    Исключение для остановки выполнения сценария.
    
    Используется когда нужно дождаться ввода пользователя или внешнего события.
    НЕ является ошибкой!
    """
    
    def __init__(self, message: str, reason: str = "user_input_required", wait_for: str = None):
        super().__init__(message)
        self.reason = reason
        self.wait_for = wait_for
        self.timestamp = datetime.now().isoformat()

# === ОСНОВНОЙ ДВИЖОК ===

class SimpleScenarioEngine:
    """
    🚀 ПРОСТОЙ И МОЩНЫЙ ДВИЖОК СЦЕНАРИЕВ
    
    Особенности:
    - Выполняет JSON сценарии с шагами
    - Система плагинов через BasePlugin
    - Поддержка переключения сценариев
    - Human-in-the-loop через StopExecution
    - Сохранение состояния между вызовами
    """
    
    def __init__(self):
        self.step_handlers: Dict[str, Callable] = {}
        self.plugins: Dict[str, BasePlugin] = {}
        self.logger = logger.bind(component="SimpleScenarioEngine")
        
        # Регистрируем базовые обработчики
        self._register_core_handlers()
        
        self.logger.info("🚀 SimpleScenarioEngine инициализирован")
    
    def _register_core_handlers(self):
        """Регистрирует базовые обработчики шагов"""
        self.step_handlers.update({
            # === БАЗОВЫЕ ОБРАБОТЧИКИ ===
            "start": self._handle_start,
            "end": self._handle_end,
            "action": self._handle_action,
            "input": self._handle_input,
            "branch": self._handle_branch,
            "conditional_execute": self._handle_conditional_execute,
            "switch_scenario": self._handle_switch_scenario,
            "log_message": self._handle_log_message,
            
            # === TELEGRAM ИНТЕГРАЦИЯ ===
            "channel_action": self._handle_channel_action,
            "extract_telegram_context": self._handle_extract_telegram_context,
            
            # === УТИЛИТЫ ===
            "validate_field": self._handle_validate_field,
            "increment": self._handle_increment,
            "save_to_object": self._handle_save_to_object,
        })
        
        self.logger.info("✅ Базовые обработчики зарегистрированы", 
                        handlers=list(self.step_handlers.keys()))
    
    def register_plugin(self, plugin: BasePlugin):
        """
        Регистрирует плагин и его обработчики
        
        Args:
            plugin: Экземпляр плагина наследующего BasePlugin
        """
        # Передаём ссылку на движок плагину
        plugin.set_engine(self)
        
        self.plugins[plugin.name] = plugin
        
        # Регистрируем обработчики плагина
        plugin_handlers = plugin.register_handlers()
        self.step_handlers.update(plugin_handlers)
        
        self.logger.info(f"🔌 Плагин {plugin.name} зарегистрирован",
                        plugin=plugin.name,
                        new_handlers=list(plugin_handlers.keys()))
    
    async def healthcheck(self) -> Dict[str, bool]:
        """Проверяет здоровье движка и всех плагинов"""
        health = {"engine": True}
        
        for plugin_name, plugin in self.plugins.items():
            try:
                health[plugin_name] = await plugin.healthcheck()
            except Exception as e:
                self.logger.error(f"❌ Ошибка healthcheck плагина {plugin_name}: {e}")
                health[plugin_name] = False
        
        self.logger.info("🔍 Healthcheck завершён", health=health)
        return health
    
    async def execute_scenario(self, scenario: Union[str, Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        ГЛАВНЫЙ МЕТОД: Выполняет сценарий от начала до конца
        
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
                "type": "mongo_find_one_document",
                "params": {
                    "collection": "scenarios",
                    "filter": {"scenario_id": scenario_id}
                }
            }
            
            temp_context = {}
            await self.execute_step(get_scenario_step, temp_context)
            
            if not temp_context.get("document"):
                raise ValueError(f"Сценарий {scenario_id} не найден в БД")
            
            scenario = temp_context["document"]
        
        scenario_id = scenario.get("scenario_id", "unknown")
        steps_data = scenario.get("steps", [])
        
        # Поддерживаем как объект, так и массив шагов
        if isinstance(steps_data, dict):
            steps = list(steps_data.values())
        else:
            steps = steps_data
        
        self.logger.info(f"🎯 Начинаю выполнение сценария {scenario_id}",
                        scenario_id=scenario_id,
                        steps_count=len(steps),
                        initial_context=context)
        
        # Инициализируем контекст выполнения
        execution_context = {
            **context,
            "scenario_id": scenario_id,
            "execution_started": True,
            "start_time": datetime.now().isoformat()
        }
        
        # НЕ перезаписываем current_step если он уже есть (для продолжения)
        if "current_step" not in execution_context:
            execution_context["current_step"] = None
        
        try:
            # Находим стартовый шаг
            if execution_context.get("current_step"):
                # Продолжаем с указанного шага
                target_step_id = execution_context["current_step"]
                current_step = self._find_step_by_id(steps, target_step_id)
                
                if not current_step:
                    self.logger.warning(f"⚠️ Шаг {target_step_id} не найден, начинаю с первого")
                    current_step = self._find_first_step(steps)
                else:
                    self.logger.info(f"📍 Продолжаю с шага: {target_step_id}")
            else:
                # Ищем первый шаг (обычно type="start")
                current_step = self._find_first_step(steps)
            
            if not current_step:
                raise ValueError(f"Не найден стартовый шаг в сценарии {scenario_id}")
            
            # Выполняем шаги последовательно
            while current_step:
                execution_context["current_step"] = current_step.get("id")
                
                try:
                    # Выполняем текущий шаг
                    step_result = await self.execute_step(current_step, execution_context)
                    
                    # Обновляем контекст результатом
                    execution_context.update(step_result)
                    
                    # Проверяем переключение сценария
                    if execution_context.get("scenario_switched"):
                        new_scenario_id = execution_context.get("switched_to")
                        if new_scenario_id and new_scenario_id != scenario_id:
                            self.logger.info(f"🔄 Переключение сценария: {scenario_id} → {new_scenario_id}")
                            
                            try:
                                # Рекурсивно выполняем новый сценарий
                                return await self.execute_scenario(new_scenario_id, execution_context)
                            except StopExecution as stop_e:
                                self.logger.info(f"⏱️ Новый сценарий ожидает ввод: {stop_e}")
                                execution_context["execution_stopped"] = True
                                execution_context["stop_reason"] = str(stop_e)
                                execution_context["waiting_for_input"] = True
                                return execution_context
                    
                    # Находим следующий шаг
                    current_step = self._find_next_step(steps, current_step, execution_context)
                    
                except StopExecution as e:
                    # НОРМАЛЬНАЯ остановка для ожидания ввода - НЕ ошибка!
                    self.logger.info(f"⏱️ Выполнение остановлено: {e.reason}")
                    execution_context["execution_stopped"] = True
                    execution_context["stop_reason"] = str(e)
                    execution_context["waiting_for_input"] = True
                    execution_context["wait_for"] = e.wait_for
                    return execution_context
            
            # Сценарий завершён успешно
            execution_context["execution_completed"] = True
            execution_context["end_time"] = datetime.now().isoformat()
            
            self.logger.info(f"✅ Сценарий {scenario_id} выполнен успешно",
                           scenario_id=scenario_id)
            
            return execution_context
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка выполнения сценария {scenario_id}: {e}",
                            scenario_id=scenario_id,
                            current_step=execution_context.get("current_step"),
                            error=str(e))
            
            execution_context["execution_error"] = True
            execution_context["error"] = str(e)
            execution_context["error_time"] = datetime.now().isoformat()
            
            raise
    
    async def execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполняет один шаг сценария
        
        Args:
            step: Данные шага
            context: Контекст выполнения
            
        Returns:
            Dict[str, Any]: Результат выполнения шага
        """
        step_id = step.get("id", "unknown")
        step_type = step.get("type", "unknown")
        
        self.logger.debug(f"🔧 Выполняю шаг {step_id} (type: {step_type})")
        
        # Ищем обработчик для типа шага
        if step_type not in self.step_handlers:
            raise ValueError(f"Неизвестный тип шага: {step_type}")
        
        handler = self.step_handlers[step_type]
        
        try:
            # Выполняем обработчик
            start_time = time.time()
            result = await handler(step, context)
            execution_time = int((time.time() - start_time) * 1000)
            
            self.logger.debug(f"✅ Шаг {step_id} выполнен за {execution_time}мс")
            
            return result or {}
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка выполнения шага {step_id}: {e}")
            raise
    
    # === ПОИСК ШАГОВ ===
    
    def _find_first_step(self, steps: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Находит первый шаг сценария"""
        # Ищем шаг с type="start"
        for step in steps:
            if step.get("type") == "start":
                return step
        
        # Если нет start, берём первый шаг
        return steps[0] if steps else None
    
    def _find_step_by_id(self, steps: List[Dict[str, Any]], step_id: str) -> Optional[Dict[str, Any]]:
        """Находит шаг по ID"""
        for step in steps:
            if step.get("id") == step_id:
                return step
        return None
    
    def _find_next_step(self, steps: List[Dict[str, Any]], current_step: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Находит следующий шаг для выполнения"""
        # Проверяем переопределение следующего шага (для условных переходов)
        next_step_id = context.get("next_step_override") or current_step.get("next_step")
        
        # Очищаем переопределение после использования
        if "next_step_override" in context:
            del context["next_step_override"]
        
        if not next_step_id:
            return None  # Сценарий завершён
        
        return self._find_step_by_id(steps, next_step_id)
    
    # === УТИЛИТЫ ===
    
    def _resolve_template(self, template: str, context: Dict[str, Any]) -> str:
        """Подстановка переменных {var} из контекста"""
        if not isinstance(template, str):
            return str(template)
        
        result = template
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        return result
    
    def get_registered_handlers(self) -> List[str]:
        """Возвращает список зарегистрированных обработчиков"""
        return list(self.step_handlers.keys())
    
    def get_registered_plugins(self) -> List[str]:
        """Возвращает список зарегистрированных плагинов"""
        return list(self.plugins.keys())
    
    # === БАЗОВЫЕ ОБРАБОТЧИКИ ===
    
    async def _handle_start(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик шага 'start'"""
        message = step.get("params", {}).get("message", "Сценарий запущен")
        self.logger.info(f"🚀 START: {message}")
        return {"start_message": message}
    
    async def _handle_end(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик шага 'end'"""
        message = step.get("params", {}).get("message", "Сценарий завершён")
        self.logger.info(f"🏁 END: {message}")
        return {"end_message": message, "scenario_completed": True}
    
    async def _handle_action(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик шага 'action' - универсальное действие"""
        params = step.get("params", {})
        action_type = params.get("action", "unknown")
        
        self.logger.info(f"⚡ ACTION: {action_type}")
        
        # Здесь можно добавить различные типы действий
        result = {"action_executed": action_type, "action_params": params}
        
        return result
    
    async def _handle_input(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик шага 'input' - ожидание ввода пользователя"""
        params = step.get("params", {})
        input_type = params.get("type", "text")
        prompt = params.get("prompt", "Введите данные:")
        
        # Проверяем есть ли уже ввод в контексте
        if context.get("user_input") is not None:
            user_input = context["user_input"]
            self.logger.info(f"📝 INPUT получен: {user_input}")
            
            # Сохраняем ввод в переменную
            var_name = params.get("save_to", "user_input")
            return {var_name: user_input, "input_received": True}
        else:
            # Останавливаем выполнение для ожидания ввода
            self.logger.info(f"⏳ INPUT ожидает ввод: {prompt}")
            raise StopExecution(
                message=prompt,
                reason="user_input_required",
                wait_for=input_type
            )
    
    async def _handle_branch(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик шага 'branch' - условное ветвление"""
        params = step.get("params", {})
        condition = params.get("condition", "true")
        true_step = params.get("true_step")
        false_step = params.get("false_step")
        
        # Вычисляем условие
        condition_result = self._evaluate_condition(condition, context)
        
        self.logger.info(f"🔀 BRANCH: {condition} = {condition_result}")
        
        # Устанавливаем следующий шаг
        next_step = true_step if condition_result else false_step
        
        if next_step:
            return {"next_step_override": next_step, "branch_result": condition_result}
        else:
            return {"branch_result": condition_result}
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Простое вычисление условий"""
        # Заменяем переменные в условии
        resolved_condition = self._resolve_template(condition, context)
        
        # Простые проверки
        if resolved_condition in ["true", "True", "1"]:
            return True
        elif resolved_condition in ["false", "False", "0"]:
            return False
        
        # Проверки на существование переменных
        if resolved_condition.startswith("exists:"):
            var_name = resolved_condition[7:]
            return var_name in context
        
        # По умолчанию false
        return False
    
    async def _handle_conditional_execute(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик условного выполнения"""
        params = step.get("params", {})
        condition = params.get("condition", "true")
        
        if self._evaluate_condition(condition, context):
            # Выполняем вложенные шаги если условие истинно
            nested_steps = params.get("steps", [])
            for nested_step in nested_steps:
                await self.execute_step(nested_step, context)
        
        return {"conditional_executed": True}
    
    async def _handle_switch_scenario(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик переключения сценария"""
        params = step.get("params", {})
        target_scenario = params.get("scenario_id")
        
        if not target_scenario:
            raise ValueError("Не указан scenario_id для переключения")
        
        # Разрешаем шаблоны в ID сценария
        target_scenario = self._resolve_template(target_scenario, context)
        
        self.logger.info(f"🔄 SWITCH_SCENARIO: переключение на {target_scenario}")
        
        return {
            "scenario_switched": True,
            "switched_to": target_scenario,
            "switch_reason": params.get("reason", "manual_switch")
        }
    
    async def _handle_log_message(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик логирования"""
        params = step.get("params", {})
        level = params.get("level", "info")
        message = params.get("message", "Log message")
        
        # Разрешаем шаблоны в сообщении
        resolved_message = self._resolve_template(message, context)
        
        # Логируем с нужным уровнем
        if level == "debug":
            self.logger.debug(resolved_message)
        elif level == "warning":
            self.logger.warning(resolved_message)
        elif level == "error":
            self.logger.error(resolved_message)
        else:
            self.logger.info(resolved_message)
        
        return {"logged": True, "log_level": level, "log_message": resolved_message}
    
    # === TELEGRAM/CHANNEL ОБРАБОТЧИКИ ===
    
    async def _handle_channel_action(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик действий с каналами (Telegram и др.)"""
        params = step.get("params", {})
        action = params.get("action", "send_message")
        
        self.logger.info(f"📡 CHANNEL_ACTION: {action}")
        
        # Делегируем выполнение соответствующему плагину
        if "simple_telegram" in self.plugins:
            telegram_plugin = self.plugins["simple_telegram"]
            return await telegram_plugin.handle_channel_action(action, params, context)
        else:
            self.logger.warning("Telegram плагин не найден")
            return {"channel_action_skipped": True, "reason": "no_telegram_plugin"}
    
    async def _handle_extract_telegram_context(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Извлечение Telegram контекста"""
        telegram_data = context.get("telegram_data", {})
        
        extracted = {
            "chat_id": telegram_data.get("chat_id"),
            "user_id": telegram_data.get("user_id"),
            "message_id": telegram_data.get("message_id"),
            "username": telegram_data.get("username"),
        }
        
        self.logger.debug("📱 Извлечён Telegram контекст", extracted=extracted)
        
        return {"telegram_context": extracted, **extracted}
    
    # === УТИЛИТНЫЕ ОБРАБОТЧИКИ ===
    
    async def _handle_validate_field(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация полей"""
        params = step.get("params", {})
        field_name = params.get("field")
        validation_type = params.get("type", "required")
        
        field_value = context.get(field_name)
        is_valid = True
        error_message = None
        
        if validation_type == "required":
            is_valid = field_value is not None and str(field_value).strip() != ""
            if not is_valid:
                error_message = f"Поле {field_name} обязательно для заполнения"
        
        elif validation_type == "email":
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            is_valid = bool(re.match(email_pattern, str(field_value or "")))
            if not is_valid:
                error_message = f"Поле {field_name} должно содержать валидный email"
        
        return {
            "validation_result": is_valid,
            "field_name": field_name,
            "error_message": error_message
        }
    
    async def _handle_increment(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Инкремент переменной"""
        params = step.get("params", {})
        var_name = params.get("variable", "counter")
        increment = params.get("increment", 1)
        
        current_value = context.get(var_name, 0)
        new_value = current_value + increment
        
        return {var_name: new_value, "incremented": True}
    
    async def _handle_save_to_object(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Сохранение данных в объект"""
        params = step.get("params", {})
        object_name = params.get("object", "data")
        field_mappings = params.get("fields", {})
        
        # Получаем или создаём объект
        obj = context.get(object_name, {})
        
        # Сохраняем поля
        for field_name, source_var in field_mappings.items():
            if source_var in context:
                obj[field_name] = context[source_var]
        
        return {object_name: obj, "saved_to_object": True} 