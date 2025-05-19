#!/usr/bin/env python3
import requests
import json
import sys

def update_agent_model(agent_id, model_name):
    """
    Обновляет модель для указанного агента
    
    Args:
        agent_id: ID агента
        model_name: Название модели
    """
    try:
        # Получаем текущие данные агента
        response = requests.get(f"http://localhost:8000/agents/{agent_id}")
        if response.status_code != 200:
            print(f"Ошибка при получении данных агента: {response.status_code}")
            print(response.text)
            return False
            
        agent_data = response.json()
        
        # Обновляем модель в конфигурации
        if "config" not in agent_data:
            agent_data["config"] = {}
        
        agent_data["config"]["model"] = model_name
        
        # Отправляем обновленные данные
        update_response = requests.patch(
            f"http://localhost:8000/agents/{agent_id}",
            json={"config": agent_data["config"]}
        )
        
        if update_response.status_code == 200:
            print(f"Модель агента {agent_id} успешно обновлена на {model_name}")
            return True
        else:
            print(f"Ошибка при обновлении агента: {update_response.status_code}")
            print(update_response.text)
            return False
            
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python update_agent_model.py <agent_id> <model_name>")
        sys.exit(1)
        
    agent_id = sys.argv[1]
    model_name = sys.argv[2]
    
    update_agent_model(agent_id, model_name) 