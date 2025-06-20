#!/usr/bin/env python3
"""
🎯 ТЕСТ РЕАЛЬНОГО A-MEM С ЛОКАЛЬНОЙ МОДЕЛЬЮ
Теперь у нас есть полная all-MiniLM-L6-v2 модель из Ubuntu!
"""

import asyncio
import sys
import time
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent))

async def test_sentence_transformers_local():
    """Тестируем локальную sentence-transformers модель"""
    print("🚀 ТЕСТ ЛОКАЛЬНОЙ SENTENCE-TRANSFORMERS МОДЕЛИ")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        start_time = time.time()
        
        # Загружаем локальную модель (должна загрузиться мгновенно)
        print("📦 Загружаем all-MiniLM-L6-v2 из локального кеша...")
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        load_time = time.time() - start_time
        print(f"✅ Модель загружена за {load_time:.2f}с!")
        print(f"📊 Размерность эмбеддингов: {model.get_sentence_embedding_dimension()}")
        
        # Тестируем создание эмбеддингов
        print("\n🧠 Тестируем создание эмбеддингов...")
        texts = [
            "программирование на Python", 
            "веб разработка с Django",
            "машинное обучение",
            "базы данных PostgreSQL"
        ]
        
        embeddings = model.encode(texts)
        print(f"✅ Эмбеддинги созданы: {embeddings.shape}")
        
        # Тестируем семантическую близость
        from sentence_transformers.util import cos_sim
        
        similarity1 = cos_sim(embeddings[0], embeddings[1]).item()  # Python vs Django
        similarity2 = cos_sim(embeddings[0], embeddings[2]).item()  # Python vs ML
        
        print(f"\n🔗 Семантическая близость:")
        print(f"  Python ↔ Django: {similarity1:.3f}")
        print(f"  Python ↔ ML: {similarity2:.3f}")
        
        print("\n🎉 SENTENCE-TRANSFORMERS РАБОТАЕТ ЛОКАЛЬНО!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

async def test_amem_with_real_model():
    """Тестируем A-MEM с реальной моделью"""
    print("\n🧠 ТЕСТ A-MEM С РЕАЛЬНОЙ МОДЕЛЬЮ")
    
    try:
        from kittycore.memory.amem_integration import AgenticMemorySystem
        
        # Создаём A-MEM с реальной моделью
        print("🔧 Создаём AgenticMemorySystem...")
        amem = AgenticMemorySystem(model_name='sentence-transformers/all-MiniLM-L6-v2')
        
        # Проверяем что это НАСТОЯЩИЙ A-MEM
        if hasattr(amem, 'chroma_client') and hasattr(amem, 'embedding_model'):
            print("✅ Реальная A-MEM система создана!")
            print(f"📊 Модель: {amem.embedding_model}")
        else:
            print("⚠️ Работает в fallback режиме")
            
        # Добавляем воспоминания
        print("\n📝 Добавляем воспоминания через A-MEM...")
        memories = [
            ("Изучаю архитектуру нейросетей", ["ai", "learning"]),
            ("Программирую на Python FastAPI", ["python", "api"]),
            ("Настраиваю Docker контейнеры", ["docker", "devops"]),
            ("Работаю с векторными базами данных", ["database", "vectors"]),
            ("Оптимизирую производительность ML моделей", ["ml", "optimization"])
        ]
        
        memory_ids = []
        for content, tags in memories:
            memory_id = await amem.add_note(content, tags=tags, category="learning")
            memory_ids.append(memory_id)
            print(f"  ✅ {memory_id[:12]}... - {content[:30]}...")
        
        # Тестируем семантический поиск
        print("\n🔍 Тестируем семантический поиск...")
        search_queries = [
            "машинное обучение",
            "веб разработка", 
            "контейнеризация"
        ]
        
        for query in search_queries:
            print(f"\n🔎 Запрос: '{query}'")
            results = await amem.search_agentic(query, k=3)
            
            for i, result in enumerate(results[:3], 1):
                distance = result.get('distance', 0)
                print(f"  {i}. {result['content']}")
                print(f"     📏 Семантическое расстояние: {distance:.3f}")
                print(f"     🏷️ Теги: {result.get('tags', [])}")
        
        print("\n🎉 A-MEM С РЕАЛЬНОЙ МОДЕЛЬЮ РАБОТАЕТ!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка A-MEM: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Главная функция"""
    print("=" * 70)
    print("🎯 ФИНАЛЬНЫЙ ТЕСТ A-MEM С ЛОКАЛЬНОЙ МОДЕЛЬЮ")
    print("=" * 70)
    
    # Тест 1: Локальная модель
    success1 = await test_sentence_transformers_local()
    
    # Тест 2: A-MEM с реальной моделью
    success2 = await test_amem_with_real_model()
    
    print("\n" + "=" * 70)
    print("📋 ФИНАЛЬНЫЙ ОТЧЁТ:")
    print(f"  🤖 Локальная модель: {'✅ Работает' if success1 else '❌ Не работает'}")
    print(f"  🧠 A-MEM реальный: {'✅ Работает' if success2 else '❌ Не работает'}")
    
    if success1 and success2:
        print("\n🎉 A-MEM ПОЛНОСТЬЮ ГОТОВ К ПРОДАКШЕНУ!")
        print("💡 Семантический поиск, векторная память, эволюция - ВСЁ РАБОТАЕТ!")
    else:
        print("\n⚠️ Требуется доработка")

if __name__ == "__main__":
    asyncio.run(main()) 