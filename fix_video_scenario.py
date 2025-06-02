#!/usr/bin/env python3
"""
Скрипт для исправления проблемы с видео в сценарии OntoBot.
Заменяем forward_message на send_message с объяснением.
"""

import requests
import json
import sys

API_BASE = "http://localhost:8085/api/v1/simple"

def get_scenario():
    """Получить сценарий mr_ontobot_diagnostic_ya_ya"""
    response = requests.post(f"{API_BASE}/mongo/find", json={
        "collection": "scenarios",
        "filter": {"scenario_id": "mr_ontobot_diagnostic_ya_ya"}
    })
    
    if response.status_code == 200:
        data = response.json()
        if data["success"] and data["data"]:
            return data["data"][0]
    
    print("❌ Ошибка получения сценария")
    return None

def update_scenario(scenario):
    """Обновить сценарий в базе данных"""
    response = requests.post(f"{API_BASE}/mongo/update", json={
        "collection": "scenarios",
        "filter": {"scenario_id": "mr_ontobot_diagnostic_ya_ya"},
        "document": scenario
    })
    
    if response.status_code == 200:
        data = response.json()
        return data.get("success", False)
    
    return False

def fix_video_step(scenario):
    """Исправить шаг отправки видео"""
    steps = scenario.get("steps", [])
    
    for step in steps:
        if step.get("id") == "send_ya_ya_video":
            print(f"🔧 Исправляю шаг {step['id']}")
            
            # Заменяем forward_message на send_message с объяснением
            step["type"] = "channel_action"
            step["params"] = {
                "action": "send_message",
                "chat_id": "{chat_id}",
                "text": "🎥 **Задание 1: Диагностика «Я-Я»**\n\n" +
                       "Сейчас тебе нужно написать свои мыслевирусы в сфере отношения к себе.\n\n" +
                       "📌 *Видео с инструкцией временно недоступно, но ты можешь сразу перейти к заданию.*",
                "parse_mode": "Markdown"
            }
            
            print(f"✅ Шаг {step['id']} исправлен: заменен forward_message на send_message")
            return True
    
    print("❌ Шаг send_ya_ya_video не найден")
    return False

def main():
    print("🔧 Исправление проблемы с видео в сценарии OntoBot...")
    
    # Получить сценарий
    scenario = get_scenario()
    if not scenario:
        sys.exit(1)
    
    print(f"📋 Сценарий получен: {scenario['scenario_id']}")
    
    # Исправить шаг видео
    if fix_video_step(scenario):
        # Обновить сценарий в базе
        if update_scenario(scenario):
            print("✅ Сценарий успешно обновлен в базе данных!")
        else:
            print("❌ Ошибка обновления сценария в базе данных")
            sys.exit(1)
    else:
        print("❌ Не удалось исправить шаг видео")
        sys.exit(1)

if __name__ == "__main__":
    main() 