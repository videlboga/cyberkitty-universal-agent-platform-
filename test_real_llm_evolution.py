#!/usr/bin/env python3
"""
🧠 РЕАЛЬНЫЙ ТЕСТ САМОРЕДУПЛИЦИРУЮЩЕЙСЯ СИСТЕМЫ С LLM

Цель: Протестировать эволюцию агентов с реальными LLM вызовами
Принцип: "Настоящие агенты, настоящие задачи, настоящее обучение"
"""

import asyncio
import time
import json
import random
import os
from datetime import datetime
from pathlib import Path

# Настраиваем окружение для тестирования с бесплатными моделями
# Если нет API ключа в окружении - используем fallback
if not os.getenv("OPENROUTER_API_KEY"):
    # Пробуем реальный fallback - mock режим
    print("⚠️ OPENROUTER_API_KEY не найден - используем mock режим")
    os.environ["DEFAULT_MODEL"] = "mock"
else:
    # Используем лучшую бесплатную модель
    os.environ["DEFAULT_MODEL"] = "deepseek/deepseek-chat"  # Лучшая бесплатная модель с инструментами

os.environ["MAX_TOKENS"] = "100"  # Ограничиваем для быстрых тестов  
os.environ["TEMPERATURE"] = "0.1"  # Детерминированные ответы

# Настройка логирования  
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Реальные задачи для LLM агентов
REAL_TASKS = [
    {
        "type": "simple_math",
        "description": "Посчитай 15 * 7 + 23",
        "expected_pattern": "128",
        "complexity": "simple",
        "agent_type": "analysis"
    },
    {
        "type": "code_generation", 
        "description": "Напиши Python функцию для вычисления факториала числа",
        "expected_pattern": "def factorial",
        "complexity": "medium",
        "agent_type": "code"
    },
    {
        "type": "text_analysis",
        "description": "Определи настроение этого текста: 'Я очень расстроен и злюсь!'",
        "expected_pattern": "негативное",
        "complexity": "simple", 
        "agent_type": "analysis"
    },
    {
        "type": "problem_solving",
        "description": "У меня есть 100 рублей. Хлеб стоит 30 рублей, молоко 50 рублей. Сколько сдачи?",
        "expected_pattern": "20",
        "complexity": "medium",
        "agent_type": "analysis"
    },
    {
        "type": "creative_writing",
        "description": "Напиши короткий стих про кота (2 строчки)",
        "expected_pattern": "кот",
        "complexity": "medium",
        "agent_type": "creative"
    }
]

async def execute_real_llm_task(task, agent_dna, prompt_dna):
    """🧠 Выполнение реальной задачи через LLM"""
    
    print(f"   🤖 Агент {agent_dna.agent_id[:12]}... выполняет: {task['description']}")
    
    try:
        # Импорт реального LLM провайдера
        from kittycore.llm import get_llm_provider
        from kittycore.core.prompt_evolution import generate_prompt_text
        
        # Создаём LLM провайдера с конкретной моделью (не auto!)
        llm = get_llm_provider(model="deepseek/deepseek-chat")
        
        # Формируем промпт на основе эволюции
        base_prompt = generate_prompt_text(prompt_dna)
        evolved_prompt = f"""
{base_prompt}

Задача: {task['description']}

Ответь чётко и по делу. Дай конкретный результат.
"""
        
        start_time = time.time()
        
        # РЕАЛЬНЫЙ LLM ЗАПРОС!
        print(f"   🧠 LLM запрос... (промпт {len(evolved_prompt)} символов)")
        response = llm.complete(evolved_prompt)
        
        execution_time = time.time() - start_time
        
        # Анализируем ответ
        response_text = response.lower()
        expected_pattern = task['expected_pattern'].lower()
        
        # Проверяем успех
        success = expected_pattern in response_text
        
        # Оцениваем качество (длина ответа, релевантность)
        quality_score = min(1.0, len(response) / 100) if success else 0.0
        if success and len(response) > 10:
            quality_score = min(1.0, quality_score + 0.3)
            
        print(f"   📊 LLM ответ ({len(response)} символов): {response[:100]}...")
        print(f"   📊 Результат: {'✅ Успех' if success else '❌ Неудача'}")
        print(f"   📊 Качество: {quality_score:.2f}, Время: {execution_time:.1f}с")
        
        return {
            'success': success,
            'quality': quality_score,
            'execution_time': execution_time,
            'response': response,
            'response_length': len(response)
        }
        
    except Exception as e:
        print(f"   ❌ Ошибка LLM: {e}")
        return {
            'success': False,
            'quality': 0.0,
            'execution_time': 999.0,
            'response': f"Ошибка: {e}",
            'response_length': 0
        }

