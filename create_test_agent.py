import asyncio
import json
import os
import sys
from datetime import datetime
from loguru import logger

from motor.motor_asyncio import AsyncIOMotorClient

# Настройка логгера
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/script.log", rotation="10 MB", level="INFO")

async def create_test_agent():
    # Попытка подключения к MongoDB
    try:
        mongo_uri = "mongodb://localhost:27017/agent_platform"
        logger.info(f"Подключение к MongoDB по URI: {mongo_uri}")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.get_database()
        logger.info(f"Успешное подключение к базе данных: {db.name}")
    except Exception as e:
        logger.error(f"Ошибка подключения к MongoDB: {e}")
        return None
    
    # Проверка наличия сценария
    scenario_id = "test_scenario_001"
    scenario = await db.scenarios.find_one({"_id": scenario_id})
    
    if not scenario:
        logger.error(f"Сценарий с ID {scenario_id} не найден в базе данных")
        return None
    
    logger.info(f"Найден сценарий: {scenario['name']}")
    
    # Определение данных тестового агента
    agent_data = {
        "_id": "test_agent_001",
        "name": "Тестовый агент отправки сообщений",
        "description": "Агент для тестирования отправки сообщений через Telegram",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "config": {
            "scenario_id": scenario_id,
            "role": "telegram_bot",
            "active": True,
            "max_context_length": 10,
            "default_language": "ru",
            "plugins": [
                {
                    "name": "telegram",
                    "enabled": True,
                    "config": {
                        "token": "${TELEGRAM_BOT_TOKEN}",
                        "webhook_url": "${WEBHOOK_BASE_URL}/telegram/webhook"
                    }
                }
            ]
        }
    }
    
    try:
        # Сохранение агента в коллекцию agents
        result = await db.agents.replace_one(
            {"_id": agent_data["_id"]}, 
            agent_data, 
            upsert=True
        )
        
        if result.matched_count:
            logger.info(f"Агент '{agent_data['name']}' обновлен в базе данных")
        elif result.upserted_id:
            logger.info(f"Агент '{agent_data['name']}' добавлен в базу данных с ID: {result.upserted_id}")
        else:
            logger.info(f"Агент '{agent_data['name']}' не изменился")
        
        # Вывод идентификатора агента
        logger.info(f"ID агента: {agent_data['_id']}")
        return agent_data["_id"]
    except Exception as e:
        logger.error(f"Ошибка при сохранении агента: {e}")
        return None

async def main():
    agent_id = await create_test_agent()
    if agent_id:
        logger.info(f"Агент успешно сохранен с ID: {agent_id}")
    else:
        logger.error("Не удалось создать тестовый агент")

if __name__ == "__main__":
    asyncio.run(main()) 