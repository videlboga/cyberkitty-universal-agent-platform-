#!/usr/bin/env python3
"""
🌍 ТЕСТ СИСТЕМЫ ОБУЧЕНИЯ НА РЕАЛЬНЫХ ЗАДАЧАХ
Проверяем как агенты учатся на практических примерах
"""

import asyncio
import os
from pathlib import Path

from kittycore.core.agent_learning_system import learning_system
from kittycore.core.iterative_improvement import IterativeImprovement
from agents.smart_validator import SmartValidator
from kittycore.agents.working_agent import WorkingAgent

async def test_calculator_task():
    """Тест создания калькулятора"""
    print("🧮 ТЕСТ: СОЗДАНИЕ КАЛЬКУЛЯТОРА")
    print("=" * 40)
    
    agent = WorkingAgent(
        role="calculator_developer",
        subtask={
            "description": "Создай простой калькулятор на Python",
            "expected_output": "Рабочий Python файл"
        }
    )
    
    validator = SmartValidator()
    improvement = IterativeImprovement()
    
    print("🎯 Задача: Создай простой калькулятор на Python")
    
    # Выполнение
    result = await agent.execute_task()
    print(f"📄 Результат: {result.get('output', 'Нет вывода')[:100]}...")
    
    # Валидация
    validation = await validator.validate_result(
        original_task="Создай простой калькулятор на Python",
        result=result,
        created_files=result.get("files_created", [])
    )
    
    print(f"📊 Оценка: {validation.score:.1f}/1.0")
    print(f"🔍 Проблемы: {', '.join(validation.issues)}")
    
    # Улучшение если нужно
    if validation.score < 0.7:
        print("\n🔄 Запускаем улучшение...")
        
        final_result, attempts = await improvement.improve_agent_iteratively(
            agent=agent,
            task="Создай простой калькулятор на Python",
            initial_result=result,
            initial_validation=validation,
            smart_validator=validator
        )
        
        print(f"📈 Попыток улучшения: {len(attempts)}")
        if attempts and attempts[-1].improved_validation:
            print(f"📊 Финальная оценка: {attempts[-1].improved_validation.score:.1f}")
    
    return validation.score

async def test_real_task_2_website():
    """Тест 2: Создание веб-сайта - от описания к HTML"""
    
    print("\n🌐 ТЕСТ 2: СОЗДАНИЕ ВЕБ-САЙТА")
    print("=" * 50)
    
    # Создаём агента для веб-разработки
    agent = WorkingAgent(
        role="web_developer", 
        subtask={
            "description": "Создай красивый сайт-портфолио для программиста",
            "expected_output": "HTML файл с CSS стилями"
        }
    )
    
    validator = SmartValidator()
    improvement = IterativeImprovement()
    
    print("🎯 Задача: Создай красивый сайт-портфолио для программиста")
    
    # Выполнение
    print("\n1️⃣ Выполнение задачи...")
    result = await agent.execute_task()
    print(f"📄 Результат: {result.get('output', 'Нет вывода')[:100]}...")
    
    # Валидация
    validation = await validator.validate_result(
        original_task="Создай красивый сайт-портфолио для программиста",
        result=result,
        created_files=result.get("files_created", [])
    )
    
    print(f"📊 Оценка: {validation.score:.1f}/1.0")
    print(f"🔍 Проблемы: {', '.join(validation.issues)}")
    
    # Улучшение если нужно
    if validation.score < 0.7:
        print("\n🔄 Запускаем улучшение...")
        
        final_result, attempts = await improvement.improve_agent_iteratively(
            agent=agent,
            task="Создай красивый сайт-портфолио для программиста", 
            initial_result=result,
            initial_validation=validation,
            smart_validator=validator
        )
        
        print(f"\n📈 РЕЗУЛЬТАТЫ:")
        print(f"   - Попыток: {len(attempts)}")
        if attempts and attempts[-1].improved_validation:
            print(f"   - Финальная оценка: {attempts[-1].improved_validation.score:.1f}")
        
        # Проверяем файлы
        files_created = final_result.get("files_created", [])
        if files_created:
            print(f"\n📁 Созданные файлы: {files_created}")
            for file_path in files_created:
                if os.path.exists(file_path) and file_path.endswith('.html'):
                    print(f"🌐 {file_path} - HTML файл создан")
                    # Проверяем что это реальный HTML
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if '<html>' in content.lower() and '<body>' in content.lower():
                                print("✅ Содержит валидную HTML структуру")
                            else:
                                print("⚠️ Возможно не валидный HTML")
                    except Exception as e:
                        print(f"❌ Ошибка проверки HTML: {e}")
    
    return validation.score

