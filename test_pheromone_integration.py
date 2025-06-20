#!/usr/bin/env python3
"""
🐜 Тест интеграции феромонной системы с UnifiedOrchestrator

Проверяем что система накапливает опыт и даёт рекомендации
"""

import asyncio
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def test_pheromone_integration():
    """Тест интеграции феромонной памяти с оркестратором"""
    
    print("🐜 Тест интеграции феромонной системы с UnifiedOrchestrator")
    
    try:
        # Импортируем компоненты
        from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig
        from kittycore.core.pheromone_memory import get_pheromone_system, get_optimal_approach
        
        # Создаём тестовую конфигурацию
        config = UnifiedConfig(
            vault_path="./test_pheromone_vault",
            enable_smart_validation=True,
            enable_amem_memory=False,  # Отключаем A-MEM для простоты
            enable_vector_memory=False,
            enable_human_intervention=False
        )
        
        # Создаём оркестратор
        orchestrator = UnifiedOrchestrator(config)
        
        print("\n📊 Симулируем выполнение задач...")
        
        # Симулируем несколько задач для накопления феромонов
        test_tasks = [
            "Создай Python скрипт для расчёта факториала",
            "Напиши код для сортировки массива",
            "Создай веб-страницу с формой",
            "Сделай анализ данных продаж"
        ]
        
        for i, task in enumerate(test_tasks):
            print(f"\n{i+1}. Задача: {task}")
            
            # Симулируем результат выполнения
            final_result = {
                'created_files': [f'result_{i}.py'] if 'код' in task or 'скрипт' in task else [f'result_{i}.html'],
                'validation_summary': {'quality_score': 0.8 if i % 2 == 0 else 0.5},  # Чередуем успех/неудачу
                'process_trace': [f'Анализ задачи: {task}', 'Создание решения', 'Валидация результата'],
                'coordination_log': ['CodeAgent выполняет задачу'] if 'код' in task else ['WebAgent создаёт страницу']
            }
            
            # Вызываем методы оркестратора для записи феромонов
            task_type = orchestrator._determine_task_type(task)
            solution_pattern = orchestrator._extract_solution_pattern(final_result)
            agent_combination = orchestrator._get_agent_combination(final_result)
            tools_used = orchestrator._get_tools_used(final_result)
            
            print(f"  Тип задачи: {task_type}")
            print(f"  Паттерн решения: {solution_pattern}")
            print(f"  Агенты: {agent_combination}")
            print(f"  Инструменты: {tools_used}")
            
            # Записываем в феромонную систему
            from kittycore.core.pheromone_memory import record_agent_success
            
            quality_score = final_result['validation_summary']['quality_score']
            success = quality_score >= 0.7
            
            record_agent_success(
                task_type=task_type,
                solution_pattern=solution_pattern,
                agent_combination=agent_combination,
                tools_used=tools_used,
                success=success
            )
            
            print(f"  Результат: {'✅ Успех' if success else '❌ Неудача'} (качество: {quality_score})")
        
        print("\n🎯 Получаем рекомендации на основе накопленного опыта...")
        
        # Тестируем рекомендации для разных типов задач
        test_recommendations = [
            "programming",
            "web_development", 
            "data_analysis"
        ]
        
        for task_type in test_recommendations:
            approach = get_optimal_approach(task_type)
            print(f"\n📋 Рекомендации для {task_type}:")
            print(f"  Лучшие паттерны: {approach['best_solution_patterns']}")
            print(f"  Лучшие агенты: {approach['best_agent_combination']}")
            print(f"  Лучшие инструменты: {approach['best_tools']}")
            print(f"  Уверенность: {approach['confidence']:.2f}")
        
        # Статистика феромонной системы
        pheromone_system = get_pheromone_system()
        stats = pheromone_system.get_pheromone_statistics()
        
        print(f"\n📈 Статистика феромонной системы:")
        print(f"  Типов задач: {stats['task_types']}")
        print(f"  Комбинаций агентов: {stats['agent_combinations']}")
        print(f"  Всего следов: {stats['total_trails']}")
        print(f"  Здоровье системы: {stats['system_health']:.2f}")
        
        if stats['strongest_trails']:
            print(f"\n🏆 Самые сильные феромонные следы:")
            for trail in stats['strongest_trails'][:3]:
                print(f"  • {trail['task_type']} -> {trail['solution_pattern']} "
                      f"(сила: {trail['strength']:.2f}, успех: {trail['success_rate']:.2f})")
        
        if stats['best_agents']:
            print(f"\n🤖 Лучшие агентные комбинации:")
            for agent in stats['best_agents'][:3]:
                print(f"  • {agent['combination']} "
                      f"(сила: {agent['strength']:.2f}, успех: {agent['success_rate']:.2f})")
        
        print("\n✅ Интеграция феромонной системы работает!")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_pheromone_integration())
    if success:
        print("\n🎉 Тест прошёл успешно! Феромонная система интегрирована.")
    else:
        print("\n💥 Тест провален. Нужно исправить ошибки.") 