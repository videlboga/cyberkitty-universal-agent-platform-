"""
KittyCore 3.0 Obsidian Integration
=================================

Интеграция агентной системы KittyCore с Obsidian для создания
живого графа знаний с выполнением кода и автоматической перелинковкой.

Возможности:
- Автоматическое создание заметок агентами
- Выполнение кода в заметках Obsidian
- Автоматическая перелинковка между агентами и задачами
- Метаданные для фильтрации и организации
- Граф связей для визуализации процессов
- Peer-review между агентами через ссылки
"""

from .obsidian_adapter import ObsidianAdapter, ObsidianConfig
from .note_manager import NoteManager
from .code_executor import CodeExecutor
from .link_manager import LinkManager
from .metadata_manager import MetadataManager
from .graph_updater import GraphUpdater

__all__ = [
    'ObsidianAdapter',
    'ObsidianConfig',
    'NoteManager', 
    'CodeExecutor',
    'LinkManager',
    'MetadataManager',
    'GraphUpdater'
]

__version__ = "1.0.0" 