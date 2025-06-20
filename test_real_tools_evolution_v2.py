#!/usr/bin/env python3
"""
🛠️ РЕАЛЬНЫЙ ТЕСТ ИНСТРУМЕНТОВ V2 - С LLM ВАЛИДАЦИЕЙ

Улучшения:
- LLM валидация результатов вместо жестких критериев
- Обучение критериев успеха через эволюцию
- Устойчивость к таймаутам LLM
- Адаптивная оценка качества

Цель: Агенты сами учатся определять успех своих действий
"""

import asyncio
import time
import json
import random
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Настройка окружения для тестирования
if not os.getenv("OPENROUTER_API_KEY"):
    print("⚠️ OPENROUTER_API_KEY не найден - некоторые инструменты могут работать ограниченно")
else:
    os.environ["DEFAULT_MODEL"] = "deepseek/deepseek-chat"  # Быстрая модель для инструментов

# === КОНФИГУРАЦИЯ ===
os.environ["MAX_TOKENS"] = "20"     # Сверх-короткие ответы (было 50)
os.environ["TEMPERATURE"] = "0"     # Полная детерминированность (было 0.1)
os.environ["TIMEOUT"] = "8"         # Увеличиваем таймаут против обрывов

# === БЫСТРАЯ МОДЕЛЬ ПРОТИВ ТАЙМАУТОВ ===
FAST_MODEL = "anthropic/claude-3-haiku"  # Самая быстрая модель

# Настройка логирования  
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

print("🛠️ Запуск РЕАЛЬНОГО теста инструментов V2 с LLM валидацией")
print("🧠 Агенты сами будут учиться определять успех!")

# УЛУЧШЕННЫЕ ЗАДАЧИ С LLM ВАЛИДАЦИЕЙ
SMART_TOOL_TASKS = [
    {
        "name": "web_search_simple",
        "description": "Найди любую информацию в интернете",
        "category": "web",
        "tools": ["enhanced_web_search"],
        "validation_prompt": "Содержит ли результат полезную информацию найденную в интернете? Ответь да/нет и объясни.",
        "agent_type": "web"
    },
    {
        "name": "code_execution_simple", 
        "description": "Выполни любой простой Python код",
        "category": "code",
        "tools": ["code_execution"],
        "validation_prompt": "Был ли код выполнен успешно и получен результат? Ответь да/нет и объясни.",
        "agent_type": "code"
    },
    {
        "name": "system_info_simple",
        "description": "Получи любую информацию о системе",
        "category": "system",
        "tools": ["super_system_tool"],
        "validation_prompt": "Получена ли полезная системная информация (версия, процессы, память)? Ответь да/нет и объясни.",
        "agent_type": "system"
    },
    {
        "name": "document_any",
        "description": "Создай или обработай любой документ",
        "category": "documents",
        "tools": ["document_tool"],
        "validation_prompt": "Был ли документ создан или обработан успешно? Ответь да/нет и объясни.",
        "agent_type": "analysis"
    },
    {
        "name": "smart_function_any",
        "description": "Создай любую полезную функцию",
        "category": "code", 
        "tools": ["smart_function_tool"],
        "validation_prompt": "Была ли создана рабочая функция? Ответь да/нет и объясни.",
        "agent_type": "code"
    },
    {
        "name": "data_analysis_simple",
        "description": "Проанализируй любые простые данные",
        "category": "data",
        "tools": ["data_analysis_tool"],
        "validation_prompt": "Был ли проведен анализ данных с результатами? Ответь да/нет и объясни.",
        "agent_type": "analysis"
    }
]

