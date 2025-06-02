#!/usr/bin/env python3
"""
Тест интеграции валидатора сценариев с API
"""

import requests
import json

API_BASE = "http://localhost:8085/api/v1/simple"

# Тестовый сценарий с проблемами
test_scenario = {
    "scenario_id": "test_validator_scenario",
    "description": "Тестовый сценарий для проверки валидатора",
    "initial_context": {},
    "steps": [
        {
            "id": "start_step",
            "type": "start"
        },
        {
            "id": "broken_step",
            "type": "telegram_send_message",  # Неправильный тип
            "params": {
                "text": "Привет!"
                # Отсутствует chat_id
            }
        },
        {
            "id": "broken_action",
            "type": "action",
            "params": {
                "action": "update_context",  # Неподдерживаемый action
                "data": {
                    "test_field": "test_value"
                }
            }
        },
        {
            "id": "end_step", 
            "type": "end"
        }
    ]
}

def test_validator_api():
    """Тестирует API с валидатором"""
    print("🧪 Тестирование API с валидатором сценариев")
    
    # Отправляем тестовый сценарий
    response = requests.post(f"{API_BASE}/mongo/save-scenario", json={
        "collection": "scenarios",
        "document": test_scenario
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Статус: {result['success']}")
        
        if result.get("warnings"):
            print("⚠️ Предупреждения валидатора:")
            for warning in result["warnings"]:
                print(f"  - {warning}")
        else:
            print("📋 Предупреждений нет")
            
        print(f"💾 Данные: {result.get('data')}")
        
    else:
        print(f"❌ Ошибка API: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_validator_api() 