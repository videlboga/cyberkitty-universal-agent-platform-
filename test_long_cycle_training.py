#!/usr/bin/env python3
"""
🔄 Тест долгосрочного обучения саморедуплицирующейся системы

Цель: Тренировка системы на реальных задачах с использованием инструментов
Принцип: "Система учится через многократные циклы реальной работы"
"""

import asyncio
import time
import random
from datetime import datetime
from pathlib import Path

# Настройка логирования
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Реальные задачи для тренировки
TRAINING_TASKS = [
    {
        "type": "code_analysis",
        "description": "Анализ Python кода на ошибки",
        "tools": ["code_execution", "document_tool"],
        "complexity": "medium"
    },
    {
        "type": "web_research", 
        "description": "Поиск информации о технологиях",
        "tools": ["enhanced_web_search", "document_tool"],
        "complexity": "simple"
    },
    {
        "type": "data_processing",
        "description": "Обработка CSV данных",
        "tools": ["data_analysis_tool", "document_tool"],
        "complexity": "medium"
    },
    {
        "type": "system_check",
        "description": "Проверка системных ресурсов",
        "tools": ["super_system_tool", "document_tool"], 
        "complexity": "simple"
    },
    {
        "type": "security_audit",
        "description": "Базовая проверка безопасности",
        "tools": ["security_tool", "document_tool"],
        "complexity": "complex"
    }
]

async def simulate_task_execution(task, agent_dna, prompt_dna):
    """🎯 Симуляция выполнения задачи с реальными инструментами"""
    
    print(f"   🤖 Агент {agent_dna.agent_id} выполняет: {task['description']}")
    print(f"   🛠️ Инструменты: {', '.join(task['tools'])}")
    
    start_time = time.time()
    
    # Симулируем использование инструментов
    tool_success = {}
    overall_success = True
    
    for tool_name in task['tools']:
        # Базируем успех на генетике агента + случайность
        tool_efficiency = agent_dna.genes.tool_efficiency.get(tool_name, 0.5)
        success_chance = (tool_efficiency + agent_dna.genes.success_rate) / 2
        
        # Добавляем реалистичную случайность
        actual_success = random.random() < success_chance
        tool_success[tool_name] = actual_success
        
        if not actual_success:
            overall_success = False
        
        print(f"      🔧 {tool_name}: {'✅' if actual_success else '❌'}")
    
    # Время выполнения зависит от сложности и скорости агента
    complexity_multiplier = {"simple": 1.0, "medium": 1.5, "complex": 2.0}
    base_time = complexity_multiplier.get(task['complexity'], 1.0) * 10
    execution_time = base_time / agent_dna.genes.speed_factor
    
    # Качество зависит от успеха инструментов и качественного фактора
    tool_success_rate = sum(tool_success.values()) / len(tool_success)
    quality_score = tool_success_rate * agent_dna.genes.quality_factor
    
    end_time = time.time()
    
    print(f"   📊 Результат: {'✅ Успех' if overall_success else '❌ Неудача'}")
    print(f"   📊 Качество: {quality_score:.2f}, Время: {execution_time:.1f}с")
    print(f"   📊 Успех инструментов: {tool_success_rate:.1%}")
    
    return {
        'success': overall_success,
        'quality': quality_score,
        'execution_time': execution_time,
        'tool_success': tool_success,
        'tool_success_rate': tool_success_rate
    }

