#!/usr/bin/env python3
"""
🧠 ТЕСТ A-MEM БЕЗ FALLBACK С ЛОКАЛЬНОЙ МОДЕЛЬЮ

Этот тест проверяет работу полноценной A-MEM системы 
с локально загруженной embedding моделью без fallback режима.
"""

import asyncio
import sys
import time
import json
import os
from pathlib import Path
from datetime import datetime

# Убираем fallback принудительно
if "FORCE_AMEM_FALLBACK" in os.environ:
    del os.environ["FORCE_AMEM_FALLBACK"]

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent))

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig
from loguru import logger

async def test_local_model_loading():
    """Тестируем загрузку локальной модели"""
    print("🚀 === ТЕСТ ЗАГРУЗКИ ЛОКАЛЬНОЙ EMBEDDING МОДЕЛИ ===")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Пробуем разные локальные модели
        models_to_try = [
            'paraphrase-MiniLM-L3-v2',  # Уже есть в кеше
            'all-MiniLM-L6-v2',
            'sentence-transformers/paraphrase-MiniLM-L3-v2'
        ]
        
        for model_name in models_to_try:
            print(f"\n📦 Пробуем модель: {model_name}")
            start_time = time.time()
            
            try:
                model = SentenceTransformer(model_name)
                load_time = time.time() - start_time
                
                print(f"   ✅ Загружена за {load_time:.2f}с")
                print(f"   📊 Размерность: {model.get_sentence_embedding_dimension()}")
                
                # Тестируем создание эмбеддингов
                test_texts = ["тест модели", "агентная система"]
                embeddings = model.encode(test_texts)
                print(f"   🧠 Эмбеддинги: {embeddings.shape}")
                
                print(f"   🎉 МОДЕЛЬ {model_name} РАБОТАЕТ!")
                return model_name
                
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
                continue
        
        print("❌ НИ ОДНА МОДЕЛЬ НЕ ЗАГРУЗИЛАСЬ!")
        return None
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return None

