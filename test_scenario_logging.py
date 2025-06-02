#!/usr/bin/env python3
"""
🧪 ТЕСТ СИСТЕМЫ ЛОГИРОВАНИЯ СЦЕНАРИЕВ
Демонстрация детального логирования каждого шага выполнения
"""

import asyncio
import json
from datetime import datetime
from loguru import logger

# Настройка логирования для теста
logger.add(
    "logs/test_scenario_logging.log",
    rotation="10 MB",
    retention="7 days",
    compression="gz",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | TEST | {message}",
    level="DEBUG"
)

async def test_scenario_logging():
    """Тестирует систему логирования сценариев."""
    
    logger.info("🧪 Начинаю тест системы логирования сценариев")
    
    try:
        # Импортируем зависимости
        from app.simple_dependencies import initialize_global_engine, get_global_engine
        from app.core.scenario_logger import get_scenario_logger, LogLevel
        
        # Инициализируем систему
        logger.info("🚀 Инициализация системы...")
        await initialize_global_engine()
        
        engine = await get_global_engine()
        scenario_logger = get_scenario_logger()
        
        logger.info("✅ Система инициализирована")
        
        # Создаем тестовый сценарий
        test_scenario = {
            "scenario_id": "test_logging_scenario",
            "name": "Тестовый сценарий для логирования",
            "description": "Демонстрация детального логирования каждого шага",
            "steps": [
                {
                    "id": "start",
                    "type": "start",
                    "next_step": "log_hello"
                },
                {
                    "id": "log_hello",
                    "type": "log_message",
                    "params": {
                        "message": "Привет из тестового сценария! Пользователь: {user_name}",
                        "level": "INFO"
                    },
                    "next_step": "increment_counter"
                },
                {
                    "id": "increment_counter",
                    "type": "increment",
                    "params": {
                        "variable": "test_counter",
                        "output_var": "new_counter_value"
                    },
                    "next_step": "log_counter"
                },
                {
                    "id": "log_counter",
                    "type": "log_message",
                    "params": {
                        "message": "Счетчик увеличен до: {new_counter_value}",
                        "level": "INFO"
                    },
                    "next_step": "end"
                },
                {
                    "id": "end",
                    "type": "end",
                    "params": {
                        "message": "Тестовый сценарий завершен успешно!"
                    }
                }
            ]
        }
        
        # Тестовый контекст
        test_context = {
            "user_id": "test_user_123",
            "chat_id": "test_chat_456",
            "channel_id": "test_channel",
            "user_name": "Тестовый Пользователь",
            "test_counter": 5,
            "test_mode": True
        }
        
        logger.info("📋 Запускаю тестовый сценарий...")
        logger.info(f"📊 Начальный контекст: {test_context}")
        
        # Выполняем сценарий
        start_time = datetime.now()
        result_context = await engine.execute_scenario(test_scenario, test_context)
        end_time = datetime.now()
        
        execution_duration = (end_time - start_time).total_seconds() * 1000
        
        logger.info(f"✅ Сценарий выполнен за {execution_duration:.1f}ms")
        logger.info(f"📊 Финальный контекст: {result_context}")
        
        # Проверяем активные сценарии
        active_scenarios = scenario_logger.get_active_scenarios()
        logger.info(f"📈 Активных сценариев: {len(active_scenarios)}")
        
        # Выводим статистику
        if result_context.get("execution_id"):
            execution_id = result_context["execution_id"]
            status = scenario_logger.get_scenario_status(execution_id)
            if status:
                logger.info(f"📊 Статус выполнения: {json.dumps(status, indent=2, ensure_ascii=False)}")
        
        logger.info("🎉 Тест системы логирования завершен успешно!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте логирования: {e}")
        return False

async def test_error_scenario():
    """Тестирует логирование ошибок в сценариях."""
    
    logger.info("🧪 Тест логирования ошибок...")
    
    try:
        from app.simple_dependencies import get_global_engine
        
        engine = await get_global_engine()
        
        # Сценарий с ошибкой
        error_scenario = {
            "scenario_id": "test_error_scenario",
            "steps": [
                {
                    "id": "start",
                    "type": "start",
                    "next_step": "invalid_step"
                },
                {
                    "id": "invalid_step",
                    "type": "non_existent_type",  # Несуществующий тип шага
                    "next_step": "end"
                },
                {
                    "id": "end",
                    "type": "end"
                }
            ]
        }
        
        test_context = {
            "user_id": "error_test_user",
            "test_mode": True
        }
        
        logger.info("📋 Запускаю сценарий с ошибкой...")
        
        try:
            await engine.execute_scenario(error_scenario, test_context)
        except Exception as e:
            logger.info(f"✅ Ошибка корректно обработана: {e}")
        
        logger.info("🎉 Тест логирования ошибок завершен!")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте ошибок: {e}")

async def main():
    """Главная функция теста."""
    
    logger.info("🚀 Запуск тестов системы логирования сценариев")
    
    # Тест 1: Обычное выполнение
    success1 = await test_scenario_logging()
    
    # Тест 2: Обработка ошибок
    await test_error_scenario()
    
    if success1:
        logger.info("✅ Все тесты пройдены успешно!")
        
        # Выводим информацию о логах
        logger.info("📁 Логи сохранены в:")
        logger.info("   - logs/scenario_execution.log - детальные логи выполнения")
        logger.info("   - logs/test_scenario_logging.log - логи этого теста")
        logger.info("   - MongoDB коллекция 'scenario_execution_logs' - структурированные данные")
        
        logger.info("🌐 API endpoints для просмотра логов:")
        logger.info("   - GET /api/v1/simple/scenario-logs/active - активные выполнения")
        logger.info("   - GET /api/v1/simple/scenario-logs/{execution_id} - детали выполнения")
        logger.info("   - GET /api/v1/simple/scenario-logs/history - история выполнений")
        
    else:
        logger.error("❌ Некоторые тесты не прошли")

if __name__ == "__main__":
    asyncio.run(main()) 