#!/usr/bin/env python3
import asyncio
import json
import motor.motor_asyncio
import requests
import subprocess
from datetime import datetime
from bson import ObjectId
from loguru import logger

logger.add('logs/test_execute_fixed_scenario.log', rotation='10 MB', level='INFO')

async def test_execute_scenario():
    """
    Тестирует выполнение исправленного сценария через API
    """
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017/agent_platform')
    db = client.agent_platform
    
    try:
        # Найти агента и сценарий
        agent = await db.agents.find_one({"name": "Тестовый LLM агент"})
        if not agent:
            logger.error("Агент 'Тестовый LLM агент' не найден")
            return
        logger.info(f"Найден агент: {agent['name']}")
        
        scenario = await db.scenarios.find_one({"name": "Тестовый LLM бот (исправленный)"})
        if not scenario:
            logger.error("Сценарий 'Тестовый LLM бот (исправленный)' не найден")
            return
        logger.info(f"Найден сценарий: {scenario['name']} с ID {scenario['_id']}")
        
        # Создать запись о запуске сценария
        execution = {
            "agent_id": agent["_id"],
            "scenario_id": scenario["_id"],
            "status": "pending",
            "created_at": datetime.utcnow(),
            "context": {}
        }
        
        execution_result = await db.scenario_executions.insert_one(execution)
        execution_id = execution_result.inserted_id
        logger.info(f"Создана запись о запуске сценария с ID: {execution_id}")
        
        # Выполнить API-запрос для запуска сценария
        agent_id = str(agent["_id"])
        scenario_id = str(scenario["_id"])
        
        curl_command = f"""
        curl -X POST http://localhost:8000/api/v1/agents/{agent_id}/execute \\
        -H 'Content-Type: application/json' \\
        -d '{{"scenario_id": "{scenario_id}", "user_id": "test_user_123", "chat_id": "648981358"}}'
        """
        
        logger.info(f"Выполняем API-запрос для запуска сценария для агента {agent_id}")
        logger.info(f"Команда: {curl_command}")
        
        process = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
        logger.info(f"Результат выполнения команды: {process.returncode}")
        logger.info(f"Вывод: {process.stdout}")
        
        if process.stderr:
            logger.error(f"Ошибка: {process.stderr}")
        
        try:
            response = json.loads(process.stdout)
            logger.info(f"API-ответ: {response}")
            
            if response.get("success") == False:
                logger.error(f"Ошибка при выполнении сценария: {response.get('error')}")
            else:
                logger.info("Сценарий успешно запущен")
                
        except json.JSONDecodeError:
            logger.error("Не удалось декодировать ответ API")
    
    except Exception as e:
        logger.error(f"Ошибка при тестировании сценария: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_execute_scenario()) 