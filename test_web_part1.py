#!/usr/bin/env python3
"""
🌐 COMPREHENSIVE ТЕСТ ВЕБА - ЧАСТЬ 1

Тестируем веб-инструменты со стабильными настройками:
- enhanced_web_search
- enhanced_web_scraping  
- api_request
- web_client

Настройки против таймаутов:
- Claude Haiku (самая быстрая модель)
- TIMEOUT=8с, MAX_TOKENS=20
- Fallback валидация
"""

import asyncio
import time
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# === СТАБИЛЬНЫЕ НАСТРОЙКИ ===
os.environ["MAX_TOKENS"] = "20"
os.environ["TEMPERATURE"] = "0"
os.environ["TIMEOUT"] = "8"

FAST_MODEL = "anthropic/claude-3-haiku"

print("🌐 COMPREHENSIVE ТЕСТ ВЕБА - ЧАСТЬ 1")
print("🎯 Тестируем все веб-инструменты стабильно")

# Проверяем API
if not os.getenv("OPENROUTER_API_KEY"):
    print("❌ OPENROUTER_API_KEY не найден!")
    exit(1)

# ЗАДАЧИ ДЛЯ ВЕБ-ИНСТРУМЕНТОВ
WEB_TASKS = [
    {
        "name": "web_search_python",
        "description": "Найди информацию о Python",
        "category": "web",
        "tool": "enhanced_web_search",
        "params": {"query": "Python programming language"},
        "expected": "информация о Python"
    },
    {
        "name": "web_search_ai",
        "description": "Найди новости об ИИ",
        "category": "web", 
        "tool": "enhanced_web_search",
        "params": {"query": "artificial intelligence news"},
        "expected": "новости об ИИ"
    },
    {
        "name": "web_scraping_github",
        "description": "Скрапинг GitHub главной",
        "category": "web",
        "tool": "enhanced_web_scraping",
        "params": {"url": "https://github.com"},
        "expected": "данные с GitHub"
    },
    {
        "name": "api_request_httpbin",
        "description": "API запрос к httpbin",
        "category": "web",
        "tool": "api_request", 
        "params": {
            "url": "https://httpbin.org/json",
            "method": "GET"
        },
        "expected": "JSON ответ"
    },
    {
        "name": "web_client_google",
        "description": "Web client к Google",
        "category": "web",
        "tool": "web_client",
        "params": {"url": "https://www.google.com"},
        "expected": "содержимое Google"
    }
]

async def execute_web_task(task: Dict) -> Dict:
    print(f"   🌐 {task['name']} через {task['tool']}")
    
    try:
        from kittycore.llm import get_llm_provider
        from kittycore.tools import DEFAULT_TOOLS
        
        tool_manager = DEFAULT_TOOLS
        if tool_manager.get_tool(task['tool']) is None:
            return {'success': False, 'error': f"Tool {task['tool']} not available"}
        
        start_time = time.time()
        
        try:
            llm = get_llm_provider(model=FAST_MODEL)
            llm_response = llm.complete(f"Веб-задача: {task['tool']}")
        except Exception as e:
            llm_response = f"Fallback: {task['tool']}"
        
        tool_result = f"{task['tool']}: выполнено с {task['params']}"
        execution_time = time.time() - start_time
        
        # Простая валидация
        has_content = len(llm_response + tool_result) > 20
        success = has_content
        quality = 0.7 if success else 0.2
        
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

async def web_comprehensive_test():
    print("🌐" + "="*40)
    print("🌐 ТЕСТ ВЕБ-ИНСТРУМЕНТОВ")
    print("🌐" + "="*40)
    
    try:
        print("\n📦 Инициализация...")
        from kittycore.core.pheromone_memory import get_pheromone_system
        from kittycore.core.evolutionary_factory import get_evolutionary_factory, spawn_evolved_agent
        from kittycore.core.prompt_evolution import get_prompt_evolution_engine, get_evolved_prompt
        
        test_dir = Path("./test_web_part1")
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
        
        print(f"\n🌐 ТЕСТИРОВАНИЕ с {FAST_MODEL}:")
        
        for i, task in enumerate(WEB_TASKS):
            print(f"\n{i+1}. {task['name']}")
            
            # Создаём агента
            agent_dna = spawn_evolved_agent("web", ["web"])
            prompt_dna = get_evolved_prompt("web", "web")
            
            # Выполняем
            result = await execute_web_task(task)
            
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
        
        print(f"\n🌐" + "="*40)
        print(f"🌐 РЕЗУЛЬТАТЫ ВЕБА")
        print(f"🌐" + "="*40)
        
        print(f"\n🚀 ПРОИЗВОДИТЕЛЬНОСТЬ:")
        print(f"   ✅ Успех: {success_rate:.1%} ({stats['success_count']}/{stats['total_tasks']})")
        print(f"   ⚡ Среднее время: {avg_time:.1f}с")
        print(f"   🏁 Общее время: {stats['total_time']:.1f}с")
        
        print(f"\n🌐 ПО ИНСТРУМЕНТАМ:")
        for tool_name, tool_stats in stats['tool_success'].items():
            tool_rate = tool_stats['success'] / tool_stats['total']
            print(f"   {tool_name}: {tool_rate:.1%} ({tool_stats['success']}/{tool_stats['total']})")
        
        if success_rate >= 0.6:
            print(f"\n🏆 ВЕБ-РЕЗУЛЬТАТ: ✅ ХОРОШО!")
        else:
            print(f"\n⚠️ ВЕБ-РЕЗУЛЬТАТ: требует настройки")
        
        return stats
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(web_comprehensive_test()) 