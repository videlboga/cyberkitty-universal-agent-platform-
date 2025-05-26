#!/usr/bin/env python3
"""
🔧 УПРОЩЕННЫЕ ЗАВИСИМОСТИ - МИНИМАЛЬНАЯ ИНИЦИАЛИЗАЦИЯ
Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!

Убрано дублирование логики инициализации - используем create_engine из simple_engine.py
"""

import os
import asyncio
from typing import Optional
from loguru import logger

from app.core.simple_engine import SimpleScenarioEngine, create_engine

# === ЛОГИРОВАНИЕ ===
logger.add(
    "logs/dependencies.log",
    rotation="10 MB",
    retention="7 days",
    compression="gz",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO"
)

# Глобальные переменные для кеширования
_engine: Optional[SimpleScenarioEngine] = None
_lock = asyncio.Lock()


async def get_simple_engine() -> SimpleScenarioEngine:
    """
    Получает настроенный SimpleScenarioEngine.
    
    Singleton pattern - создается только один раз и переиспользуется.
    Использует create_engine() из simple_engine.py для избежания дублирования.
    """
    global _engine
    
    async with _lock:
        if _engine is None:
            logger.info("🔧 Инициализация SimpleScenarioEngine через create_engine()...")
            
            # Используем create_engine из simple_engine.py
            _engine = await create_engine()
            
            logger.info("🎯 SimpleScenarioEngine настроен через create_engine()")
            
        return _engine


async def cleanup_engine():
    """Очистка ресурсов движка."""
    global _engine
    
    if _engine:
        logger.info("🧹 Очистка SimpleScenarioEngine...")
        
        # Здесь можно добавить логику очистки плагинов
        # Например, закрытие соединений с БД
        
        _engine = None
        logger.info("✅ SimpleScenarioEngine очищен")


# === УТИЛИТЫ ===

def is_initialized() -> bool:
    """Проверяет инициализирована ли система."""
    return _engine is not None


async def healthcheck() -> dict:
    """
    Проверяет здоровье всей системы.
    
    Returns:
        dict: Статус здоровья системы
    """
    if not _engine:
        return {
            "healthy": False,
            "reason": "System not initialized"
        }
    
    try:
        engine_healthy = await _engine.healthcheck()
        
        if engine_healthy:
            return {
                "healthy": True,
                "engine": "SimpleScenarioEngine",
                "plugins": _engine.get_registered_plugins(),
                "handlers": _engine.get_registered_handlers()
            }
        else:
            return {
                "healthy": False,
                "reason": "Engine healthcheck failed"
            }
            
    except Exception as e:
        logger.error(f"Healthcheck error: {e}")
        return {
            "healthy": False,
            "reason": f"Healthcheck exception: {e}"
        }


# === ENVIRONMENT VALIDATION ===

def validate_environment():
    """
    Проверяет переменные окружения.
    Выводит предупреждения о недостающих настройках.
    """
    logger.info("🔍 Проверка переменных окружения...")
    
    # Опциональные переменные
    optional_vars = {
        "TELEGRAM_BOT_TOKEN": "Telegram интеграция будет недоступна",
        "MONGODB_URI": "MongoDB интеграция будет недоступна", 
        "OPENROUTER_API_KEY": "LLM интеграция будет недоступна",
        "RAG_URL": "RAG интеграция будет недоступна (по умолчанию: https://rag.cyberkitty.tech)"
    }
    
    for var_name, warning_msg in optional_vars.items():
        value = os.getenv(var_name)
        if value:
            # Скрываем секретные части
            if "KEY" in var_name or "TOKEN" in var_name:
                masked = value[:8] + "..." if len(value) > 8 else "***"
                logger.info(f"✅ {var_name}: {masked}")
            else:
                logger.info(f"✅ {var_name}: {value}")
        else:
            logger.warning(f"⚠️ {var_name} не установлен: {warning_msg}")
    
    logger.info("🔍 Проверка переменных окружения завершена")


# === ИНИЦИАЛИЗАЦИЯ ПРИ ИМПОРТЕ ===

# Проверяем окружение при импорте модуля
validate_environment()

logger.info("📦 Модуль simple_dependencies загружен")
logger.info("💡 Используйте get_simple_engine() для получения движка") 