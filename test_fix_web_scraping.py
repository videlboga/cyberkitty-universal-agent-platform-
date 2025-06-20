#!/usr/bin/env python3
"""
🕷️ ОТЛАДКА: enhanced_web_scraping_tool
Проверяем правильные async вызовы и параметры

ПРОБЛЕМЫ ИЗ ПАМЯТИ:
- Инструмент требует async/await
- Неправильные параметры (нет action, есть urls)
- Возвращал пустые данные

ПЛАН ОТЛАДКИ:
1. Правильный async вызов
2. Правильные параметры (urls вместо url)
3. Проверка реальных скрапинг-данных
"""

import asyncio
import time
import json

# Импорт инструмента
try:
    from kittycore.tools.enhanced_web_scraping_tool import EnhancedWebScrapingTool
    IMPORT_OK = True
    print("✅ Импорт enhanced_web_scraping_tool успешен")
except ImportError as e:
    print(f"❌ ИМПОРТ ОШИБКА: {e}")
    IMPORT_OK = False

async def test_web_scraping_correct():
    """Правильный тест с async и корректными параметрами"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🕷️ Тестирую enhanced_web_scraping с правильными параметрами...")
    start_time = time.time()
    
    tool = EnhancedWebScrapingTool()
    
    # ПРАВИЛЬНЫЙ вызов: await + urls (НЕ action, НЕ url)
    result = await tool.execute(
        urls=["https://httpbin.org/html"],
        extract_links=True,
        extract_metadata=True
    )
    
    execution_time = time.time() - start_time
    
    print(f"⏱️ Время выполнения: {execution_time:.2f}с")
    print(f"📊 Результат: {type(result)}")
    
    if isinstance(result, dict):
        print(f"✅ Success: {result.get('success', 'НЕТ')}")
        if result.get('success'):
            print(f"📦 Всего URL: {result.get('total_urls', 0)}")
            print(f"🎯 Успешных скрапингов: {result.get('successful_scrapes', 0)}")
            
            # Проверим результаты
            results = result.get('results', [])
            if results:
                first_result = results[0]
                print(f"🔍 Первый результат:")
                print(f"   URL: {first_result.get('url', 'НЕТ')}")
                print(f"   Success: {first_result.get('success', 'НЕТ')}")
                print(f"   Размер контента: {first_result.get('content_length', 0)} байт")
                if first_result.get('success'):
                    if 'text_preview' in first_result:
                        preview = first_result['text_preview'][:100]
                        print(f"   Текст: {preview}...")
                    if 'metadata' in first_result:
                        metadata = first_result['metadata']
                        print(f"   Метаданные: {len(metadata)} элементов")
                        if 'title' in metadata:
                            print(f"   Заголовок: {metadata['title'][:50]}...")
        else:
            print(f"❌ Ошибка: {result.get('error', 'НЕИЗВЕСТНО')}")
    
    return result

async def test_web_scraping_multiple():
    """Тест с несколькими URL"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🕷️ Тест enhanced_web_scraping с несколькими URL...")
    
    tool = EnhancedWebScrapingTool()
    
    # Тест с несколькими надежными URL
    result = await tool.execute(
        urls=[
            "https://httpbin.org/html",
            "https://httpbin.org/robots.txt"
        ],
        extract_links=True,
        extract_images=False,
        max_content_length=10000
    )
    
    print(f"📊 Множественный тест результат: {type(result)}")
    if isinstance(result, dict):
        print(f"✅ Success: {result.get('success')}")
        print(f"📦 Всего URL: {result.get('total_urls', 0)}")
        print(f"🎯 Успешных: {result.get('successful_scrapes', 0)}")
    
    return result

