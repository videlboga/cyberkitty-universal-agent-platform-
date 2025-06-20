#!/usr/bin/env python3
"""
🔍 ВЕРИФИКАЦИЯ: Глубокая проверка реальности "успешных" инструментов

Проверяем:
1. Реальность данных (не заглушки)
2. Корректность размеров ответов
3. Логичность результатов
4. Отсутствие hardcoded значений
"""

import time
import json
import tempfile
import os
import csv
from PIL import Image

# Импорты успешных инструментов
successful_tools = {}

try:
    from kittycore.tools.enhanced_web_search_tool import EnhancedWebSearchTool
    successful_tools['web_search'] = EnhancedWebSearchTool()
except ImportError as e:
    print(f"❌ web_search: {e}")

try:
    from kittycore.tools.enhanced_web_scraping_tool import EnhancedWebScrapingTool
    successful_tools['web_scraping'] = EnhancedWebScrapingTool()
except ImportError as e:
    print(f"❌ web_scraping: {e}")

try:
    from kittycore.tools.api_request_tool import ApiRequestTool
    successful_tools['api_request'] = ApiRequestTool()
except ImportError as e:
    print(f"❌ api_request: {e}")

try:
    from kittycore.tools.super_system_tool import SuperSystemTool
    successful_tools['super_system'] = SuperSystemTool()
except ImportError as e:
    print(f"❌ super_system: {e}")

try:
    from kittycore.tools.security_tool import SecurityTool
    successful_tools['security'] = SecurityTool()
except ImportError as e:
    print(f"❌ security: {e}")

def verify_web_search_reality():
    """ГЛУБОКАЯ ПРОВЕРКА: web_search реально ищет в интернете"""
    if 'web_search' not in successful_tools:
        return "IMPORT_ERROR"
    
    print("\n🔍 ВЕРИФИКАЦИЯ: enhanced_web_search_tool")
    tool = successful_tools['web_search']
    
    # Тест 1: Поиск текущих событий (должен дать свежие результаты)
    current_query = "Python 3.13 new features"
    result1 = tool.execute(query=current_query, limit=3)
    
    if not (hasattr(result1, 'success') and result1.success):
        return "❌ ПРОВАЛ: Поиск не работает"
    
    # Тест 2: Поиск уникального запроса (другие результаты)
    unique_query = "Rust programming language 2024"
    result2 = tool.execute(query=unique_query, limit=3)
    
    if not (hasattr(result2, 'success') and result2.success):
        return "❌ ПРОВАЛ: Второй поиск не работает"
    
    # Анализ результатов
    data1_str = str(result1.data)
    data2_str = str(result2.data)
    
    # Проверка 1: Разные запросы = разные результаты
    if data1_str == data2_str:
        return "❌ ФЕЙК: Одинаковые результаты для разных запросов"
    
    # Проверка 2: Наличие реальных URL
    url_indicators = ['http', 'www', '.com', '.org', '.net']
    has_urls1 = any(indicator in data1_str.lower() for indicator in url_indicators)
    has_urls2 = any(indicator in data2_str.lower() for indicator in url_indicators)
    
    if not (has_urls1 and has_urls2):
        return "❌ ФЕЙК: Нет настоящих URL в результатах"
    
    # Проверка 3: Различные домены/источники
    domains1 = set()
    domains2 = set()
    for indicator in ['.com', '.org', '.net', '.io', '.dev']:
        if indicator in data1_str:
            domains1.add(indicator)
        if indicator in data2_str:
            domains2.add(indicator)
    
    # Проверка 4: Размер данных адекватен (реальные поисковые результаты)
    if len(data1_str) < 200 or len(data2_str) < 200:
        return "❌ ФЕЙК: Слишком маленькие результаты поиска"
    
    # Проверка 5: Нет hardcoded заглушек
    fake_patterns = ['демо результат', 'тестовый поиск', 'заглушка', 'example.com']
    for pattern in fake_patterns:
        if pattern.lower() in data1_str.lower() or pattern.lower() in data2_str.lower():
            return f"❌ ФЕЙК: Найдена заглушка: {pattern}"
    
    return f"✅ РЕАЛЬНЫЙ: {len(data1_str)} + {len(data2_str)} байт, разные домены: {domains1 | domains2}"

