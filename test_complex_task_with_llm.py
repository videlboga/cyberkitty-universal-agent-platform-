#!/usr/bin/env python3
"""
🎯 ТЕСТИРОВАНИЕ СЛОЖНЫХ ЗАДАЧ С LLM - KittyCore 3.0
Скрипт для тестирования UnifiedOrchestrator на реальных сложных задачах с LLM
"""

import asyncio
import os
import time
from datetime import datetime
from pathlib import Path

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig
from kittycore.config.base_config import Config


def setup_llm_provider():
    """Настройка LLM провайдера"""
    
    # Проверяем API ключ
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("❌ OPENROUTER_API_KEY не найден!")
        print("\n🔧 Для работы с LLM нужно настроить API ключ:")
        print("1. Идите на https://openrouter.ai")
        print("2. Создайте аккаунт (бесплатно)")
        print("3. Получите API ключ в разделе Keys")
        print("4. Установите переменную окружения:")
        print("   export OPENROUTER_API_KEY='sk-or-v1-ваш-ключ-здесь'")
        print("\n🆓 Доступны БЕСПЛАТНЫЕ модели навсегда!")
        return False
    
    print(f"✅ LLM API ключ найден: {api_key[:20]}...{api_key[-10:]}")
    return True


# Простые задачи для тестирования
SIMPLE_TASKS = {
    "hello_world": {
        "difficulty": "⭐",
        "category": "Простая задача",
        "task": "Создай простой Python скрипт, который выводит 'Hello, World!' и сохрани его в файл hello.py",
        "expected_outputs": ["python_script"],
        "time_limit": 60  # 1 минута
    },
    
    "simple_calculation": {
        "difficulty": "⭐⭐",
        "category": "Вычисления",
        "task": "Создай Python скрипт для расчёта площади круга. Скрипт должен принимать радиус и выводить площадь. Сохрани в файл circle_area.py",
        "expected_outputs": ["python_script"],
        "time_limit": 120  # 2 минуты
    },
    
    "data_analysis_mini": {
        "difficulty": "⭐⭐⭐",
        "category": "Анализ данных",
        "task": """
Создай простую систему анализа данных:

1. Сгенерируй CSV файл с тестовыми данными продаж (50 записей)
2. Создай Python скрипт для анализа этих данных
3. Найди общую сумму продаж
4. Создай простой отчёт в текстовом файле

Результат: CSV файл + Python скрипт + текстовый отчёт
        """,
        "expected_outputs": ["csv_data", "python_script", "text_report"],
        "time_limit": 300  # 5 минут
    }
}


async def run_simple_task_test(task_name: str, orchestrator: UnifiedOrchestrator):
    """Запуск теста простой задачи"""
    
    if task_name not in SIMPLE_TASKS:
        print(f"❌ Задача '{task_name}' не найдена!")
        return None
    
    task_config = SIMPLE_TASKS[task_name]
    
    print(f"\n🎯 ЗАПУСК ТЕСТА: {task_name}")
    print(f"📊 Сложность: {task_config['difficulty']}")
    print(f"📂 Категория: {task_config['category']}")
    print(f"⏱️ Лимит времени: {task_config['time_limit']} секунд")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Запуск задачи
        result = await orchestrator.solve_task(task_config['task'])
        
        execution_time = time.time() - start_time
        
        # Анализ результатов
        print(f"\n✅ ЗАДАЧА ЗАВЕРШЕНА за {execution_time:.1f} секунд")
        print(f"📋 Статус: {result.get('status', 'unknown')}")
        print(f"📊 Оценка качества: {result.get('quality_score', 'N/A')}")
        
        # Проверка ожидаемых выходов
        created_files = result.get('created_files', [])
        print(f"\n📁 Созданные файлы ({len(created_files)}):")
        for file_path in created_files:
            print(f"  - {file_path}")
        
        # Проверка содержимого файлов
        print(f"\n📄 Содержимое созданных файлов:")
        for file_path in created_files:
            if Path(file_path).exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"\n--- {file_path} ---")
                        print(content[:500] + ("..." if len(content) > 500 else ""))
                except Exception as e:
                    print(f"❌ Ошибка чтения {file_path}: {e}")
        
        # Оценка успешности
        success_score = evaluate_task_success(task_config, result, execution_time)
        print(f"\n🎯 ИТОГОВАЯ ОЦЕНКА: {success_score:.1f}/10.0")
        
        return {
            "task_name": task_name,
            "success_score": success_score,
            "execution_time": execution_time,
            "result": result
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"\n❌ ОШИБКА при выполнении задачи: {e}")
        print(f"⏱️ Время до ошибки: {execution_time:.1f} секунд")
        
        return {
            "task_name": task_name,
            "success_score": 0.0,
            "execution_time": execution_time,
            "error": str(e)
        }


