#!/usr/bin/env python3
"""
Простой тест SmartValidator
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'kittycore'))

from kittycore.agents.smart_validator import SmartValidator

async def test_validator():
    """Тест валидатора"""
    
    print("🧪 ТЕСТ SmartValidator")
    print("=" * 50)
    
    validator = SmartValidator()
    
    # Тест 1: Плохой результат (план вместо сайта)
    print("\n🔍 ТЕСТ 1: План вместо сайта")
    task1 = "Создай сайт с котятами"
    result1 = {"status": "completed", "output": "План создания сайта готов"}
    files1 = []
    
    try:
        validation1 = await validator.validate_result(task1, result1, files1)
        print(f"✅ Образ результата: {validation1.expected_result}")
        print(f"📊 Валидность: {validation1.is_valid}")
        print(f"🎯 Оценка: {validation1.score:.1f}/1.0")
        print(f"💬 Вердикт: {validation1.verdict}")
        if validation1.issues:
            print(f"❌ Проблемы: {', '.join(validation1.issues)}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест 2: Хороший результат (рабочий HTML)
    print("\n🔍 ТЕСТ 2: Рабочий HTML файл")
    task2 = "Создай сайт с котятами"
    result2 = {"status": "completed", "output": "Создан HTML файл"}
    
    # Создаём тестовый HTML файл
    test_html = "test_kittens.html"
    with open(test_html, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head><title>Котята</title></head>
<body>
    <h1>Сайт с котятами</h1>
    <img src="kitten.jpg" alt="Котёнок">
    <button onclick="alert('Мяу!')">Нажми меня</button>
</body>
</html>""")
    
    files2 = [test_html]
    
    try:
        validation2 = await validator.validate_result(task2, result2, files2)
        print(f"✅ Образ результата: {validation2.expected_result}")
        print(f"📊 Валидность: {validation2.is_valid}")
        print(f"🎯 Оценка: {validation2.score:.1f}/1.0")
        print(f"💬 Вердикт: {validation2.verdict}")
        if validation2.issues:
            print(f"❌ Проблемы: {', '.join(validation2.issues)}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        # Удаляем тестовый файл
        if os.path.exists(test_html):
            os.remove(test_html)
    
    print("\n🎯 ИТОГ: SmartValidator протестирован!")

if __name__ == "__main__":
    asyncio.run(test_validator()) 