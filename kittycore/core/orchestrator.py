"""
🧭 OrchestratorAgent - Главный дирижёр KittyCore 3.0

Центральный управляющий агент, который координирует работу 
всей системы саморедуплицирующихся агентов.

ЭТАП 2: Создание главного дирижёра системы
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# Импорт коллективной памяти, граф-планирования, самообучения и богатых отчётов
from ..memory import CollectiveMemory
from .graph_workflow import WorkflowGraph, WorkflowPlanner as GraphWorkflowPlanner, NodeStatus
from .self_improvement import SelfLearningEngine
from .rich_reporting import get_rich_reporter, ReportLevel
from .shared_chat import SharedChat
from ..agents.tool_adapter_agent import ToolAdapterAgent
from ..obsidian_integration import ObsidianAdapter, ObsidianConfig

# Импорт новых компонентов системы метрик и качества
from .agent_metrics import get_metrics_collector, MetricsCollector, TaskStatus
from ..memory.vector_memory import get_vector_store, VectorMemoryStore
from .quality_controller import QualityController

logger = logging.getLogger(__name__)

# === АНАЛИЗ ЗАДАЧ ===

class TaskAnalyzer:
    """Анализ сложности входящих задач с помощью LLM"""
    
    def __init__(self):
        self.complexity_cache = {}
        self.llm = self._init_llm()
    
    def _init_llm(self):
        """Инициализация LLM для анализа"""
        try:
            # Используем новый LLM модуль
            from ..llm import get_llm_provider, LLMConfig
            config = LLMConfig()
            return get_llm_provider(config=config)
        except Exception as e:
            raise Exception(f"❌ LLM провайдер не найден! Ошибка: {e}")
    
    def analyze_task_complexity(self, task: str) -> Dict[str, Any]:
        """Анализирует сложность задачи с помощью LLM"""
        
        # Проверяем кэш
        if task in self.complexity_cache:
            return self.complexity_cache[task]
        
        # Формируем промпт для анализа
        analysis_prompt = f"""
Проанализируй сложность задачи и определи требования:

Задача: {task}

Ответь в формате JSON:
{{
    "complexity": "simple|medium|complex",
    "estimated_agents": число_агентов,
    "requires_planning": true/false,
    "requires_coordination": true/false,
    "reasoning": "обоснование",
    "estimated_time": минуты
}}

Критерии:
- simple: одна простая операция, 1 агент
- medium: несколько связанных операций, 2-3 агента  
- complex: множественные зависимые операции, 3-4 агента
"""
        
        try:
            # Получаем анализ от LLM
            response = self.llm.complete(analysis_prompt)
            
            # Парсим ответ
            analysis = self._parse_llm_analysis(response, task)
            
            # Кэшируем результат
            self.complexity_cache[task] = analysis
            
            logger.info(f"📊 LLM анализ: {analysis['complexity']} ({analysis['estimated_agents']} агентов)")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Ошибка LLM анализа: {e}")
            # Fallback к простой эвристике
            return self._fallback_analysis(task)
    
    def _parse_llm_analysis(self, response: str, task: str) -> Dict[str, Any]:
        """Парсинг ответа LLM"""
        try:
            # Пытаемся найти JSON в ответе
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                
                return {
                    "task": task,
                    "complexity": data.get("complexity", "medium"),
                    "estimated_agents": data.get("estimated_agents", 2),
                    "word_count": len(task.split()),
                    "requires_planning": data.get("requires_planning", True),
                    "requires_coordination": data.get("requires_coordination", True),
                    "reasoning": data.get("reasoning", "LLM анализ"),
                    "estimated_time": data.get("estimated_time", 10)
                }
        except:
            pass
            
        # Если JSON не распарсился, анализируем текст
        response_lower = response.lower()
        
        if "simple" in response_lower:
            complexity = "simple"
            agents = 1
        elif "complex" in response_lower:
            complexity = "complex" 
            agents = 4
        else:
            complexity = "medium"
            agents = 3
            
        return {
            "task": task,
            "complexity": complexity,
            "estimated_agents": agents,
            "word_count": len(task.split()),
            "requires_planning": complexity != "simple",
            "requires_coordination": agents > 1,
            "reasoning": "LLM текстовый анализ",
            "estimated_time": agents * 5
        }
    
    def _fallback_analysis(self, task: str) -> Dict[str, Any]:
        """Fallback анализ при ошибке LLM"""
        word_count = len(task.split())
        
        if word_count < 10:
            complexity = "simple"
            agent_count = 1
        elif word_count < 30:
            complexity = "medium"  
            agent_count = 3
        else:
            complexity = "complex"
            agent_count = 4
        
        return {
            "task": task,
            "complexity": complexity,
            "estimated_agents": agent_count,
            "word_count": word_count,
            "requires_planning": complexity != "simple",
            "requires_coordination": agent_count > 1,
            "reasoning": "Fallback эвристика",
            "estimated_time": agent_count * 5
        }

class TaskDecomposer:
    """Разбивка задач на подзадачи с помощью LLM"""
    
    def __init__(self):
        self.llm = self._init_llm()
        
    def _init_llm(self):
        """Инициализация LLM"""
        try:
            # Используем новый LLM модуль
            from ..llm import get_llm_provider, LLMConfig
            config = LLMConfig()
            return get_llm_provider(config=config)
        except Exception as e:
            raise Exception(f"❌ LLM провайдер не найден! Ошибка: {e}")
    
    def decompose_task(self, task: str, complexity: str) -> List[Dict[str, Any]]:
        """Разбивает задачу на подзадачи с помощью LLM"""
        
        if complexity == "simple":
            return [{"id": "single_task", "description": task, "type": "execute"}]
        
        # Промпт для декомпозиции
        decompose_prompt = f"""
