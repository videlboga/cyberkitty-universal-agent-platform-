#!/usr/bin/env python3
"""
🐱 СУПЕР ЛЁГКИЙ ТЕСТ A-MEM 
Используем paraphrase-MiniLM-L3-v2 (17.4M параметров, ~25MB)
"""

import asyncio
import sys
import time
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent))

from kittycore.memory.amem_integration import AgenticMemorySystem

async def test_lightweight_amem():
    """Тест с лёгкой моделью"""
    print("🚀 ТЕСТ ЛЁГКОГО A-MEM")
    print(f"📦 Модель: paraphrase-MiniLM-L3-v2 (17.4M параметров)")
    
    start_time = time.time()
    
    # Создаём A-MEM с лёгкой моделью
    amem = AgenticMemorySystem(model_name='paraphrase-MiniLM-L3-v2')
    
    init_time = time.time() - start_time
    print(f"⏱️ Инициализация: {init_time:.2f}с")
    
    # Проверяем что это НАСТОЯЩИЙ A-MEM
    if hasattr(amem, 'chroma_client'):
        print("✅ ChromaDB инициализирован!")
        print(f"📊 Коллекция: {amem.collection.name}")
        print(f"🤖 Модель: {amem.model_name}")
    else:
        print("❌ Fallback режим")
        return False
    
    # Добавляем простые воспоминания
    print("\n📝 Добавляем воспоминания...")
    memories = [
        "Создал Python скрипт",
        "Написал HTML страницу", 
        "Настроил базу данных"
    ]
    
    for memory in memories:
        await amem.add_note(
            content=memory,
            tags=["test"],
            category="development"
        )
        print(f"  💾 {memory}")
    
    # Тестируем семантический поиск
    print("\n🔍 Семантический поиск:")
    
    queries = ["программирование", "веб разработка", "данные"]
    total_found = 0
    
    for query in queries:
        results = await amem.search_agentic(query, k=2)
        print(f"  📋 '{query}': {len(results)} результатов")
        total_found += len(results)
        
        for result in results:
            print(f"    🎯 {result['content']}")
    
    total_time = time.time() - start_time
    print(f"\n⏱️ Общее время: {total_time:.2f}с")
    
    if total_found > 0:
        print("🎉 A-MEM РАБОТАЕТ С СЕМАНТИЧЕСКИМ ПОИСКОМ!")
        return True
    else:
        print("😞 Семантический поиск не работает")
        return False

if __name__ == "__main__":
    asyncio.run(test_lightweight_amem()) 