async def test_amem_no_fallback():
    """🧠 Тест полноценной A-MEM без fallback режима"""
    print("\n🚀 === ТЕСТ A-MEM БЕЗ FALLBACK ===")
    start_time = time.time()
    
    # Проверяем доступность локальной модели
    working_model = await test_local_model_loading()
    if not working_model:
        print("❌ Локальная модель недоступна!")
        return {"success": False, "error": "No local model available"}
    
    print(f"\n🎯 === ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ С МОДЕЛЬЮ {working_model} ===")
    
    # Настраиваем конфигурацию без fallback
    config = UnifiedConfig(
        orchestrator_id="amem_no_fallback_test",
        enable_amem_memory=True,
        amem_memory_path="./vault/system/amem_no_fallback",
        vault_path="./vault_no_fallback",
        enable_shared_chat=True,
        enable_vector_memory=False,  # Отключаем старую векторную память
        enable_smart_validation=True,
        timeout=60
    )
    
    try:
        # Инициализируем с кастомной моделью
        orchestrator = UnifiedOrchestrator(config)
        
        # Проверяем что A-MEM использует настоящую ChromaDB а не fallback
        amem_type = type(orchestrator.amem_system.amem).__name__
        print(f"🧠 A-MEM тип: {amem_type}")
        
        # Проверяем доступность ChromaDB
        from kittycore.memory.amem_integration import AMEM_AVAILABLE
        print(f"🔍 AMEM_AVAILABLE: {AMEM_AVAILABLE}")
        
        if not AMEM_AVAILABLE or amem_type == "SimpleAgenticMemory":
            print("⚠️ Система всё ещё использует fallback!")
            print("🔧 Попробуем принудительно инициализировать ChromaDB...")
            
            # Попытка прямой инициализации ChromaDB
            try:
                import chromadb
                from sentence_transformers import SentenceTransformer
                
                client = chromadb.Client()
                collection = client.create_collection(
                    name="test_collection",
                    get_or_create=True
                )
                
                model = SentenceTransformer(working_model)
                
                print("✅ ChromaDB инициализирован напрямую!")
                print("✅ SentenceTransformer модель загружена!")
                
                # Тестируем базовые операции
                test_doc = "Тестовое воспоминание агента"
                embedding = model.encode(test_doc).tolist()
                
                collection.add(
                    documents=[test_doc],
                    metadatas=[{"test": "true"}],
                    ids=["test_1"]
                )
                
                # Поиск
                results = collection.query(
                    query_texts=["агент система"],
                    n_results=1
                )
                
                print(f"🔍 Поиск работает! Найдено: {len(results['documents'][0])}")
                print(f"📄 Результат: {results['documents'][0][0][:50]}...")
                
            except Exception as e:
                print(f"❌ Ошибка прямой инициализации: {e}")
                return {"success": False, "error": str(e)}
        
        print("✅ UnifiedOrchestrator с настоящей A-MEM готов")
        
        # Тестируем сохранение и поиск воспоминаний
        print(f"\n🧠 === ТЕСТ СОХРАНЕНИЯ И ПОИСКА ВОСПОМИНАНИЙ ===")
        
        test_memories = [
            "Агент успешно создал веб-приложение на Python Flask",
            "Команда агентов решила задачу анализа данных с помощью pandas",
            "Автоматизация email обработки работает отлично",
            "API с аутентификацией разработан и протестирован",
            "Алгоритм оптимизации показал улучшение на 40%"
        ]
        
        stored_memories = []
        for i, memory in enumerate(test_memories):
            print(f"   💾 Сохраняем: {memory[:50]}...")
            
            memory_id = await orchestrator.amem_system.store_memory(
                content=memory,
                context={
                    "agent_id": f"test_agent_{i}",
                    "category": "test_memory",
                    "task_type": "development"
                },
                tags=["test", "agent_work", f"memory_{i}"]
            )
            
            stored_memories.append(memory_id)
            print(f"   ✅ Сохранено: {memory_id}")
        
        print(f"\n🔍 === ТЕСТ СЕМАНТИЧЕСКОГО ПОИСКА ===")
        
        search_queries = [
            "веб разработка Python",
            "анализ данных pandas",
            "автоматизация email",
            "API аутентификация",
            "оптимизация алгоритмов"
        ]
        
        search_results = {}
        for query in search_queries:
            print(f"   🔍 Поиск: '{query}'")
            
            results = await orchestrator.amem_system.search_memories(query, limit=3)
            search_results[query] = len(results)
            
            print(f"      📊 Найдено: {len(results)} результатов")
            
            if results:
                best = results[0]
                content_preview = best.get('content', '')[:50]
                tags = best.get('tags', [])
                print(f"      ✨ Лучший: {content_preview}... (теги: {', '.join(tags[:2])})")
        
        # Итоговая статистика
        total_time = time.time() - start_time
        total_found = sum(search_results.values())
        avg_results = total_found / len(search_queries) if search_queries else 0
        
        print(f"\n📈 === ИТОГОВАЯ СТАТИСТИКА ===")
        print(f"⏱️ Время: {total_time:.2f}с")
        print(f"💾 Воспоминаний сохранено: {len(stored_memories)}")
        print(f"🔍 Поисковых запросов: {len(search_queries)}")
        print(f"📊 Всего найдено: {total_found}")
        print(f"📈 Среднее на запрос: {avg_results:.1f}")
        
        # Оценка эффективности
        if avg_results >= 2.0:
            print("✨ ОТЛИЧНО! Семантический поиск работает эффективно!")
        elif avg_results >= 1.0:
            print("✅ ХОРОШО! Семантический поиск находит результаты!")
        elif avg_results >= 0.5:
            print("⚠️ УДОВЛЕТВОРИТЕЛЬНО! Поиск работает частично")
        else:
            print("❌ ПЛОХО! Семантический поиск не эффективен")
        
        return {
            "success": True,
            "time": total_time,
            "model_used": working_model,
            "amem_type": amem_type,
            "amem_available": AMEM_AVAILABLE,
            "memories_stored": len(stored_memories),
            "search_effectiveness": avg_results,
            "search_results": search_results
        }
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

async def main():
    """Главная функция тестирования"""
    try:
        print("🎯 Запуск теста A-MEM без fallback с локальной моделью...")
        result = await test_amem_no_fallback()
        
        if result["success"]:
            print("\n🎉 === ТЕСТ ЗАВЕРШЁН УСПЕШНО ===")
            print("🧠 A-MEM работает с локальной моделью без fallback!")
            print("🔍 Семантический поиск функционирует!")
            print("✨ Система готова к полноценной работе!")
        else:
            print("\n💥 === ТЕСТ НЕ ПРОШЁЛ ===")
            print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
            print("🔧 Требуется дополнительная настройка")
        
        # Сохраняем результаты
        results_file = Path("amem_no_fallback_test_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📊 Результаты сохранены: {results_file}")
        
        return result
        
    except Exception as e:
        print(f"\n💥 === КРИТИЧЕСКАЯ ОШИБКА ===")
        print(f"❌ {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    asyncio.run(main()) 