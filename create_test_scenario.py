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

async def create_test_scenario():
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
    
    # Определение данных тестового сценария
    scenario_data = {
        "_id": "test_scenario_001",
        "name": "Тестовый сценарий отправки сообщений",
        "description": "Сценарий для тестирования отправки сообщений через Telegram",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "steps": [
            {
                "id": "start",
                "type": "start",
                "next": "send_message"
            },
            {
                "id": "send_message",
                "type": "action",
                "action": "send_message",
                "config": {
                    "plugin": "telegram",
                    "method": "send_message",
                    "params": {
                        "chat_id": "648981358",
                        "text": "Привет! Это тестовое сообщение от сценария."
                    }
                },
                "next": "end"
            },
            {
                "id": "end",
                "type": "end"
            }
        ],
        "triggers": [
            {
                "type": "api",
                "enabled": True
            }
        ],
        "variables": [],
        "active": True
    }
    
    try:
        # Сохранение сценария в коллекцию scenarios
        result = await db.scenarios.replace_one(
            {"_id": scenario_data["_id"]}, 
            scenario_data, 
            upsert=True
        )
        
        if result.matched_count:
            logger.info(f"Сценарий '{scenario_data['name']}' обновлен в базе данных")
        elif result.upserted_id:
            logger.info(f"Сценарий '{scenario_data['name']}' добавлен в базу данных с ID: {result.upserted_id}")
        else:
            logger.info(f"Сценарий '{scenario_data['name']}' не изменился")
        
        # Вывод идентификатора сценария
        logger.info(f"ID сценария: {scenario_data['_id']}")
        return scenario_data["_id"]
    except Exception as e:
        logger.error(f"Ошибка при сохранении сценария: {e}")
        return None

async def main():
    scenario_id = await create_test_scenario()
    if scenario_id:
        logger.info(f"Сценарий успешно сохранен с ID: {scenario_id}")
    else:
        logger.error("Не удалось создать тестовый сценарий")

if __name__ == "__main__":
    asyncio.run(main()) 