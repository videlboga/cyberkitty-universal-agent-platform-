#!/usr/bin/env python3
"""
🔒 ОТЛАДКА: security_tool
"""

import asyncio
import time
import json

try:
    from kittycore.tools.security_tool import SecurityTool
    IMPORT_OK = True
    print("✅ Импорт security_tool успешен")
except ImportError as e:
    print(f"❌ ИМПОРТ ОШИБКА: {e}")
    IMPORT_OK = False

async def test_password_analysis():
    """Тест анализа пароля"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🔐 Тестирую анализ пароля...")
    tool = SecurityTool()
    
    # Тестируем анализ слабого пароля
    result = await tool.execute("analyze_password", password="123456")
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            if isinstance(data, dict):
                strength = data.get('strength', 'UNKNOWN')
                score = data.get('score', 0)
                print(f"🔐 Пароль '123456': сила={strength}, оценка={score}")
    
    return result

async def test_secure_password_generation():
    """Тест генерации безопасного пароля"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🔑 Тестирую генерацию безопасного пароля...")
    tool = SecurityTool()
    
    # Генерируем безопасный пароль
    result = await tool.execute("generate_secure_password", length=12)
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            if isinstance(data, dict):
                password = data.get('password', 'UNKNOWN')
                strength = data.get('strength', 'UNKNOWN')
                print(f"🔑 Сгенерированный пароль: длина={len(password)}, сила={strength}")
    
    return result

async def test_code_vulnerability_scan():
    """Тест сканирования уязвимостей в коде"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🔍 Тестирую сканирование уязвимостей кода...")
    tool = SecurityTool()
    
    # Тестовый код с потенциальными уязвимостями
    vulnerable_code = '''
def login(username, password):
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)
    return cursor.fetchone()

def display_content(user_input):
    document.innerHTML = "<div>" + user_input + "</div>"
'''
    
    result = await tool.execute("scan_code_vulnerabilities", code=vulnerable_code)
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            if isinstance(data, dict):
                vulnerabilities = data.get('vulnerabilities', [])
                security_score = data.get('security_score', 0)
                print(f"🔍 Найдено уязвимостей: {len(vulnerabilities)}, оценка безопасности: {security_score}")
    
    return result

async def test_hash_analysis():
    """Тест анализа хеша"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🔐 Тестирую анализ хеша...")
    tool = SecurityTool()
    
    # Тестируем MD5 хеш
    md5_hash = "5d41402abc4b2a76b9719d911017c592"  # хеш от "hello"
    result = await tool.execute("analyze_hash", hash_value=md5_hash)
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            if isinstance(data, dict):
                algorithms = data.get('possible_algorithms', [])
                confidence = data.get('confidence', 0)
                print(f"🔐 Хеш анализ: алгоритмы={algorithms}, уверенность={confidence}")
    
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
        "security_tool: успешно",
        "демо сканирование",
        "заглушка пароля"
    ]
    
    for pattern in fake_patterns:
        if pattern.lower() in data_str.lower():
            print(f"❌ {test_name}: Найден фейковый паттерн: {pattern}")
            return False
    
    # Проверка на реальные признаки анализа безопасности
    security_indicators = [
        "password", "strength", "vulnerability", "hash", "security", "score", 
        "algorithm", "weak", "strong", "sql", "xss", "injection", "confidence"
    ]
    
    has_security_data = any(indicator.lower() in data_str.lower() for indicator in security_indicators)
    
    if not has_security_data:
        print(f"❌ {test_name}: Нет признаков реального анализа безопасности")
        return False
    
    if data_size < 50:
        print(f"❌ {test_name}: Слишком маленький результат ({data_size} байт)")
        return False
    
    print(f"✅ {test_name}: ЧЕСТНЫЙ результат ({data_size} байт)")
    return True

async def main():
    print("🔒 ОТЛАДКА: security_tool")
    
    if not IMPORT_OK:
        return
    
    results = {}
    
    # Тесты (все асинхронные)
    tests = [
        ("password_analysis", test_password_analysis),
        ("secure_password_generation", test_secure_password_generation),
        ("code_vulnerability_scan", test_code_vulnerability_scan),
        ("hash_analysis", test_hash_analysis)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*30}")
        print(f"ТЕСТ: {test_name}")
        try:
            result = await test_func()
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
    asyncio.run(main()) 