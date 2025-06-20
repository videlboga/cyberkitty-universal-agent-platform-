#!/usr/bin/env python3
"""
🤖 ОТЛАДКА: ai_integration_tool
"""

import time
import json

try:
    from kittycore.tools.ai_integration_tool import AIIntegrationTool
    IMPORT_OK = True
    print("✅ Импорт ai_integration_tool успешен")
except ImportError as e:
    print(f"❌ ИМПОРТ ОШИБКА: {e}")
    IMPORT_OK = False

def test_vpn_status():
    """Тест получения статуса VPN"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🔒 Тестирую статус VPN...")
    tool = AIIntegrationTool()
    
    # Проверяем статус VPN (должно работать быстро)
    result = tool.execute("vpn_status")
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            if isinstance(data, dict):
                status = data.get('status', 'UNKNOWN')
                print(f"🔒 VPN статус: {status}")
    
    return result

def test_connection_test():
    """Тест проверки соединения"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🌐 Тестирую проверку соединения...")
    tool = AIIntegrationTool()
    
    # Быстрая проверка соединения
    result = tool.execute("test_connection")
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            if isinstance(data, dict):
                api_accessible = data.get('api_accessible', False)
                print(f"🌐 API доступен: {api_accessible}")
    
    return result

def test_stats():
    """Тест получения статистики"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📊 Тестирую получение статистики...")
    tool = AIIntegrationTool()
    
    # Получаем статистику использования
    result = tool.execute("get_stats")
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            if isinstance(data, dict):
                total_requests = data.get('total_requests', 0)
                total_cost = data.get('total_cost', 0.0)
                print(f"📈 Статистика: {total_requests} запросов, ${total_cost:.6f}")
    
    return result

def test_model_info():
    """Тест получения информации о модели"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🤖 Тестирую информацию о модели...")
    tool = AIIntegrationTool()
    
    # Получаем информацию о популярной модели (должно работать из кеша)
    result = tool.execute("get_model_info", model="gpt-3.5-turbo")
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            if isinstance(data, dict):
                model_name = data.get('name', 'UNKNOWN')
                context_length = data.get('context_length', 'UNKNOWN')
                print(f"🤖 Модель: {model_name}, контекст: {context_length}")
    
    return result

def is_result_honest(result, test_name):
    """Проверка честности результата"""
    if not result:
        print(f"❌ {test_name}: Пустой результат")
        return False
    
    # Проверяем базовую структуру ToolResult
    if not hasattr(result, 'success'):
        print(f"❌ {test_name}: Результат не ToolResult")
        return False
    
    success = result.success
    if not success:
        print(f"❌ {test_name}: success=False")
        if hasattr(result, 'error'):
            print(f"   Ошибка: {result.error}")
        return False
    
    # Конвертируем в строку для анализа
    data_str = str(result.data) if hasattr(result, 'data') else str(result)
    data_size = len(data_str)
    
    # Проверка на фейковые паттерны
    fake_patterns = [
        "ai_integration: успешно",
        "демо ответ",
        "заглушка модели"
    ]
    
    for pattern in fake_patterns:
        if pattern.lower() in data_str.lower():
            print(f"❌ {test_name}: Найден фейковый паттерн: {pattern}")
            return False
    
    # Проверка на реальные признаки AI интеграции
    ai_indicators = [
        "vpn", "connection", "api", "model", "status", "cost", "tokens", 
        "requests", "statistics", "wireguard", "openrouter"
    ]
    
    has_ai_data = any(indicator.lower() in data_str.lower() for indicator in ai_indicators)
    
    if not has_ai_data:
        print(f"❌ {test_name}: Нет признаков реальной AI интеграции")
        return False
    
    if data_size < 20:
        print(f"❌ {test_name}: Слишком маленький результат ({data_size} байт)")
        return False
    
    print(f"✅ {test_name}: ЧЕСТНЫЙ результат ({data_size} байт)")
    return True

def main():
    print("🤖 ОТЛАДКА: ai_integration_tool")
    
    if not IMPORT_OK:
        return
    
    results = {}
    
    # Тесты (все синхронные, быстрые)
    tests = [
        ("vpn_status", test_vpn_status),
        ("connection_test", test_connection_test),
        ("stats", test_stats),
        ("model_info", test_model_info)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*30}")
        print(f"ТЕСТ: {test_name}")
        try:
            result = test_func()
            results[test_name] = is_result_honest(result, test_name)
        except Exception as e:
            print(f"❌ ТЕСТ ОШИБКА: {e}")
            results[test_name] = False
    
    # Итоги
    print(f"\n{'='*50}")
    print("📊 ИТОГИ:")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Всего тестов: {total_tests}")
    print(f"Прошло тестов: {passed_tests}")
    print(f"Процент успеха: {success_rate:.1f}%")
    
    for test_name, success in results.items():
        status = "✅ ПРОШЕЛ" if success else "❌ ПРОВАЛЕН"
        print(f"  {test_name}: {status}")
    
    print(f"\n📊 Статус: {'✅ РАБОТАЕТ' if success_rate >= 75 else '❌ НЕ РАБОТАЕТ'}")

if __name__ == "__main__":
    main() 