def verify_web_scraping_reality():
    """ГЛУБОКАЯ ПРОВЕРКА: web_scraping реально скрапит сайты"""
    if 'web_scraping' not in successful_tools:
        return "IMPORT_ERROR"
    
    print("\n🕷️ ВЕРИФИКАЦИЯ: enhanced_web_scraping_tool")
    tool = successful_tools['web_scraping']
    
    # Тест: Скрапинг простого статичного сайта
    test_url = "https://httpbin.org/html"  # Простой HTML тестовый сайт
    result = tool.execute(url=test_url, extract_type="text")
    
    if not (hasattr(result, 'success') and result.success):
        return "❌ ПРОВАЛ: Скрапинг не работает"
    
    data_str = str(result.data)
    
    # Проверка 1: Содержит реальный HTML контент
    html_indicators = ['<html>', '<body>', '<h1>', '<p>', 'Herman Melville']
    found_html = sum(1 for indicator in html_indicators if indicator.lower() in data_str.lower())
    
    if found_html < 2:
        return "❌ ФЕЙК: Нет признаков реального HTML контента"
    
    # Проверка 2: Размер адекватен скрапингу
    if len(data_str) < 100:
        return "❌ ФЕЙК: Слишком маленький результат скрапинга"
    
    # Проверка 3: Нет заглушек
    fake_patterns = ['демо скрапинг', 'тестовая страница', 'заглушка контента']
    for pattern in fake_patterns:
        if pattern.lower() in data_str.lower():
            return f"❌ ФЕЙК: Найдена заглушка: {pattern}"
    
    return f"✅ РЕАЛЬНЫЙ: {len(data_str)} байт, HTML элементов: {found_html}"

def verify_api_request_reality():
    """ГЛУБОКАЯ ПРОВЕРКА: api_request реально делает HTTP запросы"""
    if 'api_request' not in successful_tools:
        return "IMPORT_ERROR"
    
    print("\n🌐 ВЕРИФИКАЦИЯ: api_request_tool")
    tool = successful_tools['api_request']
    
    # Тест 1: GET к API с временными данными
    result1 = tool.execute(
        url="https://httpbin.org/uuid",
        method="GET",
        timeout=10
    )
    
    if not (hasattr(result1, 'success') and result1.success):
        return "❌ ПРОВАЛ: GET запрос не работает"
    
    # Тест 2: Второй GET (должен быть другой UUID)
    result2 = tool.execute(
        url="https://httpbin.org/uuid", 
        method="GET",
        timeout=10
    )
    
    if not (hasattr(result2, 'success') and result2.success):
        return "❌ ПРОВАЛ: Второй GET запрос не работает"
    
    data1_str = str(result1.data)
    data2_str = str(result2.data)
    
    # Проверка 1: Разные UUID (признак реальных запросов)
    if data1_str == data2_str:
        return "❌ ФЕЙК: Одинаковые ответы для разных запросов"
    
    # Проверка 2: Формат UUID
    uuid_indicators = ['-', 'uuid', 'status', '200']
    found_uuid = sum(1 for indicator in uuid_indicators if indicator in data1_str.lower())
    
    if found_uuid < 2:
        return "❌ ФЕЙК: Нет признаков реального API ответа"
    
    return f"✅ РЕАЛЬНЫЙ: {len(data1_str)} + {len(data2_str)} байт, разные UUID"

def verify_security_tool_reality():
    """ГЛУБОКАЯ ПРОВЕРКА: security_tool реально анализирует безопасность"""
    if 'security' not in successful_tools:
        return "IMPORT_ERROR"
    
    print("\n🔒 ВЕРИФИКАЦИЯ: security_tool")
    tool = successful_tools['security']
    
    # Тест: Анализ разных паролей (должны быть разные оценки)
    passwords = ["123", "MyStrongPassword123!", "password"]
    results = []
    
    for pwd in passwords:
        result = tool.execute("analyze_password", password=pwd)
        if hasattr(result, 'success') and result.success:
            results.append((pwd, str(result.data)))
        else:
            return f"❌ ПРОВАЛ: Анализ пароля '{pwd}' не работает"
    
    # Проверка 1: Разные пароли = разные результаты
    if len(set(data for _, data in results)) < 2:
        return "❌ ФЕЙК: Одинаковые результаты для разных паролей"
    
    # Проверка 2: Логичность оценок (слабый vs сильный пароль)
    weak_result = results[0][1]  # "123"
    strong_result = results[1][1]  # "MyStrongPassword123!"
    
    # Сильный пароль должен иметь больше данных/лучшую оценку
    if len(strong_result) <= len(weak_result):
        return "❌ ФЕЙК: Сильный пароль не лучше слабого"
    
    # Проверка 3: Присутствие реальной терминологии безопасности
    security_terms = ['strength', 'weak', 'strong', 'score', 'entropy', 'password']
    found_terms = sum(1 for term in security_terms 
                     if any(term.lower() in data.lower() for _, data in results))
    
    if found_terms < 3:
        return "❌ ФЕЙК: Нет терминологии безопасности"
    
    return f"✅ РЕАЛЬНЫЙ: {len(results)} паролей, разные оценки, {found_terms} терминов"