async def test_web_scraping_minimal():
    """Минимальный тест с одним параметром"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🕷️ Минимальный тест enhanced_web_scraping...")
    
    tool = EnhancedWebScrapingTool()
    
    # Минимальный вызов - только urls
    result = await tool.execute(urls=["https://httpbin.org/html"])
    
    print(f"📊 Минимальный тест результат: {type(result)}")
    if isinstance(result, dict):
        print(f"✅ Success: {result.get('success')}")
        if result.get('success'):
            total_size = 0
            for res in result.get('results', []):
                if res.get('success'):
                    total_size += res.get('content_length', 0)
            print(f"📦 Общий размер: {total_size} байт")
    
    return result

def is_result_honest(result, test_name):
    """Проверка честности результата"""
    if not result:
        print(f"❌ {test_name}: Пустой результат")
        return False
    
    if not isinstance(result, dict):
        print(f"❌ {test_name}: Результат не dict")
        return False
    
    if not result.get('success'):
        print(f"❌ {test_name}: success=False")
        if 'error' in result:
            print(f"   Ошибка: {result['error']}")
        return False
    
    # Проверяем структуру данных
    required_keys = ['total_urls', 'successful_scrapes', 'results']
    for key in required_keys:
        if key not in result:
            print(f"❌ {test_name}: Отсутствует ключ {key}")
            return False
    
    results = result.get('results', [])
    if not results:
        print(f"❌ {test_name}: Нет результатов скрапинга")
        return False
    
    # Проверяем первый результат
    first_result = results[0]
    if not first_result.get('success'):
        print(f"❌ {test_name}: Первый результат неуспешен")
        if 'error' in first_result:
            print(f"   Ошибка: {first_result['error']}")
        return False
    
    # Проверка на фейковые паттерны
    result_str = str(result)
    fake_patterns = [
        "enhanced_web_scraping: успешно",
        "демо скрапинг",
        "заглушка скрапинга",
        "тестовые HTML данные"
    ]
    
    for pattern in fake_patterns:
        if pattern.lower() in result_str.lower():
            print(f"❌ {test_name}: Найден фейковый паттерн: {pattern}")
            return False
    
    # Проверка на реальные скрапинг-признаки
    scraping_indicators = [
        "content_length", "text_preview", "metadata", "httpbin", "response_time"
    ]
    
    has_scraping_data = any(indicator in result_str.lower() for indicator in scraping_indicators)
    
    if not has_scraping_data:
        print(f"❌ {test_name}: Нет признаков реального скрапинга")
        return False
    
    # Проверяем размер данных
    total_content = sum(
        res.get('content_length', 0) 
        for res in results 
        if res.get('success')
    )
    
    if total_content < 100:
        print(f"❌ {test_name}: Слишком маленький контент ({total_content} байт)")
        return False
    
    print(f"✅ {test_name}: ЧЕСТНЫЙ результат ({len(result_str)} байт, контент {total_content} байт)")
    return True

async def main():
    """Главная функция отладки"""
    print("🕷️ ОТЛАДКА: enhanced_web_scraping_tool")
    print("=" * 50)
    
    if not IMPORT_OK:
        print("❌ Невозможно продолжить - ошибка импорта")
        return
    
    results = {}
    
    # Тест 1: Правильный полный тест
    print("\n" + "=" * 30)
    print("ТЕСТ 1: Правильные параметры")
    try:
        result1 = await test_web_scraping_correct()
        results["correct_params"] = is_result_honest(result1, "Правильные параметры")
    except Exception as e:
        print(f"❌ ТЕСТ 1 ОШИБКА: {e}")
        results["correct_params"] = False
    
    # Тест 2: Множественные URL
    print("\n" + "=" * 30)
    print("ТЕСТ 2: Множественные URL")
    try:
        result2 = await test_web_scraping_multiple()
        results["multiple_urls"] = is_result_honest(result2, "Множественные URL")
    except Exception as e:
        print(f"❌ ТЕСТ 2 ОШИБКА: {e}")
        results["multiple_urls"] = False
    
    # Тест 3: Минимальные параметры
    print("\n" + "=" * 30)
    print("ТЕСТ 3: Минимальные параметры")
    try:
        result3 = await test_web_scraping_minimal()
        results["minimal_params"] = is_result_honest(result3, "Минимальные параметры")
    except Exception as e:
        print(f"❌ ТЕСТ 3 ОШИБКА: {e}")
        results["minimal_params"] = False
    
    # Итоги
    print("\n" + "=" * 50)
    print("📊 ИТОГИ ОТЛАДКИ:")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Всего тестов: {total_tests}")
    print(f"Прошло тестов: {passed_tests}")
    print(f"Процент успеха: {success_rate:.1f}%")
    
    print("\nДетали:")
    for test_name, success in results.items():
        status = "✅ ПРОШЕЛ" if success else "❌ ПРОВАЛЕН"
        print(f"  {test_name}: {status}")
    
    # Сохраняем результаты
    with open("web_scraping_fix_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "tool": "enhanced_web_scraping_tool",
            "tests": results,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate
            },
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в web_scraping_fix_results.json")
    
    # Вердикт
    if success_rate >= 66:
        print("\n🎉 ENHANCED_WEB_SCRAPING_TOOL ИСПРАВЛЕН!")
        print("Инструмент работает с правильными async вызовами и параметрами")
        return True
    elif success_rate >= 33:
        print("\n⚠️ ENHANCED_WEB_SCRAPING_TOOL ЧАСТИЧНО РАБОТАЕТ")
        print("Требуется дополнительная отладка")
        return False
    else:
        print("\n❌ ENHANCED_WEB_SCRAPING_TOOL НЕ РАБОТАЕТ")
        print("Требуется серьезная доработка")
        return False

if __name__ == "__main__":
    asyncio.run(main()) 