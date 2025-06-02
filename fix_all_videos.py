#!/usr/bin/env python3
"""
Скрипт для исправления всех видео в сценариях OntoBot:
1. Правильные message_id
2. Добавление флага disable_notification для пересылки без подписей
"""

import requests
import json

API_BASE = "http://localhost:8085/api/v1/simple"

# Правильные соответствия video -> message_id
VIDEO_MAPPINGS = {
    "send_diagnostic_video": 2,        # "Диагностика мыслевирусов"
    "send_ya_ya_video": 4,             # "Задание 1. Я-Я" 
    "send_ya_delo_video": 5,           # "Задание 2. Я-Дело"
    "send_ya_relations_video": 6,      # "Задание 3. Я-Отношения"
}

def get_scenarios():
    """Получить все сценарии OntoBot"""
    response = requests.post(f"{API_BASE}/mongo/find", json={
        "collection": "scenarios",
        "filter": {"scenario_id": {"$regex": "^mr_ontobot"}}
    })
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            return data["data"]
    
    print("❌ Ошибка получения сценариев")
    return []

def fix_video_step(step):
    """Исправить параметры шага с видео"""
    step_id = step.get("id")
    
    if step_id in VIDEO_MAPPINGS:
        params = step.get("params", {})
        old_message_id = params.get("message_id")
        new_message_id = VIDEO_MAPPINGS[step_id]
        
        # Обновляем message_id
        params["message_id"] = new_message_id
        
        # Добавляем параметр для пересылки без подписей (если его нет)
        if "disable_notification" not in params:
            params["disable_notification"] = True
            
        print(f"  ✅ {step_id}: {old_message_id} -> {new_message_id} (+ disable_notification)")
        return True
    
    return False

def update_scenario(scenario):
    """Обновить сценарий в БД"""
    response = requests.post(f"{API_BASE}/mongo/save-scenario", json={
        "collection": "scenarios",
        "scenario_id": scenario["scenario_id"],
        "document": scenario
    })
    
    if response.status_code == 200:
        data = response.json()
        return data["success"]
    
    return False

def main():
    print("🔧 Исправляю все видео в сценариях OntoBot")
    
    scenarios = get_scenarios()
    if not scenarios:
        return
    
    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]
        print(f"\n📋 Проверяю сценарий: {scenario_id}")
        
        modified = False
        for step in scenario["steps"]:
            if fix_video_step(step):
                modified = True
        
        if modified:
            if update_scenario(scenario):
                print(f"  💾 Сценарий {scenario_id} обновлен")
            else:
                print(f"  ❌ Ошибка обновления {scenario_id}")
        else:
            print(f"  ✅ Видео в {scenario_id} уже правильные")
    
    print("\n🎉 Все видео исправлены!")

if __name__ == "__main__":
    main() 