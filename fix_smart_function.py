#!/usr/bin/env python3
"""
🔧 ИСПРАВЛЕНИЕ: SmartFunctionTool

ПРОБЛЕМА: Неправильное действие 'execute' → нужно 'execute_function'
"""

import asyncio

async def test_smart_function_fix():
    """Тест исправления SmartFunctionTool"""
    print("🔧 ИСПРАВЛЕНИЕ: SmartFunctionTool")
    print("=" * 50)
    
    from kittycore.tools.smart_function_tool import SmartFunctionTool
    tool = SmartFunctionTool()
    
    # Тест 1: Создание функции
    print("\n📝 Тест 1: Создание функции")
    result1 = await tool.execute(
        action="create_function",
        code="def test_func(): return 'Hello from function!'",
        function_name="test_func"
    )
    print(f"✅ Создание: success={result1.success}")
    if result1.data:
        print(f"📊 Данные: {len(str(result1.data))} символов")
    
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
    
    # Проверяем общий успех
    if result1.success and result2.success:
        print(f"\n🎉 SmartFunctionTool ИСПРАВЛЕН!")
        return True
    else:
        print(f"\n❌ SmartFunctionTool всё ещё не работает")
        return False

if __name__ == "__main__":
    asyncio.run(test_smart_function_fix()) 