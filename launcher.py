#!/usr/bin/env python3
"""
🚀 KittyCore 3.0 Unified Launcher

Единая точка входа для всех сценариев работы:
- Ввод задачи
- Вывод процесса работы  
- Вывод путей к созданным файлам
- Human-in-the-loop интеграция

ПРИНЦИП: "Простота превыше всего"
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Добавляем путь к kittycore
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from kittycore.core.orchestrator import OrchestratorAgent, OrchestratorConfig


class SimpleLauncher:
    """
    🚀 Простой launcher для KittyCore 3.0
    
    Демонстрирует единую логику работы:
    - Obsidian-совместимое хранилище
    - Процесс работы агентов
    - Пути к результатам
    - Human-in-the-loop
    """
    
    def __init__(self):
        # Настраиваем единое хранилище
        self.vault_path = Path("./vault")
        self.vault_path.mkdir(exist_ok=True)
        
        # Создаём структуру папок
        folders = ["tasks", "agents", "results", "system", "coordination", "human"]
        for folder in folders:
            (self.vault_path / folder).mkdir(exist_ok=True)
        
        # Настраиваем оркестратор с Obsidian-совместимым хранилищем
        config = OrchestratorConfig(
            orchestrator_id="unified_launcher",
            enable_obsidian=True,
            obsidian_vault_path=str(self.vault_path),
            enable_human_intervention=True,
            enable_metrics=True,
            enable_vector_memory=True,
            enable_quality_control=True
        )
        
        self.orchestrator = OrchestratorAgent(config)
        
        logger.info(f"🚀 SimpleLauncher инициализирован")
        logger.info(f"📁 Единое хранилище: {self.vault_path}")
    
    async def run_task(self, task: str) -> Dict[str, Any]:
        """
        🎯 Выполнение задачи с выводом процесса
        
        Args:
            task: Описание задачи
            
        Returns:
            Результат с путями к файлам
        """
        print(f"\n🎯 ЗАДАЧА: {task}")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Выполняем задачу через оркестратор
            result = await self.orchestrator.solve_task(task, {"user_id": "launcher_user"})
            
            # Выводим процесс работы
            self._display_process(result)
            
            # Выводим созданные файлы
            created_files = self._collect_created_files()
            self._display_results(created_files)
            
            # Обновляем результат
            result["created_files"] = created_files
            result["vault_path"] = str(self.vault_path)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n✅ ЗАДАЧА ЗАВЕРШЕНА за {duration:.2f}с")
            print(f"📁 Результаты в: {self.vault_path}")
            
            return result
            
        except Exception as e:
            print(f"\n❌ ОШИБКА: {e}")
            logger.error(f"Ошибка выполнения задачи: {e}")
            raise e
    
    def _display_process(self, result: Dict[str, Any]):
        """Отображение процесса работы"""
        print("\n📊 ПРОЦЕСС РАБОТЫ:")
        print("-" * 40)
        
        # Анализ сложности
        complexity = result.get("complexity_analysis", {})
        print(f"🔍 Сложность: {complexity.get('complexity', 'неизвестно')}")
        print(f"🤖 Агентов создано: {result.get('agents_created', 0)}")
        
        # Подзадачи
        subtasks = result.get("subtasks", [])
        if subtasks:
            print(f"🔄 Подзадач: {len(subtasks)}")
            for i, subtask in enumerate(subtasks[:3], 1):  # Показываем первые 3
                print(f"   {i}. {subtask.get('description', 'Неизвестная подзадача')[:50]}...")
        
        # Команда
        team = result.get("team", {})
        if team:
            print(f"👥 Размер команды: {team.get('team_size', 0)}")
        
        # Workflow
        workflow = result.get("workflow", {})
        if workflow:
            print(f"📋 Шагов workflow: {len(workflow.get('steps', []))}")
        
        # Выполнение
        execution = result.get("execution", {})
        if execution:
            print(f"⚡ Статус выполнения: {execution.get('status', 'неизвестно')}")
    
    def _collect_created_files(self) -> list:
        """Сбор всех созданных файлов"""
        created_files = []
        
        # Ищем файлы в результатах
        results_folder = self.vault_path / "results"
        if results_folder.exists():
            for file_path in results_folder.rglob("*"):
                if file_path.is_file():
                    created_files.append({
                        "path": str(file_path),
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "type": "result"
                    })
        
        # Ищем файлы агентов
        agents_folder = self.vault_path / "agents"
        if agents_folder.exists():
            for file_path in agents_folder.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.md', '.txt', '.py', '.html', '.json']:
                    created_files.append({
                        "path": str(file_path),
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "type": "agent_output"
                    })
        
        # Ищем файлы в outputs (для совместимости)
        outputs_folder = Path("./outputs")
        if outputs_folder.exists():
            for file_path in outputs_folder.rglob("*"):
                if file_path.is_file():
                    created_files.append({
                        "path": str(file_path),
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "type": "legacy_output"
                    })
        
        return created_files
    
    def _display_results(self, created_files: list):
        """Отображение созданных файлов"""
        print("\n📁 СОЗДАННЫЕ ФАЙЛЫ:")
        print("-" * 40)
        
        if not created_files:
            print("❌ Файлы не созданы")
            return
        
        # Группируем по типам
        by_type = {}
        for file_info in created_files:
            file_type = file_info["type"]
            if file_type not in by_type:
                by_type[file_type] = []
            by_type[file_type].append(file_info)
        
        # Выводим по группам
        for file_type, files in by_type.items():
            type_names = {
                "result": "🎯 Результаты",
                "agent_output": "🤖 Выходы агентов", 
                "legacy_output": "📦 Legacy выходы"
            }
            print(f"\n{type_names.get(file_type, file_type)}:")
            
            for file_info in files:
                size_kb = file_info["size"] / 1024
                print(f"   📄 {file_info['name']} ({size_kb:.1f} KB)")
                print(f"      {file_info['path']}")
        
        print(f"\n📊 Всего файлов: {len(created_files)}")


async def main():
    """Главная функция launcher'а"""
    print("🚀 KittyCore 3.0 Unified Launcher")
    print("=" * 50)
    print("Единая система для всех сценариев работы")
    print("Obsidian-совместимое хранилище + Human-in-the-loop")
    print()
    
    launcher = SimpleLauncher()
    
    # Интерактивный режим
    while True:
        try:
            print("\n" + "="*50)
            task = input("🎯 Введите задачу (или 'exit' для выхода): ").strip()
            
            if task.lower() in ['exit', 'quit', 'выход']:
                print("👋 До свидания!")
                break
            
            if not task:
                print("❌ Пустая задача")
                continue
            
            # Выполняем задачу
            result = await launcher.run_task(task)
            
            # Предлагаем продолжить
            print("\n" + "-"*30)
            continue_work = input("🔄 Продолжить работу? (y/n): ").strip().lower()
            if continue_work in ['n', 'no', 'нет']:
                print("👋 До свидания!")
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Прервано пользователем")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            logger.error(f"Ошибка в main: {e}")


if __name__ == "__main__":
    # Настраиваем логирование
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
        colorize=True
    )
    
    # Запускаем
    asyncio.run(main()) 