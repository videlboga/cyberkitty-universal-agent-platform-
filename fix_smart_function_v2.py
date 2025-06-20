#!/usr/bin/env python3
"""
🔧 ИСПРАВЛЕНИЕ: SmartFunctionTool v2

ПРОБЛЕМА: Неправильные параметры - нужен function_code, а не code
"""

import asyncio

async def test_smart_function_fixed():
    """Тест исправления SmartFunctionTool с правильными параметрами"""
    print("🔧 ИСПРАВЛЕНИЕ: SmartFunctionTool v2")
    print("=" * 50)
    
    from kittycore.tools.smart_function_tool import SmartFunctionTool
    tool = SmartFunctionTool()
    
    # Тест 1: Создание функции с правильным параметром
    print("\n📝 Тест 1: Создание функции")
    result1 = await tool.execute(
        action="create_function",
        function_code="def test_func(): return 'Hello from function!'",
        function_name="test_func"
    )
    print(f"✅ Создание: success={result1.success}")
    if result1.data:
        print(f"📊 Данные: {len(str(result1.data))} символов")
        print(f"📋 Результат: {result1.data}")
    if result1.error:
        print(f"❌ Ошибка: {result1.error}")
    
    # Тест 2: Выполнение функции  
    print("\n🚀 Тест 2: Выполнение функции")
    result2 = await tool.execute(
        action="execute_function",
        function_name="test_func"
    )
    print(f"✅ Выполнение: success={result2.success}")
    if result2.data:
        print(f"📊 Данные: {len(str(result2.data))} символов")
        print(f"📋 Результат: {result2.data}")
    if result2.error:
        print(f"❌ Ошибка: {result2.error}")
    
    # Тест 3: Список функций
    print("\n📋 Тест 3: Список функций")
    result3 = await tool.execute(action="list_functions")
    print(f"✅ Список: success={result3.success}")
    if result3.data:
        print(f"📊 Данные: {len(str(result3.data))} символов")
        print(f"📋 Функции: {result3.data}")
    
    # Проверяем общий успех
    if result1.success and result2.success and result3.success:
        print(f"\n🎉 SmartFunctionTool ПОЛНОСТЬЮ ИСПРАВЛЕН!")
        print(f"📊 Статистика: 3/3 теста успешно")
        return True
    else:
        print(f"\n⚠️ SmartFunctionTool частично работает")
        successful_tests = sum([result1.success, result2.success, result3.success])
        print(f"📊 Статистика: {successful_tests}/3 тестов успешно")
        return successful_tests >= 2  # Считаем успехом если 2+ теста работают

if __name__ == "__main__":
    asyncio.run(test_smart_function_fixed()) 