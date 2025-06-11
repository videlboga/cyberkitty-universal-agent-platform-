"""
📊 KittyCore 3.0 - Visualization System
Система визуализации агентных процессов и граф-оркестрации
"""

# Визуализация (будут добавлены при миграции)
# from .graph_renderer import GraphRenderer
# from .mermaid_generator import MermaidGenerator
# from .progress_monitor import ProgressMonitor

__version__ = "3.0.0"
__all__ = [
    # "GraphRenderer",
    # "MermaidGenerator",
    # "ProgressMonitor"
]

# Типы визуализации
VISUALIZATION_TYPES = {
    "workflow_graph": "Граф рабочих процессов",
    "agent_network": "Сеть взаимодействия агентов",
    "memory_map": "Карта коллективной памяти", 
    "progress_dashboard": "Dashboard прогресса выполнения",
    "performance_analytics": "Аналитика производительности"
} 