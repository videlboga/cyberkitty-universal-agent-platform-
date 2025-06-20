#!/usr/bin/env python3
"""
🧪 Тест интеграции SmartValidator в ObsidianOrchestrator
"""

import asyncio
from kittycore.core.obsidian_orchestrator import solve_with_obsidian_orchestrator

async def test_smart_integration():
    print("🧪 ТЕСТ ИНТЕГРАЦИИ SmartValidator")
    print("=" * 50)
    
    # Простая задача для теста
    task = "Создай Python скрипт для вычисления факториала числа"
    
    try:
        result = await solve_with_obsidian_orchestrator(task)
        
        print(f"✅ Статус: {result['status']}")
        print(f"⏱️ Время: {result['duration']:.1f}с")
        print(f"🤖 Агентов: {result['agents_created']}")
        
        # Проверяем валидацию в результатах
        validation_found = False
        for step_id, step_result in result['execution']['step_results'].items():
            if 'validation' in step_result:
                validation = step_result['validation']
                print(f"🔍 Валидация шага {step_id}: {validation.get('verdict', 'нет данных')}")
                if 'score' in validation:
                    print(f"📊 Оценка: {validation['score']:.1f}/1.0")
                validation_found = True
        
        if validation_found:
            print("🎯 SmartValidator ИНТЕГРИРОВАН и работает!")
        else:
            print("❌ SmartValidator НЕ найден в результатах")
            
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")

if __name__ == "__main__":
    asyncio.run(test_smart_integration()) 