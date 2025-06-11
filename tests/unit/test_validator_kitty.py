#!/usr/bin/env python3
"""
🧪 Демо ValidatorKitty
"""

import asyncio
from core.validator_kitty import ValidatorKitty
# from core.memory_management import MemoryManager

async def demo_validator():
    """Демонстрация работы ValidatorKitty"""
    
    print("🧪 ДЕМО ValidatorKitty")
    print("=" * 30)
    
    # Создаем валидатор
    validator = ValidatorKitty()
    
    # Тестовые запросы
    test_requests = [
        "Сделай сайт с котятами",
        "создай файл с планом на завтра", 
        "посчитай плотность чёрной дыры"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{i}. 🔍 АНАЛИЗ ЗАПРОСА: '{request}'")
        print("-" * 40)
        
        # Анализируем запрос
        expectation = await validator.analyze_request(request)
        
        # Показываем образ результата
        expectation_text = validator.format_expectation_for_user(expectation)
        print(expectation_text)
        
        print("-" * 40)
    
    print("\n✅ ДЕМО ЗАВЕРШЕНО!")
    print("ValidatorKitty готов к работе!")

if __name__ == "__main__":
    asyncio.run(demo_validator()) 