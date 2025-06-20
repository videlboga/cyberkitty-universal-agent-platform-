#!/usr/bin/env python3
"""
💻 ОТЛАДКА: code_execution_tool
Проверяем реальное выполнение Python и shell кода

ОСОБЕННОСТИ:
- Инструмент СИНХРОННЫЙ с АСИНХРОННЫМИ внутренними методами
- Основные параметры: action (обязательный), code, language, timeout
- Действия: execute_python, execute_shell, validate_python, validate_shell
- Безопасность: sandbox, таймауты, блокировка опасных операций

ПЛАН ОТЛАДКИ:
1. Правильный синхронный вызов execute()
2. Правильные параметры (action + code)
3. Проверка реального выполнения кода
4. Тест безопасности sandbox
"""

import time
import json

# Импорт инструмента
try:
    from kittycore.tools.code_execution_tools import CodeExecutionTool
    IMPORT_OK = True
    print("✅ Импорт code_execution_tool успешен")
except ImportError as e:
    print(f"❌ ИМПОРТ ОШИБКА: {e}")
    IMPORT_OK = False

def test_python_execution():
    """Тест выполнения Python кода"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🐍 Тестирую Python выполнение...")
    tool = CodeExecutionTool()
    
    python_code = """
import math
result = math.sqrt(16)
print(f"Результат: {result}")
numbers = [1, 2, 3]
print(f"Сумма: {sum(numbers)}")
"""
    
    result = tool.execute(
        action="execute_python",
        code=python_code,
        timeout=10
    )
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            print(f"📦 Размер: {len(str(data))} байт")
            print(f"🔑 Ключи: {list(data.keys()) if isinstance(data, dict) else 'не dict'}")
    
    return result

def test_shell_execution():
    """Тест выполнения shell команд"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🐚 Тестирую code_execution с shell командами...")
    
    tool = CodeExecutionTool()
    
    # Безопасная shell команда
    shell_code = """
echo "Привет от shell!"
echo "Текущая дата: $(date)"
echo "Файлы в /tmp:"
ls -la /tmp | head -5
echo "Процессы Python:"
ps aux | grep python | head -3
"""
    
    result = tool.execute(
        action="execute_shell",
        code=shell_code,
        timeout=10
    )
    
    print(f"📊 Shell результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            output = data.get('output', '') if isinstance(data, dict) else str(data)
            print(f"📺 Shell вывод: {len(output)} символов")
            
            # Проверяем ожидаемые результаты
            expected_shell = ["Привет от shell", "Текущая дата", "Файлы в /tmp"]
            for expected in expected_shell:
                if expected in output:
                    print(f"✅ Найден ожидаемый shell результат: {expected}")
                else:
                    print(f"❌ НЕ найден shell результат: {expected}")
        else:
            print(f"❌ Shell ошибка: {getattr(result, 'error', 'НЕИЗВЕСТНО')}")
    
    return result

def test_validation():
    """Тест валидации кода"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🔍 Тестирую валидацию кода...")
    
    tool = CodeExecutionTool()
    
    # Тест валидации безопасного кода
    safe_code = "print('Hello World')\nresult = 2 + 2"
    
    result = tool.execute(
        action="validate_python",
        code=safe_code
    )
    
    print(f"📊 Валидация безопасного кода: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        
        # Тест валидации опасного кода
        dangerous_code = "import os\nos.system('rm -rf /')"
        
        dangerous_result = tool.execute(
            action="validate_python",
            code=dangerous_code
        )
        
        print(f"📊 Валидация опасного кода: {type(dangerous_result)}")
        if hasattr(dangerous_result, 'success'):
            print(f"🚫 Dangerous Success (должно быть False): {dangerous_result.success}")
            if not dangerous_result.success:
                print("✅ Система безопасности работает - опасный код заблокирован")
    
    return result

def test_list_actions():
    """Тест получения информации о возможностях инструмента"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📋 Тестирую информационные действия...")
    
    tool = CodeExecutionTool()
    
    # Тест списка библиотек
    result1 = tool.execute(action="list_libraries")
    print(f"📊 Список библиотек: {type(result1)}")
    if hasattr(result1, 'success') and result1.success:
        data = result1.data
        if isinstance(data, dict) and 'libraries' in data:
            libs = data['libraries']
            print(f"📚 Доступных библиотек: {len(libs)}")
            print(f"   Первые 5: {list(libs)[:5]}")
    
    # Тест лимитов выполнения
    result2 = tool.execute(action="get_execution_limits")
    print(f"📊 Лимиты выполнения: {type(result2)}")
    if hasattr(result2, 'success') and result2.success:
        data = result2.data
        if isinstance(data, dict):
            print(f"⏱️ Python timeout: {data.get('python_timeout', 'НЕТ')}")
            print(f"⏱️ Shell timeout: {data.get('shell_timeout', 'НЕТ')}")
            print(f"📦 Max output: {data.get('max_output_size', 'НЕТ')}")
    
    return result1

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
        "code_execution: успешно",
        "демо выполнение",
        "заглушка кода",
        "тестовое выполнение"
    ]
    
    for pattern in fake_patterns:
        if pattern.lower() in data_str.lower():
            print(f"❌ {test_name}: Найден фейковый паттерн: {pattern}")
            return False
    
    # Проверка на реальные признаки выполнения кода
    code_indicators = [
        "output", "stdout", "stderr", "execution_time", "return_code", 
        "квадратный корень", "сумма квадратов", "привет от shell", "текущая дата"
    ]
    
    has_code_data = any(indicator.lower() in data_str.lower() for indicator in code_indicators)
    
    if not has_code_data:
        print(f"❌ {test_name}: Нет признаков реального выполнения кода")
        return False
    
    if data_size < 50:
        print(f"❌ {test_name}: Слишком маленький результат ({data_size} байт)")
        return False
    
    # Специальные проверки для разных типов
    if "python" in test_name.lower():
        # Для Python проверяем математические результаты
        python_results = ["4.0", "55", "[1, 4, 9, 16, 25]"]
        has_python_result = any(result in data_str for result in python_results)
        if not has_python_result:
            print(f"❌ {test_name}: Нет математических результатов Python")
            return False
    
    if "shell" in test_name.lower():
        # Для shell проверяем системную информацию
        shell_results = ["привет от shell", "текущая дата", "файлы в /tmp"]
        has_shell_result = any(result.lower() in data_str.lower() for result in shell_results)
        if not has_shell_result:
            print(f"❌ {test_name}: Нет системной информации shell")
            return False
    
    print(f"✅ {test_name}: ЧЕСТНЫЙ результат ({data_size} байт)")
    return True

