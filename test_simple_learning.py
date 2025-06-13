#!/usr/bin/env python3
"""
🧠 ПРОСТОЙ ТЕСТ СИСТЕМЫ ОБУЧЕНИЯ
"""

import asyncio
from kittycore.core.agent_learning_system import learning_system
from kittycore.core.iterative_improvement import IterativeImprovement
from agents.smart_validator import SmartValidator
from kittycore.agents.working_agent import WorkingAgent

async def test_simple_learning():
    """Простой тест обучения агента"""
    print("🧠 ПРОСТОЙ ТЕСТ СИСТЕМЫ ОБУЧЕНИЯ")
    print("=" * 40)
    
    # Создаём агента
    agent = WorkingAgent(
        role="simple_developer",
        subtask={
            "description": "Создай файл hello.py с print('Hello World')",
            "expected_output": "Python файл"
        }
    )
    
    validator = SmartValidator()
    improvement = IterativeImprovement()
    
    print("🎯 Задача: Создай файл hello.py с print('Hello World')")
    
    try:
        # Выполнение
        result = await agent.execute_task()
        print(f"📄 Результат: {result.get('output', 'Нет вывода')[:100]}...")
        
        # Валидация
        validation = await validator.validate_result(
            original_task="Создай файл hello.py с print('Hello World')",
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
                task="Создай файл hello.py с print('Hello World')",
                initial_result=result,
                initial_validation=validation,
                smart_validator=validator,
                max_attempts=2  # Ограничиваем попытки
            )
            
            print(f"📈 Попыток улучшения: {len(attempts)}")
            if attempts and attempts[-1].improved_validation:
                print(f"📊 Финальная оценка: {attempts[-1].improved_validation.score:.1f}")
        
        # Проверяем накопленные знания
        print("\n🧠 ПРОВЕРЯЕМ НАКОПЛЕННЫЕ ЗНАНИЯ:")
        knowledge = await learning_system.get_agent_knowledge("simple_developer")
        
        print(f"   📊 Всего попыток: {knowledge.total_attempts}")
        print(f"   ✅ Успешные паттерны: {len(knowledge.successful_patterns)}")
        print(f"   ❌ Паттерны ошибок: {len(knowledge.error_patterns)}")
        print(f"   📚 Уроки: {len(knowledge.lessons_learned)}")
        
        if knowledge.lessons_learned:
            print(f"   💡 Последний урок: {knowledge.lessons_learned[-1]}")
        
        return validation.score
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return 0.0

async def main():
    """Запуск простого теста"""
    print("🌍 ПРОСТОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ ОБУЧЕНИЯ")
    print("=" * 50)
    
    try:
        score = await test_simple_learning()
        
        print(f"\n🏆 ИТОГОВЫЙ РЕЗУЛЬТАТ: {score:.1f}/1.0")
        
        if score >= 0.7:
            print("🎉 ОТЛИЧНЫЙ РЕЗУЛЬТАТ! Система обучения работает!")
        elif score >= 0.4:
            print("👍 ХОРОШИЙ РЕЗУЛЬТАТ! Система показывает прогресс!")
        else:
            print("⚠️ ТРЕБУЕТСЯ ДОРАБОТКА!")
            
        print("\n✅ ПРОСТОЙ ТЕСТ ЗАВЕРШЁН!")
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 