from typing import Dict, Any
from loguru import logger

class PluginBase:
    """Базовый класс для всех плагинов."""
    async def initialize(self, app: Any = None):
        """Опциональный метод для асинхронной инициализации плагина."""
        logger.info(f"PluginBase_INITIALIZE_CALLED_VERSION_PLUGIN_BASE_FILE для плагина {self.__class__.__name__}.")

    def register_step_handlers(self, step_handlers: Dict[str, callable]):
        """
        Метод для регистрации обработчиков шагов, которые предоставляет плагин.
        Ключ - тип шага, значение - асинхронная функция-обработчик.
        """
        pass # Реализуется в дочерних классах

    async def healthcheck(self) -> bool:
        """
        Опциональный метод для проверки работоспособности плагина.
        Должен возвращать True, если плагин работает корректно, иначе False.
        """
        return True # По умолчанию плагин считается рабочим 