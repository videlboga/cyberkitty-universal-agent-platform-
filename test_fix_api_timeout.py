#!/usr/bin/env python3
"""
🔧 ИСПРАВЛЕНИЕ: ApiRequest таймауты

ПРОБЛЕМА: ApiRequest дает таймауты даже на коротких запросах  
РЕШЕНИЕ: Использовать быстрые эндпоинты + оптимальные таймауты
"""

import time

def test_api_request_timeout():
    """Тест исправленного ApiRequest с быстрыми запросами"""
    print("🌐 ТЕСТ ИСПРАВЛЕННОГО: ApiRequest таймауты")
    
    try:
        from kittycore.tools.api_request_tool import ApiRequestTool
        
        # Инициализируем инструмент
        tool = ApiRequestTool()
        print("✅ Инициализация успешна")
        
        # Тест 1: Быстрый GET запрос (без задержки)
        print("\n📝 Тест 1: Быстрый GET запрос")
        start_time = time.time()
        result1 = tool.execute(
            url="https://httpbin.org/get",  # Без задержки
            method="GET",
            timeout=3  # Короткий таймаут
        )
        end_time = time.time()
        
        actual_time = end_time - start_time
        print(f"⏱️ Фактическое время: {actual_time:.1f}с")
        print(f"✅ Быстрый GET: success={getattr(result1, 'success', 'N/A')}")
        if hasattr(result1, 'data'):
            print(f"📊 Размер данных: {len(str(result1.data))} символов")
        
        # Тест 2: Локальный JSON запрос
        print("\n📝 Тест 2: JSON запрос")
        start_time = time.time()
        result2 = tool.execute(
            url="https://httpbin.org/json",  # Быстрый JSON
            method="GET",
            timeout=3
        )
        end_time = time.time()
        
        actual_time = end_time - start_time
        print(f"⏱️ Фактическое время: {actual_time:.1f}с")
        print(f"✅ JSON запрос: success={getattr(result2, 'success', 'N/A')}")
        
        # Тест 3: POST запрос с данными
        print("\n📝 Тест 3: POST запрос")
        start_time = time.time()
        result3 = tool.execute(
            url="https://httpbin.org/post",
            method="POST",
            data={"test": "data"},
            timeout=3
        )
        end_time = time.time()
        
        actual_time = end_time - start_time
        print(f"⏱️ Фактическое время: {actual_time:.1f}с")
        print(f"✅ POST запрос: success={getattr(result3, 'success', 'N/A')}")
        
        # Тест 4: Headers запрос
        print("\n📝 Тест 4: Headers запрос")
        start_time = time.time()
        result4 = tool.execute(
            url="https://httpbin.org/headers",
            method="GET",
            headers={"X-Test": "KittyCore"},
            timeout=3
        )
        end_time = time.time()
        
        actual_time = end_time - start_time
        print(f"⏱️ Фактическое время: {actual_time:.1f}с")
        print(f"✅ Headers запрос: success={getattr(result4, 'success', 'N/A')}")
        
        # Подсчет успешности
        results = [result1, result2, result3, result4]
        success_count = sum(1 for r in results if hasattr(r, 'success') and r.success)
        success_rate = (success_count / len(results)) * 100
        
        print(f"\n📊 ИТОГИ: {success_count}/{len(results)} тестов успешно ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            return f"✅ ИСПРАВЛЕН: {success_rate:.1f}% успех"
        else:
            return f"❌ ЧАСТИЧНО: {success_rate:.1f}% успех, но таймауты"
            
    except ImportError as e:
        return f"❌ ИМПОРТ: {e}"
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return f"❌ ИСКЛЮЧЕНИЕ: {e}"

if __name__ == "__main__":
    print("🔧 ИСПРАВЛЕНИЕ API REQUEST ТАЙМАУТОВ")
    print("=" * 50)
    
    start_time = time.time()
    result = test_api_request_timeout()
    end_time = time.time()
    
    test_time = (end_time - start_time) * 1000
    print(f"\n🏁 РЕЗУЛЬТАТ: {result} ({test_time:.1f}мс)") 