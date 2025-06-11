#!/usr/bin/env python3
"""
🧪 Ручной тест CLI с несколькими задачами
"""

import asyncio
from kittycore_cli import process_request

async def run_tests():
    """Запуск тестов CLI"""
    
    test_cases = [
        {
            "name": "🌐 Создание сайта (ожидаем проблемы)",
            "task": "Сделай сайт с котятами",
            "expect_issues": True
        },
        {
            "name": "📊 Анализ (может быть быстро)",  
            "task": "посчитай плотность чёрной дыры",
            "expect_issues": False  # Это анализ, файлы не нужны
        },
        {
            "name": "📝 Создание файла (ожидаем файлы)",
            "task": "создай файл с планом на завтра", 
            "expect_issues": False  # Должно создать файл
        }
    ]
    
    print("🧪 РУЧНОЕ ТЕСТИРОВАНИЕ CLI")
    print("=" * 40)
    print("Система качества должна обнаруживать проблемы автоматически!")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Задача: '{test_case['task']}'")
        print(f"   Ожидаем проблемы: {'Да' if test_case['expect_issues'] else 'Нет'}")
        print("   " + "="*50)
        
        try:
            await process_request(test_case['task'])
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print("   " + "="*50)
        
        # Небольшая пауза между тестами
        await asyncio.sleep(1)
    
    print(f"\n✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
    print(f"Система качества должна была показать проблемы для задач создания сайта")
    print(f"и нормальную работу для анализа и создания файлов.")

if __name__ == "__main__":
    asyncio.run(run_tests()) 