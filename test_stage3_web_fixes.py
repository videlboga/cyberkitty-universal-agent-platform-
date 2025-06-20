#!/usr/bin/env python3
"""
🌐 ЭТАП 3: ВЕБ-ИНСТРУМЕНТЫ ИСПРАВЛЕНИЯ
Тестирование веб-инструментов с неправильными параметрами

ПЛАН ЭТАПА 3:
- enhanced_web_search_tool: исправить параметры (max_results vs limit)
- enhanced_web_scraping_tool: исправить пустые данные
- Оценить прогресс: +2 инструмента готовых (1-2 дня)

ПРИНЦИПЫ:
✅ РЕАЛЬНЫЕ веб-запросы
❌ НЕТ фиктивных URL
✅ Правильные параметры API
✅ Запись рабочих веб-паттернов в память
"""

import time
import json
import asyncio
import traceback
from pathlib import Path

# ИМПОРТЫ ВЕБ-ИНСТРУМЕНТОВ
try:
    from kittycore.tools.enhanced_web_search_tool import EnhancedWebSearchTool
    IMPORT_WEB_SEARCH_OK = True
except ImportError as e:
    print(f"❌ ИМПОРТ enhanced_web_search_tool: {e}")
    IMPORT_WEB_SEARCH_OK = False

try:
    from kittycore.tools.enhanced_web_scraping_tool import EnhancedWebScrapingTool
    IMPORT_WEB_SCRAPING_OK = True
except ImportError as e:
    print(f"❌ ИМПОРТ enhanced_web_scraping_tool: {e}")
    IMPORT_WEB_SCRAPING_OK = False

class WebHonestTester:
    """Честная система тестирования веб-инструментов"""
    
    def __init__(self):
        self.results = []
        self.memory_records = []
        self.web_parameters_tested = []
    
    def test_web_tool_honest(self, tool_name, test_func):
        """Честное тестирование веб-инструмента"""
        print(f"\n🌐 Тестирую веб {tool_name}...")
        start_time = time.time()
        
        try:
            result = test_func()
            execution_time = time.time() - start_time
            
            # Честная проверка веб-результата
            is_honest = self.is_web_result_honest(result, tool_name)
            
            test_result = {
                "tool": tool_name,
                "success": is_honest,
                "size_bytes": len(str(result)) if result else 0,
                "execution_time": round(execution_time, 2),
                "honest": is_honest,
                "result_sample": str(result)[:150] if result else "NO_DATA",
                "web_data": True
            }
            
            self.results.append(test_result)
            
            if is_honest:
                print(f"✅ {tool_name}: {test_result['size_bytes']} байт за {execution_time:.2f}с (веб)")
                self.record_working_web_params(tool_name, test_func.__name__)
            else:
                print(f"❌ {tool_name}: подозрительный веб-результат")
            
            return test_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)[:150]
            print(f"❌ {tool_name}: ВЕБ ОШИБКА - {error_msg}")
            
            # Специальная диагностика веб-ошибок
            web_diagnostic = self.diagnose_web_error(e, tool_name)
            
            test_result = {
                "tool": tool_name,
                "success": False,
                "size_bytes": 0,
                "execution_time": round(execution_time, 2),
                "honest": False,
                "error": error_msg,
                "web_diagnostic": web_diagnostic
            }
            
            self.results.append(test_result)
            return test_result
    
    def diagnose_web_error(self, error, tool_name):
        """Диагностика веб-ошибок"""
        error_str = str(error).lower()
        
        if "unexpected keyword argument" in error_str:
            return f"PARAMETER_ERROR: Неправильные параметры для {tool_name}"
        elif "max_results" in error_str:
            return f"MAX_RESULTS_ERROR: Использовать limit вместо max_results"
        elif "connection" in error_str or "timeout" in error_str:
            return f"NETWORK_ERROR: Проблемы с сетью/таймаут"
        elif "api" in error_str or "key" in error_str:
            return f"API_ERROR: Проблемы с API ключом"
        else:
            return f"UNKNOWN_WEB: {error_str}"
    
    def is_web_result_honest(self, result, tool_name):
        """Проверка честности веб-результата"""
        if not result:
            return False
        
        result_str = str(result)
        
        # Подозрительные веб-паттерны
        fake_patterns = [
            f"{tool_name}: веб-поиск завершён",
            "данные получены с сайта",
            "результат веб-скрапинга",
            "демо веб-данные",
            "пример поисковых результатов",
            "http://example.com",
            "https://fake-url.com"
        ]
        
        for pattern in fake_patterns:
            if pattern.lower() in result_str.lower():
                return False
        
        # Проверка на реальные веб-данные
        real_indicators = [
            "http", "www.", ".com", ".org", ".net",
            "title", "content", "url", "snippet"
        ]
        
        has_real_data = any(indicator in result_str.lower() for indicator in real_indicators)
        
        # Минимальный размер + признаки реальных веб-данных
        return len(result_str) > 30 and has_real_data
    
    def record_working_web_params(self, tool_name, action_name):
        """Записать рабочие веб-параметры в память"""
        memory_record = {
            "tool": tool_name,
            "working_action": action_name,
            "timestamp": time.time(),
            "status": "WEB_WORKING",
            "web_pattern": "real web requests success",
            "notes": f"Web test passed for {tool_name} with real data"
        }
        self.memory_records.append(memory_record)

def test_enhanced_web_search_limit():
    """Тест EnhancedWebSearchTool с правильным параметром limit"""
    if not IMPORT_WEB_SEARCH_OK:
        return "IMPORT_ERROR"
    
    tool = EnhancedWebSearchTool()
    
    # РЕАЛЬНЫЙ тест с правильным параметром limit
    result = tool.execute(
        action="search",
        query="KittyCore агентная система",
        limit=3  # НЕ max_results!
    )
    
    return result

