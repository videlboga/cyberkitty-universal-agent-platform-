#!/usr/bin/env python3
"""
🧠 Пример саморазвивающегося агента - KittyCore 2.0

Демонстрирует концепции из исследования 2025:
- Self-improving agents
- Autonomous tool creation  
- Performance tracking
- Recursive optimization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
import logging
from kittycore import Agent
from kittycore.self_improvement import create_self_improving_agent

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("🧠 Демонстрация саморазвивающегося агента")
    print("=" * 50)
    
    # Создать базового агента
    base_agent = Agent(
        prompt="""
        Ты умный аналитический агент, который:
        1. Анализирует данные и находит закономерности
        2. Создаёт SQL запросы для извлечения данных
        3. Генерирует отчёты и визуализации
        4. Оптимизирует свою работу на основе опыта
        
        Всегда стремись к улучшению своих результатов!
        """,
        model="mock"  # Используем mock модель для демонстрации
    )
    
    # Обернуть в саморазвивающегося агента
    smart_agent = create_self_improving_agent("analytics_agent", base_agent)
    
    # Список задач для демонстрации
    tasks = [
        "Проанализируй продажи за последний месяц",
        "Создай SQL запрос для поиска топ-10 клиентов",
        "Найди аномалии в данных о заказах",
        "Построй прогноз продаж на следующий квартал",
        "Оптимизируй производительность базы данных",
        "Создай дашборд для мониторинга KPI",
        "Анализируй поведение пользователей на сайте",
        "Найди корреляции между маркетинговыми кампаниями и продажами",
        "Создай отчёт о рентабельности продуктов",
        "Оптимизируй процесс обработки заказов",
        "Проанализируй эффективность рекламных каналов",
        "Создай модель прогнозирования оттока клиентов",
        "Найди возможности для увеличения среднего чека",
        "Оптимизируй логистические маршруты",
        "Создай систему раннего предупреждения о проблемах"
    ]
    
    print(f"📋 Выполнение {len(tasks)} задач с самооценкой...")
    print()
    
    # Выполнить задачи с отслеживанием прогресса
    for i, task in enumerate(tasks, 1):
        print(f"🔄 Задача {i}/{len(tasks)}: {task}")
        
        start_time = time.time()
        
        try:
            # Выполнить задачу с самооценкой
            result = smart_agent.run_with_self_improvement(
                task,
                context={
                    'task_number': i,
                    'total_tasks': len(tasks),
                    'domain': 'analytics'
                }
            )
            
            execution_time = time.time() - start_time
            print(f"✅ Выполнено за {execution_time:.2f}с")
            
            # Показать результат (сокращённо)
            result_preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            print(f"📄 Результат: {result_preview}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            
        print()
        
        # Небольшая пауза для наглядности
        time.sleep(0.5)
    
    print("=" * 50)
    print("📊 ОТЧЁТ О САМООЦЕНКЕ АГЕНТА")
    print("=" * 50)
    
    # Получить отчёт о самооценке
    report = smart_agent.get_self_improvement_report()
    
    print(f"🆔 ID агента: {report['agent_id']}")
    print(f"📈 Выполнено задач: {report['task_count']}")
    print(f"🛠️ Создано инструментов: {report['created_tools']}")
    print(f"🔧 Применено оптимизаций: {report['optimizations_applied']}")
    print()
    
    # Показать метрики производительности
    print("📊 МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ:")
    performance = report['performance_summary']
    
    for metric_name, data in performance.items():
        trend_emoji = {
            'improving': '📈',
            'stable': '➡️', 
            'declining': '📉'
        }.get(data['trend'], '❓')
        
        print(f"{trend_emoji} {metric_name}:")
        print(f"   Базовая: {data['baseline']:.3f}")
        print(f"   Текущая: {data['current']:.3f}")
        print(f"   Улучшение: {data['improvement_rate']:.1%}")
        print(f"   Тренд: {data['trend']}")
        print()
    
    # Показать созданные инструменты
    if smart_agent.tool_creator.created_tools:
        print("🛠️ СОЗДАННЫЕ ИНСТРУМЕНТЫ:")
        for tool in smart_agent.tool_creator.created_tools:
            print(f"• {tool['name']}")
            print(f"  Назначение: {tool['purpose']}")
            print(f"  Создан: {tool['created_at']}")
            print()
    
    # Показать историю оптимизаций
    if smart_agent.self_optimizer.optimization_history:
        print("🔧 ИСТОРИЯ ОПТИМИЗАЦИЙ:")
        for action in smart_agent.self_optimizer.optimization_history:
            print(f"• {action.action_type}: {action.description}")
            print(f"  Ожидаемое улучшение: {action.expected_improvement:.1%}")
            print(f"  Время: {action.timestamp.strftime('%H:%M:%S')}")
            print()
    
    print("=" * 50)
    print("🎯 ВЫВОДЫ:")
    
    # Анализ результатов
    total_improvement = sum(
        data['improvement_rate'] 
        for data in performance.values()
    ) / len(performance) if performance else 0
    
    if total_improvement > 0.1:
        print("✅ Агент показал значительное улучшение производительности!")
    elif total_improvement > 0:
        print("📈 Агент показал умеренное улучшение производительности")
    else:
        print("➡️ Производительность агента стабильна")
    
    print(f"📊 Среднее улучшение: {total_improvement:.1%}")
    print(f"🛠️ Автономно создано инструментов: {len(smart_agent.tool_creator.created_tools)}")
    print(f"🔧 Применено оптимизаций: {len(smart_agent.self_optimizer.optimization_history)}")
    
    print("\n🚀 Демонстрация завершена!")
    print("Агент успешно продемонстрировал способности к самооценке и улучшению!")

if __name__ == "__main__":
    main() 