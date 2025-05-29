#!/usr/bin/env python3
"""
Main FastAPI application для Universal Agent Platform.
Принцип: Простота выполнения сценариев через каналы.

Новая архитектура:
- Каналы связывают пользователей с сценариями
- Сценарии в MongoDB, могут изменяться на лету
- Один движок SimpleScenarioEngine для всех
- REST API для выполнения сценариев
"""

import sys
import os
import asyncio
from contextlib import asynccontextmanager

# Добавляем корневую папку в PYTHONPATH для импортов
sys.path.append('/app')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Импортируем API роутеры
from app.api.simple import router as simple_router

# Глобальный ChannelManager
_channel_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    
    НОВАЯ АРХИТЕКТУРА:
    1. ChannelManager НЕ запускается автоматически
    2. Каналы запускаются по требованию через API
    3. Каждый канал = отдельный экземпляр движка
    """
    global _channel_manager
    
    logger.info("🚀 Запуск Universal Agent Platform...")
    
    try:
        # Создаем ChannelManager БЕЗ автоинициализации
        logger.info("🔧 Создание ChannelManager (без автозапуска)...")
        from app.core.channel_manager import ChannelManager
        _channel_manager = ChannelManager()
        logger.info("✅ ChannelManager создан (каналы запускаются по требованию)")
        
        logger.info("🎉 Universal Agent Platform запущена!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска приложения: {e}")
        raise
    finally:
        # Очистка ресурсов
        logger.info("🛑 Остановка Universal Agent Platform...")
        
        if _channel_manager:
            # Останавливаем все активные каналы
            await _channel_manager.stop_all_polling()
                
        logger.info("✅ Universal Agent Platform остановлена")

def get_channel_manager():
    """Получить глобальный ChannelManager."""
    return _channel_manager

# Настраиваем логирование
logger.remove()  # Убираем стандартный обработчик
logger.add(
    "logs/api.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO",
    rotation="10 MB",
    compression="gz",
    serialize=True
)
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level="INFO"
)

# Создаем FastAPI приложение
app = FastAPI(
    title="Universal Agent Platform",
    description="Простая и мощная платформа для создания ИИ агентов",
    version="1.0.0",
    lifespan=lifespan  # Подключаем управление жизненным циклом
)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(simple_router, prefix="/api/v1")  # Простой API

@app.get("/")
async def root():
    """Корневая страница с информацией о платформе."""
    return {
        "platform": "Universal Agent Platform - Simple",
        "version": "3.0.0-simple",
        "description": "Платформа выполнения сценариев через каналы",
        "architecture": "Simple + Flexible",
        "features": [
            "🤖 Выполнение сценариев через каналы",
            "📜 JSON сценарии с переключением",
            "🔄 Простая архитектура с плагинами",
            "📡 Поддержка Telegram",
            "📅 Планировщик отложенных задач",
            "⚙️ SimpleScenarioEngine - один движок для всех"
        ],
        "endpoints": {
            "docs": "/docs",
            "simple_api": "/api/v1/simple",
            "health": "/api/v1/simple/health",
            "mongo_api": "/api/v1/simple/mongo",
            "execute_step": "/api/v1/simple/execute"
        },
        "principles": [
            "ПРОСТОТА ПРЕВЫШЕ ВСЕГО!",
            "Один движок для всех сценариев",
            "Минимум зависимостей",
            "Явная передача контекста"
        ]
    }

@app.get("/health")
async def health_check():
    """Быстрая проверка здоровья системы."""
    return {"status": "healthy", "platform": "Universal Agent Platform"}

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Запуск Universal Agent Platform - Simple")
    logger.info("📋 Архитектура: Каналы + Сценарии + SimpleScenarioEngine")
    logger.info("🔗 API документация: http://localhost:8000/docs")
    
    uvicorn.run(
        "app.simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # В продакшене отключаем reload
        log_level="info"
    ) 