def main():
    """Главная функция отладки"""
    print("💻 ОТЛАДКА: code_execution_tool")
    print("=" * 50)
    
    if not IMPORT_OK:
        print("❌ Невозможно продолжить - ошибка импорта")
        return
    
    results = {}
    
    # Тест 1: Python код
    print("\n" + "=" * 30)
    print("ТЕСТ 1: Python выполнение")
    try:
        result1 = test_python_execution()
        results["python_execution"] = is_result_honest(result1, "Python выполнение")
    except Exception as e:
        print(f"❌ ТЕСТ 1 ОШИБКА: {e}")
        results["python_execution"] = False
    
    # Тест 2: Shell команды
    print("\n" + "=" * 30)
    print("ТЕСТ 2: Shell выполнение")
    try:
        result2 = test_shell_execution()
        results["shell_execution"] = is_result_honest(result2, "Shell выполнение")
    except Exception as e:
        print(f"❌ ТЕСТ 2 ОШИБКА: {e}")
        results["shell_execution"] = False
    
    # Тест 3: Валидация
    print("\n" + "=" * 30)
    print("ТЕСТ 3: Валидация кода")
    try:
        result3 = test_validation()
        results["code_validation"] = is_result_honest(result3, "Валидация кода")
    except Exception as e:
        print(f"❌ ТЕСТ 3 ОШИБКА: {e}")
        results["code_validation"] = False
    
    # Тест 4: Информационные действия
    print("\n" + "=" * 30)
    print("ТЕСТ 4: Информационные действия")
    try:
        result4 = test_list_actions()
        results["info_actions"] = is_result_honest(result4, "Информационные действия")
    except Exception as e:
        print(f"❌ ТЕСТ 4 ОШИБКА: {e}")
        results["info_actions"] = False
    
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
    with open("code_execution_fix_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "tool": "code_execution_tool",
            "tests": results,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate
            },
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в code_execution_fix_results.json")
    
    # Вердикт
    if success_rate >= 75:
        print("\n🎉 CODE_EXECUTION_TOOL ИСПРАВЛЕН!")
        print("Инструмент работает с реальным выполнением кода")
        return True
    elif success_rate >= 50:
        print("\n⚠️ CODE_EXECUTION_TOOL ЧАСТИЧНО РАБОТАЕТ")
        print("Требуется дополнительная отладка")
        return False
    else:
        print("\n❌ CODE_EXECUTION_TOOL НЕ РАБОТАЕТ")
        print("Требуется серьезная доработка")
        return False

if __name__ == "__main__":
    main() 