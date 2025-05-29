#!/usr/bin/env python3
"""
Простой тест YAML загрузчика
Проверяет соответствие принципам Universal Agent Platform
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.yaml_scenario_loader import yaml_loader


def test_yaml_loader():
    """Тестируем загрузку YAML сценария."""
    print("🧪 Тестируем YAML загрузчик...")
    
    try:
        # Загружаем тестовый сценарий
        scenario = yaml_loader.load_from_file("scenarios/yaml/simple_test.yaml")
        
        print(f"✅ Сценарий загружен: {scenario['scenario_id']}")
        print(f"📊 Количество шагов: {len(scenario['steps'])}")
        
        # Проверяем структуру
        assert scenario['scenario_id'] == 'simple_yaml_test'
        assert len(scenario['steps']) == 5
        assert scenario['steps'][0]['type'] == 'start'
        assert scenario['steps'][-1]['type'] == 'end'
        
        # Проверяем initial_context
        assert 'initial_context' in scenario
        assert 'test_data' in scenario['initial_context']
        
        print("✅ Все проверки пройдены!")
        
        # Выводим структуру для проверки
        print("\n📋 Структура сценария:")
        for step in scenario['steps']:
            print(f"  - {step['id']} ({step['type']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False


def test_json_to_yaml_conversion():
    """Тестируем конвертацию JSON в YAML."""
    print("\n🔄 Тестируем конвертацию JSON -> YAML...")
    
    # Простой JSON сценарий для тестирования
    json_scenario = {
        "scenario_id": "test_conversion",
        "initial_context": {
            "data": {}
        },
        "steps": [
            {
                "id": "start",
                "type": "start",
                "next_step": "send_msg"
            },
            {
                "id": "send_msg",
                "type": "telegram_send_message",
                "params": {
                    "chat_id": "{chat_id}",
                    "text": "Тест сообщение"
                },
                "next_step": "end"
            },
            {
                "id": "end",
                "type": "end"
            }
        ]
    }
    
    try:
        yaml_content = yaml_loader.convert_json_to_yaml(json_scenario)
        print("✅ Конвертация успешна!")
        print("\n📄 YAML результат:")
        print(yaml_content)
        
        # Проверяем, что можем загрузить обратно
        converted_back = yaml_loader.load_from_string(yaml_content)
        assert converted_back['scenario_id'] == 'test_conversion'
        print("✅ Обратная загрузка успешна!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конвертации: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Запуск тестов YAML загрузчика...\n")
    
    success = True
    success &= test_yaml_loader()
    success &= test_json_to_yaml_conversion()
    
    if success:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! YAML loader готов к использованию")
    else:
        print("\n❌ Есть ошибки в тестах")
        sys.exit(1) 