#!/usr/bin/env python3
"""
🚀 ОТЛАДКА: 4 оставшихся инструмента
NetworkTool, DatabaseTool, VectorSearchTool, EmailTool
"""

import time
import json

# Импорты инструментов
imports = {}
tools = {}

try:
    from kittycore.tools.network_tool import NetworkTool
    imports['network'] = True
    tools['network'] = NetworkTool()
except ImportError as e:
    imports['network'] = str(e)

try:
    from kittycore.tools.database_tool import DatabaseTool
    imports['database'] = True
    tools['database'] = DatabaseTool()
except ImportError as e:
    imports['database'] = str(e)

try:
    from kittycore.tools.vector_search_tool import VectorSearchTool
    imports['vector_search'] = True
    tools['vector_search'] = VectorSearchTool()
except ImportError as e:
    imports['vector_search'] = str(e)

try:
    from kittycore.tools.email_tool import EmailTool
    imports['email'] = True
    tools['email'] = EmailTool()
except ImportError as e:
    imports['email'] = str(e)

def test_network_tool():
    """Быстрый тест NetworkTool"""
    if imports['network'] != True:
        return f"IMPORT_ERROR: {imports['network']}"
    
    tool = tools['network']
    
    # Тест ping localhost
    result = tool.execute("ping", host="127.0.0.1", count=1)
    
    if hasattr(result, 'success') and result.success:
        data_str = str(result.data)
        return f"SUCCESS: {len(data_str)} байт"
    else:
        error = getattr(result, 'error', 'Unknown error')
        return f"FAILED: {error}"

def test_database_tool():
    """Быстрый тест DatabaseTool"""
    if imports['database'] != True:
        return f"IMPORT_ERROR: {imports['database']}"
    
    tool = tools['database']
    
    # Тест получения информации
    result = tool.execute("get_info")
    
    if hasattr(result, 'success') and result.success:
        data_str = str(result.data)
        return f"SUCCESS: {len(data_str)} байт"
    else:
        error = getattr(result, 'error', 'Unknown error')
        return f"FAILED: {error}"

def test_vector_search_tool():
    """Быстрый тест VectorSearchTool"""
    if imports['vector_search'] != True:
        return f"IMPORT_ERROR: {imports['vector_search']}"
    
    tool = tools['vector_search']
    
    # Тест получения статистики
    result = tool.execute("get_stats")
    
    if hasattr(result, 'success') and result.success:
        data_str = str(result.data)
        return f"SUCCESS: {len(data_str)} байт"
    else:
        error = getattr(result, 'error', 'Unknown error')
        return f"FAILED: {error}"

def test_email_tool():
    """Быстрый тест EmailTool"""
    if imports['email'] != True:
        return f"IMPORT_ERROR: {imports['email']}"
    
    tool = tools['email']
    
    # Тест получения информации
    result = tool.execute("get_info")
    
    if hasattr(result, 'success') and result.success:
        data_str = str(result.data)
        return f"SUCCESS: {len(data_str)} байт"
    else:
        error = getattr(result, 'error', 'Unknown error')
        return f"FAILED: {error}"

def is_honest_result(test_result):
    """Проверка честности результата"""
    if "SUCCESS:" in test_result:
        # Извлекаем размер данных
        try:
            size = int(test_result.split(" ")[1])
            return size >= 30  # Минимум 30 байт для честного результата
        except:
            return False
    return False

def main():
    print("🚀 ОТЛАДКА: 4 оставшихся инструмента")
    
    # Показываем статус импортов
    print("\n📦 СТАТУС ИМПОРТОВ:")
    for tool_name, status in imports.items():
        if status == True:
            print(f"  ✅ {tool_name}_tool: импорт успешен")
        else:
            print(f"  ❌ {tool_name}_tool: {status}")
    
    # Быстрые тесты
    test_functions = {
        'NetworkTool': test_network_tool,
        'DatabaseTool': test_database_tool, 
        'VectorSearchTool': test_vector_search_tool,
        'EmailTool': test_email_tool
    }
    
    results = {}
    
    print(f"\n{'='*50}")
    print("🧪 БЫСТРЫЕ ТЕСТЫ:")
    
    for tool_name, test_func in test_functions.items():
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            test_time = (end_time - start_time) * 1000  # в миллисекундах
            
            is_honest = is_honest_result(result)
            status = "✅ РАБОТАЕТ" if is_honest else "❌ НЕ РАБОТАЕТ"
            
            print(f"  {tool_name}: {result} ({test_time:.1f}мс) - {status}")
            results[tool_name] = is_honest
            
        except Exception as e:
            print(f"  {tool_name}: EXCEPTION: {e} - ❌ НЕ РАБОТАЕТ")
            results[tool_name] = False
    
    # Итоги
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{'='*50}")
    print("📊 ИТОГИ ОСТАВШИХСЯ 4 ИНСТРУМЕНТОВ:")
    print(f"Всего тестов: {total_tests}")
    print(f"Прошло тестов: {passed_tests}")
    print(f"Процент успеха: {success_rate:.1f}%")
    
    # Статус каждого инструмента
    for tool_name, success in results.items():
        status = "✅ ПРОШЕЛ" if success else "❌ ПРОВАЛЕН"
        print(f"  {tool_name}: {status}")

if __name__ == "__main__":
    main() 