def verify_super_system_reality():
    """ГЛУБОКАЯ ПРОВЕРКА: super_system_tool реально получает системную информацию"""
    if 'super_system' not in successful_tools:
        return "IMPORT_ERROR"
    
    print("\n🖥️ ВЕРИФИКАЦИЯ: super_system_tool")
    tool = successful_tools['super_system']
    
    # Тест 1: Системная информация
    result1 = tool.execute(action="get_system_info")
    if not (hasattr(result1, 'success') and result1.success):
        return "❌ ПРОВАЛ: Системная информация не работает"
    
    # Тест 2: Использование ресурсов (должно меняться между вызовами)
    time.sleep(0.1)  # Небольшая пауза
    result2 = tool.execute(action="get_resource_usage")
    if not (hasattr(result2, 'success') and result2.success):
        return "❌ ПРОВАЛ: Использование ресурсов не работает"
    
    data1_str = str(result1.data)
    data2_str = str(result2.data)
    
    # Проверка 1: Реальная системная информация
    system_indicators = ['cpu', 'memory', 'disk', 'linux', 'manjaro', 'python']
    found_system = sum(1 for indicator in system_indicators if indicator.lower() in data1_str.lower())
    
    if found_system < 3:
        return "❌ ФЕЙК: Нет признаков реальной системной информации"
    
    # Проверка 2: Размеры адекватны системным данным
    if len(data1_str) < 200 or len(data2_str) < 200:
        return "❌ ФЕЙК: Слишком маленькие системные данные"
    
    return f"✅ РЕАЛЬНЫЙ: {len(data1_str)} + {len(data2_str)} байт, {found_system} системных терминов"

def main():
    print("🔍 ГЛУБОКАЯ ВЕРИФИКАЦИЯ УСПЕШНЫХ ИНСТРУМЕНТОВ")
    print("=" * 60)
    
    verifications = {
        "WebSearch": verify_web_search_reality,
        "WebScraping": verify_web_scraping_reality,
        "ApiRequest": verify_api_request_reality,
        "SecurityTool": verify_security_tool_reality,
        "SuperSystem": verify_super_system_reality
    }
    
    results = {}
    
    for tool_name, verify_func in verifications.items():
        try:
            start_time = time.time()
            result = verify_func()
            end_time = time.time()
            
            test_time = (end_time - start_time) * 1000
            
            # Определяем статус
            is_real = result.startswith("✅ РЕАЛЬНЫЙ")
            status = "✅ РЕАЛЬНЫЙ" if is_real else "❌ ФЕЙКОВЫЙ/ОШИБКА"
            
            print(f"{tool_name}: {result} ({test_time:.1f}мс)")
            results[tool_name] = is_real
            
        except Exception as e:
            print(f"{tool_name}: ❌ ИСКЛЮЧЕНИЕ: {e}")
            results[tool_name] = False
    
    # Итоги верификации
    print("\n" + "=" * 60)
    print("📊 ИТОГИ ГЛУБОКОЙ ВЕРИФИКАЦИИ:")
    
    total_verified = len(results)
    real_tools = sum(1 for is_real in results.values() if is_real)
    reality_rate = (real_tools / total_verified * 100) if total_verified > 0 else 0
    
    print(f"Всего проверено: {total_verified}")
    print(f"Реально работающих: {real_tools}")
    print(f"Процент реальности: {reality_rate:.1f}%")
    
    print("\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    for tool_name, is_real in results.items():
        status = "✅ РЕАЛЬНЫЙ" if is_real else "❌ ФЕЙКОВЫЙ"
        print(f"  {tool_name}: {status}")
    
    # Рекомендации
    fake_tools = [name for name, is_real in results.items() if not is_real]
    if fake_tools:
        print(f"\n🔧 ТРЕБУЮТ ИСПРАВЛЕНИЯ: {', '.join(fake_tools)}")
    else:
        print(f"\n🎉 ВСЕ ПРОВЕРЕННЫЕ ИНСТРУМЕНТЫ РЕАЛЬНО РАБОТАЮТ!")

if __name__ == "__main__":
    main() 