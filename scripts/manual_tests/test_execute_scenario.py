import asyncio
import json
import os
import sys
from datetime import datetime
from loguru import logger

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Настройка логгера
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/test_executor.log", rotation="10 MB", level="INFO")

async def test_scenario_execution():
    """Тестирование выполнения сценария через ScenarioExecutor."""
    try:
        # Подключение к MongoDB
        mongo_uri = "mongodb://localhost:27017/agent_platform"
        logger.info(f"Подключение к MongoDB по URI: {mongo_uri}")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.get_database()
        logger.info(f"Успешное подключение к базе данных: {db.name}")
        
        # Используем правильный ID агента, который существует в базе
        agent_id = "682465d66ba933f50fd0f3fc"
        
        # Пробуем найти агента сначала по строковому ID, затем пробуем преобразовать в ObjectId
        agent = await db.agents.find_one({"_id": agent_id})
        if not agent:
            try:
                # Пробуем найти по ObjectId
                agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
            except Exception as e:
                logger.warning(f"Ошибка при преобразовании в ObjectId: {e}")
        
        if not agent:
            logger.error(f"Агент с ID {agent_id} не найден в базе данных")
            return False
        
        logger.info(f"Найден агент: {agent['name']}")
        
        # Получаем тестовый сценарий
        scenario_id = agent['config']['scenario_id']
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        
        if not scenario:
            # Пробуем найти по ObjectId
            try:
                scenario = await db.scenarios.find_one({"_id": ObjectId(scenario_id)})
            except Exception as e:
                logger.warning(f"Ошибка при преобразовании scenario_id в ObjectId: {e}")
        
        if not scenario:
            logger.error(f"Сценарий с ID {scenario_id} не найден")
            return False
        
        logger.info(f"Найден сценарий: {scenario['name']}")
        
        # Создаем записи о выполнении сценария в БД
        execution_id = str(ObjectId())
        execution_data = {
            "_id": execution_id,
            "agent_id": agent_id,
            "scenario_id": scenario_id,
            "status": "started",
            "user_id": "test_user_123",
            "chat_id": "648981358",  # ID тестового чата в Telegram
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None,
            "steps_executed": [],
            "variables": {},
            "context": {}
        }
        
        logger.info(f"Создание записи о выполнении сценария с ID: {execution_id}")
        await db.executions.insert_one(execution_data)
        
        # Создаем API-запрос для выполнения сценария
        logger.info(f"Выполняем API-запрос для запуска сценария для агента {agent_id}")
        
        # Используем curl для отправки запроса
        import subprocess
        
        curl_command = [
            "curl", "-X", "POST", 
            f"http://localhost:8000/agent-actions/{agent_id}/execute",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "user_id": "test_user_123",
                "chat_id": "648981358"  # ID тестового чата
            })
        ]
        
        # Выполнение команды curl
        logger.info(f"Выполнение команды: {' '.join(curl_command)}")
        result = subprocess.run(curl_command, capture_output=True, text=True)
        
        logger.info(f"Результат выполнения команды curl:")
        logger.info(f"Статус: {result.returncode}")
        logger.info(f"Вывод: {result.stdout}")
        
        if result.returncode != 0:
            logger.error(f"Ошибка при выполнении команды curl: {result.stderr}")
            return False
        
        # Проверка результата
        try:
            response = json.loads(result.stdout)
            logger.info(f"API ответ: {response}")
            
            if response.get("success", False):
                logger.info("Сценарий успешно запущен на выполнение!")
                return True
            else:
                logger.error(f"Ошибка при запуске сценария: {response.get('error', 'Неизвестная ошибка')}")
                return False
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при разборе JSON-ответа: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при тестировании выполнения сценария: {e}")
        return False

async def main():
    result = await test_scenario_execution()
    if result:
        logger.info("Тестирование выполнения сценария успешно завершено!")
    else:
        logger.error("Тестирование выполнения сценария завершилось с ошибкой.")

if __name__ == "__main__":
    asyncio.run(main()) 