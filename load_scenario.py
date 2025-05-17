import json
import sys
from pymongo import MongoClient
from bson import ObjectId

# Инициализация подключения к БД
client = MongoClient("mongodb://localhost:27017/")
db = client["agent_platform"]
collection = db["scenarios"]

# Загрузка JSON-файла
scenario_path = "docs/examples/test_llm_telegram_scenario.json"
print(f"Загрузка сценария из {scenario_path}...")

try:
    with open(scenario_path, "r", encoding="utf-8") as f:
        scenario_data = json.load(f)
        
    # Обновляем или создаем запись в БД
    result = collection.find_one_and_update(
        {"name": scenario_data["name"]},
        {"$set": scenario_data},
        upsert=True,
        return_document=True
    )
    
    print(f"Сценарий '{scenario_data['name']}' успешно сохранен в базе данных.")
    
    # Вывод id сценария
    if "_id" in result:
        print(f"ID сценария: {result['_id']}")
        
    # Проверка количества шагов
    if "steps" in result:
        print(f"Количество шагов: {len(result['steps'])}")
    
except Exception as e:
    print(f"Ошибка при загрузке сценария: {e}")
    sys.exit(1) 