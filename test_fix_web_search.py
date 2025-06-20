#!/usr/bin/env python3
"""
🔍 ОТЛАДКА: enhanced_web_search_tool
Проверяем правильные async вызовы и параметры

ПРОБЛЕМЫ ИЗ ПАМЯТИ:
- Инструмент требует async/await
- Неправильные параметры (нет action, есть query/limit)
- Нет max_results, есть limit

ПЛАН ОТЛАДКИ:
1. Правильный async вызов
2. Правильные параметры (query, limit)
3. Проверка реальных веб-данных
"""

import asyncio
import time
import json

# Импорт инструмента
try:
    from kittycore.tools.enhanced_web_search_tool import EnhancedWebSearchTool
    IMPORT_OK = True
    print("✅ Импорт enhanced_web_search_tool успешен")
except ImportError as e:
    print(f"❌ ИМПОРТ ОШИБКА: {e}")
    IMPORT_OK = False

async def test_web_search_correct():
    """Правильный тест с async и корректными параметрами"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🔍 Тестирую enhanced_web_search с правильными параметрами...")
    start_time = time.time()
    
    tool = EnhancedWebSearchTool()
    
    # ПРАВИЛЬНЫЙ вызов: await + query + limit (НЕ action, НЕ max_results)
    result = await tool.execute(
        query="Python programming tutorial",
        limit=3
    )
    
    execution_time = time.time() - start_time
    
    print(f"⏱️ Время выполнения: {execution_time:.2f}с")
    print(f"📊 Результат: {type(result)}")
    
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data_size = len(str(result.data))
            print(f"📦 Размер данных: {data_size} байт")
            
            # Проверим структуру данных
            if isinstance(result.data, dict):
                print(f"🔑 Ключи данных: {list(result.data.keys())}")
                if 'results' in result.data:
                    results_count = len(result.data['results'])
                    print(f"🔢 Количество результатов: {results_count}")
                    
                    # Покажем первый результат
                    if results_count > 0:
                        first_result = result.data['results'][0]
                        print(f"🎯 Первый результат:")
                        print(f"   Заголовок: {first_result.get('title', 'НЕТ')[:50]}...")
                        print(f"   URL: {first_result.get('url', 'НЕТ')[:50]}...")
                        print(f"   Фрагмент: {first_result.get('snippet', 'НЕТ')[:80]}...")
        else:
            print(f"❌ Ошибка: {getattr(result, 'error', 'НЕИЗВЕСТНО')}")
    
    return result

async def test_web_search_simple():
    """Простой тест с минимальными параметрами"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🔍 Простой тест enhanced_web_search...")
    
    tool = EnhancedWebSearchTool()
    
    # Минимальный вызов - только query
    result = await tool.execute(query="test")
    
    print(f"📊 Простой тест результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success:
            data_size = len(str(result.data)) if hasattr(result, 'data') else 0
            print(f"📦 Размер: {data_size} байт")
    
    return result

async def test_web_search_sources():
    """Тест с разными источниками"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🔍 Тест enhanced_web_search с источниками...")
    
    tool = EnhancedWebSearchTool()
    
    # Тест с конкретными источниками
    result = await tool.execute(
        query="KittyCore",
        limit=2,
        sources=["duckduckgo"]
    )
    
    print(f"📊 Тест источников результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
    
    return result

def is_result_honest(result, test_name):
    """Проверка честности результата"""
    if not result:
        print(f"❌ {test_name}: Пустой результат")
        return False
    
    if not hasattr(result, 'success'):
        print(f"❌ {test_name}: Нет атрибута success")
        return False
    
    if not result.success:
        print(f"❌ {test_name}: success=False")
        if hasattr(result, 'error'):
            print(f"   Ошибка: {result.error}")
        return False
    
    if not hasattr(result, 'data') or not result.data:
        print(f"❌ {test_name}: Нет данных")
        return False
    
    data_str = str(result.data)
    data_size = len(data_str)
    
    # Проверка на фейковые паттерны
    fake_patterns = [
        "enhanced_web_search: успешно",
        "демо поиск",
        "заглушка поиска",
        "тестовые результаты"
    ]
    
    for pattern in fake_patterns:
        if pattern.lower() in data_str.lower():
            print(f"❌ {test_name}: Найден фейковый паттерн: {pattern}")
            return False
    
    # Проверка на реальные веб-признаки
    web_indicators = [
        "url", "title", "snippet", "http", "results"
    ]
    
    has_web_data = any(indicator in data_str.lower() for indicator in web_indicators)
    
    if not has_web_data:
        print(f"❌ {test_name}: Нет признаков веб-данных")
        return False
    
    if data_size < 50:
        print(f"❌ {test_name}: Слишком маленький результат ({data_size} байт)")
        return False
    
    print(f"✅ {test_name}: ЧЕСТНЫЙ результат ({data_size} байт)")
    return True

async def main():
    """Главная функция отладки"""
    print("🔍 ОТЛАДКА: enhanced_web_search_tool")
    print("=" * 50)
    
    if not IMPORT_OK:
        print("❌ Невозможно продолжить - ошибка импорта")
        return
    
    results = {}
    
    # Тест 1: Правильный полный тест
    print("\n" + "=" * 30)
    print("ТЕСТ 1: Правильные параметры")
    try:
        result1 = await test_web_search_correct()
        results["correct_params"] = is_result_honest(result1, "Правильные параметры")
    except Exception as e:
        print(f"❌ ТЕСТ 1 ОШИБКА: {e}")
        results["correct_params"] = False
    
    # Тест 2: Простой тест
    print("\n" + "=" * 30)
    print("ТЕСТ 2: Минимальные параметры")
    try:
        result2 = await test_web_search_simple()
        results["simple_params"] = is_result_honest(result2, "Минимальные параметры")
    except Exception as e:
        print(f"❌ ТЕСТ 2 ОШИБКА: {e}")
        results["simple_params"] = False
    
    # Тест 3: Тест источников
    print("\n" + "=" * 30)
    print("ТЕСТ 3: Конкретные источники")
    try:
        result3 = await test_web_search_sources()
        results["sources_params"] = is_result_honest(result3, "Конкретные источники")
    except Exception as e:
        print(f"❌ ТЕСТ 3 ОШИБКА: {e}")
        results["sources_params"] = False
    
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
    with open("web_search_fix_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "tool": "enhanced_web_search_tool",
            "tests": results,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate
            },
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в web_search_fix_results.json")
    
    # Вердикт
    if success_rate >= 66:
        print("\n🎉 ENHANCED_WEB_SEARCH_TOOL ИСПРАВЛЕН!")
        print("Инструмент работает с правильными async вызовами и параметрами")
        return True
    elif success_rate >= 33:
        print("\n⚠️ ENHANCED_WEB_SEARCH_TOOL ЧАСТИЧНО РАБОТАЕТ")
        print("Требуется дополнительная отладка")
        return False
    else:
        print("\n❌ ENHANCED_WEB_SEARCH_TOOL НЕ РАБОТАЕТ")
        print("Требуется серьезная доработка")
        return False

if __name__ == "__main__":
    asyncio.run(main()) 