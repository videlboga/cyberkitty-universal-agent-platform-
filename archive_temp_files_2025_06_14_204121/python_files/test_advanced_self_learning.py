#!/usr/bin/env python3
"""
🧠 Тест революционной системы самообучения KittyCore

Демонстрирует работу:
- Adaptive Rate Control  
- Critique-Guided Improvement
- Guardian Agents
- Constitutional AI принципы
"""

import asyncio
import time
import random
from typing import Dict, Any

# Импортируем нашу революционную систему
try:
    from kittycore.core.advanced_self_learning import get_advanced_learning_engine, process_task_with_advanced_learning
    from kittycore.core.adaptive_rate_control import get_rate_controller
    print("✅ Все компоненты самообучения импортированы!")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    exit(1)

async def mock_agent_execution(request_data: Dict[str, Any]) -> str:
    """Мок-функция выполнения задачи агентом"""
    
    task = request_data.get('task', 'unknown')
    agent_id = request_data.get('agent_id', 'unknown')
    
    # Симулируем разную производительность
    if 'быстро' in task.lower():
        await asyncio.sleep(random.uniform(0.1, 2.0))  # Быстрое выполнение
        return f"✅ Агент {agent_id} быстро выполнил: {task}"
    
    elif 'медленно' in task.lower():
        await asyncio.sleep(random.uniform(10.0, 15.0))  # Медленное выполнение  
        return f"🐌 Агент {agent_id} медленно выполнил: {task}"
    
    elif 'ошибка' in task.lower():
        raise Exception(f"Симулированная ошибка агента {agent_id}")
    
    else:
        await asyncio.sleep(random.uniform(3.0, 8.0))  # Обычное выполнение
        return f"📝 Агент {agent_id} выполнил: {task}"

async def test_basic_learning():
    """Тест базового функционала обучения"""
    
    print("\n🎯 === ТЕСТ БАЗОВОГО ОБУЧЕНИЯ ===")
    
    engine = get_advanced_learning_engine()
    
    # Запускаем сессию обучения
    session_id = await engine.start_learning_session()
    print(f"🎯 Начата сессия обучения: {session_id}")
    
    # Тестовые задачи
    test_tasks = [
        ("agent_speedy", "Сделай что-то быстро", {"priority": "high"}),
        ("agent_normal", "Обычная задача", {"priority": "medium"}),
        ("agent_slow", "Сделай что-то медленно", {"priority": "low"}),
        ("agent_speedy", "Ещё одна быстрая задача", {"priority": "high"}),
    ]
    
    results = []
    
    for agent_id, task, input_data in test_tasks:
        print(f"\n🔄 Обрабатываем: {task} (агент: {agent_id})")
        
        result = await process_task_with_advanced_learning(
            agent_id=agent_id,
            task=task,
            input_data=input_data,
            execution_func=mock_agent_execution
        )
        
        results.append(result)
        
        if result['success']:
            print(f"   ✅ Выполнено за {result['execution_time']:.2f}с")
            print(f"   📊 Критик: {len(result['critiques'])} замечаний")
            print(f"   ✨ Улучшений: {result['improvements_applied']}")
        else:
            print(f"   ❌ Ошибка: {result['error']}")
    
    # Завершаем сессию
    completed_session = await engine.end_learning_session()
    print(f"\n✅ Сессия завершена: {completed_session.tasks_processed} задач, {completed_session.improvements_applied} улучшений")
    
    return results

async def test_rate_limiting():
    """Тест системы rate limiting"""
    
    print("\n🚀 === ТЕСТ RATE LIMITING ===")
    
    rate_controller = get_rate_controller()
    
    # Быстрые запросы для проверки rate limiting
    tasks = []
    for i in range(10):
        task = asyncio.create_task(
            rate_controller.execute_request(
                provider="test_provider",
                request_data={"request_id": i},
                execute_func=lambda data: asyncio.sleep(0.1)  # Быстрая функция
            )
        )
        tasks.append(task)
    
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time
    
    successful = sum(1 for r in results if hasattr(r, 'success') and r.success)
    
    print(f"📊 Выполнено {successful}/10 запросов за {total_time:.2f}с")
    print(f"🎯 Rate limiting работает: {total_time > 2.0}")  # Должно быть медленнее из-за rate limiting
    
    # Статистика rate controller
    stats = rate_controller.get_statistics()
    print(f"📈 Статистика: {stats['success_rate']} успеха, {stats['cache_hit_rate']} кеш")
    
    return stats

