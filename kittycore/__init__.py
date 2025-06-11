"""
🐱 KittyCore 3.0 - Саморедуплицирующаяся Агентная Система

═══════════════════════════════════════════════════════════════════
    ПРИНЦИП: "Агенты создают агентов, коллективный интеллект превыше всего"
═══════════════════════════════════════════════════════════════════

🔄 САМОПОРОЖДЕНИЕ: Агенты создают других агентов под задачи
🧠 КОЛЛЕКТИВНАЯ ПАМЯТЬ: Общая память и знания для всей команды агентов  
📊 ГРАФ-ОРКЕСТРАЦИЯ: Визуальное планирование и выполнение сложных процессов
🎯 АДАПТИВНОСТЬ: Система адаптируется под сложность и тип задач
👤 HUMAN-AI СИНЕРГИЯ: Умное вмешательство человека в нужные моменты
🚀 САМООБУЧЕНИЕ: Система улучшается на основе результатов

╔══════════════════════════════════════════════════════════════════════╗
║                    АРХИТЕКТУРА KITTYCORE 3.0                        ║
╚══════════════════════════════════════════════════════════════════════╝

🧭 OrchestratorAgent - Главный дирижёр системы
🏭 AgentFactory 2.0 - Фабрика агентов нового поколения
🧠 CollectiveMemory - Коллективная память системы
📊 WorkflowGraph - Граф рабочих процессов  
🔀 ConditionalLogic - Умная логика принятия решений
👤 HumanCollaboration - Сотрудничество с человеком
🔄 SelfImprovement - Самосовершенствование системы

═══════════════════════════════════════════════════════════════════
"""

__version__ = "3.0.0"
__author__ = "CyberKitty Team"
__description__ = "Саморедуплицирующаяся агентная система с коллективным интеллектом"

# ====== ОСНОВНЫЕ КОМПОНЕНТЫ СИСТЕМЫ ======

# Главный оркестратор (Этап 2 - активен)
from .core.orchestrator import (
    OrchestratorAgent, OrchestratorConfig, UnifiedKittyCoreEngine, UnifiedConfig,
    create_orchestrator, solve_with_orchestrator
)

# TODO: Остальные core компоненты будут активированы в следующих этапах
# from .core.memory_management import MemoryManagementEngine  
# from .core.conditional_logic import AdvancedConditionalEngine
# from .core.human_collaboration import HumanInterventionEngine
# from .core.graph_workflow import GraphVisualizationEngine
# from .core.self_improvement import SelfImprovementEngine

# Система агентов (мигрированы в новую структуру)
from .agents import Agent, AgentConfig, AgentFactory, AgentSpecification

# Система памяти (мигрированы)
from .memory import Memory, SimpleMemory, PersistentMemory

# Инструменты (мигрированы)
from .tools import Tool, ToolResult

# Конфигурация (мигрированы)
from .config import Config, get_config

# ====== ОБРАТНАЯ СОВМЕСТИМОСТЬ ======
# TODO: Удалить после завершения миграции

# Пока оставляем старые импорты для совместимости
# from .agent import Agent as LegacyAgent
# from .agent_factory import AgentFactory as LegacyAgentFactory
# from .master_agent import MasterAgent, create_master_agent

# ====== ЭКСПОРТ КОМПОНЕНТОВ ======

__all__ = [
    # Версия и метаинформация
    "__version__", "__author__", "__description__",
    
    # Основные движки KittyCore 3.0
    "UnifiedKittyCoreEngine",
    "OrchestratorAgent", "OrchestratorConfig", "UnifiedConfig",
    "create_orchestrator", "solve_with_orchestrator",
    
    # Система агентов
    "Agent", "AgentConfig", "AgentFactory", "AgentSpecification",
    
    # Система памяти
    "Memory", "SimpleMemory", "PersistentMemory",
    
    # Инструменты
    "Tool", "ToolResult",
    
    # Конфигурация
    "Config", "get_config",
    
    # Обратная совместимость (временно)
    # "MasterAgent", "create_master_agent"
]

# ====== БЫСТРЫЙ СТАРТ ======

def create_agent(prompt: str, **kwargs) -> Agent:
    """
    🚀 Быстрое создание агента
    
    Args:
        prompt: Системный промпт агента
        **kwargs: Дополнительные параметры (model, tools, memory)
    
    Returns:
        Готовый к работе агент
    
    Example:
        >>> agent = kittycore.create_agent("You are a helpful assistant")
        >>> result = agent.run("Hello, world!")
    """
    return Agent(prompt, **kwargs)

def create_agent_team(project_description: str) -> list:
    """
    🤖 Создание команды агентов для проекта
    
    Args:
        project_description: Описание проекта
        
    Returns:
        Список специализированных агентов
    
    Example:
        >>> team = kittycore.create_agent_team("Create a web scraper")
        >>> # Автоматически создаст агентов: планировщик, разработчик, тестер
    """
    factory = AgentFactory()
    return factory.create_collaborative_team(project_description)

# Добавляем функции в экспорт
__all__.extend(["create_agent", "create_agent_team"])

# ====== СИСТЕМА ЛОГИРОВАНИЯ ======

import logging
from pathlib import Path

# Создаём папку для логов
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Настраиваем логирование для KittyCore
logger = logging.getLogger("kittycore")
if not logger.handlers:
    handler = logging.FileHandler(logs_dir / "kittycore.log")
    handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

logger.info(f"🐱 KittyCore {__version__} инициализирован")
logger.info("🔄 Саморедуплицирующаяся агентная система готова к работе")

# ====== ПРИНЦИПЫ KITTYCORE 3.0 ======

PRINCIPLES = {
    "self_replication": "Агенты создают других агентов под конкретные задачи",
    "collective_memory": "Общая память и знания для всей команды агентов", 
    "graph_orchestration": "Визуальное планирование и выполнение процессов",
    "adaptivity": "Система адаптируется под сложность и тип задач",
    "human_ai_synergy": "Умное вмешательство человека в нужные моменты",
    "self_learning": "Система улучшается на основе результатов"
}

ARCHITECTURE_COMPONENTS = {
    "orchestrator": "OrchestratorAgent - главный дирижёр системы",
    "agent_factory": "AgentFactory 2.0 - фабрика агентов нового поколения", 
    "collective_memory": "CollectiveMemory - коллективная память системы",
    "workflow_graph": "WorkflowGraph - граф рабочих процессов",
    "conditional_logic": "ConditionalLogic - умная логика принятия решений",
    "human_collaboration": "HumanCollaboration - сотрудничество с человеком",
    "self_improvement": "SelfImprovement - самосовершенствование системы"
}

logger.info("🚀 KittyCore 3.0 - готов превосходить CrewAI, LangGraph, AutoGen и Swarm!") 