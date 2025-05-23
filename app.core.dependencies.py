from loguru import logger
logger.info("!!!!!!!!!!!!!!!!! APP/CORE/DEPENDENCIES.PY STARTED !!!!!!!!!!!!!!!!!!")

import os
from motor.motor_asyncio import AsyncIOMotorClient
from telegram.ext import Application as TelegramApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler

from app.utils.scheduler import SchedulerService
from app.plugins.telegram_plugin import TelegramPlugin
from app.plugins.mongo_storage_plugin import MongoStoragePlugin
from app.plugins.scheduling_plugin import SchedulingPlugin

# Добавляем импорты для ScenarioExecutor и его зависимостей
from app.core.scenario_executor import ScenarioExecutor
from app.db.scenario_repository import ScenarioRepository
from app.db.agent_repository import AgentRepository
from app.core.plugin_manager import PluginManager
# Предполагаем, что LLM и RAG плагины находятся здесь (путь может отличаться)
from app.plugins.llm_plugin import LLMPlugin
from app.plugins.rag_plugin import RAGPlugin

# --- Конфигурация ---
MONGO_URI = os.getenv("MONGO_URI", os.getenv("MONGO_URL", "mongodb://mongo:27017/"))
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "universal_agent_platform")
API_BASE_URL = os.getenv("API_URL", "http://app:8000")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

logger.critical(f"[DEPENDENCIES_CONFIG_CHECK] MONGO_URI: '{MONGO_URI}', DB_NAME: '{MONGODB_DATABASE_NAME}', API_BASE_URL: '{API_BASE_URL}'")

# --- Инициализация Клиента MongoDB ---
db_client = None
# ... остальной код ... 