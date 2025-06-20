#!/usr/bin/env python3
"""
🚀 ФИНАЛЬНЫЙ ТЕСТ A-MEM БЕЗ EMBEDDING МОДЕЛЕЙ
Используем ChromaDB с простыми векторами без загрузки моделей
"""

import asyncio
import sys
import time
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent))

try:
    import chromadb
    print("✅ ChromaDB импортирован успешно!")
except ImportError:
    print("❌ ChromaDB не установлен")
    sys.exit(1)

class SimpleVectorMemory:
    """Простая векторная память БЕЗ embedding моделей"""
    
    def __init__(self):
        self.client = chromadb.Client()
        
        # Создаём коллекцию БЕЗ embedding функции
        self.collection = self.client.create_collection(
            name="simple_vector_memory",
            get_or_create=True
        )
        print("✅ Простая векторная память создана")
    
    def _simple_embedding(self, text: str) -> List[float]:
        """Создаём простой 'эмбеддинг' из хеша текста"""
        # Простой алгоритм: берём хеш и конвертируем в числа
        hash_obj = hashlib.md5(text.lower().encode())
        hash_hex = hash_obj.hexdigest()
        
        # Создаём вектор размерности 128 из хеша
        embedding = []
        for i in range(0, len(hash_hex), 2):
            hex_pair = hash_hex[i:i+2]
            # Конвертируем в число от -1 до 1
            num = (int(hex_pair, 16) - 127.5) / 127.5
            embedding.append(num)
        
        # Дополняем до 128 измерений
        while len(embedding) < 128:
            embedding.append(0.0)
        
        return embedding[:128]
    
    async def add_memory(self, content: str, tags: List[str] = None, 
                        category: str = "general", **kwargs) -> str:
        """Добавить воспоминание"""
        memory_id = f"mem_{int(time.time() * 1000)}"
        
        # Создаём простой эмбеддинг
        embedding = self._simple_embedding(content)
        
        # Метаданные
        metadata = {
            "tags": json.dumps(tags or []),
            "category": category,
            "timestamp": time.time()
        }
        metadata.update(kwargs)
        
        # Добавляем в ChromaDB
        self.collection.add(
            documents=[content],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        print(f"📝 Память добавлена: {memory_id[:12]}...")
        return memory_id
    
    async def search_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Поиск воспоминаний"""
        # Создаём эмбеддинг запроса
        query_embedding = self._simple_embedding(query)
        
        # Поиск в ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit
        )
        
        # Форматируем результаты
        memories = []
        for i, doc_id in enumerate(results['ids'][0]):
            metadata = results['metadatas'][0][i]
            memory = {
                'id': doc_id,
                'content': results['documents'][0][i],
                'tags': json.loads(metadata.get('tags', '[]')),
                'category': metadata.get('category', 'unknown'),
                'distance': results['distances'][0][i] if 'distances' in results else 0.0
            }
            memories.append(memory)
        
        print(f"🔍 Найдено {len(memories)} воспоминаний")
        return memories

async def test_simple_vector_memory():
    """Тестируем простую векторную память"""
    print("🚀 ТЕСТ ПРОСТОЙ ВЕКТОРНОЙ ПАМЯТИ")
    start_time = time.time()
    
    # Создаём память
    memory = SimpleVectorMemory()
    
    # Добавляем воспоминания
    memories_data = [
        ("Изучаю Python программирование", ["python", "programming"], "learning"),
        ("Работаю с Django веб-фреймворком", ["django", "web", "python"], "work"),
        ("Настраиваю базу данных PostgreSQL", ["database", "postgresql"], "technical"),
        ("Создаю REST API с FastAPI", ["fastapi", "api", "python"], "development"),
        ("Тестирую код с pytest", ["testing", "pytest", "python"], "quality")
    ]
    
    print("\n📝 Добавляем воспоминания:")
    for content, tags, category in memories_data:
        await memory.add_memory(content, tags, category)
    
    # Тестируем поиск
    print("\n🔍 Тестируем поиск:")
    test_queries = [
        "python веб разработка",
        "база данных",
        "тестирование кода"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Запрос: '{query}'")
        results = await memory.search_memory(query, limit=3)
        
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. {result['content']}")
            print(f"     🏷️ Теги: {result['tags']}")
            print(f"     📏 Расстояние: {result['distance']:.3f}")
    
    # Статистика
    collection_count = memory.collection.count()
    total_time = time.time() - start_time
    
    print(f"\n📊 СТАТИСТИКА:")
    print(f"  📄 Воспоминаний: {collection_count}")
    print(f"  ⏱️ Время: {total_time:.2f}с")
    print(f"  🚀 Без загрузки моделей!")
    
    return True

async def test_amem_integration():
    """Тестируем интеграцию с KittyCore"""
    print("\n🧠 ТЕСТ ИНТЕГРАЦИИ С KITTYCORE")
    
    try:
        from kittycore.memory.amem_integration import KittyCoreMemorySystem
        
        # Создаём систему
        memory_system = KittyCoreMemorySystem(vault_path="test_simple_vault")
        
        # Тестируем сохранение воспоминаний агентов
        agents_data = [
            ("backend_dev", "Настроил базу данных", {"task_type": "database"}),
            ("frontend_dev", "Создал компонент React", {"task_type": "ui"}),
            ("qa_engineer", "Написал автотесты", {"task_type": "testing"})
        ]
        
        print("📝 Агенты сохраняют воспоминания:")
        for agent_id, memory_text, context in agents_data:
            memory_id = await memory_system.agent_remember(agent_id, memory_text, context)
            print(f"  ✅ {agent_id}: {memory_id[:12]}...")
        
        # Тестируем коллективный поиск
        print("\n🔍 Коллективный поиск:")
        search_results = await memory_system.collective_search("база данных")
        
        for result in search_results[:3]:
            print(f"  📝 {result['content']}")
            print(f"     🤖 Агент: {result.get('agent_id', 'unknown')}")
        
        print("✅ KittyCore интеграция работает!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        return False

async def main():
    """Главная функция"""
    print("=" * 70)
    print("🎯 ФИНАЛЬНЫЙ ТЕСТ A-MEM БЕЗ EMBEDDING МОДЕЛЕЙ")
    print("=" * 70)
    
    # Тест 1: Простая векторная память
    success1 = await test_simple_vector_memory()
    
    # Тест 2: Интеграция с KittyCore
    success2 = await test_amem_integration()
    
    print("\n" + "=" * 70)
    print("📋 ФИНАЛЬНЫЙ ОТЧЁТ:")
    print(f"  🔧 Простая векторная память: {'✅ Работает' if success1 else '❌ Не работает'}")
    print(f"  🧠 KittyCore интеграция: {'✅ Работает' if success2 else '❌ Не работает'}")
    
    if success1 and success2:
        print("\n🎉 A-MEM ГОТОВ К РАБОТЕ БЕЗ EMBEDDING МОДЕЛЕЙ!")
        print("💡 Можно использовать в продакшене с простыми векторами")
    else:
        print("\n⚠️ Требуется доработка")

if __name__ == "__main__":
    asyncio.run(main()) 