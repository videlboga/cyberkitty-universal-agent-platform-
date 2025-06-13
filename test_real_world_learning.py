#!/usr/bin/env python3
"""
🌍 Тест революционной системы самообучения на РЕАЛЬНЫХ задачах

Использует настоящий OrchestratorAgent KittyCore для выполнения реальных задач
и показывает как система обучается, критикует и улучшается.
"""

import asyncio
import time
import json
from typing import Dict, Any

# Импортируем реальную систему KittyCore
try:
    from kittycore.core.orchestrator import OrchestratorAgent
    from kittycore.core.advanced_self_learning import get_advanced_learning_engine, process_task_with_advanced_learning
    from kittycore.core.adaptive_rate_control import get_rate_controller
    print("✅ Все компоненты KittyCore импортированы!")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    exit(1)

class RealWorldTaskExecutor:
    """Выполнитель реальных задач через OrchestratorAgent"""
    
    def __init__(self):
        from kittycore.core.orchestrator import OrchestratorConfig
        config = OrchestratorConfig(orchestrator_id="real_world_orchestrator")
        self.orchestrator = OrchestratorAgent(config)
        
    async def execute_real_task(self, request_data: Dict[str, Any]) -> Any:
        """Выполнить реальную задачу через оркестратор"""
        
        task = request_data.get('task', '')
        input_data = request_data.get('input_data', {})
        agent_id = request_data.get('agent_id', 'unknown')
        
        print(f"🎯 Оркестратор выполняет: {task}")
        
        try:
            # Выполняем задачу через настоящий оркестратор
            result = await self.orchestrator.execute_task(task)
            
            print(f"   ✅ Результат получен: {len(str(result))} символов")
            return result
            
        except Exception as e:
            print(f"   ❌ Ошибка оркестратора: {e}")
            raise e

async def test_real_file_creation():
    """Тест создания реальных файлов"""
    
    print("\n📝 === ТЕСТ СОЗДАНИЯ РЕАЛЬНЫХ ФАЙЛОВ ===")
    
    engine = get_advanced_learning_engine()
    executor = RealWorldTaskExecutor()
    session_id = await engine.start_learning_session()
    
    # Реальные задачи создания файлов
    file_tasks = [
        {
            "agent_id": "file_creator",
            "task": "Создай файл hello_world.py с программой 'Hello World' на Python",
            "input_data": {"file_type": "python", "complexity": "simple"}
        },
        {
            "agent_id": "file_creator", 
            "task": "Создай HTML страницу с формой регистрации пользователя",
            "input_data": {"file_type": "html", "complexity": "medium"}
        },
        {
            "agent_id": "file_creator",
            "task": "Создай JSON файл с конфигурацией веб-сервера",
            "input_data": {"file_type": "json", "complexity": "simple"}
        }
    ]
    
    results = []
    
    for task_data in file_tasks:
        print(f"\n🔄 Выполняем: {task_data['task']}")
        
        result = await process_task_with_advanced_learning(
            agent_id=task_data["agent_id"],
            task=task_data["task"],
            input_data=task_data["input_data"],
            execution_func=executor.execute_real_task
        )
        
        results.append(result)
        
        if result['success']:
            print(f"   ✅ Выполнено за {result['execution_time']:.2f}с")
            print(f"   📊 Критики дали {len(result['critiques'])} оценок")
            
            # Показываем детали критики
            for i, critique_data in enumerate(result['critiques']):
                critique = critique_data
                score = critique.get('overall_score', 0)
                priority = critique.get('improvement_priority', 'unknown')
                print(f"      🎭 Критик {i+1}: балл {score:.2f}, приоритет {priority}")
                
            print(f"   ✨ Применено улучшений: {result['improvements_applied']}")
        else:
            print(f"   ❌ Ошибка: {result['error']}")
    
    completed_session = await engine.end_learning_session()
    print(f"\n✅ Сессия создания файлов завершена: {completed_session.tasks_processed} задач")
    
    return results

