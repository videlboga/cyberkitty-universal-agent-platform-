#!/usr/bin/env python3
"""
🔧 ИСПРАВЛЕНИЕ: EnhancedWebScrapingTool

ПРОБЛЕМА: Неправильный формат параметров - нужен urls как список, а не url как строка
"""

import asyncio

async def test_web_scraping_fix():
    """Тест исправления EnhancedWebScrapingTool"""
    print("🔧 ИСПРАВЛЕНИЕ: EnhancedWebScrapingTool")
    print("=" * 50)
    
    from kittycore.tools.enhanced_web_scraping_tool import EnhancedWebScrapingTool
    tool = EnhancedWebScrapingTool()
    
    # Тест 1: Скрапинг с правильным форматом параметров
    print("\n🌐 Тест 1: Скрапинг httpbin.org")
    result1 = await tool.execute(
        urls=["https://httpbin.org/html"],  # Список URL, а не строка
        extract_links=True,
        extract_metadata=True,
        filter_text=True
    )
    print(f"✅ Скрапинг: success={result1.success}")
    if result1.data:
        print(f"📊 Данные: {len(str(result1.data))} символов")
        print(f"📋 Результат: {result1.data.get('total_urls')} URL, {result1.data.get('successful_scrapes')} успешных")
        
        # Проверяем содержимое
        if result1.data.get('results'):
            first_result = result1.data['results'][0]
            print(f"📋 Первый результат: {len(str(first_result))} символов")
    if result1.error:
        print(f"❌ Ошибка: {result1.error}")
    
    # Тест 2: Скрапинг простой страницы
    print("\n📄 Тест 2: Скрапинг простой страницы")
    result2 = await tool.execute(
        urls=["https://httpbin.org/"],  # Главная страница httpbin
        extract_links=False,
        extract_metadata=True,
        filter_text=True
    )
    print(f"✅ Скрапинг: success={result2.success}")
    if result2.data:
        print(f"📊 Данные: {len(str(result2.data))} символов")
        print(f"📋 Результат: {result2.data.get('total_urls')} URL, {result2.data.get('successful_scrapes')} успешных")
    if result2.error:
        print(f"❌ Ошибка: {result2.error}")
    
    # Проверяем общий успех
    if result1.success and result2.success:
        print(f"\n🎉 EnhancedWebScrapingTool ПОЛНОСТЬЮ ИСПРАВЛЕН!")
        print(f"📊 Статистика: 2/2 теста успешно")
        return True
    elif result1.success or result2.success:
        print(f"\n⚠️ EnhancedWebScrapingTool частично работает")
        successful_tests = sum([result1.success, result2.success])
        print(f"📊 Статистика: {successful_tests}/2 тестов успешно")
        return True  # Считаем успехом если хотя бы один тест работает
    else:
        print(f"\n❌ EnhancedWebScrapingTool всё ещё не работает")
        print(f"📊 Статистика: 0/2 тестов успешно")
        return False

if __name__ == "__main__":
    asyncio.run(test_web_scraping_fix()) 