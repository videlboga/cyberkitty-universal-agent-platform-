from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import asyncio
import json
import sys
from loguru import logger
import requests

logger.add("logs/update_scenario.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip")

async def update_scenario(scenario_id='68246055a3813ead9bd861e0', file_path='docs/examples/test_llm_telegram_scenario.json'):
    try:
        # Подключение к MongoDB
        client = AsyncIOMotorClient('mongodb://localhost:27017/agent_platform')
        db = client.get_database()
        
        # Загрузка данных сценария из JSON-файла
        with open(file_path, 'r', encoding='utf-8') as f:
            scenario_data = json.load(f)
        
        # Обновление сценария в коллекции scenarios
        try:
            object_id = ObjectId(scenario_id)
            id_filter = {'_id': object_id}
        except:
            id_filter = {'_id': scenario_id}
        
        result = await db.scenarios.replace_one(id_filter, scenario_data, upsert=True)
        
        if result.modified_count > 0:
            logger.info(f"Сценарий обновлен: {result.modified_count} документов изменено")
            print(f"Сценарий обновлен: {result.modified_count} документов изменено")
        elif result.upserted_id:
            logger.info(f"Сценарий добавлен с ID: {result.upserted_id}")
            print(f"Сценарий добавлен с ID: {result.upserted_id}")
        else:
            logger.info("Сценарий не изменился")
            print("Сценарий не изменился")
        
        await client.close()
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении сценария: {e}")
        print(f"Ошибка: {e}")
        return False

def update_scenario_http(scenario_id):
    # Получаем текущий сценарий
    response = requests.get(f"http://localhost:8000/scenarios/{scenario_id}")
    if response.status_code != 200:
        print(f"Ошибка при получении сценария: {response.status_code}")
        return False
    
    scenario = response.json()
    
    # Находим индекс шага ask_followup
    ask_followup_index = None
    for i, step in enumerate(scenario["steps"]):
        if step["id"] == "ask_followup":
            ask_followup_index = i
            break
    
    if ask_followup_index is None:
        print("Шаг ask_followup не найден")
        return False
    
    # Создаем новый шаг для получения ответа пользователя
    wait_for_followup = {
        "id": "wait_for_followup",
        "type": "input",
        "prompt": "Ваш ответ (да/нет):",
        "output_var": "user_query_followup",
        "next_step": "followup_branch"
    }
    
    # Изменяем следующий шаг для ask_followup
    scenario["steps"][ask_followup_index]["next_step"] = "wait_for_followup"
    
    # Вставляем новый шаг после ask_followup
    scenario["steps"].insert(ask_followup_index + 1, wait_for_followup)
    
    # Обновляем сценарий
    update_response = requests.patch(
        f"http://localhost:8000/scenarios/{scenario_id}",
        json=scenario
    )
    
    if update_response.status_code != 200:
        print(f"Ошибка при обновлении сценария: {update_response.status_code}")
        return False
    
    print(f"Сценарий успешно обновлен")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python3 update_scenario.py <scenario_id>")
        sys.exit(1)
    
    scenario_id = sys.argv[1]
    success = update_scenario_http(scenario_id)
    
    if not success:
        sys.exit(1) 