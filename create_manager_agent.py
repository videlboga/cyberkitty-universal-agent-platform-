#!/usr/bin/env python3

import requests
import json
import sys
import os
from loguru import logger

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.remove()
logger.add("logs/agent_creation.log", rotation="10 MB", level="INFO")

API_BASE_URL = "http://localhost:8000"

def create_agent(name, description, scenario_id, agent_type="manager"):
    """
    Создает нового агента через API
    """
    url = f"{API_BASE_URL}/agents/"
    
    # Конфигурация агента
    agent_data = {
        "name": name,
        "description": description,
        "config": {
            "scenario_id": scenario_id,
            "role": "manager",
            "active": True,
            "max_context_length": 20,
            "default_language": "ru",
            "plugins": [
                {
                    "name": "telegram",
                    "enabled": True,
                    "config": {
                        "token": "${TELEGRAM_BOT_TOKEN}",
                        "webhook_url": "${WEBHOOK_BASE_URL}/telegram/webhook"
                    }
                },
                {
                    "name": "agent_manager",
                    "enabled": True,
                    "config": {
                        "available_agents": ["expert", "coach", "lifehacker", "mentor", "digest"]
                    }
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, json=agent_data)
        response.raise_for_status()
        agent_id = response.json().get("_id")
        logger.info(f"Агент '{name}' успешно создан с ID: {agent_id}")
        return agent_id
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при создании агента: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Ответ сервера: {e.response.text}")
        return None

if __name__ == "__main__":
    # ID сценария менеджера агентов
    scenario_id = "6824731282a9e8d3ba630afe"
    
    # Создание агента-менеджера
    agent_id = create_agent(
        name="Агент-менеджер",
        description="Главный агент-менеджер для управления другими агентами и маршрутизации запросов",
        scenario_id=scenario_id
    )
    
    if agent_id:
        print(f"Агент-менеджер успешно создан с ID: {agent_id}")
    else:
        print("Не удалось создать агента-менеджера") 