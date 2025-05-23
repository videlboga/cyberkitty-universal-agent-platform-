from loguru import logger
logger.info("!!!!!!!!!!!!!!!!! APP/CORE/DEPENDENCIES.PY STARTED !!!!!!!!!!!!!!!!!!")

import os
from motor.motor_asyncio import AsyncIOMotorClient
from telegram.ext import Application as TelegramApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler
from pymongo import MongoClient

from app.utils.scheduler import SchedulerService
from app.plugins.telegram_plugin import TelegramPlugin
from app.plugins.mongo_storage_plugin import MongoStoragePlugin
# from app.plugins.scheduling_plugin import SchedulingPlugin

# Добавляем импорты для ScenarioExecutor и его зависимостей
from app.core.scenario_executor import ScenarioExecutor
from app.db.scenario_repository import ScenarioRepository
from app.db.agent_repository import AgentRepository
from app.core.plugin_manager import PluginManager
# Предполагаем, что LLM и RAG плагины находятся здесь (путь может отличаться)
from app.plugins.llm_plugin import LLMPlugin
from app.plugins.rag_plugin import RAGPlugin
# Новые плагины
from app.plugins.scheduler_plugin import SchedulerPlugin
from app.plugins.orchestrator_plugin import OrchestratorPlugin

# --- Конфигурация ---
MONGO_URI = os.getenv("MONGO_URI", os.getenv("MONGO_URL", "mongodb://mongo:27017/"))
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "universal_agent_platform")
API_BASE_URL = os.getenv("API_URL", "http://app:8000")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# --- Инициализация Клиента MongoDB ---
db_client = None
db = None
try:
    db_client = AsyncIOMotorClient(MONGO_URI)
    db = db_client[MONGODB_DATABASE_NAME]
    logger.info(f"Core Dependencies: MongoDB клиент инициализирован для базы '{MONGODB_DATABASE_NAME}'.")
except Exception as e:
    logger.error(f"Core Dependencies: Ошибка инициализации MongoDB клиента: {e}", exc_info=True)
    # Приложение, вероятно, не сможет работать без БД, но позволяем остальным зависимостям попытаться инициализироваться.

# --- Инициализация SchedulerService ---
# try:
#     scheduler_service = SchedulerService(
#         mongo_uri=MONGO_URI, 
#         api_base_url=API_BASE_URL
#     )
#     logger.info("Core Dependencies: SchedulerService инициализирован.")
# except Exception as e:
#     logger.error(f"Core Dependencies: Ошибка инициализации SchedulerService: {e}", exc_info=True)
#     scheduler_service = None

# --- Инициализация MongoStoragePlugin ---
mongo_async_client = AsyncIOMotorClient(MONGO_URI)
try:
    mongo_storage_plugin = MongoStoragePlugin(
        mongo_async_client,
        db_name=MONGODB_DATABASE_NAME
    )
    logger.info("Core Dependencies: MongoStoragePlugin инициализирован.")
except Exception as e:
    logger.error(f"Core Dependencies: Ошибка инициализации MongoStoragePlugin: {e}", exc_info=True)
    mongo_storage_plugin = None

# --- Инициализация SchedulingPlugin ---
# if scheduler_service:
#     try:
#         scheduling_plugin = SchedulingPlugin(scheduler_service=scheduler_service)
#         logger.info("Core Dependencies: SchedulingPlugin инициализирован.")
#     except Exception as e:
#         logger.error(f"Core Dependencies: Ошибка инициализации SchedulingPlugin: {e}", exc_info=True)
#         scheduling_plugin = None
# else:
#     scheduling_plugin = None
#     logger.warning("Core Dependencies: SchedulingPlugin не инициализирован, так как scheduler_service отсутствует.")

# --- Инициализация Telegram ---
telegram_app_instance = None
telegram_plugin = None

if not TELEGRAM_BOT_TOKEN:
    logger.warning("Core Dependencies: TELEGRAM_BOT_TOKEN не найден. Telegram интеграция будет неактивна.")
else:
    try:
        # !!!!! ВАЖНОЕ ИЗМЕНЕНИЕ !!!!!
        # Поскольку TelegramApplicationBuilder это Application, мы можем установить DEFAULT_SHUTDOWN_SIGNALS для него.
        # Это должно предотвратить регистрацию обработчиков сигналов, которые вызывают проблемы в потоках.
        TelegramApplicationBuilder.DEFAULT_SHUTDOWN_SIGNALS = []
        logger.info("Core Dependencies: TelegramApplicationBuilder.DEFAULT_SHUTDOWN_SIGNALS установлен в [].")
        # !!!!! КОНЕЦ ВАЖНОГО ИЗМЕНЕНИЯ !!!!!

        telegram_app_builder = TelegramApplicationBuilder.builder().token(TELEGRAM_BOT_TOKEN)
        telegram_app_instance = telegram_app_builder.build()
        telegram_app_instance.bot_data = {} 
        
        telegram_plugin = TelegramPlugin(app=telegram_app_instance)
        logger.info("Core Dependencies: Telegram Application instance и TelegramPlugin успешно инициализированы.")

    except Exception as e:
        logger.error(f"Core Dependencies: Ошибка инициализации Telegram: {e}", exc_info=True)
        # telegram_app_instance и telegram_plugin останутся None

