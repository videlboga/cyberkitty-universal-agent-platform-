#!/usr/bin/env python3
"""
🧪 Комплексный тест ObsidianOrchestrator - Часть 1: Базовая функциональность

ПРОВЕРЯЕТ:
✅ Создание и инициализацию ObsidianDB
✅ Сохранение и чтение заметок
✅ Создание агентов с workspace
✅ Базовую координацию между агентами
"""

import asyncio
import shutil
import json
from pathlib import Path
from datetime import datetime
from kittycore.core.obsidian_orchestrator import (
    ObsidianOrchestrator, create_obsidian_orchestrator
)
from kittycore.core.obsidian_db import ObsidianDB, ObsidianNote

class TestResults:
    """Класс для накопления результатов тестов"""
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
        
    def add_test(self, name: str, passed: bool, details: str = ""):
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {name}: ПРОЙДЕН")
        else:
            self.tests_failed += 1
            self.failures.append(f"{name}: {details}")
            print(f"❌ {name}: ПРОВАЛЕН - {details}")
        
        if details and passed:
            print(f"   📝 {details}")
    
    def get_summary(self):
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        return {
            "tests_run": self.tests_run,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "success_rate": success_rate,
            "failures": self.failures
        }

async def test_1_obsidian_db_basic(results: TestResults):
    """Тест 1: Базовая функциональность ObsidianDB"""
    print("\n🧪 ТЕСТ 1: Базовая функциональность ObsidianDB")
    
    vault_path = "./test_comprehensive_vault"
    if Path(vault_path).exists():
        shutil.rmtree(vault_path)
    
    try:
        # Создание ObsidianDB
        db = ObsidianDB(vault_path)
        results.add_test(
            "1.1 Создание ObsidianDB", 
            True, 
            f"Vault создан: {vault_path}"
        )
        
        # Создание заметки
        note = ObsidianNote(
            title="Тестовая заметка",
            content="Это тестовая заметка для проверки функциональности",
            tags=["test", "basic"],
            metadata={"test_id": "test_1", "timestamp": datetime.now().isoformat()},
            folder="test"
        )
        
        saved_path = db.save_note(note)
        results.add_test(
            "1.2 Сохранение заметки",
            Path(saved_path).exists(),
            f"Заметка сохранена: {saved_path}"
        )
        
        # Чтение заметки
        retrieved_note = db.get_note("Тестовая-заметка.md")
        results.add_test(
            "1.3 Чтение заметки",
            retrieved_note is not None and retrieved_note.title == "Тестовая заметка",
            f"Заметка прочитана: {retrieved_note.title if retrieved_note else 'None'}"
        )
        
        # Поиск заметок
        search_results = db.search_notes(metadata_filter={"test_id": "test_1"})
        results.add_test(
            "1.4 Поиск заметок",
            len(search_results) == 1,
            f"Найдено заметок: {len(search_results)}"
        )
        
        # Проверка структуры папок
        expected_folders = ["tasks", "agents", "coordination", "results", "system", "test"]
        vault_folders = [f.name for f in Path(vault_path).iterdir() if f.is_dir()]
        folders_created = all(folder in vault_folders for folder in expected_folders)
        results.add_test(
            "1.5 Структура папок",
            folders_created,
            f"Созданы папки: {vault_folders}"
        )
        
    except Exception as e:
        results.add_test("1.X Базовая функциональность", False, f"Ошибка: {str(e)}")

async def test_2_orchestrator_initialization(results: TestResults):
    """Тест 2: Инициализация ObsidianOrchestrator"""
    print("\n🧪 ТЕСТ 2: Инициализация ObsidianOrchestrator")
    
    vault_path = "./test_comprehensive_vault"
    
    try:
        # Создание оркестратора
        orchestrator = create_obsidian_orchestrator(vault_path)
        results.add_test(
            "2.1 Создание оркестратора",
            orchestrator is not None,
            f"Оркестратор создан с vault: {vault_path}"
        )
        
        # Проверка компонентов
        components_exist = all([
            hasattr(orchestrator, 'task_analyzer'),
            hasattr(orchestrator, 'task_decomposer'),
            hasattr(orchestrator, 'agent_spawner'),
            hasattr(orchestrator, 'execution_manager'),
            hasattr(orchestrator, 'db'),
            hasattr(orchestrator, 'task_manager')
        ])
        results.add_test(
            "2.2 Компоненты оркестратора",
            components_exist,
            "Все компоненты инициализированы"
        )
        
        # Проверка статистики
        stats = orchestrator.get_statistics()
        results.add_test(
            "2.3 Статистика оркестратора",
            'tasks_processed' in stats and 'vault_statistics' in stats,
            f"Статистика: {stats['tasks_processed']} задач обработано"
        )
        
    except Exception as e:
        results.add_test("2.X Инициализация оркестратора", False, f"Ошибка: {str(e)}")

async def test_3_simple_task_execution(results: TestResults):
    """Тест 3: Выполнение простой задачи"""
    print("\n🧪 ТЕСТ 3: Выполнение простой задачи")
    
    vault_path = "./test_comprehensive_vault"
    
    try:
        orchestrator = create_obsidian_orchestrator(vault_path)
        
        # Выполнение простой задачи
        task = "Создай простой Python скрипт для вычисления факториала"
        result = await orchestrator.solve_task(task, user_id="test_simple")
        
        results.add_test(
            "3.1 Выполнение задачи",
            result['status'] == 'completed',
            f"Статус: {result['status']}, Длительность: {result['duration']:.2f}с"
        )
        
        results.add_test(
            "3.2 Создание агентов",
            result['agents_created'] > 0,
            f"Создано агентов: {result['agents_created']}"
        )
        
        results.add_test(
            "3.3 Выполнение шагов",
            result['steps_completed'] > 0,
            f"Выполнено шагов: {result['steps_completed']}"
        )
        
        # Проверка результатов в ObsidianDB
        task_id = result['task_id']
        task_notes = orchestrator.db.search_notes(metadata_filter={"task_id": task_id})
        results.add_test(
            "3.4 Сохранение в ObsidianDB",
            len(task_notes) > 0,
            f"Создано заметок: {len(task_notes)}"
        )
        
        # Проверка создания файлов в vault
        vault_files = len(list(Path(vault_path).rglob("*.md")))
        results.add_test(
            "3.5 Создание заметок",
            vault_files > result.get('vault_notes_created', 0),
            f"Заметок в vault: {vault_files}"
        )
        
    except Exception as e:
        results.add_test("3.X Выполнение простой задачи", False, f"Ошибка: {str(e)}")

async def run_basic_tests():
    """Запуск базовых тестов"""
    print("🚀 ЗАПУСК БАЗОВЫХ ТЕСТОВ OBSIDIANORCHESTRATOR")
    print("=" * 60)
    
    results = TestResults()
    
    # Запуск тестов
    await test_1_obsidian_db_basic(results)
    await test_2_orchestrator_initialization(results)
    await test_3_simple_task_execution(results)
    
    # Итоги
    summary = results.get_summary()
    print("\n" + "=" * 60)
    print("📊 ИТОГИ БАЗОВЫХ ТЕСТОВ:")
    print(f"✅ Тестов пройдено: {summary['tests_passed']}/{summary['tests_run']}")
    print(f"📈 Успешность: {summary['success_rate']:.1f}%")
    
    if summary['failures']:
        print(f"\n❌ Провалившиеся тесты:")
        for failure in summary['failures']:
            print(f"   - {failure}")
    
    return summary

if __name__ == "__main__":
    asyncio.run(run_basic_tests()) 