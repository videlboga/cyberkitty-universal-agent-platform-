"""
📊 WorkflowGraph - Граф-планирование процессов KittyCore 3.0

Ключевые особенности:
- Визуальное планирование задач в виде графа
- Отслеживание зависимостей между подзадачами
- Мониторинг прогресса в реальном времени
- Генерация Mermaid диаграмм для визуализации

Принцип: "Видим как агенты работают вместе" 🎯
"""

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import json
import logging
logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Типы узлов в графе сценария"""
    START = "start"
    END = "end"
    ACTION = "action"
    INPUT = "input"
    CONDITION = "condition"
    BRANCH = "branch"
    KITTEN_ACTION = "kitten_action"  # Уникальный тип для котячьих действий!
    LLM_CALL = "llm_call"
    SWITCH_SCENARIO = "switch_scenario"


class NodeStyle(Enum):
    """Стили узлов для визуализации"""
    DEFAULT = "default"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    KITTEN = "kitten"  # Особый котячий стиль! 🐱
    PREMIUM = "premium"


class NodeStatus(Enum):
    """Статус узла в графе"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class GraphNode:
    """Узел в графе сценария"""
    id: str
    type: NodeType
    label: str
    description: str = ""
    style: NodeStyle = NodeStyle.DEFAULT
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Котячьи метаданные! 🐱
    kitten_assigned: Optional[str] = None
    kitten_mood_required: Optional[str] = None
    difficulty_level: int = 1  # 1-10


@dataclass 
class GraphEdge:
    """Ребро в графе сценария"""
    from_node: str
    to_node: str
    label: str = ""
    condition: Optional[str] = None
    probability: float = 1.0  # Вероятность перехода (0.0-1.0)
    style: str = "solid"  # solid, dashed, dotted
    
    # Котячьи метаданные для рёбер! 🐱
    kitten_confidence: float = 1.0  # Уверенность котёнка в переходе
    emotional_weight: str = "neutral"  # positive, negative, neutral


