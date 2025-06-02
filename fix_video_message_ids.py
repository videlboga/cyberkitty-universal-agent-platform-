#!/usr/bin/env python3
"""
Скрипт для исправления message_id видео в сценариях OntoBot.
Заменяет несуществующий message_id: 3 на правильные id.
"""

import requests
import json
import sys

API_BASE = "http://localhost:8085/api/v1/simple"

# Правильные message_id для видео
VIDEO_MESSAGE_IDS = {
    "send_intro_video": 2,  # "Диагностика мыслевирусов"
    "send_ya_ya_video": 4,  # "Задание 1. Я-Я"
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

def fix_video_message_ids(scenario):
    """Исправить message_id для видео в сценарии"""
    steps = scenario.get("steps", [])
    fixed = False
    
    for step in steps:
        step_id = step.get("id", "")
        params = step.get("params", {})
        
        # Проверяем шаги с пересылкой сообщений
        if (step.get("type") == "channel_action" and 
            params.get("action") == "forward_message"):
            
            current_message_id = params.get("message_id")
            
            # Исправляем известные проблемные шаги
            if step_id in VIDEO_MESSAGE_IDS:
                correct_id = VIDEO_MESSAGE_IDS[step_id]
                if current_message_id != correct_id:
                    print(f"🔧 Исправляю {step_id}: {current_message_id} → {correct_id}")
                    params["message_id"] = correct_id
                    fixed = True
            
            # Исправляем message_id: 3 (не существует)
            elif current_message_id == 3:
                # Определяем правильный id по контексту
                if "ya_ya" in step_id.lower() or "задание" in step.get("params", {}).get("text", "").lower():
                    print(f"🔧 Исправляю {step_id}: message_id 3 → 4 (Я-Я видео)")
                    params["message_id"] = 4
                    fixed = True
                else:
                    print(f"🔧 Исправляю {step_id}: message_id 3 → 2 (интро видео)")
                    params["message_id"] = 2
                    fixed = True
    
    return fixed

def update_scenario(scenario):
    """Обновить сценарий в базе данных"""
    response = requests.post(f"{API_BASE}/mongo/update", json={
        "collection": "scenarios",
        "filter": {"scenario_id": scenario["scenario_id"]},
        "document": {"$set": {"steps": scenario["steps"]}}
    })
    
    if response.status_code == 200:
        data = response.json()
        return data.get("success", False)
    
    return False

def main():
    print("🎬 Исправление message_id для видео в сценариях OntoBot")
    print("=" * 60)
    
    scenarios = get_scenarios()
    if not scenarios:
        print("❌ Сценарии не найдены")
        return
    
    total_fixed = 0
    
    for scenario in scenarios:
        scenario_id = scenario.get("scenario_id", "unknown")
        print(f"\n📋 Проверяю сценарий: {scenario_id}")
        
        if fix_video_message_ids(scenario):
            if update_scenario(scenario):
                print(f"✅ Сценарий {scenario_id} обновлен")
                total_fixed += 1
            else:
                print(f"❌ Ошибка обновления {scenario_id}")
        else:
            print(f"ℹ️ Сценарий {scenario_id} не требует исправлений")
    
    print(f"\n🎯 Итого исправлено сценариев: {total_fixed}")
    
    if total_fixed > 0:
        print("\n📺 Правильные message_id для видео:")
        print("   • message_id: 2 = 'Диагностика мыслевирусов'")
        print("   • message_id: 4 = 'Задание 1. Я-Я'")

if __name__ == "__main__":
    main() 