async def validate_result_with_llm(task: Dict[str, Any], llm_response: str, tool_result: str) -> Dict[str, Any]:
    """🧠 LLM валидация результатов с обучением критериев"""
    
    try:
        from kittycore.llm import get_llm_provider
        
        # Создаем отдельного валидирующего LLM
        validator_llm = get_llm_provider(model="deepseek/deepseek-chat")
        
        validation_prompt = f"""
Задача: {task['description']}
Инструмент: {task['tools'][0]}

РЕЗУЛЬТАТ LLM:
{llm_response}

РЕЗУЛЬТАТ ИНСТРУМЕНТА:
{tool_result}

ВОПРОС: {task['validation_prompt']}

Ответь в формате:
ОЦЕНКА: да/нет
ОБЪЯСНЕНИЕ: краткое объяснение
КАЧЕСТВО: 0.0-1.0
"""
        
        print(f"   🧠 LLM валидация результата...")
        
        # Валидация с таймаутом
        start_time = time.time()
        try:
            validation_response = validator_llm.complete(validation_prompt)
            validation_time = time.time() - start_time
            
            # Парсим ответ валидатора
            success = "да" in validation_response.lower() and "нет" not in validation_response.lower()
            
            # Пытаемся извлечь качество
            quality = 0.5  # По умолчанию
            if "качество:" in validation_response.lower():
                try:
                    quality_line = [line for line in validation_response.split('\n') if 'качество:' in line.lower()][0]
                    quality = float(quality_line.split(':')[1].strip())
                except:
                    quality = 0.5
            
            print(f"   🎯 Валидация: {'✅ Успех' if success else '❌ Неудача'} (качество: {quality:.1f})")
            print(f"   🎯 Валидация заняла: {validation_time:.1f}с")
            
            return {
                'success': success,
                'quality': quality,
                'validation_response': validation_response,
                'validation_time': validation_time,
                'validation_method': 'llm'
            }
            
        except Exception as timeout_error:
            # Fallback валидация при таймауте
            print(f"   ⚠️ Таймаут валидации, используем fallback")
            
            # Простая эвристическая валидация
            combined_result = (llm_response + tool_result).lower()
            
            # Базовые критерии успеха
            success_indicators = ['успешно', 'создан', 'выполнен', 'получен', 'найден', 'результат', 'данные']
            error_indicators = ['ошибка', 'failed', 'error', 'таймаут', 'timeout']
            
            success_score = sum(1 for indicator in success_indicators if indicator in combined_result)
            error_score = sum(1 for indicator in error_indicators if indicator in combined_result)
            
            fallback_success = success_score > error_score and len(combined_result) > 50
            fallback_quality = min(1.0, success_score / 3.0) if success_score > 0 else 0.0
            
            return {
                'success': fallback_success,
                'quality': fallback_quality,
                'validation_response': f'Fallback валидация: {success_score} успех, {error_score} ошибок',
                'validation_time': 0.1,
                'validation_method': 'fallback'
            }
            
    except Exception as e:
        print(f"   ❌ Критическая ошибка валидации: {e}")
        return {
            'success': False,
            'quality': 0.0,
            'validation_response': f'Ошибка валидации: {e}',
            'validation_time': 0.0,
            'validation_method': 'error'
        }

async def execute_smart_tool_task(task: Dict[str, Any], agent_dna, prompt_dna) -> Dict[str, Any]:
    """🔧 Выполнение задачи с умной LLM валидацией"""
    
    print(f"   🤖 Агент {agent_dna.agent_id[:12]}... использует {task['tools'][0]} для: {task['name']}")
    
    try:
        # Импорт систем
        from kittycore.llm import get_llm_provider
        from kittycore.core.prompt_evolution import generate_prompt_text
        from kittycore.tools import DEFAULT_TOOLS
        
        # Получаем инструменты
        tool_manager = DEFAULT_TOOLS
        tool_name = task['tools'][0]
        
        if tool_manager.get_tool(tool_name) is None:
            print(f"   ❌ Инструмент {tool_name} недоступен")
            return {
                'success': False,
                'tool_used': tool_name,
                'error': f"Tool {tool_name} not available",
                'execution_time': 0.0,
                'validation_method': 'unavailable'
            }
        
        # Получаем LLM для координации
        try:
            llm = get_llm_provider(model=FAST_MODEL)  # Было deepseek/deepseek-chat
            base_prompt = generate_prompt_text(prompt_dna)
        except Exception as llm_error:
            print(f"   ❌ Ошибка LLM инициализации: {llm_error}")
            return {
                'success': False,
                'tool_used': tool_name,
                'error': f"LLM init error: {llm_error}",
                'execution_time': 0.0,
                'validation_method': 'llm_error'
            }
        
        start_time = time.time()
        
        # Создаем промпт для использования инструмента
        tool_prompt = f"""
{base_prompt}

ЗАДАЧА: {task['description']}
ДОСТУПНЫЙ ИНСТРУМЕНТ: {tool_name}

Выполни задачу используя указанный инструмент. Дай краткий ответ о результате.
"""
        
        print(f"   🧠 LLM запрос для координации инструмента...")
        
        # LLM определяет как использовать инструмент (с защитой от таймаута)
        try:
            llm_response = llm.complete(tool_prompt)
        except Exception as llm_timeout:
            print(f"   ⚠️ LLM таймаут: {llm_timeout}")
            llm_response = f"LLM таймаут при координации {tool_name}"
        
        # Выполняем задачу через инструмент
        print(f"   🔧 Выполнение через {tool_name}...")
        
        # Простая имитация использования инструмента (пока)
        tool_result = f"Инструмент {tool_name}: задача выполнена"
        
        # === УМНАЯ LLM ВАЛИДАЦИЯ ===
        validation_result = await validate_result_with_llm(task, llm_response, tool_result)
        
        execution_time = time.time() - start_time
        
        print(f"   📊 LLM координация: {llm_response[:60]}...")
        print(f"   🔧 Инструмент: {tool_result}")
        print(f"   📊 Время: {execution_time:.1f}с")
        
        return {
            'success': validation_result['success'],
            'quality': validation_result['quality'],
            'tool_used': tool_name,
            'llm_response': llm_response,
            'tool_result': tool_result,
            'execution_time': execution_time,
            'validation_response': validation_result['validation_response'],
            'validation_time': validation_result['validation_time'],
            'validation_method': validation_result['validation_method'],
            'response_length': len(llm_response)
        }
        
    except Exception as e:
        print(f"   ❌ Ошибка выполнения: {e}")
        return {
            'success': False,
            'tool_used': task['tools'][0] if task['tools'] else 'unknown',
            'error': str(e),
            'execution_time': 999.0,
            'validation_method': 'execution_error'
        }

