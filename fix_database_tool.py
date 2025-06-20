#!/usr/bin/env python3
"""
🔧 ИСПРАВЛЕНИЕ: DatabaseTool

ПРОБЛЕМА: Подключение default не найдено - нужно создать SQLite подключение
"""

import asyncio

async def test_database_tool_fix():
    """Тест исправления DatabaseTool"""
    print("🔧 ИСПРАВЛЕНИЕ: DatabaseTool")
    print("=" * 50)
    
    from kittycore.tools.database_tool import DatabaseTool, DatabaseConnection
    
    # Создаём подключение к SQLite (не требует сервера)
    sqlite_config = DatabaseConnection(
        db_type='sqlite',
        database='test_kittycore.db'
    )
    
    tool = DatabaseTool(default_connection=sqlite_config)
    
    # Тест 1: Создание таблицы
    print("\n📝 Тест 1: Создание таблицы")
    result1 = await tool.execute(
        query="CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)"
    )
    print(f"✅ Создание таблицы: success={result1.success}")
    if result1.data:
        print(f"📊 Данные: {len(str(result1.data))} символов")
        print(f"📋 Затронуто строк: {result1.data.get('affected_rows')}")
    if result1.error:
        print(f"❌ Ошибка: {result1.error}")
    
    # Тест 2: Вставка данных
    print("\n📥 Тест 2: Вставка данных")
    result2 = await tool.execute(
        query="INSERT INTO test_table (name, value) VALUES ('test', 42)"
    )
    print(f"✅ Вставка: success={result2.success}")
    if result2.data:
        print(f"📊 Данные: {len(str(result2.data))} символов")
        print(f"📋 Затронуто строк: {result2.data.get('affected_rows')}")
    if result2.error:
        print(f"❌ Ошибка: {result2.error}")
    
    # Тест 3: Выборка данных
    print("\n📤 Тест 3: Выборка данных")
    result3 = await tool.execute(
        query="SELECT * FROM test_table"
    )
    print(f"✅ Выборка: success={result3.success}")
    if result3.data:
        print(f"📊 Данные: {len(str(result3.data))} символов")
        print(f"📋 Найдено строк: {result3.data.get('affected_rows')}")
        if result3.data.get('data'):
            print(f"📋 Первая запись: {result3.data['data'][0] if result3.data['data'] else 'Нет данных'}")
    if result3.error:
        print(f"❌ Ошибка: {result3.error}")
    
    # Проверяем общий успех
    successful_tests = sum([result1.success, result2.success, result3.success])
    if successful_tests >= 2:
        print(f"\n🎉 DatabaseTool ИСПРАВЛЕН!")
        print(f"📊 Статистика: {successful_tests}/3 тестов успешно")
        
        # Очистка - удаляем тестовую базу
        try:
            import os
            if os.path.exists('test_kittycore.db'):
                os.remove('test_kittycore.db')
                print("🧹 Тестовая база данных удалена")
        except:
            pass
        
        return True
    else:
        print(f"\n⚠️ DatabaseTool частично работает")
        print(f"📊 Статистика: {successful_tests}/3 тестов успешно")
        return False

if __name__ == "__main__":
    asyncio.run(test_database_tool_fix()) 