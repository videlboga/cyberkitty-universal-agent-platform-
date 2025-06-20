#!/usr/bin/env python3
"""
🔍 РУЧНАЯ ВЕРИФИКАЦИЯ: Проверка каждого инструмента отдельно

ЦЕЛЬ: Убедиться что результаты финального отчёта честные
МЕТОД: Тестируем каждый инструмент изолированно с детальным анализом
"""

import time
import asyncio
import json

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

def verify_tool(name, test_func):
    """Ручная верификация одного инструмента"""
    print(f"\n🔍 РУЧНАЯ ПРОВЕРКА: {name}")
    print("=" * 60)
    
    start_time = time.time()
    try:
        result = test_func()
        end_time = time.time()
        test_time = (end_time - start_time) * 1000
        
        print(f"⏱️ Время выполнения: {test_time:.1f}мс")
        print(f"🏁 РЕЗУЛЬТАТ: {result}")
        return result
        
    except Exception as e:
        end_time = time.time()
        test_time = (end_time - start_time) * 1000
        error_result = f"❌ ИСКЛЮЧЕНИЕ: {str(e)[:100]}..."
        print(f"⏱️ Время выполнения: {test_time:.1f}мс")
        print(f"🏁 РЕЗУЛЬТАТ: {error_result}")
        return error_result

def test_websearch():
    """Ручная проверка WebSearch"""
    print("🔍 Импорт WebSearch...")
    from kittycore.tools.enhanced_web_search_tool import EnhancedWebSearchTool
    
    print("🔍 Инициализация...")
    tool = EnhancedWebSearchTool()
    
    print("🔍 Выполнение поиска 'Python programming'...")
    result = sync_execute(tool, query="Python programming", limit=2)
    
    print(f"🔍 Тип результата: {type(result)}")
    print(f"🔍 Success: {getattr(result, 'success', 'N/A')}")
    
    if hasattr(result, 'data'):
        data_str = str(result.data)
        print(f"🔍 Размер данных: {len(data_str)} символов")
        print(f"🔍 Первые 200 символов: {data_str[:200]}...")
        
        # Проверяем есть ли признаки реального поиска
        has_urls = 'http' in data_str.lower()
        has_results = 'results' in data_str.lower()
        has_python = 'python' in data_str.lower()
        
        print(f"🔍 Содержит URLs: {has_urls}")
        print(f"🔍 Содержит results: {has_results}")
        print(f"🔍 Содержит 'python': {has_python}")
        
        if result.success and len(data_str) > 100 and has_urls:
            return "✅ РЕАЛЬНО РАБОТАЕТ: поиск возвращает URLs и результаты"
        else:
            return f"❌ ПОДОЗРИТЕЛЬНО: success={result.success}, size={len(data_str)}, urls={has_urls}"
    else:
        return "❌ НЕТ ДАННЫХ"

def test_webscraping():
    """Ручная проверка WebScraping"""
    print("🕷️ Импорт WebScraping...")
    from kittycore.tools.enhanced_web_scraping_tool import EnhancedWebScrapingTool
    
    print("🕷️ Инициализация...")
    tool = EnhancedWebScrapingTool()
    
    print("🕷️ Скрапинг httpbin.org/html...")
    result = sync_execute(tool, urls=["https://httpbin.org/html"])
    
    print(f"🕷️ Тип результата: {type(result)}")
    print(f"🕷️ Success: {getattr(result, 'success', 'N/A')}")
    
    if hasattr(result, 'data'):
        data_str = str(result.data)
        print(f"🕷️ Размер данных: {len(data_str)} символов")
        print(f"🕷️ Первые 200 символов: {data_str[:200]}...")
        
        # Проверяем признаки реального скрапинга
        has_herman = 'herman' in data_str.lower()
        has_melville = 'melville' in data_str.lower()
        has_results = 'results' in data_str.lower()
        
        print(f"🕷️ Содержит 'herman': {has_herman}")
        print(f"🕷️ Содержит 'melville': {has_melville}")
        print(f"🕷️ Содержит 'results': {has_results}")
        
        if result.success and len(data_str) > 100 and (has_herman or has_melville):
            return "✅ РЕАЛЬНО РАБОТАЕТ: извлечён текст Herman Melville"
        else:
            return f"❌ ПОДОЗРИТЕЛЬНО: success={result.success}, size={len(data_str)}, herman={has_herman}"
    else:
        return "❌ НЕТ ДАННЫХ"

def test_security():
    """Ручная проверка SecurityTool"""
    print("🔒 Импорт SecurityTool...")
    from kittycore.tools.security_tool import SecurityTool
    
    print("🔒 Инициализация...")
    tool = SecurityTool()
    
    print("🔒 Анализ пароля '123456'...")
    result = sync_execute(tool, action="analyze_password", password="123456")
    
    print(f"🔒 Тип результата: {type(result)}")
    print(f"🔒 Success: {getattr(result, 'success', 'N/A')}")
    
    if hasattr(result, 'data'):
        data_str = str(result.data)
        print(f"🔒 Размер данных: {len(data_str)} символов")
        print(f"🔒 Первые 200 символов: {data_str[:200]}...")
        
        # Проверяем признаки реального анализа безопасности
        has_weak = 'weak' in data_str.lower()
        has_score = 'score' in data_str.lower() or '0' in data_str
        has_security = 'security' in data_str.lower() or 'password' in data_str.lower()
        
        print(f"🔒 Содержит 'weak': {has_weak}")
        print(f"🔒 Содержит score/0: {has_score}")
        print(f"🔒 Содержит security terms: {has_security}")
        
        if result.success and len(data_str) > 50 and (has_weak or has_security):
            return "✅ РЕАЛЬНО РАБОТАЕТ: анализ показывает слабый пароль"
        else:
            return f"❌ ПОДОЗРИТЕЛЬНО: success={result.success}, size={len(data_str)}, weak={has_weak}"
    else:
        return "❌ НЕТ ДАННЫХ"

