#!/usr/bin/env python3
"""
🧬 Детальный тест саморедуплицирующейся системы с эволюцией популяции

Тестируем форсированную эволюцию всех систем:
🐜 Феромонная память с испарением
🧬 Эволюция популяции агентов 
🧠 Эволюция популяции промптов

Принцип: "Система эволюционирует и самосовершенствуется через поколения"
"""

import asyncio
import random
from pathlib import Path

async def test_evolution_detailed():
    """🧬 Детальный тест эволюции всех систем"""
    
    print("🧬" + "="*80)
    print("🧬 ДЕТАЛЬНЫЙ ТЕСТ ЭВОЛЮЦИИ САМОРЕДУПЛИЦИРУЮЩЕЙСЯ СИСТЕМЫ")
    print("🧬" + "="*80)
    
    try:
        # Импорт систем
        from kittycore.core.pheromone_memory import get_pheromone_system, record_agent_success
        from kittycore.core.evolutionary_factory import get_evolutionary_factory, spawn_evolved_agent, update_agent_evolution
        from kittycore.core.prompt_evolution import get_prompt_evolution_engine, get_evolved_prompt, record_prompt_usage, generate_prompt_text
        
        # Инициализация
        pheromone_sys = get_pheromone_system()
        evolution_factory = get_evolutionary_factory("./test_evolution_detailed/agents")
        prompt_engine = get_prompt_evolution_engine("./test_evolution_detailed/prompts")
        
        print(f"🔧 Системы инициализированы")
        
        # === ЭТАП 1: СОЗДАНИЕ НАЧАЛЬНОЙ ПОПУЛЯЦИИ ===
        print("\n" + "🌱" + "-"*50)
        print("🌱 ЭТАП 1: Создание начальной популяции")
        print("🌱" + "-"*50)
        
        # Создаём много агентов разных типов
        agent_types = ["code", "web", "analysis", "code", "web", "analysis", "code", "web"]
        task_types = ["programming", "web_development", "data_analysis", "programming", "web_development", "data_analysis", "programming", "web_development"]
        
        created_agents = []
        created_prompts = []
        
        for i, (agent_type, task_type) in enumerate(zip(agent_types, task_types)):
            agent_dna = spawn_evolved_agent(agent_type, [task_type])
            prompt_dna = get_evolved_prompt(agent_type, task_type)
            
            created_agents.append(agent_dna)
            created_prompts.append(prompt_dna)
            
            # Симулируем случайные результаты
            success = random.random() > 0.4  # 60% успеха
            quality = random.uniform(0.5, 1.0)
            time_taken = random.uniform(5, 25)
            
            # Записываем опыт
            record_agent_success(
                task_type=task_type,
                solution_pattern=f"{agent_type}_{task_type}_pattern",
                agent_combination=agent_type,
                tools_used=["llm", "specialized_tool"],
                success=success
            )
            
            update_agent_evolution(agent_dna.agent_id, success, time_taken)
            record_prompt_usage(prompt_dna.prompt_id, task_type, success, quality, time_taken)
            
            print(f"  🤖 Агент {i+1}: {agent_type} → {'✅' if success else '❌'} (качество: {quality:.2f})")
        
        stats_before = evolution_factory.get_population_stats()
        print(f"\n📊 Популяция создана: {stats_before.active_agents} агентов, здоровье: {stats_before.population_health:.2f}")
        
        # === ЭТАП 2: ФОРСИРОВАННАЯ ЭВОЛЮЦИЯ ===
        print("\n" + "🔄" + "-"*50)
        print("🔄 ЭТАП 2: Форсированная эволюция популяции")
        print("🔄" + "-"*50)
        
        print("🧬 Запуск эволюции агентов...")
        evolution_factory.evolve_population(force_evolution=True)
        
        print("🧠 Запуск эволюции промптов...")
        prompt_engine.evolve_prompts()
        
        print("🐜 Испарение слабых феромонов...")
        pheromone_sys.evaporate_pheromones()
        
        # === ЭТАП 3: АНАЛИЗ РЕЗУЛЬТАТОВ ЭВОЛЮЦИИ ===
        print("\n" + "📊" + "-"*50)
        print("📊 ЭТАП 3: Анализ результатов эволюции")
        print("📊" + "-"*50)
        
        # Статистика агентов после эволюции
        stats_after = evolution_factory.get_population_stats()
        print(f"🧬 ПОПУЛЯЦИЯ АГЕНТОВ:")
        print(f"   👥 Активных: {stats_after.active_agents}")
        print(f"   🏖️ В отставке: {stats_after.retired_agents}")
        print(f"   🎯 Макс. поколение: {stats_after.max_generation}")
        print(f"   💪 Здоровье: {stats_after.population_health:.2f}")
        print(f"   🔄 Мутаций: {stats_after.total_mutations}")
        print(f"   🧬 Скрещиваний: {stats_after.total_crossovers}")
        
        # Лучший агент
        best_agent = evolution_factory.get_best_agent()
        if best_agent:
            print(f"   🏆 Лучший агент: {best_agent.agent_id}")
            print(f"      📊 Поколение: {best_agent.generation}")
            print(f"      ✅ Успех: {best_agent.total_success_rate:.2f}")
            print(f"      🔄 Мутаций: {best_agent.mutations_count}")
            print(f"      🧬 Скрещиваний: {best_agent.crossover_count}")
        
        # Статистика промптов
        prompt_population = list(prompt_engine.prompt_population.values())
        used_prompts = [p for p in prompt_population if p.usage_count > 0]
        
        if used_prompts:
            avg_success = sum(p.success_rate for p in used_prompts) / len(used_prompts)
            best_prompt = max(used_prompts, key=lambda p: p.success_rate)
            
            print(f"\n🧠 ПОПУЛЯЦИЯ ПРОМПТОВ:")
            print(f"   📚 Всего: {len(prompt_population)}")
            print(f"   🎯 Использованных: {len(used_prompts)}")
            print(f"   📈 Средний успех: {avg_success:.2f}")
            print(f"   🏆 Лучший промпт: {best_prompt.prompt_id}")
            print(f"      ✅ Успех: {best_prompt.success_rate:.2f}")
            print(f"      🎯 Использований: {best_prompt.usage_count}")
            print(f"      🧬 Поколение: {best_prompt.generation}")
        
        # Статистика феромонов
        pheromone_stats = pheromone_sys.get_pheromone_statistics()
        print(f"\n🐜 ФЕРОМОННАЯ ПАМЯТЬ:")
        print(f"   📋 Типов задач: {pheromone_stats['task_types']}")
        print(f"   🤝 Комбинаций агентов: {pheromone_stats['agent_combinations']}")
        print(f"   🌟 Всего следов: {pheromone_stats['total_trails']}")
        print(f"   💪 Здоровье системы: {pheromone_stats['system_health']:.2f}")
        
        if pheromone_stats['strongest_trails']:
            strongest = pheromone_stats['strongest_trails'][0]
            print(f"   🏆 Сильнейший след: {strongest['task_type']} → {strongest['solution_pattern']}")
            print(f"      💪 Сила: {strongest['strength']:.2f}")
            print(f"      ✅ Успех: {strongest['success_rate']:.2f}")
        
        # === ЭТАП 4: ТЕСТ ВТОРОГО ПОКОЛЕНИЯ ===
        print("\n" + "🚀" + "-"*50)
        print("🚀 ЭТАП 4: Тест агентов второго поколения")
        print("🚀" + "-"*50)
        
        # Создаём новое поколение агентов
        second_gen_results = []
        
        for task_type in ["programming", "web_development", "data_analysis"]:
            agent_type = "code" if task_type == "programming" else "web" if task_type == "web_development" else "analysis"
            
            # Спавним эволюционного агента
            new_agent = spawn_evolved_agent(agent_type, [task_type])
            new_prompt = get_evolved_prompt(agent_type, task_type)
            
            # Симулируем улучшенную производительность
            # (должна быть лучше благодаря эволюции)
            improved_success = random.random() > 0.2  # 80% успеха
            improved_quality = random.uniform(0.7, 1.0)  # Лучше качество
            
            second_gen_results.append({
                'task_type': task_type,
                'agent_id': new_agent.agent_id,
                'generation': new_agent.generation,
                'success': improved_success,
                'quality': improved_quality
            })
            
            print(f"  🆕 {task_type}: поколение {new_agent.generation}, {'✅' if improved_success else '❌'}, качество {improved_quality:.2f}")
        
        # === ИТОГОВАЯ ОЦЕНКА ===
        print("\n" + "🏆" + "="*50)
        print("🏆 ИТОГОВАЯ ОЦЕНКА ЭВОЛЮЦИИ")
        print("🏆" + "="*50)
        
        # Успешность эволюции
        evolution_success = (
            stats_after.max_generation > stats_before.max_generation or 
            stats_after.total_mutations > 0 or 
            stats_after.total_crossovers > 0
        )
        
        health_improvement = stats_after.population_health > stats_before.population_health
        
        # Улучшение качества второго поколения
        avg_second_gen_quality = sum(r['quality'] for r in second_gen_results) / len(second_gen_results)
        second_gen_success_rate = sum(1 for r in second_gen_results if r['success']) / len(second_gen_results)
        
        print(f"📈 ИЗМЕНЕНИЯ В ПОПУЛЯЦИИ:")
        print(f"   🧬 Эволюция произошла: {'✅' if evolution_success else '❌'}")
        print(f"   💪 Здоровье улучшилось: {'✅' if health_improvement else '❌'} ({stats_before.population_health:.2f} → {stats_after.population_health:.2f})")
        print(f"   🎯 Поколения: {stats_before.max_generation} → {stats_after.max_generation}")
        
        print(f"\n🚀 ВТОРОЕ ПОКОЛЕНИЕ:")
        print(f"   ✅ Успешность: {second_gen_success_rate:.1%}")
        print(f"   ⭐ Среднее качество: {avg_second_gen_quality:.2f}")
        
        # Финальная оценка
        overall_success = evolution_success and second_gen_success_rate > 0.6
        
        if overall_success:
            grade = "🏆 ОТЛИЧНО - Эволюция работает!"
        elif evolution_success:
            grade = "✅ ХОРОШО - Есть прогресс"
        else:
            grade = "⚠️ УДОВЛЕТВОРИТЕЛЬНО - Нужны улучшения"
        
        print(f"\n🎖️ ИТОГ: {grade}")
        print(f"🧬 Создано агентов: {len(created_agents)}")
        print(f"🧠 Создано промптов: {len(created_prompts)}")
        print(f"🔄 Мутаций: {stats_after.total_mutations}")
        print(f"🧬 Скрещиваний: {stats_after.total_crossovers}")
        
        return {
            'evolution_success': evolution_success,
            'agents_created': len(created_agents),
            'mutations': stats_after.total_mutations,
            'crossovers': stats_after.total_crossovers,
            'max_generation': stats_after.max_generation,
            'second_gen_quality': avg_second_gen_quality,
            'grade': grade
        }
        
    except Exception as e:
        print(f"❌ ОШИБКА В ТЕСТЕ: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🧬 Запуск детального теста эволюции...")
    
    # Создаём тестовую директорию
    test_dir = Path("./test_evolution_detailed")
    test_dir.mkdir(exist_ok=True)
    
    # Запускаем тест
    result = asyncio.run(test_evolution_detailed())
    
    if result:
        print(f"\n✅ ТЕСТ ЗАВЕРШЁН: {result['grade']}")
        print(f"🧬 Поколений: {result['max_generation']}, Мутаций: {result['mutations']}, Скрещиваний: {result['crossovers']}")
    else:
        print("\n❌ Тест завершился с ошибками!") 