# --- Инициализация RAG и LLM плагинов ---
rag_plugin_instance = RAGPlugin()
llm_plugin_instance = LLMPlugin()

# --- Инициализация новых плагинов ---
scheduler_plugin_instance = SchedulerPlugin()
orchestrator_plugin_instance = OrchestratorPlugin()
logger.info("Core Dependencies: SchedulerPlugin и OrchestratorPlugin инициализированы.")

# --- Инициализация Repositories ---
scenario_repo_instance = None
agent_repo_instance = None
if db is not None: # ИСПРАВЛЕНО: Используем 'is not None' для проверки объекта БД
    try:
        scenario_repo_instance = ScenarioRepository(db)
        agent_repo_instance = AgentRepository(db)
        logger.info("Core Dependencies: ScenarioRepository и AgentRepository инициализированы.")
    except Exception as e:
        logger.error(f"Core Dependencies: Ошибка инициализации репозиториев: {e}", exc_info=True)

# --- Инициализация PluginManager ---
# plugin_manager_instance = None
# if telegram_plugin and mongo_storage_plugin and scheduling_plugin: # и другие обязательные плагины
#     try:
#         plugin_manager_instance = PluginManager()
#         plugin_manager_instance.register_plugin("telegram", telegram_plugin)
#         plugin_manager_instance.register_plugin("mongo_storage", mongo_storage_plugin)
#         plugin_manager_instance.register_plugin("scheduler", scheduling_plugin)
#         plugin_manager_instance.register_plugin("llm", llm_plugin_instance)
#         plugin_manager_instance.register_plugin("rag", rag_plugin_instance)
#         logger.info("Core Dependencies: PluginManager инициализирован и плагины зарегистрированы.")
#     except Exception as e:
#         logger.error(f"Core Dependencies: Ошибка инициализации PluginManager: {e}", exc_info=True)

# --- Инициализация ScenarioExecutor ---
scenario_executor_instance = None
if scenario_repo_instance and agent_repo_instance: 
    try:
        # Собираем список плагинов для ScenarioExecutor
        plugins_list = []
        if telegram_plugin:
            plugins_list.append(telegram_plugin)
        if mongo_storage_plugin:
            plugins_list.append(mongo_storage_plugin)
        if llm_plugin_instance:
            plugins_list.append(llm_plugin_instance)
        if rag_plugin_instance:
            plugins_list.append(rag_plugin_instance)
        if scheduler_plugin_instance:
            plugins_list.append(scheduler_plugin_instance)
        if orchestrator_plugin_instance:
            plugins_list.append(orchestrator_plugin_instance)
        
        scenario_executor_instance = ScenarioExecutor(plugins=plugins_list, scenario_repo=scenario_repo_instance)
        logger.info(f"ScenarioExecutor instance created successfully in dependencies: id(self)={id(scenario_executor_instance)}")
        logger.info(f"Plugins registered: {[p.__class__.__name__ for p in plugins_list]}")
        logger.info(f"Step handlers available: {list(scenario_executor_instance.step_handlers.keys())}")

        # !!! КЛЮЧЕВОЙ МОМЕНТ: Добавляем scenario_executor в bot_data Telegram !!!
        if telegram_app_instance:
            telegram_app_instance.bot_data["scenario_executor"] = scenario_executor_instance
            logger.info("Core Dependencies: scenario_executor_instance добавлен в telegram_app_instance.bot_data.")
        else:
            logger.warning("Core Dependencies: telegram_app_instance отсутствует, не удалось добавить scenario_executor в bot_data.")

        if telegram_plugin and telegram_app_instance: # Доп. проверка, хотя выше они должны быть созданы
            logger.info(f"Core Dependencies: Попытка вызова add_handlers() для telegram_plugin (id: {id(telegram_plugin)}) на telegram_app_instance (id: {id(telegram_app_instance)}).")
            telegram_plugin.add_handlers() # Это должно добавить CallbackQueryHandler и другие
            logger.info(f"Core Dependencies: add_handlers() для telegram_plugin ВЫЗВАН. Проверяем зарегистрированные обработчики...")
            if telegram_app_instance.handlers:
                for group, group_handlers in telegram_app_instance.handlers.items():
                    logger.info(f"Core Dependencies: Telegram Handler Group {group}:")
                    for i, handler in enumerate(group_handlers):
                        logger.info(f"Core Dependencies:   - Handler {i}: {handler} (type: {type(handler)})")
                        if hasattr(handler, 'callback'):
                            logger.info(f"Core Dependencies:     - Callback: {handler.callback}")
                        if isinstance(handler, CallbackQueryHandler):
                            logger.info(f"Core Dependencies:     - CallbackQueryHandler specific: pattern={handler.pattern if hasattr(handler, 'pattern') else 'N/A'}")
                        elif isinstance(handler, MessageHandler):
                            logger.info(f"Core Dependencies:     - MessageHandler specific: filters={handler.filters}")
                        elif isinstance(handler, CommandHandler):
                            logger.info(f"Core Dependencies:     - CommandHandler specific: commands={handler.commands}")

            else:
                logger.warning("Core Dependencies: telegram_app_instance.handlers пуст или отсутствует после вызова add_handlers!")

    except Exception as e:
        logger.error(f"Core Dependencies: Ошибка инициализации ScenarioExecutor: {e}", exc_info=True)

logger.info("app.core.dependencies загружен и инициализировал сервисы.") 