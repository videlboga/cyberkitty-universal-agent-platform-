"""
🧠 KittyCore 3.0 - Memory System
Многоуровневая коллективная память агентов
"""

# Базовая система памяти (обратная совместимость)
from .base_memory import Memory, SimpleMemory, PersistentMemory

# Коллективная память команд (НОВОЕ!)
from .collective_memory import CollectiveMemory, TeamMemoryEntry

# Система памяти (будут добавлены при миграции)
# from .working_memory import WorkingMemory
# from .short_term_memory import ShortTermMemory
# from .long_term_memory import LongTermMemory
# from .memory_utils import MemoryUtils

__version__ = "3.0.0"
__all__ = [
    # Базовая память (обратная совместимость)
    "Memory", "SimpleMemory", "PersistentMemory",
    
    # Коллективная память (НОВОЕ!)
    "CollectiveMemory", "TeamMemoryEntry",
    
    # Новая архитектура (будут добавлены)
    # "WorkingMemory",
    # "ShortTermMemory",
    # "LongTermMemory", 
    # "MemoryUtils"
]

# Типы памяти
MEMORY_TYPES = {
    "working": "Рабочая память - текущие задачи команды",
    "short_term": "Краткосрочная память - недавние результаты", 
    "long_term": "Долгосрочная память - база знаний и опыт",
    "cross_agent": "Общая память между агентами команды",
    "collective": "Коллективная память команды агентов"  # НОВОЕ!
} 