async def long_cycle_training(cycles=10, tasks_per_cycle=5):
    """🔄 Долгосрочный цикл обучения системы"""
    
    print("🧬" + "="*80)
    print("🧬 ДОЛГОСРОЧНЫЙ ЦИКЛ ОБУЧЕНИЯ САМОРЕДУПЛИЦИРУЮЩЕЙСЯ СИСТЕМЫ")
    print("🧬" + "="*80)
    
    try:
        # Импорт всех систем
        print("\n📦 Импорт систем...")
        from kittycore.core.pheromone_memory import get_pheromone_system, record_agent_success
        from kittycore.core.evolutionary_factory import get_evolutionary_factory, spawn_evolved_agent, update_agent_evolution
        from kittycore.core.prompt_evolution import get_prompt_evolution_engine, get_evolved_prompt, record_prompt_usage
        
        # Инициализация
        pheromone_sys = get_pheromone_system()
        evolution_factory = get_evolutionary_factory("./long_training/agents")
        prompt_engine = get_prompt_evolution_engine("./long_training/prompts")
        
        print(f"✅ Системы инициализированы")
        
        # Статистика обучения
        training_stats = {
            'cycles_completed': 0,
            'total_tasks': 0,
            'total_successes': 0,
            'tool_stats': {},
            'generation_progress': [],
            'quality_progression': []
        }
        
        # === ОСНОВНОЙ ЦИКЛ ОБУЧЕНИЯ ===
        for cycle in range(cycles):
            print(f"\n" + "🔄" + "-"*60)
            print(f"🔄 ЦИКЛ ОБУЧЕНИЯ {cycle + 1}/{cycles}")
            print(f"🔄" + "-"*60)
            
            cycle_results = []
            cycle_successes = 0
            cycle_quality_sum = 0
            
            # Выполняем задачи в цикле
            for task_num in range(tasks_per_cycle):
                # Выбираем случайную задачу
                task = random.choice(TRAINING_TASKS)
                
                print(f"\n🎯 Задача {task_num + 1}/{tasks_per_cycle}: {task['type']}")
                
                # Определяем тип агента для задачи
                agent_type_mapping = {
                    "code_analysis": "code",
                    "web_research": "web", 
                    "data_processing": "analysis",
                    "system_check": "general",
                    "security_audit": "analysis"
                }
                
                agent_type = agent_type_mapping.get(task['type'], 'general')
                
                # Создаём/получаем эволюционного агента
                agent_dna = spawn_evolved_agent(agent_type, [task['type']])
                prompt_dna = get_evolved_prompt(agent_type, task['type'])
                
                # Выполняем задачу
                result = await simulate_task_execution(task, agent_dna, prompt_dna)
                
                # Записываем результаты во все системы
                record_agent_success(
                    task_type=task['type'],
                    solution_pattern=f"{agent_type}_{task['type']}_pattern",
                    agent_combination=agent_type,
                    tools_used=task['tools'],
                    success=result['success']
                )
                
                update_agent_evolution(agent_dna.agent_id, result['success'], result['execution_time'])
                record_prompt_usage(prompt_dna.prompt_id, task['type'], result['success'], result['quality'], result['execution_time'])
                
                # Статистика
                cycle_results.append(result)
                if result['success']:
                    cycle_successes += 1
                cycle_quality_sum += result['quality']
                
                # Статистика инструментов
                for tool, success in result['tool_success'].items():
                    if tool not in training_stats['tool_stats']:
                        training_stats['tool_stats'][tool] = {'used': 0, 'successful': 0}
                    training_stats['tool_stats'][tool]['used'] += 1
                    if success:
                        training_stats['tool_stats'][tool]['successful'] += 1
                
                # Небольшая пауза
                await asyncio.sleep(0.1)
            
            # Статистика цикла
            cycle_success_rate = cycle_successes / tasks_per_cycle
            cycle_avg_quality = cycle_quality_sum / tasks_per_cycle
            
            print(f"\n📊 РЕЗУЛЬТАТЫ ЦИКЛА {cycle + 1}:")
            print(f"   ✅ Успешность: {cycle_success_rate:.1%} ({cycle_successes}/{tasks_per_cycle})")
            print(f"   ⭐ Среднее качество: {cycle_avg_quality:.2f}")
            
            # Обновляем общую статистику
            training_stats['cycles_completed'] = cycle + 1
            training_stats['total_tasks'] += tasks_per_cycle
            training_stats['total_successes'] += cycle_successes
            
            # Запускаем эволюцию каждые 3 цикла
            if (cycle + 1) % 3 == 0:
                print(f"   🧬 Запуск эволюции после {cycle + 1} циклов...")
                
                evolution_factory.evolve_population(force_evolution=True)
                prompt_engine.evolve_prompts()
                pheromone_sys.evaporate_pheromones()
                
                # Получаем статистику после эволюции
                evolution_stats = evolution_factory.get_population_stats()
                training_stats['generation_progress'].append({
                    'cycle': cycle + 1,
                    'max_generation': evolution_stats.max_generation,
                    'population_health': evolution_stats.population_health,
                    'success_rate': cycle_success_rate,
                    'avg_quality': cycle_avg_quality
                })
                
                print(f"   📈 Поколение: {evolution_stats.max_generation}, Здоровье: {evolution_stats.population_health:.2f}")
            
            training_stats['quality_progression'].append(cycle_avg_quality)
        
        return training_stats
        
    except Exception as e:
        print(f"❌ ОШИБКА В ОБУЧЕНИИ: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_training_results(stats):
    """📊 Анализ результатов долгосрочного обучения"""
    
    print("\n" + "📊" + "="*80)
    print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ ДОЛГОСРОЧНОГО ОБУЧЕНИЯ")
    print("📊" + "="*80)
    
    if not stats:
        print("❌ Нет данных для анализа")
        return
    
    # Общая статистика
    overall_success_rate = stats['total_successes'] / stats['total_tasks']
    print(f"\n🎯 ОБЩИЕ РЕЗУЛЬТАТЫ:")
    print(f"   🔄 Циклов завершено: {stats['cycles_completed']}")
    print(f"   📋 Всего задач: {stats['total_tasks']}")
    print(f"   ✅ Общая успешность: {overall_success_rate:.1%} ({stats['total_successes']}/{stats['total_tasks']})")
    
    # Прогресс качества
    if stats['quality_progression']:
        initial_quality = stats['quality_progression'][0]
        final_quality = stats['quality_progression'][-1]
        quality_improvement = final_quality - initial_quality
        
        print(f"\n📈 ПРОГРЕСС КАЧЕСТВА:")
        print(f"   🌱 Начальное качество: {initial_quality:.2f}")
        print(f"   🎯 Финальное качество: {final_quality:.2f}")
        print(f"   📊 Улучшение: {quality_improvement:+.2f} ({(quality_improvement/initial_quality)*100:+.1f}%)")
    
    # Статистика инструментов
    print(f"\n🛠️ ИСПОЛЬЗОВАНИЕ ИНСТРУМЕНТОВ:")
    tool_success_rates = {}
    for tool, data in stats['tool_stats'].items():
        success_rate = data['successful'] / data['used'] if data['used'] > 0 else 0
        tool_success_rates[tool] = success_rate
        print(f"   🔧 {tool}: {success_rate:.1%} ({data['successful']}/{data['used']})")
    
    # Лучшие и худшие инструменты
    if tool_success_rates:
        best_tool = max(tool_success_rates.items(), key=lambda x: x[1])
        worst_tool = min(tool_success_rates.items(), key=lambda x: x[1])
        
        print(f"\n🏆 ЛУЧШИЙ ИНСТРУМЕНТ: {best_tool[0]} ({best_tool[1]:.1%} успех)")
        print(f"⚠️ ХУДШИЙ ИНСТРУМЕНТ: {worst_tool[0]} ({worst_tool[1]:.1%} успех)")
    
    # Прогресс эволюции
    if stats['generation_progress']:
        print(f"\n🧬 ЭВОЛЮЦИОННЫЙ ПРОГРЕСС:")
        for i, progress in enumerate(stats['generation_progress']):
            print(f"   📊 Цикл {progress['cycle']}: поколение {progress['max_generation']}, "
                  f"здоровье {progress['population_health']:.2f}, "
                  f"успех {progress['success_rate']:.1%}")
    
    # Итоговая оценка
    if overall_success_rate >= 0.8:
        grade = "🏆 ОТЛИЧНО"
        status = "Система превосходно обучена!"
    elif overall_success_rate >= 0.6:
        grade = "✅ ХОРОШО" 
        status = "Система хорошо обучена"
    elif overall_success_rate >= 0.4:
        grade = "⚠️ УДОВЛЕТВОРИТЕЛЬНО"
        status = "Система требует дополнительного обучения"
    else:
        grade = "❌ НЕУДОВЛЕТВОРИТЕЛЬНО"
        status = "Система нуждается в серьёзной доработке"
    
    print(f"\n🎖️ ИТОГОВАЯ ОЦЕНКА: {grade}")
    print(f"📝 СТАТУС: {status}")
    print(f"🎯 Общий балл: {overall_success_rate:.1%}")
    
    return {
        'grade': grade,
        'overall_success_rate': overall_success_rate,
        'quality_improvement': quality_improvement if stats['quality_progression'] else 0,
        'best_tool': best_tool[0] if tool_success_rates else None,
        'worst_tool': worst_tool[0] if tool_success_rates else None
    }

async def main():
    """🚀 Основная функция запуска долгосрочного обучения"""
    
    print("🔄 Запуск долгосрочного обучения саморедуплицирующейся системы...")
    
    # Создаём директорию для обучения
    training_dir = Path("./long_training")
    training_dir.mkdir(exist_ok=True)
    
    # Запускаем обучение (начнём с малого - 6 циклов по 3 задачи)
    print("📋 Конфигурация: 6 циклов по 3 задачи = 18 задач")
    print("🧬 Эволюция каждые 3 цикла")
    
    stats = await long_cycle_training(cycles=6, tasks_per_cycle=3)
    
    if stats:
        analysis = analyze_training_results(stats)
        print(f"\n✅ ОБУЧЕНИЕ ЗАВЕРШЕНО: {analysis['grade']}")
    else:
        print("\n❌ Обучение завершилось с ошибками!")

if __name__ == "__main__":
    print("🔄 Базовая структура теста долгосрочного обучения создана!")
    print(f"📋 Подготовлено {len(TRAINING_TASKS)} типов задач для тренировки")
    
    # Запускаем обучение
    asyncio.run(main()) 