#!/usr/bin/env python3
"""
⏰ ЭТАП 4: ИСПРАВЛЕНИЕ ТАЙМАУТОВ
Тестирование инструментов с проблемами таймаутов

ПЛАН ЭТАПА 4:
- ai_integration_tool: исправить проблемы таймаутов (16+ минут → 30-60с)
- Тестировать разные модели/провайдеры
- Оценить прогресс: +1 инструмент готовый (1 день)

ПРИНЦИПЫ:
✅ РЕАЛЬНЫЕ AI API запросы
❌ НЕТ бесконечных таймаутов
✅ Быстрые лёгкие модели для тестов
✅ Fallback режимы при недоступности API
"""

import time
import json
import asyncio
import traceback
from pathlib import Path

# ИМПОРТ AI ИНСТРУМЕНТА
try:
    from kittycore.tools.ai_integration_tool import AIIntegrationTool
    IMPORT_AI_OK = True
except ImportError as e:
    print(f"❌ ИМПОРТ ai_integration_tool: {e}")
    IMPORT_AI_OK = False

class TimeoutHonestTester:
    """Честная система тестирования инструментов с таймаутами"""
    
    def __init__(self):
        self.results = []
        self.memory_records = []
        self.timeout_tests = []
    
    def test_tool_timeout_honest(self, tool_name, test_func, expected_max_time=60):
        """Честное тестирование инструмента с контролем таймаута"""
        print(f"\n⏰ Тестирую таймаут {tool_name} (макс {expected_max_time}с)...")
        start_time = time.time()
        
        try:
            result = test_func()
            execution_time = time.time() - start_time
            
            # Честная проверка результата и времени
            is_honest = self.is_timeout_result_honest(result, tool_name, execution_time, expected_max_time)
            
            test_result = {
                "tool": tool_name,
                "success": is_honest,
                "size_bytes": len(str(result)) if result else 0,
                "execution_time": round(execution_time, 2),
                "expected_max_time": expected_max_time,
                "timeout_ok": execution_time <= expected_max_time,
                "honest": is_honest,
                "result_sample": str(result)[:200] if result else "NO_DATA"
            }
            
            self.results.append(test_result)
            
            if is_honest:
                time_status = "⚡ БЫСТРО" if execution_time <= expected_max_time else "🐌 МЕДЛЕННО"
                print(f"✅ {tool_name}: {test_result['size_bytes']} байт за {execution_time:.2f}с {time_status}")
                self.record_working_timeout_params(tool_name, test_func.__name__, execution_time)
            else:
                print(f"❌ {tool_name}: подозрительный результат (время: {execution_time:.2f}с)")
            
            return test_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)[:200]
            print(f"❌ {tool_name}: ТАЙМАУТ ОШИБКА - {error_msg} (время: {execution_time:.2f}с)")
            
            # Специальная диагностика таймаут-ошибок
            timeout_diagnostic = self.diagnose_timeout_error(e, tool_name, execution_time)
            
            test_result = {
                "tool": tool_name,
                "success": False,
                "size_bytes": 0,
                "execution_time": round(execution_time, 2),
                "expected_max_time": expected_max_time,
                "timeout_ok": execution_time <= expected_max_time,
                "honest": False,
                "error": error_msg,
                "timeout_diagnostic": timeout_diagnostic
            }
            
            self.results.append(test_result)
            return test_result
    
    def diagnose_timeout_error(self, error, tool_name, execution_time):
        """Диагностика таймаут-ошибок"""
        error_str = str(error).lower()
        
        if "timeout" in error_str:
            return f"TIMEOUT_ERROR: {tool_name} превысил лимит времени ({execution_time:.1f}с)"
        elif "connection" in error_str:
            return f"CONNECTION_ERROR: Проблемы с подключением к API"
        elif "api" in error_str or "key" in error_str:
            return f"API_ERROR: Проблемы с API ключом или лимитами"
        elif "rate" in error_str or "limit" in error_str:
            return f"RATE_LIMIT: Превышен лимит запросов API"
        else:
            return f"UNKNOWN_TIMEOUT: {error_str}"
    
    def is_timeout_result_honest(self, result, tool_name, execution_time, expected_max_time):
        """Проверка честности результата с учётом времени выполнения"""
        if not result:
            return False
        
        result_str = str(result)
        
        # Подозрительные паттерны для AI инструментов
        fake_patterns = [
            f"{tool_name}: AI запрос выполнен",
            "демо режим AI",
            "модель недоступна - заглушка",
            "ответ сгенерирован локально",
            "AI эмулятор активирован"
        ]
        
        for pattern in fake_patterns:
            if pattern.lower() in result_str.lower():
                return False
        
        # Проверка на реальные AI признаки
        ai_indicators = [
            "model", "provider", "response", "completion",
            "gpt", "claude", "llama", "openai", "anthropic"
        ]
        
        has_ai_data = any(indicator in result_str.lower() for indicator in ai_indicators)
        
        # Минимальный размер + AI признаки + разумное время
        size_ok = len(result_str) > 30
        time_ok = execution_time <= (expected_max_time + 10)  # Даём 10с буфер
        
        return size_ok and has_ai_data and time_ok
    
    def record_working_timeout_params(self, tool_name, action_name, execution_time):
        """Записать рабочие таймаут-параметры в память"""
        memory_record = {
            "tool": tool_name,
            "working_action": action_name,
            "timestamp": time.time(),
            "execution_time": execution_time,
            "status": "TIMEOUT_WORKING",
            "timeout_pattern": f"success in {execution_time:.1f}s",
            "notes": f"Timeout test passed for {tool_name} in reasonable time"
        }
        self.memory_records.append(memory_record)

