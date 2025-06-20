#!/usr/bin/env python3
"""
🎯 РЕАЛЬНЫЙ ТЕСТ KITTYCORE 3.0 - АНАЛИЗ БИТРИКС24

Сложная многоэтапная задача:
1. Анализ рынка приложений Битрикс24
2. Топ популярных приложений  
3. Сложность реализации и проблемы
4. 3 прототипа для быстрой разработки
"""

import asyncio
import os
from pathlib import Path

# Настройки
os.environ["TIMEOUT"] = "30"  # Увеличиваем таймаут для сложной задачи
os.environ["MAX_TOKENS"] = "4000"  # Больше токенов для детального анализа

async def test_bitrix_analysis():
    print("🎯 РЕАЛЬНЫЙ ТЕСТ: АНАЛИЗ БИТРИКС24")
    print("="*50)
    
    task = """Проведи анализ рынка приложений маркета битрикс 24, найди топ популярных, составь отчёт о том, какие там есть, насколько они сложны в реализации и какие проблемы имеют. После сделай 3 прототипа приложений на основе этого анализа - которые можно сделать быстро с улучшением UX"""
    
    try:
        from kittycore.core.unified_orchestrator import UnifiedOrchestrator
        
        print("🚀 Запуск UnifiedOrchestrator...")
        orchestrator = UnifiedOrchestrator()
        
        print(f"📋 Задача: {task[:100]}...")
        
        # Выполняем задачу
        result = await orchestrator.solve_task(task)
        
        print("\n" + "="*50)
        print("🎯 РЕЗУЛЬТАТЫ:")
        print("="*50)
        
        if result:
            print(f"✅ Статус: {result.get('status', 'unknown')}")
            print(f"📊 Качество: {result.get('quality', 0):.2f}")
            print(f"⏱️ Время: {result.get('execution_time', 0):.1f}с")
            
            if 'files_created' in result:
                print(f"📁 Файлы: {result['files_created']}")
                
            if 'summary' in result:
                print(f"📝 Резюме: {result['summary'][:200]}...")
                
        else:
            print("❌ Результат не получен")
            
        # Проверяем созданные файлы
        print(f"\n📂 Проверяем созданные файлы в outputs/:")
        outputs_dir = Path("outputs")
        if outputs_dir.exists():
            files = list(outputs_dir.glob("*"))
            for file in files[-5:]:  # Показываем последние 5 файлов
                print(f"   📄 {file.name} ({file.stat().st_size} байт)")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_bitrix_analysis()) 