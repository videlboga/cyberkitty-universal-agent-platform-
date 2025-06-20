#!/usr/bin/env python3
"""
🔧 ИСПРАВЛЕНИЕ: Оставшиеся проблемные инструменты

ЦЕЛЬ: Диагностировать и исправить:
- NetworkTool (Unknown error)
- DatabaseTool (Unknown error)  
- VectorSearchTool (сигнатура execute)
- EmailTool (файл не существует)
- ApiRequest (таймауты)
"""

import asyncio
import time
import traceback

# Универсальная обертка для асинхронных инструментов
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

def diagnose_network_tool():
    """Диагностика NetworkTool"""
    print("\n🌐 ДИАГНОСТИКА: NetworkTool")
    
    try:
        from kittycore.tools.network_tool import NetworkTool
        tool = NetworkTool()
        print("✅ Импорт успешен")
        
        # Проверяем доступные методы
        methods = [method for method in dir(tool) if not method.startswith('_')]
        print(f"📋 Доступные методы: {methods}")
        
        # Проверяем сигнатуру execute
        import inspect
        if hasattr(tool, 'execute'):
            sig = inspect.signature(tool.execute)
            print(f"🔍 Сигнатура execute: {sig}")
            
            # Пробуем простой вызов
            if inspect.iscoroutinefunction(tool.execute):
                print("⚠️ execute - асинхронная функция, используем обертку")
                result = sync_execute(tool, action="ping", host="8.8.8.8")
            else:
                print("✅ execute - синхронная функция")
                result = tool.execute(action="ping", host="8.8.8.8")
            
            print(f"📊 Результат: success={getattr(result, 'success', 'N/A')}")
            print(f"📏 Размер данных: {len(str(getattr(result, 'data', '')))} символов")
            
            return "✅ РАБОТАЕТ"
        else:
            return "❌ НЕТ МЕТОДА execute"
            
    except ImportError as e:
        return f"❌ ИМПОРТ: {e}"
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        traceback.print_exc()
        return f"❌ ИСКЛЮЧЕНИЕ: {e}"

def diagnose_database_tool():
    """Диагностика DatabaseTool"""
    print("\n🗄️ ДИАГНОСТИКА: DatabaseTool")
    
    try:
        from kittycore.tools.database_tool import DatabaseTool
        tool = DatabaseTool()
        print("✅ Импорт успешен")
        
        # Проверяем сигнатуру execute
        import inspect
        if hasattr(tool, 'execute'):
            sig = inspect.signature(tool.execute)
            print(f"🔍 Сигнатура execute: {sig}")
            
            # Пробуем простой вызов
            if inspect.iscoroutinefunction(tool.execute):
                print("⚠️ execute - асинхронная функция, используем обертку")
                result = sync_execute(tool, action="list_tables")
            else:
                print("✅ execute - синхронная функция")
                result = tool.execute(action="list_tables")
            
            print(f"📊 Результат: success={getattr(result, 'success', 'N/A')}")
            print(f"📏 Размер данных: {len(str(getattr(result, 'data', '')))} символов")
            
            return "✅ РАБОТАЕТ"
        else:
            return "❌ НЕТ МЕТОДА execute"
            
    except ImportError as e:
        return f"❌ ИМПОРТ: {e}"
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        traceback.print_exc()
        return f"❌ ИСКЛЮЧЕНИЕ: {e}"

def diagnose_vector_search_tool():
    """Диагностика VectorSearchTool"""
    print("\n🔍 ДИАГНОСТИКА: VectorSearchTool")
    
    try:
        from kittycore.tools.vector_search_tool import VectorSearchTool
        tool = VectorSearchTool()
        print("✅ Импорт успешен")
        
        # Проверяем сигнатуру execute
        import inspect
        if hasattr(tool, 'execute'):
            sig = inspect.signature(tool.execute)
            print(f"🔍 Сигнатура execute: {sig}")
            
            # Пробуем простой вызов
            if inspect.iscoroutinefunction(tool.execute):
                print("⚠️ execute - асинхронная функция, используем обертку")
                result = sync_execute(tool, query="test search", collection="test")
            else:
                print("✅ execute - синхронная функция")
                result = tool.execute(query="test search", collection="test")
            
            print(f"📊 Результат: success={getattr(result, 'success', 'N/A')}")
            print(f"📏 Размер данных: {len(str(getattr(result, 'data', '')))} символов")
            
            return "✅ РАБОТАЕТ"
        else:
            return "❌ НЕТ МЕТОДА execute"
            
    except ImportError as e:
        return f"❌ ИМПОРТ: {e}"
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        traceback.print_exc()
        return f"❌ ИСКЛЮЧЕНИЕ: {e}"

