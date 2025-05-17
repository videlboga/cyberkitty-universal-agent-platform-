import asyncio
import json
import sys
from bson import ObjectId, json_util
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

# Настройка логгера
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/debug.log", rotation="10 MB", level="DEBUG")

async def check_agent_in_db():
    """Проверка наличия агента в базе данных и вывод его структуры."""
    try:
        # Подключение к MongoDB
        mongo_uri = "mongodb://localhost:27017/agent_platform"
        logger.info(f"Подключение к MongoDB по URI: {mongo_uri}")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.get_database()
        logger.info(f"Успешное подключение к базе данных: {db.name}")
        
        # Список всех коллекций
        collections = await db.list_collection_names()
        logger.info(f"Коллекции в базе данных: {collections}")
        
        # Проверка агента по ID
        agent_id = "test_agent_001"
        logger.info(f"Поиск агента с ID: {agent_id}")
        
        agent = await db.agents.find_one({"_id": agent_id})
        
        if agent:
            logger.info(f"Агент найден: {agent['name']}")
            # Преобразуем в JSON для удобного вывода
            agent_json = json.loads(json_util.dumps(agent))
            print(json.dumps(agent_json, indent=2, ensure_ascii=False))
        else:
            logger.warning(f"Агент с ID {agent_id} не найден")
            
            # Поиск всех агентов
            logger.info("Поиск всех агентов в коллекции:")
            all_agents = await db.agents.find().to_list(length=100)
            
            if all_agents:
                logger.info(f"Найдено агентов: {len(all_agents)}")
                for idx, ag in enumerate(all_agents):
                    agent_json = json.loads(json_util.dumps(ag))
                    print(f"\n--- Агент #{idx+1} ---")
                    print(f"ID: {agent_json.get('_id')}")
                    print(f"Имя: {agent_json.get('name')}")
                    print(f"Тип ID: {type(ag.get('_id'))}")
            else:
                logger.warning("Агенты не найдены в коллекции")
        
        # Проверка наличия API-роутов для агентов
        logger.info("Проверка эндпоинтов FastAPI:")
        routes_collection = db.get_collection("api_routes")
        if routes_collection:
            routes = await routes_collection.find().to_list(length=100)
            if routes:
                logger.info(f"Найдено {len(routes)} API-роутов")
                for route in routes:
                    print(f"Путь: {route.get('path')}, Метод: {route.get('method')}")
            else:
                logger.warning("API-роуты не найдены в коллекции")
        
    except Exception as e:
        logger.error(f"Ошибка при проверке агента: {e}")

async def main():
    await check_agent_in_db()

if __name__ == "__main__":
    asyncio.run(main()) 