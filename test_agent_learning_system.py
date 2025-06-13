"""
🧠 ТЕСТ СИСТЕМЫ НАКОПЛЕНИЯ ЗНАНИЙ АГЕНТОВ
Проверяем что агенты учатся от ошибок и накапливают опыт
"""

import asyncio
import json
from pathlib import Path

from kittycore.core.agent_learning_system import learning_system, AgentKnowledge
from kittycore.core.iterative_improvement import IterativeImprovement
from agents.smart_validator import SmartValidator, ValidationResult

async def test_learning_system():
    """Тестируем систему накопления знаний"""
    
    print("🧠 ТЕСТ СИСТЕМЫ НАКОПЛЕНИЯ ЗНАНИЙ АГЕНТОВ")
    print("=" * 60)
    
    # 1. Тестируем запись опыта обучения
    print("\n1️⃣ Тестируем запись опыта обучения...")
    
    lesson = await learning_system.record_learning(
        agent_id="test_agent",
        task_description="Создать файл с расчётом площади кота",
        attempt_number=1,
        score_before=0.2,
        score_after=0.4,
        error_patterns=["Создал отчёт вместо файла", "Использовал неправильный инструмент"],
        successful_actions=["Использовал file_manager", "Создал файл area.txt"],
        failed_actions=["Использовал Python вместо code_generator"],
        feedback_received="Используй file_manager для создания файлов",
        tools_used=["file_manager", "Python"]
    )
    
    print(f"✅ Урок записан: {lesson}")
    
    # 2. Тестируем получение знаний агента
    print("\n2️⃣ Тестируем получение знаний агента...")
    
    knowledge = await learning_system.get_agent_knowledge("test_agent")
    print(f"📊 Знания агента:")
    print(f"   - Всего попыток: {knowledge.total_attempts}")
    print(f"   - Успешные паттерны: {knowledge.successful_patterns}")
    print(f"   - Паттерны ошибок: {knowledge.error_patterns}")
    print(f"   - Предпочтения инструментов: {knowledge.tool_preferences}")
    print(f"   - Уроки: {knowledge.lessons_learned}")
    
    # 3. Добавляем ещё один опыт
    print("\n3️⃣ Добавляем второй опыт обучения...")
    
    lesson2 = await learning_system.record_learning(
        agent_id="test_agent",
        task_description="Создать Python скрипт для расчёта",
        attempt_number=2,
        score_before=0.4,
        score_after=0.7,
        error_patterns=["Забыл импорт math"],
        successful_actions=["Использовал code_generator", "Добавил import math"],
        failed_actions=[],
        feedback_received="Всегда добавляй необходимые импорты",
        tools_used=["code_generator"]
    )
    
    print(f"✅ Второй урок записан: {lesson2}")
    
    # 4. Тестируем предложения по улучшению
    print("\n4️⃣ Тестируем предложения по улучшению...")
    
    suggestions = await learning_system.get_improvement_suggestions(
        agent_id="test_agent",
        current_task="Создать файл с расчётом объёма сферы",
        current_errors=["Создал отчёт вместо файла", "Забыл формулу"]
    )
    
    print(f"💡 Предложения по улучшению:")
    for suggestion in suggestions:
        print(f"   - {suggestion}")
    
    # 5. Проверяем файлы в vault
    print("\n5️⃣ Проверяем созданные файлы...")
    
    vault_path = Path("obsidian_vault")
    knowledge_dir = vault_path / "knowledge"
    
    if knowledge_dir.exists():
        learning_files = list(knowledge_dir.glob("learning_*.md"))
        knowledge_files = list(knowledge_dir.glob("knowledge_*.json"))
        
        print(f"📁 Файлы обучения: {len(learning_files)}")
        print(f"📁 Файлы знаний: {len(knowledge_files)}")
        
        # Показываем последний файл обучения
        if learning_files:
            latest_learning = max(learning_files, key=lambda f: f.stat().st_mtime)
            print(f"\n📄 Последний файл обучения: {latest_learning.name}")
            content = latest_learning.read_text(encoding='utf-8')
            print(content[:500] + "..." if len(content) > 500 else content)
        
        # Показываем файл знаний
        if knowledge_files:
            knowledge_file = knowledge_files[0]
            print(f"\n📄 Файл знаний: {knowledge_file.name}")
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                knowledge_data = json.load(f)
                print(json.dumps(knowledge_data, ensure_ascii=False, indent=2))
    
    print("\n✅ ТЕСТ СИСТЕМЫ ОБУЧЕНИЯ ЗАВЕРШЁН!")
    return True

