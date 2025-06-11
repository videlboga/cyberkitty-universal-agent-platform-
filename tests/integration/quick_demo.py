#!/usr/bin/env python3
"""
🚀 БЫСТРОЕ ДЕМО УНИВЕРСАЛЬНОЙ СИСТЕМЫ
"""

import asyncio
from universal_task_handler import UniversalTaskHandler

async def quick_demo():
    """Быстрые демо разных типов задач"""
    
    handler = UniversalTaskHandler()
    
    # Тестируем разные типы задач
    test_cases = [
        "Создай логотип для стартапа",  # Простая задача
        "Проанализируй конкурентов и создай стратегию продвижения",  # Сложная задача
        "Рассчитай ROI для рекламной кампании"  # Простая задача
    ]
    
    for i, task in enumerate(test_cases, 1):
        print(f"\n{'🔥'*20} ТЕСТ {i}/3 {'🔥'*20}")
        await handler.process_text_request(task)
        print(f"{'✅'*20} ЗАВЕРШЕНО {'✅'*20}")

if __name__ == "__main__":
    asyncio.run(quick_demo()) 