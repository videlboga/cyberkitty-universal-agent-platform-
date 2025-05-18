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
from app.api.integration import router as integration_router, telegram_app
from app.api.runner import router as runner_router
from app.api.agent import router as agent_router
from app.api.collection import router as collection_router
from app.api.learning import router as learning_router
from app.api.scheduler_updated import router as scheduler_router, scheduler_service
import threading
import logging
import asyncio

# Настройка логирования loguru
os.makedirs("logs", exist_ok=True)
logger.add("logs/api.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

app = FastAPI(title="Universal Agent Platform API", description="API универсальной платформы ИИ-агентов", version="0.1.0")

# --- Переменная для хранения потока Telegram ---
telegram_polling_thread = None
# --- Конец переменной для хранения потока Telegram ---

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

@app.on_event("startup")
async def startup_event():
    """Запуск фоновых задач при старте приложения"""
    # global telegram_polling_thread # Больше не нужен здесь
    try:
        # Запуск планировщика задач
        await scheduler_service.start()
        logger.info("Планировщик задач успешно запущен при старте приложения")
    except Exception as e:
        logger.error(f"Ошибка при запуске планировщика задач: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Остановка фоновых задач при остановке приложения"""
    # global telegram_polling_thread # Больше не нужен здесь
    try:
        # Остановка планировщика задач
        await scheduler_service.stop()
        logger.info("Планировщик задач успешно остановлен при остановке приложения")
    except Exception as e:
        logger.error(f"Ошибка при остановке планировщика задач: {e}")

# Удалён запуск polling Telegram-бота из main.py (старый комментарий, актуализировано выше) 
# Также удаляем функцию run_telegram_polling_in_thread, так как она больше не используется 