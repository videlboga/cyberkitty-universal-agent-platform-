#!/usr/bin/env python3
"""
Скрипт для исправления структуры inline кнопок в сценариях OntoBot.
Кнопки должны быть Array of Arrays для Telegram API.
"""

import requests
import json
import sys

API_BASE = "http://localhost:8085/api/v1/simple"

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

def fix_buttons_structure(buttons):
    """Исправить структуру кнопок - каждая кнопка должна быть в отдельном массиве"""
    if not buttons:
        return buttons
    
    # Если уже массив массивов - не трогаем
    if isinstance(buttons[0], list):
        return buttons
    
    # Преобразуем каждую кнопку в отдельный массив
    return [[button] for button in buttons]

def update_scenario(scenario):
    """Обновить сценарий с исправленными кнопками"""
    scenario_id = scenario.get("scenario_id", "unknown")
    print(f"🔍 Проверяю сценарий: {scenario_id}")
    
    updated = False
    steps = scenario.get("steps", [])
    
    for step in steps:
        # Ищем шаги с channel_action и send_buttons
        if (step.get("type") == "channel_action" and 
            step.get("params", {}).get("action") == "send_buttons"):
            
            buttons = step["params"].get("buttons", [])
            if buttons:
                # Исключение для request_contact - он должен быть reply
                step_id = step.get("id", "")
                if "request_contact" in step_id or "contact" in step.get("params", {}).get("text", "").lower():
                    print(f"  ⚠️ Пропускаю {step_id} - это reply кнопка для контакта")
                    continue
                
                # Исправляем inline кнопки
                original_structure = json.dumps(buttons, ensure_ascii=False)
                fixed_buttons = fix_buttons_structure(buttons)
                new_structure = json.dumps(fixed_buttons, ensure_ascii=False)
                
                if original_structure != new_structure:
                    step["params"]["buttons"] = fixed_buttons
                    updated = True
                    print(f"  ✅ Исправлен шаг {step_id}")
                    print(f"     Было: {original_structure}")
                    print(f"     Стало: {new_structure}")
    
    if updated:
        # Сохраняем обновленный сценарий
        response = requests.post(f"{API_BASE}/mongo/update", json={
            "collection": "scenarios",
            "filter": {"scenario_id": scenario_id},
            "document": {"steps": steps}
        })
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print(f"✅ Сценарий {scenario_id} обновлен")
                return True
            else:
                print(f"❌ Ошибка обновления {scenario_id}: {data.get('error')}")
        else:
            print(f"❌ HTTP ошибка при обновлении {scenario_id}: {response.status_code}")
    else:
        print(f"  ℹ️ Сценарий {scenario_id} не требует изменений")
    
    return updated

def main():
    print("🚀 Исправление структуры inline кнопок в сценариях OntoBot")
    print("=" * 60)
    
    scenarios = get_scenarios()
    if not scenarios:
        print("❌ Сценарии не найдены")
        sys.exit(1)
    
    print(f"📋 Найдено сценариев: {len(scenarios)}")
    
    updated_count = 0
    for scenario in scenarios:
        if update_scenario(scenario):
            updated_count += 1
        print()
    
    print("=" * 60)
    print(f"✅ Готово! Обновлено сценариев: {updated_count}")
    
    if updated_count > 0:
        print("\n🔄 Рекомендуется перезапустить Telegram поллинг для применения изменений")

if __name__ == "__main__":
    main() 