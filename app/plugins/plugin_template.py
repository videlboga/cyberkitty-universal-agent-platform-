"""
ШАБЛОН ПЛАГИНА для Universal Agent Platform.

Скопируйте этот файл и адаптируйте под свои нужды.
Следуйте принципу: Простота превыше всего!

Пример использования:
1. Скопируйте файл: cp plugin_template.py my_plugin.py
2. Замените TemplatePlugin на MyPlugin
3. Реализуйте нужные обработчики
4. Зарегистрируйте в движке
"""

from typing import Dict, Callable, Any
from app.core.base_plugin import BasePlugin


class TemplatePlugin(BasePlugin):
    """
    Шаблон плагина - замените на свой класс.
    
    Этот плагин демонстрирует:
    - Как регистрировать обработчики шагов
    - Как использовать утилиты BasePlugin
    - Как правильно логировать
    - Как обрабатывать ошибки
    """
    
    def __init__(self):
        # ВАЖНО: передайте уникальное имя плагина
        super().__init__("template_plugin")
        
        # Здесь можете инициализировать свои переменные
        self.some_config = "default_value"
        
    async def _do_initialize(self):
        """
        Опциональная инициализация плагина.
        Вызывается один раз при регистрации в движке.
        """
        # Здесь можете:
        # - Подключиться к внешним сервисам
        # - Загрузить конфигурацию
        # - Проверить зависимости
        
        self.logger.info("Инициализация TemplatePlugin")
        
        # Пример проверки конфигурации
        if not self.some_config:
            raise ValueError("some_config не может быть пустым")
            
    def register_handlers(self) -> Dict[str, Callable]:
        """
        Регистрирует обработчики шагов сценария.
        
        Returns:
            Dict[str, Callable]: Словарь {step_type: handler_function}
        """
        return {
            # Замените на свои типы шагов и обработчики
            "template_action": self.handle_template_action,
            "template_send": self.handle_template_send,
            "template_process": self.handle_template_process,
        }
        
    async def healthcheck(self) -> bool:
        """
        Проверяет здоровье плагина.
        
        Returns:
            bool: True если плагин работает
        """
        try:
            # Здесь проверьте:
            # - Доступность внешних сервисов
            # - Валидность конфигурации
            # - Состояние соединений
            
            # Пример простой проверки
            if not self.some_config:
                return False
                
            self.logger.debug("TemplatePlugin healthcheck passed")
            return True
            
        except Exception as e:
            self.logger.error(f"TemplatePlugin healthcheck failed: {e}")
            return False
            
    # === ОБРАБОТЧИКИ ШАГОВ ===
    
    async def handle_template_action(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага 'template_action'.
        
        Пример шага в сценарии:
        {
            "id": "action1",
            "type": "template_action",
            "params": {
                "message": "Hello {user.name}!",
                "target": "console"
            }
        }
        """
        self.log_step_start(step)
        
        try:
            # Получаем параметры с валидацией
            message = self.get_param(step, "message", required=True)
            target = self.get_param(step, "target", default="console")
            
            # Подставляем переменные из контекста
            resolved_message = self.resolve_template(message, context)
            
            # Выполняем действие
            if target == "console":
                print(f"[TemplatePlugin] {resolved_message}")
            else:
                self.logger.info(f"Отправка сообщения: {resolved_message}")
                
            # Обновляем контекст
            updates = {
                "last_message": resolved_message,
                "action_completed": True
            }
            
            result = self.update_context(context, updates, prefix="template_")
            
            self.log_step_success(step, resolved_message)
            return result
            
        except Exception as e:
            self.log_step_error(step, e)
            raise
            
    async def handle_template_send(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага 'template_send'.
        
        Пример более сложного обработчика с валидацией.
        """
        self.log_step_start(step)
        
        try:
            # Валидируем обязательные параметры
            self.validate_required_params(step, ["recipient", "content"])
            
            recipient = self.get_param(step, "recipient")
            content = self.get_param(step, "content")
            priority = self.get_param(step, "priority", default="normal")
            
            # Подставляем переменные
            resolved_content = self.resolve_template(content, context)
            
            # Симуляция отправки
            self.logger.info(
                f"Отправка сообщения",
                recipient=recipient,
                content=resolved_content[:50],
                priority=priority
            )
            
            # Обновляем контекст
            result = self.update_context(context, {
                "sent_to": recipient,
                "sent_content": resolved_content,
                "sent_at": "2024-01-01T12:00:00Z"  # В реальности используйте datetime.now()
            }, prefix="template_")
            
            self.log_step_success(step, f"Sent to {recipient}")
            return result
            
        except Exception as e:
            self.log_step_error(step, e)
            raise
            
    async def handle_template_process(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага 'template_process'.
        
        Пример обработки данных из контекста.
        """
        self.log_step_start(step)
        
        try:
            # Получаем данные для обработки
            input_data = self.get_param(step, "input_data")
            operation = self.get_param(step, "operation", default="count")
            
            # Если input_data это путь в контексте - получаем значение
            if isinstance(input_data, str) and input_data.startswith("{") and input_data.endswith("}"):
                path = input_data[1:-1]  # Убираем скобки
                try:
                    actual_data = self._get_nested_value(context, path)
                except KeyError:
                    actual_data = []
            else:
                actual_data = input_data or []
                
            # Выполняем операцию
            if operation == "count":
                result_value = len(actual_data) if hasattr(actual_data, '__len__') else 0
            elif operation == "sum" and isinstance(actual_data, list):
                result_value = sum(x for x in actual_data if isinstance(x, (int, float)))
            else:
                result_value = str(actual_data)
                
            # Обновляем контекст
            result = self.update_context(context, {
                "processed_data": actual_data,
                "operation": operation,
                "result": result_value
            }, prefix="template_")
            
            self.log_step_success(step, f"Operation {operation} = {result_value}")
            return result
            
        except Exception as e:
            self.log_step_error(step, e)
            raise


# === ПРИМЕР ИСПОЛЬЗОВАНИЯ ===

async def example_usage():
    """Пример использования TemplatePlugin."""
    from app.core.simple_engine import SimpleScenarioEngine
    
    # Создаем движок
    engine = SimpleScenarioEngine()
    
    # Создаем и регистрируем плагин
    plugin = TemplatePlugin()
    engine.register_plugin(plugin)
    
    # Пример сценария
    scenario = {
        "scenario_id": "template_demo",
        "steps": [
            {
                "id": "start",
                "type": "start",
                "next_step": "action1"
            },
            {
                "id": "action1", 
                "type": "template_action",
                "params": {
                    "message": "Привет, {user_name}!",
                    "target": "console"
                },
                "next_step": "send1"
            },
            {
                "id": "send1",
                "type": "template_send", 
                "params": {
                    "recipient": "{user_email}",
                    "content": "Ваш заказ #{order_id} готов!",
                    "priority": "high"
                },
                "next_step": "end"
            },
            {
                "id": "end",
                "type": "end"
            }
        ]
    }
    
    # Контекст
    context = {
        "user_name": "Иван",
        "user_email": "ivan@example.com", 
        "order_id": "12345"
    }
    
    # Выполняем сценарий
    result = await engine.execute_scenario(scenario, context)
    print("Результат:", result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage()) 