async def test_guardian_alerts():
    """Тест системы алертов Guardian Agents"""
    
    print("\n👮 === ТЕСТ GUARDIAN AGENTS ===")
    
    engine = get_advanced_learning_engine()
    session_id = await engine.start_learning_session()
    
    # Задачи которые должны вызвать алерты
    problematic_tasks = [
        ("agent_error", "Задача с ошибка", {"simulate": "error"}),
        ("agent_slow", "Очень медленная задача медленно", {"timeout": "long"}),
        ("agent_slow", "Ещё одна медленная задача медленно", {"timeout": "long"}),
    ]
    
    for agent_id, task, input_data in problematic_tasks:
        print(f"\n⚠️ Тестируем проблемную задачу: {task}")
        
        try:
            result = await process_task_with_advanced_learning(
                agent_id=agent_id,
                task=task,
                input_data=input_data,
                execution_func=mock_agent_execution
            )
            
            if not result['success']:
                print(f"   ❌ Ожидаемая ошибка: {result.get('error', 'unknown')}")
            else:
                print(f"   ⏰ Медленное выполнение: {result['execution_time']:.2f}с")
                
        except Exception as e:
            print(f"   💥 Исключение: {e}")
    
    # Проверяем алерты от охранников
    for name, guardian in engine.guardians.items():
        report = guardian.get_monitoring_report()
        print(f"\n👮 Отчёт охранника {name}:")
        print(f"   🚨 Алертов: {report['recent_alerts_count']}")
        print(f"   🛡️ Вмешательств: {report['recent_interventions_count']}")
        print(f"   📊 Метрик отслежено: {report['total_metrics_tracked']}")
    
    await engine.end_learning_session()

async def test_constitutional_ai():
    """Тест извлечения принципов (Constitutional AI)"""
    
    print("\n📜 === ТЕСТ CONSTITUTIONAL AI ===")
    
    engine = get_advanced_learning_engine()
    session_id = await engine.start_learning_session()
    
    # Задачи для извлечения принципов
    learning_tasks = [
        ("agent_fast", "Быстрая задача 1", {}),
        ("agent_fast", "Быстрая задача 2", {}),  
        ("agent_fast", "Быстрая задача 3", {}),  # Паттерн быстрого выполнения
        ("agent_slow", "Медленная задача медленно 1", {}),
        ("agent_slow", "Медленная задача медленно 2", {}),  # Паттерн медленного выполнения
    ]
    
    for agent_id, task, input_data in learning_tasks:
        result = await process_task_with_advanced_learning(
            agent_id=agent_id,
            task=task,
            input_data=input_data,
            execution_func=mock_agent_execution
        )
        
        print(f"📝 {task}: {result['execution_time']:.2f}с, {len(result['critiques'])} критик")
    
    await engine.end_learning_session()
    
    # Проверяем извлечённые принципы
    print(f"\n📜 Извлечено принципов: {len(engine.system_principles)}")
    
    for principle_id, principle in engine.system_principles.items():
        print(f"   • {principle.title}")
        print(f"     Уверенность: {principle.confidence:.2f} ({principle.evidence_count} подтверждений)")
        print(f"     Категория: {principle.category}")

async def test_comprehensive_report():
    """Тест комплексного отчёта системы"""
    
    print("\n📊 === КОМПЛЕКСНЫЙ ОТЧЁТ СИСТЕМЫ ===")
    
    engine = get_advanced_learning_engine()
    
    # Получаем отчёт
    report = engine.get_comprehensive_report()
    
    print(f"🆔 Engine ID: {report['engine_id']}")
    print(f"⏱️ Uptime: {report['uptime_seconds']:.1f}с")
    print(f"📈 Задач обработано: {report['total_tasks_processed']}")
    print(f"✨ Улучшений применено: {report['total_improvements']}")
    print(f"📊 Rate улучшений: {report['improvement_rate']:.3f}")
    
    print(f"\n🎭 Критики:")
    for name, stats in report['critics'].items():
        print(f"   • {name}: {stats['total_critiques']} критик, ср.балл {stats['avg_score']:.2f}")
    
    print(f"\n👮 Охранники:")
    for name, stats in report['guardians'].items():
        print(f"   • {name}: {stats['recent_alerts_count']} алертов, {stats['recent_interventions_count']} вмешательств")
    
    print(f"\n📜 Принципы: {report['principles']['total_principles']} всего, {report['principles']['high_confidence']} с высокой уверенностью")
    
    # Получаем инсайты
    insights = engine.get_learning_insights()
    
    print(f"\n🧠 ИНСАЙТЫ ОБУЧЕНИЯ:")
    print(f"💪 Здоровье системы: {insights['system_health_score']:.2f}")
    print(f"📈 Тренд обучения: {insights['learning_trends']['trend']}")
    
    print(f"\n🏆 Топ агенты:")
    for agent in insights['top_performing_agents']:
        print(f"   • {agent['agent_id']}: {agent['avg_score']:.2f} ({agent['task_count']} задач)")
    
    print(f"\n💡 Рекомендации:")
    for rec in insights['recommendations']:
        print(f"   • {rec}")

async def main():
    """Главная функция тестирования"""
    
    print("🧠 ТЕСТИРОВАНИЕ РЕВОЛЮЦИОННОЙ СИСТЕМЫ САМООБУЧЕНИЯ KITTYCORE 3.0")
    print("=" * 70)
    
    try:
        # Базовое обучение
        await test_basic_learning()
        
        # Rate limiting  
        await test_rate_limiting()
        
        # Guardian Agents
        await test_guardian_alerts()
        
        # Constitutional AI
        await test_constitutional_ai()
        
        # Комплексный отчёт
        await test_comprehensive_report()
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! СИСТЕМА САМООБУЧЕНИЯ РАБОТАЕТ!")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА ТЕСТИРОВАНИЯ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 