async def real_llm_evolution_test(cycles=3, tasks_per_cycle=2):
    """🧬 Реальный тест эволюции с LLM"""
    
    print("🧠" + "="*80)
    print("🧠 РЕАЛЬНЫЙ ТЕСТ САМОРЕДУПЛИЦИРУЮЩЕЙСЯ СИСТЕМЫ С LLM")
    print("🧠" + "="*80)
    
    try:
        # Импорт всех систем
        print("\n📦 Импорт эволюционных систем...")
        from kittycore.core.pheromone_memory import get_pheromone_system, record_agent_success
        from kittycore.core.evolutionary_factory import get_evolutionary_factory, spawn_evolved_agent, update_agent_evolution
        from kittycore.core.prompt_evolution import get_prompt_evolution_engine, get_evolved_prompt, record_prompt_usage
        
        # Инициализация хранилищ  
        test_dir = Path("./test_real_llm")
        test_dir.mkdir(exist_ok=True)
        
        pheromone_sys = get_pheromone_system()
        evolution_factory = get_evolutionary_factory(str(test_dir / "agents"))
        prompt_engine = get_prompt_evolution_engine(str(test_dir / "prompts"))
        
        print(f"✅ Системы инициализированы")
        
        # Статистика РЕАЛЬНОГО обучения
        real_stats = {
            'cycles_completed': 0,
            'total_tasks': 0,
            'total_successes': 0,
            'total_llm_calls': 0,
            'avg_response_time': 0,
            'generation_progress': [],
            'quality_progression': [],
            'llm_responses': []
        }
        
        # === ОСНОВНОЙ ЦИКЛ РЕАЛЬНОГО ОБУЧЕНИЯ ===
        for cycle in range(cycles):
            print(f"\n" + "🧠" + "-"*60)
            print(f"🧠 РЕАЛЬНЫЙ ЦИКЛ {cycle + 1}/{cycles}")
            print(f"🧠" + "-"*60)
            
            cycle_successes = 0
            cycle_quality_sum = 0
            cycle_time_sum = 0
            
            # Выполняем РЕАЛЬНЫЕ задачи
            for task_num in range(tasks_per_cycle):
                task = random.choice(REAL_TASKS)
                
                print(f"\n🎯 Реальная задача {task_num + 1}: {task['type']}")
                
                # Создаём эволюционного агента для задачи
                agent_dna = spawn_evolved_agent(task['agent_type'], [task['type']])
                prompt_dna = get_evolved_prompt(task['agent_type'], task['type'])
                
                # РЕАЛЬНОЕ выполнение с LLM
                result = await execute_real_llm_task(task, agent_dna, prompt_dna)
                
                # Записываем результаты в эволюционные системы
                record_agent_success(
                    task_type=task['type'],
                    solution_pattern=f"llm_{task['agent_type']}_pattern",
                    agent_combination=task['agent_type'],
                    tools_used=['llm_provider'],
                    success=result['success']
                )
                
                update_agent_evolution(agent_dna.agent_id, result['success'], result['execution_time'])
                record_prompt_usage(prompt_dna.prompt_id, task['type'], result['success'], result['quality'], result['execution_time'])
                
                # Накапливаем статистику
                if result['success']:
                    cycle_successes += 1
                cycle_quality_sum += result['quality']
                cycle_time_sum += result['execution_time']
                
                real_stats['total_llm_calls'] += 1
                real_stats['llm_responses'].append({
                    'task': task['type'],
                    'success': result['success'],
                    'quality': result['quality'],
                    'response_length': result['response_length'],
                    'time': result['execution_time']
                })
                
                # Пауза между LLM запросами
                await asyncio.sleep(1.0)
            
            # Статистика цикла
            cycle_success_rate = cycle_successes / tasks_per_cycle
            cycle_avg_quality = cycle_quality_sum / tasks_per_cycle
            cycle_avg_time = cycle_time_sum / tasks_per_cycle
            
            real_stats['cycles_completed'] += 1
            real_stats['total_tasks'] += tasks_per_cycle
            real_stats['total_successes'] += cycle_successes
            real_stats['quality_progression'].append(cycle_avg_quality)
            
            print(f"\n📊 РЕЗУЛЬТАТЫ ЦИКЛА {cycle + 1}:")
            print(f"   ✅ Успех: {cycle_success_rate:.1%} ({cycle_successes}/{tasks_per_cycle})")
            print(f"   📊 Качество: {cycle_avg_quality:.2f}")
            print(f"   ⏱️ Среднее время LLM: {cycle_avg_time:.1f}с")
            
            # Эволюция каждые 2 цикла
            if (cycle + 1) % 2 == 0:
                print(f"\n🧬 Запуск эволюции после цикла {cycle + 1}...")
                
                # Получаем статистику популяций
                pop_stats = evolution_factory.get_population_stats()
                prompt_stats = prompt_engine.get_population_stats()
                pheromone_stats = pheromone_sys.get_pheromone_statistics()
                pheromone_health = pheromone_stats.get('system_health', 0.0)
                
                real_stats['generation_progress'].append({
                    'cycle': cycle + 1,
                    'agents': pop_stats,
                    'prompts': prompt_stats,
                    'pheromones': pheromone_health
                })
                
                print(f"   🧬 Агенты: {pop_stats.active_agents} активных, поколение {pop_stats.max_generation}")
                print(f"   🧬 Промпты: {prompt_stats['population_size']} штук, успех {prompt_stats['avg_success']:.1%}")
                print(f"   🧬 Феромоны: здоровье {pheromone_health:.2f}")
        
        # === ФИНАЛЬНЫЙ АНАЛИЗ РЕАЛЬНОГО ОБУЧЕНИЯ ===
        print(f"\n" + "🎯" + "="*80)
        print(f"🎯 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ РЕАЛЬНОГО LLM ОБУЧЕНИЯ")
        print(f"🎯" + "="*80)
        
        overall_success = real_stats['total_successes'] / real_stats['total_tasks']
        avg_quality = sum(real_stats['quality_progression']) / len(real_stats['quality_progression'])
        total_llm_time = sum([r['time'] for r in real_stats['llm_responses']])
        
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   🎯 Всего задач: {real_stats['total_tasks']}")
        print(f"   ✅ Успешных: {real_stats['total_successes']} ({overall_success:.1%})")
        print(f"   📊 Среднее качество: {avg_quality:.2f}")
        print(f"   🧠 Всего LLM запросов: {real_stats['total_llm_calls']}")
        print(f"   ⏱️ Общее время LLM: {total_llm_time:.1f}с")
        
        # Анализ качества LLM ответов
        response_lengths = [r['response_length'] for r in real_stats['llm_responses']]
        successful_responses = [r for r in real_stats['llm_responses'] if r['success']]
        
        print(f"\n🧠 АНАЛИЗ LLM ОТВЕТОВ:")
        print(f"   📏 Средняя длина ответа: {sum(response_lengths)/len(response_lengths):.0f} символов")
        print(f"   ✅ Успешные ответы: {len(successful_responses)}/{len(real_stats['llm_responses'])}")
        
        if successful_responses:
            avg_success_length = sum([r['response_length'] for r in successful_responses]) / len(successful_responses)
            avg_success_quality = sum([r['quality'] for r in successful_responses]) / len(successful_responses)
            print(f"   🎯 Качество успешных: {avg_success_quality:.2f}")
            print(f"   📏 Длина успешных: {avg_success_length:.0f} символов")
        
        # Сохраняем результаты
        results_file = test_dir / "real_llm_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(real_stats, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 Результаты сохранены: {results_file}")
        
        # Итоговая оценка
        if overall_success >= 0.7:
            grade = "🏆 ОТЛИЧНО"
        elif overall_success >= 0.5:
            grade = "✅ ХОРОШО" 
        elif overall_success >= 0.3:
            grade = "⚠️ УДОВЛЕТВОРИТЕЛЬНО"
        else:
            grade = "❌ НЕУДОВЛЕТВОРИТЕЛЬНО"
            
        print(f"\n🎓 ИТОГОВАЯ ОЦЕНКА: {grade}")
        print(f"🎓 Система {'РАБОТАЕТ с реальными LLM!' if overall_success > 0.3 else 'требует доработки'}")
        
        return real_stats
        
    except Exception as e:
        print(f"❌ Критическая ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """🚀 Запуск реального теста"""
    
    print("🚀 Запуск РЕАЛЬНОГО теста саморедуплицирующейся системы с LLM")
    print("🧠 Будут выполнены настоящие LLM запросы!")
    
    # Запускаем реальный тест
    results = await real_llm_evolution_test(cycles=3, tasks_per_cycle=3)
    
    if results:
        print(f"\n🎉 Реальный тест завершён успешно!")
        print(f"🎉 Система прошла {results['total_tasks']} реальных LLM задач")
    else:
        print(f"\n💥 Реальный тест не удался")

if __name__ == "__main__":
    asyncio.run(main()) 