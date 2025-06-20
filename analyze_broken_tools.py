#!/usr/bin/env python3
"""
🔧 АНАЛИЗ НЕРАБОЧИХ ИНСТРУМЕНТОВ KittyCore 3.0

ЦЕЛЬ: Определить причины неработоспособности и план исправления
НЕРАБОЧИЕ: enhanced_web_scraping, smart_function, database, network
"""

import asyncio
import traceback

async def analyze_broken_tool(tool_name, module_path, class_name, test_params):
    """Детальный анализ проблем инструмента"""
    print(f"\n🔧 АНАЛИЗ: {tool_name.upper()}")
    print("=" * 60)
    
    try:
        # Импорт
        import importlib
        module = importlib.import_module(module_path)
        tool_class = getattr(module, class_name)
        tool = tool_class()
        
        print(f"✅ Импорт: OK")
        print(f"✅ Инициализация: OK")
        
        # Тестирование
        try:
            result = await tool.execute(**test_params)
            
            print(f"✅ Execute: OK")
            print(f"📊 Success: {getattr(result, 'success', 'N/A')}")
            print(f"📊 Data: {len(str(getattr(result, 'data', ''))) if hasattr(result, 'data') else 0} символов")
            
            if hasattr(result, 'error'):
                print(f"⚠️ Error: {result.error}")
            
            # Диагностика проблемы
            if hasattr(result, 'success') and not result.success:
                print(f"🔍 ПРОБЛЕМА: Инструмент выполняется, но возвращает success=False")
                if hasattr(result, 'error'):
                    print(f"🔍 ПРИЧИНА: {result.error}")
                return "LOGIC_ERROR"
            elif not hasattr(result, 'data') or not result.data:
                print(f"🔍 ПРОБЛЕМА: Пустые данные")
                return "EMPTY_DATA"
            else:
                print(f"🔍 ПРОБЛЕМА: Неизвестная - инструмент работает но тест не прошёл")
                return "UNKNOWN"
                
        except Exception as e:
            print(f"❌ Execute: ОШИБКА")
            print(f"🔍 Exception: {str(e)[:200]}")
            print(f"🔍 Traceback:")
            traceback.print_exc()
            return "EXECUTION_ERROR"
            
    except ImportError as e:
        print(f"❌ Импорт: ОШИБКА - {e}")
        return "IMPORT_ERROR"
    except Exception as e:
        print(f"❌ Инициализация: ОШИБКА - {e}")
        return "INIT_ERROR"

async def main():
    """Анализ всех нерабочих инструментов"""
    print("🔧 АНАЛИЗ НЕРАБОЧИХ ИНСТРУМЕНТОВ")
    print("=" * 80)
    
    broken_tools = [
        {
            "name": "enhanced_web_scraping",
            "module": "kittycore.tools.enhanced_web_scraping_tool", 
            "class": "EnhancedWebScrapingTool",
            "params": {"url": "https://httpbin.org/html"},
            "expected": "HTML контент с httpbin.org"
        },
        {
            "name": "smart_function",
            "module": "kittycore.tools.smart_function_tool",
            "class": "SmartFunctionTool",
            "params": {"action": "execute", "code": "def test(): return 'ok'", "function_name": "test"},
            "expected": "Результат выполнения функции 'ok'"
        },
        {
            "name": "database",
            "module": "kittycore.tools.database_tool", 
            "class": "DatabaseTool",
            "params": {"query": "SELECT 1 as test"},
            "expected": "Результат SQL запроса"
        },
        {
            "name": "network",
            "module": "kittycore.tools.network_tool",
            "class": "NetworkTool", 
            "params": {"action": "get_info"},
            "expected": "Информация о сети"
        }
    ]
    
    problems = {}
    
    for tool_config in broken_tools:
        print(f"\n📋 ОЖИДАЕТСЯ: {tool_config['expected']}")
        
        problem_type = await analyze_broken_tool(
            tool_config["name"],
            tool_config["module"],
            tool_config["class"], 
            tool_config["params"]
        )
        
        problems[tool_config["name"]] = problem_type
    
    # Итоги анализа
    print(f"\n📊 ИТОГИ АНАЛИЗА ПРОБЛЕМ")
    print("=" * 80)
    
    problem_groups = {}
    for tool, problem in problems.items():
        if problem not in problem_groups:
            problem_groups[problem] = []
        problem_groups[problem].append(tool)
    
    for problem_type, tools in problem_groups.items():
        print(f"\n🔍 {problem_type}:")
        for tool in tools:
            print(f"  - {tool}")
    
    # План исправления
    print(f"\n🛠️ ПЛАН ИСПРАВЛЕНИЯ")
    print("=" * 80)
    
    if "LOGIC_ERROR" in problem_groups:
        print(f"📝 LOGIC_ERROR инструменты:")
        print(f"   - Проверить внутреннюю логику execute()")
        print(f"   - Исправить условия success=True")
        print(f"   - Протестировать с правильными параметрами")
    
    if "EMPTY_DATA" in problem_groups:
        print(f"📝 EMPTY_DATA инструменты:")
        print(f"   - Проверить генерацию данных")
        print(f"   - Убедиться что данные записываются в result.data")
    
    if "EXECUTION_ERROR" in problem_groups:
        print(f"📝 EXECUTION_ERROR инструменты:")
        print(f"   - Исправить исключения в коде")
        print(f"   - Добавить обработку ошибок")
    
    if "IMPORT_ERROR" in problem_groups:
        print(f"📝 IMPORT_ERROR инструменты:")
        print(f"   - Проверить пути импорта")
        print(f"   - Установить недостающие зависимости")
    
    return problems

if __name__ == "__main__":
    asyncio.run(main()) 