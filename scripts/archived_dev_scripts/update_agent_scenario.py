#!/usr/bin/env python3
import requests
import json
import sys

def update_agent_scenario(agent_id, scenario_id):
    # Получаем текущие данные агента
    response = requests.get(f"http://localhost:8000/agents/{agent_id}")
    if response.status_code != 200:
        print(f"Ошибка при получении данных агента: {response.status_code}")
        return False
    
    agent_data = response.json()
    
    # Обновляем ID сценария
    agent_data["scenario_id"] = scenario_id
    
    # Отправляем обновленные данные
    update_response = requests.patch(
        f"http://localhost:8000/agents/{agent_id}",
        json={"scenario_id": scenario_id}
    )
    
    if update_response.status_code != 200:
        print(f"Ошибка при обновлении агента: {update_response.status_code}")
        return False
    
    print(f"Агент {agent_id} успешно обновлен для использования сценария {scenario_id}")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python3 update_agent_scenario.py <agent_id> <scenario_id>")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    scenario_id = sys.argv[2]
    success = update_agent_scenario(agent_id, scenario_id)
    
    if not success:
        sys.exit(1) 