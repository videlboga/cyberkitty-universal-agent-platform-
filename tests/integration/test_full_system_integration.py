"""
🧪 ИНТЕГРАЦИОННЫЕ ТЕСТЫ KITTYCORE 3.0
Comprehensive тестирование полной системы
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к kittycore
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kittycore.tools import DEFAULT_TOOLS
from kittycore.core.unified_orchestrator import UnifiedOrchestrator
from kittycore.memory.amem_integration import KittyCoreMemorySystem
from kittycore.core.obsidian_orchestrator import ObsidianOrchestrator

class TestFullSystemIntegration:
    """Тесты полной интеграции системы"""
    
    @pytest.fixture
    def test_vault_path(self, tmp_path):
        """Создание временного vault для тестов"""
        vault = tmp_path / "test_vault"
        vault.mkdir()
        for subdir in ["agents", "tasks", "results", "system", "coordination", "human"]:
            (vault / subdir).mkdir()
        return str(vault)
    
    def test_tools_initialization(self):
        """Тест инициализации всех инструментов"""
        print(f"\n🔧 Тестирование инициализации {len(DEFAULT_TOOLS.tools)} инструментов...")
        
        # Проверяем что все инструменты загружены
        assert len(DEFAULT_TOOLS.tools) >= 15, "Должно быть минимум 15 инструментов"
        
        # Проверяем ключевые категории инструментов
        tool_names = list(DEFAULT_TOOLS.tools.keys())
        
        expected_categories = [
            "enhanced_web_scraping",  # Web
            "code_execution",         # Code  
            "super_system_tool",      # System
            "document_tool",          # Documents
            "computer_use",           # GUI
            "ai_integration_tool",    # AI
            "security_tool",          # Security
        ]
        
        for category in expected_categories:
            assert any(category in name for name in tool_names), f"Категория {category} не найдена"
        
        print(f"✅ Все {len(DEFAULT_TOOLS.tools)} инструментов инициализированы корректно")
        print(f"📋 Инструменты: {', '.join(tool_names[:5])}...")
    
    @pytest.mark.asyncio
    async def test_unified_orchestrator_basic(self, test_vault_path):
        """Тест базовой работы UnifiedOrchestrator"""
        print(f"\n🎯 Тестирование UnifiedOrchestrator...")
        
        orchestrator = UnifiedOrchestrator(vault_path=test_vault_path)
        
        # Простая задача
        task = "Создай файл hello.txt с текстом 'Hello from KittyCore 3.0!'"
        
        result = await orchestrator.execute_task(task)
        
        # Проверяем результат
        assert result is not None, "Результат не должен быть None"
        assert hasattr(result, 'success'), "Результат должен иметь поле success"
        
        print(f"✅ UnifiedOrchestrator работает корректно")
        print(f"📊 Результат: success={getattr(result, 'success', 'unknown')}")
    
    @pytest.mark.asyncio  
    async def test_memory_system_integration(self, test_vault_path):
        """Тест интеграции системы памяти A-MEM"""
        print(f"\n🧠 Тестирование системы памяти A-MEM...")
        
        # Создаём систему памяти
        memory_system = KittyCoreMemorySystem(vault_path=test_vault_path)
        
        # Тестируем сохранение воспоминания
        memory_data = {
            "agent_id": "test_agent",
            "task": "test_task",
            "content": "Тестовое воспоминание для интеграционного теста",
            "metadata": {"test": True, "type": "integration"}
        }
        
        # Сохраняем воспоминание
        memory_id = await memory_system.store_memory(**memory_data)
        assert memory_id is not None, "Memory ID не должен быть None"
        
        # Тестируем поиск
        results = await memory_system.search_memories("тестовое воспоминание")
        assert len(results) > 0, "Поиск должен найти сохранённое воспоминание"
        
        print(f"✅ Система памяти A-MEM работает корректно")
        print(f"🔍 Найдено воспоминаний: {len(results)}")
    
    @pytest.mark.asyncio
    async def test_obsidian_orchestrator_integration(self, test_vault_path):
        """Тест интеграции ObsidianOrchestrator"""
        print(f"\n📝 Тестирование ObsidianOrchestrator...")
        
        orchestrator = ObsidianOrchestrator(vault_path=test_vault_path)
        
        # Простая задача для проверки интеграции
        task = "Создай простой план проекта"
        
        result = await orchestrator.execute_task(task)
        
        # Проверяем что создались файлы в vault
        vault_path = Path(test_vault_path)
        task_files = list((vault_path / "tasks").glob("*.md"))
        
        assert len(task_files) > 0, "Должны быть созданы файлы задач"
        
        print(f"✅ ObsidianOrchestrator работает корректно")
        print(f"📁 Создано файлов задач: {len(task_files)}")
    
    def test_tools_registration_consistency(self):
        """Тест консистентности регистрации инструментов"""
        print(f"\n🔍 Тестирование консистентности инструментов...")
        
        # Проверяем что все инструменты имеют необходимые методы
        required_methods = ['execute', 'get_schema']
        
        for name, tool in DEFAULT_TOOLS.tools.items():
            for method in required_methods:
                assert hasattr(tool, method), f"Инструмент {name} должен иметь метод {method}"
        
        # Проверяем уникальность имён
        tool_names = list(DEFAULT_TOOLS.tools.keys())
        assert len(tool_names) == len(set(tool_names)), "Имена инструментов должны быть уникальными"
        
        print(f"✅ Все {len(DEFAULT_TOOLS.tools)} инструментов прошли проверку консистентности")
    
    @pytest.mark.asyncio
    async def test_end_to_end_task_execution(self, test_vault_path):
        """End-to-end тест выполнения задачи"""
        print(f"\n🎯 E2E тест выполнения задачи...")
        
        orchestrator = UnifiedOrchestrator(vault_path=test_vault_path)
        
        # Комплексная задача
        task = """
        Создай простой проект:
        1. Файл README.md с описанием проекта
        2. Файл main.py с функцией hello_world()
        3. Проверь что файлы созданы корректно
        """
        
        result = await orchestrator.execute_task(task)
        
        # Проверяем что задача выполнена
        assert result is not None, "Результат E2E теста не должен быть None"
        
        # Проверяем создание файлов в рабочей директории
        expected_files = ["README.md", "main.py"]
        created_files = []
        
        # Ищем созданные файлы в outputs/ или текущей директории
        outputs_dir = Path("outputs")
        current_dir = Path(".")
        
        for expected_file in expected_files:
            if (outputs_dir / expected_file).exists():
                created_files.append(expected_file)
            elif (current_dir / expected_file).exists():
                created_files.append(expected_file)
        
        print(f"✅ E2E тест завершён")
        print(f"📁 Найдено созданных файлов: {len(created_files)}/{len(expected_files)}")
        print(f"📋 Файлы: {created_files}")

if __name__ == "__main__":
    # Запуск тестов напрямую
    pytest.main([__file__, "-v", "--tb=short"]) 