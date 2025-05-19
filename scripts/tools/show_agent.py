#!/usr/bin/env python3
import asyncio
import json
import motor.motor_asyncio
from bson import ObjectId
import sys
from loguru import logger

logger.add('logs/show_agent.log', rotation='10 MB', level='INFO')

async def show_agent(agent_id=None, agent_name=None):
    """
    Отображает информацию об агенте из базы данных
    
    Args:
        agent_id (str): ID агента (опционально)
        agent_name (str): Имя агента (опционально)
    """
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017/agent_platform')
    db = client.agent_platform
    
    try:
        query = {}
        if agent_id:
            try:
                query["_id"] = ObjectId(agent_id)
            except:
                query["_id"] = agent_id
        elif agent_name:
            query["name"] = agent_name
        else:
            logger.error("Необходимо указать ID или имя агента")
            return
            
        agent = await db.agents.find_one(query)
        if agent:
            print(f"Агент найден:")
            print(f"ID: {agent['_id']}")
            print(f"Имя: {agent['name']}")
            print(f"Описание: {agent.get('description', 'Нет описания')}")
            print(f"Конфигурация:")
            print(json.dumps(agent.get('config', {}), indent=2, ensure_ascii=False))
        else:
            logger.error(f"Агент не найден")
            print(f"Агент не найден")
        
    except Exception as e:
        logger.error(f"Ошибка при получении агента: {e}")
        print(f"Ошибка: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        agent_identifier = sys.argv[1]
        # Проверяем, это ID или имя
        if len(agent_identifier) == 24 and all(c in '0123456789abcdef' for c in agent_identifier):
            asyncio.run(show_agent(agent_id=agent_identifier))
        else:
            asyncio.run(show_agent(agent_name=agent_identifier))
    else:
        print("Использование: python3 show_agent.py <agent_id или agent_name>") 