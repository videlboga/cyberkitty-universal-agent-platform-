#!/usr/bin/env python3
"""
🚀 KittyCore 3.0 - Демонстрация на реальных задачах

Покажем как система справляется с настоящими жизненными задачами!
"""

import asyncio
import kittycore

async def demo_real_world_tasks():
    print("🚀 KittyCore 3.0 - Демонстрация на реальных задачах")
    print("=" * 50)
    
    # Создаём оркестратор
    orchestrator = kittycore.create_orchestrator()
    
    # Реальные задачи разной сложности
    real_tasks = [
        {
            "title": "Простая задача",
            "description": "Создать Python скрипт для парсинга CSV файлов",
            "category": "programming"
        },
        {
            "title": "Средняя задача", 
            "description": "Разработать REST API для управления задачами с аутентификацией пользователей, базой данных PostgreSQL и документацией Swagger",
            "category": "backend"
        },
        {
            "title": "Сложная задача",
            "description": "Создать полноценную платформу электронной коммерции с витриной товаров, корзиной покупок, системой оплаты, панелью администратора, мобильным приложением, системой уведомлений и аналитикой продаж",
            "category": "fullstack"
        }
    ]
    
    results = []
    
    for i, task in enumerate(real_tasks, 1):
        print(f"\n📋 Задача {i}: {task['title']}")
        print(f"📝 Описание: {task['description']}")
        print(f"🏷️ Категория: {task['category']}")
        print("-" * 50)
        
        # Выполняем задачу
        result = await orchestrator.solve_task(task['description'])
        
        # Анализируем результат
        print(f"✅ Статус: {result['status']}")
        print(f"⏱️ Время выполнения: {result['duration']:.2f}с")
        print(f"🧮 Сложность: {result['complexity_analysis']['complexity']}")
        print(f"👥 Команда: {result['team']['team_size']} агентов")
        print(f"📊 Подзадач: {len(result['subtasks'])}")
        print(f"🧠 Память: {result['collective_memory_stats']['total_memories']} записей")
        print(f"🧬 Улучшений: {result['self_improvement_report']['improvements_made']}")
        
        # Показываем workflow
        print(f"\n📈 Workflow диаграмма:")
        print(result['workflow_graph']['mermaid'])
        
        results.append(result)
    
    # Финальная аналитика
    print(f"\n🎯 ФИНАЛЬНАЯ АНАЛИТИКА:")
    print("=" * 50)
    
    total_time = sum(r['duration'] for r in results)
    total_agents = orchestrator.self_improvement.get_system_report()['total_agents']
    total_tasks = orchestrator.self_improvement.get_system_report()['total_tasks']
    improvements = orchestrator.self_improvement.get_system_report()['improvements_made']
    
    print(f"📊 Общая статистика:")
    print(f"   - Всего задач решено: {len(results)}")
    print(f"   - Общее время: {total_time:.2f}с")
    print(f"   - Среднее время: {total_time/len(results):.2f}с")
    print(f"   - Уникальных агентов: {total_agents}")
    print(f"   - Всего выполнений: {total_tasks}")
    print(f"   - Эволюций агентов: {improvements}")
    
    # Показываем топ агентов
    top_performers = orchestrator.self_improvement.get_system_report()['top_performers']
    if top_performers:
        print(f"\n🏆 Топ агенты:")
        for performer in top_performers[:3]:
            print(f"   - {performer['agent_id']}: эффективность {performer['efficiency']:.3f}")
    
    print(f"\n🎉 Демонстрация завершена! KittyCore 3.0 справился со всеми задачами!")

if __name__ == "__main__":
    asyncio.run(demo_real_world_tasks()) 