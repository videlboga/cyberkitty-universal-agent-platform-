#!/usr/bin/env python3
"""
🧪 Тестирование современной системы самообучения KittyCore 3.0
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kittycore.core.self_improvement import SelfLearningEngine
import time

async def test_self_learning_engine():
    """Тест современного движка самообучения"""
    
    print("🧠 === ТЕСТ SELFLEARNINGENGINE 3.0 ===")
    
    # Создать движок
    engine = SelfLearningEngine()
    
    # Симуляция работы агента Nova
    agent_id = "nova_agent"
    
    print(f"\n📊 Симуляция работы агента {agent_id}...")
    
    # Успешные выполнения
    for i in range(5):
        await engine.record_agent_execution(
            agent_id=agent_id,
            task_id=f"task_{i}",
            input_data={"query": f"Анализ данных #{i}", "type": "analysis"},
            output=f"Результат анализа #{i}: данные обработаны успешно",
            execution_time=1.2 + i * 0.1,
            success=True,
            quality_score=0.85 + i * 0.02,
            user_feedback="Хороший результат" if i % 2 == 0 else None
        )
    
    # Несколько ошибок
    for i in range(2):
        await engine.record_agent_execution(
            agent_id=agent_id,
            task_id=f"error_task_{i}",
            input_data={"query": f"Сложная задача #{i}", "type": "complex"},
            output=f"Error: Не удалось обработать данные",
            execution_time=3.0,
            success=False,
            user_feedback="Нужно исправить"
        )
    
    print(f"✅ Записано 7 выполнений для агента {agent_id}")
    
    # Получить план улучшений
    print(f"\n📈 Получение плана улучшений...")
    improvement_plan = await engine.get_agent_improvement_plan(agent_id)
    
    print(f"🎯 Статус плана: {improvement_plan['status']}")
    print(f"🔥 Приоритет улучшений: {improvement_plan['improvement_priority']}")
    print(f"📊 Общая статистика обучения:")
    stats = improvement_plan['learning_statistics']
    print(f"   - Всего обратной связи: {stats['total_feedback']}")
    print(f"   - Средний балл: {stats['avg_score']:.2f}")
    print(f"   - Обнаружено паттернов: {stats['patterns_detected']}")
    
    dataset_stats = improvement_plan['dataset_statistics']
    print(f"📦 Статистика датасета:")
    print(f"   - Всего примеров: {dataset_stats['total_examples']}")
    print(f"   - Готов к обучению: {dataset_stats['ready_for_training']}")
    print(f"   - Доля качественных: {dataset_stats.get('high_quality_ratio', 0):.2f}")
    
    monitoring = improvement_plan['monitoring_status']
    print(f"🔍 Мониторинг:")
    print(f"   - Статус: {monitoring['status']}")
    print(f"   - Активные алерты: {monitoring['active_alerts']}")
    print(f"   - Отслеживаемые метрики: {len(monitoring['monitored_metrics'])}")
    
    # Few-shot примеры
    few_shot = improvement_plan['few_shot_examples']
    if few_shot:
        print(f"🎯 Few-shot примеры для промптов: {len(few_shot)} шт.")
        for i, example in enumerate(few_shot[:2]):
            print(f"   Пример {i+1}: качество {example['quality']:.2f}")
    
    # Автоматическое улучшение всех агентов
    print(f"\n🔄 Автоматическое улучшение агентов...")
    auto_improvements = await engine.auto_improve_all_agents()
    
    print(f"📈 Результаты автоулучшения:")
    print(f"   - Агентов проанализировано: {auto_improvements['total_agents_analyzed']}")
    print(f"   - Агентов улучшено: {auto_improvements['total_agents_improved']}")
    print(f"   - Здоровье системы: {auto_improvements['system_health']:.2f}")
    
    # Общий обзор системы
    print(f"\n🌐 Обзор системы самообучения:")
    overview = engine.get_system_overview()
    
    print(f"🏥 Статус системы: {overview['system_status']}")
    print(f"📊 Здоровье системы: {overview['system_health_score']:.3f}")
    print(f"🤖 Агенты:")
    agents = overview['agents']
    print(f"   - Всего: {agents['total']}")
    print(f"   - С обратной связью: {agents['with_feedback']}")
    print(f"   - С датасетами: {agents['with_datasets']}")
    
    feedback = overview['feedback']
    print(f"🔄 Обратная связь:")
    print(f"   - Обработано всего: {feedback['total_processed']}")
    print(f"   - Обнаружено паттернов: {feedback['patterns_detected']}")
    print(f"   - Активные алерты: {feedback['active_alerts']}")
    
    datasets = overview['datasets']
    print(f"📦 Датасеты:")
    print(f"   - Всего примеров: {datasets['total_examples']}")
    print(f"   - Готовы к обучению: {datasets['agents_ready_for_training']} агентов")
    
    performance = overview['performance']
    print(f"⚡ Производительность:")
    print(f"   - Всего улучшений: {performance['total_improvements_made']}")
    print(f"   - Среднее feedback на агента: {performance['avg_feedback_per_agent']}")

if __name__ == "__main__":
    asyncio.run(test_self_learning_engine()) 