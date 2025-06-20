#!/usr/bin/env python3
"""
⚡ ЭТАП 2: ASYNC/SYNC ИСПРАВЛЕНИЯ
Тестирование инструментов с async/sync проблемами

ПЛАН ЭТАПА 2:
- network_tool: исправить "coroutine was never awaited"
- security_tool: исправить async проблемы
- data_analysis_tool: исправить "a coroutine was expected"
- Оценить прогресс: +3 инструмента готовых (2-3 дня)

ПРИНЦИПЫ:
✅ РЕАЛЬНЫЕ async/await вызовы
❌ НЕТ синхронных заглушек
✅ Правильная обработка корутин
✅ Запись правильных async паттернов в память
"""

import time
import json
import asyncio
import traceback
from pathlib import Path

# ИМПОРТЫ ПРОБЛЕМНЫХ ИНСТРУМЕНТОВ
try:
    from kittycore.tools.network_tool import NetworkTool
    IMPORT_NETWORK_OK = True
except ImportError as e:
    print(f"❌ ИМПОРТ network_tool: {e}")
    IMPORT_NETWORK_OK = False

try:
    from kittycore.tools.security_tool import SecurityTool
    IMPORT_SECURITY_OK = True
except ImportError as e:
    print(f"❌ ИМПОРТ security_tool: {e}")
    IMPORT_SECURITY_OK = False

try:
    from kittycore.tools.data_analysis_tool import DataAnalysisTool
    IMPORT_DATA_OK = True
except ImportError as e:
    print(f"❌ ИМПОРТ data_analysis_tool: {e}")
    IMPORT_DATA_OK = False

class AsyncHonestTester:
    """Честная система тестирования async инструментов"""
    
    def __init__(self):
        self.results = []
        self.memory_records = []
    
    async def test_tool_async_honest(self, tool_name, test_func):
        """Честное тестирование async инструмента"""
        print(f"\n⚡ Тестирую async {tool_name}...")
        start_time = time.time()
        
        try:
            # Пробуем выполнить как async функцию
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            execution_time = time.time() - start_time
            
            # Честная проверка
            is_honest = self.is_result_honest(result, tool_name)
            
            test_result = {
                "tool": tool_name,
                "success": is_honest,
                "size_bytes": len(str(result)) if result else 0,
                "execution_time": round(execution_time, 2),
                "honest": is_honest,
                "result_sample": str(result)[:100] if result else "NO_DATA",
                "async_handled": True
            }
            
            self.results.append(test_result)
            
            if is_honest:
                print(f"✅ {tool_name}: {test_result['size_bytes']} байт за {execution_time:.2f}с (async)")
                self.record_working_async_params(tool_name, test_func.__name__)
            else:
                print(f"❌ {tool_name}: подозрительный async результат")
            
            return test_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)[:100]
            print(f"❌ {tool_name}: ASYNC ОШИБКА - {error_msg}")
            
            # Специальная диагностика async проблем
            async_diagnostic = self.diagnose_async_error(e, tool_name)
            
            test_result = {
                "tool": tool_name,
                "success": False,
                "size_bytes": 0,
                "execution_time": round(execution_time, 2),
                "honest": False,
                "error": error_msg,
                "async_diagnostic": async_diagnostic
            }
            
            self.results.append(test_result)
            return test_result
    
    def diagnose_async_error(self, error, tool_name):
        """Диагностика async ошибок"""
        error_str = str(error).lower()
        
        if "coroutine was never awaited" in error_str:
            return f"ASYNC_PROBLEM: {tool_name} возвращает корутину, но не await"
        elif "a coroutine was expected" in error_str:
            return f"SYNC_PROBLEM: {tool_name} ожидает корутину, но получает sync"
        elif "cannot be called from a running event loop" in error_str:
            return f"LOOP_PROBLEM: {tool_name} конфликт event loop"
        else:
            return f"UNKNOWN_ASYNC: {error_str}"
    
    def is_result_honest(self, result, tool_name):
        """Проверка честности результата"""
        if not result:
            return False
        
        result_str = str(result)
        
        # Подозрительные паттерны
        fake_patterns = [
            f"{tool_name}: успешно протестирован",
            "async тестирование завершено",
            "корутина выполнена успешно",
            "async заглушка",
            "await результат получен"
        ]
        
        for pattern in fake_patterns:
            if pattern.lower() in result_str.lower():
                return False
        
        # Минимальный размер для честности
        return len(result_str) > 20
    
    def record_working_async_params(self, tool_name, action_name):
        """Записать рабочие async параметры в память"""
        memory_record = {
            "tool": tool_name,
            "working_action": action_name,
            "timestamp": time.time(),
            "status": "ASYNC_WORKING",
            "async_pattern": "await tool.execute() success",
            "notes": f"Async test passed for {tool_name}"
        }
        self.memory_records.append(memory_record)

async def test_network_tool_async():
    """Тест NetworkTool с правильным async подходом"""
    if not IMPORT_NETWORK_OK:
        return "IMPORT_ERROR"
    
    tool = NetworkTool()
    
    # РЕАЛЬНЫЙ async тест - ping команда
    result = await tool.execute_async(
        action="ping",
        host="8.8.8.8",
        count=3,
        timeout=5
    )
    
    return result