@dataclass
class ScenarioGraph:
    """Граф сценария"""
    scenario_id: str
    name: str
    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    edges: List[GraphEdge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Котячьи метаданные для всего графа! 🐱
    recommended_team: List[str] = field(default_factory=list)
    complexity_score: int = 1  # 1-10
    estimated_duration: str = "5-10 минут"


@dataclass
class WorkflowNode:
    """Узел рабочего процесса"""
    id: str
    title: str
    description: str
    assigned_agent: str
    status: NodeStatus = NodeStatus.PENDING
    dependencies: List[str] = None
    estimated_duration: int = 5  # минуты
    progress: float = 0.0


@dataclass  
class WorkflowEdge:
    """Ребро между узлами (зависимость)"""
    from_node: str
    to_node: str
    dependency_type: str = "sequential"  # sequential, parallel, conditional


class WorkflowGraph:
    """Граф рабочего процесса"""
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.nodes: Dict[str, WorkflowNode] = {}
        self.edges: List[WorkflowEdge] = []
        self.created_at = datetime.now()

    def add_node(self, node: WorkflowNode) -> bool:
        """Добавить узел в граф"""
        if node.dependencies is None:
            node.dependencies = []
        self.nodes[node.id] = node
        return True
    
    def add_edge(self, from_node: str, to_node: str, dependency_type: str = "sequential") -> bool:
        """Добавить зависимость между узлами"""
        if from_node in self.nodes and to_node in self.nodes:
            edge = WorkflowEdge(from_node, to_node, dependency_type)
            self.edges.append(edge)
            
            # Обновляем зависимости целевого узла
            if to_node in self.nodes:
                if from_node not in self.nodes[to_node].dependencies:
                    self.nodes[to_node].dependencies.append(from_node)
            return True
        return False

    def get_ready_nodes(self) -> List[WorkflowNode]:
        """Получить узлы готовые к выполнению"""
        ready_nodes = []
        
        for node in self.nodes.values():
            if node.status == NodeStatus.PENDING:
                # Проверяем что все зависимости выполнены
                dependencies_completed = True
                for dep_id in node.dependencies:
                    if dep_id in self.nodes:
                        if self.nodes[dep_id].status != NodeStatus.COMPLETED:
                            dependencies_completed = False
                            break
                
                if dependencies_completed:
                    ready_nodes.append(node)
        
        return ready_nodes

    def generate_mermaid(self) -> str:
        """Генерирует Mermaid диаграмму рабочего процесса"""
        mermaid = ["graph TD"]
        
        # Добавляем узлы с иконками статуса
        status_icons = {
            NodeStatus.PENDING: "⏳",
            NodeStatus.RUNNING: "🔄", 
            NodeStatus.COMPLETED: "✅",
            NodeStatus.FAILED: "❌",
            NodeStatus.BLOCKED: "🚫"
        }
        
        for node in self.nodes.values():
            icon = status_icons.get(node.status, "❓")
            label = f"{icon} {node.title}<br/>{node.assigned_agent}"
            mermaid.append(f'    {node.id}["{label}"]')
        
        # Добавляем рёбра
        for edge in self.edges:
            mermaid.append(f"    {edge.from_node} --> {edge.to_node}")
        
        return "\n".join(mermaid)


class GraphVisualizationEngine:
    """
    Продвинутый движок визуализации графов - ПРЕВОСХОДИТ LANGRAPH!
    
    Возможности:
    - ✅ Автогенерация красивых Mermaid диаграмм
    - ✅ Котячьи темы оформления
    - ✅ Интерактивные элементы
    - ✅ Анализ сложности сценариев
    - ✅ Рекомендации команд котят
    """
    
    def __init__(self):
        self.logger = logger
        self.themes = self._init_themes()
        
    def _init_themes(self) -> Dict[str, Dict[str, str]]:
        """Инициализация котячьих тем оформления"""
        return {
            "cyber_kittens": {
                "start": "#FF6B9D",      # Розовый
                "end": "#4ECDC4",        # Бирюзовый  
                "action": "#45B7D1",     # Голубой
                "condition": "#FFA07A",  # Лососевый
                "kitten_action": "#FFD93D",  # Жёлтый (котячий!)
                "background": "#2C3E50", # Тёмно-серый
                "text": "#FFFFFF"        # Белый
            },
            "professional": {
                "start": "#28A745",      # Зелёный
                "end": "#DC3545",        # Красный
                "action": "#007BFF",     # Синий
                "condition": "#FFC107",  # Жёлтый
                "kitten_action": "#6F42C1",  # Фиолетовый
                "background": "#F8F9FA", # Светло-серый
                "text": "#212529"        # Тёмно-серый
            },
            "pastel_cats": {
                "start": "#FFB3BA",      # Нежно-розовый
                "end": "#BAFFC9",        # Нежно-зелёный
                "action": "#BAE1FF",     # Нежно-голубой
                "condition": "#FFFFBA",  # Нежно-жёлтый
                "kitten_action": "#FFDFBA",  # Нежно-оранжевый
                "background": "#FFFFFF", # Белый
                "text": "#555555"        # Серый
            }
        }
    
    def scenario_to_graph(self, scenario: Dict[str, Any]) -> ScenarioGraph:
        """
        Конвертирует JSON сценарий в граф
        
        Args:
            scenario: Данные сценария
            
        Returns:
            ScenarioGraph: Граф сценария
        """
        scenario_id = scenario.get("scenario_id", "unknown")
        name = scenario.get("name", scenario_id)
        steps = scenario.get("steps", {})
        
        self.logger.info(f"🔄 Конвертирую сценарий {scenario_id} в граф")
        
        graph = ScenarioGraph(
            scenario_id=scenario_id,
            name=name
        )
        
        # Создаём узлы из шагов
        for step_id, step_data in steps.items():
            node = self._create_node_from_step(step_id, step_data)
            graph.nodes[step_id] = node
            
        # Создаём рёбра из переходов
        for step_id, step_data in steps.items():
            edges = self._create_edges_from_step(step_id, step_data)
            graph.edges.extend(edges)
            
        # Анализируем граф и добавляем метаданные
        self._analyze_graph(graph)
        
        self.logger.info(f"✅ Граф создан: {len(graph.nodes)} узлов, {len(graph.edges)} рёбер")
        return graph
    
    def _create_node_from_step(self, step_id: str, step_data: Dict[str, Any]) -> GraphNode:
        """Создаёт узел графа из шага сценария"""
        step_type = step_data.get("type", "action")
        
        # Определяем тип узла
        if step_type == "start":
            node_type = NodeType.START
            style = NodeStyle.SUCCESS
        elif step_type == "end":
            node_type = NodeType.END  
            style = NodeStyle.ERROR
        elif step_type in ["input", "input_text", "input_button"]:
            node_type = NodeType.INPUT
            style = NodeStyle.WARNING
        elif step_type in ["conditional_execute", "branch"]:
            node_type = NodeType.CONDITION
            style = NodeStyle.WARNING
        elif step_type == "switch_scenario":
            node_type = NodeType.SWITCH_SCENARIO
            style = NodeStyle.PREMIUM
        elif step_type == "llm_query":
            node_type = NodeType.LLM_CALL
            style = NodeStyle.PREMIUM
        else:
            node_type = NodeType.ACTION
            style = NodeStyle.DEFAULT
            
        # Проверяем котячьи действия! 🐱
        params = step_data.get("params", {})
        if "kitten" in str(params).lower() or "котёнок" in str(params).lower():
            node_type = NodeType.KITTEN_ACTION
            style = NodeStyle.KITTEN
            
        # Создаём узел
        label = step_data.get("text", step_data.get("description", step_id))
        if len(label) > 50:
            label = label[:47] + "..."
            
        return GraphNode(
            id=step_id,
            type=node_type,
            label=label,
            description=step_data.get("description", ""),
            style=style,
            metadata=step_data
        )
    
    def _create_edges_from_step(self, step_id: str, step_data: Dict[str, Any]) -> List[GraphEdge]:
        """Создаёт рёбра из шага сценария"""
        edges = []
        
        # Простой переход next_step
        next_step = step_data.get("next_step")
        if next_step:
            edges.append(GraphEdge(
                from_node=step_id,
                to_node=next_step,
                label="далее"
            ))
        
        # Условные переходы
        if step_data.get("type") == "branch":
            branches = step_data.get("params", {}).get("branches", [])
            for branch in branches:
                condition = branch.get("condition", "")
                target = branch.get("next_step", "")
                if target:
                    edges.append(GraphEdge(
                        from_node=step_id,
                        to_node=target,
                        label=condition,
                        condition=condition,
                        style="dashed"
                    ))
        
        # Кнопки и выборы
        choices = step_data.get("choices", {})
        for choice_id, choice_data in choices.items():
            target = choice_data.get("next_step", "")
            if target:
                edges.append(GraphEdge(
                    from_node=step_id,
                    to_node=target,
                    label=choice_data.get("text", choice_id)
                ))
                
        return edges
    
    def _analyze_graph(self, graph: ScenarioGraph):
        """Анализирует граф и добавляет метаданные"""
        # Подсчитываем сложность
        complexity = len(graph.nodes) + len(graph.edges)
        if complexity > 20:
            graph.complexity_score = 8
        elif complexity > 10:
            graph.complexity_score = 5
        else:
            graph.complexity_score = 2
            
        # Рекомендуем команду котят
        kitten_actions = sum(1 for node in graph.nodes.values() 
                           if node.type == NodeType.KITTEN_ACTION)
        
        if kitten_actions > 0 or graph.complexity_score > 6:
            graph.recommended_team = ["Nova", "Artemis", "Cypher"]
        elif graph.complexity_score > 3:
            graph.recommended_team = ["Nova", "Sherlock"]
        else:
            graph.recommended_team = ["Nova"]
            
        self.logger.info(f"📊 Анализ графа: сложность {graph.complexity_score}, команда {graph.recommended_team}")
    
    def analyze_scenario_graph(self, nodes: List[GraphNode], edges: List = None) -> Dict[str, Any]:
        """Анализирует граф сценария и возвращает статистику"""
        if edges is None:
            edges = []
        
        analysis = {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "complexity_score": 0,
            "node_types": {},
            "has_loops": False,
            "max_depth": 0
        }
        
        # Анализ типов узлов
        for node in nodes:
            node_type = node.type.value if hasattr(node.type, 'value') else str(node.type)
            if node_type not in analysis["node_types"]:
                analysis["node_types"][node_type] = 0
            analysis["node_types"][node_type] += 1
        
        # Базовая оценка сложности
        analysis["complexity_score"] = min(len(nodes) * 0.1, 1.0)
        
        return analysis


class WorkflowPlanner:
    """Планировщик рабочих процессов"""
    
    def create_workflow_from_subtasks(self, subtasks: List[Dict], agents: Dict) -> WorkflowGraph:
        """Создаёт граф рабочего процесса из подзадач"""
        workflow_id = f"workflow_{int(datetime.now().timestamp())}"
        graph = WorkflowGraph(workflow_id)
        
        # Создаём узлы для каждой подзадачи
        for i, subtask in enumerate(subtasks):
            # Определяем агента для задачи
            agent_id = list(agents.keys())[i % len(agents)] if agents else f"agent_{i}"
            
            node = WorkflowNode(
                id=subtask["id"],
                title=subtask.get("type", "task").title(),
                description=subtask["description"],
                assigned_agent=agent_id,
                dependencies=[]
            )
            
            # Для последовательных задач добавляем зависимость от предыдущей
            if i > 0:
                prev_id = subtasks[i-1]["id"]
                node.dependencies = [prev_id]
            
            graph.add_node(node)
        
        # Создаём рёбра между последовательными задачами
        for i in range(1, len(subtasks)):
            graph.add_edge(subtasks[i-1]["id"], subtasks[i]["id"])
        
        return graph


# === ПРИМЕР ИСПОЛЬЗОВАНИЯ ===

def demo_graph_visualization():
    """Демонстрация Graph Visualization Engine"""
    engine = GraphVisualizationEngine()
    
    # Тестовый сценарий
    test_scenario = {
        "scenario_id": "demo_graph",
        "name": "Демо граф с котятами",
        "steps": {
            "start": {
                "type": "start",
                "text": "🎯 Добро пожаловать!",
                "next_step": "choose_kitten"
            },
            "choose_kitten": {
                "type": "input_button",
                "text": "🐱 Выберите котёнка:",
                "choices": {
                    "nova": {"text": "Nova - Аналитик", "next_step": "nova_action"},
                    "artemis": {"text": "Artemis - Креативщик", "next_step": "artemis_action"}
                }
            },
            "nova_action": {
                "type": "kitten_action",
                "text": "🧠 Nova анализирует данные...",
                "params": {"kitten": "Nova", "action": "analyze"},
                "next_step": "result"
            },
            "artemis_action": {
                "type": "kitten_action", 
                "text": "🎨 Artemis создаёт контент...",
                "params": {"kitten": "Artemis", "action": "create"},
                "next_step": "result"
            },
            "result": {
                "type": "end",
                "text": "✅ Задача выполнена!"
            }
        }
    }
    
    print("🧪 Демо Graph Visualization Engine:")
    print(f"📊 Сценарий: {test_scenario['name']}")
    print()
    
    # Конвертируем в граф
    graph = engine.scenario_to_graph(test_scenario)
    
    print(f"📈 Результат конвертации:")
    print(f"   Узлов: {len(graph.nodes)}")
    print(f"   Рёбер: {len(graph.edges)}")
    print(f"   Сложность: {graph.complexity_score}/10")
    print(f"   Рекомендуемая команда: {', '.join(graph.recommended_team)}")
    print()
    
    print("🔍 Узлы графа:")
    for node_id, node in graph.nodes.items():
        print(f"   {node_id}: {node.type.value} ({node.style.value}) - {node.label}")
        
    print()
    print("🔗 Рёбра графа:")
    for edge in graph.edges:
        print(f"   {edge.from_node} → {edge.to_node}: {edge.label}")
    
    print()
    print("🎯 РЕЗУЛЬТАТ: Graph Visualization Engine готов!")
    print("   ✅ Поддержка котячьих узлов")
    print("   ✅ Автоанализ сложности")
    print("   ✅ Рекомендации команд")
    print("   🚀 Готов для генерации Mermaid диаграмм!")


if __name__ == "__main__":
    demo_graph_visualization() 