#!/usr/bin/env python3
"""
🐱 KittyCore 3.0 - CLI с ValidatorKitty

Интеллектуальный валидатор результатов:
1. Анализирует запрос → создает образ результата
2. Показывает пользователю → получает подтверждение  
3. Агенты работают → создают результат
4. Валидатор проверяет → отправляет на доработку если нужно
"""

import asyncio
import sys
import kittycore
from core.validator_kitty import ValidatorKitty, ResultExpectation, ValidationResult
# from core.memory_management import MemoryManager

def format_files_created(result):
    """Форматировать список созданных файлов"""
    execution = result.get('execution', {})
    files = execution.get('files_created', [])
    
    if files:
        files_count = len(files)
        files_text = "\n".join([f"   📄 {file}" for file in files])
        return f"\n📁 СОЗДАННЫЕ ФАЙЛЫ ({files_count}):\n{files_text}"
    return "\n📁 СОЗДАННЫЕ ФАЙЛЫ:\n   (файлы не создавались)"

def format_execution_results(result):
    """Форматировать результаты выполнения"""
    execution = result.get('execution', {})
    step_results = execution.get('step_results', {})
    
    if not step_results:
        return "   (детали выполнения недоступны)"
    
    formatted = []
    for step_id, step_result in step_results.items():
        status_icon = "✅" if step_result.get('status') == 'completed' else "❌"
        agent = step_result.get('agent', 'unknown')
        result_text = step_result.get('result', 'No result')
        formatted.append(f"   {status_icon} {agent}: {result_text}")
    
    return "\n".join(formatted)

async def get_user_approval(expectation: ResultExpectation) -> tuple[bool, str]:
    """
    ФАЗА 2: Получение подтверждения от пользователя
    """
    validator = ValidatorKitty()
    
    # Показываем образ результата
    expectation_text = validator.format_expectation_for_user(expectation)
    print(expectation_text)
    
    while True:
        try:
            response = input("➤ Твой ответ: ").strip().lower()
            
            if response in ['да', 'yes', 'y', 'д', '+', '1']:
                return True, ""
            elif response in ['нет', 'no', 'n', 'н', '-', '0']:
                return False, ""
            elif response.startswith('уточни') or 'уточнения' in response:
                clarification = input("📝 Какие уточнения нужны? ")
                return False, clarification
            else:
                print("❓ Пожалуйста, ответь: 'да', 'нет' или 'уточни'")
                
        except KeyboardInterrupt:
            return False, ""

async def process_request_with_validator(user_input: str):
    """
    Обработка запроса с ValidatorKitty workflow
    """
    print(f"\n🔍 Обрабатываю запрос: {user_input}")
    print("=" * 50)
    
    # Создаем компоненты
    validator = ValidatorKitty()
    
    # ФАЗА 1: Анализ запроса и создание образа результата
    print("\n🎯 ФАЗА 1: Анализ запроса")
    print("ValidatorKitty анализирует что должно получиться...")
    
    expectation = await validator.analyze_request(user_input)
    
    # ФАЗА 2: Показать образ пользователю и получить подтверждение
    print("\n👤 ФАЗА 2: Подтверждение ожиданий")
    approved, clarification = await get_user_approval(expectation)
    
    if not approved:
        if clarification:
            print(f"\n📝 Получены уточнения: {clarification}")
            print("🔄 Перенализируем запрос с уточнениями...")
            # Можно здесь модифицировать expectation на основе уточнений
            user_input = f"{user_input}. Уточнения: {clarification}"
        else:
            print("❌ Задача отменена пользователем")
            return
    
    expectation.user_approved = True
    print("✅ Ожидания подтверждены! Запускаем агентов...")
    
    # ФАЗА 3: Выполнение задачи агентами
    print("\n🤖 ФАЗА 3: Выполнение агентами")
    print("Агенты работают над задачей...")
    
    orchestrator = kittycore.create_orchestrator()
    result = await orchestrator.solve_task(user_input)
    
    if result['status'] == 'completed':
        print(f"✅ Агенты завершили работу за {result['duration']:.2f}с")
        
        # ФАЗА 4: Валидация результата
        print("\n🔍 ФАЗА 4: Валидация результата")
        print("ValidatorKitty проверяет соответствие ожиданиям...")
        
        execution = result.get('execution', {})
        created_files = execution.get('files_created', [])
        step_results = execution.get('step_results', {})
        
        validation_result = await validator.validate_results(
            expectation, created_files, step_results
        )
        
        # Показываем результат валидации
        validation_text = validator.format_validation_result(validation_result)
        print(validation_text)
        
        # ФАЗА 5: Решение о доработке или принятии
        if validation_result.retry_needed:
            print("\n🔄 ФАЗА 5: Требуется доработка")
            
            retry_decision = input("🤔 Отправить на доработку? (да/нет): ").strip().lower()
            
            if retry_decision in ['да', 'yes', 'y', 'д']:
                print("🔄 Отправляем задачу на доработку...")
                # Здесь можно запустить повторное выполнение с улучшенными инструкциями
                print("⚠️ Функция доработки будет реализована в следующей версии")
            else:
                print("✅ Принимаем результат как есть")
        
        # Показываем детальную информацию
        print(f"\n📊 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ:")
        print(f"📊 Сложность: {result['complexity_analysis']['complexity']}")
        print(f"👥 Команда: {result['team']['team_size']} агентов")
        
        print(f"\n📋 План решения:")
        for i, subtask in enumerate(result['subtasks'], 1):
            print(f"   {i}. {subtask['description']}")
        
        print(f"\n📈 Workflow:")
        print(result['workflow_graph']['mermaid'])
        
        print(format_files_created(result))
        
        print(f"\n🔧 ВЫПОЛНЕННЫЕ ДЕЙСТВИЯ:")
        print(format_execution_results(result))
        
        # Статистика коллективной памяти
        memory_stats = result.get('collective_memory_stats', {})
        if memory_stats:
            print(f"\n🧠 КОЛЛЕКТИВНАЯ ПАМЯТЬ:")
            print(f"   📝 Записей: {memory_stats.get('total_entries', 0)}")
            print(f"   👥 Агентов: {memory_stats.get('agents', 0)}")
        
    else:
        print(f"❌ Ошибка выполнения: {result.get('error', 'Неизвестная ошибка')}")

async def main():
    print("🐱 KittyCore 3.0 - CLI с ValidatorKitty")
    print("=" * 45)
    print("🎯 Умная валидация результатов:")
    print("   1. Анализирую запрос → создаю образ результата")
    print("   2. Показываю тебе → получаю подтверждение") 
    print("   3. Агенты работают → создают результат")
    print("   4. Проверяю качество → отправляю на доработку если нужно")
    print("\nВведи 'exit' для выхода\n")
    
    while True:
        try:
            user_input = input("💬 Твой запрос: ").strip()
            
            if user_input.lower() in ['exit', 'выход', 'quit']:
                print("👋 До свидания!")
                break
            
            if not user_input:
                continue
                
            await process_request_with_validator(user_input)
            print("\n" + "="*50)
            
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 