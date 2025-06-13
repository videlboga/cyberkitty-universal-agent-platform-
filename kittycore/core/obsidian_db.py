"""
🗄️ ObsidianDB - Центральная база данных на основе Obsidian

Единая система хранения и координации для всех агентов KittyCore 3.0:
- Все результаты агентов сохраняются как .md файлы
- Агенты читают и пишут через ObsidianDB
- Автоматические связи между заметками
- Версионирование и история изменений
- Поиск и индексация контента

Структура:
📁 obsidian_vault/
├── 📁 tasks/           ← Задачи пользователей
├── 📁 agents/          ← Результаты работы агентов  
├── 📁 coordination/    ← Координация между агентами
├── 📁 results/         ← Финальные результаты
└── 📁 system/          ← Системные данные
"""

import os
import json
import yaml
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import hashlib
import re

from loguru import logger

class ObsidianNote:
    """Представление заметки Obsidian"""
    
    def __init__(self, title: str, content: str = "", tags: List[str] = None, 
                 metadata: Dict[str, Any] = None, folder: str = ""):
        self.title = title
        self.content = content
        self.tags = tags or []
        self.metadata = metadata or {}
        self.folder = folder
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    def to_markdown(self) -> str:
        """Конвертирует в Obsidian-совместимый markdown"""
        lines = []
        
        # YAML frontmatter с метаданными
        if self.metadata or self.tags:
            lines.append("---")
            
            # Базовые метаданные
            lines.append(f"created: {self.created_at.isoformat()}")
            lines.append(f"updated: {self.updated_at.isoformat()}")
            
            # Теги
            if self.tags:
                lines.append(f"tags: [{', '.join(self.tags)}]")
            
            # Дополнительные метаданные
            for key, value in self.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    lines.append(f"{key}: {value}")
                elif isinstance(value, datetime):
                    lines.append(f"{key}: {value.isoformat()}")
                else:
                    try:
                        lines.append(f"{key}: {json.dumps(value)}")
                    except TypeError:
                        lines.append(f"{key}: {str(value)}")
                    
            lines.append("---")
            lines.append("")
        
        # Заголовок
        lines.append(f"# {self.title}")
        lines.append("")
        
        # Контент
        lines.append(self.content)
        
        return "\n".join(lines)
    
    @classmethod
    def from_markdown(cls, filepath: str) -> 'ObsidianNote':
        """Создаёт заметку из markdown файла"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим YAML frontmatter
        metadata = {}
        tags = []
        
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_content = parts[1].strip()
                main_content = parts[2].strip()
                
                try:
                    yaml_data = yaml.safe_load(yaml_content)
                    if yaml_data:
                        tags = yaml_data.pop("tags", [])
                        metadata = yaml_data
                except:
                    main_content = content
            else:
                main_content = content
        else:
            main_content = content
        
        # Извлекаем заголовок
        title_match = re.search(r'^# (.+)$', main_content, re.MULTILINE)
        title = title_match.group(1) if title_match else Path(filepath).stem
        
        # Убираем заголовок из контента
        if title_match:
            main_content = main_content.replace(title_match.group(0), "").strip()
        
        note = cls(title=title, content=main_content, tags=tags, metadata=metadata)
        
        # Устанавливаем даты из метаданных
        if "created" in metadata:
            try:
                note.created_at = datetime.fromisoformat(metadata["created"])
            except:
                pass
                
        if "updated" in metadata:
            try:
                note.updated_at = datetime.fromisoformat(metadata["updated"])
            except:
                pass
        
        return note

class ObsidianDB:
    """Центральная база данных на основе Obsidian"""
    
    def __init__(self, vault_path: str = "./obsidian_vault"):
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(exist_ok=True)
        
        # Создаём структуру папок
        self.folders = {
            "tasks": self.vault_path / "tasks",
            "agents": self.vault_path / "agents", 
            "coordination": self.vault_path / "coordination",
            "results": self.vault_path / "results",
            "system": self.vault_path / "system"
        }
        
        for folder in self.folders.values():
            folder.mkdir(exist_ok=True)
            
        # Индекс заметок для быстрого поиска
        self._notes_index = {}
        self._rebuild_index()
        
        logger.info(f"🗄️ ObsidianDB инициализирована: {vault_path}")
    
    def _rebuild_index(self):
        """Перестраивает индекс всех заметок"""
        self._notes_index = {}
        
        for md_file in self.vault_path.rglob("*.md"):
            try:
                note = ObsidianNote.from_markdown(str(md_file))
                relative_path = md_file.relative_to(self.vault_path)
                self._notes_index[str(relative_path)] = {
                    "title": note.title,
                    "tags": note.tags,
                    "metadata": note.metadata,
                    "created": note.created_at,
                    "updated": note.updated_at,
                    "path": str(md_file)
                }
            except Exception as e:
                logger.warning(f"Не удалось проиндексировать {md_file}: {e}")
    
    def save_note(self, note: ObsidianNote, filename: str = None) -> str:
        """Сохраняет заметку в vault"""
        if not filename:
            # Генерируем имя файла из заголовка
            safe_title = re.sub(r'[^\w\s-]', '', note.title)
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            filename = f"{safe_title}.md"
        
        # Определяем папку из метаданных или используем по умолчанию
        folder_name = note.metadata.get("folder", note.folder or "system")
        folder_path = self.folders.get(folder_name, self.folders["system"])
        
        filepath = folder_path / filename
        note.updated_at = datetime.now()
        
        # Сохраняем файл
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(note.to_markdown())
        
        # Обновляем индекс
        relative_path = filepath.relative_to(self.vault_path)
        self._notes_index[str(relative_path)] = {
            "title": note.title,
            "tags": note.tags,
            "metadata": note.metadata,
            "created": note.created_at,
            "updated": note.updated_at,
            "path": str(filepath)
        }
        
        logger.debug(f"💾 Заметка сохранена: {relative_path}")
        return str(filepath)
    
    def get_note(self, filename: str) -> Optional[ObsidianNote]:
        """Получает заметку по имени файла"""
        # Ищем файл в индексе
        for path, info in self._notes_index.items():
            if Path(path).name == filename or Path(path).stem == filename:
                return ObsidianNote.from_markdown(info["path"])
        
        # Если не найдено в индексе, ищем напрямую
        for folder in self.folders.values():
            filepath = folder / filename
            if not filepath.suffix:
                filepath = filepath.with_suffix('.md')
            
            if filepath.exists():
                return ObsidianNote.from_markdown(str(filepath))
        
        return None
    
    def search_notes(self, query: str = "", tags: List[str] = None, 
                    folder: str = None, metadata_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Поиск заметок по различным критериям"""
        results = []
        
        for path, info in self._notes_index.items():
            match = True
            
            # Фильтр по тексту
            if query:
                if query.lower() not in info["title"].lower():
                    try:
                        note = ObsidianNote.from_markdown(info["path"])
                        if query.lower() not in note.content.lower():
                            match = False
                    except:
                        match = False
            
            # Фильтр по тегам
            if tags and match:
                if not any(tag in info["tags"] for tag in tags):
                    match = False
            
            # Фильтр по папке
            if folder and match:
                if not str(path).startswith(folder):
                    match = False
            
            # Фильтр по метаданным
            if metadata_filter and match:
                for key, value in metadata_filter.items():
                    if info["metadata"].get(key) != value:
                        match = False
                        break
            
            if match:
                results.append({
                    "path": path,
                    "title": info["title"],
                    "tags": info["tags"],
                    "metadata": info["metadata"],
                    "created": info["created"],
                    "updated": info["updated"]
                })
        
        # Сортируем по дате обновления (новые первыми)
        results.sort(key=lambda x: x["updated"], reverse=True)
        return results
    
    def create_link(self, from_note: str, to_note: str, link_text: str = None) -> bool:
        """Создаёт связь между заметками (Obsidian-style)"""
        note = self.get_note(from_note)
        if not note:
            return False
        
        # Формируем ссылку в формате Obsidian
        to_title = Path(to_note).stem
        if link_text:
            link = f"[[{to_title}|{link_text}]]"
        else:
            link = f"[[{to_title}]]"
        
        # Добавляем ссылку в конец заметки
        if link not in note.content:
            note.content += f"\n\n{link}"
            self.save_note(note, from_note)
        
        return True
    
    def get_backlinks(self, note_title: str) -> List[str]:
        """Получает список заметок, которые ссылаются на данную"""
        backlinks = []
        link_pattern = rf"\[\[{re.escape(note_title)}(?:\|[^\]]+)?\]\]"
        
        for path, info in self._notes_index.items():
            try:
                note = ObsidianNote.from_markdown(info["path"])
                if re.search(link_pattern, note.content):
                    backlinks.append(info["title"])
            except:
                continue
        
        return backlinks
    
    async def save_artifact(self, agent_id: str, content: str, artifact_type: str = "file", filename: str = None) -> str:
        """Сохраняет артефакт агента в ObsidianDB"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if not filename:
            filename = f"{artifact_type}_{timestamp}.md"
        else:
            # Убираем расширение если есть и добавляем .md
            base_name = Path(filename).stem
            filename = f"{base_name}_{timestamp}.md"
        
        note = ObsidianNote(
            title=f"{agent_id} - {artifact_type} - {filename}",
            content=content,
            tags=[agent_id, artifact_type, "artifact"],
            metadata={
                "agent_id": agent_id,
                "artifact_type": artifact_type,
                "original_filename": filename,
                "created_timestamp": timestamp,
                "folder": f"agents/{agent_id}/artifacts"
            },
            folder=f"agents/{agent_id}/artifacts"
        )
        
        # Создаём папку если не существует
        artifact_folder = self.vault_path / "agents" / agent_id / "artifacts"
        artifact_folder.mkdir(parents=True, exist_ok=True)
        
        artifact_filename = f"{agent_id}_artifact_{timestamp}.md"
        filepath = self.save_note(note, artifact_filename)
        
        logger.debug(f"💎 Артефакт {artifact_type} сохранён для {agent_id}: {filepath}")
        return filepath

class AgentWorkspace:
    """Рабочее пространство агента в ObsidianDB"""
    
    def __init__(self, agent_id: str, obsidian_db: ObsidianDB):
        self.agent_id = agent_id
        self.db = obsidian_db
        self.workspace_folder = f"agents/{agent_id}"
        
        # Создаём папку агента
        agent_folder = self.db.vault_path / "agents" / agent_id
        agent_folder.mkdir(exist_ok=True)
        
        logger.debug(f"🤖 Рабочее пространство агента {agent_id} готово")
    
    def save_result(self, task_id: str, content: str, result_type: str = "result") -> str:
        """Сохраняет результат работы агента"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        note = ObsidianNote(
            title=f"{self.agent_id} - {result_type} - {task_id}",
            content=content,
            tags=[self.agent_id, result_type, "agent-output"],
            metadata={
                "agent_id": self.agent_id,
                "task_id": task_id,
                "result_type": result_type,
                "timestamp": timestamp,
                "folder": "agents"
            },
            folder="agents"
        )
        
        filename = f"{self.agent_id}_{result_type}_{timestamp}.md"
        filepath = self.db.save_note(note, filename)
        
        logger.info(f"💾 Агент {self.agent_id} сохранил результат: {filename}")
        return filepath
    
    def get_task_context(self, task_id: str) -> Dict[str, Any]:
        """Получает контекст задачи из других агентов"""
        # Ищем все заметки связанные с задачей
        related_notes = self.db.search_notes(
            metadata_filter={"task_id": task_id}
        )
        
        context = {
            "task_id": task_id,
            "related_agents": [],
            "previous_results": [],
            "coordination_notes": []
        }
        
        for note_info in related_notes:
            if note_info["metadata"].get("agent_id") != self.agent_id:
                context["related_agents"].append(note_info["metadata"].get("agent_id"))
                
                if note_info["metadata"].get("result_type") == "result":
                    note = self.db.get_note(note_info["path"])
                    if note:
                        context["previous_results"].append({
                            "agent": note_info["metadata"].get("agent_id"),
                            "content": note.content[:500] + "..." if len(note.content) > 500 else note.content,
                            "timestamp": note_info["updated"]
                        })
        
        return context
    
    def coordinate_with_agent(self, other_agent_id: str, message: str, task_id: str) -> str:
        """Отправляет сообщение другому агенту через координационную заметку"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        note = ObsidianNote(
            title=f"Координация: {self.agent_id} → {other_agent_id}",
            content=f"**От:** {self.agent_id}\n**К:** {other_agent_id}\n**Задача:** {task_id}\n\n{message}",
            tags=["coordination", self.agent_id, other_agent_id],
            metadata={
                "from_agent": self.agent_id,
                "to_agent": other_agent_id,
                "task_id": task_id,
                "message_type": "coordination",
                "timestamp": timestamp,
                "folder": "coordination"
            },
            folder="coordination"
        )
        
        filename = f"coord_{self.agent_id}_to_{other_agent_id}_{timestamp}.md"
        filepath = self.db.save_note(note, filename)
        
        logger.info(f"📨 {self.agent_id} отправил сообщение {other_agent_id}")
        return filepath
    
    def get_messages_for_me(self, task_id: str = None) -> List[Dict[str, Any]]:
        """Получает сообщения адресованные этому агенту"""
        filter_criteria = {"to_agent": self.agent_id}
        if task_id:
            filter_criteria["task_id"] = task_id
        
        messages = self.db.search_notes(
            folder="coordination",
            metadata_filter=filter_criteria
        )
        
        result = []
        for msg_info in messages:
            note = self.db.get_note(msg_info["path"])
            if note:
                result.append({
                    "from_agent": msg_info["metadata"].get("from_agent"),
                    "content": note.content,
                    "timestamp": msg_info["updated"],
                    "task_id": msg_info["metadata"].get("task_id")
                })
        
        return result

class TaskManager:
    """Менеджер задач в ObsidianDB"""
    
    def __init__(self, obsidian_db: ObsidianDB):
        self.db = obsidian_db
        
    def create_task(self, task_description: str, user_id: str = None) -> str:
        """Создаёт новую задачу"""
        task_id = hashlib.md5(f"{task_description}{datetime.now()}".encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        note = ObsidianNote(
            title=f"Задача: {task_description[:50]}...",
            content=f"""## Описание задачи

