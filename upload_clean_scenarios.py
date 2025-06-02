#!/usr/bin/env python3
"""
Скрипт для загрузки чистых сценариев OntoBot в базу данных
"""

import requests
import json
import yaml

API_BASE = "http://localhost:8085/api/v1/simple"

def load_yaml_scenario(file_path):
    """Загрузить сценарий из YAML файла"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def upload_scenario(scenario_data):
    """Загрузить сценарий в базу данных"""
    response = requests.post(f"{API_BASE}/mongo/save-scenario", json={
        "collection": "scenarios",
        "scenario_id": scenario_data["scenario_id"],
        "document": scenario_data
    })
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print(f"✅ Сценарий {scenario_data['scenario_id']} загружен успешно")
            return True
        else:
            print(f"❌ Ошибка загрузки {scenario_data['scenario_id']}: {data.get('error', 'неизвестно')}")
    else:
        print(f"❌ HTTP ошибка для {scenario_data['scenario_id']}: {response.status_code}")
    
    return False

def main():
    scenarios_to_upload = [
        "clean_ontobot_main_router.yaml",
        "clean_ontobot_diagnostic_ya_ya.yaml", 
        "clean_ontobot_diagnostic_ya_delo.yaml",
        "clean_ontobot_diagnostic_ya_relations.yaml",
        "clean_ontobot_contact_collection.yaml"
    ]
    
    print("🚀 Загружаю чистые сценарии OntoBot...")
    
    success_count = 0
    for file_path in scenarios_to_upload:
        try:
            print(f"\n📋 Обрабатываю {file_path}...")
            scenario_data = load_yaml_scenario(file_path)
            
            if upload_scenario(scenario_data):
                success_count += 1
            
        except Exception as e:
            print(f"❌ Ошибка обработки {file_path}: {e}")
    
    print(f"\n🎯 Результат: {success_count}/{len(scenarios_to_upload)} сценариев загружено")
    
    if success_count == len(scenarios_to_upload):
        print("✅ Все сценарии загружены успешно!")
    else:
        print("⚠️ Есть ошибки при загрузке")

if __name__ == "__main__":
    main() 