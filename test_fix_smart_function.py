#!/usr/bin/env python3
"""
🧠 ОТЛАДКА: smart_function_tool
Проверяем правильные async вызовы и параметры

ОСОБЕННОСТИ:
- Инструмент АСИНХРОННЫЙ (требует await)
- Основные параметры: action (обязательный), + доп. параметры по действию
- Поддерживает много действий: create_function, execute_function, list_functions, и др.
- По умолчанию выполняет list_functions

ПЛАН ОТЛАДКИ:
1. Правильный async вызов
2. Правильные параметры (action + доп. параметры)
3. Проверка реальной работы с функциями
"""

import asyncio
import time
import json

# Импорт инструмента
try:
    from kittycore.tools.smart_function_tool import SmartFunctionTool
    IMPORT_OK = True
    print("✅ Импорт smart_function_tool успешен")
except ImportError as e:
    print(f"❌ ИМПОРТ ОШИБКА: {e}")
    IMPORT_OK = False

async def test_smart_function_list():
    """Тест получения списка функций"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🧠 Тестирую smart_function с list_functions...")
    start_time = time.time()
    
    tool = SmartFunctionTool()
    
    # ПРАВИЛЬНЫЙ вызов: await + action
    result = await tool.execute(action="list_functions")
    
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
                print(f"📊 Всего функций: {data.get('total_functions', 'НЕТ')}")
                if 'functions' in data:
                    functions = data['functions']
                    print(f"📝 Список функций: {list(functions.keys()) if functions else 'пусто'}")
        else:
            print(f"❌ Ошибка: {getattr(result, 'error', 'НЕИЗВЕСТНО')}")
    
    return result

async def test_smart_function_create():
    """Тест создания функции"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🧠 Тестирую smart_function с create_function...")
    
    tool = SmartFunctionTool()
    
    # Простая функция для создания
    function_code = """
def hello_world(name="World"):
    '''Приветствует пользователя'''
    return f"Hello, {name}!"
"""
    
    # Тест создания функции
    result = await tool.execute(
        action="create_function",
        function_code=function_code,
        auto_import=True
    )
    
    print(f"📊 Create function результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            print(f"🎯 Имя функции: {data.get('function_name', 'НЕТ')}")
            print(f"📋 Зарегистрирована: {data.get('registered', 'НЕТ')}")
            if 'metadata' in data:
                metadata = data['metadata']
                print(f"📝 Сигнатура: {metadata.get('signature', 'НЕТ')}")
                print(f"⚡ Сложность: {metadata.get('complexity', 'НЕТ')}")
    
    return result

async def test_smart_function_execute():
    """Тест выполнения функции"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🧠 Тестирую smart_function с execute_function...")
    
    tool = SmartFunctionTool()
    
    # Сначала создаем функцию
    function_code = """
def add_numbers(a, b):
    '''Складывает два числа'''
    return a + b
"""
    
    create_result = await tool.execute(
        action="create_function",
        function_code=function_code
    )
    
    if not create_result.success:
        print(f"❌ Не удалось создать функцию: {create_result.error}")
        return create_result
    
    # Теперь выполняем функцию
    result = await tool.execute(
        action="execute_function",
        function_name="add_numbers",
        args=[5, 3]
    )
    
    print(f"📊 Execute function результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            print(f"🎯 Результат: {data.get('result', 'НЕТ')}")
            print(f"⏱️ Время выполнения: {data.get('execution_time', 'НЕТ')}с")
            print(f"📝 Функция: {data.get('function_name', 'НЕТ')}")
    
    return result

async def test_smart_function_validate():
    """Тест валидации кода"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🧠 Тестирую smart_function с validate_code...")
    
    tool = SmartFunctionTool()
    
    # Тест валидации
    test_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
"""
    
    result = await tool.execute(
        action="validate_code",
        code=test_code
    )
    
    print(f"📊 Validate code результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            print(f"✅ Валидный: {data.get('valid', 'НЕТ')}")
            print(f"⚠️ Предупреждений: {len(data.get('warnings', []))}")
            print(f"📊 AST узлов: {data.get('ast_nodes', 'НЕТ')}")
    
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
        "smart_function: успешно",
        "демо функция",
        "заглушка функции",
        "тестовая функция"
    ]
    
    for pattern in fake_patterns:
        if pattern.lower() in data_str.lower():
            print(f"❌ {test_name}: Найден фейковый паттерн: {pattern}")
            return False
    
    # Проверка на реальные признаки работы с функциями
    function_indicators = [
        "function", "result", "metadata", "signature", "execution_time", "valid", "ast_nodes"
    ]
    
    has_function_data = any(indicator in data_str.lower() for indicator in function_indicators)
    
    if not has_function_data:
        print(f"❌ {test_name}: Нет признаков реальной работы с функциями")
        return False
    
    if data_size < 30:
        print(f"❌ {test_name}: Слишком маленький результат ({data_size} байт)")
        return False
    
    print(f"✅ {test_name}: ЧЕСТНЫЙ результат ({data_size} байт)")
    return True

async def main():
    """Главная функция отладки"""
    print("🧠 ОТЛАДКА: smart_function_tool")
    print("=" * 50)
    
    if not IMPORT_OK:
        print("❌ Невозможно продолжить - ошибка импорта")
        return
    
    results = {}
    
    # Тест 1: Список функций
    print("\n" + "=" * 30)
    print("ТЕСТ 1: Список функций")
    try:
        result1 = await test_smart_function_list()
        results["list_functions"] = is_result_honest(result1, "Список функций")
    except Exception as e:
        print(f"❌ ТЕСТ 1 ОШИБКА: {e}")
        results["list_functions"] = False
    
    # Тест 2: Создание функции
    print("\n" + "=" * 30)
    print("ТЕСТ 2: Создание функции")
    try:
        result2 = await test_smart_function_create()
        results["create_function"] = is_result_honest(result2, "Создание функции")
    except Exception as e:
        print(f"❌ ТЕСТ 2 ОШИБКА: {e}")
        results["create_function"] = False
    
    # Тест 3: Выполнение функции
    print("\n" + "=" * 30)
    print("ТЕСТ 3: Выполнение функции")
    try:
        result3 = await test_smart_function_execute()
        results["execute_function"] = is_result_honest(result3, "Выполнение функции")
    except Exception as e:
        print(f"❌ ТЕСТ 3 ОШИБКА: {e}")
        results["execute_function"] = False
    
    # Тест 4: Валидация кода
    print("\n" + "=" * 30)
    print("ТЕСТ 4: Валидация кода")
    try:
        result4 = await test_smart_function_validate()
        results["validate_code"] = is_result_honest(result4, "Валидация кода")
    except Exception as e:
        print(f"❌ ТЕСТ 4 ОШИБКА: {e}")
        results["validate_code"] = False
    
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
    with open("smart_function_fix_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "tool": "smart_function_tool",
            "tests": results,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate
            },
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в smart_function_fix_results.json")
    
    # Вердикт
    if success_rate >= 75:
        print("\n🎉 SMART_FUNCTION_TOOL ИСПРАВЛЕН!")
        print("Инструмент работает с правильными async вызовами и параметрами")
        return True
    elif success_rate >= 50:
        print("\n⚠️ SMART_FUNCTION_TOOL ЧАСТИЧНО РАБОТАЕТ")
        print("Требуется дополнительная отладка")
        return False
    else:
        print("\n❌ SMART_FUNCTION_TOOL НЕ РАБОТАЕТ")
        print("Требуется серьезная доработка")
        return False

if __name__ == "__main__":
    asyncio.run(main()) 