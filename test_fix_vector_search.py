#!/usr/bin/env python3
"""
🔧 ИСПРАВЛЕНИЕ: VectorSearchTool - правильные параметры

ПРОБЛЕМА: search_documents(collection_name=...), а не search_documents(collection=...)
РЕШЕНИЕ: Использовать правильную сигнатуру + тестировать реальные документы
"""

import time
import tempfile
import os

def test_vector_search_tool():
    """Тест исправленного VectorSearchTool"""
    print("🔍 ТЕСТ ИСПРАВЛЕННОГО: VectorSearchTool")
    
    try:
        from kittycore.tools.vector_search_tool import VectorSearchTool
        
        # Создаем временную директорию для ChromaDB
        temp_dir = tempfile.mkdtemp()
        print(f"📁 Временная директория: {temp_dir}")
        
        # Инициализируем инструмент
        tool = VectorSearchTool(
            storage_path=temp_dir,
            embedding_model="all-MiniLM-L6-v2",
            collection_name="test_collection"
        )
        print("✅ Инициализация успешна")
        
        # Тест 1: Создание коллекции
        print("\n📝 Тест 1: Создание коллекции")
        result1 = tool.execute(action="create_collection", collection_name="test_docs")
        print(f"✅ Создание коллекции: success={getattr(result1, 'success', 'N/A')}")
        if hasattr(result1, 'data'):
            print(f"📊 Статус: {result1.data.get('status', 'unknown')}")
        
        # Тест 2: Добавление документов
        test_documents = [
            "Это тестовый документ о машинном обучении",
            "KittyCore - саморедуплицирующаяся агентная система", 
            "Python - отличный язык программирования"
        ]
        
        print("\n📝 Тест 2: Добавление документов")
        result2 = tool.execute(
            action="add_documents",
            documents=test_documents,
            collection_name="test_docs",
            metadatas=[{"topic": "ml"}, {"topic": "ai"}, {"topic": "programming"}]
        )
        print(f"✅ Добавление документов: success={getattr(result2, 'success', 'N/A')}")
        if hasattr(result2, 'data'):
            print(f"📊 Добавлено документов: {result2.data.get('added_count', 0)}")
        
        # Тест 3: Поиск документов (исправленные параметры!)
        print("\n📝 Тест 3: Поиск документов")
        result3 = tool.execute(
            action="search_documents",
            query="машинное обучение",
            collection_name="test_docs",  # Правильный параметр!
            top_k=2
        )
        print(f"✅ Поиск документов: success={getattr(result3, 'success', 'N/A')}")
        if hasattr(result3, 'data') and result3.data:
            matches = result3.data.get('matches', [])
            print(f"📊 Найдено совпадений: {len(matches)}")
            if matches:
                best_match = matches[0]
                print(f"🥇 Лучшее совпадение: score={best_match.get('score', 0):.3f}")
        
        # Тест 4: Список коллекций
        print("\n📝 Тест 4: Список коллекций")
        result4 = tool.execute(action="list_collections")
        print(f"✅ Список коллекций: success={getattr(result4, 'success', 'N/A')}")
        if hasattr(result4, 'data'):
            collections = result4.data.get('collections', [])
            print(f"📊 Найдено коллекций: {len(collections)}")
        
        # Очистка
        try:
            import shutil
            shutil.rmtree(temp_dir)
            print(f"🗑️ Временная директория удалена")
        except:
            pass
        
        # Подсчет успешности
        results = [result1, result2, result3, result4]
        success_count = sum(1 for r in results if hasattr(r, 'success') and r.success)
        success_rate = (success_count / len(results)) * 100
        
        print(f"\n📊 ИТОГИ: {success_count}/{len(results)} тестов успешно ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            return f"✅ ИСПРАВЛЕН: {success_rate:.1f}% успех"
        else:
            return f"❌ ЧАСТИЧНО: {success_rate:.1f}% успех"
            
    except ImportError as e:
        return f"❌ ИМПОРТ: {e}"
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return f"❌ ИСКЛЮЧЕНИЕ: {e}"

if __name__ == "__main__":
    print("🔧 ИСПРАВЛЕНИЕ VECTORSEARCHTOOL")
    print("=" * 50)
    
    start_time = time.time()
    result = test_vector_search_tool()
    end_time = time.time()
    
    test_time = (end_time - start_time) * 1000
    print(f"\n🏁 РЕЗУЛЬТАТ: {result} ({test_time:.1f}мс)") 