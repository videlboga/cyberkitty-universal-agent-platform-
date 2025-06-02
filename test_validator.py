#!/usr/bin/env python3
import yaml
import json
import requests

def test_scenario_validator(yaml_file_path):
    """Тестирует валидатор на конкретном YAML файле"""
    
    # Загружаем YAML файл
    with open(yaml_file_path, 'r', encoding='utf-8') as f:
        scenario_data = yaml.safe_load(f)
    
    print(f"🔍 Тестируем валидатор на файле: {yaml_file_path}")
    print(f"Scenario ID: {scenario_data.get('scenario_id')}")
    
    # Отправляем через API с валидатором
    url = "http://localhost:8085/api/v1/simple/mongo/save-scenario"
    payload = {
        "collection": "scenarios",
        "scenario_id": scenario_data.get('scenario_id'),
        "document": scenario_data
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    print(f"✅ Статус: {result.get('success')}")
    
    if result.get('warnings'):
        print(f"⚠️ Предупреждения валидатора ({len(result['warnings'])}):")
        for warning in result['warnings']:
            print(f"   - {warning}")
    else:
        print("✨ Валидатор не нашел проблем!")
    
    if result.get('error'):
        print(f"❌ Ошибка: {result['error']}")
    
    return result

if __name__ == "__main__":
    # Тестируем наши исправленные файлы
    test_files = [
        "scenarios/mr_ontobot_diagnostic_ya_delo.yaml",
        "scenarios/mr_ontobot_diagnostic_ya_relations.yaml"
    ]
    
    for file_path in test_files:
        print("\n" + "="*60)
        test_scenario_validator(file_path)
        print("="*60) 