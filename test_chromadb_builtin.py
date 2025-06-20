#!/usr/bin/env python3
"""
🔧 ТЕСТ CHROMADB С ВСТРОЕННЫМИ EMBEDDING
Используем встроенную default_ef функцию ChromaDB
"""

import asyncio
import sys
import time
from pathlib import Path

try:
    import chromadb
    from chromadb.utils import embedding_functions
    print("✅ ChromaDB импортирован успешно!")
except ImportError:
    print("❌ ChromaDB не установлен")
    sys.exit(1)

async def test_chromadb_builtin():
    """Тест ChromaDB с встроенной embedding функцией"""
    print("🚀 ТЕСТ CHROMADB С ВСТРОЕННЫМИ EMBEDDING")
    
    start_time = time.time()
    
    # Создаём ChromaDB клиент
    client = chromadb.Client()
    print("✅ ChromaDB клиент создан")
    
    # Используем встроенную embedding функцию
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    print("✅ Встроенная embedding функция создана")
    
    # Создаём коллекцию с embedding функцией
    collection = client.create_collection(
        name="test_builtin_collection",
        embedding_function=default_ef,
        get_or_create=True
    )
    print(f"✅ Коллекция создана: {collection.name}")
    
    # Добавляем документы (ChromaDB сам создаст эмбеддинги)
    documents = [
        "программирование на Python",
        "веб разработка с Django", 
        "машинное обучение",
        "базы данных PostgreSQL",
        "фронтенд разработка React"
    ]
    
    ids = [f"doc_{i}" for i in range(len(documents))]
    metadatas = [{"category": "programming", "id": i} for i in range(len(documents))]
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✅ Добавлено {len(documents)} документов")
    
    # Тестируем поиск
    query = "Python разработка"
    results = collection.query(
        query_texts=[query],
        n_results=3
    )
    
    print(f"\n🔍 Поиск: '{query}'")
    print(f"📊 Найдено: {len(results['documents'][0])} результатов")
    
    for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
        print(f"  {i+1}. {doc} (расстояние: {distance:.3f})")
    
    # Проверяем статистику
    collection_count = collection.count()
    print(f"\n📈 Статистика:")
    print(f"  📄 Документов в коллекции: {collection_count}")
    
    total_time = time.time() - start_time
    print(f"  ⏱️ Общее время: {total_time:.2f}с")
    
    print("\n🎉 ВСТРОЕННЫЕ EMBEDDING РАБОТАЮТ!")
    return True

async def test_amem_with_builtin():
    """Тест A-MEM с встроенными embedding"""
    print("\n🧠 ТЕСТ A-MEM С ВСТРОЕННЫМИ EMBEDDING")
    
    # Добавляем путь к модулям
    sys.path.append(str(Path(__file__).parent))
    
    try:
        # Импортируем и модифицируем A-MEM для работы без sentence_transformers
        from kittycore.memory.amem_integration import KittyCoreMemorySystem
        
        # Создаём A-MEM систему
        memory = KittyCoreMemorySystem(vault_path="test_vault")
        
        # Добавляем воспоминания через правильный API
        await memory.agent_remember(
            agent_id="test_agent",
            memory="Изучаю Python программирование",
            context={"task_type": "learning", "tags": ["python", "programming"]}
        )
        
        await memory.agent_remember(
            agent_id="test_agent", 
            memory="Работаю с Django веб-фреймворком",
            context={"task_type": "work", "tags": ["django", "web", "python"]}
        )
        
        await memory.agent_remember(
            agent_id="test_agent",
            memory="Настраиваю базу данных PostgreSQL", 
            context={"task_type": "technical", "tags": ["database", "postgresql"]}
        )
        
        print("✅ Добавлено 3 воспоминания")
        
        # Тестируем поиск
        search_query = "python веб разработка"
        memories = await memory.collective_search(search_query)
        
        print(f"\n🔍 Поиск: '{search_query}'")
        print(f"📊 Найдено: {len(memories)} воспоминаний")
        
        for memory_item in memories:
            print(f"  📝 {memory_item['content']}")
            print(f"     🏷️ Теги: {memory_item.get('tags', [])}")
            print(f"     🆔 ID: {memory_item.get('id', 'unknown')}")
        
        print("\n🎉 A-MEM С ВСТРОЕННЫМИ EMBEDDING РАБОТАЕТ!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка A-MEM: {e}")
        return False

async def main():
    """Главная функция"""
    print("=" * 60)
    
    # Тест 1: Чистый ChromaDB 
    success1 = await test_chromadb_builtin()
    
    # Тест 2: A-MEM с ChromaDB
    success2 = await test_amem_with_builtin()
    
    print("\n" + "=" * 60)
    print("📋 ИТОГОВЫЙ ОТЧЁТ:")
    print(f"  🧪 ChromaDB builtin: {'✅ Работает' if success1 else '❌ Не работает'}")
    print(f"  🧠 A-MEM builtin: {'✅ Работает' if success2 else '❌ Не работает'}")

if __name__ == "__main__":
    asyncio.run(main()) 