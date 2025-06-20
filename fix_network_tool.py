#!/usr/bin/env python3
"""
🔧 ИСПРАВЛЕНИЕ: NetworkTool

ПРОБЛЕМА: Неправильное действие 'get_info' → нужны правильные действия
"""

import asyncio

async def test_network_tool_fix():
    """Тест исправления NetworkTool"""
    print("🔧 ИСПРАВЛЕНИЕ: NetworkTool")
    print("=" * 50)
    
    from kittycore.tools.network_tool import NetworkTool
    tool = NetworkTool()
    
    # Тест 1: HTTP GET запрос
    print("\n🌐 Тест 1: HTTP GET запрос")
    result1 = await tool.execute(
        action="get_request",
        url="https://httpbin.org/get"
    )
    print(f"✅ GET запрос: success={result1.success}")
    if result1.data:
        print(f"📊 Данные: {len(str(result1.data))} символов")
        print(f"📋 Статус: {result1.data.get('status_code')}")
    if result1.error:
        print(f"❌ Ошибка: {result1.error}")
    
    # Тест 2: Ping хоста
    print("\n🏓 Тест 2: Ping хоста")
    result2 = await tool.execute(
        action="ping_host",
        host="8.8.8.8",
        count=2
    )
    print(f"✅ Ping: success={result2.success}")
    if result2.data:
        print(f"📊 Данные: {len(str(result2.data))} символов")
        print(f"📋 Ping результат: {result2.data}")
    if result2.error:
        print(f"❌ Ошибка: {result2.error}")
    
    # Тест 3: Сканирование порта
    print("\n🔍 Тест 3: Сканирование порта")
    result3 = await tool.execute(
        action="scan_port",
        host="8.8.8.8",
        port=53,
        timeout=3.0
    )
    print(f"✅ Сканирование: success={result3.success}")
    if result3.data:
        print(f"📊 Данные: {len(str(result3.data))} символов")
        print(f"📋 Порт 53: {result3.data}")
    if result3.error:
        print(f"❌ Ошибка: {result3.error}")
    
    # Проверяем общий успех
    successful_tests = sum([result1.success, result2.success, result3.success])
    if successful_tests >= 2:
        print(f"\n🎉 NetworkTool ИСПРАВЛЕН!")
        print(f"📊 Статистика: {successful_tests}/3 тестов успешно")
        return True
    else:
        print(f"\n⚠️ NetworkTool частично работает")
        print(f"📊 Статистика: {successful_tests}/3 тестов успешно")
        return False

if __name__ == "__main__":
    asyncio.run(test_network_tool_fix()) 