def test_ai_integration_fast():
    """Тест AIIntegrationTool с быстрой моделью"""
    if not IMPORT_AI_OK:
        return "IMPORT_ERROR"
    
    tool = AIIntegrationTool()
    
    # РЕАЛЬНЫЙ тест с быстрой лёгкой моделью
    result = tool.execute(
        action="complete",
        prompt="Say 'Hello World' in one word only",
        provider="groq",  # Быстрый провайдер
        model="llama-3.1-8b-instant",  # Лёгкая модель
        max_tokens=5,  # Очень короткий ответ
        temperature=0.1  # Детерминированный
    )
    
    return result

def test_ai_integration_models():
    """Тест AIIntegrationTool получение списка моделей"""
    if not IMPORT_AI_OK:
        return "IMPORT_ERROR"
    
    tool = AIIntegrationTool()
    
    # РЕАЛЬНЫЙ тест - получение информации без LLM вызова
    result = tool.execute(
        action="list_models",
        provider="openrouter"  # Известный провайдер
    )
    
    return result

def test_ai_integration_providers():
    """Тест AIIntegrationTool получение провайдеров"""
    if not IMPORT_AI_OK:
        return "IMPORT_ERROR"
    
    tool = AIIntegrationTool()
    
    # РЕАЛЬНЫЙ тест - получение информации о провайдерах
    result = tool.execute(
        action="list_providers"
    )
    
    return result

def test_ai_integration_config():
    """Тест AIIntegrationTool проверка конфигурации"""
    if not IMPORT_AI_OK:
        return "IMPORT_ERROR"
    
    tool = AIIntegrationTool()
    
    # РЕАЛЬНЫЙ тест - проверка настроек
    result = tool.execute(
        action="get_config"
    )
    
    return result

