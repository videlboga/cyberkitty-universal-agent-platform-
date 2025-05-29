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
from typing import Optional

# Добавляем корневую папку в PYTHONPATH для импортов
sys.path.append('/app')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Импортируем API роутеры
from app.api.simple import router as simple_router

# Импортируем компоненты платформы
from app.core.channel_manager import ChannelManager
from app.simple_dependencies import initialize_global_engine, get_global_engine_sync

# === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===
_channel_manager: Optional[ChannelManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    
    НОВАЯ АРХИТЕКТУРА:
    1. ОДИН ГЛОБАЛЬНЫЙ движок для всех каналов
    2. ChannelManager использует глобальный движок
    3. Каналы запускаются по требованию через API
    """
    logger.info("🚀 Запуск Universal Agent Platform...")
    
    try:
        # 1. КРИТИЧНО: Сначала инициализируем глобальный движок
        await initialize_global_engine()
        
        # 2. Затем инициализируем ChannelManager с глобальным движком
        global _channel_manager
        global_engine = get_global_engine_sync()
        _channel_manager = ChannelManager(global_engine=global_engine)
        await _channel_manager.initialize()
        
        logger.info("✅ Universal Agent Platform запущена")
        
        yield  # Приложение работает
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска приложения: {e}")
        raise
    finally:
        logger.info("🛑 Остановка Universal Agent Platform...")
        
        # Останавливаем ChannelManager
        if _channel_manager:
            await _channel_manager.stop_all_polling()
            
        logger.info("✅ Universal Agent Platform остановлена")

def get_channel_manager() -> Optional[ChannelManager]:
    """Возвращает глобальный ChannelManager."""
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
    
    # Читаем настройки из переменных окружения
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8085"))
    
    logger.info("🚀 Запуск Universal Agent Platform - Simple")
    logger.info("📋 Архитектура: Каналы + Сценарии + SimpleScenarioEngine")
    logger.info(f"🔗 API документация: http://localhost:{port}/docs")
    
    uvicorn.run(
        "app.simple_main:app",
        host=host,
        port=port,
        reload=False,  # В продакшене отключаем reload
        log_level="info"
    ) 