{task_description}

## Статус
- **ID задачи:** {task_id}
- **Создана:** {datetime.now().isoformat()}
- **Пользователь:** {user_id or 'anonymous'}
- **Статус:** В работе

## Агенты
*Агенты будут добавлены автоматически*

## Результаты
*Результаты будут добавлены по мере выполнения*

## Связанные заметки
""",
            tags=["task", "active", task_id],
            metadata={
                "task_id": task_id,
                "user_id": user_id,
                "status": "active",
                "created_timestamp": timestamp,
                "folder": "tasks"
            },
            folder="tasks"
        )
        
        filename = f"task_{task_id}_{timestamp}.md"
        filepath = self.db.save_note(note, filename)
        
        logger.info(f"📋 Создана задача {task_id}: {task_description[:50]}...")
        return task_id
    
    def update_task_status(self, task_id: str, status: str, details: str = ""):
        """Обновляет статус задачи"""
        # Находим заметку задачи
        task_notes = self.db.search_notes(metadata_filter={"task_id": task_id})
        
        for note_info in task_notes:
            if note_info["metadata"].get("folder") == "tasks":
                note = self.db.get_note(note_info["path"])
                if note:
                    # Обновляем статус в метаданных
                    note.metadata["status"] = status
                    note.metadata["updated_timestamp"] = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Обновляем теги
                    note.tags = [tag for tag in note.tags if tag not in ["active", "completed", "failed"]]
                    note.tags.append(status)
                    
                    # Добавляем детали в контент
                    if details:
                        note.content += f"\n\n### Обновление статуса ({datetime.now().strftime('%H:%M:%S')})\n**Статус:** {status}\n{details}"
                    
                    self.db.save_note(note, Path(note_info["path"]).name)
                    logger.info(f"📋 Задача {task_id} обновлена: {status}")
                    break
    
    def add_agent_to_task(self, task_id: str, agent_id: str, role: str = ""):
        """Добавляет агента к задаче"""
        task_notes = self.db.search_notes(metadata_filter={"task_id": task_id})
        
        for note_info in task_notes:
            if note_info["metadata"].get("folder") == "tasks":
                note = self.db.get_note(note_info["path"])
                if note:
                    # Добавляем агента в контент
                    agent_section = f"\n- **{agent_id}** ({role or 'worker'}) - добавлен {datetime.now().strftime('%H:%M:%S')}"
                    
                    if "## Агенты" in note.content:
                        note.content = note.content.replace(
                            "*Агенты будут добавлены автоматически*",
                            agent_section.strip()
                        )
                        if agent_section not in note.content:
                            # Добавляем после секции агентов
                            note.content = note.content.replace("## Агенты", f"## Агенты{agent_section}")
                    
                    # Создаём связь с рабочим пространством агента
                    self.db.create_link(Path(note_info["path"]).stem, f"agents/{agent_id}", f"Агент {agent_id}")
                    
                    self.db.save_note(note, Path(note_info["path"]).name)
                    logger.info(f"🤖 Агент {agent_id} добавлен к задаче {task_id}")
                    break
    
    def add_result_to_task(self, task_id: str, agent_id: str, result_content: str, result_type: str = "result"):
        """Добавляет результат агента к задаче"""
        task_notes = self.db.search_notes(metadata_filter={"task_id": task_id})
        
        for note_info in task_notes:
            if note_info["metadata"].get("folder") == "tasks":
                note = self.db.get_note(note_info["path"])
                if note:
                    # Добавляем результат в контент
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    result_section = f"""
### {agent_id} - {result_type} ({timestamp})

