"""
ObsidianAdapter - главный адаптер интеграции KittyCore с Obsidian
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from loguru import logger

from .note_manager import NoteManager
from .metadata_manager import MetadataManager
from .link_manager import LinkManager
from .code_executor import CodeExecutor
from .graph_updater import GraphUpdater


@dataclass
class ObsidianConfig:
    """Конфигурация интеграции с Obsidian"""
    vault_path: str
    notes_folder: str = "KittyCore"
    agents_folder: str = "Agents" 
    tasks_folder: str = "Tasks"
    results_folder: str = "Results"
    reports_folder: str = "Reports"
    auto_link: bool = True
    execute_code: bool = True
    create_graph: bool = True


class ObsidianAdapter:
    """
    Главный адаптер для интеграции KittyCore с Obsidian
    
    Обеспечивает:
    - Создание и управление заметками
    - Автоматическую перелинковку
    - Выполнение кода в заметках
    - Управление метаданными
    - Синхронизацию с агентами
    """
    
    def __init__(self, config: ObsidianConfig):
        self.config = config
        self.vault_path = Path(config.vault_path)
        
        # Инициализация компонентов
        self.note_manager = NoteManager(self.vault_path, config)
        self.metadata_manager = MetadataManager()
        self.link_manager = LinkManager(self.vault_path)
        self.code_executor = CodeExecutor()
        self.graph_updater = GraphUpdater(self.vault_path)
        
        # Проверка и создание структуры папок
        self._setup_vault_structure()
        
        logger.info(f"🔗 ObsidianAdapter инициализирован для vault: {self.vault_path}")
    
    def _setup_vault_structure(self):
        """Создание структуры папок в Obsidian vault"""
        folders = [
            self.config.notes_folder,
            f"{self.config.notes_folder}/{self.config.agents_folder}",
            f"{self.config.notes_folder}/{self.config.tasks_folder}",
            f"{self.config.notes_folder}/{self.config.results_folder}",
            f"{self.config.notes_folder}/{self.config.reports_folder}",
        ]
        
        for folder in folders:
            folder_path = self.vault_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"📁 Создана папка: {folder_path}")
    
    async def create_agent_note(self, agent_name: str, agent_data: Dict[str, Any]) -> str:
        """
        Создание заметки агента
        
        Args:
            agent_name: Имя агента
            agent_data: Данные агента
            
        Returns:
            Путь к созданной заметке
        """
        metadata = self.metadata_manager.create_agent_metadata(agent_name, agent_data)
        
        content = f"""# {agent_name}

## Специализация
{agent_data.get('description', 'Универсальный агент')}

## Возможности
{self._format_capabilities(agent_data.get('capabilities', []))}

## Статистика
- Создан: {metadata['created']}
- Задач выполнено: {agent_data.get('tasks_completed', 0)}
- Успешность: {agent_data.get('success_rate', 0)}%

## Связанные заметки
- Задачи: [[{self.config.tasks_folder}]]
- Результаты: [[{self.config.results_folder}]]

## Теги
{self._format_tags(['agent', agent_name.lower(), agent_data.get('type', 'general')])}
"""
        
        note_path = await self.note_manager.create_note(
            folder=self.config.agents_folder,
            filename=f"{agent_name}-Agent",
            content=content,
            metadata=metadata
        )
        
        logger.info(f"📝 Создана заметка агента: {note_path}")
        return note_path
    
    async def create_task_note(self, task_id: str, task_data: Dict[str, Any]) -> str:
        """
        Создание заметки задачи
        
        Args:
            task_id: ID задачи
            task_data: Данные задачи
            
        Returns:
            Путь к созданной заметке
        """
        metadata = self.metadata_manager.create_task_metadata(task_id, task_data)
        
        # Автоматическая перелинковка с агентами
        agent_links = ""
        if 'assigned_agents' in task_data:
            agent_links = "\n".join([
                f"- [[{agent}-Agent]]" 
                for agent in task_data['assigned_agents']
            ])
        
        content = f"""# Задача: {task_data.get('title', task_id)}

