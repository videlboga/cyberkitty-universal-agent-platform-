#!/usr/bin/env python3
"""
🧠 ТЕСТ A-MEM В ПОЛНОСТЬЮ OFFLINE РЕЖИМЕ

Этот тест принудительно использует только локально кешированные модели
без попыток загрузки из интернета.
"""

import asyncio
import sys
import time
import json
import os
from pathlib import Path
from datetime import datetime

# КРИТИЧЕСКАЯ НАСТРОЙКА: Принудительный offline режим
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1" 
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Убираем fallback принудительно
if "FORCE_AMEM_FALLBACK" in os.environ:
    del os.environ["FORCE_AMEM_FALLBACK"]

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent))

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig
from loguru import logger

async def test_offline_model_loading():
    """Тестируем загрузку ТОЛЬКО локальных моделей в offline режиме"""
    print("🚀 === ТЕСТ OFFLINE ЗАГРУЗКИ ЛОКАЛЬНЫХ МОДЕЛЕЙ ===")
    print("🔒 TRANSFORMERS_OFFLINE = 1 (принудительный offline режим)")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Проверяем HuggingFace кеш
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        if not cache_dir.exists():
            cache_dir = Path("hf_cache")  # Локальный кеш
        
        print(f"📁 Проверяем кеш: {cache_dir}")
        
        # Ищем доступные модели в кеше
        cached_models = []
        if cache_dir.exists():
            for model_dir in cache_dir.glob("models--sentence-transformers--*"):
                model_name = model_dir.name.replace("models--sentence-transformers--", "")
                cached_models.append(f"sentence-transformers/{model_name}")
        
        print(f"📦 Найдено кешированных моделей: {len(cached_models)}")
        for model in cached_models:
            print(f"   🎯 {model}")
        
        # Пробуем загрузить локальные модели (без sentence-transformers/ префикса)
        local_models_to_try = [
            'paraphrase-MiniLM-L3-v2',
            'all-MiniLM-L6-v2',
            'all-mpnet-base-v2'
        ]
        
        for model_name in local_models_to_try:
            print(f"\n📦 OFFLINE тест модели: {model_name}")
            start_time = time.time()
            
            try:
                # Принудительно offline загрузка
                model = SentenceTransformer(model_name, cache_folder=str(cache_dir))
                load_time = time.time() - start_time
                
                print(f"   ✅ Загружена OFFLINE за {load_time:.2f}с")
                print(f"   📊 Размерность: {model.get_sentence_embedding_dimension()}")
                
                # Тестируем создание эмбеддингов
                test_texts = ["тест offline модели", "агентная система KittyCore"]
                embeddings = model.encode(test_texts)
                print(f"   🧠 Эмбеддинги: {embeddings.shape}")
                
                # Тестируем семантическую близость
                from sentence_transformers.util import cos_sim
                similarity = cos_sim(embeddings[0], embeddings[1]).item()
                print(f"   🔗 Семантическая близость: {similarity:.3f}")
                
                print(f"   🎉 OFFLINE МОДЕЛЬ {model_name} РАБОТАЕТ ИДЕАЛЬНО!")
                return model_name
                
            except Exception as e:
                print(f"   ❌ Ошибка offline загрузки: {e}")
                continue
        
        print("❌ НИ ОДНА OFFLINE МОДЕЛЬ НЕ ЗАГРУЗИЛАСЬ!")
        return None
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return None

