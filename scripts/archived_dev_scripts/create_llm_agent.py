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

def create_agent(name, description, scenario_id, model="deepsik/SibGPT-13B"):
    """
    Создает нового LLM-агента через API
    """
    url = f"{API_BASE_URL}/agents/"
    
    # Конфигурация агента
    agent_data = {
        "name": name,
        "description": description,
        "config": {
            "scenario_id": scenario_id,
            "type": "llm_assistant",
            "model": model,
            "active": True,
            "max_context_length": 15,
            "default_language": "ru",
            "plugins": [
                {
                    "name": "telegram",
                    "enabled": True,
                    "config": {
                        "token": "${TELEGRAM_BOT_TOKEN}",
                        "webhook_url": "${WEBHOOK_BASE_URL}/telegram/webhook"
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
    # ID сценария базового LLM-агента
    scenario_id = "6824738982a9e8d3ba630b00"
    
    # Создание LLM-агента с использованием модели DeepSik
    agent_id = create_agent(
        name="DeepSik LLM-агент",
        description="Базовый LLM-агент на основе модели DeepSik/SibGPT-13B",
        scenario_id=scenario_id,
        model="deepsik/SibGPT-13B"
    )
    
    if agent_id:
        print(f"LLM-агент успешно создан с ID: {agent_id}")
    else:
        print("Не удалось создать LLM-агента") 