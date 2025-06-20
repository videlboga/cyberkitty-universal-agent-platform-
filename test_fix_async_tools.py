#!/usr/bin/env python3
"""
🔧 ИСПРАВЛЕНИЕ: Async/Sync проблемы в инструментах

ПРОБЛЕМА: Многие инструменты имеют async def execute(), но вызываются синхронно
РЕШЕНИЕ: Универсальная синхронная обертка + тестирование исправлений
"""

import asyncio
import time
import json
import tempfile
import os

# Универсальная обертка для асинхронных инструментов
def sync_execute(async_tool, *args, **kwargs):
    """Универсальная синхронная обертка для async execute"""
    try:
        # Проверяем есть ли запущенный event loop
        loop = asyncio.get_running_loop()
        # Если да - выполняем в отдельном потоке
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, async_tool.execute(*args, **kwargs))
            return future.result(timeout=30)  # 30 сек таймаут
    except RuntimeError:
        # Нет запущенного loop - можем использовать asyncio.run
        return asyncio.run(async_tool.execute(*args, **kwargs))

# Импорты исправляемых инструментов
fixed_tools = {}

try:
    from kittycore.tools.enhanced_web_search_tool import EnhancedWebSearchTool
    fixed_tools['web_search'] = EnhancedWebSearchTool()
    print("✅ web_search импортирован")
except ImportError as e:
    print(f"❌ web_search: {e}")

try:
    from kittycore.tools.enhanced_web_scraping_tool import EnhancedWebScrapingTool
    fixed_tools['web_scraping'] = EnhancedWebScrapingTool()
    print("✅ web_scraping импортирован")
except ImportError as e:
    print(f"❌ web_scraping: {e}")

try:
    from kittycore.tools.security_tool import SecurityTool
    fixed_tools['security'] = SecurityTool()
    print("✅ security импортирован")
except ImportError as e:
    print(f"❌ security: {e}")

try:
    from kittycore.tools.api_request_tool import ApiRequestTool
    fixed_tools['api_request'] = ApiRequestTool()
    print("✅ api_request импортирован")
except ImportError as e:
    print(f"❌ api_request: {e}")

def test_fixed_web_search():
    """Тест исправленного web_search"""
    if 'web_search' not in fixed_tools:
        return "IMPORT_ERROR"
    
    print("\n🔍 ТЕСТ ИСПРАВЛЕННОГО: enhanced_web_search_tool")
    tool = fixed_tools['web_search']
    
    try:
        # Используем синхронную обертку
        result = sync_execute(tool, query="Python programming", limit=3)
        
        if hasattr(result, 'success') and result.success:
            data_str = str(result.data)
            size = len(data_str)
            
            # Проверяем реальность
            has_urls = any(indicator in data_str.lower() for indicator in ['http', 'www', '.com'])
            has_query = 'python' in data_str.lower()
            
            if has_urls and has_query and size > 100:
                return f"✅ ИСПРАВЛЕН: {size} байт, есть URL и запрос"
            else:
                return f"❌ ФЕЙК: {size} байт, URL={has_urls}, query={has_query}"
        else:
            error = getattr(result, 'error', 'Unknown error')
            return f"❌ ПРОВАЛ: {error}"
    
    except Exception as e:
        return f"❌ ИСКЛЮЧЕНИЕ: {e}"

def test_fixed_web_scraping():
    """Тест исправленного web_scraping"""
    if 'web_scraping' not in fixed_tools:
        return "IMPORT_ERROR"
    
    print("\n🕷️ ТЕСТ ИСПРАВЛЕННОГО: enhanced_web_scraping_tool")
    tool = fixed_tools['web_scraping']
    
    try:
        # Используем синхронную обертку с правильными параметрами
        result = sync_execute(tool, urls=["https://httpbin.org/html"])
        
        if hasattr(result, 'success') and result.success:
            data_str = str(result.data)
            size = len(data_str)
            
            # Проверяем реальность извлеченного ТЕКСТА (не HTML тегов!)
            has_content = 'herman melville' in data_str.lower()
            has_results = 'results' in data_str and 'text_preview' in data_str
            has_real_size = size > 500  # Реальный контент должен быть значительным
            
            if has_content and has_results and has_real_size:
                return f"✅ ИСПРАВЛЕН: {size} байт, content={has_content}, results={has_results}"
            else:
                return f"❌ ФЕЙК: {size} байт, content={has_content}, results={has_results}"
        else:
            error = getattr(result, 'error', 'Unknown error')
            return f"❌ ПРОВАЛ: {error}"
    
    except Exception as e:
        return f"❌ ИСКЛЮЧЕНИЕ: {e}"

