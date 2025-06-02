#!/usr/bin/env python3
"""
Простое исправление message_id в сценарии mr_ontobot_diagnostic_ya_ya
"""

import requests
import json

API_BASE = "http://localhost:8085/api/v1/simple"

def main():
    print("🔧 Исправляю message_id в сценарии mr_ontobot_diagnostic_ya_ya")
    
    # Получаем сценарий
    response = requests.post(f"{API_BASE}/mongo/find", json={
        "collection": "scenarios",
        "filter": {"scenario_id": "mr_ontobot_diagnostic_ya_ya"}
    })
    
    if not response.json()["success"]:
        print("❌ Ошибка получения сценария")
        return
    
    scenario = response.json()["data"][0]
    
    # Исправляем message_id
    for step in scenario["steps"]:
        if step.get("id") == "send_ya_ya_video":
            old_id = step.get("params", {}).get("message_id")
            step["params"]["message_id"] = 4
            print(f"✅ Исправлено: {old_id} → 4")
            break
    
    # Обновляем сценарий
    response = requests.post(f"{API_BASE}/mongo/update", json={
        "collection": "scenarios", 
        "filter": {"scenario_id": "mr_ontobot_diagnostic_ya_ya"},
        "document": scenario
    })
    
    if response.json()["success"]:
        print("✅ Сценарий обновлен успешно")
    else:
        print(f"❌ Ошибка обновления: {response.json()}")

if __name__ == "__main__":
    main() 