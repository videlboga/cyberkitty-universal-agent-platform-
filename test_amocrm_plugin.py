#!/usr/bin/env python3
"""
Тест AmoCRM плагина - проверка инициализации и работы
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append('/app')
sys.path.append('.')

from loguru import logger
from app.core.simple_engine import SimpleScenarioEngine

# Настраиваем логирование
logger.remove()
logger.add(
    "logs/test_amocrm.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="DEBUG",
    rotation="10 MB"
)
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
    level="INFO"
)

async def test_amocrm_plugin():
    """Тестирует AmoCRM плагин"""
    
    logger.info("🧪 Начинаем тест AmoCRM плагина")
    
    # Создаем движок
    engine = SimpleScenarioEngine()
    logger.info("✅ SimpleScenarioEngine создан")
    
    # Пытаемся зарегистрировать MongoDB плагин первым
    try:
        logger.info("📦 Регистрация MongoDB Plugin...")
        from app.plugins.mongo_plugin import MongoPlugin
        mongo_plugin = MongoPlugin()
        engine.register_plugin(mongo_plugin)
        await mongo_plugin.initialize()
        logger.info("✅ MongoDB Plugin зарегистрирован и инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка MongoDB Plugin: {e}")
        return False
    
    # Теперь регистрируем AmoCRM плагин
    try:
        logger.info("📦 Регистрация AmoCRM Plugin...")
        from app.plugins.simple_amocrm_plugin import SimpleAmoCRMPlugin
        amocrm_plugin = SimpleAmoCRMPlugin()
        engine.register_plugin(amocrm_plugin)
        logger.info("✅ AmoCRM Plugin зарегистрирован")
        
        # Инициализируем плагин
        logger.info("🚀 Инициализация AmoCRM Plugin...")
        await amocrm_plugin.initialize()
        logger.info("✅ AmoCRM Plugin инициализирован")
        
        # Проверяем healthcheck
        logger.info("🏥 Проверка healthcheck AmoCRM Plugin...")
        health = await amocrm_plugin.healthcheck()
        logger.info(f"🏥 Healthcheck результат: {health}")
        
        # Проверяем настройки
        logger.info("⚙️ Проверка текущих настроек...")
        settings = amocrm_plugin.get_current_settings()
        logger.info(f"⚙️ Текущие настройки: {settings}")
        
        # Проверяем зарегистрированные обработчики
        handlers = amocrm_plugin.register_handlers()
        logger.info(f"🔧 Зарегистрированные обработчики: {list(handlers.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка AmoCRM Plugin: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False

async def test_amocrm_settings():
    """Тестирует сохранение и загрузку настроек AmoCRM"""
    
    logger.info("🧪 Тест настроек AmoCRM")
    
    # Создаем движок с плагинами
    engine = SimpleScenarioEngine()
    
    # MongoDB плагин
    from app.plugins.mongo_plugin import MongoPlugin
    mongo_plugin = MongoPlugin()
    engine.register_plugin(mongo_plugin)
    await mongo_plugin.initialize()
    
    # AmoCRM плагин
    from app.plugins.simple_amocrm_plugin import SimpleAmoCRMPlugin
    amocrm_plugin = SimpleAmoCRMPlugin()
    engine.register_plugin(amocrm_plugin)
    await amocrm_plugin.initialize()
    
    # Тестовые настройки
    test_settings = {
        "base_url": "https://test.amocrm.ru",
        "access_token": "test_token_12345"
    }
    
    logger.info("💾 Сохранение тестовых настроек...")
    result = await amocrm_plugin.save_settings_to_db(
        test_settings["base_url"], 
        test_settings["access_token"]
    )
    logger.info(f"💾 Результат сохранения: {result}")
    
    # Перезагружаем настройки
    logger.info("🔄 Перезагрузка настроек...")
    await amocrm_plugin._load_settings_from_db()
    
    # Проверяем настройки
    current_settings = amocrm_plugin.get_current_settings()
    logger.info(f"⚙️ Настройки после перезагрузки: {current_settings}")
    
    # Проверяем, что настройки применились
    if (amocrm_plugin.base_url == test_settings["base_url"] and 
        amocrm_plugin.access_token == test_settings["access_token"]):
        logger.info("✅ Настройки успешно сохранены и загружены!")
        return True
    else:
        logger.error("❌ Настройки не применились корректно")
        return False

async def main():
    """Основная функция тестирования"""
    
    logger.info("🚀 Запуск тестов AmoCRM плагина")
    
    # Тест 1: Базовая инициализация
    logger.info("\n" + "="*50)
    logger.info("ТЕСТ 1: Базовая инициализация AmoCRM плагина")
    logger.info("="*50)
    
    test1_result = await test_amocrm_plugin()
    
    # Тест 2: Настройки
    logger.info("\n" + "="*50)
    logger.info("ТЕСТ 2: Сохранение и загрузка настроек")
    logger.info("="*50)
    
    test2_result = await test_amocrm_settings()
    
    # Итоги
    logger.info("\n" + "="*50)
    logger.info("ИТОГИ ТЕСТИРОВАНИЯ")
    logger.info("="*50)
    logger.info(f"✅ Тест инициализации: {'ПРОЙДЕН' if test1_result else 'ПРОВАЛЕН'}")
    logger.info(f"✅ Тест настроек: {'ПРОЙДЕН' if test2_result else 'ПРОВАЛЕН'}")
    
    if test1_result and test2_result:
        logger.info("🎉 Все тесты пройдены! AmoCRM плагин работает корректно.")
    else:
        logger.error("❌ Есть проблемы с AmoCRM плагином.")

if __name__ == "__main__":
    asyncio.run(main()) 