def main():
    """Главная функция тестирования этапа 4"""
    print("⏰ ЭТАП 4: ИСПРАВЛЕНИЕ ТАЙМАУТОВ")
    print("=" * 50)
    
    tester = TimeoutHonestTester()
    
    # Тестируем AI инструмент с разными временными ограничениями
    if IMPORT_AI_OK:
        # Быстрые тесты (должны работать за секунды)
        tester.test_tool_timeout_honest("ai_providers", test_ai_integration_providers, 5)
        tester.test_tool_timeout_honest("ai_config", test_ai_integration_config, 5)
        tester.test_tool_timeout_honest("ai_models", test_ai_integration_models, 10)
        
        # Медленный тест (реальный LLM запрос)
        tester.test_tool_timeout_honest("ai_fast_llm", test_ai_integration_fast, 30)
    else:
        print("❌ ai_integration_tool: ИМПОРТ НЕ ИСПРАВЛЕН")
    
    # Результаты этапа 4
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ЭТАПА 4:")
    
    total_tests = len(tester.results)
    honest_tests = sum(1 for r in tester.results if r["honest"])
    timeout_ok_tests = sum(1 for r in tester.results if r["timeout_ok"])
    success_rate = (honest_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Всего таймаут-тестов: {total_tests}")
    print(f"Честных тестов: {honest_tests}")
    print(f"Укложились в время: {timeout_ok_tests}")
    print(f"Процент успеха: {success_rate:.1f}%")
    
    print("\n🎯 ДЕТАЛИ:")
    for result in tester.results:
        status = "✅ ЧЕСТНЫЙ" if result["honest"] else "❌ ПРОБЛЕМА"
        time_status = "⚡" if result["timeout_ok"] else "🐌"
        expected = result["expected_max_time"]
        actual = result["execution_time"]
        print(f"{result['tool']}: {status} {time_status} ({actual:.1f}с из {expected}с, {result['size_bytes']} байт)")
        
        if "timeout_diagnostic" in result:
            print(f"   🔍 Таймаут-диагностика: {result['timeout_diagnostic']}")
        elif result["honest"]:
            print(f"   ⏰ Образец: {result['result_sample'][:100]}...")
    
    # Сохраняем результаты
    with open("stage4_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "stage": 4,
            "description": "Timeout fixes for AI tools",
            "results": tester.results,
            "memory_records": tester.memory_records,
            "summary": {
                "total_tests": total_tests,
                "honest_tests": honest_tests,
                "timeout_ok_tests": timeout_ok_tests,
                "success_rate": success_rate,
                "ai_tools_tested": 1
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в stage4_results.json")
    
    # Подсчёт уникальных AI инструментов
    unique_ai_tools = set()
    for result in tester.results:
        if result["honest"] and result["timeout_ok"]:
            if "ai_" in result["tool"]:
                unique_ai_tools.add("ai_integration_tool")
    
    new_honest_tools = len(unique_ai_tools)
    
    # Прогресс к цели
    current_honest = 8  # из этапов 1-2
    total_honest = current_honest + new_honest_tools
    total_target = 18
    
    print(f"\n🚀 ПРОГРЕСС К ЦЕЛИ:")
    print(f"Было честных: {current_honest}/18 (44.4%)")
    print(f"Стало честных: {total_honest}/18 ({total_honest/total_target*100:.1f}%)")
    print(f"Улучшение: +{new_honest_tools} AI инструментов")
    
    # Анализ времени выполнения
    print(f"\n⏰ АНАЛИЗ ВРЕМЕНИ:")
    fast_tests = [r for r in tester.results if r["execution_time"] <= 10]
    slow_tests = [r for r in tester.results if r["execution_time"] > 10]
    
    if fast_tests:
        avg_fast = sum(r["execution_time"] for r in fast_tests) / len(fast_tests)
        print(f"⚡ Быстрые тесты ({len(fast_tests)}): среднее {avg_fast:.1f}с")
    
    if slow_tests:
        avg_slow = sum(r["execution_time"] for r in slow_tests) / len(slow_tests)
        print(f"🐌 Медленные тесты ({len(slow_tests)}): среднее {avg_slow:.1f}с")
    
    if success_rate >= 50 and timeout_ok_tests >= (total_tests * 0.75):
        print("\n🎉 ЭТАП 4 УСПЕШЕН! Переходим к ЭТАПУ 5...")
        return True
    else:
        print("\n⚠️ ЭТАП 4 ТРЕБУЕТ ДОРАБОТКИ")
        return False

if __name__ == "__main__":
    main() 