async def test_real_calculation_tasks():
    """Тест реальных вычислительных задач"""
    
    print("\n🧮 === ТЕСТ РЕАЛЬНЫХ ВЫЧИСЛЕНИЙ ===")
    
    engine = get_advanced_learning_engine()
    executor = RealWorldTaskExecutor()
    session_id = await engine.start_learning_session()
    
    # Реальные вычислительные задачи
    calc_tasks = [
        {
            "agent_id": "calculator",
            "task": "Вычисли площадь круга с радиусом 5 метров",
            "input_data": {"type": "geometry", "difficulty": "easy"}
        },
        {
            "agent_id": "calculator",
            "task": "Найди корни квадратного уравнения x² - 5x + 6 = 0",
            "input_data": {"type": "algebra", "difficulty": "medium"}
        },
        {
            "agent_id": "calculator", 
            "task": "Посчитай сумму чисел от 1 до 100",
            "input_data": {"type": "arithmetic", "difficulty": "easy"}
        }
    ]
    
    results = []
    
    for task_data in calc_tasks:
        print(f"\n🔄 Вычисляем: {task_data['task']}")
        
        result = await process_task_with_advanced_learning(
            agent_id=task_data["agent_id"],
            task=task_data["task"], 
            input_data=task_data["input_data"],
            execution_func=executor.execute_real_task
        )
        
        results.append(result)
        
        if result['success']:
            print(f"   ✅ Вычислено за {result['execution_time']:.2f}с")
            print(f"   📊 Получено {len(result['critiques'])} критических оценок")
            print(f"   ✨ Автоулучшений: {result['improvements_applied']}")
        else:
            print(f"   ❌ Ошибка вычисления: {result['error']}")
    
    completed_session = await engine.end_learning_session()
    print(f"\n✅ Сессия вычислений завершена: {completed_session.tasks_processed} задач")
    
    return results

async def test_real_web_tasks():
    """Тест реальных веб-задач"""
    
    print("\n🌐 === ТЕСТ РЕАЛЬНЫХ ВЕБ-ЗАДАЧ ===")
    
    engine = get_advanced_learning_engine()
    executor = RealWorldTaskExecutor()
    session_id = await engine.start_learning_session()
    
    # Реальные веб-задачи
    web_tasks = [
        {
            "agent_id": "web_developer",
            "task": "Создай простую веб-страницу с котятами",
            "input_data": {"type": "html", "theme": "cats", "complexity": "simple"}
        },
        {
            "agent_id": "web_developer",
            "task": "Создай CSS стили для красивой формы входа",
            "input_data": {"type": "css", "component": "login", "complexity": "medium"}
        }
    ]
    
    results = []
    
    for task_data in web_tasks:
        print(f"\n🔄 Разрабатываем: {task_data['task']}")
        
        result = await process_task_with_advanced_learning(
            agent_id=task_data["agent_id"],
            task=task_data["task"],
            input_data=task_data["input_data"], 
            execution_func=executor.execute_real_task
        )
        
        results.append(result)
        
        if result['success']:
            print(f"   ✅ Разработано за {result['execution_time']:.2f}с")
            print(f"   📊 Критики: {len(result['critiques'])} анализов")
            print(f"   ✨ Улучшений: {result['improvements_applied']}")
        else:
            print(f"   ❌ Ошибка разработки: {result['error']}")
    
    completed_session = await engine.end_learning_session()
    print(f"\n✅ Сессия веб-разработки завершена: {completed_session.tasks_processed} задач")
    
    return results

