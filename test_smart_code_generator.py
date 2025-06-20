#!/usr/bin/env python3
"""
🧪 ТЕСТ SMART CODE GENERATOR
Проверяем работу нового умного генератора кода на задаче calculator.py
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к kittycore
sys.path.append('.')

from kittycore.tools.smart_code_generator import SmartCodeGenerator


async def test_calculator_generation():
    """Тестирует генерацию калькулятора через SmartCodeGenerator"""
    
    print("🧪 ТЕСТ SMART CODE GENERATOR")
    print("=" * 50)
    
    # Создаём генератор
    generator = SmartCodeGenerator(agent_id="test_agent")
    
    # Задача как в реальном сценарии
    task_description = "Создай Python файл calculator.py с функциями сложения, вычитания, умножения и деления"
    filename = "calculator_smart.py"
    
    print(f"📝 Задача: {task_description}")
    print(f"📁 Файл: {filename}")
    print()
    
    try:
        # Генерируем код
        print("🚀 Запускаем генерацию...")
        result = await generator.generate_python_script(task_description, filename)
        
        print("📊 РЕЗУЛЬТАТ ГЕНЕРАЦИИ:")
        print(f"✅ Успех: {result.get('success', False)}")
        print(f"📝 Сообщение: {result.get('message', 'Нет сообщения')}")
        print(f"📁 Файл: {result.get('filename', 'Не указан')}")
        print(f"📏 Размер кода: {result.get('code_length', 0)} символов")
        print(f"🔧 Функций: {result.get('functions_count', 0)}")
        print(f"✅ Синтаксис валиден: {result.get('syntax_valid', False)}")
        print()
        
        if result.get('success'):
            # Проверяем содержимое файла
            file_path = Path("outputs") / filename
            if file_path.exists():
                print("📖 СОДЕРЖИМОЕ ФАЙЛА:")
                print("-" * 30)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(content)
                print("-" * 30)
                print()
                
                # Анализируем качество
                await analyze_generated_code(content, task_description)
            else:
                print("❌ Файл не найден!")
        
        return result
        
    except Exception as e:
        print(f"❌ ОШИБКА ТЕСТА: {e}")
        return {"success": False, "error": str(e)}


async def analyze_generated_code(code: str, original_task: str):
    """Анализирует качество сгенерированного кода"""
    
    print("🔍 АНАЛИЗ КАЧЕСТВА КОДА:")
    
    # Проверки качества
    checks = {
        "has_add_function": "def add(" in code,
        "has_subtract_function": "def subtract(" in code,
        "has_multiply_function": "def multiply(" in code,
        "has_divide_function": "def divide(" in code,
        "has_main_function": "def main(" in code,
        "has_if_name_main": 'if __name__ == "__main__"' in code,
        "has_docstrings": '"""' in code or "'''" in code,
        "has_arithmetic_operations": any(op in code for op in ['+', '-', '*', '/']),
        "not_just_description": not any(word in code.lower() for word in ['задача:', 'выполнено агентом', 'результат работы']),
        "reasonable_length": len(code) > 200  # Больше чем просто описание
    }
    
    # Подсчёт качества
    passed = sum(checks.values())
    total = len(checks)
    quality_score = (passed / total) * 100
    
    print(f"📊 ДЕТАЛЬНАЯ ОЦЕНКА:")
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {passed}")
    
    print()
    print(f"🎯 ИТОГОВАЯ ОЦЕНКА: {quality_score:.1f}/100")
    
    if quality_score >= 80:
        print("🏆 ОТЛИЧНО - код соответствует требованиям!")
    elif quality_score >= 60:
        print("⚠️ УДОВЛЕТВОРИТЕЛЬНО - есть что улучшить")
    else:
        print("❌ НЕУДОВЛЕТВОРИТЕЛЬНО - требуется доработка")
    
    return quality_score


async def main():
    """Основная функция теста"""
    
    # Запускаем тест
    result = await test_calculator_generation()
    
    print("\n🏁 ИТОГИ ТЕСТА:")
    print(f"✅ SmartCodeGenerator работает: {result.get('success', False)}")
    
    if result.get('success'):
        print(f"🚀 SmartCodeGenerator готов к интеграции!")
    else:
        print(f"❌ Требуется доработка: {result.get('error', 'неизвестная ошибка')}")


if __name__ == "__main__":
    asyncio.run(main()) 