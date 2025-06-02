#!/usr/bin/env python3
"""
Скрипт для восстановления правильных inline кнопок в сценарии mr_ontobot_diagnostic_ya_relations.
Исправляет только шаги show_ya_relations_options и request_feedback, 
оставляя request_contact с reply кнопкой.
"""

import requests
import json
from loguru import logger

def fix_scenario_buttons():
    """Восстанавливает правильные кнопки в сценарии"""
    
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
    steps = scenario["steps"]
    
    # 2. Найдем и исправим нужные шаги
    for step in steps:
        if step["id"] == "show_ya_relations_options":
            logger.info("🔧 Исправляю шаг show_ya_relations_options...")
            step["params"]["reply_markup"] = {
                "inline_keyboard": [
                    [{"text": "Посмотреть примеры мыслевирусов", "callback_data": "view_ya_relations_examples"}],
                    [{"text": "Написать мыслевирусы «Я-Отношения»", "callback_data": "write_ya_relations_viruses"}]
                ]
            }
            
        elif step["id"] == "request_feedback":
            logger.info("🔧 Исправляю шаг request_feedback...")
            step["params"]["reply_markup"] = {
                "inline_keyboard": [
                    [{"text": "Все про меня", "callback_data": "rating_perfect"}],
                    [{"text": "Норм", "callback_data": "rating_good"}],
                    [{"text": "Готов поспорить", "callback_data": "rating_disagree"}],
                    [{"text": "Не совсем согласен", "callback_data": "rating_partly_disagree"}],
                    [{"text": "Я еще не посмотрел досье", "callback_data": "rating_not_viewed"}]
                ]
            }
            
        elif step["id"] == "request_contact":
            logger.info("✅ Шаг request_contact уже исправлен правильно (reply кнопка)")
    
    # 3. Обновляем сценарий в БД
    logger.info("💾 Сохраняю исправленный сценарий...")
    update_response = requests.post(f"{base_url}/update", json={
        "collection": "scenarios",
        "filter": {"scenario_id": "mr_ontobot_diagnostic_ya_relations"},
        "document": {"steps": steps}
    })
    
    if update_response.json().get("success"):
        logger.success("✅ Сценарий успешно исправлен!")
        logger.info("📋 Исправлены шаги:")
        logger.info("  • show_ya_relations_options: inline кнопки восстановлены")
        logger.info("  • request_feedback: inline кнопки восстановлены")
        logger.info("  • request_contact: остается reply кнопка (как нужно)")
        return True
    else:
        logger.error(f"❌ Ошибка обновления: {update_response.json()}")
        return False

if __name__ == "__main__":
    logger.add("logs/fix_buttons.log", rotation="1 MB")
    logger.info("🚀 Запуск исправления кнопок в сценарии...")
    
    if fix_scenario_buttons():
        logger.success("🎉 Все исправлено!")
    else:
        logger.error("💥 Что-то пошло не так") 