def evaluate_task_success(task_config, result, execution_time):
    """Оценка успешности выполнения задачи"""
    
    score = 0.0
    max_score = 10.0
    
    # 1. Базовая успешность (4 балла)
    if result.get('status') == 'completed':
        score += 4.0
    elif result.get('status') == 'partial':
        score += 2.0
    
    # 2. Качество результата (3 балла)
    quality_score = result.get('quality_score', 0)
    if quality_score:
        score += quality_score * 3.0
    
    # 3. Соблюдение времени (2 балла)
    time_limit = task_config['time_limit']
    if execution_time <= time_limit:
        score += 2.0
    elif execution_time <= time_limit * 1.5:
        score += 1.0
    
    # 4. Создание файлов (1 балл)
    created_files = result.get('created_files', [])
    if created_files:
        score += 1.0
    
    return min(score, max_score)


async def run_test_suite():
    """Запуск набора простых тестов"""
    
    print("🚀 ЗАПУСК ПРОСТЫХ ТЕСТОВ - KittyCore 3.0 с LLM")
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Проверка LLM
    if not setup_llm_provider():
        return
    
    # Инициализация системы
    vault_path = Path("test_vault_llm")
    vault_path.mkdir(exist_ok=True)
    
    config = UnifiedConfig(vault_path=str(vault_path))
    orchestrator = UnifiedOrchestrator(config)
    
    # Запуск тестов
    results = []
    
    for task_name in SIMPLE_TASKS.keys():
        result = await run_simple_task_test(task_name, orchestrator)
        if result:
            results.append(result)
        
        print("\n" + "="*60)
        await asyncio.sleep(2)  # Пауза между тестами
    
    # Итоговый отчёт
    print("\n🏆 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 60)
    
    total_score = 0
    successful_tasks = 0
    
    for result in results:
        task_name = result['task_name']
        score = result['success_score']
        time_taken = result['execution_time']
        
        status = "✅" if score >= 7.0 else "⚠️" if score >= 4.0 else "❌"
        print(f"{status} {task_name}: {score:.1f}/10.0 ({time_taken:.1f}s)")
        
        total_score += score
        if score >= 7.0:
            successful_tasks += 1
    
    avg_score = total_score / len(results) if results else 0
    success_rate = (successful_tasks / len(results) * 100) if results else 0
    
    print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"   Средняя оценка: {avg_score:.1f}/10.0")
    print(f"   Успешных задач: {successful_tasks}/{len(results)} ({success_rate:.1f}%)")
    print(f"   Всего тестов: {len(results)}")
    
    return results


if __name__ == "__main__":
    print("🎯 ПРОСТЫЕ ТЕСТЫ С LLM - KittyCore 3.0")
    print("\nВыберите режим тестирования:")
    print("1. Одна задача (быстро)")
    print("2. Все простые тесты")
    print("3. Выход")
    
    choice = input("\nВаш выбор (1-3): ").strip()
    
    if choice == "1":
        if not setup_llm_provider():
            exit(1)
            
        print("\nДоступные задачи:")
        for i, (task_name, config) in enumerate(SIMPLE_TASKS.items(), 1):
            print(f"{i}. {task_name} {config['difficulty']}")
        
        task_choice = input(f"\nВыберите задачу (1-{len(SIMPLE_TASKS)}): ").strip()
        
        try:
            task_index = int(task_choice) - 1
            task_name = list(SIMPLE_TASKS.keys())[task_index]
            
            # Инициализация системы
            vault_path = Path("test_vault_llm")
            vault_path.mkdir(exist_ok=True)
            
            config = UnifiedConfig(vault_path=str(vault_path))
            orchestrator = UnifiedOrchestrator(config)
            
            # Запуск одной задачи
            asyncio.run(run_simple_task_test(task_name, orchestrator))
            
        except (ValueError, IndexError):
            print("❌ Неверный выбор задачи!")
    
    elif choice == "2":
        # Запуск всех простых тестов
        asyncio.run(run_test_suite())
    
    elif choice == "3":
        print("👋 До свидания!")
    
    else:
        print("❌ Неверный выбор!") 