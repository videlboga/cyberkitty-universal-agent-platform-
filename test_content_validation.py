#!/usr/bin/env python3
"""
Тест системы валидации содержимого файлов
"""

import asyncio
import os
from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig

async def test_content_validation():
    """Тест валидации содержимого файлов"""
    
    # Создаём тестовые файлы
    test_files = {
        "good_hello.py": "print('Hello, World!')",
        "bad_hello.py": """<html>
<head><title>Отчёт о создании файла</title></head>
<body>
<div class="header">
    <h1>Результат выполнения задачи</h1>
    <p>Создан файл hello.py с кодом print('Hello, World!')</p>
</div>
</body>
</html>""",
        "fake_script.py": """
# Результат выполнения задачи
# Генерировано KittyCore 3.0 🐱
# TODO: Реализовать логику

def main():
    print("Задача обработана интеллектуальным агентом")

if __name__ == "__main__":
    main()
""",
        "valid_html.html": """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>""",
        "invalid_json.json": "{ invalid json content }",
        "valid_json.json": '{"message": "Hello, World!", "status": "success"}'
    }
    
    # Создаём файлы
    for filename, content in test_files.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    try:
        # Создаём оркестратор
        config = UnifiedConfig(vault_path="./test_vault")
        orchestrator = UnifiedOrchestrator(config)
        
        # Тестируем валидацию содержимого
        print("🧪 Тестируем валидацию содержимого файлов...")
        
        task = "Создай файл hello.py с кодом print('Hello, World!')"
        expected_outcome = {
            'type': 'Создание файла с кодом Python',
            'description': 'Создание Python файла',
            'validation_criteria': ['Файл должен содержать print("Hello, World!")']
        }
        
        # Тестируем каждый файл
        for filename in test_files.keys():
            print(f"\n📁 Тестируем файл: {filename}")
            
            validation_result = await orchestrator._validate_file_contents(
                created_files=[filename],
                task=task,
                expected_outcome=expected_outcome
            )
            
            print(f"   📊 Бонус к оценке: {validation_result['score_bonus']:.2f}")
            print(f"   ✅ Детали: {validation_result['details']}")
            if validation_result['issues']:
                print(f"   ❌ Проблемы: {validation_result['issues']}")
        
        print("\n🎯 Тест завершён!")
        
    finally:
        # Удаляем тестовые файлы
        for filename in test_files.keys():
            if os.path.exists(filename):
                os.remove(filename)
        print("🧹 Тестовые файлы удалены")

if __name__ == "__main__":
    asyncio.run(test_content_validation()) 