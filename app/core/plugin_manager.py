from typing import Dict, Any
from loguru import logger

class PluginBase:
    """Базовый класс для всех плагинов."""
    async def initialize(self, app: Any = None):
        """Опциональный метод для асинхронной инициализации плагина."""
        logger.info(f"Плагин {self.__class__.__name__} инициализирован (базовая реализация).")

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

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, PluginBase] = {}
        logger.info("PluginManager инициализирован.")

    def register_plugin(self, name: str, plugin_instance: PluginBase):
        if name in self.plugins:
            logger.warning(f"Плагин с именем '{name}' уже зарегистрирован. Перезапись.")
        self.plugins[name] = plugin_instance
        logger.info(f"Плагин '{name}' ({plugin_instance.__class__.__name__}) зарегистрирован.")

    def get_plugin(self, name: str) -> PluginBase | None:
        plugin = self.plugins.get(name)
        if not plugin:
            logger.warning(f"Запрошен плагин '{name}', но он не найден.")
        return plugin

    def get_all_plugins(self) -> Dict[str, PluginBase]:
        return self.plugins

    async def initialize_all_plugins(self, app: Any = None):
        logger.info("Начинается инициализация всех зарегистрированных плагинов...")
        for name, plugin in self.plugins.items():
            try:
                await plugin.initialize(app) # Передаем FastAPI app, если плагину это нужно
                logger.info(f"Плагин '{name}' успешно инициализирован.")
            except Exception as e:
                logger.error(f"Ошибка при инициализации плагина '{name}': {e}", exc_info=True)
        logger.info("Инициализация всех плагинов завершена.")

    def register_all_step_handlers(self, scenario_executor_step_handlers: Dict[str, callable]):
        """
        Собирает обработчики шагов от всех плагинов и регистрирует их
        в словаре обработчиков ScenarioExecutor.
        """
        logger.info("Регистрация обработчиков шагов от всех плагинов...")
        for name, plugin in self.plugins.items():
            try:
                # Убедимся, что передаем копию или что плагин не модифицирует напрямую
                # текущий словарь обработчиков ScenarioExecutor без контроля.
                # Лучше, чтобы плагин возвращал свои обработчики, а PM их мержил.
                # Но если register_step_handlers ожидает словарь для заполнения, то так:
                plugin.register_step_handlers(scenario_executor_step_handlers)
                # logger.debug(f"Обработчики от плагина '{name}' зарегистрированы.") # Может быть слишком много логов
            except Exception as e:
                logger.error(f"Ошибка при регистрации обработчиков шагов от плагина '{name}': {e}", exc_info=True)
        logger.info(f"Все обработчики шагов от плагинов зарегистрированы. Всего: {len(scenario_executor_step_handlers)}.")

    async def run_all_healthchecks(self) -> Dict[str, bool]:
        """
        Запускает healthcheck для всех плагинов, которые его реализуют.
        Возвращает словарь {plugin_name: status}.
        """
        health_statuses = {}
        logger.info("Запуск healthcheck для всех плагинов...")
        for name, plugin in self.plugins.items():
            try:
                status = await plugin.healthcheck()
                health_statuses[name] = status
                logger.debug(f"Healthcheck для плагина '{name}': {'OK' if status else 'FAIL'}")
            except Exception as e:
                logger.error(f"Ошибка при выполнении healthcheck для плагина '{name}': {e}", exc_info=True)
                health_statuses[name] = False
        logger.info(f"Healthcheck для всех плагинов завершен. Статусы: {health_statuses}")
        return health_statuses 