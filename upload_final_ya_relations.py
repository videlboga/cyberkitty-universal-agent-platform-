#!/usr/bin/env python3

import yaml
import requests
import json

def upload_scenario():
    # Загружаем YAML файл
    with open('scenarios/mr_ontobot_diagnostic_ya_relations.yaml', 'r', encoding='utf-8') as f:
        scenario_data = yaml.safe_load(f)
    
    # Подготавливаем данные для отправки
    payload = {
        "collection": "scenarios",
        "scenario_id": "mr_ontobot_diagnostic_ya_relations",
        "document": scenario_data
    }
    
    # Отправляем в API
    response = requests.post(
        'http://localhost:8085/api/v1/simple/mongo/save-scenario',
        headers={'Content-Type': 'application/json'},
        json=payload
    )
    
    print(f"📤 Загрузка ФИНАЛЬНОГО сценария mr_ontobot_diagnostic_ya_relations...")
    print(f"Status: {response.status_code}")
    
    try:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('success'):
            print("✅ ФИНАЛЬНЫЙ сценарий с used_fields_map успешно загружен!")
            print("🎯 AmoCRM интеграция теперь должна работать ПОЛНОСТЬЮ!")
        else:
            print("❌ Ошибка при загрузке сценария")
            
    except Exception as e:
        print(f"❌ Ошибка парсинга ответа: {e}")
        print(f"Raw response: {response.text}")

if __name__ == "__main__":
    upload_scenario() 