#!/usr/bin/env python3
"""
🐛 ОТЛАДКА: Детальный анализ web_scraping_tool

Проверяем:
1. Что именно возвращает web_scraping
2. Структуру данных
3. Почему HTML теги не найдены
"""

import asyncio
import json

try:
    from kittycore.tools.enhanced_web_scraping_tool import EnhancedWebScrapingTool
    
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

    print("🐛 ОТЛАДКА ENHANCED_WEB_SCRAPING_TOOL")
    print("=" * 50)
    
    tool = EnhancedWebScrapingTool()
    result = sync_execute(tool, urls=["https://httpbin.org/html"])
    
    print(f"✅ Результат получен: success={getattr(result, 'success', 'N/A')}")
    print(f"📏 Размер result.data: {len(str(result.data))} символов")
    
    if hasattr(result, 'data') and result.data:
        print(f"\n📋 СТРУКТУРА DATA:")
        data = result.data
        for key, value in data.items():
            if isinstance(value, list) and key == 'results':
                print(f"  {key}: список из {len(value)} элементов")
                if value:
                    first_result = value[0]
                    print(f"    Первый результат: {type(first_result)}")
                    if isinstance(first_result, dict):
                        for subkey, subvalue in first_result.items():
                            if isinstance(subvalue, str):
                                length = len(subvalue)
                                preview = subvalue[:100] + "..." if length > 100 else subvalue
                                print(f"      {subkey}: '{preview}' ({length} символов)")
                            else:
                                print(f"      {subkey}: {type(subvalue)} = {subvalue}")
            else:
                print(f"  {key}: {value}")
        
        # Специальная проверка HTML контента
        if 'results' in data and data['results']:
            first_result = data['results'][0]
            if isinstance(first_result, dict):
                # Проверяем содержимое text_preview
                if 'text_preview' in first_result:
                    text_content = first_result['text_preview']
                    print(f"\n🔍 АНАЛИЗ TEXT_PREVIEW:")
                    print(f"  Размер: {len(text_content)} символов")
                    
                    # Поиск HTML тегов
                    html_tags = ['<html>', '<body>', '<h1>', '<title>', '<div>', '<p>']
                    found_tags = []
                    for tag in html_tags:
                        if tag.lower() in text_content.lower():
                            found_tags.append(tag)
                    
                    print(f"  Найденные HTML теги: {found_tags}")
                    
                    # Поиск ключевых слов
                    keywords = ['herman melville', 'moby dick', 'html', 'body']
                    found_keywords = []
                    for keyword in keywords:
                        if keyword.lower() in text_content.lower():
                            found_keywords.append(keyword)
                    
                    print(f"  Найденные ключевые слова: {found_keywords}")
                    
                    # Показываем начало контента
                    print(f"\n📝 НАЧАЛО КОНТЕНТА (первые 300 символов):")
                    print(f"'{text_content[:300]}'")
                    
                    # Показываем конец контента
                    if len(text_content) > 300:
                        print(f"\n📝 КОНЕЦ КОНТЕНТА (последние 100 символов):")
                        print(f"'{text_content[-100:]}'")
    
    else:
        print("❌ Нет данных в result.data")
        if hasattr(result, 'error'):
            print(f"❌ Ошибка: {result.error}")

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")
    import traceback
    traceback.print_exc() 