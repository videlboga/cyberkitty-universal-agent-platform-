import json
import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
from loguru import logger

# Настройка логирования
logger.add("logs/db_operations.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

# Загрузка тестового сценария в MongoDB
async def load_test_scenario():
    # Использование локального подключения к MongoDB
    mongo_uri = "mongodb://localhost:27017/agent_platform"
    scenario_file = "docs/examples/test_llm_telegram_scenario.json"
    
    try:
        # Подключение к MongoDB
        logger.info(f"Подключение к MongoDB: {mongo_uri}")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.get_default_database()
        
        # Чтение файла сценария
        logger.info(f"Чтение файла сценария: {scenario_file}")
        with open(scenario_file, "r", encoding="utf-8") as f:
            scenario_data = json.load(f)
        
        # Добавление служебных полей
        if "_id" not in scenario_data:
            scenario_data["_id"] = ObjectId()
        
        if "created_at" not in scenario_data:
            scenario_data["created_at"] = datetime.now().isoformat()
        
        if "updated_at" not in scenario_data:
            scenario_data["updated_at"] = datetime.now().isoformat()
        
        # Сохранение сценария в коллекции
        logger.info(f"Сохранение сценария '{scenario_data.get('name', 'Unnamed')}' в коллекции scenarios")
        result = await db.scenarios.replace_one(
            {"_id": scenario_data["_id"]}, 
            scenario_data, 
            upsert=True
        )
        
        if result.modified_count > 0:
            logger.info(f"Сценарий обновлен: {result.modified_count} документ")
        elif result.upserted_id:
            logger.info(f"Сценарий добавлен с ID: {result.upserted_id}")
        else:
            logger.info("Сценарий не изменился")
        
        print(f"Сценарий '{scenario_data.get('name', 'Unnamed')}' успешно сохранен в MongoDB")
        print(f"ID сценария: {scenario_data['_id']}")
        
        return str(scenario_data["_id"])
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке сценария: {e}")
        print(f"Ошибка: {e}")
        return None

async def main():
    await load_test_scenario()

if __name__ == "__main__":
    asyncio.run(main()) 