async def analyze_learning_results(all_results):
    """Анализ результатов обучения"""
    
    print("\n🧠 === АНАЛИЗ РЕЗУЛЬТАТОВ ОБУЧЕНИЯ ===")
    
    engine = get_advanced_learning_engine()
    
    # Общая статистика
    total_tasks = len(all_results)
    successful_tasks = sum(1 for r in all_results if r['success'])
    total_time = sum(r['execution_time'] for r in all_results if r['success'])
    total_critiques = sum(len(r['critiques']) for r in all_results if r['success'])
    total_improvements = sum(r['improvements_applied'] for r in all_results if r['success'])
    
    print(f"📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"   🎯 Задач выполнено: {successful_tasks}/{total_tasks} ({successful_tasks/total_tasks*100:.1f}%)")
    print(f"   ⏱️ Общее время: {total_time:.2f}с (среднее: {total_time/max(1,successful_tasks):.2f}с)")
    print(f"   🎭 Всего критики: {total_critiques} (среднее: {total_critiques/max(1,successful_tasks):.1f} на задачу)")
    print(f"   ✨ Всего улучшений: {total_improvements}")
    
    # Анализ по агентам
    print(f"\n📈 АНАЛИЗ ПО АГЕНТАМ:")
    
    agent_stats = {}
    for result in all_results:
        if not result['success']:
            continue
            
        # Попробуем извлечь agent_id из task_id или другим способом
        agent_id = "unknown_agent"  # fallback
        
        if agent_id not in agent_stats:
            agent_stats[agent_id] = {
                'tasks': 0,
                'total_time': 0,
                'critiques': 0,
                'improvements': 0
            }
        
        stats = agent_stats[agent_id]
        stats['tasks'] += 1
        stats['total_time'] += result['execution_time']
        stats['critiques'] += len(result['critiques'])
        stats['improvements'] += result['improvements_applied']
    
    for agent_id, stats in agent_stats.items():
        avg_time = stats['total_time'] / stats['tasks']
        avg_critiques = stats['critiques'] / stats['tasks']
        print(f"   🤖 {agent_id}: {stats['tasks']} задач, ср.время {avg_time:.2f}с, ср.критик {avg_critiques:.1f}")
    
    # Получаем комплексный отчёт системы
    report = engine.get_comprehensive_report()
    
    print(f"\n🔍 СИСТЕМА САМООБУЧЕНИЯ:")
    print(f"   💪 Здоровье системы: {engine._calculate_system_health_score():.2f}")
    print(f"   📈 Rate улучшений: {report['improvement_rate']:.3f}")
    print(f"   🎯 Rate controller: {report['rate_control']['success_rate']} успеха")
    print(f"   💾 Кеш: {report['rate_control']['cache_hit_rate']} попаданий")
    
    # Извлечённые принципы
    print(f"\n📜 ИЗВЛЕЧЁННЫЕ ПРИНЦИПЫ:")
    if engine.system_principles:
        for principle_id, principle in engine.system_principles.items():
            print(f"   • {principle.title}")
            print(f"     Уверенность: {principle.confidence:.2f} ({principle.evidence_count} подтверждений)")
            print(f"     Категория: {principle.category}")
    else:
        print("   Принципы ещё не извлечены - нужно больше данных")
    
    # Рекомендации по улучшению
    insights = engine.get_learning_insights()
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    for rec in insights['recommendations']:
        print(f"   • {rec}")
    
    return {
        'total_tasks': total_tasks,
        'success_rate': successful_tasks/total_tasks,
        'avg_time': total_time/max(1,successful_tasks),
        'system_health': engine._calculate_system_health_score(),
        'principles_count': len(engine.system_principles)
    }

async def main():
    """Главная функция тестирования на реальных задачах"""
    
    print("🌍 ТЕСТИРОВАНИЕ СИСТЕМЫ САМООБУЧЕНИЯ НА РЕАЛЬНЫХ ЗАДАЧАХ KITTYCORE")
    print("=" * 75)
    
    all_results = []
    
    try:
        # Тест создания файлов
        file_results = await test_real_file_creation()
        all_results.extend(file_results)
        
        # Небольшая пауза между тестами
        await asyncio.sleep(2)
        
        # Тест вычислений
        calc_results = await test_real_calculation_tasks()
        all_results.extend(calc_results)
        
        await asyncio.sleep(2)
        
        # Тест веб-задач
        web_results = await test_real_web_tasks()
        all_results.extend(web_results)
        
        # Анализ результатов
        analysis = await analyze_learning_results(all_results)
        
        print(f"\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        print(f"📊 Успешность: {analysis['success_rate']*100:.1f}%")
        print(f"💪 Здоровье системы: {analysis['system_health']:.2f}")
        print(f"📜 Принципов извлечено: {analysis['principles_count']}")
        
        if analysis['success_rate'] > 0.8:
            print("✅ СИСТЕМА САМООБУЧЕНИЯ РАБОТАЕТ ОТЛИЧНО!")
        elif analysis['success_rate'] > 0.6:
            print("🟡 СИСТЕМА РАБОТАЕТ ХОРОШО, ЕСТЬ ТОЧКИ РОСТА")
        else:
            print("🔴 СИСТЕМА ТРЕБУЕТ ДОРАБОТКИ")
            
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 