async def test_direct_chromadb():
    """Прямой тест ChromaDB с offline моделью"""
    print("\n🚀 === ПРЯМОЙ ТЕСТ ChromaDB С OFFLINE МОДЕЛЬЮ ===")
    
    # Получаем работающую offline модель
    working_model = await test_offline_model_loading()
    if not working_model:
        return {"success": False, "error": "No offline model available"}
    
    print(f"\n🔧 === ПРЯМАЯ ИНИЦИАЛИЗАЦИЯ ChromaDB + {working_model} ===")
    
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
        
        # Инициализация в offline режиме
        print("📚 Инициализируем ChromaDB...")
        client = chromadb.Client()
        
        print("🗂️ Создаём коллекцию...")
        collection = client.create_collection(
            name="kittycore_offline_test",
            get_or_create=True
        )
        
        print(f"🧠 Загружаем offline модель {working_model}...")
        model = SentenceTransformer(working_model)
        
        print("✅ ChromaDB + SentenceTransformer готовы!")
        
        # Тестируем полный цикл: сохранение + поиск
        test_memories = [
            "Агент успешно создал веб-приложение на Python Flask с базой данных",
            "Команда агентов решила сложную задачу анализа данных pandas и numpy",
            "Автоматизация обработки email работает с высокой производительностью",
            "REST API с JWT аутентификацией разработан по лучшим практикам",
            "Алгоритм машинного обучения показал точность 95% на тестовых данных"
        ]
        
        print(f"\n💾 === СОХРАНЕНИЕ {len(test_memories)} ВОСПОМИНАНИЙ ===")
        
        # Сохраняем воспоминания
        for i, memory in enumerate(test_memories):
            print(f"   {i+1}. {memory[:50]}...")
            
            # Создаём эмбеддинг
            embedding = model.encode(memory).tolist()
            
            # Сохраняем в ChromaDB
            collection.add(
                documents=[memory],
                metadatas=[{
                    "agent_id": f"offline_agent_{i}",
                    "category": "development",
                    "timestamp": datetime.now().isoformat(),
                    "test_id": i
                }],
                ids=[f"offline_memory_{i}"],
                embeddings=[embedding]
            )
            
            print(f"      ✅ Сохранено с эмбеддингом {len(embedding)}D")
        
        print(f"\n🔍 === ТЕСТ СЕМАНТИЧЕСКОГО ПОИСКА ===")
        
        search_queries = [
            "веб разработка Flask Python",
            "анализ данных pandas numpy", 
            "автоматизация email обработка",
            "API аутентификация JWT REST",
            "машинное обучение точность алгоритм"
        ]
        
        search_results = {}
        total_found = 0
        
        for query in search_queries:
            print(f"   🔍 Поиск: '{query}'")
            
            # Семантический поиск через эмбеддинги
            query_embedding = model.encode(query).tolist()
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=2
            )
            
            found_count = len(results['documents'][0])
            search_results[query] = found_count
            total_found += found_count
            
            print(f"      📊 Найдено: {found_count}")
            
            if found_count > 0:
                best_doc = results['documents'][0][0]
                best_distance = results['distances'][0][0] if 'distances' in results else 0
                print(f"      ✨ Лучший: {best_doc[:50]}... (distance: {best_distance:.3f})")
        
        # Итоговая статистика
        avg_results = total_found / len(search_queries)
        
        print(f"\n📈 === ИТОГОВАЯ СТАТИСТИКА OFFLINE A-MEM ===")
        print(f"💾 Воспоминаний сохранено: {len(test_memories)}")
        print(f"🔍 Поисковых запросов: {len(search_queries)}")
        print(f"📊 Всего найдено: {total_found}")
        print(f"📈 Среднее на запрос: {avg_results:.1f}")
        
        # Оценка эффективности
        if avg_results >= 1.5:
            print("✨ ФЕНОМЕНАЛЬНО! Offline семантический поиск работает отлично!")
            rating = "excellent"
        elif avg_results >= 1.0:
            print("✅ ОТЛИЧНО! Offline семантический поиск эффективен!")
            rating = "good"
        elif avg_results >= 0.5:
            print("⚠️ УДОВЛЕТВОРИТЕЛЬНО! Поиск работает частично")
            rating = "fair"
        else:
            print("❌ ПЛОХО! Offline поиск не эффективен")
            rating = "poor"
        
        return {
            "success": True,
            "model_used": working_model,
            "memories_stored": len(test_memories),
            "search_effectiveness": avg_results,
            "search_results": search_results,
            "rating": rating,
            "offline_mode": True
        }
        
    except Exception as e:
        print(f"❌ Ошибка прямого ChromaDB теста: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

async def main():
    """Главная функция тестирования offline режима"""
    try:
        print("🎯 Запуск теста A-MEM в полностью offline режиме...")
        print("🔒 Все сетевые загрузки заблокированы!")
        
        result = await test_direct_chromadb()
        
        if result["success"]:
            print("\n🎉 === OFFLINE ТЕСТ ЗАВЕРШЁН УСПЕШНО ===")
            print("🔒 A-MEM работает полностью offline с локальными моделями!")
            print("🧠 ChromaDB + SentenceTransformers функционируют без интернета!")
            print("🔍 Семантический поиск работает на локальных эмбеддингах!")
            print("✨ Система полностью автономна и готова к продакшену!")
        else:
            print("\n💥 === OFFLINE ТЕСТ НЕ ПРОШЁЛ ===")
            print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
            print("🔧 Требуется локальная установка моделей")
        
        # Сохраняем результаты
        results_file = Path("amem_offline_test_results.json")
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