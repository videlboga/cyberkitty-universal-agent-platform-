import os
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from telegram.ext import Application as TelegramApplicationBuilder

from app.utils.scheduler import SchedulerService
from app.plugins.telegram_plugin import TelegramPlugin
from app.plugins.mongo_storage_plugin import MongoStoragePlugin
from app.plugins.scheduling_plugin import SchedulingPlugin

# --- Конфигурация ---
MONGO_URI = os.getenv("MONGO_URL", "mongodb://mongo:27017/") # В integration.py было MONGO_URL, здесь MONGO_URI. Приводим к одному.
# Используем MONGO_URI как приоритетный, если он есть, иначе MONGO_URL
MONGO_URI = os.getenv("MONGO_URI", os.getenv("MONGO_URL", "mongodb://mongo:27017/"))

MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "universal_agent_platform")
# Используем API_URL из окружения, как и в scheduler.py, с дефолтом http://app:8000
API_BASE_URL = os.getenv("API_URL", "http://app:8000")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# --- Инициализация Клиента MongoDB ---
# Этот клиент может быть не нужен здесь, если репозитории получают db напрямую или через Depends
# db_client = AsyncIOMotorClient(MONGO_URI)
# db = db_client[MONGODB_DATABASE_NAME]

# --- Инициализация SchedulerService ---
# SchedulerService требует mongo_uri и api_base_url при инициализации, если его конструктор был изменен.
# Если он все еще SchedulerService(), то параметры по умолчанию.
# Судя по app/api/scheduler_updated.py, он инициализируется как SchedulerService()
# Судя по app/utils/scheduler.py, конструктор __init__(self, mongo_uri: str, db_name: str = "uasp_db", api_base_url: str = "http://localhost:8000", ...)
# Значит, нужно передавать параметры.
try:
    # Важно: Убедимся, что SchedulerService получает правильные параметры для подключения к MongoDB
    # которые используются внутри него для коллекции scheduled_tasks.
    scheduler_service = SchedulerService(
        mongo_uri=MONGO_URI, 
        api_base_url=API_BASE_URL
    )
    logger.info("Core Dependencies: SchedulerService инициализирован.")
except Exception as e:
    logger.error(f"Core Dependencies: Ошибка инициализации SchedulerService: {e}", exc_info=True)
    scheduler_service = None

# --- Инициализация MongoStoragePlugin ---
try:
    mongo_storage_plugin = MongoStoragePlugin(mongo_uri=MONGO_URI, database_name=MONGODB_DATABASE_NAME)
    logger.info("Core Dependencies: MongoStoragePlugin инициализирован.")
except Exception as e:
    logger.error(f"Core Dependencies: Ошибка инициализации MongoStoragePlugin: {e}", exc_info=True)
    mongo_storage_plugin = None

# --- Инициализация SchedulingPlugin ---
if scheduler_service:
    try:
        scheduling_plugin = SchedulingPlugin(scheduler_service=scheduler_service)
        logger.info("Core Dependencies: SchedulingPlugin инициализирован.")
    except Exception as e:
        logger.error(f"Core Dependencies: Ошибка инициализации SchedulingPlugin: {e}", exc_info=True)
        scheduling_plugin = None
else:
    scheduling_plugin = None
    logger.warning("Core Dependencies: SchedulingPlugin не инициализирован, так как scheduler_service отсутствует.")

# --- Инициализация Telegram ---
telegram_app_instance = None
telegram_plugin = None

if not TELEGRAM_BOT_TOKEN:
    logger.warning("Core Dependencies: TELEGRAM_BOT_TOKEN не найден. Telegram интеграция будет неактивна.")
else:
    try:
        telegram_app_builder = TelegramApplicationBuilder.builder().token(TELEGRAM_BOT_TOKEN)
        telegram_app_instance = telegram_app_builder.build()
        # bot_data можно будет заполнить позже, например, в main.py startup event, если там нужен ScenarioExecutor
        telegram_app_instance.bot_data = {} 
        
        telegram_plugin = TelegramPlugin(app=telegram_app_instance)
        logger.info("Core Dependencies: Telegram Application instance и TelegramPlugin успешно инициализированы.")
    except Exception as e:
        logger.error(f"Core Dependencies: Ошибка инициализации Telegram: {e}", exc_info=True)
        # telegram_app_instance и telegram_plugin останутся None

# --- Другие глобальные плагины/сервисы при необходимости ---
# Например, NewsPlugin, RAGPlugin из integration.py
# from app.plugins.news_plugin import NewsPlugin
# from app.plugins.rag_plugin import RAGPlugin
# news_plugin = NewsPlugin()
# rag_plugin = RAGPlugin()
# logger.info("Core Dependencies: NewsPlugin and RAGPlugin initialized.")

logger.info("app.core.dependencies загружен и инициализировал сервисы.") 