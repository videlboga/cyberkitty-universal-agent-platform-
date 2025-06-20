#!/usr/bin/env python3
"""
🎯 ТЕСТИРОВАНИЕ СЛОЖНЫХ ЗАДАЧ - KittyCore 3.0
Скрипт для тестирования UnifiedOrchestrator на реальных сложных задачах
"""

import asyncio
import time
from datetime import datetime
from pathlib import Path

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig


# Сложные задачи для тестирования
COMPLEX_TASKS = {
    "data_analysis_simple": {
        "difficulty": "⭐⭐⭐",
        "category": "Анализ данных",
        "task": """
Создай простую систему анализа продаж для интернет-магазина:

1. Сгенерируй тестовые данные продаж за последние 3 месяца (1000 записей)
2. Проанализируй тренды продаж по категориям товаров
3. Найди топ-10 самых продаваемых товаров
4. Создай визуализацию динамики продаж
5. Подготовь краткий отчёт с выводами

Результат: Python скрипт + CSV файл + графики + отчёт в markdown
        """,
        "expected_outputs": ["python_script", "csv_data", "visualizations", "markdown_report"],
        "time_limit": 300  # 5 минут
    },
    
    "research_synthesis": {
        "difficulty": "⭐⭐⭐⭐",
        "category": "Исследование и синтез",
        "task": """
Проведи исследование современных тенденций в области искусственного интеллекта:

1. Найди информацию о последних достижениях в LLM (поиск в интернете)
2. Проанализируй ключевые тренды 2024-2025 года
3. Сравни подходы разных компаний (OpenAI, Google, Anthropic)
4. Оцени влияние на различные индустрии
5. Спрогнозируй развитие на ближайшие 2 года

Результат: Исследовательский отчёт + презентация + список источников
        """,
        "expected_outputs": ["research_report", "presentation", "sources_list"],
        "time_limit": 600  # 10 минут
    },
    
    "code_generation": {
        "difficulty": "⭐⭐⭐⭐",
        "category": "Создание систем",
        "task": """
Создай простое веб-приложение для управления задачами (TODO app):

1. Спроектируй архитектуру (frontend + backend + database)
2. Создай REST API с основными операциями (CRUD)
3. Реализуй простой веб-интерфейс
4. Добавь базовую аутентификацию
5. Напиши тесты для API
6. Создай Docker-контейнер для развёртывания

Результат: Полное веб-приложение + тесты + Docker + документация
        """,
        "expected_outputs": ["web_application", "api_tests", "docker_config", "documentation"],
        "time_limit": 900  # 15 минут
    }
}


async def run_complex_task_test(task_name: str, orchestrator: UnifiedOrchestrator):
    """Запуск теста сложной задачи"""
    
    if task_name not in COMPLEX_TASKS:
        print(f"❌ Задача '{task_name}' не найдена!")
        return None
    
    task_config = COMPLEX_TASKS[task_name]
    
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
    
    # 1. Базовая успешность (3 балла)
    if result.get('status') == 'completed':
        score += 3.0
    elif result.get('status') == 'partial':
        score += 1.5
    
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
    
    # 4. Полнота результата (2 балла)
    expected_outputs = task_config.get('expected_outputs', [])
    created_files = result.get('created_files', [])
    
    if expected_outputs:
        completion_ratio = min(len(created_files) / len(expected_outputs), 1.0)
        score += completion_ratio * 2.0
    
    return min(score, max_score)


async def run_benchmark_suite():
    """Запуск полного набора тестов"""
    
    print("🚀 ЗАПУСК BENCHMARK SUITE - KittyCore 3.0")
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Инициализация системы
    vault_path = Path("test_vault")
    vault_path.mkdir(exist_ok=True)
    
    config = UnifiedConfig(vault_path=str(vault_path))
    orchestrator = UnifiedOrchestrator(config)
    
    # Запуск тестов
    results = []
    
    for task_name in COMPLEX_TASKS.keys():
        result = await run_complex_task_test(task_name, orchestrator)
        if result:
            results.append(result)
        
        print("\n" + "="*60)
        await asyncio.sleep(2)  # Пауза между тестами
    
    # Итоговый отчёт
    print("\n🏆 ИТОГОВЫЕ РЕЗУЛЬТАТЫ BENCHMARK")
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
    
    # Сохранение результатов
    save_benchmark_results(results, avg_score, success_rate)
    
    return results


def save_benchmark_results(results, avg_score, success_rate):
    """Сохранение результатов бенчмарка"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"benchmark_results_{timestamp}.md"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write(f"# 🎯 Результаты Benchmark - KittyCore 3.0\n\n")
        f.write(f"**Дата**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Средняя оценка**: {avg_score:.1f}/10.0\n")
        f.write(f"**Успешность**: {success_rate:.1f}%\n\n")
        
        f.write("## Детальные результаты\n\n")
        
        for result in results:
            task_name = result['task_name']
            score = result['success_score']
            time_taken = result['execution_time']
            
            f.write(f"### {task_name}\n")
            f.write(f"- **Оценка**: {score:.1f}/10.0\n")
            f.write(f"- **Время**: {time_taken:.1f} секунд\n")
            
            if 'error' in result:
                f.write(f"- **Ошибка**: {result['error']}\n")
            
            f.write("\n")
    
    print(f"\n💾 Результаты сохранены в: {results_file}")


if __name__ == "__main__":
    print("🎯 COMPLEX TASKS BENCHMARK - KittyCore 3.0")
    print("\nВыберите режим тестирования:")
    print("1. Одна задача (быстро)")
    print("2. Полный benchmark (долго)")
    print("3. Выход")
    
    choice = input("\nВаш выбор (1-3): ").strip()
    
    if choice == "1":
        print("\nДоступные задачи:")
        for i, (task_name, config) in enumerate(COMPLEX_TASKS.items(), 1):
            print(f"{i}. {task_name} {config['difficulty']}")
        
        task_choice = input(f"\nВыберите задачу (1-{len(COMPLEX_TASKS)}): ").strip()
        
        try:
            task_index = int(task_choice) - 1
            task_name = list(COMPLEX_TASKS.keys())[task_index]
            
            # Инициализация системы
            vault_path = Path("test_vault")
            vault_path.mkdir(exist_ok=True)
            
            config = UnifiedConfig(vault_path=str(vault_path))
            orchestrator = UnifiedOrchestrator(config)
            
            # Запуск одной задачи
            asyncio.run(run_complex_task_test(task_name, orchestrator))
            
        except (ValueError, IndexError):
            print("❌ Неверный выбор задачи!")
    
    elif choice == "2":
        # Запуск полного benchmark
        asyncio.run(run_benchmark_suite())
    
    elif choice == "3":
        print("👋 До свидания!")
    
    else:
        print("❌ Неверный выбор!") 