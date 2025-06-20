#!/usr/bin/env python3
"""
🧪 Тест системы метрик и качества KittyCore 3.0

Проверяем работу новых компонентов:
- ✅ Метрики агентов
- ✅ Векторная память  
- ✅ Контроллер качества

ЦЕЛЬ: Убедиться, что система работает! 🚀
"""

import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_metrics_system():
    """Тест системы метрик"""
    print("🧪 Тестируем систему метрик...")
    
    try:
        from kittycore.core.agent_metrics import MetricsCollector, TaskStatus, get_metrics_collector
        
        # Создаём сборщик метрик
        collector = get_metrics_collector()
        
        # Тестируем отслеживание задачи
        task_metric = collector.start_task_tracking(
            task_id="test_task_001", 
            agent_id="test_agent", 
            task_description="Тестовая задача для проверки метрик"
        )
        
        print(f"✅ Задача начата: {task_metric.task_id}")
        
        # Обновляем прогресс
        collector.update_task_progress("test_task_001", TaskStatus.IN_PROGRESS)
        print("✅ Прогресс обновлён")
        
        # Завершаем задачу
        collector.complete_task(
            task_id="test_task_001",
            quality_score=0.8,
            artifacts_created=2,
            errors=["Тестовая ошибка"],
            tools_used=["file_writer", "code_generator"],
            llm_calls=3
        )
        
        print("✅ Задача завершена")
        
        # Получаем метрики агента
        agent_metrics = collector.get_agent_performance("test_agent")
        if agent_metrics:
            print(f"✅ Метрики агента: качество {agent_metrics.average_quality:.2f}, задач {agent_metrics.total_tasks}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования метрик: {e}")
        return False

async def test_vector_memory():
    """Тест векторной памяти"""
    print("🧪 Тестируем векторную память...")
    
    try:
        from kittycore.memory.vector_memory import VectorMemoryStore
        
        # Создаём хранилище
        store = VectorMemoryStore("test_vector_storage")
        
        # Создаём тестовые документы
        test_docs_path = Path("test_documents")
        test_docs_path.mkdir(exist_ok=True)
        
        # Тестовый документ
        test_file = test_docs_path / "test_doc.md"
        test_file.write_text("""
# Тестовый документ

Это тестовый документ для проверки векторизации.
Содержит информацию о котах и их площади.

## Формула площади кота

Площадь кота можно рассчитать по формуле:
A = π * r²

Где r - радиус кота в состоянии покоя.
""", encoding='utf-8')
        
        # Индексируем документы
        indexed_count = await store.index_documents(test_docs_path)
        print(f"✅ Проиндексировано документов: {indexed_count}")
        
        # Тестируем поиск
        if indexed_count > 0:
            results = await store.search("площадь кота", limit=3)
            print(f"✅ Найдено результатов: {len(results)}")
            
            if results:
                best_result = results[0]
                print(f"✅ Лучший результат: {best_result.document.title} (сходство: {best_result.similarity_score:.2f})")
        
        # Очистка
        import shutil
        shutil.rmtree(test_docs_path, ignore_errors=True)
        shutil.rmtree("test_vector_storage", ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования векторной памяти: {e}")
        return False

async def test_quality_controller():
    """Тест контроллера качества"""
    print("🧪 Тестируем контроллер качества...")
    
    try:
        from kittycore.core.quality_controller import QualityController
        
        controller = QualityController()
        
        # Создаём тестовые артефакты
        test_artifacts_path = Path("test_artifacts")
        test_artifacts_path.mkdir(exist_ok=True)
        
        # Хороший файл
        good_file = test_artifacts_path / "good_result.txt"
        good_file.write_text("Это готовый результат работы. Файл создан и содержит полезную информацию. Задача выполнена успешно.", encoding='utf-8')
        
        # Плохой файл с планами
        bad_file = test_artifacts_path / "bad_result.txt"
        bad_file.write_text("План: нужно сделать файл. TODO: добавить содержимое. Планирую создать структуру.", encoding='utf-8')
        
        # Тестируем оценку качества
        assessment = await controller.assess_quality(
            task_description="Создать файл с результатами расчёта площади кота",
            result={"status": "completed", "message": "Файл создан и содержит результаты"},
            artifacts_paths=[good_file, bad_file]
        )
        
        print(f"✅ Оценка качества: {assessment.verdict} ({assessment.overall_score:.2f}/1.0)")
        print(f"✅ Пройдено проверок: {assessment.passed_checks}/{assessment.total_checks}")
        
        if assessment.fatal_issues:
            print(f"⚠️ Фатальные проблемы: {len(assessment.fatal_issues)}")
        
        # Очистка
        import shutil
        shutil.rmtree(test_artifacts_path, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования контроллера качества: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов системы метрик и качества KittyCore 3.0\n")
    
    results = []
    
    # Тест метрик
    results.append(await test_metrics_system())
    print()
    
    # Тест векторной памяти  
    results.append(await test_vector_memory())
    print()
    
    # Тест контроллера качества
    results.append(await test_quality_controller())
    print()
    
    # Итоги
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"🎯 ИТОГИ ТЕСТИРОВАНИЯ: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Система метрик и качества работает!")
    else:
        print("⚠️ Некоторые тесты не прошли. Требуется доработка.")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 