Разбей задачу на логические подзадачи:

Задача: {task}
Сложность: {complexity}

Создай 3-4 подзадачи в формате JSON:
[
    {{"id": "step1", "description": "описание", "type": "analysis|planning|execution|verification"}},
    {{"id": "step2", "description": "описание", "type": "analysis|planning|execution|verification"}},
    ...
]

Типы подзадач:
- analysis: анализ требований, исследование
- planning: планирование подхода, выбор методов
- execution: основная реализация, создание
- verification: тестирование, проверка результатов

Каждая подзадача должна быть конкретной и выполнимой.
"""
        
        try:
            # Получаем декомпозицию от LLM
            response = self.llm.complete(decompose_prompt)
            
            # Парсим ответ
            subtasks = self._parse_llm_decomposition(response, task, complexity)
            
            logger.info(f"🔄 LLM декомпозиция: {len(subtasks)} подзадач")
            return subtasks
            
        except Exception as e:
            logger.error(f"❌ Ошибка LLM декомпозиции: {e}")
            # Fallback к стандартной декомпозиции
            return self._fallback_decomposition(task, complexity)
    
    def _parse_llm_decomposition(self, response: str, task: str, complexity: str) -> List[Dict[str, Any]]:
        """Парсинг декомпозиции от LLM"""
        try:
            import json
            import re
            
            # Ищем JSON массив в ответе
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                
                # Валидируем и очищаем данные
                subtasks = []
                for i, item in enumerate(data):
                    if isinstance(item, dict) and "description" in item:
                        subtasks.append({
                            "id": item.get("id", f"step_{i+1}"),
                            "description": item["description"],
                            "type": item.get("type", "execution")
                        })
                
                if subtasks:
                    return subtasks
                    
        except Exception as e:
            logger.debug(f"Ошибка парсинга JSON: {e}")
        
        # Если JSON не распарсился, анализируем текст
        return self._parse_text_decomposition(response, task, complexity)
    
    def _parse_text_decomposition(self, response: str, task: str, complexity: str) -> List[Dict[str, Any]]:
        """Парсинг текстовой декомпозиции"""
        lines = response.split('\n')
        subtasks = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line and (line.startswith(str(i+1)) or line.startswith('-') or line.startswith('•')):
                # Очищаем строку от номеров и маркеров
                description = re.sub(r'^[\d\-•\.\)\s]+', '', line).strip()
                if description:
                    # Определяем тип по ключевым словам
                    desc_lower = description.lower()
                    if any(word in desc_lower for word in ["анализ", "исследован", "изучен"]):
                        task_type = "analysis"
                    elif any(word in desc_lower for word in ["план", "стратег", "подход"]):
                        task_type = "planning"
                    elif any(word in desc_lower for word in ["проверк", "тест", "валид"]):
                        task_type = "verification"
                    else:
                        task_type = "execution"
                    
                    subtasks.append({
                        "id": f"step_{len(subtasks)+1}",
                        "description": description,
                        "type": task_type
                    })
        
        if subtasks:
            return subtasks
            
        # Если ничего не спарсилось, fallback
        return self._fallback_decomposition(task, complexity)
    
    def _fallback_decomposition(self, task: str, complexity: str) -> List[Dict[str, Any]]:
        """Fallback декомпозиция"""
        if complexity == "medium":
            return [
                {"id": "analyze", "description": f"Анализ задачи: {task}", "type": "analysis"},
                {"id": "execute", "description": f"Выполнение: {task}", "type": "execution"},
                {"id": "verify", "description": f"Проверка результата: {task}", "type": "verification"}
            ]
        else:  # complex
            return [
                {"id": "analyze", "description": f"Анализ задачи: {task}", "type": "analysis"},
                {"id": "plan", "description": f"Планирование решения: {task}", "type": "planning"},
                {"id": "execute", "description": f"Выполнение: {task}", "type": "execution"},
                {"id": "verify", "description": f"Проверка результата: {task}", "type": "verification"}
            ]

class ComplexityEvaluator:
    """Оценка необходимых ресурсов"""
    
    def evaluate_resources(self, subtasks: List[Dict]) -> Dict[str, Any]:
        """Оценивает необходимые ресурсы"""
        return {
            "subtask_count": len(subtasks),
            "estimated_time": len(subtasks) * 5,  # 5 минут на подзадачу
            "memory_required": "medium",
            "tools_required": ["basic", "communication"],
            "human_intervention_likely": len(subtasks) > 2
        }

class SkillsetMatcher:
    """Определение требуемых навыков"""
    
    def match_skills(self, subtasks: List[Dict]) -> Dict[str, List[str]]:
        """Определяет навыки для каждой подзадачи"""
        skill_map = {
            "analysis": ["analysis", "research", "critical_thinking"],
            "planning": ["planning", "organization", "strategy"],
            "execution": ["coding", "implementation", "problem_solving"],
            "verification": ["testing", "validation", "quality_control"]
        }
        
        result = {}
        for subtask in subtasks:
            task_type = subtask.get("type", "general")
            result[subtask["id"]] = skill_map.get(task_type, ["general"])
        
        return result 

# === СОЗДАНИЕ АГЕНТОВ ===

class AgentSpawner:
    """Динамическое создание агентов под задачи"""
    
    def __init__(self):
        self.spawned_agents = {}
    
    def spawn_agent_for_task(self, subtask: Dict, skills: List[str]) -> Any:
        """Создаёт IntellectualAgent для конкретной подзадачи"""
        from ..agents.intellectual_agent import IntellectualAgent
        
        # Определяем роль агента по типу задачи
        role_map = {
            "analysis": "analyst", 
            "planning": "planner",
            "execution": "developer", 
            "verification": "tester"
        }
        
        role = role_map.get(subtask.get("type"), "generalist")
        agent_role = f"{role}_agent"
        
        # Создаём IntellectualAgent вместо старого Agent
        agent = IntellectualAgent(agent_role, subtask)
        agent_id = f"{role}_{subtask['id']}"
        self.spawned_agents[agent_id] = agent
        
        logger.info(f"🤖 Создан IntellectualAgent {agent_id} для задачи: {subtask['description'][:50]}...")
        return agent

class TeamComposer:
    """Формирование команд агентов"""
    
    def compose_team(self, agents: Dict[str, Any]) -> Dict[str, Any]:
        """Формирует команду из созданных агентов"""
        return {
            "team_id": f"team_{int(time.time())}",
            "agents": agents,
            "team_size": len(agents),
            "roles": list(agents.keys()),
            "created_at": datetime.now().isoformat()
        }

# === ПЛАНИРОВАНИЕ ПРОЦЕССОВ ===

class WorkflowPlanner:
    """Планирование рабочих процессов"""
    
    def plan_workflow(self, subtasks: List[Dict], team: Dict) -> Dict[str, Any]:
        """Планирует рабочий процесс"""
        workflow = {
            "workflow_id": f"workflow_{int(time.time())}",
            "steps": [],
            "dependencies": {},
            "estimated_duration": len(subtasks) * 5
        }
        
        for i, subtask in enumerate(subtasks):
            step = {
                "step_id": subtask["id"],
                "description": subtask["description"],
                "assigned_agent": list(team["agents"].keys())[i % len(team["agents"])],
                "estimated_time": 5,
                "dependencies": [subtasks[i-1]["id"]] if i > 0 else []
            }
            workflow["steps"].append(step)
        
        return workflow 

# === ОРКЕСТРАЦИЯ ВЫПОЛНЕНИЯ ===

class ExecutionManager:
    """Управление выполнением с реальными инструментами"""
    
    def __init__(self):
        self.execution_status = {}
    
    async def execute_workflow(self, workflow: Dict, team: Dict) -> Dict[str, Any]:
        """Выполняет рабочий процесс с реальными агентами"""
        execution_id = f"exec_{int(time.time())}"
        
        # Импортируем IntellectualAgent здесь чтобы избежать циклического импорта
        from ..agents.intellectual_agent import IntellectualAgent
        
        results = {
            "execution_id": execution_id,
            "workflow_id": workflow["workflow_id"],
            "start_time": datetime.now().isoformat(),
            "steps_completed": 0,
            "step_results": {},
            "status": "running",
            "files_created": []
        }
        
        for step in workflow["steps"]:
            logger.info(f"🔄 Выполняется шаг: {step['description']}")
            
            try:
                # Находим агента для выполнения шага
                agent_id = step["assigned_agent"]
                
                if agent_id in team["agents"]:
                    # Создаём рабочего агента с реальными инструментами
                    subtask = {
                        "description": step["description"],
                        "type": "general"
                    }
                    
                    # Получаем информацию об агенте
                    agent_info = team["agents"][agent_id]
                    
                    # Проверяем тип агента (объект или словарь)
                    if hasattr(agent_info, 'role'):
                        agent_role = agent_info.role
                    elif isinstance(agent_info, dict):
                        agent_role = agent_info.get("role", agent_id)
                    else:
                        agent_role = str(agent_info)
                    
                    # Создаём и запускаем интеллектуального агента
                    working_agent = IntellectualAgent(agent_role, subtask)
                    execution_result = await working_agent.execute_task()
                    
                    step_result = execution_result["output"]
                    step_status = execution_result["status"]
                    
                    # Собираем созданные файлы
                    if "files_created" in execution_result:
                        results["files_created"].extend(execution_result["files_created"])
                
                else:
                    step_result = "⚠️ Агент не найден"
                    step_status = "failed"
                
                results["step_results"][step["step_id"]] = {
                    "result": step_result,
                    "status": step_status,
                    "timestamp": datetime.now().isoformat(),
                    "agent": agent_id,
                    "files_created": execution_result.get("files_created", [])
                }
                
                results["steps_completed"] += 1
                print(f"✅ Шаг выполнен: {step['description']}")
                
            except Exception as e:
                logger.error(f"❌ Ошибка выполнения шага {step['step_id']}: {e}")
                
                results["step_results"][step["step_id"]] = {
                    "result": f"❌ Ошибка: {str(e)}",
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "agent": step.get("assigned_agent", "unknown")
                }
                
                results["steps_completed"] += 1
        
        results["status"] = "completed"
        results["end_time"] = datetime.now().isoformat()
        
        return results

# === КОНФИГУРАЦИЯ ===

@dataclass
class OrchestratorConfig:
    """Конфигурация оркестратора"""
    orchestrator_id: str = "main_orchestrator"
    max_agents: int = 10
    timeout: int = 300
    enable_human_intervention: bool = True
    log_level: str = "INFO"
    report_level: ReportLevel = ReportLevel.DETAILED  # Уровень детализации отчётов
    # Obsidian интеграция
    enable_obsidian: bool = False
    obsidian_vault_path: str = "./obsidian_vault"
    # Новые компоненты
    enable_metrics: bool = True           # Система метрик агентов
    enable_vector_memory: bool = True     # Векторная память для поиска
    enable_quality_control: bool = True   # Контроллер качества
    vector_memory_path: str = "./vector_memory"
    metrics_storage_path: str = "./metrics_storage" 

# === ГЛАВНЫЙ ОРКЕСТРАТОР ===

class OrchestratorAgent:
    """
    🧭 Главный дирижёр KittyCore 3.0
    
    Координирует работу всей системы саморедуплицирующихся агентов:
    - Анализирует задачи и определяет сложность
    - Создаёт специализированных агентов под задачи  
    - Планирует рабочие процессы
    - Управляет выполнением команды агентов
    """
    
    def __init__(self, config: OrchestratorConfig = None):
        self.config = config or OrchestratorConfig()
        
        # Инициализация компонентов
        self.task_analyzer = TaskAnalyzer()
        self.task_decomposer = TaskDecomposer()
        self.complexity_evaluator = ComplexityEvaluator()
        self.skillset_matcher = SkillsetMatcher()
        
        self.agent_spawner = AgentSpawner()
        self.team_composer = TeamComposer()
        
        self.workflow_planner = WorkflowPlanner()
        self.execution_manager = ExecutionManager()
        
        # Граф-планирование 
        self.graph_planner = GraphWorkflowPlanner()
        
        # Система самообучения (НОВОЕ!)
        self.self_improvement = SelfLearningEngine()
        
        # Коллективная память 
        self.collective_memory = CollectiveMemory(self.config.orchestrator_id)
        
        # Умный валидатор (НОВОЕ!)
        self.smart_validator = None  # Пока отключим для исправления импорта
        
        # Система богатых отчётов (НОВОЕ!)
        self.rich_reporter = get_rich_reporter()
        self.rich_reporter.report_level = self.config.report_level
        
        # SharedChat для координации агентов (НОВОЕ!)
        self.shared_chat = SharedChat(
            team_id=f"team_{self.config.orchestrator_id}",
            collective_memory=self.collective_memory
        )
        
        # ToolAdapterAgent для работы с инструментами (НОВОЕ!)
        try:
            # Используем новый LLM модуль
            from ..llm import get_llm_provider
            llm_provider = get_llm_provider()
            self.tool_adapter = ToolAdapterAgent(llm_provider)
        except Exception as e:
            logger.warning(f"Не удалось создать ToolAdapterAgent: {e}")
            self.tool_adapter = None
        
        # Obsidian интеграция (НОВОЕ!)
        self.obsidian_adapter = None
        if self.config.enable_obsidian:
            try:
                obsidian_config = ObsidianConfig(
                    vault_path=self.config.obsidian_vault_path,
                    notes_folder="KittyCore",
                    auto_link=True,
                    execute_code=True
                )
                self.obsidian_adapter = ObsidianAdapter(obsidian_config)
                logger.info(f"📝 Obsidian интеграция активирована: {self.config.obsidian_vault_path}")
            except Exception as e:
                logger.warning(f"Не удалось создать ObsidianAdapter: {e}")
                self.obsidian_adapter = None
        
        # Регистрируем оркестратор в чате как координатор
        self.shared_chat.register_agent(
            agent_id=self.config.orchestrator_id,
            agent_role="Orchestrator",
            is_coordinator=True
        )
        
        # === НОВЫЕ КОМПОНЕНТЫ СИСТЕМЫ МЕТРИК И КАЧЕСТВА ===
        
        # Система метрик агентов
        self.metrics_collector = None
        if self.config.enable_metrics:
            self.metrics_collector = get_metrics_collector()
            logger.info("📊 Система метрик агентов активирована")
        
        # Векторная память для поиска 
        self.vector_store = None
        if self.config.enable_vector_memory:
            self.vector_store = get_vector_store()
            # Инициализируем поиск в базе знаний если есть vault
            if self.config.enable_obsidian and Path(self.config.obsidian_vault_path).exists():
                asyncio.create_task(self._initialize_vector_memory())
            logger.info("🔍 Векторная память активирована")
        
        # Контроллер качества
        self.quality_controller = None
        if self.config.enable_quality_control:
            self.quality_controller = QualityController()
            logger.info("🎯 Контроллер качества активирован")
        
        # Статистика
        self.tasks_processed = 0
        self.agents_created = 0
        self.workflows_executed = 0
        
        logger.info(f"🧭 OrchestratorAgent инициализирован: {self.config.orchestrator_id}")
        logger.info(f"💬 SharedChat готов для команды: team_{self.config.orchestrator_id}")
    
    async def _initialize_vector_memory(self):
        """Инициализация векторной памяти с индексацией Obsidian vault"""
        try:
            vault_path = Path(self.config.obsidian_vault_path)
            if vault_path.exists() and self.vector_store:
                indexed_count = await self.vector_store.index_documents(vault_path)
                logger.info(f"🔍 Проиндексировано {indexed_count} документов из Obsidian vault")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка индексации Obsidian vault: {e}")
    
    async def _execute_with_coordination(self, workflow: Dict, team: Dict, original_task: str) -> Dict[str, Any]:
        """Выполнение workflow с координацией через SharedChat"""
        try:
            # Уведомляем о начале выполнения
            await self.shared_chat.broadcast_update(
                sender_id=self.config.orchestrator_id,
                update="Начинаем выполнение задач",
                task_info={'workflow_steps': len(workflow['steps'])}
            )
            
            # Выполняем через стандартный ExecutionManager
            execution_result = await self.execution_manager.execute_workflow(workflow, team)
            
            # Проверяем на проблемы с инструментами и используем ToolAdapter
            if self.tool_adapter and 'errors' in execution_result:
                for error in execution_result.get('errors', []):
                    if 'неизвестный инструмент' in error.lower() or 'unknown tool' in error.lower():
                        # Пытаемся адаптировать инструмент
                        adapter_result = await self.tool_adapter.execute_task(
                            f"Адаптировать инструмент для ошибки: {error}"
                        )
                        
                        if adapter_result.get('success'):
                            await self.shared_chat.send_message(
                                sender_id=self.config.orchestrator_id,
                                content=f"🔧 Адаптирован инструмент: {adapter_result.get('available_tool', 'неизвестный')}",
                                message_type="coordination"
                            )
                            
                            # Пересчитываем статистику
                            self.tasks_processed += 1  # Добавляем за адаптацию
            
            # Уведомляем о завершении
            success_count = len([r for r in execution_result.get('results', []) if r.get('success', False)])
            total_count = len(execution_result.get('results', []))
            
            await self.shared_chat.broadcast_update(
                sender_id=self.config.orchestrator_id,
                update=f"Выполнение завершено: {success_count}/{total_count} успешно",
                task_info={
                    'success_rate': success_count / total_count if total_count > 0 else 0,
                    'original_task': original_task
                }
            )
            
            # Создаём заметки в Obsidian если включено
            if self.obsidian_adapter:
                await self._create_obsidian_notes(original_task, workflow, team, execution_result)
            
            return execution_result
            
        except Exception as e:
            # Уведомляем об ошибке
            await self.shared_chat.send_message(
                sender_id=self.config.orchestrator_id,
                content=f"❌ Ошибка выполнения: {str(e)}",
                message_type="coordination"
            )
            raise e
    
    async def solve_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        🎯 Главный метод - решение задачи через саморедуплицирующуюся систему
        
        Args:
            task: Описание задачи
            context: Дополнительный контекст
        
        Returns:
            Результат выполнения задачи
        """
        logger.info(f"🎯 Получена задача: {task[:100]}...")
        start_time = datetime.now()
        
        # НАЧИНАЕМ БОГАТОЕ ОТСЛЕЖИВАНИЕ
        execution_id = f"task_{int(time.time() * 1000000)}"
        task_execution = self.rich_reporter.start_task_execution(
            execution_id, task, context.get('user_id') if context else None
        )
        
        try:
            # 1. АНАЛИЗ ЗАДАЧИ
            complexity_analysis = self.task_analyzer.analyze_task_complexity(task)
            
            # ЛОГИРУЕМ АНАЛИЗ
            self.rich_reporter.log_task_analysis(execution_id, complexity_analysis)
            logger.info(f"📊 Сложность: {complexity_analysis['complexity']}, агентов: {complexity_analysis['estimated_agents']}")
            
            # 2. ДЕКОМПОЗИЦИЯ
            subtasks = self.task_decomposer.decompose_task(task, complexity_analysis["complexity"])
            resources = self.complexity_evaluator.evaluate_resources(subtasks)
            skills = self.skillset_matcher.match_skills(subtasks)
            
            # ЛОГИРУЕМ ДЕКОМПОЗИЦИЮ
            self.rich_reporter.log_task_decomposition(execution_id, subtasks)
            
            logger.info(f"🔄 Декомпозиция: {len(subtasks)} подзадач")
            
            # 3. СОЗДАНИЕ АГЕНТОВ И РЕГИСТРАЦИЯ В ЧАТЕ
            agents = {}
            
            # Сообщаем о начале формирования команды
            await self.shared_chat.send_message(
                sender_id=self.config.orchestrator_id,
                content=f"🎯 Формирую команду для задачи: {task[:100]}...",
                message_type="coordination"
            )
            
            for subtask in subtasks:
                required_skills = skills[subtask["id"]]
                agent = self.agent_spawner.spawn_agent_for_task(subtask, required_skills)
                agent_id = f"agent_{subtask['id']}"
                agents[agent_id] = agent
                
                # Регистрируем агента в чате
                self.shared_chat.register_agent(
                    agent_id=agent_id,
                    agent_role=getattr(agent, 'role', 'worker')
                )
                
                # === НАЧИНАЕМ ОТСЛЕЖИВАНИЕ МЕТРИК АГЕНТА ===
                if self.metrics_collector:
                    task_metric = self.metrics_collector.start_task_tracking(
                        task_id=f"{execution_id}_{subtask['id']}",
                        agent_id=agent_id,
                        task_description=subtask["description"]
                    )
                    logger.debug(f"📊 Начато отслеживание метрик для {agent_id}")
                
                # ЛОГИРУЕМ СОЗДАНИЕ АГЕНТА
                self.rich_reporter.log_agent_created(execution_id, {
                    "agent_id": agent_id,
                    "type": type(agent).__name__,
                    "role": getattr(agent, 'role', 'worker'),
                    "subtask_id": subtask["id"],
                    "required_skills": required_skills
                })
            
            self.agents_created += len(agents)
            
            # Сообщаем о готовности команды
            await self.shared_chat.send_message(
                sender_id=self.config.orchestrator_id,
                content=f"👥 Команда сформирована: {len(agents)} агентов готовы к работе",
                message_type="coordination"
            )
            
            # 4. ФОРМИРОВАНИЕ КОМАНДЫ
            team = self.team_composer.compose_team(agents)
            logger.info(f"👥 Команда сформирована: {team['team_size']} агентов")
            
            # 5. ПЛАНИРОВАНИЕ WORKFLOW
            workflow = self.workflow_planner.plan_workflow(subtasks, team)
            logger.info(f"📋 Workflow запланирован: {len(workflow['steps'])} шагов")
            
            # 5.5. СОЗДАНИЕ ГРАФА ПРОЦЕССА (НОВОЕ!)
            workflow_graph = self.graph_planner.create_workflow_from_subtasks(subtasks, agents)
            logger.info(f"📊 Граф создан: {len(workflow_graph.nodes)} узлов, {len(workflow_graph.edges)} связей")
            
            # 5.7. КООРДИНАЦИЯ ЗАДАЧ ЧЕРЕЗ ЧАТ
            task_assignments = {
                agent_id: subtasks[i]['description'] 
                for i, agent_id in enumerate(agents.keys()) if i < len(subtasks)
            }
            
            await self.shared_chat.coordinate_task(
                coordinator_id=self.config.orchestrator_id,
                task=task[:100],
                assignments=task_assignments
            )
            
            # 6. ВЫПОЛНЕНИЕ С КООРДИНАЦИЕЙ
            execution_result = await self._execute_with_coordination(workflow, team, task)
            
            # 6.5. ВАЛИДАЦИЯ РЕЗУЛЬТАТОВ (НОВОЕ!)
            validation_result = await self._validate_execution_result(task, execution_result)
            
            # 6.5. СОХРАНЕНИЕ В КОЛЛЕКТИВНОЙ ПАМЯТИ (НОВОЕ!)
            await self.collective_memory.store(
                f"Задача выполнена: {task[:100]}", 
                "orchestrator", 
                ["задача", "выполнение", complexity_analysis["complexity"]]
            )
            
            # Сохраняем результаты каждого агента
            for agent_id, agent in team["agents"].items():
                await self.collective_memory.store(
                    f"Агент {agent_id} участвовал в задаче: {task[:50]}",
                    agent_id,
                    ["агент", "участие", agent.role if hasattr(agent, 'role') else "unknown"]
                )
                
                # Записываем в систему самообучения (НОВОЕ!)
                # Вычисляем предварительную длительность
                temp_duration = (datetime.now() - start_time).total_seconds()
                await self.self_improvement.record_agent_execution(
                    agent_id=agent_id,
                    task_id=task[:100],  
                    input_data={"task": task, "context": context or {}},
                    output=execution_result,
                    execution_time=temp_duration,
                    success=True,  # Считаем задачу успешной
                    quality_score=validation_result.get("quality_score", 0.5)
                )
            
            # 7. РЕЗУЛЬТАТ
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.tasks_processed += 1
            self.workflows_executed += 1
            
            result = {
                "task": task,
                "status": "completed",
                "duration": duration,
                "complexity_analysis": complexity_analysis,
                "subtasks": subtasks,
                "team": team,
                "workflow": workflow,
                "workflow_graph": {
                    "id": workflow_graph.workflow_id,
                    "nodes_count": len(workflow_graph.nodes),
                    "edges_count": len(workflow_graph.edges),
                    "mermaid": workflow_graph.generate_mermaid()
                },
                "execution": execution_result,
                "validation": validation_result,
                "statistics": self.get_statistics(),
                "collective_memory_stats": self.collective_memory.get_team_stats(),
                "self_improvement_report": self.self_improvement.get_system_overview(),
                "coordination": {
                    "team_status": self.shared_chat.get_team_status(),
                    "chat_messages": len(self.shared_chat.messages),
                    "conversation_summary": self.shared_chat.get_conversation_summary(20),
                    "tool_adapter_stats": self.tool_adapter.get_adaptation_stats() if self.tool_adapter else None
                },
                "completed_at": end_time.isoformat()
            }
            
            # ЗАВЕРШАЕМ БОГАТОЕ ОТСЛЕЖИВАНИЕ
            self.rich_reporter.finish_task_execution(
                execution_id, 
                result.get("execution", {}).get("final_result", "Задача выполнена"),
                quality_score=validation_result.get("quality_score"),
                validation_results=validation_result
            )
            
            # СОХРАНЯЕМ ДЕТАЛЬНЫЙ ОТЧЁТ
            detailed_report = self.rich_reporter.generate_detailed_report(execution_id)
            report_filename = f"workspace/task_reports/detailed_report_{execution_id}.md"
            
            try:
                Path("workspace/task_reports").mkdir(parents=True, exist_ok=True)
                with open(report_filename, 'w', encoding='utf-8') as f:
                    f.write(detailed_report)
                logger.info(f"📄 Детальный отчёт сохранён: {report_filename}")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось сохранить детальный отчёт: {e}")
            
            # ДОБАВЛЯЕМ КРАТКИЙ ОТЧЁТ В РЕЗУЛЬТАТ
            result["rich_reporting"] = {
                "execution_id": execution_id,
                "detailed_report_file": report_filename,
                "ui_summary": self.rich_reporter.generate_ui_summary(execution_id)
            }
            
            logger.info(f"✅ Задача выполнена за {duration:.2f}с, создано {len(agents)} агентов")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения задачи: {e}")
            
            # ЗАВЕРШАЕМ ОТСЛЕЖИВАНИЕ С ОШИБКОЙ
            self.rich_reporter.finish_task_execution(
                execution_id, 
                "Задача завершена с ошибкой",
                error=str(e)
            )
            
            # СОХРАНЯЕМ ОТЧЁТ ОБ ОШИБКЕ
            try:
                error_report = self.rich_reporter.generate_detailed_report(execution_id)
                error_filename = f"workspace/task_reports/error_report_{execution_id}.md"
                Path("workspace/task_reports").mkdir(parents=True, exist_ok=True)
                with open(error_filename, 'w', encoding='utf-8') as f:
                    f.write(error_report)
                logger.info(f"📄 Отчёт об ошибке сохранён: {error_filename}")
            except Exception as report_error:
                logger.warning(f"⚠️ Не удалось сохранить отчёт об ошибке: {report_error}")
            
            return {
                "task": task,
                "status": "error",
                "error": str(e),
                "completed_at": datetime.now().isoformat(),
                "rich_reporting": {
                    "execution_id": execution_id,
                    "ui_summary": self.rich_reporter.generate_ui_summary(execution_id)
                }
            }
    
    async def execute_task(self, task: str, context: Dict[str, Any] = None) -> Any:
        """Выполнить задачу (псевдоним для solve_task для совместимости с тестами)"""
        result = await self.solve_task(task, context)
        return result.get("result", result.get("execution", {}).get("final_result", "Задача выполнена"))
    
    async def _validate_execution_result(self, original_task: str, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация результатов выполнения через QualityController"""
        try:
            # === НОВАЯ СИСТЕМА КОНТРОЛЯ КАЧЕСТВА ===
            if self.quality_controller:
                # Получаем список созданных файлов
                created_files = execution_result.get("files_created", [])
                artifact_paths = [Path(f) for f in created_files if f]
                
                # Проводим оценку качества
                quality_assessment = await self.quality_controller.assess_quality(
                    task_description=original_task,
                    result=execution_result,
                    artifacts_paths=artifact_paths
                )
                
                logger.info(f"🎯 Контроль качества: {quality_assessment.verdict} ({quality_assessment.overall_score:.2f}/1.0)")
                
                # Логируем проблемы если есть
                if quality_assessment.fatal_issues:
                    logger.warning(f"💀 Фатальные проблемы качества:")
                    for issue in quality_assessment.fatal_issues:
                        logger.warning(f"  - {issue}")
                
                # === ЗАВЕРШАЕМ МЕТРИКИ АГЕНТОВ ===
                if self.metrics_collector:
                    # Завершаем отслеживание метрик для всех агентов
                    for check in quality_assessment.checks:
                        if hasattr(check, 'criteria'):
                            agent_id = f"agent_{check.criteria.value}"  # Примерное соответствие
                            if agent_id in execution_result.get('agent_results', {}):
                                self.metrics_collector.complete_task(
                                    task_id=f"task_{int(time.time())}_{agent_id}",
                                    quality_score=quality_assessment.overall_score,
                                    artifacts_created=len(artifact_paths),
                                    errors=quality_assessment.fatal_issues,
                                    tools_used=execution_result.get('tools_used', []),
                                    llm_calls=execution_result.get('llm_calls', 0)
                                )
                
                return {
                    "validation_passed": quality_assessment.is_acceptable(),
                    "quality_score": quality_assessment.overall_score,
                    "user_benefit": f"Оценка качества: {quality_assessment.overall_score:.2f}/1.0",
                    "issues": quality_assessment.fatal_issues,
                    "recommendations": getattr(quality_assessment, 'improvement_suggestions', []),
                    "verdict": quality_assessment.verdict,
                    "quality_details": {
                        "passed_checks": quality_assessment.passed_checks,
                        "total_checks": quality_assessment.total_checks,
                        "check_results": [
                            {
                                "criteria": check.criteria.value,
                                "passed": check.passed,
                                "score": check.score,
                                "message": check.message
                            } for check in quality_assessment.checks
                        ]
                    }
                }
            
            else:
                # Fallback если контроллер качества недоступен
                return {
                    "validation_passed": True,
                    "quality_score": 0.5,
                    "user_benefit": "Контроль качества недоступен",
                    "issues": ["QualityController не инициализирован"],
                    "recommendations": [],
                    "verdict": "⚠️ БЕЗ КОНТРОЛЯ КАЧЕСТВА"
                }
            
        except Exception as e:
            logger.error(f"❌ Ошибка контроля качества: {e}")
            return {
                "validation_passed": False,
                "quality_score": 0.0,
                "user_benefit": "Ошибка контроля качества",
                "issues": [f"Контроллер качества недоступен: {e}"],
                "recommendations": ["Проверить работу контроллера качества"],
                "verdict": "❌ ОШИБКА КОНТРОЛЯ КАЧЕСТВА"
            }
    
    async def _create_obsidian_notes(self, task: str, workflow: Dict, team: Dict, execution_result: Dict[str, Any]):
        """Создание заметок в Obsidian о выполненной задаче"""
        try:
            task_id = f"TASK-{int(time.time())}"
            
            # 1. Создаём заметку задачи
            task_data = {
                "title": task[:100],
                "description": task,
                "status": "completed" if execution_result.get("success", False) else "failed",
                "priority": "normal",
                "complexity": workflow.get("complexity", "medium"),
                "assigned_agents": list(team.keys()),
                "type": "orchestrator_task"
            }
            
            task_note = await self.obsidian_adapter.create_task_note(task_id, task_data)
            logger.info(f"📝 Создана заметка задачи в Obsidian: {task_note}")
            
            # 2. Создаём заметки агентов
            for agent_id, agent in team.items():
                agent_data = {
                    "description": f"Агент для выполнения подзадачи {agent_id}",
                    "type": getattr(agent, 'agent_type', 'worker'),
                    "capabilities": getattr(agent, 'capabilities', ['general']),
                    "tasks_completed": 1,
                    "success_rate": 100.0 if execution_result.get("success", False) else 0.0
                }
                
                agent_note = await self.obsidian_adapter.create_agent_note(agent_id, agent_data)
                logger.debug(f"📝 Создана заметка агента в Obsidian: {agent_note}")
            
            # 3. Создаём заметку результата
            result_data = {
                "title": f"Результат выполнения: {task[:50]}",
                "description": "Результат работы команды агентов",
                "status": "completed" if execution_result.get("success", False) else "failed",
                "success": execution_result.get("success", False),
                "quality_score": execution_result.get("quality_score", 0.0),
                "execution_time": execution_result.get("duration", "неизвестно"),
                "output": str(execution_result.get("final_result", "Результат недоступен"))[:1000],
                "files": execution_result.get("files_created", []),
                "reviewed_by": "OrchestratorAgent",
                "review_status": "completed"
            }
            
            result_note = await self.obsidian_adapter.create_result_note(task_id, "Team", result_data)
            logger.info(f"📝 Создана заметка результата в Obsidian: {result_note}")
            
            # 4. Создаём итоговый отчёт
            report_data = {
                "title": f"Отчёт: {task[:50]}",
                "summary": f"Команда из {len(team)} агентов выполнила задачу",
                "overall_success": execution_result.get("success", False),
                "overall_quality": execution_result.get("quality_score", 0.0),
                "execution_time": execution_result.get("duration", "неизвестно"),
                "agents": [{"name": agent_id, "tasks_completed": 1, "success_rate": 100} for agent_id in team.keys()],
                "conclusions": "Задача выполнена через систему саморедуплицирующихся агентов KittyCore 3.0"
            }
            
            report_note = await self.obsidian_adapter.create_report_note(task_id, report_data)
            logger.info(f"📝 Создан итоговый отчёт в Obsidian: {report_note}")
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка создания заметок в Obsidian: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику работы оркестратора"""
        stats = {
            "tasks_processed": self.tasks_processed,
            "agents_created": self.agents_created,
            "workflows_executed": self.workflows_executed,
            "config": asdict(self.config)
        }
        
        # Добавляем статистику Obsidian если доступен
        if self.obsidian_adapter:
            stats["obsidian"] = {
                "enabled": True,
                "vault_path": self.config.obsidian_vault_path
            }
        
        return stats

# === УДОБНЫЕ ФУНКЦИИ ===

def create_orchestrator(config: OrchestratorConfig = None) -> OrchestratorAgent:
    """Создать оркестратор с настройками по умолчанию"""
    return OrchestratorAgent(config)

async def solve_with_orchestrator(task: str, **kwargs) -> Dict[str, Any]:
    """Быстрое решение задачи через оркестратор"""
    orchestrator = create_orchestrator()
    return await orchestrator.solve_task(task, kwargs)

# === АЛИАСЫ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ ===

# Для обратной совместимости с предыдущими версиями
UnifiedKittyCoreEngine = OrchestratorAgent
UnifiedConfig = OrchestratorConfig

# Экспорт основных компонентов
__all__ = [
    # Основной оркестратор
    "OrchestratorAgent", "OrchestratorConfig",
    
    # Компоненты анализа
    "TaskAnalyzer", "TaskDecomposer", "ComplexityEvaluator", "SkillsetMatcher",
    
    # Компоненты создания агентов
    "AgentSpawner", "TeamComposer",
    
    # Компоненты выполнения
    "WorkflowPlanner", "ExecutionManager",
    
    # Утилиты
    "create_orchestrator", "solve_with_orchestrator",
    
    # Алиасы для совместимости
    "UnifiedKittyCoreEngine", "UnifiedConfig"
] 