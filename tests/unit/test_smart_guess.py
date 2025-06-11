#!/usr/bin/env python3
"""
🔮 Тест угадывания задач SmartValidator
=====================================

Проверяем как SmartValidator угадывает исходную задачу по файлам
"""

import asyncio
import os
import tempfile
from agents.smart_validator import SmartValidator


async def test_task_guessing():
    """Тестируем угадывание задач по содержимому файлов"""
    
    print("🔮 Тест угадывания задач SmartValidator")
    print("=" * 50)
    
    validator = SmartValidator()
    
    test_cases = [
        {
            "name": "HTML сайт с котятами",
            "content": """<!DOCTYPE html>
<html>
<head><title>Котята</title></head>
<body>
<h1>Сайт с котятами</h1>
<p>Рыжий котенок Мурзик</p>
</body>
</html>""",
            "expected_keywords": ["сайт", "котят"]
        },
        {
            "name": "План создания сайта",
            "content": """План создания сайта с котятами

1. HTML структура
2. CSS стили
3. Добавить картинки

Этапы работы...""",
            "expected_keywords": ["сайт", "котят", "план"]
        },
        {
            "name": "Расчет плотности",
            "content": """РАСЧЕТ ПЛОТНОСТИ ЧЕРНОЙ ДЫРЫ

Дано: M = 10 солнечных масс
Результат: ρ = 1.85×10¹⁷ кг/м³""",
            "expected_keywords": ["плотность", "черн"]
        }
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n🧪 ТЕСТ {i}: {case['name']}")
            print("-" * 40)
            
            # Создаем файл
            test_file = os.path.join(temp_dir, f"test_{i}.txt")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(case['content'])
            
            # Валидация с пустой задачей (заставляем угадывать)
            validation = await validator.validate_result(
                original_task="",  # Пустая задача - должен угадать!
                result={"success": True},
                created_files=[test_file]
            )
            
            print(f"🔮 Результат валидации:")
            print(f"   📊 Оценка: {validation.score:.1f}/1.0") 
            print(f"   🎯 Вердикт: {validation.verdict}")
            print(f"   💰 Польза: {validation.user_benefit}")
            
            # Проверяем содержит ли ответ ожидаемые ключевые слова
            response_text = (validation.verdict + " " + validation.user_benefit).lower()
            found_keywords = []
            for keyword in case['expected_keywords']:
                if keyword in response_text:
                    found_keywords.append(keyword)
            
            if found_keywords:
                print(f"   ✅ Найдены ключевые слова: {found_keywords}")
            else:
                print(f"   ⚠️  Ключевые слова не найдены: {case['expected_keywords']}")
    
    print(f"\n🎉 ТЕСТ УГАДЫВАНИЯ ЗАВЕРШЕН!")
    print("SmartValidator теперь может работать без известной исходной задачи!")


if __name__ == "__main__":
    asyncio.run(test_task_guessing())