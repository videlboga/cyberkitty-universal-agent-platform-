#!/usr/bin/env python3
"""
🌐 ОТЛАДКА: web_client_tool
Проверяем правильные синхронные вызовы и параметры

ОСОБЕННОСТИ:
- Инструмент СИНХРОННЫЙ (НЕ async)
- Основные параметры: url (обязательный), check_type, timeout
- Поддерживает 3 типа проверок: status, ping, full
- Возвращает ToolResult со структурированными данными

ПЛАН ОТЛАДКИ:
1. Правильный синхронный вызов
2. Правильные параметры (url, check_type)
3. Проверка реальных веб-проверок
"""

import time
import json

# Импорт инструмента
try:
    from kittycore.tools.web_client_tool import WebClientTool
    IMPORT_OK = True
    print("✅ Импорт web_client_tool успешен")
except ImportError as e:
    print(f"❌ ИМПОРТ ОШИБКА: {e}")
    IMPORT_OK = False

def test_web_client_status():
    """Тест проверки HTTP статуса"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🌐 Тестирую web_client со status проверкой...")
    start_time = time.time()
    
    tool = WebClientTool()
    
    # ПРАВИЛЬНЫЙ вызов: обычный execute (НЕ await) + url + check_type
    result = tool.execute(
        url="https://httpbin.org/status/200",
        check_type="status",
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
                print(f"🔑 Ключи данных: {list(data.keys())[:10]}...")  # Первые 10 ключей
                print(f"🎯 URL: {data.get('url', 'НЕТ')}")
                print(f"🌐 Домен: {data.get('domain', 'НЕТ')}")
                print(f"📡 Статус код: {data.get('status_code', 'НЕТ')}")
                print(f"✅ Доступен: {data.get('available', 'НЕТ')}")
                print(f"⏱️ Время ответа: {data.get('response_time_ms', 'НЕТ')}мс")
        else:
            print(f"❌ Ошибка: {getattr(result, 'error', 'НЕИЗВЕСТНО')}")
    
    return result

def test_web_client_ping():
    """Тест ping проверки"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🌐 Тестирую web_client с ping проверкой...")
    
    tool = WebClientTool()
    
    # Тест ping
    result = tool.execute(
        url="https://httpbin.org",
        check_type="ping"
    )
    
    print(f"📊 Ping тест результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            print(f"🏓 Ping успех: {data.get('ping_success', 'НЕТ')}")
            print(f"🌐 Домен: {data.get('domain', 'НЕТ')}")
            print(f"⏱️ Время ping: {data.get('ping_time_seconds', 'НЕТ')}с")
    
    return result

def test_web_client_full():
    """Тест полной проверки"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🌐 Тестирую web_client с полной проверкой...")
    
    tool = WebClientTool()
    
    # Тест полной проверки
    result = tool.execute(
        url="https://httpbin.org",
        check_type="full",
        timeout=15
    )
    
    print(f"📊 Полная проверка результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            print(f"🌐 Общая доступность: {data.get('overall_available', 'НЕТ')}")
            print(f"📝 Сводка: {len(data.get('summary', []))} элементов")
            if 'summary' in data:
                for item in data['summary'][:3]:  # Первые 3 элемента
                    print(f"   {item}")
    
    return result

def test_web_client_action_api():
    """Тест через execute_action API"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🌐 Тестирую web_client через execute_action...")
    
    tool = WebClientTool()
    
    # Тест через action API
    result = tool.execute_action(
        action="status",
        url="https://httpbin.org/status/200"
    )
    
    print(f"📊 Action API результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success:
            data_size = len(str(result.data)) if hasattr(result, 'data') else 0
            print(f"📦 Размер: {data_size} байт")
    
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
        "web_client: успешно",
        "демо проверка",
        "заглушка клиента",
        "тестовая проверка"
    ]
    
    for pattern in fake_patterns:
        if pattern.lower() in data_str.lower():
            print(f"❌ {test_name}: Найден фейковый паттерн: {pattern}")
            return False
    
    # Проверка на реальные веб-признаки
    web_indicators = [
        "status_code", "response_time", "domain", "available", "ping_success", "url", "httpbin"
    ]
    
    has_web_data = any(indicator in data_str.lower() for indicator in web_indicators)
    
    if not has_web_data:
        print(f"❌ {test_name}: Нет признаков реальной веб-проверки")
        return False
    
    if data_size < 50:
        print(f"❌ {test_name}: Слишком маленький результат ({data_size} байт)")
        return False
    
    # Проверяем наличие базовых полей
    required_fields = ['url', 'check_type']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        print(f"❌ {test_name}: Отсутствуют обязательные поля: {missing_fields}")
        return False
    
    print(f"✅ {test_name}: ЧЕСТНЫЙ результат ({data_size} байт)")
    return True

def main():
    """Главная функция отладки"""
    print("🌐 ОТЛАДКА: web_client_tool")
    print("=" * 50)
    
    if not IMPORT_OK:
        print("❌ Невозможно продолжить - ошибка импорта")
        return
    
    results = {}
    
    # Тест 1: Status проверка
    print("\n" + "=" * 30)
    print("ТЕСТ 1: Status проверка")
    try:
        result1 = test_web_client_status()
        results["status_check"] = is_result_honest(result1, "Status проверка")
    except Exception as e:
        print(f"❌ ТЕСТ 1 ОШИБКА: {e}")
        results["status_check"] = False
    
    # Тест 2: Ping проверка
    print("\n" + "=" * 30)
    print("ТЕСТ 2: Ping проверка")
    try:
        result2 = test_web_client_ping()
        results["ping_check"] = is_result_honest(result2, "Ping проверка")
    except Exception as e:
        print(f"❌ ТЕСТ 2 ОШИБКА: {e}")
        results["ping_check"] = False
    
    # Тест 3: Полная проверка
    print("\n" + "=" * 30)
    print("ТЕСТ 3: Полная проверка")
    try:
        result3 = test_web_client_full()
        results["full_check"] = is_result_honest(result3, "Полная проверка")
    except Exception as e:
        print(f"❌ ТЕСТ 3 ОШИБКА: {e}")
        results["full_check"] = False
    
    # Тест 4: Action API
    print("\n" + "=" * 30)
    print("ТЕСТ 4: Action API")
    try:
        result4 = test_web_client_action_api()
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
    with open("web_client_fix_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "tool": "web_client_tool",
            "tests": results,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate
            },
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в web_client_fix_results.json")
    
    # Вердикт
    if success_rate >= 75:
        print("\n🎉 WEB_CLIENT_TOOL ИСПРАВЛЕН!")
        print("Инструмент работает с правильными синхронными вызовами и параметрами")
        return True
    elif success_rate >= 50:
        print("\n⚠️ WEB_CLIENT_TOOL ЧАСТИЧНО РАБОТАЕТ")
        print("Требуется дополнительная отладка")
        return False
    else:
        print("\n❌ WEB_CLIENT_TOOL НЕ РАБОТАЕТ")
        print("Требуется серьезная доработка")
        return False

if __name__ == "__main__":
    main() 