def test_fixed_security_tool():
    """Тест исправленного security_tool"""
    if 'security' not in fixed_tools:
        return "IMPORT_ERROR"
    
    print("\n🔒 ТЕСТ ИСПРАВЛЕННОГО: security_tool")
    tool = fixed_tools['security']
    
    try:
        # Используем синхронную обертку
        result = sync_execute(tool, "analyze_password", password="TestPassword123!")
        
        if hasattr(result, 'success') and result.success:
            data_str = str(result.data)
            size = len(data_str)
            
            # Проверяем реальность анализа безопасности
            has_security = any(term in data_str.lower() for term in ['strength', 'score', 'password'])
            has_details = size > 200  # Полный анализ должен быть детальным
            
            if has_security and has_details:
                return f"✅ ИСПРАВЛЕН: {size} байт, security terms found"
            else:
                return f"❌ ФЕЙК: {size} байт, security={has_security}"
        else:
            error = getattr(result, 'error', 'Unknown error')
            return f"❌ ПРОВАЛ: {error}"
    
    except Exception as e:
        return f"❌ ИСКЛЮЧЕНИЕ: {e}"

def test_fixed_api_request():
    """Тест исправленного api_request_tool"""
    if 'api_request' not in fixed_tools:
        return "IMPORT_ERROR"
    
    print("\n🌐 ТЕСТ ИСПРАВЛЕННОГО: api_request_tool")
    tool = fixed_tools['api_request']
    
    try:
        # api_request_tool обычно синхронный, но проверим
        result = tool.execute(url="https://httpbin.org/get", method="GET", timeout=10)
        
        if hasattr(result, 'success') and result.success:
            data_str = str(result.data)
            size = len(data_str)
            
            # Проверяем реальность HTTP ответа
            has_http = any(term in data_str.lower() for term in ['status', '200', 'headers'])
            has_url = 'httpbin' in data_str.lower()
            
            if has_http and has_url and size > 100:
                return f"✅ РАБОТАЕТ: {size} байт, HTTP response"
            else:
                return f"❌ ФЕЙК: {size} байт, HTTP={has_http}, URL={has_url}"
        else:
            error = getattr(result, 'error', 'Unknown error')
            return f"❌ ПРОВАЛ: {error}"
    
    except Exception as e:
        return f"❌ ИСКЛЮЧЕНИЕ: {e}"

def main():
    print("🔧 ИСПРАВЛЕНИЕ ASYNC/SYNC ПРОБЛЕМ В ИНСТРУМЕНТАХ")
    print("=" * 60)
    
    # Тесты исправлений
    tests = {
        "WebSearch": test_fixed_web_search,
        "WebScraping": test_fixed_web_scraping,
        "SecurityTool": test_fixed_security_tool,
        "ApiRequest": test_fixed_api_request
    }
    
    results = {}
    
    for tool_name, test_func in tests.items():
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            test_time = (end_time - start_time) * 1000
            
            # Определяем статус
            is_fixed = result.startswith("✅")
            status = "✅ ИСПРАВЛЕН" if is_fixed else "❌ НЕ ИСПРАВЛЕН"
            
            print(f"{tool_name}: {result} ({test_time:.1f}мс)")
            results[tool_name] = is_fixed
            
        except Exception as e:
            print(f"{tool_name}: ❌ ИСКЛЮЧЕНИЕ: {e}")
            results[tool_name] = False
    
    # Итоги исправлений
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ИСПРАВЛЕНИЙ:")
    
    total_tests = len(results)
    fixed_tools_count = sum(1 for is_fixed in results.values() if is_fixed)
    fix_rate = (fixed_tools_count / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Всего протестировано: {total_tests}")
    print(f"Исправлено инструментов: {fixed_tools_count}")
    print(f"Процент исправлений: {fix_rate:.1f}%")
    
    print("\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    for tool_name, is_fixed in results.items():
        status = "✅ ИСПРАВЛЕН" if is_fixed else "❌ НЕ ИСПРАВЛЕН"
        print(f"  {tool_name}: {status}")
    
    # Рекомендации
    broken_tools = [name for name, is_fixed in results.items() if not is_fixed]
    if broken_tools:
        print(f"\n🔧 ТРЕБУЮТ ДОПОЛНИТЕЛЬНЫХ ИСПРАВЛЕНИЙ: {', '.join(broken_tools)}")
    else:
        print(f"\n🎉 ВСЕ ИНСТРУМЕНТЫ УСПЕШНО ИСПРАВЛЕНЫ!")

if __name__ == "__main__":
    main() 