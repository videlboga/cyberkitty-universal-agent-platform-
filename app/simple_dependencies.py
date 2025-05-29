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

# === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===
_global_engine: Optional[SimpleScenarioEngine] = None

async def get_global_engine() -> SimpleScenarioEngine:
    """
    Возвращает ГЛОБАЛЬНЫЙ движок который создается один раз при старте.
    
    КРИТИЧНО: НЕ создает новый движок при каждом вызове!
    
    Используется в FastAPI dependency injection.
    """
    global _global_engine
    if _global_engine is None:
        raise RuntimeError("Global engine not initialized. Call initialize_global_engine() first.")
    return _global_engine

async def initialize_global_engine():
    """Инициализирует глобальный движок один раз при старте."""
    global _global_engine
    if _global_engine is None:
        logger.info("🚀 Создание ГЛОБАЛЬНОГО движка...")
        _global_engine = await create_engine()
        logger.info("✅ ГЛОБАЛЬНЫЙ движок создан и готов к работе")
    else:
        logger.info("⚠️ ГЛОБАЛЬНЫЙ движок уже инициализирован")

def get_global_engine_sync() -> Optional[SimpleScenarioEngine]:
    """Синхронная версия для использования в ChannelManager."""
    global _global_engine
    return _global_engine

# === УТИЛИТЫ ===

def is_initialized() -> bool:
    """Проверяет инициализирована ли система."""
    return _global_engine is not None


async def healthcheck() -> dict:
    """
    Проверяет здоровье всей системы.
    
    Returns:
        dict: Статус здоровья системы
    """
    if not _global_engine:
        return {
            "healthy": False,
            "reason": "System not initialized"
        }
    
    try:
        engine_healthy = await _global_engine.healthcheck()
        
        if engine_healthy:
            return {
                "healthy": True,
                "engine": "SimpleScenarioEngine",
                "plugins": _global_engine.get_registered_plugins(),
                "handlers": _global_engine.get_registered_handlers()
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
logger.info("💡 Используйте get_global_engine() для получения движка")

# === BACKWARD COMPATIBILITY ===
# Старые функции для совместимости

_engine = None

async def get_engine() -> SimpleScenarioEngine:
    """
    УСТАРЕВШИЙ метод. Используйте get_global_engine().
    
    Использует create_engine() из simple_engine.py для избежания дублирования.
    
    Returns:
        SimpleScenarioEngine: Настроенный движок
    """
    logger.warning("⚠️ get_engine() устарел, используйте get_global_engine()")
    return await get_global_engine()

async def cleanup_engine():
    """Очистка ресурсов движка."""
    global _engine, _global_engine
    
    if _engine:
        logger.info("🧹 Очистка SimpleScenarioEngine...")
        _engine = None
        logger.info("✅ SimpleScenarioEngine очищен")
        
    if _global_engine:
        logger.info("🧹 Очистка ГЛОБАЛЬНОГО движка...")
        _global_engine = None
        logger.info("✅ ГЛОБАЛЬНЫЙ движок очищен") 