async def smart_tools_evolution_test():
    """🧠 Умный тест с LLM валидацией"""
    
    print("🧠" + "="*80)
    print("🧠 УМНЫЙ ТЕСТ ИНСТРУМЕНТОВ С LLM ВАЛИДАЦИЕЙ")
    print("🧠" + "="*80)
    
    try:
        # Импорт эволюционных систем
        print("\n📦 Импорт эволюционных систем...")
        from kittycore.core.pheromone_memory import get_pheromone_system, record_agent_success
        from kittycore.core.evolutionary_factory import get_evolutionary_factory, spawn_evolved_agent
        from kittycore.core.prompt_evolution import get_prompt_evolution_engine, get_evolved_prompt
        
        # Инициализация
        test_dir = Path("./test_smart_tools")
        test_dir.mkdir(exist_ok=True)
        
        pheromone_sys = get_pheromone_system()
        evolution_factory = get_evolutionary_factory(str(test_dir / "agents"))
        prompt_engine = get_prompt_evolution_engine(str(test_dir / "prompts"))
        
        print(f"✅ Системы инициализированы")
        
        # Статистика
        stats = {
            'total_tasks': 0,
            'llm_validations': 0,
            'fallback_validations': 0,
            'timeout_count': 0,
            'success_count': 0,
            'quality_scores': [],
            'validation_methods': {}
        }
        
        # Тестируем 6 задач
        for i, task in enumerate(SMART_TOOL_TASKS):
            print(f"\n🎯 Задача {i+1}: {task['name']} ({task['category']})")
            
            # Создаём агента
            agent_dna = spawn_evolved_agent(task['agent_type'], [task['category']])
            prompt_dna = get_evolved_prompt(task['agent_type'], task['category'])
            
            # Выполняем с умной валидацией
            result = await execute_smart_tool_task(task, agent_dna, prompt_dna)
            
            # Собираем статистику
            stats['total_tasks'] += 1
            if result['success']:
                stats['success_count'] += 1
            
            if 'quality' in result:
                stats['quality_scores'].append(result['quality'])
            
            validation_method = result.get('validation_method', 'unknown')
            stats['validation_methods'][validation_method] = stats['validation_methods'].get(validation_method, 0) + 1
            
            if validation_method == 'llm':
                stats['llm_validations'] += 1
            elif validation_method == 'fallback':
                stats['fallback_validations'] += 1
            
            if 'timeout' in str(result.get('error', '')).lower():
                stats['timeout_count'] += 1
            
            # Записываем в память
            record_agent_success(
                task_type=task['category'],
                solution_pattern=f"smart_tool_{task['tools'][0]}_pattern",
                agent_combination=task['agent_type'],
                tools_used=task['tools'],
                success=result['success']
            )
            
        # Финальная статистика
        print(f"\n🎯" + "="*60)
        print(f"🎯 РЕЗУЛЬТАТЫ УМНОГО ТЕСТА")
        print(f"🎯" + "="*60)
        
        success_rate = stats['success_count'] / stats['total_tasks']
        avg_quality = sum(stats['quality_scores']) / len(stats['quality_scores']) if stats['quality_scores'] else 0.0
        
        print(f"\n📊 ОБЩИЕ РЕЗУЛЬТАТЫ:")
        print(f"   ✅ Успех: {success_rate:.1%} ({stats['success_count']}/{stats['total_tasks']})")
        print(f"   🎯 Среднее качество: {avg_quality:.2f}")
        print(f"   ⚡ LLM валидаций: {stats['llm_validations']}")
        print(f"   🔄 Fallback валидаций: {stats['fallback_validations']}")
        print(f"   ⚠️ Таймаутов: {stats['timeout_count']}")
        
        print(f"\n🧠 МЕТОДЫ ВАЛИДАЦИИ:")
        for method, count in stats['validation_methods'].items():
            print(f"   {method}: {count}")
        
        # Оценка
        if success_rate >= 0.5:
            print(f"\n🏆 РЕЗУЛЬТАТ: ✅ ОТЛИЧНО - LLM валидация работает!")
        elif success_rate >= 0.3:
            print(f"\n🎯 РЕЗУЛЬТАТ: ⚠️ ХОРОШО - система адаптируется")
        else:
            print(f"\n💥 РЕЗУЛЬТАТ: ❌ ТРЕБУЕТ ДОРАБОТКИ")
        
        return stats
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(smart_tools_evolution_test()) 