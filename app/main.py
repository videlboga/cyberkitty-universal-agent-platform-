from fastapi import FastAPI
from loguru import logger
import os
from app.api.user import router as user_router
from app.api.scenario import router as scenario_router
from app.api.integration import router as integration_router, telegram_app
from app.api.runner import router as runner_router
from app.api.agent import router as agent_router
from app.api.collection import router as collection_router
import threading
import logging
import asyncio

# Настройка логирования loguru
os.makedirs("logs", exist_ok=True)
logger.add("logs/api.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

app = FastAPI(title="Universal Agent Platform API", description="API универсальной платформы ИИ-агентов", version="0.1.0")

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

# Удалён запуск polling Telegram-бота из main.py 