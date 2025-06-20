import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig

@pytest.mark.asyncio
async def test_metrics_and_vector_memory_integration():
    """Тест интеграции метрик и векторной памяти"""
    
    # Создаём конфигурацию с включёнными системами
    config = UnifiedConfig(
        vault_path="test_vault_part4",
        enable_obsidian_features=True,
        enable_metrics=True,
        enable_vector_memory=True,
        enable_quality_control=True,
        enable_human_intervention=False,
        enable_shared_chat=True
    )
    
    # Создаём оркестратор
    orchestrator = UnifiedOrchestrator(config)
    
    # Проверяем что системы инициализированы
    assert orchestrator.metrics_collector is not None
    assert orchestrator.vector_store is not None
    
    # Проверяем начальное состояние метрик
    initial_stats = orchestrator.metrics_collector.get_current_stats()
    assert initial_stats['active_tasks'] == 0
    assert initial_stats['active_agents'] == 0
    assert initial_stats['total_tasks_processed'] == 0
    
    # Проверяем векторную память (может содержать данные из предыдущих тестов)
    initial_vector_count = len(orchestrator.vector_store.vectors)
    
    print("✅ Тест интеграции метрик и векторной памяти пройден")

@pytest.mark.asyncio
async def test_metrics_tracking():
    """Тест отслеживания метрик"""
    
    config = UnifiedConfig(
        vault_path="test_vault_metrics",
        enable_metrics=True,
        enable_vector_memory=False,
        enable_human_intervention=False
    )
    
    orchestrator = UnifiedOrchestrator(config)
    
    # Тестируем отслеживание задачи
    task_metrics = orchestrator.metrics_collector.start_task_tracking(
        task_id="test_task_001",
        task_type="test",
        complexity_score=0.5
    )
    
    assert task_metrics.task_id == "test_task_001"
    assert task_metrics.complexity_score == 0.5
    assert task_metrics.end_time is None
    
    # Проверяем что задача в активных
    stats = orchestrator.metrics_collector.get_current_stats()
    assert stats['active_tasks'] == 1
    assert stats['total_tasks_processed'] == 1
    
    # Завершаем отслеживание
    finished_metrics = orchestrator.metrics_collector.finish_task_tracking(
        task_id="test_task_001",
        quality_score=0.8,
        files_created=3
    )
    
    assert finished_metrics.end_time is not None
    assert finished_metrics.quality_score == 0.8
    assert finished_metrics.files_created == 3
    
    # Проверяем что задача больше не активна
    final_stats = orchestrator.metrics_collector.get_current_stats()
    assert final_stats['active_tasks'] == 0
    
    print("✅ Тест отслеживания метрик пройден")

@pytest.mark.asyncio
async def test_vector_memory_operations():
    """Тест операций векторной памяти"""
    
    config = UnifiedConfig(
        vault_path="test_vault_vector",
        enable_metrics=False,
        enable_vector_memory=True,
        enable_human_intervention=False
    )
    
    orchestrator = UnifiedOrchestrator(config)
    
    # Добавляем решение в векторную память
    task_id = orchestrator.vector_store.add_task_solution(
        task_id="test_solution_001",
        task_description="Создать простое приложение",
        solution="Создано Python приложение с GUI",
        success_score=0.9,
        metadata={'task_type': 'application', 'complexity': 0.6}
    )
    
    assert task_id == "test_solution_001"
    assert len(orchestrator.vector_store.vectors) == 1
    
    # Тестируем поиск похожих задач
    similar_tasks = orchestrator.vector_store.search_similar_tasks(
        query="Создать приложение с интерфейсом",
        limit=3
    )
    
    assert len(similar_tasks) >= 1
    assert similar_tasks[0].entry.id == "test_solution_001"
    assert similar_tasks[0].similarity > 0.3
    
    # Тестируем получение успешных паттернов
    successful_patterns = orchestrator.vector_store.get_successful_patterns(
        min_success_score=0.8
    )
    
    assert len(successful_patterns) == 1
    assert successful_patterns[0].id == "test_solution_001"
    
    print("✅ Тест операций векторной памяти пройден")

if __name__ == "__main__":
    asyncio.run(test_metrics_and_vector_memory_integration())
    asyncio.run(test_metrics_tracking())
    asyncio.run(test_vector_memory_operations()) 