def test_enhanced_web_search_max_results():
    """Тест EnhancedWebSearchTool с неправильным параметром max_results"""
    if not IMPORT_WEB_SEARCH_OK:
        return "IMPORT_ERROR"
    
    tool = EnhancedWebSearchTool()
    
    # Тест с неправильным параметром для диагностики
    try:
        result = tool.execute(
            action="search",
            query="Python programming",
            max_results=3  # Проверяем что это НЕ работает
        )
        return result
    except Exception as e:
        return f"EXPECTED_ERROR: {str(e)}"

def test_enhanced_web_scraping_real():
    """Тест EnhancedWebScrapingTool с реальным URL"""
    if not IMPORT_WEB_SCRAPING_OK:
        return "IMPORT_ERROR"
    
    tool = EnhancedWebScrapingTool()
    
    # РЕАЛЬНЫЙ тест с реальным URL
    result = tool.execute(
        action="scrape_page",
        url="https://httpbin.org/html",
        extract_links=True,
        extract_text=True
    )
    
    return result

def test_enhanced_web_scraping_info():
    """Тест EnhancedWebScrapingTool получение информации"""
    if not IMPORT_WEB_SCRAPING_OK:
        return "IMPORT_ERROR"
    
    tool = EnhancedWebScrapingTool()
    
    # Тест получения информации о возможностях
    result = tool.execute(
        action="get_scraping_options"
    )
    
    return result

def main():
    """Главная функция тестирования этапа 3"""
    print("🌐 ЭТАП 3: ВЕБ-ИНСТРУМЕНТЫ ИСПРАВЛЕНИЯ")
    print("=" * 50)
    
    tester = WebHonestTester()
    
    # Тестируем веб-инструменты с разными параметрами
    if IMPORT_WEB_SEARCH_OK:
        tester.test_web_tool_honest("web_search_limit", test_enhanced_web_search_limit)
        tester.test_web_tool_honest("web_search_max_results", test_enhanced_web_search_max_results)
    else:
        print("❌ enhanced_web_search_tool: ИМПОРТ НЕ ИСПРАВЛЕН")
    
    if IMPORT_WEB_SCRAPING_OK:
        tester.test_web_tool_honest("web_scraping_real", test_enhanced_web_scraping_real)
        tester.test_web_tool_honest("web_scraping_info", test_enhanced_web_scraping_info)
    else:
        print("❌ enhanced_web_scraping_tool: ИМПОРТ НЕ ИСПРАВЛЕН")
    
    # Результаты этапа 3
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ЭТАПА 3:")
    
    total_tests = len(tester.results)
    honest_tests = sum(1 for r in tester.results if r["honest"])
    success_rate = (honest_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Всего веб-тестов: {total_tests}")
    print(f"Честных веб-тестов: {honest_tests}")
    print(f"Процент успеха: {success_rate:.1f}%")
    
    print("\n🎯 ДЕТАЛИ:")
    for result in tester.results:
        status = "✅ ЧЕСТНЫЙ" if result["honest"] else "❌ ПРОБЛЕМА"
        web_info = " (веб)" if result.get("web_data") else ""
        print(f"{result['tool']}: {status} ({result['size_bytes']} байт){web_info}")
        if "web_diagnostic" in result:
            print(f"   🔍 Веб-диагностика: {result['web_diagnostic']}")
        elif result["honest"]:
            print(f"   🌐 Образец: {result['result_sample'][:80]}...")
    
    # Сохраняем результаты
    with open("stage3_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "stage": 3,
            "description": "Web tools parameter fixes",
            "results": tester.results,
            "memory_records": tester.memory_records,
            "summary": {
                "total_tests": total_tests,
                "honest_tests": honest_tests,
                "success_rate": success_rate,
                "web_tools_tested": 2
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в stage3_results.json")
    
    # Подсчёт уникальных веб-инструментов
    unique_web_tools = set()
    for result in tester.results:
        if result["honest"]:
            if "web_search" in result["tool"]:
                unique_web_tools.add("enhanced_web_search_tool")
            elif "web_scraping" in result["tool"]:
                unique_web_tools.add("enhanced_web_scraping_tool")
    
    new_honest_tools = len(unique_web_tools)
    
    # Прогресс к цели
    current_honest = 8  # из этапов 1-2
    total_honest = current_honest + new_honest_tools
    total_target = 18
    
    print(f"\n🚀 ПРОГРЕСС К ЦЕЛИ:")
    print(f"Было честных: {current_honest}/18 (44.4%)")
    print(f"Стало честных: {total_honest}/18 ({total_honest/total_target*100:.1f}%)")
    print(f"Улучшение: +{new_honest_tools} веб-инструментов")
    
    # Анализ параметров
    print(f"\n🔧 АНАЛИЗ ПАРАМЕТРОВ:")
    working_params = []
    failing_params = []
    
    for result in tester.results:
        if result["honest"]:
            working_params.append(result["tool"])
        else:
            failing_params.append(result["tool"])
    
    if working_params:
        print(f"✅ Рабочие: {', '.join(working_params)}")
    if failing_params:
        print(f"❌ Проблемные: {', '.join(failing_params)}")
    
    if success_rate >= 25:  # Хотя бы 1 из 4 тестов
        print("\n🎉 ЭТАП 3 УСПЕШЕН! Переходим к ЭТАПУ 4...")
        return True
    else:
        print("\n⚠️ ЭТАП 3 ТРЕБУЕТ ДОРАБОТКИ")
        return False

if __name__ == "__main__":
    main() 