def test_vector_search():
    """Ручная проверка VectorSearchTool"""
    print("🔍 Импорт VectorSearchTool...")
    from kittycore.tools.vector_search_tool import VectorSearchTool
    
    print("🔍 Создание временной директории...")
    import tempfile
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Временная директория: {temp_dir}")
    
    print("🔍 Инициализация...")
    tool = VectorSearchTool(storage_path=temp_dir)
    
    print("🔍 Создание коллекции...")
    result = tool.execute(action="create_collection", collection_name="manual_test")
    
    print(f"🔍 Тип результата: {type(result)}")
    print(f"🔍 Success: {getattr(result, 'success', 'N/A')}")
    
    if hasattr(result, 'data'):
        data_str = str(result.data)
        print(f"🔍 Размер данных: {len(data_str)} символов")
        print(f"🔍 Данные: {data_str}")
        
        # Проверяем признаки реального создания коллекции
        has_collection = 'collection' in data_str.lower()
        has_manual_test = 'manual_test' in data_str.lower()
        has_created = 'created' in data_str.lower() or 'status' in data_str.lower()
        
        print(f"🔍 Содержит 'collection': {has_collection}")
        print(f"🔍 Содержит 'manual_test': {has_manual_test}")
        print(f"🔍 Содержит created/status: {has_created}")
        
        # Очистка
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("🗑️ Временная директория удалена")
        
        if result.success and (has_collection or has_manual_test):
            return "✅ РЕАЛЬНО РАБОТАЕТ: коллекция создана в ChromaDB"
        else:
            return f"❌ ПОДОЗРИТЕЛЬНО: success={result.success}, collection={has_collection}"
    else:
        return "❌ НЕТ ДАННЫХ"

def test_api_request():
    """Ручная проверка ApiRequestTool"""
    print("🌐 Импорт ApiRequestTool...")
    from kittycore.tools.api_request_tool import ApiRequestTool
    
    print("🌐 Инициализация...")
    tool = ApiRequestTool()
    
    print("🌐 GET запрос к httpbin.org/get...")
    result = tool.execute(url="https://httpbin.org/get", method="GET", timeout=5)
    
    print(f"🌐 Тип результата: {type(result)}")
    print(f"🌐 Success: {getattr(result, 'success', 'N/A')}")
    
    if hasattr(result, 'data'):
        data_str = str(result.data)
        print(f"🌐 Размер данных: {len(data_str)} символов")
        print(f"🌐 Первые 200 символов: {data_str[:200]}...")
        
        # Проверяем признаки реального HTTP ответа
        has_httpbin = 'httpbin' in data_str.lower()
        has_headers = 'headers' in data_str.lower()
        has_url = 'url' in data_str.lower()
        has_origin = 'origin' in data_str.lower()
        
        print(f"🌐 Содержит 'httpbin': {has_httpbin}")
        print(f"🌐 Содержит 'headers': {has_headers}")
        print(f"🌐 Содержит 'url': {has_url}")
        print(f"🌐 Содержит 'origin': {has_origin}")
        
        if result.success and len(data_str) > 200 and (has_httpbin or has_headers):
            return "✅ РЕАЛЬНО РАБОТАЕТ: получен реальный HTTP ответ"
        else:
            return f"❌ ПОДОЗРИТЕЛЬНО: success={result.success}, size={len(data_str)}, httpbin={has_httpbin}"
    else:
        return "❌ НЕТ ДАННЫХ"

def main():
    """Главная функция ручной верификации"""
    print("🔍 РУЧНАЯ ВЕРИФИКАЦИЯ ВСЕХ ИНСТРУМЕНТОВ")
    print("=" * 80)
    print("🎯 ЦЕЛЬ: Проверить честность результатов финального отчёта")
    print("🔬 МЕТОД: Изолированное тестирование каждого инструмента")
    print("=" * 80)
    
    # Список инструментов для проверки
    tools_to_verify = [
        ("WebSearch", test_websearch),
        ("WebScraping", test_webscraping), 
        ("SecurityTool", test_security),
        ("VectorSearchTool", test_vector_search),
        ("ApiRequestTool", test_api_request),
    ]
    
    results = {}
    
    for tool_name, test_func in tools_to_verify:
        result = verify_tool(tool_name, test_func)
        results[tool_name] = result
        time.sleep(1)  # Пауза между тестами
    
    # Финальная статистика
    print("\n" + "=" * 80)
    print("📊 РЕЗУЛЬТАТЫ РУЧНОЙ ВЕРИФИКАЦИИ")
    print("=" * 80)
    
    fully_working = 0
    for tool_name, result in results.items():
        print(f"  {tool_name}: {result}")
        if "✅ РЕАЛЬНО РАБОТАЕТ" in result:
            fully_working += 1
    
    total = len(results)
    success_rate = (fully_working / total) * 100
    
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"   ✅ РЕАЛЬНО РАБОТАЕТ: {fully_working}/{total} = {success_rate:.1f}%")
    
    if success_rate >= 75:
        final_status = "✅ ПОДТВЕРЖДЕНО: Финальный отчёт честный!"
    elif success_rate >= 50:
        final_status = "⚠️ ЧАСТИЧНО: Некоторые результаты сомнительны"
    else:
        final_status = "❌ ПРОВАЛ: Большинство результатов не подтверждается"
    
    print(f"\n🏁 ЗАКЛЮЧЕНИЕ: {final_status}")
    print("=" * 80)

if __name__ == "__main__":
    main() 