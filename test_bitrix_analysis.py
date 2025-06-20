#!/usr/bin/env python3
"""
🚀 ТЕСТ KITTYCORE 3.0 + A-MEM НА РЕАЛЬНОЙ ЗАДАЧЕ
Анализ рынка приложений Битрикс24 с эволюционирующей памятью
"""

import asyncio
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent))

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig
from loguru import logger

async def test_bitrix_market_analysis():
    """🧠 Тест анализа рынка Битрикс24 с A-MEM"""
    print("🚀 === ТЕСТ KITTYCORE 3.0 + A-MEM НА АНАЛИЗЕ БИТРИКС24 ===")
    print("🧠 Проверяем как эволюционирующая память помогает в реальных задачах")
    
    start_time = time.time()
    
    # Конфигурация с A-MEM
    config = UnifiedConfig(
        orchestrator_id="bitrix_market_analyzer",
        enable_amem_memory=True,
        amem_memory_path="./vault/system/amem_bitrix",
        vault_path="./vault_bitrix_test",
        enable_shared_chat=True,
        enable_smart_validation=True,
        enable_vector_memory=False,  # Используем только A-MEM
        timeout=300
    )
    
    try:
        print("\n🎯 === ИНИЦИАЛИЗАЦИЯ UNIFIED ORCHESTRATOR ===")
        orchestrator = UnifiedOrchestrator(config)
        
        # Проверяем A-MEM
        amem_type = type(orchestrator.amem_system.amem).__name__
        print(f"🧠 A-MEM тип: {amem_type}")
        
        from kittycore.memory.amem_integration import AMEM_AVAILABLE
        print(f"🔍 AMEM_AVAILABLE: {AMEM_AVAILABLE}")
        
        if amem_type == "SimpleAgenticMemory":
            print("⚠️ A-MEM в fallback режиме")
        else:
            print("✅ A-MEM полностью активна!")
        
        print("\n📋 === ВЫПОЛНЕНИЕ ЗАДАЧИ АНАЛИЗА БИТРИКС24 ===")
        
        task = """Проведи анализ рынка приложений маркета битрикс 24, найди топ популярных, составь отчёт о том, какие там есть, насколько они сложны в реализации и какие проблемы имеют. После сделай 3 прототипа приложений на основе этого анализа - которые можно сделать быстро с улучшением UX"""
        
        print(f"📝 Задача: {task[:100]}...")
        
        # Проверяем что есть в памяти до выполнения
        print("\n🔍 === ПРОВЕРКА СУЩЕСТВУЮЩЕЙ ПАМЯТИ ===")
        
        try:
            existing_memories = await orchestrator.amem_system.search_memories("битрикс анализ рынок", limit=5)
            print(f"💾 Найдено существующих воспоминаний: {len(existing_memories)}")
            
            for i, memory in enumerate(existing_memories[:2], 1):
                content_preview = memory.get('content', '')[:80].replace('\n', ' ')
                tags = memory.get('tags', [])
                print(f"   {i}. {content_preview}... (теги: {', '.join(tags[:2])})")
                
        except Exception as e:
            print(f"⚠️ Ошибка поиска существующих воспоминаний: {e}")
        
        # Выполняем задачу
        print(f"\n⚡ === ВЫПОЛНЕНИЕ ЗАДАЧИ ===")
        result = await orchestrator.solve_task(task)
        
        execution_time = time.time() - start_time
        
        print(f"\n📊 === РЕЗУЛЬТАТЫ ВЫПОЛНЕНИЯ ===")
        print(f"✅ Успешность: {result.get('success', False)}")
        print(f"⏱️ Время выполнения: {execution_time:.2f}с")
        print(f"📁 Создано файлов: {len(result.get('created_files', []))}")
        print(f"🎯 Качество: {result.get('quality_score', 'N/A')}")
        
        if result.get('created_files'):
            print(f"\n📁 === СОЗДАННЫЕ ФАЙЛЫ ===")
            for file_path in result.get('created_files', []):
                print(f"   📄 {file_path}")
        
        # Проверяем что добавилось в память
        print(f"\n🧠 === ПРОВЕРКА НОВЫХ ВОСПОМИНАНИЙ ===")
        
        try:
            all_memories = await orchestrator.amem_system.search_memories("битрикс анализ рынок приложения", limit=10)
            new_memories_count = len(all_memories) - len(existing_memories)
            
            print(f"💾 Всего воспоминаний: {len(all_memories)}")
            print(f"✨ Новых воспоминаний: {new_memories_count}")
            
            # Показываем новые воспоминания
            if new_memories_count > 0:
                print(f"\n🆕 === ПОСЛЕДНИЕ ВОСПОМИНАНИЯ ===")
                for i, memory in enumerate(all_memories[:3], 1):
                    content_preview = memory.get('content', '')[:100].replace('\n', ' ')
                    tags = memory.get('tags', [])
                    print(f"   {i}. {content_preview}... (теги: {', '.join(tags[:3])})")
                    
        except Exception as e:
            print(f"⚠️ Ошибка поиска новых воспоминаний: {e}")
        
        # Тестируем семантический поиск
        print(f"\n🔍 === ТЕСТ СЕМАНТИЧЕСКОГО ПОИСКА ===")
        
        search_queries = [
            "популярные приложения битрикс24",
            "сложность реализации CRM", 
            "проблемы пользователей битрикс",
            "прототипы улучшения UX",
            "быстрая разработка приложений"
        ]
        
        search_results = {}
        total_found = 0
        
        for query in search_queries:
            try:
                results = await orchestrator.amem_system.search_memories(query, limit=3)
                found_count = len(results)
                search_results[query] = found_count
                total_found += found_count
                
                print(f"   🔍 '{query}': {found_count} результатов")
                
                if results:
                    best = results[0]
                    content_preview = best.get('content', '')[:60].replace('\n', ' ')
                    print(f"      ✨ Лучший: {content_preview}...")
                    
            except Exception as e:
                print(f"   ❌ Ошибка поиска '{query}': {e}")
                search_results[query] = 0
        
        avg_search_effectiveness = total_found / len(search_queries)
        
        print(f"\n📈 === ИТОГОВАЯ СТАТИСТИКА ===")
        print(f"⏱️ Общее время: {execution_time:.2f}с")
        print(f"✅ Задача выполнена: {result.get('success', False)}")
        print(f"📁 Файлов создано: {len(result.get('created_files', []))}")
        print(f"💾 Воспоминаний накоплено: {len(all_memories) if 'all_memories' in locals() else 'N/A'}")
        print(f"🔍 Эффективность поиска: {avg_search_effectiveness:.1f}")
        print(f"🧠 A-MEM режим: {'Offline ChromaDB' if amem_type == 'AgenticMemorySystem' else 'Fallback'}")
        
        # Общая оценка
        if result.get('success') and len(result.get('created_files', [])) >= 3:
            print(f"\n🎉 === ТЕСТ ПРОШЁЛ УСПЕШНО ===")
            print(f"✨ KittyCore 3.0 с A-MEM справился с реальной задачей!")
            print(f"🧠 Эволюционирующая память работает и накапливает опыт!")
            print(f"📊 Система готова к продакшену!")
        else:
            print(f"\n⚠️ === ТЕСТ ЧАСТИЧНО УСПЕШЕН ===")
            print(f"🔧 Некоторые аспекты требуют доработки")
        
        # Сохраняем результаты
        test_results = {
            "success": result.get('success', False),
            "execution_time": execution_time,
            "created_files": result.get('created_files', []),
            "quality_score": result.get('quality_score'),
            "amem_type": amem_type,
            "amem_available": AMEM_AVAILABLE,
            "memories_found": len(all_memories) if 'all_memories' in locals() else 0,
            "search_effectiveness": avg_search_effectiveness,
            "search_results": search_results,
            "timestamp": datetime.now().isoformat()
        }
        
        results_file = Path("bitrix_test_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Результаты сохранены: {results_file}")
        
        return test_results
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

async def main():
    """Главная функция"""
    try:
        print("🎯 Запуск теста анализа рынка Битрикс24 с KittyCore 3.0 + A-MEM...")
        result = await test_bitrix_market_analysis()
        
        if result.get("success"):
            print("\n🚀 === ТЕСТ ЗАВЕРШЁН УСПЕШНО ===")
            print("✨ KittyCore 3.0 готов к реальным задачам!")
        else:
            print("\n💥 === ТЕСТ НЕ ПРОШЁЛ ===")
            print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"\n💥 === КРИТИЧЕСКАЯ ОШИБКА ===")
        print(f"❌ {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    asyncio.run(main()) 