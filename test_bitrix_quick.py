#!/usr/bin/env python3
"""
⚡ БЫСТРЫЙ ТЕСТ A-MEM НА БИТРИКС24
Проверяем основные функции без полного выполнения
"""

import asyncio
import sys
import time
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent))

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig

async def quick_bitrix_test():
    """⚡ Быстрый тест A-MEM"""
    print("⚡ === БЫСТРЫЙ ТЕСТ A-MEM НА БИТРИКС24 ===")
    
    # Конфигурация
    config = UnifiedConfig(
        orchestrator_id="bitrix_quick_test",
        enable_amem_memory=True,
        vault_path="./vault_quick_test",
        enable_shared_chat=False,  # Отключаем для скорости
        enable_smart_validation=False,  # Отключаем для скорости
        timeout=60
    )
    
    try:
        print("🎯 Инициализация...")
        orchestrator = UnifiedOrchestrator(config)
        
        # Проверяем A-MEM
        amem_type = type(orchestrator.amem_system.amem).__name__
        print(f"🧠 A-MEM: {amem_type}")
        
        from kittycore.memory.amem_integration import AMEM_AVAILABLE
        print(f"✅ AMEM доступна: {AMEM_AVAILABLE}")
        
        if amem_type == "AgenticMemorySystem":
            print("🚀 A-MEM полностью активна!")
            
            # Тест сохранения памяти
            print("\n💾 Тест сохранения воспоминаний...")
            
            test_memories = [
                "Анализ рынка Битрикс24: найдены популярные CRM приложения",
                "Топ приложения: SalesBooster, ClientTracker, TaskManager Pro", 
                "Проблемы: сложный UX, медленная загрузка, высокая стоимость",
                "Прототип 1: Простой CRM дашборд с быстрой навигацией",
                "Прототип 2: Мобильное приложение для задач с offline режимом"
            ]
            
            for i, memory in enumerate(test_memories):
                await orchestrator.amem_system.store_memory(
                    content=memory,
                    agent_id=f"bitrix_analyzer_{i}",
                    tags=["битрикс24", "анализ", "рынок", "приложения"]
                )
                print(f"   ✅ Память {i+1} сохранена")
            
            # Тест семантического поиска
            print(f"\n🔍 Тест семантического поиска...")
            
            search_queries = [
                "популярные приложения битрикс24",
                "проблемы пользователей CRM",
                "прототипы улучшения UX",
                "быстрая разработка дашборд"
            ]
            
            total_found = 0
            for query in search_queries:
                results = await orchestrator.amem_system.search_memories(query, limit=2)
                found = len(results)
                total_found += found
                print(f"   🔍 '{query}': {found} результатов")
                
                if results:
                    best = results[0]
                    preview = best.get('content', '')[:50]
                    print(f"      ✨ {preview}...")
            
            effectiveness = total_found / len(search_queries)
            print(f"\n📊 Эффективность поиска: {effectiveness:.1f}")
            
            if effectiveness >= 1.0:
                print("🎉 A-MEM работает отлично!")
                success = True
            else:
                print("⚠️ A-MEM работает частично")
                success = False
                
        else:
            print("⚠️ A-MEM в fallback режиме")
            success = False
        
        return {"success": success, "amem_type": amem_type, "amem_available": AMEM_AVAILABLE}
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {"success": False, "error": str(e)}

async def main():
    """Главная функция"""
    start_time = time.time()
    
    result = await quick_bitrix_test()
    
    elapsed = time.time() - start_time
    print(f"\n⏱️ Время: {elapsed:.2f}с")
    
    if result.get("success"):
        print("✅ Быстрый тест прошёл успешно!")
        print("🚀 A-MEM готова к полному тесту на Битрикс24!")
    else:
        print("❌ Быстрый тест не прошёл")
        print(f"Ошибка: {result.get('error', 'Unknown')}")
    
    return result

if __name__ == "__main__":
    asyncio.run(main()) 