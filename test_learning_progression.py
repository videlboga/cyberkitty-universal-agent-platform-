#!/usr/bin/env python3
"""
📈 ТЕСТ ПРОГРЕССИИ ОБУЧЕНИЯ АГЕНТОВ
Проверяем как агенты учатся и улучшаются
"""

import asyncio
from kittycore.core.agent_learning_system import learning_system
from kittycore.core.iterative_improvement import IterativeImprovement
from agents.smart_validator import SmartValidator
from kittycore.agents.working_agent import WorkingAgent

async def test_learning_progression():
    """Тест прогрессии обучения"""
    print("📈 ТЕСТ ПРОГРЕССИИ ОБУЧЕНИЯ АГЕНТОВ")
    print("=" * 50)
    
    # Создаём агента для сложной задачи
    agent = WorkingAgent(
        role="math_developer",
        subtask={
            "description": "Создай Python скрипт для расчёта факториала числа 5",
            "expected_output": "Рабочий Python файл с функцией факториала"
        }
    )
    
    validator = SmartValidator()
    improvement = IterativeImprovement()
    
    print("🎯 Задача: Создай Python скрипт для расчёта факториала числа 5")
    
    try:
        # Первое выполнение
        print("\n1️⃣ ПЕРВОЕ ВЫПОЛНЕНИЕ:")
        result = await agent.execute_task()
        print(f"📄 Результат: {result.get('output', 'Нет вывода')[:100]}...")
        
        # Валидация
        validation = await validator.validate_result(
            original_task="Создай Python скрипт для расчёта факториала числа 5",
            result=result,
            created_files=result.get("files_created", [])
        )
        
        print(f"📊 Начальная оценка: {validation.score:.1f}/1.0")
        print(f"🔍 Проблемы: {', '.join(validation.issues)}")
        
        # Улучшение если нужно
        if validation.score < 0.7:
            print("\n🔄 ЗАПУСКАЕМ ИТЕРАТИВНОЕ УЛУЧШЕНИЕ:")
            
            final_result, attempts = await improvement.improve_agent_iteratively(
                agent=agent,
                task="Создай Python скрипт для расчёта факториала числа 5",
                initial_result=result,
                initial_validation=validation,
                smart_validator=validator
            )
            
            print(f"\n📈 РЕЗУЛЬТАТЫ УЛУЧШЕНИЯ:")
            print(f"   - Попыток: {len(attempts)}")
            print(f"   - Начальная оценка: {validation.score:.1f}")
            
            for i, attempt in enumerate(attempts, 1):
                if attempt.improved_validation:
                    print(f"   - Попытка {i}: {attempt.validation.score:.1f} → {attempt.improved_validation.score:.1f}")
                else:
                    print(f"   - Попытка {i}: {attempt.validation.score:.1f} → ошибка")
        
        # Проверяем накопленные знания
        print("\n🧠 НАКОПЛЕННЫЕ ЗНАНИЯ АГЕНТА:")
        knowledge = await learning_system.get_agent_knowledge("math_developer")
        
        print(f"   📊 Всего попыток: {knowledge.total_attempts}")
        print(f"   ✅ Успешные паттерны: {len(knowledge.successful_patterns)}")
        print(f"   ❌ Паттерны ошибок: {len(knowledge.error_patterns)}")
        print(f"   🔧 Предпочтения инструментов: {len(knowledge.tool_preferences)}")
        print(f"   📚 Уроки: {len(knowledge.lessons_learned)}")
        
        if knowledge.lessons_learned:
            print(f"\n💡 УРОКИ АГЕНТА:")
            for i, lesson in enumerate(knowledge.lessons_learned[-3:], 1):  # Последние 3 урока
                print(f"   {i}. {lesson}")
        
        if knowledge.tool_preferences:
            print(f"\n🔧 ПРЕДПОЧТЕНИЯ ИНСТРУМЕНТОВ:")
            for tool, count in knowledge.tool_preferences.items():
                print(f"   - {tool}: {count} успехов")
        
        if knowledge.successful_patterns:
            print(f"\n✅ УСПЕШНЫЕ ПАТТЕРНЫ:")
            for pattern in knowledge.successful_patterns[-2:]:  # Последние 2 паттерна
                print(f"   - {pattern}")
        
        return validation.score
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return 0.0

async def test_multiple_agents_learning():
    """Тест обучения нескольких агентов"""
    print("\n👥 ТЕСТ ОБУЧЕНИЯ НЕСКОЛЬКИХ АГЕНТОВ")
    print("=" * 50)
    
    agents_data = [
        ("file_creator", "Создай файл numbers.txt с числами от 1 до 10"),
        ("text_processor", "Создай файл greeting.txt с приветствием на русском"),
        ("data_formatter", "Создай файл info.txt с информацией о системе")
    ]
    
    scores = []
    
    for role, task in agents_data:
        print(f"\n🤖 Агент: {role}")
        print(f"🎯 Задача: {task}")
        
        agent = WorkingAgent(
            role=role,
            subtask={
                "description": task,
                "expected_output": "Текстовый файл"
            }
        )
        
        validator = SmartValidator()
        
        try:
            # Выполнение
            result = await agent.execute_task()
            
            # Валидация
            validation = await validator.validate_result(
                original_task=task,
                result=result,
                created_files=result.get("files_created", [])
            )
            
            print(f"📊 Оценка: {validation.score:.1f}/1.0")
            scores.append((role, validation.score))
            
            # Записываем опыт в систему обучения
            await learning_system.record_learning(
                agent_id=role,
                task_description=task,
                attempt_number=1,
                score_before=0.0,
                score_after=validation.score,
                error_patterns=validation.issues,
                successful_actions=["file_creation"] if validation.score > 0.5 else [],
                failed_actions=validation.issues,
                feedback_received=f"Оценка: {validation.score}",
                tools_used=["file_manager"]
            )
            
        except Exception as e:
            print(f"❌ Ошибка агента {role}: {e}")
            scores.append((role, 0.0))
    
    # Итоговая статистика
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    total_score = 0
    for role, score in scores:
        print(f"   {role}: {score:.1f}/1.0")
        total_score += score
    
    avg_score = total_score / len(scores) if scores else 0
    print(f"\n🏆 Средняя оценка: {avg_score:.1f}/1.0")
    
    return avg_score

async def main():
    """Запуск всех тестов прогрессии"""
    print("📈 ТЕСТИРОВАНИЕ ПРОГРЕССИИ ОБУЧЕНИЯ")
    print("=" * 60)
    
    try:
        # Тест 1: Прогрессия одного агента
        score1 = await test_learning_progression()
        
        # Тест 2: Обучение нескольких агентов
        score2 = await test_multiple_agents_learning()
        
        # Общие результаты
        print(f"\n🏆 ОБЩИЕ РЕЗУЛЬТАТЫ:")
        print(f"   Прогрессия агента: {score1:.1f}/1.0")
        print(f"   Средняя по команде: {score2:.1f}/1.0")
        
        overall_score = (score1 + score2) / 2
        print(f"   Общая оценка: {overall_score:.1f}/1.0")
        
        if overall_score >= 0.7:
            print("\n🎉 ПРЕВОСХОДНЫЙ РЕЗУЛЬТАТ! Система обучения работает отлично!")
        elif overall_score >= 0.5:
            print("\n👍 ХОРОШИЙ РЕЗУЛЬТАТ! Система показывает прогресс!")
        else:
            print("\n⚠️ ТРЕБУЕТСЯ ДОРАБОТКА!")
        
        print("\n✅ ВСЕ ТЕСТЫ ПРОГРЕССИИ ЗАВЕРШЕНЫ!")
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 