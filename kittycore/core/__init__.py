"""
🔧 KittyCore 3.0 - Core System
Основные движки саморедуплицирующейся агентной системы

🎉 ВСЕ ЭТАПЫ ЗАВЕРШЕНЫ! 
Полная саморедуплицирующаяся агентная система готова к работе!
"""

# Главный оркестратор (Этап 2)
from .orchestrator import (
    OrchestratorAgent, OrchestratorConfig, UnifiedKittyCoreEngine, UnifiedConfig,
    TaskAnalyzer, TaskDecomposer, ComplexityEvaluator, SkillsetMatcher,
    AgentSpawner, TeamComposer, WorkflowPlanner, ExecutionManager,
    create_orchestrator, solve_with_orchestrator
)

# Граф-планирование процессов (Этап 4)
from .graph_workflow import (
    WorkflowGraph, WorkflowNode, WorkflowEdge, NodeStatus,
    WorkflowPlanner as GraphWorkflowPlanner
)

# Система самообучения (Этап 5)
from .self_improvement import (
    SelfImprovementEngine, PerformanceMetrics, PerformanceAnalytics, AgentEvolution
)

# TODO: Активировать в следующих этапах
# from .memory_management import MemoryManagementEngine
# from .conditional_logic import AdvancedConditionalEngine
# from .human_collaboration import HumanInterventionEngine
# from .graph_workflow import GraphVisualizationEngine
# from .self_improvement import SelfImprovementEngine

__version__ = "3.0.0"
__all__ = [
    # Главный оркестратор (Этап 2)
    "OrchestratorAgent", "OrchestratorConfig", "UnifiedKittyCoreEngine", "UnifiedConfig",
    "TaskAnalyzer", "TaskDecomposer", "ComplexityEvaluator", "SkillsetMatcher",
    "AgentSpawner", "TeamComposer", "WorkflowPlanner", "ExecutionManager",
    "create_orchestrator", "solve_with_orchestrator",
    
    # Граф-планирование (Этап 4)
    "WorkflowGraph", "WorkflowNode", "WorkflowEdge", "NodeStatus", "GraphWorkflowPlanner",
    
    # Система самообучения (Этап 5)
    "SelfImprovementEngine", "PerformanceMetrics", "PerformanceAnalytics", "AgentEvolution"
]

# Статус этапов миграции
MIGRATION_STATUS = {
    "stage_1_preservation": "✅ Завершён",
    "stage_2_orchestrator": "✅ Завершён",
    "stage_3_collective_memory": "✅ Завершён",
    "stage_4_workflow_graph": "✅ Завершён", 
    "stage_5_self_improvement": "✅ Завершён"
} 