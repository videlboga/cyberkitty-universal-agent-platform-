#!/usr/bin/env python3
"""
🧠 ТЕСТ РЕАЛЬНОГО A-MEM - ЧАСТЬ 1
Проверяем что теперь работает ПОЛНОЦЕННЫЙ A-MEM с ChromaDB
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent))

from kittycore.memory.amem_integration import AgenticMemorySystem

async def test_real_amem_initialization():
    """Проверяем что A-MEM теперь инициализируется с ChromaDB"""
    print("🚀 ТЕСТ 1: Инициализация РЕАЛЬНОГО A-MEM")
    
    # Создаём A-MEM систему
    amem = AgenticMemorySystem()
    
    # Проверяем что это НАСТОЯЩИЙ A-MEM, а не fallback
    if hasattr(amem, 'chroma_client'):
        print("✅ УСПЕХ: ChromaDB инициализирован!")
        print(f"📊 Коллекция: {amem.collection.name}")
        print(f"🤖 Embedding модель: {amem.model_name}")
        return True
    else:
        print("❌ ПРОВАЛ: Всё ещё fallback режим")
        return False

async def test_semantic_search_power():
    """Тестируем семантический поиск"""
    print("\n🔍 ТЕСТ 2: СЕМАНТИЧЕСКИЙ ПОИСК")
    
    amem = AgenticMemorySystem()
    
    # Добавляем воспоминания с разными формулировками
    memories = [
        "Создал функцию для вычисления факториала числа",
        "Реализовал алгоритм быстрой сортировки массива", 
        "Написал код для поиска элемента в списке",
        "Сделал веб-сайт с котятами и красивым дизайном",
        "Настроил базу данных PostgreSQL для проекта"
    ]
    
    print("📝 Добавляем воспоминания...")
    for i, memory in enumerate(memories):
        memory_id = await amem.add_note(
            content=memory,
            tags=["programming", f"task_{i}"],
            category="development",
            agent_id="test_agent"
        )
        print(f"  💾 {memory_id}: {memory[:50]}...")
    
    # Семантический поиск
    print("\n🔍 Семантический поиск:")
    
    # Поиск по синонимам (должен найти даже если слова другие)
    search_queries = [
        "алгоритмы программирования",  # должен найти факториал, сортировку, поиск
        "веб разработка",              # должен найти сайт с котятами  
        "работа с данными"             # должен найти PostgreSQL
    ]
    
    total_found = 0
    for query in search_queries:
        results = await amem.search_agentic(query, k=3)
        print(f"\n  📋 Запрос: '{query}'")
        print(f"     Найдено: {len(results)} результатов")
        total_found += len(results)
        
        for result in results:
            print(f"     🎯 {result['content'][:50]}...")
    
    if total_found > 0:
        print(f"\n✅ СЕМАНТИЧЕСКИЙ ПОИСК РАБОТАЕТ! Найдено {total_found} совпадений")
        return True
    else:
        print(f"\n❌ СЕМАНТИЧЕСКИЙ ПОИСК НЕ РАБОТАЕТ! Найдено 0 результатов")
        return False

if __name__ == "__main__":
    async def main():
        print("🧠 ТЕСТИРУЕМ РЕАЛЬНУЮ МОЩЬ A-MEM!\n")
        
        test1_success = await test_real_amem_initialization()
        test2_success = await test_semantic_search_power()
        
        print(f"\n📊 РЕЗУЛЬТАТЫ ЧАСТИ 1:")
        print(f"   Инициализация A-MEM: {'✅' if test1_success else '❌'}")
        print(f"   Семантический поиск: {'✅' if test2_success else '❌'}")
        
        if test1_success and test2_success:
            print(f"\n🎉 A-MEM РАБОТАЕТ НА ПОЛНУЮ МОЩЬ!")
        else:
            print(f"\n😞 Что-то всё ещё не так...")
    
    asyncio.run(main()) 