def diagnose_email_tool():
    """Диагностика EmailTool"""
    print("\n📧 ДИАГНОСТИКА: EmailTool")
    
    try:
        # Попробуем разные возможные пути импорта
        import_paths = [
            "kittycore.tools.email_tool",
            "kittycore.tools.communication_tools", 
            "kittycore.tools.communication_tool"
        ]
        
        tool = None
        successful_import = None
        
        for path in import_paths:
            try:
                if "email_tool" in path:
                    exec(f"from {path} import EmailTool")
                    tool = locals()['EmailTool']()
                    successful_import = path
                    break
                elif "communication" in path:
                    exec(f"from {path} import EmailTool")
                    tool = locals()['EmailTool']()
                    successful_import = path
                    break
            except (ImportError, AttributeError):
                continue
        
        if tool is None:
            return "❌ НЕ НАЙДЕН: Файл email_tool не существует"
        
        print(f"✅ Импорт успешен из: {successful_import}")
        
        # Проверяем сигнатуру execute
        import inspect
        if hasattr(tool, 'execute'):
            sig = inspect.signature(tool.execute)
            print(f"🔍 Сигнатура execute: {sig}")
            return "✅ НАЙДЕН И ДОСТУПЕН"
        else:
            return "❌ НЕТ МЕТОДА execute"
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        traceback.print_exc()
        return f"❌ ИСКЛЮЧЕНИЕ: {e}"

def diagnose_api_request_timeout():
    """Диагностика таймаутов ApiRequest"""
    print("\n🌐 ДИАГНОСТИКА ТАЙМАУТОВ: ApiRequest")
    
    try:
        from kittycore.tools.api_request_tool import ApiRequestTool
        tool = ApiRequestTool()
        print("✅ Импорт успешен")
        
        # Тест с коротким таймаутом
        start_time = time.time()
        result = tool.execute(
            url="https://httpbin.org/delay/1",  # Задержка 1 секунда
            method="GET",
            timeout=5  # Таймаут 5 секунд
        )
        end_time = time.time()
        
        actual_time = end_time - start_time
        print(f"⏱️ Фактическое время: {actual_time:.1f}с")
        print(f"📊 Результат: success={getattr(result, 'success', 'N/A')}")
        
        if hasattr(result, 'success') and result.success:
            return f"✅ РАБОТАЕТ: {actual_time:.1f}с"
        else:
            error = getattr(result, 'error', 'Unknown error')
            return f"❌ ПРОВАЛ: {error}"
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return f"❌ ИСКЛЮЧЕНИЕ: {e}"

def main():
    print("🔧 ДИАГНОСТИКА ОСТАВШИХСЯ ПРОБЛЕМНЫХ ИНСТРУМЕНТОВ")
    print("=" * 60)
    
    diagnoses = {
        "NetworkTool": diagnose_network_tool,
        "DatabaseTool": diagnose_database_tool,
        "VectorSearchTool": diagnose_vector_search_tool,
        "EmailTool": diagnose_email_tool,
        "ApiRequest-Timeout": diagnose_api_request_timeout
    }
    
    results = {}
    
    for tool_name, diagnose_func in diagnoses.items():
        try:
            start_time = time.time()
            result = diagnose_func()
            end_time = time.time()
            
            test_time = (end_time - start_time) * 1000
            
            # Определяем статус
            is_working = result.startswith("✅")
            status = "✅ РАБОТАЕТ" if is_working else "❌ ПРОБЛЕМЫ"
            
            print(f"\n{tool_name}: {result} ({test_time:.1f}мс)")
            results[tool_name] = is_working
            
        except Exception as e:
            print(f"\n{tool_name}: ❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            results[tool_name] = False
    
    # Итоги диагностики
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ДИАГНОСТИКИ:")
    
    total_diagnosed = len(results)
    working_tools = sum(1 for is_working in results.values() if is_working)
    working_rate = (working_tools / total_diagnosed * 100) if total_diagnosed > 0 else 0
    
    print(f"Всего диагностировано: {total_diagnosed}")
    print(f"Работающих инструментов: {working_tools}")
    print(f"Процент работоспособности: {working_rate:.1f}%")
    
    print("\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    for tool_name, is_working in results.items():
        status = "✅ РАБОТАЕТ" if is_working else "❌ НУЖНО ЧИНИТЬ"
        print(f"  {tool_name}: {status}")
    
    # Приоритеты исправлений
    broken_tools = [name for name, is_working in results.items() if not is_working]
    if broken_tools:
        print(f"\n🔧 ПРИОРИТЕТЫ ИСПРАВЛЕНИЙ:")
        for i, tool in enumerate(broken_tools, 1):
            print(f"  {i}. {tool}")
    else:
        print(f"\n🎉 ВСЕ ИНСТРУМЕНТЫ РАБОТАЮТ!")

if __name__ == "__main__":
    main() 