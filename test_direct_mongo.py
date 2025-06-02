#!/usr/bin/env python3
import yaml
import requests
import sys

def test_direct_mongo():
    """Тестируем через обычный mongo/update endpoint"""
    
    # Загружаем один файл
    with open('scenarios/mr_ontobot_diagnostic_ya_delo.yaml', 'r', encoding='utf-8') as f:
        scenario_data = yaml.safe_load(f)
    
    print(f"📝 Тестируем через mongo/update: {scenario_data['scenario_id']}")
    
    # Отправляем через обычный mongo/update endpoint
    try:
        response = requests.post(
            "http://localhost:8085/api/v1/simple/mongo/update",
            json={
                "collection": "scenarios",
                "filter": {"scenario_id": scenario_data['scenario_id']},
                "document": {"$set": scenario_data}
            },
            timeout=10  # 10 секунд timeout
        )
        
        result = response.json()
        print(f"✅ Статус: {result.get('success')}")
        print(f"📊 Данные: {result.get('data')}")
        
        if result.get('error'):
            print(f"❌ Ошибка: {result['error']}")
            
        return True
        
    except requests.exceptions.Timeout:
        print("❌ Timeout - mongo/update завис!")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_direct_mongo() 