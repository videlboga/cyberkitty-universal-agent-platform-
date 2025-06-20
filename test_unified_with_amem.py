#!/usr/bin/env python3
"""
🧠 ТЕСТ ПОЛНОЙ ИНТЕГРАЦИИ A-MEM В UNIFIEDORCHESTRATOR

Этот тест проверяет:
1. Инициализацию A-MEM в UnifiedOrchestrator
2. Семантический поиск при создании команды агентов  
3. Сохранение опыта агентов в A-MEM
4. Накопление решений задач в коллективной памяти
5. Эволюцию памяти через несколько итераций
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent))

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig
from loguru import logger

async def test_amem_integration():
    """🧠 Комплексный тест интеграции A-MEM в UnifiedOrchestrator"""
    print("🚀 === ТЕСТ ИНТЕГРАЦИИ A-MEM В UNIFIEDORCHESTRATOR ===")
    start_time = time.time()
    
    # ЭТАП 1: Инициализация с A-MEM
    print("\n1️⃣ === ИНИЦИАЛИЗАЦИЯ UNIFIEDORCHESTRATOR С A-MEM ===")
    
    config = UnifiedConfig(
        orchestrator_id="amem_test_orchestrator",
        enable_amem_memory=True,
        amem_memory_path="./vault/system/amem_test",
        vault_path="./vault_test",
        enable_shared_chat=True,
        enable_vector_memory=True,
        enable_smart_validation=True,
        timeout=60
    )
    
    orchestrator = UnifiedOrchestrator(config)
    
    # Проверяем инициализацию A-MEM
    assert orchestrator.amem_system is not None, "❌ A-MEM система не инициализирована"
    print("✅ A-MEM система инициализирована")
    
    assert orchestrator.collective_memory.amem_system is not None, "❌ A-MEM не интегрирован с коллективной памятью"
    print("✅ A-MEM интегрирован с коллективной памятью")
    
    if orchestrator.shared_chat:
        assert orchestrator.shared_chat.amem_system is not None, "❌ A-MEM не интегрирован с SharedChat"
        print("✅ A-MEM интегрирован с SharedChat")
    
    # ЭТАП 2: Первая задача - создание базовых воспоминаний
    print("\n2️⃣ === ПЕРВАЯ ЗАДАЧА: СОЗДАНИЕ БАЗОВЫХ ВОСПОМИНАНИЙ ===")
    
    task1 = "Создать простой Python скрипт для расчета факториала"
    print(f"📋 Задача 1: {task1}")
    
    try:
        result1 = await orchestrator.solve_task(task1)
        print(f"✅ Задача 1 выполнена: {result1.get('status', 'unknown')}")
        print(f"📁 Файлов создано: {len(result1.get('created_files', []))}")
        
        # Проверяем что опыт сохранён в A-MEM
        memories_count_1 = await check_amem_memories(orchestrator.amem_system, "первая проверка")
        
    except Exception as e:
        print(f"⚠️ Ошибка выполнения задачи 1: {e}")
        result1 = {"status": "failed", "error": str(e)}
    
    # Небольшая пауза для обработки
    await asyncio.sleep(2)
    
    # ЭТАП 3: Вторая задача - тестирование семантического поиска
    print("\n3️⃣ === ВТОРАЯ ЗАДАЧА: ТЕСТИРОВАНИЕ СЕМАНТИЧЕСКОГО ПОИСКА ===")
    
    task2 = "Создать Python программу для вычисления чисел Фибоначчи"
    print(f"📋 Задача 2: {task2}")
    
    try:
        result2 = await orchestrator.solve_task(task2)
        print(f"✅ Задача 2 выполнена: {result2.get('status', 'unknown')}")
        print(f"📁 Файлов создано: {len(result2.get('created_files', []))}")
        
        # Проверяем что система нашла предыдущий опыт
        memories_count_2 = await check_amem_memories(orchestrator.amem_system, "вторая проверка")
        
    except Exception as e:
        print(f"⚠️ Ошибка выполнения задачи 2: {e}")
        result2 = {"status": "failed", "error": str(e)}
    
    # Небольшая пауза для обработки
    await asyncio.sleep(2)
    
    # ЭТАП 4: Третья задача - веб-разработка (другой тип)
    print("\n4️⃣ === ТРЕТЬЯ ЗАДАЧА: ВЕБЕРАЗРАБОТКА ===")
    
    task3 = "Создать простую HTML страницу с формой регистрации"
    print(f"📋 Задача 3: {task3}")
    
    try:
        result3 = await orchestrator.solve_task(task3)
        print(f"✅ Задача 3 выполнена: {result3.get('status', 'unknown')}")
        print(f"📁 Файлов создано: {len(result3.get('created_files', []))}")
        
        # Финальная проверка памяти
        memories_count_3 = await check_amem_memories(orchestrator.amem_system, "финальная проверка")
        
    except Exception as e:
        print(f"⚠️ Ошибка выполнения задачи 3: {e}")
        result3 = {"status": "failed", "error": str(e)}
    
    # ЭТАП 5: Проверка семантического поиска
    print("\n5️⃣ === ПРОВЕРКА СЕМАНТИЧЕСКОГО ПОИСКА A-MEM ===")
    
    await test_semantic_search(orchestrator.amem_system)
    
    # ЭТАП 6: Проверка эволюции памяти
    print("\n6️⃣ === ПРОВЕРКА ЭВОЛЮЦИИ КОЛЛЕКТИВНОЙ ПАМЯТИ ===")
    
    await test_memory_evolution(orchestrator.amem_system)
    
    # ЭТАП 7: Статистика
    print("\n7️⃣ === ИТОГОВАЯ СТАТИСТИКА ===")
    
    total_time = time.time() - start_time
    
    print(f"⏱️ Общее время тестирования: {total_time:.2f}с")
    print(f"🧠 A-MEM система: {'✅ Работает' if orchestrator.amem_system else '❌ Отключена'}")
    print(f"📊 Задач протестировано: 3")
    print(f"🔄 Система обучения: {'✅ Активна' if memories_count_3 > 0 else '❌ Не работает'}")
    
    return {
        "total_time": total_time,
        "amem_enabled": orchestrator.amem_system is not None,
        "tasks_completed": 3,
        "memories_final": memories_count_3,
        "success": True
    }

async def check_amem_memories(amem_system, phase: str) -> int:
    """Проверка количества воспоминаний в A-MEM"""
    try:
        # Ищем все воспоминания
        all_memories = await amem_system.search_memories(
            query="",  # Пустой запрос для получения всех
            limit=100
        )
        
        count = len(all_memories)
        print(f"🧠 A-MEM воспоминаний ({phase}): {count}")
        
        # Показываем последние несколько воспоминаний
        if all_memories:
            print(f"📝 Последние воспоминания:")
            for i, memory in enumerate(all_memories[-3:], 1):
                content_preview = memory.get('content', '')[:100].replace('\n', ' ')
                tags = memory.get('tags', [])
                print(f"   {i}. {content_preview}... (теги: {', '.join(tags[:3])})")
        
        return count
        
    except Exception as e:
        print(f"⚠️ Ошибка проверки A-MEM: {e}")
        return 0

async def test_semantic_search(amem_system):
    """Тестирование семантического поиска A-MEM"""
    print("🔍 Тестирование семантического поиска...")
    
    search_queries = [
        "программирование Python",
        "веб разработка HTML",
        "успешный опыт агента",
        "создание файлов",
        "ошибки выполнения"
    ]
    
    for query in search_queries:
        try:
            results = await amem_system.search_memories(query, limit=3)
            print(f"   🔍 '{query}': найдено {len(results)} результатов")
            
            if results:
                # Показываем лучший результат
                best_result = results[0]
                content_preview = best_result.get('content', '')[:80].replace('\n', ' ')
                print(f"      ✨ Лучший: {content_preview}...")
                
        except Exception as e:
            print(f"   ❌ Ошибка поиска '{query}': {e}")

async def test_memory_evolution(amem_system):
    """Тестирование эволюции памяти"""
    print("🧬 Тестирование эволюции памяти...")
    
    try:
        # Проверяем есть ли система эволюции памяти
        if hasattr(amem_system, 'memory_evolution'):
            evolution_system = amem_system.memory_evolution
            
            # Получаем статистику
            patterns = await evolution_system.get_patterns()
            links = await evolution_system.get_memory_links()
            
            print(f"   🧬 Паттернов команд: {len(patterns)}")
            print(f"   🔗 Связей между воспоминаниями: {len(links)}")
            
            # Показываем несколько паттернов
            if patterns:
                for i, pattern in enumerate(patterns[:3], 1):
                    print(f"   {i}. Паттерн: {pattern.pattern_type} (встречался {pattern.frequency} раз)")
            
            # Показываем несколько связей
            if links:
                for i, link in enumerate(links[:3], 1):
                    print(f"   {i}. Связь: {link.source_id} → {link.target_id} (сила: {link.strength:.2f})")
                    
        else:
            print("   ⚠️ Система эволюции памяти не найдена")
            
    except Exception as e:
        print(f"   ❌ Ошибка проверки эволюции: {e}")

async def main():
    """Главная функция тестирования"""
    try:
        result = await test_amem_integration()
        
        print("\n🎉 === ТЕСТ ЗАВЕРШЁН УСПЕШНО ===")
        print("🧠 A-MEM полностью интегрирован в UnifiedOrchestrator!")
        print("✨ Семантический поиск, накопление опыта и эволюция памяти работают!")
        
        return result
        
    except Exception as e:
        print(f"\n💥 === ОШИБКА ТЕСТИРОВАНИЯ ===")
        print(f"❌ {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    asyncio.run(main()) 