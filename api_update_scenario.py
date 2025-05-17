#!/usr/bin/env python3
import requests
import json
import sys
import argparse
from loguru import logger

# Настройка логирования
logger.add("logs/api_update_scenario.log", rotation="10 MB", level="INFO")

API_BASE_URL = "http://localhost:8000"

def update_scenario(scenario_id, file_path):
    """
    Обновляет сценарий через API
    
    Args:
        scenario_id: ID сценария
        file_path: Путь к JSON-файлу с новым сценарием
    
    Returns:
        bool: True если обновление успешно, иначе False
    """
    try:
        # Загружаем данные сценария из файла
        with open(file_path, 'r') as f:
            scenario_data = json.load(f)
        
        # Отправляем запрос на обновление сценария
        url = f"{API_BASE_URL}/scenarios/{scenario_id}"
        response = requests.patch(url, json=scenario_data)
        
        if response.status_code == 200:
            updated_scenario = response.json()
            logger.info(f"Сценарий успешно обновлен: {scenario_id}")
            print(f"Сценарий успешно обновлен: {scenario_id}")
            print(f"Название: {updated_scenario.get('name')}")
            return True
        else:
            logger.error(f"Ошибка при обновлении сценария: {response.status_code} {response.text}")
            print(f"Ошибка при обновлении сценария: {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении сценария: {e}")
        print(f"Ошибка: {e}")
        return False

def create_scenario(file_path):
    """
    Создает новый сценарий через API
    
    Args:
        file_path: Путь к JSON-файлу со сценарием
    
    Returns:
        str: ID созданного сценария или None в случае ошибки
    """
    try:
        # Загружаем данные сценария из файла
        with open(file_path, 'r') as f:
            scenario_data = json.load(f)
        
        # Отправляем запрос на создание сценария
        url = f"{API_BASE_URL}/scenarios/"
        response = requests.post(url, json=scenario_data)
        
        if response.status_code == 201:
            created_scenario = response.json()
            scenario_id = created_scenario.get('id')
            logger.info(f"Сценарий успешно создан с ID: {scenario_id}")
            print(f"Сценарий успешно создан с ID: {scenario_id}")
            print(f"Название: {created_scenario.get('name')}")
            return scenario_id
        else:
            logger.error(f"Ошибка при создании сценария: {response.status_code} {response.text}")
            print(f"Ошибка при создании сценария: {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        logger.error(f"Ошибка при создании сценария: {e}")
        print(f"Ошибка: {e}")
        return None

def update_agent_scenario(agent_id, scenario_id):
    """
    Обновляет привязку сценария к агенту через API
    
    Args:
        agent_id: ID агента
        scenario_id: ID сценария
    
    Returns:
        bool: True если обновление успешно, иначе False
    """
    try:
        # Получаем текущие данные агента
        url = f"{API_BASE_URL}/agents/{agent_id}"
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.error(f"Ошибка при получении агента: {response.status_code} {response.text}")
            print(f"Ошибка при получении агента: {response.status_code}")
            return False
        
        agent_data = response.json()
        
        # Обновляем привязку сценария
        if 'config' not in agent_data:
            agent_data['config'] = {}
        
        agent_data['config']['scenario_id'] = scenario_id
        
        # Отправляем запрос на обновление агента
        response = requests.patch(url, json={'config': agent_data['config']})
        
        if response.status_code == 200:
            logger.info(f"Привязка сценария к агенту успешно обновлена: агент {agent_id}, сценарий {scenario_id}")
            print(f"Привязка сценария к агенту успешно обновлена")
            return True
        else:
            logger.error(f"Ошибка при обновлении агента: {response.status_code} {response.text}")
            print(f"Ошибка при обновлении агента: {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
        logger.error(f"Ошибка при обновлении агента: {e}")
        print(f"Ошибка: {e}")
        return False

def execute_scenario(agent_id, user_id="test_user_123", chat_id="648981358"):
    """
    Выполняет сценарий для агента через API
    
    Args:
        agent_id: ID агента
        user_id: ID пользователя для контекста
        chat_id: ID чата для отправки сообщений
    
    Returns:
        dict: Результат выполнения сценария
    """
    try:
        # Отправляем запрос на выполнение сценария
        url = f"{API_BASE_URL}/agent-actions/{agent_id}/execute"
        data = {
            "user_id": user_id,
            "chat_id": chat_id
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            success = result.get('success', False)
            
            if success:
                logger.info(f"Сценарий успешно выполнен для агента {agent_id}")
                print("Сценарий успешно выполнен")
            else:
                error = result.get('error', 'Неизвестная ошибка')
                logger.error(f"Ошибка при выполнении сценария: {error}")
                print(f"Ошибка при выполнении сценария: {error}")
            
            return result
        else:
            logger.error(f"Ошибка при выполнении сценария: {response.status_code} {response.text}")
            print(f"Ошибка при выполнении сценария: {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        logger.error(f"Ошибка при выполнении сценария: {e}")
        print(f"Ошибка: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Утилита для работы со сценариями через API")
    subparsers = parser.add_subparsers(dest="command", help="Команда")
    
    # Парсер для команды update
    update_parser = subparsers.add_parser("update", help="Обновить существующий сценарий")
    update_parser.add_argument("scenario_id", help="ID сценария для обновления")
    update_parser.add_argument("file_path", help="Путь к JSON-файлу с новым сценарием")
    
    # Парсер для команды create
    create_parser = subparsers.add_parser("create", help="Создать новый сценарий")
    create_parser.add_argument("file_path", help="Путь к JSON-файлу со сценарием")
    
    # Парсер для команды link
    link_parser = subparsers.add_parser("link", help="Привязать сценарий к агенту")
    link_parser.add_argument("agent_id", help="ID агента")
    link_parser.add_argument("scenario_id", help="ID сценария")
    
    # Парсер для команды execute
    execute_parser = subparsers.add_parser("execute", help="Выполнить сценарий для агента")
    execute_parser.add_argument("agent_id", help="ID агента")
    execute_parser.add_argument("--user_id", default="test_user_123", help="ID пользователя (по умолчанию: test_user_123)")
    execute_parser.add_argument("--chat_id", default="648981358", help="ID чата (по умолчанию: 648981358)")
    
    # Парсер для команды full-update
    full_update_parser = subparsers.add_parser("full-update", help="Обновить сценарий и выполнить его")
    full_update_parser.add_argument("agent_id", help="ID агента")
    full_update_parser.add_argument("scenario_id", help="ID сценария")
    full_update_parser.add_argument("file_path", help="Путь к JSON-файлу с новым сценарием")
    
    args = parser.parse_args()
    
    if args.command == "update":
        update_scenario(args.scenario_id, args.file_path)
    elif args.command == "create":
        create_scenario(args.file_path)
    elif args.command == "link":
        update_agent_scenario(args.agent_id, args.scenario_id)
    elif args.command == "execute":
        execute_scenario(args.agent_id, args.user_id, args.chat_id)
    elif args.command == "full-update":
        success = update_scenario(args.scenario_id, args.file_path)
        if success:
            success = update_agent_scenario(args.agent_id, args.scenario_id)
            if success:
                execute_scenario(args.agent_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 