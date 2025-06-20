import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig, create_unified_orchestrator

@pytest.mark.asyncio
async def test_llm_unavailable_handling():
    """Тест обработки недоступности LLM"""
    
    # Создаём конфигурацию
    config = UnifiedConfig(
        vault_path="test_vault_llm_error",
        enable_obsidian_features=True,
        enable_quality_control=True,
        enable_human_intervention=False,
        enable_shared_chat=True
    )
    
    # Создаём оркестратор с недоступным LLM
    orchestrator = UnifiedOrchestrator(config)
    
    # Убираем LLM провайдер
    orchestrator.task_analyzer.llm_provider = None
    
    # Тестируем задачу
    result = await orchestrator.solve_task("Создай простое приложение")
    
    # Проверяем результат
    assert result["status"] == "failed_llm_unavailable"
    assert result["error_type"] == "llm_not_initialized"
    assert "LLM" in result["error"]
    assert "Система требует LLM" in result["message"]
    
    # Проверяем что создана заметка об ошибке
    system_folder = Path(config.vault_path) / "system"
    error_files = list(system_folder.glob("llm_error_*.md"))
    assert len(error_files) > 0
    
    # Читаем содержимое заметки об ошибке
    error_content = error_files[0].read_text(encoding='utf-8')
    assert "Критическая ошибка: LLM недоступен" in error_content
    assert "Система не может работать без LLM" in error_content
    
    print("✅ Тест обработки недоступности LLM пройден")

@pytest.mark.asyncio 
async def test_llm_error_during_execution():
    """Тест обработки ошибки LLM во время выполнения"""
    
    config = UnifiedConfig(
        vault_path="test_vault_llm_runtime_error",
        enable_obsidian_features=True,
        enable_quality_control=True,
        enable_human_intervention=False,
        enable_shared_chat=True
    )
    
    orchestrator = UnifiedOrchestrator(config)
    
    # Мокаем LLM провайдер который падает во время работы
    mock_llm = AsyncMock()
    mock_llm.generate_response.side_effect = Exception("Connection timeout to LLM provider")
    orchestrator.task_analyzer.llm_provider = mock_llm
    
    # Тестируем задачу
    result = await orchestrator.solve_task("Создай сайт с котятами")
    
    # Проверяем результат
    assert result["status"] == "failed_llm_unavailable"
    assert result["error_type"] == "llm_unavailable"
    assert "LLM" in result["error"]
    
    # Проверяем что создана заметка об ошибке
    system_folder = Path(config.vault_path) / "system"
    error_files = list(system_folder.glob("llm_error_*.md"))
    assert len(error_files) > 0
    
    print("✅ Тест обработки ошибки LLM во время выполнения пройден")

if __name__ == "__main__":
    asyncio.run(test_llm_unavailable_handling())
    asyncio.run(test_llm_error_during_execution()) 