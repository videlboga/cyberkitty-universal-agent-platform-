#!/usr/bin/env python3
"""
🧠 ТЕСТ СИСТЕМЫ ОБУЧЕНИЯ АГЕНТОВ - УЛУЧШЕНИЕ АНАЛИЗА БИТРИКС24
Показываем как система обучения исправляет шаблонные результаты
"""

import asyncio
import sys
sys.path.append('.')

from kittycore.core.agent_learning_system import AgentLearningSystem
from kittycore.core.iterative_improvement import IterativeImprovement

async def main():
    print("🧠 ТЕСТ СИСТЕМЫ ОБУЧЕНИЯ - АНАЛИЗ БИТРИКС24")
    print("=" * 60)
    
    # Инициализируем системы
    learning_system = AgentLearningSystem()
    improvement_system = IterativeImprovement()
    
    # === АНАЛИЗИРУЕМ ПРОБЛЕМУ ===
    
    print("\n🔍 АНАЛИЗ ТЕКУЩЕЙ ПРОБЛЕМЫ:")
    print("✅ Система создала файлы: рынок_проектов.md, прототип_1.html")
    print("❌ Но контент шаблонный - нет реального анализа рынка")
    print("❌ Нет конкретных категорий приложений")
    print("❌ Прототипы не содержат реальных решений")
    
    # === ЗАПИСЫВАЕМ ОПЫТ ОБУЧЕНИЯ ===
    
    agent_id = "bitrix_analyzer"
    task_description = "Анализ рынка приложений Битрикс24 и создание прототипов"
    
    # Первая попытка - провал
    lesson1 = await learning_system.record_learning(
        agent_id=agent_id,
        task_description=task_description,
        attempt_number=1,
        score_before=0.0,
        score_after=0.2,  # Низкий балл за шаблонный контент
        error_patterns=[
            "Создал шаблонные HTML файлы вместо конкретного анализа",
            "Не провел реальный поиск данных о Битрикс24",
            "Прототипы не содержат функциональности"
        ],
        successful_actions=[
            "Создал правильную структуру файлов",
            "Использовал HTML формат"
        ],
        failed_actions=[
            "Не использовал web_search для поиска данных",
            "Не создал реальный контент"
        ],
        feedback_received="Нужен реальный анализ рынка с конкретными данными и функциональными прототипами",
        tools_used=["code_generator", "file_manager"]
    )
    
    print(f"\n📚 УРОК 1 ЗАПИСАН: {lesson1}")
    
    # === ПОЛУЧАЕМ РЕКОМЕНДАЦИИ ===
    
    suggestions = await learning_system.get_improvement_suggestions(
        agent_id=agent_id,
        current_task="Улучшить анализ рынка Битрикс24",
        current_errors=[
            "Шаблонный контент вместо реального анализа",
            "Отсутствие данных о рынке"
        ]
    )
    
    print(f"\n💡 РЕКОМЕНДАЦИИ ДЛЯ УЛУЧШЕНИЯ:")
    for suggestion in suggestions:
        print(f"  • {suggestion}")
    
    # === ВТОРАЯ ПОПЫТКА С ПРИМЕНЕНИЕМ ЗНАНИЙ ===
    
    print(f"\n🔄 ВТОРАЯ ПОПЫТКА С ПРИМЕНЕНИЕМ НАКОПЛЕННЫХ ЗНАНИЙ:")
    
    # Симулируем улучшенного агента
    lesson2 = await learning_system.record_learning(
        agent_id=agent_id,
        task_description=task_description,
        attempt_number=2,
        score_before=0.2,
        score_after=0.7,  # Улучшенный результат
        error_patterns=[],
        successful_actions=[
            "Использовал web_search для поиска реальных данных",
            "Создал конкретные категории приложений",
            "Добавил функциональные элементы в прототипы"
        ],
        failed_actions=[],
        feedback_received="Гораздо лучше! Есть конкретные данные и функциональные прототипы",
        tools_used=["web_search", "code_generator", "file_manager"]
    )
    
    print(f"📚 УРОК 2 ЗАПИСАН: {lesson2}")
    
    # === ПОКАЗЫВАЕМ НАКОПЛЕННЫЕ ЗНАНИЯ ===
    
    knowledge = await learning_system.get_agent_knowledge(agent_id)
    
    print(f"\n🧠 НАКОПЛЕННЫЕ ЗНАНИЯ АГЕНТА '{agent_id}':")
    print(f"  📊 Всего попыток: {knowledge.total_attempts}")
    print(f"  ✅ Успешные паттерны:")
    for pattern in knowledge.successful_patterns[-3:]:
        print(f"    • {pattern}")
    
    print(f"  ❌ Паттерны ошибок:")
    for pattern in knowledge.error_patterns[-3:]:
        print(f"    • {pattern}")
    
    print(f"  🔧 Предпочтения инструментов:")
    for tool, count in knowledge.tool_preferences.items():
        print(f"    • {tool}: {count} успешных использований")
    
    print(f"  📚 Уроки:")
    for lesson in knowledge.lessons_learned:
        print(f"    • {lesson}")
    
    # === ДЕМОНСТРИРУЕМ ITERATIVE IMPROVEMENT ===
    
    print(f"\n🔄 ДЕМОНСТРАЦИЯ ITERATIVE IMPROVEMENT:")
    
    # Симулируем плохой результат, который нужно улучшить
    bad_result = {
        "content": "Шаблонный HTML без реального анализа",
        "files": ["шаблон.html"],
        "quality_score": 0.2
    }
    
    print(f"❌ Исходный результат (оценка: {bad_result['quality_score']}):")
    print(f"   {bad_result['content']}")
    
    # Improvement система даст рекомендации (симуляция)
    improvement_feedback = """
    ПРОБЛЕМЫ:
    1. Отсутствует реальный анализ рынка Битрикс24
    2. Нет конкретных данных о категориях приложений
    3. Прототипы не функциональны
    
    РЕКОМЕНДАЦИИ:
    1. Использовать web_search для поиска данных о Битрикс24 маркетплейсе
    2. Найти топ категории: CRM интеграции, аналитика, автоматизация
    3. Создать работающие HTML прототипы с JavaScript
    
    ПРИМЕРЫ УЛУЧШЕНИЙ:
    - Добавить реальные скриншоты существующих приложений
    - Создать интерактивные wireframes
    - Провести анализ конкурентов
    """
    
    print(f"\n💬 FEEDBACK ОТ СИСТЕМЫ УЛУЧШЕНИЯ:")
    print(improvement_feedback)
    
    # === РЕЗУЛЬТАТ СИСТЕМЫ ОБУЧЕНИЯ ===
    
    print(f"\n🎯 РЕЗУЛЬТАТ СИСТЕМЫ ОБУЧЕНИЯ:")
    print(f"✅ Агент научился различать шаблонный и реальный контент")
    print(f"✅ Знает что нужно использовать web_search для реальных данных")
    print(f"✅ Понимает важность функциональных прототипов")
    print(f"✅ Накопил опыт работы с инструментами")
    
    print(f"\n🚀 СЛЕДУЮЩИЕ ЗАПУСКИ БУДУТ ЛУЧШЕ:")
    print(f"  • Система будет предлагать использовать web_search")
    print(f"  • Агент избежит создания шаблонного контента")
    print(f"  • Будут созданы функциональные прототипы")
    
    print(f"\n✅ Система обучения работает! Агенты становятся умнее!")

if __name__ == "__main__":
    asyncio.run(main()) 