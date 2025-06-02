#!/usr/bin/env python3
"""
Скрипт для исправления шага request_contact в сценарии mr_ontobot_diagnostic_ya_relations.
Проблема: кнопка request_contact настроена как inline, но должна быть reply кнопкой.
"""

import requests
import json
from loguru import logger

def fix_contact_scenario():
    """Исправляет шаг request_contact в сценарии"""
    
    # URL API
    base_url = "http://localhost:8085/api/v1/simple/mongo"
    
    # 1. Получаем текущий сценарий
    logger.info("📥 Получаю текущий сценарий...")
    response = requests.post(f"{base_url}/find", json={
        "collection": "scenarios",
        "filter": {"scenario_id": "mr_ontobot_diagnostic_ya_relations"}
    })
    
    if not response.json().get("success"):
        logger.error("❌ Не удалось получить сценарий")
        return False
        
    scenario = response.json()["data"][0]
    logger.info(f"✅ Сценарий получен, ID: {scenario['scenario_id']}")
    
    # 2. Находим и исправляем шаг request_contact
    steps = scenario["steps"]
    for i, step in enumerate(steps):
        if step["id"] == "request_contact":
            logger.info(f"🔧 Исправляю шаг request_contact (индекс {i})")
            
            # Исправляем параметры шага
            steps[i]["params"] = {
                "action": "send_message",
                "chat_id": "{chat_id}",
                "text": "📞 **Для получения результатов диагностики поделитесь контактом**\n\nНажмите кнопку ниже, чтобы поделиться номером телефона:",
                "reply_markup": {
                    "keyboard": [
                        [
                            {
                                "text": "📱 Поделиться номером телефона",
                                "request_contact": True
                            }
                        ]
                    ],
                    "one_time_keyboard": True,
                    "resize_keyboard": True
                }
            }
            
            logger.info("✅ Шаг request_contact исправлен")
            break
    else:
        logger.error("❌ Шаг request_contact не найден")
        return False
    
    # 3. Обновляем сценарий в базе данных
    logger.info("💾 Обновляю сценарий в базе данных...")
    response = requests.post(f"{base_url}/update", json={
        "collection": "scenarios",
        "filter": {"scenario_id": "mr_ontobot_diagnostic_ya_relations"},
        "document": {
            "steps": steps
        }
    })
    
    if response.json().get("success"):
        logger.info("✅ Сценарий успешно обновлен!")
        return True
    else:
        logger.error(f"❌ Ошибка обновления сценария: {response.json()}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Запуск исправления сценария...")
    success = fix_contact_scenario()
    
    if success:
        logger.info("🎉 Исправление завершено успешно!")
    else:
        logger.error("💥 Исправление не удалось!") 