#!/usr/bin/env python3
"""
🧪 ТЕСТ ТОЛЬКО CHROMADB 
Проверяем что ChromaDB работает без embedding моделей
"""

import asyncio
import sys
import time
from pathlib import Path

try:
    import chromadb
    print("✅ ChromaDB импортирован успешно!")
except ImportError:
    print("❌ ChromaDB не установлен")
    sys.exit(1)

async def test_chromadb_basic():
    """Базовый тест ChromaDB"""
    print("🚀 ТЕСТ CHROMADB БЕЗ EMBEDDING МОДЕЛЕЙ")
    
    start_time = time.time()
    
    # Создаём ChromaDB клиент
    client = chromadb.Client()
    print("✅ ChromaDB клиент создан")
    
    # Создаём коллекцию
    collection = client.create_collection(
        name="test_collection",
        get_or_create=True
    )
    print(f"✅ Коллекция создана: {collection.name}")
    
    # Добавляем документы с ПРОСТЫМИ эмбеддингами (случайные числа)
    import random
    
    documents = [
        "Создал Python скрипт",
        "Написал HTML страницу", 
        "Настроил базу данных"
    ]
    
    # Генерируем простые эмбеддинги (384 размерности как у MiniLM)
    simple_embeddings = []
    for doc in documents:
        # Простой эмбеддинг на основе хеша текста
        hash_val = hash(doc)
        embedding = [float((hash_val + i) % 1000) / 1000.0 for i in range(384)]
        simple_embeddings.append(embedding)
    
    # Добавляем в ChromaDB
    collection.add(
        documents=documents,
        embeddings=simple_embeddings,
        metadatas=[
            {"category": "programming", "type": "script"},
            {"category": "web", "type": "page"},
            {"category": "database", "type": "config"}
        ],
        ids=[f"doc_{i}" for i in range(len(documents))]
    )
    
    print(f"✅ Добавлено {len(documents)} документов")
    
    # Тестируем поиск
    query_embedding = [float(i % 1000) / 1000.0 for i in range(384)]
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )
    
    print(f"🔍 Найдено результатов: {len(results['documents'][0])}")
    
    for i, doc in enumerate(results['documents'][0]):
        distance = results['distances'][0][i]
        print(f"  📋 {doc} (distance: {distance:.3f})")
    
    total_time = time.time() - start_time
    print(f"\n⏱️ Время выполнения: {total_time:.2f}с")
    
    print("🎉 CHROMADB РАБОТАЕТ ИДЕАЛЬНО!")
    return True

async def test_amem_fallback():
    """Тест fallback режима A-MEM"""
    print("\n🔄 ТЕСТ FALLBACK РЕЖИМА A-MEM")
    
    # Добавляем путь к модулям
    sys.path.append(str(Path(__file__).parent))
    
    # Временно ломаем импорт sentence_transformers
    import builtins
    real_import = builtins.__import__
    
    def mock_import(name, *args, **kwargs):
        if name == 'sentence_transformers':
            raise ImportError("Mock error")
        return real_import(name, *args, **kwargs)
    
    builtins.__import__ = mock_import
    
    try:
        from kittycore.memory.amem_integration import AgenticMemorySystem
        
        # Создаём A-MEM (должен упасть в fallback)
        amem = AgenticMemorySystem()
        
        if hasattr(amem, 'simple_memory'):
            print("✅ Fallback режим активирован!")
            
            # Тестируем fallback память
            memory_id = await amem.add_note(
                content="Тест fallback памяти",
                tags=["test"],
                category="fallback"
            )
            print(f"✅ Память создана: {memory_id}")
            
            # Тестируем поиск
            results = await amem.search_agentic("тест", k=5)
            print(f"✅ Поиск работает: {len(results)} результатов")
            
            return True
        else:
            print("❌ Fallback не сработал")
            return False
            
    finally:
        builtins.__import__ = real_import

if __name__ == "__main__":
    async def main():
        success1 = await test_chromadb_basic()
        success2 = await test_amem_fallback()
        
        if success1 and success2:
            print("\n🎉 ВСЁ РАБОТАЕТ! A-MEM готов к интеграции!")
        else:
            print("\n😞 Есть проблемы...")
    
    asyncio.run(main()) 