def test_network_tool_sync():
    """Тест NetworkTool с синхронным подходом"""
    if not IMPORT_NETWORK_OK:
        return "IMPORT_ERROR"
    
    tool = NetworkTool()
    
    # РЕАЛЬНЫЙ sync тест - получение информации о сети
    result = tool.execute(
        action="get_network_info"
    )
    
    return result

async def test_security_tool_async():
    """Тест SecurityTool с правильным async подходом"""
    if not IMPORT_SECURITY_OK:
        return "IMPORT_ERROR"
    
    tool = SecurityTool()
    
    # РЕАЛЬНЫЙ async тест - сканирование безопасности
    result = await tool.execute_async(
        action="scan_file",
        file_path="/tmp",
        scan_type="basic"
    )
    
    return result

def test_security_tool_sync():
    """Тест SecurityTool с синхронным подходом"""
    if not IMPORT_SECURITY_OK:
        return "IMPORT_ERROR"
    
    tool = SecurityTool()
    
    # РЕАЛЬНЫЙ sync тест - получение правил безопасности
    result = tool.execute(
        action="get_security_rules"
    )
    
    return result

async def test_data_analysis_tool_async():
    """Тест DataAnalysisTool с правильным async подходом"""
    if not IMPORT_DATA_OK:
        return "IMPORT_ERROR"
    
    tool = DataAnalysisTool()
    
    # РЕАЛЬНЫЙ async тест - анализ данных
    test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = await tool.execute_async(
        action="analyze_data",
        data=test_data,
        analysis_type="statistics"
    )
    
    return result

def test_data_analysis_tool_sync():
    """Тест DataAnalysisTool с синхронным подходом"""
    if not IMPORT_DATA_OK:
        return "IMPORT_ERROR"
    
    tool = DataAnalysisTool()
    
    # РЕАЛЬНЫЙ sync тест - получение информации о возможностях
    result = tool.execute(
        action="get_analysis_types"
    )
    
    return result

async def main():
    """Главная async функция тестирования этапа 2"""
    print("⚡ ЭТАП 2: ASYNC/SYNC ИСПРАВЛЕНИЯ")
    print("=" * 50)
    
    tester = AsyncHonestTester()
    
    # Тестируем инструменты с async/sync проблемами
    if IMPORT_NETWORK_OK:
        await tester.test_tool_async_honest("network_tool_async", test_network_tool_async)
        await tester.test_tool_async_honest("network_tool_sync", test_network_tool_sync)
    else:
        print("❌ network_tool: ИМПОРТ НЕ ИСПРАВЛЕН")
    
    if IMPORT_SECURITY_OK:
        await tester.test_tool_async_honest("security_tool_async", test_security_tool_async)
        await tester.test_tool_async_honest("security_tool_sync", test_security_tool_sync)
    else:
        print("❌ security_tool: ИМПОРТ НЕ ИСПРАВЛЕН")
    
    if IMPORT_DATA_OK:
        await tester.test_tool_async_honest("data_analysis_tool_async", test_data_analysis_tool_async)
        await tester.test_tool_async_honest("data_analysis_tool_sync", test_data_analysis_tool_sync)
    else:
        print("❌ data_analysis_tool: ИМПОРТ НЕ ИСПРАВЛЕН")
    
    # Результаты этапа 2
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ЭТАПА 2:")
    
    total_tests = len(tester.results)
    honest_tests = sum(1 for r in tester.results if r["honest"])
    success_rate = (honest_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Всего тестов: {total_tests}")
    print(f"Честных тестов: {honest_tests}")
    print(f"Процент успеха: {success_rate:.1f}%")
    
    print("\n🎯 ДЕТАЛИ:")
    for result in tester.results:
        status = "✅ ЧЕСТНЫЙ" if result["honest"] else "❌ ПРОБЛЕМА"
        async_info = " (async)" if result.get("async_handled") else ""
        print(f"{result['tool']}: {status} ({result['size_bytes']} байт){async_info}")
        if "async_diagnostic" in result:
            print(f"   🔍 Диагностика: {result['async_diagnostic']}")
    
    # Сохраняем результаты
    with open("stage2_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "stage": 2,
            "description": "Async/sync fixes",
            "results": tester.results,
            "memory_records": tester.memory_records,
            "summary": {
                "total_tests": total_tests,
                "honest_tests": honest_tests,
                "success_rate": success_rate,
                "async_tools_tested": 3
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в stage2_results.json")
    
    # Подсчёт уникальных инструментов
    unique_tools = set()
    for result in tester.results:
        if result["honest"]:
            tool_base = result["tool"].replace("_async", "").replace("_sync", "")
            unique_tools.add(tool_base)
    
    new_honest_tools = len(unique_tools)
    
    # Прогресс к цели
    current_honest = 5  # из этапа 1
    total_honest = current_honest + new_honest_tools
    total_target = 18
    
    print(f"\n🚀 ПРОГРЕСС К ЦЕЛИ:")
    print(f"Было честных: {current_honest}/18 (27.8%)")
    print(f"Стало честных: {total_honest}/18 ({total_honest/total_target*100:.1f}%)")
    print(f"Улучшение: +{new_honest_tools} инструментов")
    
    if success_rate >= 50:
        print("\n🎉 ЭТАП 2 УСПЕШЕН! Переходим к ЭТАПУ 3...")
        return True
    else:
        print("\n⚠️ ЭТАП 2 ТРЕБУЕТ ДОРАБОТКИ")
        return False

if __name__ == "__main__":
    # Запуск async main
    asyncio.run(main()) 