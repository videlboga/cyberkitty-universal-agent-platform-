from dotenv import load_dotenv
import os

# Определяем путь к файлу .env или .env.local в корне проекта
# (app/main.py -> app/ -> корень)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_local_path = os.path.join(project_root, '.env.local')
dotenv_path = os.path.join(project_root, '.env')

loaded_from = None
if os.path.exists(dotenv_local_path):
    load_dotenv(dotenv_path=dotenv_local_path)
    loaded_from = dotenv_local_path
elif os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path) # load_dotenv также может просто искать .env по умолчанию
    loaded_from = dotenv_path

if loaded_from:
    print(f"Loaded environment variables from: {loaded_from}")
else:
    print("No .env or .env.local file found in project root. Using system environment variables and defaults.")

from fastapi import FastAPI
from loguru import logger
from app.api.user import router as user_router
from app.api.scenario import router as scenario_router
from app.api.integration import router as integration_router
from app.api.runner import router as runner_router
from app.api.agent import router as agent_router
from app.api.collection import router as collection_router
from app.api.learning import router as learning_router
from app.api.scheduler_updated import router as scheduler_router
import threading
import logging
import asyncio
from typing import Optional

# Импортируем глобальные экземпляры сервисов из app.core.dependencies
from app.core.dependencies import scheduler_service, telegram_app_instance, telegram_plugin
# Если ScenarioExecutor нужен в bot_data, его нужно будет создать здесь и передать.
# Это может потребовать доступа к репозиториям и другим зависимостям, что усложняет startup.
# Альтернатива: command handlers в telegram_plugin получают ScenarioExecutor через Depends.

# Настройка логирования loguru
os.makedirs("logs", exist_ok=True)
logger.add("logs/api.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

app = FastAPI(title="Universal Agent Platform API", description="API универсальной платформы ИИ-агентов", version="0.1.0")

# --- Переменные для управления фоновыми задачами Telegram ---
telegram_polling_task: Optional[asyncio.Task] = None
stop_telegram_polling_event = asyncio.Event()

async def run_telegram_polling():
    """Асинхронная задача для запуска polling Telegram бота."""
    if not telegram_app_instance:
        logger.warning("Telegram App instance (telegram_app_instance) не инициализирован, polling не будет запущен.")
        return
    
    # Если ScenarioExecutor нужно добавить в bot_data, это можно сделать здесь перед запуском.
    # Например, если бы у нас был способ создать его без FastAPI Depends:
    # from app.db.database import get_db_session # Пример
    # async with get_db_session() as db:
    #     user_repo = UserRepository(db)
    #     agent_repo = AgentRepository(db)
    #     scenario_repo = ScenarioRepository(db)
    #     plugins = { # Собрать нужные плагины
    #         "telegram": telegram_plugin, 
    #         "scheduling": scheduling_plugin, 
    #         "mongo_storage": mongo_storage_plugin
    #     }
    #     # executor = ScenarioExecutor(scenario_repository=scenario_repo, agent_repository=agent_repo, user_repository=user_repo, plugins=plugins, user_id="system_startup")
    #     # telegram_app_instance.bot_data["scenario_executor"] = executor
    # logger.info("ScenarioExecutor (если создан) добавлен в telegram_app_instance.bot_data")
    # Это сложный паттерн для startup, обычно executor получают через Depends в обработчиках.

    try:
        logger.info("Starting Telegram bot polling...")
        await telegram_app_instance.initialize() 
        # Убедимся, что updater существует перед вызовом start_polling
        if telegram_app_instance.updater:
            await telegram_app_instance.updater.start_polling(drop_pending_updates=True)
            logger.info("Telegram bot polling started.")
            await stop_telegram_polling_event.wait() # Ожидаем сигнала на остановку
        else:
            logger.error("Telegram updater is not available, polling cannot start.")
    except Exception as e:
        logger.error(f"Error in Telegram polling: {e}", exc_info=True)
    finally:
        if telegram_app_instance and telegram_app_instance.updater and telegram_app_instance.updater.running:
            logger.info("Stopping Telegram bot polling...")
            await telegram_app_instance.updater.stop()
        if telegram_app_instance:
            await telegram_app_instance.shutdown() 
        logger.info("Telegram Application shutdown sequence complete.")

@app.on_event("startup")
async def startup_event():
    """Запуск фоновых задач при старте приложения"""
    global telegram_polling_task
    logger.info("Application startup event commencing.")
    try:
        if scheduler_service:
            await scheduler_service.start()
            logger.info("Scheduler service started successfully.")
        else:
            logger.warning("Scheduler service is not available, not starting.")
        
        if telegram_app_instance:
            stop_telegram_polling_event.clear()
            telegram_polling_task = asyncio.create_task(run_telegram_polling())
            logger.info("Telegram polling task created and started.")
        else:
            logger.warning("Telegram App instance (telegram_app_instance) is not available, Telegram polling not started.")
            
    except Exception as e:
        logger.error(f"Error during application startup: {e}", exc_info=True)

@app.on_event("shutdown")
async def shutdown_event():
    """Остановка фоновых задач при остановке приложения"""
    global telegram_polling_task
    logger.info("Application shutdown event commencing.")
    try:
        if telegram_polling_task and not telegram_polling_task.done():
            logger.info("Signaling Telegram polling task to stop...")
            stop_telegram_polling_event.set()
            try:
                await asyncio.wait_for(telegram_polling_task, timeout=10.0) 
                logger.info("Telegram polling task finished gracefully.")
            except asyncio.TimeoutError:
                logger.warning("Telegram polling task did not stop gracefully within timeout, cancelling.")
                telegram_polling_task.cancel()
            except Exception as e:
                logger.error(f"Error while waiting for Telegram polling task to stop: {e}", exc_info=True)
        
        if scheduler_service and scheduler_service.scheduler_running:
            await scheduler_service.stop()
            logger.info("Scheduler service stopped successfully.")
        elif scheduler_service:
            logger.info("Scheduler service was available but not running.")
        else:
            logger.warning("Scheduler service was not available during shutdown.")
            
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}", exc_info=True)

@app.get("/health", tags=["health"])
def health():
    """Healthcheck endpoint для проверки статуса сервиса.
    
    Returns:
        dict: Статус сервиса
    """
    logger.info("Healthcheck requested")
    return {"status": "ok"}

app.include_router(user_router)
app.include_router(scenario_router)
app.include_router(integration_router)
app.include_router(runner_router)
app.include_router(agent_router)
app.include_router(collection_router)
app.include_router(learning_router)
app.include_router(scheduler_router) 