async def test_real_task_3_data_analysis():
    """Тест 3: Анализ данных - от CSV к отчёту"""
    
    print("\n📊 ТЕСТ 3: АНАЛИЗ ДАННЫХ")
    print("=" * 50)
    
    # Создаём тестовый CSV файл
    test_csv_content = """name,age,salary,department
Алексей,25,50000,IT
Мария,30,60000,Marketing
Иван,35,70000,IT
Анна,28,55000,HR
Петр,32,65000,IT
Елена,29,58000,Marketing"""
    
    with open("test_data.csv", "w", encoding="utf-8") as f:
        f.write(test_csv_content)
    
    print("📁 Создан тестовый файл test_data.csv")
    
    # Создаём агента для анализа данных
    agent = WorkingAgent(
        role="data_analyst",
        subtask={
            "description": "Проанализируй данные в файле test_data.csv и создай отчёт с выводами",
            "expected_output": "Python скрипт для анализа + файл с результатами"
        }
    )
    
    validator = SmartValidator()
    improvement = IterativeImprovement()
    
    print("🎯 Задача: Проанализируй данные в test_data.csv и создай отчёт")
    
    # Выполнение
    print("\n1️⃣ Выполнение анализа...")
    result = await agent.execute_task()
    print(f"📄 Результат: {result.get('output', 'Нет вывода')[:100]}...")
    
    # Валидация
    validation = await validator.validate_result(
        original_task="Проанализируй данные в test_data.csv и создай отчёт",
        result=result,
        created_files=result.get("files_created", [])
    )
    
    print(f"📊 Оценка: {validation.score:.1f}/1.0")
    print(f"🔍 Проблемы: {', '.join(validation.issues)}")
    
    # Улучшение если нужно
    if validation.score < 0.7:
        print("\n🔄 Запускаем улучшение...")
        
        final_result, attempts = await improvement.improve_agent_iteratively(
            agent=agent,
            task="Проанализируй данные в test_data.csv и создай отчёт",
            initial_result=result,
            initial_validation=validation,
            smart_validator=validator
        )
        
        print(f"\n📈 РЕЗУЛЬТАТЫ:")
        print(f"   - Попыток: {len(attempts)}")
        if attempts and attempts[-1].improved_validation:
            print(f"   - Финальная оценка: {attempts[-1].improved_validation.score:.1f}")
        
        # Проверяем результаты анализа
        files_created = final_result.get("files_created", [])
        if files_created:
            print(f"\n📁 Созданные файлы: {files_created}")
            for file_path in files_created:
                if os.path.exists(file_path):
                    print(f"✅ {file_path} - создан")
                    if file_path.endswith('.py'):
                        print("🐍 Python скрипт для анализа")
                    elif file_path.endswith(('.txt', '.md')):
                        print("📄 Файл с результатами анализа")
    
    return validation.score

async def test_learning_progression():
    """Тест прогрессии обучения - проверяем что агенты действительно учатся"""
    
    print("\n🧠 ТЕСТ ПРОГРЕССИИ ОБУЧЕНИЯ")
    print("=" * 50)
    
    # Получаем знания агентов после всех тестов
    agents_to_check = ["calculator_developer", "web_developer", "data_analyst"]
    
    for agent_id in agents_to_check:
        print(f"\n🤖 Агент: {agent_id}")
        
        knowledge = await learning_system.get_agent_knowledge(agent_id)
        
        print(f"   📊 Всего попыток: {knowledge.total_attempts}")
        print(f"   ✅ Успешные паттерны: {len(knowledge.successful_patterns)}")
        print(f"   ❌ Паттерны ошибок: {len(knowledge.error_patterns)}")
        print(f"   🔧 Предпочтения инструментов: {len(knowledge.tool_preferences)}")
        print(f"   📚 Уроки: {len(knowledge.lessons_learned)}")
        
        if knowledge.lessons_learned:
            print(f"   💡 Последний урок: {knowledge.lessons_learned[-1]}")
        
        if knowledge.tool_preferences:
            best_tool = max(knowledge.tool_preferences.items(), key=lambda x: x[1])
            print(f"   🏆 Лучший инструмент: {best_tool[0]} ({best_tool[1]} успехов)")

async def main():
    """Запускаем все реальные тесты"""
    
    print("🌍 ТЕСТИРОВАНИЕ СИСТЕМЫ ОБУЧЕНИЯ НА РЕАЛЬНЫХ ЗАДАЧАХ")
    print("=" * 70)
    
    scores = []
    
    try:
        # Тест 1: Калькулятор
        score1 = await test_calculator_task()
        scores.append(("Калькулятор", score1))
        
        # Тест 2: Веб-сайт
        score2 = await test_real_task_2_website()
        scores.append(("Веб-сайт", score2))
        
        # Тест 3: Анализ данных
        score3 = await test_real_task_3_data_analysis()
        scores.append(("Анализ данных", score3))
        
        # Тест прогрессии обучения
        await test_learning_progression()
        
        # Итоговая статистика
        print("\n🏆 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
        print("=" * 50)
        
        total_score = 0
        for task_name, score in scores:
            print(f"   {task_name}: {score:.1f}/1.0")
            total_score += score
        
        avg_score = total_score / len(scores)
        print(f"\n📊 Средняя оценка: {avg_score:.1f}/1.0")
        
        if avg_score >= 0.7:
            print("🎉 ОТЛИЧНЫЙ РЕЗУЛЬТАТ! Система обучения работает эффективно!")
        elif avg_score >= 0.5:
            print("👍 ХОРОШИЙ РЕЗУЛЬТАТ! Система показывает прогресс!")
        else:
            print("⚠️ ТРЕБУЕТСЯ ДОРАБОТКА! Система нуждается в улучшении!")
        
        # Проверяем файлы в vault
        vault_path = Path("obsidian_vault/knowledge")
        if vault_path.exists():
            learning_files = list(vault_path.glob("learning_*.md"))
            knowledge_files = list(vault_path.glob("knowledge_*.json"))
            
            print(f"\n📁 Файлы обучения в vault: {len(learning_files)}")
            print(f"📁 Файлы знаний в vault: {len(knowledge_files)}")
        
        print("\n✅ ВСЕ РЕАЛЬНЫЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В РЕАЛЬНЫХ ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 