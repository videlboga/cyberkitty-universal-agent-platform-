"""
LinkManager - автоматическая перелинковка заметок в Obsidian
"""

import re
from pathlib import Path
from typing import Dict, List, Set
from loguru import logger


class LinkManager:
    """
    Простой менеджер для автоматической перелинковки заметок
    
    Основные функции:
    - Автоматическое создание [[ссылок]] между заметками
    - Поиск связанных заметок
    - Построение графа связей
    """
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        logger.debug(f"🔗 LinkManager инициализирован для: {vault_path}")
    
    async def auto_link_note(self, note_path: str) -> int:
        """
        Автоматическое создание ссылок в заметке
        
        Args:
            note_path: Путь к заметке
            
        Returns:
            Количество созданных ссылок
        """
        try:
            # Чтение заметки
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Поиск существующих заметок для линковки
            existing_notes = self._find_existing_notes()
            
            # Создание ссылок
            updated_content, links_count = self._create_links(content, existing_notes)
            
            # Сохранение если есть изменения
            if links_count > 0:
                with open(note_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                logger.info(f"🔗 Создано {links_count} ссылок в {note_path}")
            
            return links_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка автолинковки {note_path}: {e}")
            return 0
    
    async def get_graph_data(self) -> Dict[str, List]:
        """
        Получение данных для построения графа связей
        
        Returns:
            Словарь с узлами и связями
        """
        nodes = []
        edges = []
        
        try:
            # Сбор всех заметок
            for md_file in self.vault_path.rglob("*.md"):
                node_name = md_file.stem
                nodes.append({
                    "id": node_name,
                    "name": node_name,
                    "path": str(md_file)
                })
                
                # Поиск ссылок в заметке
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    links = re.findall(r'\[\[([^\]]+)\]\]', content)
                    
                    for link in links:
                        edges.append({
                            "source": node_name,
                            "target": link
                        })
                        
                except Exception as e:
                    logger.debug(f"⚠️ Ошибка чтения {md_file}: {e}")
            
            return {
                "nodes": nodes,
                "edges": edges
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания графа: {e}")
            return {"nodes": [], "edges": []}
    
    def _find_existing_notes(self) -> Dict[str, str]:
        """Поиск всех существующих заметок"""
        notes = {}
        
        for md_file in self.vault_path.rglob("*.md"):
            note_name = md_file.stem
            notes[note_name] = str(md_file)
        
        return notes
    
    def _create_links(self, content: str, existing_notes: Dict[str, str]) -> tuple:
        """Создание ссылок в контенте"""
        updated_content = content
        links_created = 0
        
        for note_name, note_path in existing_notes.items():
            # Простой поиск упоминаний имени заметки
            pattern = rf'\b{re.escape(note_name)}\b(?!\]\])'
            
            if re.search(pattern, content, re.IGNORECASE):
                # Замена на ссылку
                replacement = f'[[{note_name}]]'
                updated_content = re.sub(pattern, replacement, updated_content, count=1)
                links_created += 1
        
        return updated_content, links_created 