"""
⚙️ KittyCore 3.0 - Configuration System
Система конфигурации для агентов и компонентов
"""

# Базовая конфигурация (обратная совместимость)
from .base_config import Config, get_config

# Конфигурации компонентов (будут добавлены)
# from .settings import Settings
# from .agent_profiles import AgentProfiles
# from .memory_config import MemoryConfig

__version__ = "3.0.0"
__all__ = [
    # Базовая конфигурация (обратная совместимость)
    "Config", "get_config",
    
    # Новая архитектура (будут добавлены)
    # "Settings", 
    # "AgentProfiles",
    # "MemoryConfig"
]

# Типы конфигураций
CONFIG_TYPES = {
    "settings": "Общие настройки системы",
    "agent_profiles": "Профили специализированных агентов",
    "memory": "Конфигурация памяти",
    "tools": "Настройки инструментов",
    "visualization": "Настройки визуализации"
}

# Основные настройки KittyCore 3.0
DEFAULT_CONFIG = {
    "system": {
        "max_agents": 50,
        "memory_limit_mb": 1024,
        "async_timeout": 30,
        "event_history_limit": 1000
    },
    "orchestrator": {
        "task_complexity_threshold": 0.7,
        "agent_spawn_timeout": 30,
        "result_aggregation_timeout": 300
    },
    "memory": {
        "working_memory_ttl": 3600,
        "short_term_capacity": 100,
        "long_term_capacity": 10000,
        "sync_interval": 60
    },
    "visualization": {
        "auto_generate_graphs": True,
        "real_time_updates": True,
        "mermaid_theme": "cyber_kittens"
    }
} 