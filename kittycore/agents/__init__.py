"""
🤖 KittyCore 3.0 - Agent System
Система саморедуплицирующихся агентов
"""

# Базовая система агентов (обратная совместимость)
from .base_agent import Agent, AgentConfig
from .agent_factory import AgentFactory, AgentSpecification
from .working_agent import WorkingAgent

# Специализированные агенты
# from .specialized.nova_agent import NovaAgent
# from .specialized.artemis_agent import ArtemisAgent  
# from .specialized.cipher_agent import CipherAgent
# from .specialized.ada_agent import AdaAgent

__version__ = "3.0.0"
__all__ = [
    # Базовые агенты (обратная совместимость)
    "Agent", "AgentConfig", "AgentFactory", "AgentSpecification",
    
    # Специализированные агенты (будут добавлены)
    # "NovaAgent",
    # "ArtemisAgent", 
    # "CipherAgent",
    # "AdaAgent",
    "WorkingAgent",
]

# Типы агентов в системе
AGENT_TYPES = {
    "nova": "Анализ данных и статистика",
    "artemis": "Контент и дизайн", 
    "cipher": "Безопасность и тестирование",
    "ada": "Программирование и разработка",
    "sherlock": "Поиск и исследования",
    "warren": "Финансы и бюджет",
    "viral": "Маркетинг и реклама"
} 