#!/usr/bin/env python3
"""
Простой тест для отладки UnifiedOrchestrator
"""

import asyncio
import traceback
from pathlib import Path
from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig

async def simple_test():
    """Простой тест"""
    try:
        # Инициализация
        vault_path = Path("debug_vault")
        vault_path.mkdir(exist_ok=True)
        
        config = UnifiedConfig(vault_path=str(vault_path))
        orchestrator = UnifiedOrchestrator(config)
        
        # Простая задача
        task = "Создай файл hello.py с кодом print('Hello, World!')"
        
        print("🚀 Запуск простой задачи...")
        result = await orchestrator.solve_task(task)
        
        print("✅ Результат:")
        print(result)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n📋 Полный стек ошибки:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_test()) 