"""
Simple Routing Plugin - Универсальный плагин маршрутизации

Обеспечивает универсальную маршрутизацию внутри сценариев:
- Переходы на конкретные шаги по ID
- Условная маршрутизация на основе callback_data
- Универсальная обработка callback-ов
"""

from typing import Dict, Any
from loguru import logger

from app.core.base_plugin import BasePlugin


class SimpleRoutingPlugin(BasePlugin):
    """Универсальный плагин маршрутизации для переходов между шагами"""
    
    def __init__(self):
        super().__init__("simple_routing")
        logger.info("SimpleRoutingPlugin инициализирован")
    
    async def _do_initialize(self):
        """Инициализация плагина"""
        logger.info("✅ SimpleRoutingPlugin готов к работе")
    
    def register_handlers(self) -> Dict[str, Any]:
        """Регистрация обработчиков шагов"""
        return {
            "route_callback": self._handle_route_callback,
            "route_to_step": self._handle_route_to_step,
            "conditional_route": self._handle_conditional_route
        }
    
    async def _handle_route_callback(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Универсальный обработчик маршрутизации на основе callback_data.
        
        Параметры:
        - routes: словарь маршрутов {callback_data: target_step_id}
        - default_step: шаг по умолчанию (опционально)
        - callback_field: поле с callback данными (по умолчанию "callback_data")
        - output_var: переменная для сохранения результата (по умолчанию "route_result")
        
        Пример:
        {
            "type": "route_callback",
            "params": {
                "routes": {
                    "view_examples": "show_examples",
                    "start_diagnosis": "begin_diagnosis",
                    "contact_request": "request_contact"
                },
                "default_step": "main_menu",
                "callback_field": "telegram_callback_data",
                "output_var": "routing_result"
            }
        }
        """
        params = step_data.get("params", {})
        
        # Извлекаем параметры
        routes = params.get("routes", {})
        default_step = params.get("default_step")
        callback_field = params.get("callback_field", "callback_data")
        output_var = params.get("output_var", "route_result")
        
        # Получаем callback_data из контекста
        callback_data = context.get(callback_field)
        
        # Если callback_data не найдено в прямом поле, ищем в telegram_update
        if not callback_data and "telegram_update" in context:
            telegram_update = context["telegram_update"]
            if "callback_query" in telegram_update:
                callback_data = telegram_update["callback_query"].get("data")
            elif "message" in telegram_update:
                callback_data = telegram_update["message"].get("text")
        
        try:
            # Определяем целевой шаг
            target_step = None
            
            if callback_data and callback_data in routes:
                target_step = routes[callback_data]
                logger.info(f"📍 Маршрутизация: {callback_data} -> {target_step}")
            elif default_step:
                target_step = default_step
                logger.info(f"📍 Маршрутизация по умолчанию: -> {target_step}")
            
            # Сохраняем результат
            route_result = {
                "success": bool(target_step),
                "callback_data": callback_data,
                "target_step": target_step,
                "routes_checked": routes,
                "used_default": bool(default_step and not (callback_data and callback_data in routes))
            }
            
            context[output_var] = route_result
            
            # Устанавливаем следующий шаг если найден
            if target_step:
                context["next_step_id"] = target_step
                context["routing_successful"] = True
            else:
                context["routing_successful"] = False
                logger.warning(f"⚠️ Не найден маршрут для callback_data: {callback_data}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка маршрутизации: {e}")
            context[output_var] = {
                "success": False,
                "error": str(e),
                "callback_data": callback_data
            }
            context["routing_successful"] = False
        
        return context
    
    async def _handle_route_to_step(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Простой переход на указанный шаг.
        
        Параметры:
        - target_step: ID целевого шага (обязательно)
        - condition: условие перехода (опционально)
        - output_var: переменная для сохранения результата (по умолчанию "route_result")
        
        Пример:
        {
            "type": "route_to_step",
            "params": {
                "target_step": "confirmation_step",
                "condition": "user_confirmed == true",
                "output_var": "step_routing"
            }
        }
        """
        params = step_data.get("params", {})
        
        target_step = params.get("target_step")
        condition = params.get("condition")
        output_var = params.get("output_var", "route_result")
        
        if not target_step:
            logger.error("route_to_step: target_step не указан")
            context[output_var] = {"success": False, "error": "target_step не указан"}
            return context
        
        try:
            # Проверяем условие если есть
            should_route = True
            if condition:
                should_route = self._evaluate_condition(condition, context)
            
            if should_route:
                context["next_step_id"] = target_step
                context["routing_successful"] = True
                context[output_var] = {
                    "success": True,
                    "target_step": target_step,
                    "condition_checked": condition,
                    "condition_result": should_route
                }
                logger.info(f"📍 Переход на шаг: {target_step}")
            else:
                context["routing_successful"] = False
                context[output_var] = {
                    "success": False,
                    "target_step": target_step,
                    "condition_checked": condition,
                    "condition_result": should_route,
                    "reason": "Условие не выполнено"
                }
                logger.info(f"🚫 Переход на шаг {target_step} отменен - условие не выполнено")
        
        except Exception as e:
            logger.error(f"❌ Ошибка перехода на шаг: {e}")
            context[output_var] = {
                "success": False,
                "error": str(e),
                "target_step": target_step
            }
            context["routing_successful"] = False
        
        return context
    
    async def _handle_conditional_route(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Условная маршрутизация с несколькими вариантами.
        
        Параметры:
        - conditions: список условий и соответствующих шагов
        - default_step: шаг по умолчанию (опционально)
        - output_var: переменная для сохранения результата (по умолчанию "route_result")
        
        Пример:
        {
            "type": "conditional_route",
            "params": {
                "conditions": [
                    {"condition": "user_type == 'premium'", "target_step": "premium_menu"},
                    {"condition": "user_type == 'basic'", "target_step": "basic_menu"},
                    {"condition": "is_first_visit == true", "target_step": "welcome_tour"}
                ],
                "default_step": "main_menu",
                "output_var": "conditional_routing"
            }
        }
        """
        params = step_data.get("params", {})
        
        conditions = params.get("conditions", [])
        default_step = params.get("default_step")
        output_var = params.get("output_var", "route_result")
        
        try:
            target_step = None
            matched_condition = None
            
            # Проверяем условия по порядку
            for condition_item in conditions:
                condition = condition_item.get("condition")
                step = condition_item.get("target_step")
                
                if condition and step and self._evaluate_condition(condition, context):
                    target_step = step
                    matched_condition = condition
                    break
            
            # Используем шаг по умолчанию если ничего не подошло
            if not target_step and default_step:
                target_step = default_step
            
            # Сохраняем результат
            if target_step:
                context["next_step_id"] = target_step
                context["routing_successful"] = True
                context[output_var] = {
                    "success": True,
                    "target_step": target_step,
                    "matched_condition": matched_condition,
                    "used_default": bool(not matched_condition and default_step),
                    "conditions_checked": len(conditions)
                }
                logger.info(f"📍 Условная маршрутизация: -> {target_step}")
            else:
                context["routing_successful"] = False
                context[output_var] = {
                    "success": False,
                    "reason": "Ни одно условие не выполнено и нет шага по умолчанию",
                    "conditions_checked": len(conditions)
                }
                logger.warning("⚠️ Условная маршрутизация: ни одно условие не выполнено")
        
        except Exception as e:
            logger.error(f"❌ Ошибка условной маршрутизации: {e}")
            context[output_var] = {
                "success": False,
                "error": str(e)
            }
            context["routing_successful"] = False
        
        return context
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Простая оценка условий.
        
        Поддерживаемые операторы: ==, !=, >, <, >=, <=, and, or, not, in
        """
        try:
            # Заменяем переменные из контекста
            for key, value in context.items():
                if isinstance(value, str):
                    condition = condition.replace(f"{key}", f'"{value}"')
                else:
                    condition = condition.replace(f"{key}", str(value))
            
            # ВНИМАНИЕ: eval небезопасен в продакшене!
            # Для продакшена нужно использовать безопасный парсер выражений
            return bool(eval(condition))
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка оценки условия '{condition}': {e}")
            return False
    
    async def healthcheck(self) -> bool:
        """Проверка здоровья плагина"""
        return True 