## Описание
{task_data.get('description', 'Описание отсутствует')}

## Статус
**Текущий статус:** {task_data.get('status', 'pending')}

## Назначенные агенты
{agent_links}

## Код для выполнения
```python
# Код агентов будет выполняться здесь
{task_data.get('code', '# Код не предоставлен')}
```

## Результаты
*Результаты будут добавлены агентами автоматически*

## Связанные заметки
- Результаты: [[Результат-{task_id}]]
- Отчёт: [[Отчёт-{task_id}]]

## Теги
{self._format_tags(['task', task_data.get('type', 'general'), task_data.get('status', 'pending')])}
"""
        
        note_path = await self.note_manager.create_note(
            folder=self.config.tasks_folder,
            filename=f"Задача-{task_id}",
            content=content,
            metadata=metadata
        )
        
        # Автоматическая перелинковка
        if self.config.auto_link:
            await self.link_manager.auto_link_note(note_path)
        
        logger.info(f"📋 Создана заметка задачи: {note_path}")
        return note_path
    
    async def create_result_note(self, task_id: str, agent_name: str, result_data: Dict[str, Any]) -> str:
        """
        Создание заметки результата
        
        Args:
            task_id: ID связанной задачи
            agent_name: Имя агента
            result_data: Данные результата
            
        Returns:
            Путь к созданной заметке
        """
        metadata = self.metadata_manager.create_result_metadata(task_id, agent_name, result_data)
        
        content = f"""# Результат: {result_data.get('title', f'Задача {task_id}')}

**Выполнено агентом:** [[{agent_name}-Agent]]  
**Задача:** [[Задача-{task_id}]]  
**Статус:** {result_data.get('status', 'completed')}

## Результаты выполнения

{result_data.get('description', 'Описание результата')}

## Выполненный код
```python
{result_data.get('code', '# Код не выполнялся')}
```

## Выходные данные
```
{result_data.get('output', 'Выходных данных нет')}
```

## Файлы результатов
{self._format_file_links(result_data.get('files', []))}

## Анализ качества
- **Успешность:** {result_data.get('success', False)}
- **Качество:** {result_data.get('quality_score', 0)}/10
- **Замечания:** {result_data.get('notes', 'Нет замечаний')}

## Peer Review
- **Проверено:** [[{result_data.get('reviewed_by', 'Не проверено')}]]
- **Статус проверки:** {result_data.get('review_status', 'Ожидает')}

## Связанные заметки
- Исходная задача: [[Задача-{task_id}]]
- Агент-исполнитель: [[{agent_name}-Agent]]
- Отчёт: [[Отчёт-{task_id}]]

## Теги
{self._format_tags(['result', agent_name.lower(), result_data.get('type', 'general')])}
"""
        
        note_path = await self.note_manager.create_note(
            folder=self.config.results_folder,
            filename=f"Результат-{task_id}-{agent_name}",
            content=content,
            metadata=metadata
        )
        
        # Обновление связанной задачи
        await self._update_task_with_result(task_id, note_path)
        
        logger.info(f"✅ Создана заметка результата: {note_path}")
        return note_path
    
    async def create_report_note(self, task_id: str, report_data: Dict[str, Any]) -> str:
        """
        Создание итогового отчёта
        
        Args:
            task_id: ID задачи
            report_data: Данные отчёта
            
        Returns:
            Путь к созданной заметке
        """
        metadata = self.metadata_manager.create_report_metadata(task_id, report_data)
        
        # Сбор всех результатов
        results_section = await self._collect_task_results(task_id)
        
        content = f"""# Отчёт: {report_data.get('title', f'Задача {task_id}')}

**Задача:** [[Задача-{task_id}]]  
**Завершено:** {report_data.get('completed_at', datetime.now().isoformat())}  
**Общий статус:** {report_data.get('status', 'completed')}