async def test_iterative_improvement_with_learning():
    """Тестируем итеративное улучшение с системой обучения"""
    
    print("\n🔄 ТЕСТ ИТЕРАТИВНОГО УЛУЧШЕНИЯ С ОБУЧЕНИЕМ")
    print("=" * 60)
    
    # Создаём мок-агента
    class MockAgent:
        def __init__(self):
            self.agent_id = "learning_test_agent"
            self.attempt_count = 0
        
        async def execute_task(self):
            self.attempt_count += 1
            # Симулируем улучшение с каждой попыткой
            if self.attempt_count == 1:
                return {"output": "Отчёт о создании файла", "files_created": []}
            elif self.attempt_count == 2:
                return {"output": "Создан файл area.txt", "files_created": ["area.txt"]}
            else:
                return {"output": "Создан файл area.py с расчётом", "files_created": ["area.py"]}
    
    # Создаём мок-валидатор
    class MockValidator:
        def __init__(self):
            self.call_count = 0
        
        async def validate_result(self, original_task, result, created_files):
            self.call_count += 1
            # Симулируем улучшение оценок
            if self.call_count == 1:
                return ValidationResult(
                    is_valid=False,
                    score=0.2,
                    user_benefit="Получен отчёт вместо файла",
                    issues=["Создал отчёт вместо файла"],
                    recommendations=["Создать реальный файл"],
                    verdict="❌ НЕ ВАЛИДНО"
                )
            elif self.call_count == 2:
                return ValidationResult(
                    is_valid=False,
                    score=0.5,
                    user_benefit="Файл создан но пустой",
                    issues=["Файл создан но без содержимого"],
                    recommendations=["Добавить расчёт в файл"],
                    verdict="⚠️ ЧАСТИЧНО ВАЛИДНО"
                )
            else:
                return ValidationResult(
                    is_valid=True,
                    score=0.8,
                    user_benefit="Готовый рабочий файл с расчётом",
                    issues=[],
                    recommendations=["Отличная работа"],
                    verdict="✅ ВАЛИДНО"
                )
    
    # Тестируем
    agent = MockAgent()
    validator = MockValidator()
    improvement = IterativeImprovement()
    
    # Начальный результат
    initial_result = await agent.execute_task()
    initial_validation = await validator.validate_result(
        "Создать файл с расчётом площади", initial_result, []
    )
    
    print(f"🎯 Начальная оценка: {initial_validation.score:.1f}")
    
    # Запускаем итеративное улучшение
    final_result, attempts = await improvement.improve_agent_iteratively(
        agent=agent,
        task="Создать файл с расчётом площади",
        initial_result=initial_result,
        initial_validation=initial_validation,
        smart_validator=validator
    )
    
    print(f"\n📊 РЕЗУЛЬТАТЫ ИТЕРАТИВНОГО УЛУЧШЕНИЯ:")
    print(f"   - Количество попыток: {len(attempts)}")
    print(f"   - Финальная оценка: {final_result}")
    
    for i, attempt in enumerate(attempts, 1):
        improved_score = attempt.improved_validation.score if attempt.improved_validation else "N/A"
        print(f"   - Попытка {i}: {attempt.validation.score:.1f} → {improved_score} ({'✅' if attempt.success else '❌'})")
    
    # Проверяем что знания записались
    knowledge = await learning_system.get_agent_knowledge("learning_test_agent")
    print(f"\n🧠 НАКОПЛЕННЫЕ ЗНАНИЯ:")
    print(f"   - Всего попыток: {knowledge.total_attempts}")
    print(f"   - Уроки: {knowledge.lessons_learned}")
    
    print("\n✅ ТЕСТ ИТЕРАТИВНОГО УЛУЧШЕНИЯ С ОБУЧЕНИЕМ ЗАВЕРШЁН!")
    return True

async def main():
    """Запускаем все тесты"""
    
    try:
        # Тест 1: Система обучения
        await test_learning_system()
        
        # Тест 2: Итеративное улучшение с обучением
        await test_iterative_improvement_with_learning()
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("🧠 Система накопления знаний агентов работает!")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 