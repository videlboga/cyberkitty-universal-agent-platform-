"""
Базовый класс для всех плагинов в упрощенной архитектуре Universal Agent Platform.
Принцип: Простота превыше всего!
"""

from abc import ABC, abstractmethod
from typing import Dict, Callable, Any, Optional
from loguru import logger
import re


class BasePlugin(ABC):
    """
    Базовый класс для всех плагинов.
    
    Каждый плагин должен:
    1. Наследовать этот класс
    2. Реализовать register_handlers() - возвращает словарь обработчиков
    3. Реализовать healthcheck() - проверка состояния плагина
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger.bind(plugin=name)
        self._initialized = False
        
    @abstractmethod
    def register_handlers(self) -> Dict[str, Callable]:
        """
        Регистрирует обработчики шагов сценария.
        
        Returns:
            Dict[str, Callable]: Словарь {step_type: handler_function}
            
        Example:
            {
                "telegram_send_message": self.handle_send_message,
                "mongo_save": self.handle_save_data,
                "switch_scenario": self.handle_switch_scenario
            }
        """
        pass
        
    @abstractmethod
    async def healthcheck(self) -> bool:
        """
        Проверяет здоровье плагина.
        
        Returns:
            bool: True если плагин работает, False если есть проблемы
        """
        pass
        
    async def initialize(self) -> bool:
        """
        Опциональная инициализация плагина.
        Вызывается один раз при регистрации в движке.
        
        Returns:
            bool: True если инициализация успешна
        """
        if self._initialized:
            return True
            
        try:
            await self._do_initialize()
            self._initialized = True
            self.logger.info(f"Плагин {self.name} инициализирован")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации плагина {self.name}: {e}")
            return False
            
    async def _do_initialize(self):
        """
        Переопределите этот метод для кастомной инициализации.
        По умолчанию ничего не делает.
        """
        pass
        
    async def handle_step(self, step_type: str, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обрабатывает шаг сценария.
        
        Args:
            step_type: Тип шага (например, "telegram_send_message")
            step: Данные шага из сценария
            context: Контекст выполнения
            
        Returns:
            Dict[str, Any]: Обновленный контекст
            
        Raises:
            ValueError: Если тип шага не поддерживается
        """
        handlers = self.register_handlers()
        
        if step_type not in handlers:
            raise ValueError(f"Plugin {self.name} не поддерживает тип шага: {step_type}")
            
        handler = handlers[step_type]
        self.logger.info(f"Обрабатываю шаг {step_type}", step_id=step.get('id'), plugin=self.name)
        
        try:
            result = await handler(step, context)
            self.logger.info(f"Шаг {step_type} выполнен успешно", step_id=step.get('id'))
            return result if result else context
        except Exception as e:
            self.logger.error(f"Ошибка в обработке шага {step_type}: {e}", step_id=step.get('id'))
            raise
            
    # === УТИЛИТЫ ДЛЯ ПЛАГИНОВ ===
    
    def resolve_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Простая подстановка переменных в шаблоне.
        
        Поддерживает:
        - {variable} - простая подстановка
        - {user.name} - вложенные поля
        - {items.0} - элементы массива
        
        Args:
            template: Шаблон строки с переменными
            context: Контекст с данными
            
        Returns:
            str: Строка с подставленными значениями
        """
        if not isinstance(template, str):
            return str(template)
            
        # Ищем все переменные в фигурных скобках
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, template)
        
        result = template
        for match in matches:
            try:
                value = self._get_nested_value(context, match)
                result = result.replace(f'{{{match}}}', str(value))
            except (KeyError, IndexError, TypeError):
                self.logger.warning(f"Не удалось разрешить переменную: {match}")
                # Оставляем переменную как есть
                
        return result
        
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """
        Получает значение по вложенному пути.
        
        Args:
            data: Словарь с данными
            path: Путь к значению (например, "user.name" или "items.0")
            
        Returns:
            Any: Найденное значение
            
        Raises:
            KeyError: Если путь не найден
        """
        parts = path.split('.')
        current = data
        
        for part in parts:
            if isinstance(current, dict):
                current = current[part]
            elif isinstance(current, list):
                index = int(part)
                current = current[index]
            else:
                raise KeyError(f"Невозможно получить {part} из {type(current)}")
                
        return current
        
    def get_param(self, step: Dict[str, Any], param_name: str, default: Any = None, required: bool = False) -> Any:
        """
        Безопасно получает параметр из шага.
        
        Args:
            step: Данные шага
            param_name: Имя параметра
            default: Значение по умолчанию
            required: Обязательный ли параметр
            
        Returns:
            Any: Значение параметра
            
        Raises:
            ValueError: Если обязательный параметр отсутствует
        """
        params = step.get('params', {})
        
        if param_name not in params:
            if required:
                raise ValueError(f"Обязательный параметр '{param_name}' отсутствует в шаге {step.get('id')}")
            return default
            
        return params[param_name]
        
    def update_context(self, context: Dict[str, Any], updates: Dict[str, Any], prefix: str = None) -> Dict[str, Any]:
        """
        Безопасно обновляет контекст.
        
        Args:
            context: Исходный контекст
            updates: Обновления
            prefix: Префикс для ключей (например, "telegram_")
            
        Returns:
            Dict[str, Any]: Обновленный контекст
        """
        result = context.copy()
        
        for key, value in updates.items():
            final_key = f"{prefix}{key}" if prefix else key
            result[final_key] = value
            
        return result
        
    def validate_required_params(self, step: Dict[str, Any], required_params: list) -> None:
        """
        Проверяет наличие обязательных параметров в шаге.
        
        Args:
            step: Данные шага
            required_params: Список обязательных параметров
            
        Raises:
            ValueError: Если какой-то параметр отсутствует
        """
        params = step.get('params', {})
        missing = []
        
        for param in required_params:
            if param not in params:
                missing.append(param)
                
        if missing:
            raise ValueError(
                f"Отсутствуют обязательные параметры в шаге {step.get('id')}: {missing}"
            )
            
    def log_step_start(self, step: Dict[str, Any], extra_info: Dict[str, Any] = None):
        """Логирует начало выполнения шага."""
        info = {
            "step_id": step.get('id'),
            "step_type": step.get('type'),
            "plugin": self.name
        }
        if extra_info:
            info.update(extra_info)
            
        self.logger.info("Начинаю выполнение шага", **info)
        
    def log_step_success(self, step: Dict[str, Any], result: Any = None):
        """Логирует успешное выполнение шага."""
        info = {
            "step_id": step.get('id'),
            "step_type": step.get('type'),
            "plugin": self.name
        }
        if result:
            info["result"] = str(result)[:100]  # Ограничиваем длину лога
            
        self.logger.info("Шаг выполнен успешно", **info)
        
    def log_step_error(self, step: Dict[str, Any], error: Exception):
        """Логирует ошибку выполнения шага."""
        self.logger.error(
            f"Ошибка выполнения шага {step.get('id')}: {error}",
            step_id=step.get('id'),
            step_type=step.get('type'),
            plugin=self.name,
            error=str(error)
        )
        
    def __str__(self):
        return f"<{self.__class__.__name__}:{self.name}>"
        
    def __repr__(self):
        return self.__str__() 