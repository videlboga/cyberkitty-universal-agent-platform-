#!/usr/bin/env python3
import requests
import json
import sys
import argparse
from loguru import logger

# Настройка логирования
logger.add("logs/api_view.log", rotation="10 MB", level="INFO")

API_BASE_URL = "http://localhost:8000"

def view_scenario(scenario_id):
    """
    Получает информацию о сценарии через API
    
    Args:
        scenario_id: ID сценария
    
    Returns:
        dict: Данные сценария или None в случае ошибки
    """
    try:
        url = f"{API_BASE_URL}/scenarios/{scenario_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            scenario = response.json()
            logger.info(f"Получена информация о сценарии: {scenario_id}")
            
            # Вывод информации о сценарии
            print(f"ID: {scenario_id}")
            print(f"Название: {scenario.get('name')}")
            print(f"Описание: {scenario.get('description', 'Нет описания')}")
            print(f"Шаги: {len(scenario.get('steps', []))}")
            
            # Вывод информации о шагах
            print("\nШаги сценария:")
            for i, step in enumerate(scenario.get('steps', [])):
                print(f"  {i}. Тип: {step.get('type')}, ID: {step.get('id')}")
            
            # Проверяем наличие ветвлений с неправильным форматом
            has_invalid_branches = False
            for i, step in enumerate(scenario.get('steps', [])):
                if step.get('type') == 'branch':
                    branches = step.get('branches')
                    if isinstance(branches, list):
                        has_invalid_branches = True
                        print(f"\nВНИМАНИЕ: Шаг {i} (ID: {step.get('id')}) имеет неправильный формат ветвлений!")
                        print(f"  Текущий формат: список [{len(branches)} элементов]")
                        print(f"  Ожидаемый формат: словарь {'if': step_index, 'else': step_index}")
            
            if not has_invalid_branches:
                print("\nФормат ветвлений: OK")
            
            return scenario
        else:
            logger.error(f"Ошибка при получении сценария: {response.status_code} {response.text}")
            print(f"Ошибка при получении сценария: {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        logger.error(f"Ошибка при получении сценария: {e}")
        print(f"Ошибка: {e}")
        return None

def list_scenarios():
    """
    Получает список всех сценариев через API
    
    Returns:
        list: Список сценариев или None в случае ошибки
    """
    try:
        url = f"{API_BASE_URL}/scenarios/"
        response = requests.get(url)
        
        if response.status_code == 200:
            scenarios = response.json()
            logger.info(f"Получен список сценариев: {len(scenarios)}")
            
            # Вывод списка сценариев
            print(f"Всего сценариев: {len(scenarios)}")
            print("\nСписок сценариев:")
            for i, scenario in enumerate(scenarios):
                print(f"{i+1}. ID: {scenario.get('id')}")
                print(f"   Название: {scenario.get('name')}")
                print(f"   Шаги: {len(scenario.get('steps', []))}")
            
            return scenarios
        else:
            logger.error(f"Ошибка при получении списка сценариев: {response.status_code} {response.text}")
            print(f"Ошибка при получении списка сценариев: {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка сценариев: {e}")
        print(f"Ошибка: {e}")
        return None

def view_agent(agent_id):
    """
    Получает информацию об агенте через API
    
    Args:
        agent_id: ID агента
    
    Returns:
        dict: Данные агента или None в случае ошибки
    """
    try:
        url = f"{API_BASE_URL}/agents/{agent_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            agent = response.json()
            logger.info(f"Получена информация об агенте: {agent_id}")
            
            # Вывод информации об агенте
            print(f"ID: {agent_id}")
            print(f"Название: {agent.get('name')}")
            print(f"Описание: {agent.get('description', 'Нет описания')}")
            
            # Вывод информации о конфигурации
            config = agent.get('config', {})
            print("\nКонфигурация:")
            for key, value in config.items():
                print(f"  {key}: {value}")
            
            # Проверка привязки сценария
            scenario_id = config.get('scenario_id')
            if scenario_id:
                print(f"\nПривязанный сценарий: {scenario_id}")
                
                # Получаем информацию о сценарии
                scenario_url = f"{API_BASE_URL}/scenarios/{scenario_id}"
                scenario_response = requests.get(scenario_url)
                
                if scenario_response.status_code == 200:
                    scenario = scenario_response.json()
                    print(f"  Название сценария: {scenario.get('name')}")
                    print(f"  Количество шагов: {len(scenario.get('steps', []))}")
                else:
                    print(f"  Ошибка при получении информации о сценарии: {scenario_response.status_code}")
            else:
                print("\nНет привязанного сценария")
            
            return agent
        else:
            logger.error(f"Ошибка при получении агента: {response.status_code} {response.text}")
            print(f"Ошибка при получении агента: {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        logger.error(f"Ошибка при получении агента: {e}")
        print(f"Ошибка: {e}")
        return None

def list_agents():
    """
    Получает список всех агентов через API
    
    Returns:
        list: Список агентов или None в случае ошибки
    """
    try:
        url = f"{API_BASE_URL}/agents/"
        response = requests.get(url)
        
        if response.status_code == 200:
            agents = response.json()
            logger.info(f"Получен список агентов: {len(agents)}")
            
            # Вывод списка агентов
            print(f"Всего агентов: {len(agents)}")
            print("\nСписок агентов:")
            for i, agent in enumerate(agents):
                print(f"{i+1}. ID: {agent.get('id')}")
                print(f"   Название: {agent.get('name')}")
                
                # Проверка привязки сценария
                config = agent.get('config', {})
                scenario_id = config.get('scenario_id')
                if scenario_id:
                    print(f"   Сценарий: {scenario_id}")
                else:
                    print(f"   Сценарий: не привязан")
            
            return agents
        else:
            logger.error(f"Ошибка при получении списка агентов: {response.status_code} {response.text}")
            print(f"Ошибка при получении списка агентов: {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка агентов: {e}")
        print(f"Ошибка: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Утилита для просмотра сценариев и агентов через API")
    subparsers = parser.add_subparsers(dest="command", help="Команда")
    
    # Парсер для команды view-scenario
    view_scenario_parser = subparsers.add_parser("view-scenario", help="Просмотр информации о сценарии")
    view_scenario_parser.add_argument("scenario_id", help="ID сценария")
    
    # Парсер для команды list-scenarios
    list_scenarios_parser = subparsers.add_parser("list-scenarios", help="Просмотр списка сценариев")
    
    # Парсер для команды view-agent
    view_agent_parser = subparsers.add_parser("view-agent", help="Просмотр информации об агенте")
    view_agent_parser.add_argument("agent_id", help="ID агента")
    
    # Парсер для команды list-agents
    list_agents_parser = subparsers.add_parser("list-agents", help="Просмотр списка агентов")
    
    args = parser.parse_args()
    
    if args.command == "view-scenario":
        view_scenario(args.scenario_id)
    elif args.command == "list-scenarios":
        list_scenarios()
    elif args.command == "view-agent":
        view_agent(args.agent_id)
    elif args.command == "list-agents":
        list_agents()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 