## Сводка
{report_data.get('summary', 'Сводка отсутствует')}

## Участвовавшие агенты
{self._format_agent_summary(report_data.get('agents', []))}

## Результаты по агентам
{results_section}

## Общая оценка
- **Успешность:** {report_data.get('overall_success', False)}
- **Качество:** {report_data.get('overall_quality', 0)}/10
- **Время выполнения:** {report_data.get('execution_time', 'N/A')}

## Граф связей
![[Граф-{task_id}.png]]

## Выводы и рекомендации
{report_data.get('conclusions', 'Выводы не предоставлены')}

## Теги
{self._format_tags(['report', 'completed', report_data.get('type', 'general')])}
"""
        
        note_path = await self.note_manager.create_note(
            folder=self.config.reports_folder,
            filename=f"Отчёт-{task_id}",
            content=content,
            metadata=metadata
        )
        
        logger.info(f"📊 Создан итоговый отчёт: {note_path}")
        return note_path
    
    async def execute_code_in_note(self, note_path: str) -> Dict[str, Any]:
        """
        Выполнение кода в заметке Obsidian
        
        Args:
            note_path: Путь к заметке
            
        Returns:
            Результаты выполнения
        """
        if not self.config.execute_code:
            return {"status": "disabled", "message": "Выполнение кода отключено"}
        
        return await self.code_executor.execute_note_code(note_path)
    
    async def update_note_metadata(self, note_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Обновление метаданных заметки
        
        Args:
            note_path: Путь к заметке
            metadata: Новые метаданные
            
        Returns:
            Успешность операции
        """
        return await self.note_manager.update_metadata(note_path, metadata)
    
    async def get_graph_data(self) -> Dict[str, Any]:
        """
        Получение данных графа связей
        
        Returns:
            Данные для построения графа
        """
        return await self.link_manager.get_graph_data()
    
    # Вспомогательные методы
    
    def _format_capabilities(self, capabilities: List[str]) -> str:
        """Форматирование списка возможностей"""
        if not capabilities:
            return "- Универсальные возможности"
        return "\n".join([f"- {cap}" for cap in capabilities])
    
    def _format_tags(self, tags: List[str]) -> str:
        """Форматирование тегов"""
        return " ".join([f"#{tag}" for tag in tags])
    
    def _format_file_links(self, files: List[str]) -> str:
        """Форматирование ссылок на файлы"""
        if not files:
            return "*Файлов не создано*"
        return "\n".join([f"- [[{file}]]" for file in files])
    
    def _format_agent_summary(self, agents: List[Dict[str, Any]]) -> str:
        """Форматирование сводки по агентам"""
        if not agents:
            return "*Агенты не участвовали*"
        
        lines = []
        for agent in agents:
            name = agent.get('name', 'Unknown')
            tasks = agent.get('tasks_completed', 0)
            success = agent.get('success_rate', 0)
            lines.append(f"- [[{name}-Agent]]: {tasks} задач, {success}% успеха")
        
        return "\n".join(lines)
    
    async def _update_task_with_result(self, task_id: str, result_path: str):
        """Обновление задачи с результатом"""
        task_path = self.vault_path / self.config.notes_folder / self.config.tasks_folder / f"Задача-{task_id}.md"
        if task_path.exists():
            await self.note_manager.append_to_note(
                str(task_path), 
                f"\n- [[{Path(result_path).stem}]]"
            )
    
    async def _collect_task_results(self, task_id: str) -> str:
        """Сбор всех результатов задачи"""
        results_folder = self.vault_path / self.config.notes_folder / self.config.results_folder
        result_files = list(results_folder.glob(f"Результат-{task_id}-*.md"))
        
        if not result_files:
            return "*Результатов не найдено*"
        
        lines = []
        for result_file in result_files:
            agent_name = result_file.stem.split('-')[-1]
            lines.append(f"- [[{result_file.stem}]] (агент: [[{agent_name}-Agent]])")
        
        return "\n".join(lines) 