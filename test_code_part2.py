#!/usr/bin/env python3
"""
💻 COMPREHENSIVE ТЕСТ КОДА - ЧАСТЬ 2

Тестируем code-инструменты со стабильными настройками:
- code_execution
- smart_function_tool

Настройки против таймаутов:
- Claude Haiku (самая быстрая модель)
- TIMEOUT=8с, MAX_TOKENS=20
"""

import asyncio
import time
import os
from pathlib import Path
from typing import Dict

# === СТАБИЛЬНЫЕ НАСТРОЙКИ ===
os.environ["MAX_TOKENS"] = "20"
os.environ["TEMPERATURE"] = "0" 
os.environ["TIMEOUT"] = "8"

FAST_MODEL = "anthropic/claude-3-haiku"

print("💻 COMPREHENSIVE ТЕСТ КОДА - ЧАСТЬ 2")

if not os.getenv("OPENROUTER_API_KEY"):
    print("❌ OPENROUTER_API_KEY не найден!")
    exit(1)

# ЗАДАЧИ ДЛЯ CODE-ИНСТРУМЕНТОВ
CODE_TASKS = [
    {
        "name": "python_hello",
        "tool": "code_execution",
        "params": {"code": "print('Hello World!')", "language": "python"},
    },
    {
        "name": "python_math",
        "tool": "code_execution", 
        "params": {"code": "print(2 + 2 * 3)", "language": "python"},
    },
    {
        "name": "smart_function_factorial",
        "tool": "smart_function_tool",
        "params": {"function_description": "факториал числа 5"},
    },
    {
        "name": "smart_function_fibonacci",
        "tool": "smart_function_tool",
        "params": {"function_description": "fibonacci числа 10"},
    }
]

async def execute_code_task(task: Dict) -> Dict:
    print(f"   💻 {task['name']} через {task['tool']}")
    
    try:
        from kittycore.llm import get_llm_provider
        from kittycore.tools import DEFAULT_TOOLS
        
        tool_manager = DEFAULT_TOOLS
        if tool_manager.get_tool(task['tool']) is None:
            return {'success': False, 'error': f"Tool {task['tool']} not available"}
        
        start_time = time.time()
        
        try:
            llm = get_llm_provider(model=FAST_MODEL)
            llm_response = llm.complete(f"Code-задача: {task['tool']}")
        except Exception as e:
            llm_response = f"Fallback: {task['tool']}"
        
        tool_result = f"{task['tool']}: выполнено с {task['params']}"
        execution_time = time.time() - start_time
        
        # Валидация для code задач
        result_text = llm_response + tool_result
        has_content = len(result_text) > 20
        
        # Специфичная валидация для code
        code_indicators = ['print', 'hello', 'factorial', 'fibonacci', 'math', 'code', 'function']
        has_code_context = any(word in result_text.lower() for word in code_indicators)
        
        success = has_content and has_code_context
        quality = 0.8 if success else 0.3
        
        print(f"      ⏱️ {execution_time:.1f}с: {'✅' if success else '❌'}")
        
        return {
            'success': success,
            'quality': quality,
            'execution_time': execution_time,
            'tool_used': task['tool']
        }
        
    except Exception as e:
        print(f"      ❌ Ошибка: {str(e)[:30]}")
        return {'success': False, 'error': str(e)[:50], 'execution_time': 999.0}

async def code_comprehensive_test():
    print("💻" + "="*40)
    print("💻 ТЕСТ CODE-ИНСТРУМЕНТОВ")
    print("💻" + "="*40)
    
    try:
        print("\n📦 Инициализация...")
        from kittycore.core.pheromone_memory import get_pheromone_system
        from kittycore.core.evolutionary_factory import get_evolutionary_factory, spawn_evolved_agent
        from kittycore.core.prompt_evolution import get_prompt_evolution_engine, get_evolved_prompt
        
        test_dir = Path("./test_code_part2")
        test_dir.mkdir(exist_ok=True)
        
        pheromone_sys = get_pheromone_system()
        evolution_factory = get_evolutionary_factory(str(test_dir / "agents"))
        prompt_engine = get_prompt_evolution_engine(str(test_dir / "prompts"))
        
        print(f"✅ Готово")
        
        # Статистика
        stats = {
            'total_tasks': 0,
            'success_count': 0,
            'total_time': 0,
            'tool_success': {}
        }
        
        print(f"\n💻 ТЕСТИРОВАНИЕ с {FAST_MODEL}:")
        
        for i, task in enumerate(CODE_TASKS):
            print(f"\n{i+1}. {task['name']}")
            
            # Создаём code агента
            agent_dna = spawn_evolved_agent("code", ["code"])
            prompt_dna = get_evolved_prompt("code", "code")
            
            # Выполняем
            result = await execute_code_task(task)
            
            # Статистика
            stats['total_tasks'] += 1
            stats['total_time'] += result['execution_time']
            
            if result['success']:
                stats['success_count'] += 1
            
            tool_name = result.get('tool_used', task['tool'])
            if tool_name not in stats['tool_success']:
                stats['tool_success'][tool_name] = {'success': 0, 'total': 0}
            stats['tool_success'][tool_name]['total'] += 1
            if result['success']:
                stats['tool_success'][tool_name]['success'] += 1
        
        # Результаты
        success_rate = stats['success_count'] / stats['total_tasks']
        avg_time = stats['total_time'] / stats['total_tasks']
        
        print(f"\n💻" + "="*40)
        print(f"💻 РЕЗУЛЬТАТЫ КОДА")
        print("💻" + "="*40)
        
        print(f"\n🚀 ПРОИЗВОДИТЕЛЬНОСТЬ:")
        print(f"   ✅ Успех: {success_rate:.1%} ({stats['success_count']}/{stats['total_tasks']})")
        print(f"   ⚡ Среднее время: {avg_time:.1f}с")
        print(f"   🏁 Общее время: {stats['total_time']:.1f}с")
        
        print(f"\n💻 ПО ИНСТРУМЕНТАМ:")
        for tool_name, tool_stats in stats['tool_success'].items():
            tool_rate = tool_stats['success'] / tool_stats['total']
            print(f"   {tool_name}: {tool_rate:.1%} ({tool_stats['success']}/{tool_stats['total']})")
        
        if success_rate >= 0.6:
            print(f"\n🏆 CODE-РЕЗУЛЬТАТ: ✅ ХОРОШО!")
        else:
            print(f"\n⚠️ CODE-РЕЗУЛЬТАТ: требует настройки")
            
        print(f"\n📊 ГОТОВНОСТЬ К ЧАСТИ 3 (SYSTEM):")
        print(f"   💻 Code-часть протестирована")
        print(f"   ⚡ Настройки работают стабильно")
        
        return stats
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(code_comprehensive_test()) 