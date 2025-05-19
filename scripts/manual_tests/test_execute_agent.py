#!/usr/bin/env python3

import requests
import json
import sys
import os
import argparse
from loguru import logger

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.remove()
logger.add("logs/test_execute.log", rotation="10 MB", level="INFO")

API_BASE_URL = "http://localhost:8000"

def get_agent_by_name(name):
    """
    Получает ID агента по его имени
    """
    url = f"{API_BASE_URL}/agents/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        agents = response.json()
        
        for agent in agents:
            if agent.get("name") == name:
                logger.info(f"Найден агент '{name}' с ID: {agent.get('_id')}")
                return agent.get("_id")
        
        logger.error(f"Агент с именем '{name}' не найден")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении списка агентов: {e}")
        return None

def execute_agent_scenario(agent_id, user_id="test_user", chat_id="test_chat"):
    """
    Выполняет сценарий агента через API
    """
    url = f"{API_BASE_URL}/agent-actions/{agent_id}/execute"
    
    payload = {
        "user_id": user_id,
        "chat_id": chat_id,
        "context": {
            "platform": "test",
            "message": "Привет, это тестовое сообщение"
        }
    }
    
    try:
        logger.info(f"Отправляем запрос на выполнение сценария для агента {agent_id}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Сценарий успешно запущен: {result}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении сценария: {e}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Ответ сервера: {e.response.text}")
        return None

def get_agent_details(agent_id):
    """
    Получает подробную информацию об агенте
    """
    url = f"{API_BASE_URL}/agents/{agent_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        agent = response.json()
        logger.info(f"Получена информация об агенте {agent_id}")
        return agent
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении информации об агенте: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Тестирование выполнения сценария агента")
    parser.add_argument("agent", help="ID или название агента")
    parser.add_argument("--user", default="test_user", help="ID пользователя для контекста")
    parser.add_argument("--chat", default="test_chat", help="ID чата для контекста")
    
    args = parser.parse_args()
    
    # Определяем, передан ли ID или название агента
    if len(args.agent) < 10:  # Предполагаем, что ID длиннее 10 символов
        logger.info(f"Поиск агента по имени: {args.agent}")
        agent_id = get_agent_by_name(args.agent)
    else:
        agent_id = args.agent
    
    if not agent_id:
        print(f"Агент не найден: {args.agent}")
        return
    
    # Получаем информацию об агенте
    agent_info = get_agent_details(agent_id)
    if agent_info:
        print(f"Информация об агенте:")
        print(f"ID: {agent_info.get('_id')}")
        print(f"Название: {agent_info.get('name')}")
        print(f"Описание: {agent_info.get('description')}")
        print(f"Сценарий: {agent_info.get('config', {}).get('scenario_id')}")
    
    # Выполняем сценарий
    result = execute_agent_scenario(agent_id, args.user, args.chat)
    
    if result:
        print(f"Сценарий успешно запущен для агента {agent_id}")
        print(f"Результат: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print(f"Ошибка при выполнении сценария для агента {agent_id}")

if __name__ == "__main__":
    main() 