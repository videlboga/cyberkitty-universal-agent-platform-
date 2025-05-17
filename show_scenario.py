from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import asyncio
import json
import sys

async def get_scenario(scenario_id):
    try:
        client = AsyncIOMotorClient('mongodb://localhost:27017/agent_platform')
        db = client.get_database()
        
        # Пробуем найти сценарий по ID
        scenario = await db.scenarios.find_one({'_id': ObjectId(scenario_id)})
        
        if scenario:
            print(json.dumps(scenario, default=str, indent=2))
        else:
            print(f"Сценарий с ID {scenario_id} не найден.")
        
        await client.close()
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python3 show_scenario.py <scenario_id>")
        sys.exit(1)
        
    scenario_id = sys.argv[1]
    asyncio.run(get_scenario(scenario_id)) 