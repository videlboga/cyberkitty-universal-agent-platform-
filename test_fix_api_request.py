#!/usr/bin/env python3
"""
🌐 ОТЛАДКА: api_request_tool
Проверяем реальные HTTP запросы к API

ОСОБЕННОСТИ:
- Инструмент СИНХРОННЫЙ (НЕ async)
- Основные параметры: url (обязательный), method, headers, data, params, timeout
- Поддерживает все HTTP методы
- НЕ требует API ключей для публичных API

ПЛАН ОТЛАДКИ:
1. Правильный синхронный вызов
2. Правильные параметры (url, method)
3. Проверка реальных API запросов
4. Тест разных HTTP методов
"""

import time
import json

# Импорт инструмента
try:
    from kittycore.tools.api_request_tool import ApiRequestTool
    IMPORT_OK = True
    print("✅ Импорт api_request_tool успешен")
except ImportError as e:
    print(f"❌ ИМПОРТ ОШИБКА: {e}")
    IMPORT_OK = False

def test_api_get_request():
    """Тест GET запроса к публичному API"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🌐 Тестирую api_request с GET запросом...")
    start_time = time.time()
    
    tool = ApiRequestTool()
    
    # ПРАВИЛЬНЫЙ вызов: обычный execute (НЕ await) + url + method
    result = tool.execute(
        url="https://httpbin.org/json",
        method="GET",
        timeout=10
    )
    
    execution_time = time.time() - start_time
    
    print(f"⏱️ Время выполнения: {execution_time:.2f}с")
    print(f"📊 Результат: {type(result)}")
    
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            print(f"📦 Размер данных: {len(str(data))} байт")
            
            # Проверим структуру данных
            if isinstance(data, dict):
                print(f"🔑 Ключи данных: {list(data.keys())}")
                
                # Проверяем структуру ответа
                if 'response' in data:
                    response = data['response']
                    print(f"📡 Статус код: {response.get('status_code', 'НЕТ')}")
                    print(f"✅ Success: {response.get('success', 'НЕТ')}")
                    print(f"⏱️ Время ответа: {response.get('response_time', 'НЕТ')}с")
                    
                    # Проверяем реальные данные
                    response_data = response.get('data', {})
                    if isinstance(response_data, dict):
                        print(f"📊 Ключи ответа: {list(response_data.keys())[:5]}...")
        else:
            print(f"❌ Ошибка: {getattr(result, 'error', 'НЕИЗВЕСТНО')}")
    
    return result

def test_api_post_request():
    """Тест POST запроса с данными"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🌐 Тестирую api_request с POST запросом...")
    
    tool = ApiRequestTool()
    
    # Тест POST с JSON данными
    result = tool.execute(
        url="https://httpbin.org/post",
        method="POST",
        data={"test_key": "test_value", "timestamp": time.time()},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"📊 POST результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            response = data.get('response', {})
            print(f"📡 Статус код: {response.get('status_code', 'НЕТ')}")
            
            # Проверяем, что наши данные были отправлены
            response_data = response.get('data', {})
            if isinstance(response_data, dict) and 'json' in response_data:
                sent_data = response_data['json']
                print(f"📤 Отправленные данные получены: {bool(sent_data)}")
                print(f"🔑 Ключи отправленных данных: {list(sent_data.keys()) if sent_data else 'НЕТ'}")
    
    return result

def test_api_params_request():
    """Тест GET запроса с параметрами"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🌐 Тестирую api_request с параметрами...")
    
    tool = ApiRequestTool()
    
    # Тест GET с URL параметрами
    result = tool.execute(
        url="https://httpbin.org/get",
        method="GET",
        params={"param1": "value1", "param2": "value2"}
    )
    
    print(f"📊 Params результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            response = data.get('response', {})
            response_data = response.get('data', {})
            
            # Проверяем, что параметры были переданы
            if isinstance(response_data, dict) and 'args' in response_data:
                args = response_data['args']
                print(f"📥 Параметры получены: {bool(args)}")
                print(f"🔑 Параметры: {args}")
    
    return result

def test_api_action_method():
    """Тест через execute_action API"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🌐 Тестирую api_request через execute_action...")
    
    tool = ApiRequestTool()
    
    # Тест через action API
    result = tool.execute_action(
        action="get",
        url="https://httpbin.org/uuid"
    )
    
    print(f"📊 Action API результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            response = data.get('response', {})
            response_data = response.get('data', {})
            print(f"🆔 UUID получен: {'uuid' in str(response_data)}")
    
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
    
    data = result.data
    data_str = str(data)
    data_size = len(data_str)
    
    # Проверка на фейковые паттерны
    fake_patterns = [
        "api_request: успешно",
        "демо api",
        "заглушка api",
        "тестовый запрос"
    ]
    
    for pattern in fake_patterns:
        if pattern.lower() in data_str.lower():
            print(f"❌ {test_name}: Найден фейковый паттерн: {pattern}")
            return False
    
    # Проверка на реальные признаки HTTP API
    api_indicators = [
        "status_code", "response_time", "headers", "url", "method", "httpbin", "json"
    ]
    
    has_api_data = any(indicator in data_str.lower() for indicator in api_indicators)
    
    if not has_api_data:
        print(f"❌ {test_name}: Нет признаков реального API запроса")
        return False
    
    if data_size < 100:
        print(f"❌ {test_name}: Слишком маленький результат ({data_size} байт)")
        return False
    
    # Проверяем структуру API ответа
    if not isinstance(data, dict):
        print(f"❌ {test_name}: Данные не являются словарем")
        return False
    
    # Проверяем наличие базовых полей
    required_fields = ['request', 'response']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        print(f"❌ {test_name}: Отсутствуют обязательные поля: {missing_fields}")
        return False
    
    # Проверяем статус код
    response = data.get('response', {})
    status_code = response.get('status_code')
    
    if not isinstance(status_code, int) or status_code < 100 or status_code >= 600:
        print(f"❌ {test_name}: Неверный статус код: {status_code}")
        return False
    
    print(f"✅ {test_name}: ЧЕСТНЫЙ результат ({data_size} байт, статус {status_code})")
    return True

def main():
    """Главная функция отладки"""
    print("🌐 ОТЛАДКА: api_request_tool")
    print("=" * 50)
    
    if not IMPORT_OK:
        print("❌ Невозможно продолжить - ошибка импорта")
        return
    
    results = {}
    
    # Тест 1: GET запрос
    print("\n" + "=" * 30)
    print("ТЕСТ 1: GET запрос")
    try:
        result1 = test_api_get_request()
        results["get_request"] = is_result_honest(result1, "GET запрос")
    except Exception as e:
        print(f"❌ ТЕСТ 1 ОШИБКА: {e}")
        results["get_request"] = False
    
    # Тест 2: POST запрос
    print("\n" + "=" * 30)
    print("ТЕСТ 2: POST запрос")
    try:
        result2 = test_api_post_request()
        results["post_request"] = is_result_honest(result2, "POST запрос")
    except Exception as e:
        print(f"❌ ТЕСТ 2 ОШИБКА: {e}")
        results["post_request"] = False
    
    # Тест 3: Параметры
    print("\n" + "=" * 30)
    print("ТЕСТ 3: Запрос с параметрами")
    try:
        result3 = test_api_params_request()
        results["params_request"] = is_result_honest(result3, "Запрос с параметрами")
    except Exception as e:
        print(f"❌ ТЕСТ 3 ОШИБКА: {e}")
        results["params_request"] = False
    
    # Тест 4: Action API
    print("\n" + "=" * 30)
    print("ТЕСТ 4: Action API")
    try:
        result4 = test_api_action_method()
        results["action_api"] = is_result_honest(result4, "Action API")
    except Exception as e:
        print(f"❌ ТЕСТ 4 ОШИБКА: {e}")
        results["action_api"] = False
    
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
    with open("api_request_fix_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "tool": "api_request_tool",
            "tests": results,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate
            },
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в api_request_fix_results.json")
    
    # Вердикт
    if success_rate >= 75:
        print("\n🎉 API_REQUEST_TOOL ИСПРАВЛЕН!")
        print("Инструмент работает с реальными HTTP API запросами")
        return True
    elif success_rate >= 50:
        print("\n⚠️ API_REQUEST_TOOL ЧАСТИЧНО РАБОТАЕТ")
        print("Требуется дополнительная отладка")
        return False
    else:
        print("\n❌ API_REQUEST_TOOL НЕ РАБОТАЕТ")
        print("Требуется серьезная доработка")
        return False

if __name__ == "__main__":
    main() 