#!/usr/bin/env python3
"""Тест ToolValidatorAgent"""

from kittycore.agents.tool_validator_agent import create_tool_validator

def test_tool_validator():
    print("🔧 Тестируем ToolValidatorAgent")
    
    validator = create_tool_validator()
    
    # Проблемный план с неправильными инструментами
    bad_plan = {
        'steps': [
            {
                'step': 1, 
                'action': 'создать файл', 
                'tool': '`code_generator`.', 
                'params': {'filename': 'test.py'}
            },
            {
                'step': 2, 
                'action': 'поиск в интернете', 
                'tool': 'Python Interpreter', 
                'params': {'query': 'test'}
            },
            {
                'step': 3, 
                'action': 'запуск', 
                'tool': 'Live Server', 
                'params': {}
            }
        ]
    }
    
    print("\n📋 Исходный план:")
    for step in bad_plan['steps']:
        print(f"  Шаг {step['step']}: {step['tool']}")
    
    print("\n🔍 Валидация:")
    result = validator.validate_plan(bad_plan)
    
    print(f"\n📊 Результат:")
    print(f"  ✅ Валиден: {result.is_valid}")
    print(f"  🔧 Исправлений: {len(result.corrections_made)}")
    print(f"  ❌ Ошибок: {len(result.validation_errors)}")
    
    print(f"\n📝 Исправленный план:")
    for step in result.corrected_steps:
        print(f"  Шаг {step['step']}: {step['tool']}")
    
    return result

if __name__ == "__main__":
    test_tool_validator() 