{result_content[:300]}{"..." if len(result_content) > 300 else ""}

[[{agent_id}_{result_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}|Полный результат]]
"""
                    
                    if "## Результаты" in note.content:
                        note.content = note.content.replace(
                            "*Результаты будут добавлены по мере выполнения*",
                            result_section.strip()
                        )
                        if result_section not in note.content:
                            # Добавляем после секции результатов
                            note.content = note.content.replace("## Результаты", f"## Результаты{result_section}")
                    
                    self.db.save_note(note, Path(note_info["path"]).name)
                    logger.info(f"📊 Результат от {agent_id} добавлен к задаче {task_id}")
                    break
    
    def get_task_summary(self, task_id: str) -> Dict[str, Any]:
        """Получает сводку по задаче"""
        # Основная заметка задачи
        task_notes = self.db.search_notes(metadata_filter={"task_id": task_id})
        task_note = None
        
        for note_info in task_notes:
            if note_info["metadata"].get("folder") == "tasks":
                task_note = note_info
                break
        
        if not task_note:
            return {"error": f"Задача {task_id} не найдена"}
        
        # Все связанные заметки
        all_related = self.db.search_notes(metadata_filter={"task_id": task_id})
        
        # Группируем по типам
        agents = []
        results = []
        coordination = []
        
        for note_info in all_related:
            folder = note_info["metadata"].get("folder", "")
            if folder == "agents":
                agents.append({
                    "agent_id": note_info["metadata"].get("agent_id"),
                    "result_type": note_info["metadata"].get("result_type"),
                    "timestamp": note_info["updated"]
                })
            elif folder == "coordination":
                coordination.append({
                    "from_agent": note_info["metadata"].get("from_agent"),
                    "to_agent": note_info["metadata"].get("to_agent"),
                    "timestamp": note_info["updated"]
                })
        
        return {
            "task_id": task_id,
            "title": task_note["title"],
            "status": task_note["metadata"].get("status", "unknown"),
            "created": task_note["created"],
            "updated": task_note["updated"],
            "agents_count": len(set(a["agent_id"] for a in agents if a["agent_id"])),
            "results_count": len([a for a in agents if a["result_type"] == "result"]),
            "coordination_messages": len(coordination),
            "agents": agents,
            "coordination": coordination
        }

def get_obsidian_db(vault_path: str = "./obsidian_vault") -> ObsidianDB:
    """Получает глобальный экземпляр ObsidianDB"""
    if not hasattr(get_obsidian_db, '_instance'):
        get_obsidian_db._instance = ObsidianDB(vault_path)
    return get_obsidian_db._instance

def create_agent_workspace(agent_id: str, vault_path: str = "./obsidian_vault") -> AgentWorkspace:
    """Создаёт рабочее пространство агента"""
    db = get_obsidian_db(vault_path)
    return AgentWorkspace(agent_id, db)

def create_task_manager(vault_path: str = "./obsidian_vault") -> TaskManager:
    """Создаёт менеджер задач"""
    db = get_obsidian_db(vault_path)
    return TaskManager(db) 