#!/usr/bin/env python3
"""
⚡ Быстрый тест исправленной логики агентов
"""

import asyncio
import sys
import os
from datetime import datetime

# Добавляем путь к KittyCore
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig

async def test_quick_fix():
    """Быстрый тест что агенты работают"""
    
    print("⚡ === БЫСТРЫЙ ТЕСТ ИСПРАВЛЕННЫХ АГЕНТОВ ===")
    
    # Создаём конфигурацию
    config = UnifiedConfig(
        vault_path="./vault_quick_test",
        enable_amem_memory=True,
        enable_smart_validation=False,  # Отключаем для скорости
        max_agents=1
    )
    
    # Инициализируем оркестратор
    orchestrator = UnifiedOrchestrator(config)
    print(f"🧠 A-MEM готов: {type(orchestrator.amem_system).__name__}")
    
    # Простая задача
    task = "Создай файл hello.py с print('Hello, World!')"
    
    print(f"\n📋 Тестируем: {task}")
    start_time = datetime.now()
    
    try:
        result = await orchestrator.solve_task(task)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print(f"\n✅ РЕЗУЛЬТАТ:")
        print(f"   🎯 Успех: {result.get('success', False)}")
        print(f"   📁 Файлов: {len(result.get('files_created', []))}")
        print(f"   ⏱️ Время: {execution_time:.1f}с")
        print(f"   📝 Статус: {result.get('status', 'unknown')}")
        
        if result.get('files_created'):
            print(f"   📂 Создано: {result['files_created']}")
        
        # Проверим A-MEM
        if orchestrator.amem_system:
            try:
                memories = await orchestrator.amem_system.search_memories("план выполнение", limit=5)
                print(f"   🧠 A-MEM воспоминаний: {len(memories)}")
            except Exception as e:
                print(f"   ⚠️ A-MEM ошибка: {e}")
        
        if result.get('success'):
            print("\n🎉 АГЕНТЫ РАБОТАЮТ! Синтаксис исправлен!")
        else:
            print("\n⚠️ Агенты стартуют, но есть проблемы выполнения")
            
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("Нужно дополнительное исправление")

if __name__ == "__main__":
    asyncio.run(test_quick_fix()) 