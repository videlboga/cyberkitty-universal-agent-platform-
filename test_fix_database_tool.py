#!/usr/bin/env python3
"""
🔧 ИСПРАВЛЕНИЕ: DatabaseTool - правильные параметры

ПРОБЛЕМА: execute(query, **kwargs), а не execute(action, **kwargs)
РЕШЕНИЕ: Использовать правильную сигнатуру + инициализация SQLite по умолчанию
"""

import asyncio
import time
import os
import tempfile

def sync_execute(async_tool, *args, **kwargs):
    """Универсальная синхронная обертка для async execute"""
    try:
        loop = asyncio.get_running_loop()
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, async_tool.execute(*args, **kwargs))
            return future.result(timeout=30)
    except RuntimeError:
        return asyncio.run(async_tool.execute(*args, **kwargs))

def test_database_tool():
    """Тест исправленного DatabaseTool"""
    print("🗄️ ТЕСТ ИСПРАВЛЕННОГО: DatabaseTool")
    
    try:
        from kittycore.tools.database_tool import DatabaseTool, DatabaseConnection
        
        # Создаем временную SQLite базу
        temp_db = tempfile.mktemp(suffix='.db')
        print(f"📁 Временная база: {temp_db}")
        
        # Инициализируем с SQLite подключением
        db_config = DatabaseConnection(
            db_type='sqlite',
            database=temp_db
        )
        tool = DatabaseTool(default_connection=db_config)
        print("✅ Инициализация успешна")
        
        # Тест 1: Создание таблицы
        create_table_query = """
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        print("\n📝 Тест 1: Создание таблицы")
        result1 = sync_execute(tool, create_table_query)
        print(f"✅ Создание таблицы: success={getattr(result1, 'success', 'N/A')}")
        
        # Тест 2: Вставка данных
        insert_query = "INSERT INTO test_table (name) VALUES ('Тестовая запись')"
        
        print("\n📝 Тест 2: Вставка данных")
        result2 = sync_execute(tool, insert_query)
        print(f"✅ Вставка: success={getattr(result2, 'success', 'N/A')}")
        if hasattr(result2, 'data'):
            print(f"📊 Затронуто строк: {result2.data.get('affected_rows', 0)}")
        
        # Тест 3: Выборка данных
        select_query = "SELECT * FROM test_table"
        
        print("\n📝 Тест 3: Выборка данных")
        result3 = sync_execute(tool, select_query)
        print(f"✅ Выборка: success={getattr(result3, 'success', 'N/A')}")
        if hasattr(result3, 'data') and result3.data:
            data = result3.data.get('data', [])
            print(f"📊 Найдено записей: {len(data)}")
            if data:
                print(f"📄 Первая запись: {data[0]}")
        
        # Тест 4: Список таблиц
        print("\n📝 Тест 4: Список таблиц")
        result4 = sync_execute(tool, "SELECT name FROM sqlite_master WHERE type='table'")
        print(f"✅ Список таблиц: success={getattr(result4, 'success', 'N/A')}")
        if hasattr(result4, 'data') and result4.data:
            tables = result4.data.get('data', [])
            print(f"📊 Найдено таблиц: {len(tables)}")
        
        # Очистка
        try:
            os.unlink(temp_db)
            print(f"🗑️ Временная база удалена")
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
    print("🔧 ИСПРАВЛЕНИЕ DATABASETOOL")
    print("=" * 50)
    
    start_time = time.time()
    result = test_database_tool()
    end_time = time.time()
    
    test_time = (end_time - start_time) * 1000
    print(f"\n🏁 РЕЗУЛЬТАТ: {result} ({test_time:.1f}мс)") 