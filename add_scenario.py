#!/usr/bin/env python3
import asyncio
import json
import motor.motor_asyncio
from bson import ObjectId
from loguru import logger

logger.add('logs/add_scenario.log', rotation='10 MB', level='INFO')

async def add_scenario(file_path='docs/examples/test_llm_telegram_scenario_fixed.json'):
    """
    Добавляет сценарий из JSON-файла в базу данных MongoDB.
    
    Args:
        file_path (str): Путь к JSON-файлу сценария
    """
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017/agent_platform')
    db = client.agent_platform
    
    try:
        with open(file_path, 'r') as f:
            scenario_data = json.load(f)
            
        result = await db.scenarios.insert_one(scenario_data)
        scenario_id = str(result.inserted_id)
        logger.info(f'Сценарий добавлен с ID: {scenario_id}')
        print(f'Сценарий добавлен с ID: {scenario_id}')
        
    except Exception as e:
        logger.error(f'Ошибка при добавлении сценария: {e}')
        print(f'Ошибка: {e}')
    finally:
        client.close()

if __name__ == "__main__":
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'docs/examples/test_llm_telegram_scenario_fixed.json'
    asyncio.run(add_scenario(file_path)) 