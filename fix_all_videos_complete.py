#!/usr/bin/env python3
"""
Скрипт для исправления всех видео в сценариях OntoBot:
1. Правильные message_id для всех видео
2. Переключение с forwardMessage на copyMessage для пересылки без подписей
3. Добавление параметра disable_notification
"""

import requests
import json

API_BASE = "http://localhost:8085/api/v1/simple"

# Правильные соответствия video -> message_id в канале -1002614708769
VIDEO_MAPPINGS = {
    "send_diagnostic_video": 2,        # "Диагностика мыслевирусов"
    "send_intro_video": 2,             # "Диагностика мыслевирусов"  
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
    """Исправить настройки видео шага"""
    fixed = False
    step_id = step.get("id", "")
    
    # Проверяем, является ли это шагом с видео
    if step_id in VIDEO_MAPPINGS:
        correct_message_id = VIDEO_MAPPINGS[step_id]
        
        # Исправляем message_id если нужно
        current_message_id = step.get("params", {}).get("message_id")
        if current_message_id != correct_message_id:
            if "params" not in step:
                step["params"] = {}
            step["params"]["message_id"] = correct_message_id
            print(f"  ✅ Исправлен message_id для {step_id}: {current_message_id} → {correct_message_id}")
            fixed = True
        
        # Меняем action с forward_message на copy_message для пересылки без подписей
        current_action = step.get("params", {}).get("action")
        if current_action == "forward_message":
            step["params"]["action"] = "copy_message"
            print(f"  ✅ Изменено действие для {step_id}: forward_message → copy_message")
            fixed = True
        
        # Добавляем disable_notification для тихой пересылки
        if "disable_notification" not in step.get("params", {}):
            step["params"]["disable_notification"] = True
            print(f"  ✅ Добавлен disable_notification для {step_id}")
            fixed = True
            
        # Убираем caption чтобы видео пересылалось без подписи
        if "caption" in step.get("params", {}):
            del step["params"]["caption"]
            print(f"  ✅ Удалена подпись для {step_id}")
            fixed = True
    
    return fixed

def update_scenario(scenario):
    """Обновить сценарий в базе данных"""
    response = requests.post(f"{API_BASE}/mongo/save-scenario", json={
        "collection": "scenarios",
        "scenario_id": scenario["scenario_id"],
        "document": scenario
    })
    
    if response.status_code == 200:
        data = response.json()
        return data.get("success", False)
    
    return False

def main():
    print("🎬 Исправляю все видео в сценариях OntoBot...")
    
    scenarios = get_scenarios()
    if not scenarios:
        print("❌ Сценарии не найдены")
        return
    
    total_fixed = 0
    
    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]
        print(f"\n📋 Обрабатываю сценарий: {scenario_id}")
        
        scenario_fixed = False
        
        for step in scenario.get("steps", []):
            if fix_video_step(step):
                scenario_fixed = True
        
        if scenario_fixed:
            if update_scenario(scenario):
                print(f"  💾 Сценарий {scenario_id} обновлен")
                total_fixed += 1
            else:
                print(f"  ❌ Ошибка обновления сценария {scenario_id}")
        else:
            print(f"  ✅ Сценарий {scenario_id} не требует изменений")
    
    print(f"\n🎉 Готово! Исправлено сценариев: {total_fixed}")
    print("\n📋 Итоговые настройки видео:")
    print("  - Правильные message_id для всех видео")
    print("  - copyMessage вместо forwardMessage")
    print("  - disable_notification = true")
    print("  - Без подписей (caption удалён)")

if __name__ == "__main__":
    main() 