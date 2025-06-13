"""
NoteManager - управление заметками в Obsidian vault
"""

import os
import re
import yaml
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger


class NoteManager:
    """
    Менеджер для создания и управления заметками в Obsidian vault
    
    Возможности:
    - Создание заметок с метаданными
    - Обновление существующих заметок
    - Управление YAML frontmatter
    - Добавление контента к заметкам
    - Поиск и индексация заметок
    """
    
    def __init__(self, vault_path: Path, config):
        self.vault_path = vault_path
        self.config = config
        self.notes_folder = vault_path / config.notes_folder
        
        logger.debug(f"📁 NoteManager инициализирован для: {self.notes_folder}")
    
    async def create_note(self, folder: str, filename: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Создание новой заметки
        
        Args:
            folder: Папка в рамках notes_folder
            filename: Имя файла (без расширения)
            content: Контент заметки
            metadata: Метаданные для frontmatter
            
        Returns:
            Полный путь к созданной заметке
        """
        # Создание пути к заметке
        note_folder = self.notes_folder / folder
        note_folder.mkdir(parents=True, exist_ok=True)
        
        # Санитизация имени файла
        safe_filename = self._sanitize_filename(filename)
        note_path = note_folder / f"{safe_filename}.md"
        
        # Создание уникального имени если файл существует
        counter = 1
        while note_path.exists():
            note_path = note_folder / f"{safe_filename}-{counter}.md"
            counter += 1
        
        # Формирование полного контента с метаданными
        full_content = await self._format_note_content(content, metadata)
        
        # Запись заметки
        async with asyncio.Lock():
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
        
        logger.info(f"📝 Создана заметка: {note_path}")
        return str(note_path)
    
    async def update_note(self, note_path: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Обновление существующей заметки
        
        Args:
            note_path: Путь к заметке
            content: Новый контент
            metadata: Новые метаданные
            
        Returns:
            Успешность операции
        """
        try:
            path = Path(note_path)
            if not path.exists():
                logger.error(f"❌ Заметка не найдена: {note_path}")
                return False
            
            # Чтение существующих метаданных если не предоставлены новые
            if metadata is None:
                existing_metadata = await self._extract_metadata(note_path)
                metadata = existing_metadata
            else:
                # Обновление времени модификации
                metadata['modified'] = datetime.now().isoformat()
            
            # Формирование контента
            full_content = await self._format_note_content(content, metadata)
            
            # Запись обновлённой заметки
            async with asyncio.Lock():
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(full_content)
            
            logger.info(f"✏️ Обновлена заметка: {note_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления заметки {note_path}: {e}")
            return False
    
    async def append_to_note(self, note_path: str, content: str) -> bool:
        """
        Добавление контента к существующей заметке
        
        Args:
            note_path: Путь к заметке
            content: Контент для добавления
            
        Returns:
            Успешность операции
        """
        try:
            path = Path(note_path)
            if not path.exists():
                logger.error(f"❌ Заметка не найдена: {note_path}")
                return False
            
            # Чтение существующего контента
            with open(path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Добавление нового контента
            updated_content = existing_content + "\n" + content
            
            # Запись обновлённого контента
            async with asyncio.Lock():
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
            
            logger.debug(f"➕ Добавлен контент к заметке: {note_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка добавления контента к заметке {note_path}: {e}")
            return False
    
    async def update_metadata(self, note_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Обновление только метаданных заметки
        
        Args:
            note_path: Путь к заметке
            metadata: Новые метаданные
            
        Returns:
            Успешность операции
        """
        try:
            path = Path(note_path)
            if not path.exists():
                logger.error(f"❌ Заметка не найдена: {note_path}")
                return False
            
            # Чтение существующего контента
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Разделение метаданных и контента
            content_without_metadata = await self._extract_content_without_metadata(content)
            
            # Обновление времени модификации
            metadata['modified'] = datetime.now().isoformat()
            
            # Формирование нового контента с обновлёнными метаданными
            full_content = await self._format_note_content(content_without_metadata, metadata)
            
            # Запись обновлённой заметки
            async with asyncio.Lock():
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(full_content)
            
            logger.debug(f"📊 Обновлены метаданные заметки: {note_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления метаданных заметки {note_path}: {e}")
            return False
    
    async def get_note_content(self, note_path: str) -> Optional[str]:
        """
        Получение контента заметки без метаданных
        
        Args:
            note_path: Путь к заметке
            
        Returns:
            Контент заметки или None если ошибка
        """
        try:
            path = Path(note_path)
            if not path.exists():
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return await self._extract_content_without_metadata(content)
            
        except Exception as e:
            logger.error(f"❌ Ошибка чтения заметки {note_path}: {e}")
            return None
    
    async def get_note_metadata(self, note_path: str) -> Dict[str, Any]:
        """
        Получение метаданных заметки
        
        Args:
            note_path: Путь к заметке
            
        Returns:
            Словарь метаданных
        """
        try:
            return await self._extract_metadata(note_path)
        except Exception as e:
            logger.error(f"❌ Ошибка чтения метаданных заметки {note_path}: {e}")
            return {}
    
    async def find_notes_by_tag(self, tag: str) -> List[str]:
        """
        Поиск заметок по тегу
        
        Args:
            tag: Тег для поиска
            
        Returns:
            Список путей к заметкам
        """
        matching_notes = []
        
        for note_path in self.notes_folder.rglob("*.md"):
            try:
                metadata = await self._extract_metadata(str(note_path))
                note_tags = metadata.get('tags', [])
                
                if isinstance(note_tags, str):
                    note_tags = [note_tags]
                
                if tag in note_tags:
                    matching_notes.append(str(note_path))
                    
            except Exception as e:
                logger.debug(f"⚠️ Ошибка обработки заметки {note_path}: {e}")
                continue
        
        return matching_notes
    
    async def find_notes_by_metadata(self, key: str, value: Any) -> List[str]:
        """
        Поиск заметок по метаданным
        
        Args:
            key: Ключ метаданных
            value: Значение для поиска
            
        Returns:
            Список путей к заметкам
        """
        matching_notes = []
        
        for note_path in self.notes_folder.rglob("*.md"):
            try:
                metadata = await self._extract_metadata(str(note_path))
                
                if key in metadata and metadata[key] == value:
                    matching_notes.append(str(note_path))
                    
            except Exception as e:
                logger.debug(f"⚠️ Ошибка обработки заметки {note_path}: {e}")
                continue
        
        return matching_notes
    
    async def get_all_notes(self) -> List[Dict[str, Any]]:
        """
        Получение информации о всех заметках
        
        Returns:
            Список словарей с информацией о заметках
        """
        notes = []
        
        for note_path in self.notes_folder.rglob("*.md"):
            try:
                metadata = await self._extract_metadata(str(note_path))
                
                note_info = {
                    'path': str(note_path),
                    'name': note_path.stem,
                    'folder': str(note_path.parent.relative_to(self.notes_folder)),
                    'metadata': metadata,
                    'modified': note_path.stat().st_mtime
                }
                
                notes.append(note_info)
                
            except Exception as e:
                logger.debug(f"⚠️ Ошибка обработки заметки {note_path}: {e}")
                continue
        
        return notes
    
    # Вспомогательные методы
    
    def _sanitize_filename(self, filename: str) -> str:
        """Санитизация имени файла для безопасности"""
        # Удаление недопустимых символов
        safe_name = re.sub(r'[<>:"/\\|?*]', '-', filename)
        
        # Удаление множественных дефисов и пробелов
        safe_name = re.sub(r'[-\s]+', '-', safe_name)
        
        # Обрезка до разумной длины
        safe_name = safe_name[:100].strip('-')
        
        return safe_name or 'untitled'
    
    async def _format_note_content(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Форматирование контента заметки с метаданными
        
        Args:
            content: Основной контент
            metadata: Метаданные для frontmatter
            
        Returns:
            Полный контент заметки
        """
        if not metadata:
            return content
        
        # Создание YAML frontmatter
        yaml_content = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
        
        # Формирование полного контента
        full_content = f"---\n{yaml_content}---\n\n{content}"
        
        return full_content
    
    async def _extract_metadata(self, note_path: str) -> Dict[str, Any]:
        """
        Извлечение метаданных из заметки
        
        Args:
            note_path: Путь к заметке
            
        Returns:
            Словарь метаданных
        """
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Поиск YAML frontmatter
            match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
            
            if match:
                yaml_content = match.group(1)
                return yaml.safe_load(yaml_content) or {}
            
            return {}
            
        except Exception as e:
            logger.debug(f"⚠️ Ошибка извлечения метаданных из {note_path}: {e}")
            return {}
    
    async def _extract_content_without_metadata(self, content: str) -> str:
        """
        Извлечение контента без метаданных
        
        Args:
            content: Полный контент заметки
            
        Returns:
            Контент без frontmatter
        """
        # Удаление YAML frontmatter
        content_without_frontmatter = re.sub(r'^---\n.*?\n---\n\n?', '', content, flags=re.DOTALL)
        
        return content_without_frontmatter.strip()
    
    async def get_note_links(self, note_path: str) -> List[str]:
        """
        Получение всех [[ссылок]] из заметки
        
        Args:
            note_path: Путь к заметке
            
        Returns:
            Список найденных ссылок
        """
        try:
            content = await self.get_note_content(note_path)
            if not content:
                return []
            
            # Поиск [[ссылок]]
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            
            return list(set(links))  # Удаление дубликатов
            
        except Exception as e:
            logger.debug(f"⚠️ Ошибка извлечения ссылок из {note_path}: {e}")
            return [] 