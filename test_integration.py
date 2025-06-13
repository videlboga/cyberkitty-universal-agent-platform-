#!/usr/bin/env python3
"""
🧪 Тест полной интеграции системы метрик и качества в OrchestratorAgent

Проверяем работу всех новых компонентов в связке:
- ✅ Система метрик агентов
- ✅ Векторная память для поиска
- ✅ Контроллер качества 
- ✅ Интеграция в OrchestratorAgent

ЦЕЛЬ: Убедиться, что всё работает вместе! 🚀
"""

import asyncio
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_orchestrator_integration():
    """Тест полной интеграции OrchestratorAgent с новыми компонентами"""
    print("🧪 Тестируем интеграцию OrchestratorAgent...")
    
    try:
        from kittycore.core.orchestrator import OrchestratorAgent, OrchestratorConfig
        
        # Создаём конфигурацию с включенными новыми компонентами
        config = OrchestratorConfig(
            orchestrator_id="test_orchestrator",
            enable_metrics=True,
            enable_vector_memory=True, 
            enable_quality_control=True,
            enable_obsidian=False  # Отключаем для теста
        )
        
        # Создаём оркестратор
        orchestrator = OrchestratorAgent(config)
        print("✅ OrchestratorAgent создан с новыми компонентами")
        
        # Проверяем инициализацию компонентов
        assert orchestrator.metrics_collector is not None, "MetricsCollector не инициализирован"
        assert orchestrator.vector_store is not None, "VectorStore не инициализирован"
        assert orchestrator.quality_controller is not None, "QualityController не инициализирован"
        print("✅ Все новые компоненты инициализированы")
        
        # Тестируем выполнение простой задачи
        test_task = "Создай файл с расчётом площади кота по формуле A = π * r²"
        
        print(f"🎯 Выполняем тестовую задачу: {test_task}")
        result = await orchestrator.solve_task(test_task)
        
        print("✅ Задача выполнена через OrchestratorAgent")
        
        # Проверяем результат
        assert result is not None, "Результат не получен"
        assert "status" in result, "Статус не найден в результате"
        print(f"✅ Получен результат: {result['status']}")
        
        # Проверяем валидацию качества
        if "validation" in result:
            validation = result["validation"]
            print(f"🎯 Контроль качества: {validation.get('verdict', 'неизвестно')} ({validation.get('quality_score', 0):.2f})")
            
            if "quality_details" in validation:
                details = validation["quality_details"]
                print(f"✅ Проверок пройдено: {details['passed_checks']}/{details['total_checks']}")
        
        # Проверяем статистику
        stats = orchestrator.get_statistics()
        print(f"📊 Статистика: обработано {stats['tasks_processed']} задач, создано {stats['agents_created']} агентов")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции OrchestratorAgent: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_metrics_in_action():
    """Тест работы метрик в реальном сценарии"""
    print("🧪 Тестируем метрики в действии...")
    
    try:
        from kittycore.core.agent_metrics import get_metrics_collector
        
        collector = get_metrics_collector()
        
        # Получаем текущую статистику
        initial_agent_count = len(collector.agent_metrics)
        
        # Симулируем выполнение задачи через оркестратор
        # (в реальности это будет происходить в solve_task)
        
        print(f"📊 Начальное количество агентов в метриках: {initial_agent_count}")
        
        # Получаем топ агентов
        top_agents = collector.get_top_agents(limit=3)
        print(f"✅ Топ агентов: {len(top_agents)}")
        
        for agent in top_agents:
            print(f"  - {agent.agent_id}: качество {agent.average_quality:.2f}, задач {agent.total_tasks}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования метрик: {e}")
        return False

async def test_vector_search_integration():
    """Тест поиска в векторной памяти"""
    print("🧪 Тестируем векторный поиск...")
    
    try:
        from kittycore.memory.vector_memory import get_vector_store
        
        store = get_vector_store()
        
        # Создаём тестовые документы
        test_docs_path = Path("test_knowledge")
        test_docs_path.mkdir(exist_ok=True)
        
        # Документ о котах
        cat_doc = test_docs_path / "cats_guide.md"
        cat_doc.write_text("""
# Руководство по котам

## Измерение котов

Площадь кота вычисляется по формуле A = π * r², где r - радиус кота в расслабленном состоянии.

Средний кот имеет радиус 0.3 метра, что даёт площадь ≈ 0.28 м².

## Поведение котов

Коты любят спать, есть и мурчать. Это основные активности.
""", encoding='utf-8')
        
        # Индексируем
        indexed = await store.index_documents(test_docs_path)
        print(f"✅ Проиндексировано документов: {indexed}")
        
        # Тестируем поиск
        if indexed > 0:
            results = await store.search("как измерить площадь кота", limit=2)
            print(f"✅ Результатов поиска: {len(results)}")
            
            if results:
                best = results[0]
                print(f"✅ Лучший результат: '{best.document.title}' (сходство: {best.similarity_score:.3f})")
                print(f"   Контекст: {best.relevance_context[:100]}...")
        
        # Очистка
        import shutil
        shutil.rmtree(test_docs_path, ignore_errors=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка векторного поиска: {e}")
        return False

async def main():
    """Главная функция интеграционного тестирования"""
    print("🚀 Запуск интеграционных тестов KittyCore 3.0 с новыми компонентами\n")
    
    results = []
    
    # Тест интеграции OrchestratorAgent
    results.append(await test_orchestrator_integration())
    print()
    
    # Тест метрик в действии
    results.append(await test_metrics_in_action())
    print()
    
    # Тест векторного поиска
    results.append(await test_vector_search_integration())
    print()
    
    # Итоги
    passed = sum(results)
    total = len(results)
    
    print("=" * 60)
    print(f"🎯 ИТОГИ ИНТЕГРАЦИОННОГО ТЕСТИРОВАНИЯ: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЯ ИНТЕГРАЦИЯ РАБОТАЕТ! Система метрик и качества успешно встроена в KittyCore 3.0!")
        print("💪 Агенты теперь будут работать профессионально под строгим контролем!")
    else:
        print("⚠️ Некоторые интеграционные тесты не прошли. Требуется доработка.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 