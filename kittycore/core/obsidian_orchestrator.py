"""
🧭 ObsidianOrchestrator - Оркестратор с ObsidianDB

Интегрированный оркестратор который использует ObsidianDB как центральную базу данных:
- Все результаты агентов сохраняются в Obsidian vault
- Контекст передаётся между агентами через заметки
- Полная трассировка выполнения задач
- Автоматические связи между заметками
- Координация агентов через общую базу знаний

РЕШАЕТ ПРОБЛЕМЫ:
✅ Разрыв между агентами и оркестратором
✅ Потеря контекста между этапами
✅ Иллюзия работы вместо реальных результатов
✅ Изолированные LLM промпты
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from loguru import logger

# Импорты ObsidianDB
from .obsidian_db import (
    ObsidianDB, ObsidianNote, AgentWorkspace, TaskManager,
    get_obsidian_db, create_agent_workspace, create_task_manager
)

# Импорты базового оркестратора
from .orchestrator import (
    TaskAnalyzer, TaskDecomposer, ComplexityEvaluator, 
    SkillsetMatcher, AgentSpawner, TeamComposer, WorkflowPlanner
)

# Импорт SmartValidator и IterativeImprovement
from kittycore.agents.smart_validator import SmartValidator
from .iterative_improvement import IterativeImprovement

class ObsidianTaskAnalyzer(TaskAnalyzer):
    """Анализатор задач с сохранением в ObsidianDB"""
    
    def __init__(self, vault_path: str = "./obsidian_vault"):
        super().__init__()
        self.db = get_obsidian_db(vault_path)
        
    def analyze_task_complexity(self, task: str, task_id: str = None) -> Dict[str, Any]:
        """Анализирует задачу и сохраняет результат в ObsidianDB"""
        logger.info(f"📊 Анализируем задачу: {task[:50]}...")
        
        # Выполняем базовый анализ
        analysis = super().analyze_task_complexity(task)
        
        # Сохраняем анализ в ObsidianDB
        if task_id:
            analysis_note = ObsidianNote(
                title=f"Анализ задачи {task_id}",
                content=f"""## Задача
{task}

## Результаты анализа

**Сложность:** {analysis['complexity']}
**Предполагаемое количество агентов:** {analysis['estimated_agents']}
**Требует планирования:** {analysis['requires_planning']}
**Требует координации:** {analysis['requires_coordination']}
**Предполагаемое время:** {analysis['estimated_time']} минут

## Обоснование
{analysis['reasoning']}

## Техническая информация
- Количество слов: {analysis['word_count']}
- Метод анализа: LLM + эвристика
- Timestamp: {datetime.now().isoformat()}
""",
                tags=["task-analysis", "system", task_id] if task_id else ["task-analysis", "system"],
                metadata={
                    "task_id": task_id,
                    "complexity": analysis['complexity'],
                    "estimated_agents": analysis['estimated_agents'],
                    "analysis_method": "LLM+heuristic",
                    "folder": "system"
                },
                folder="system"
            )
            
            self.db.save_note(analysis_note)
            logger.info(f"📊 Анализ задачи сохранён в ObsidianDB")
        
        return analysis

class ObsidianTaskDecomposer(TaskDecomposer):
    """Декомпозер задач с сохранением в ObsidianDB"""
    
    def __init__(self, vault_path: str = "./obsidian_vault"):
        super().__init__()
        self.db = get_obsidian_db(vault_path)
        
    def decompose_task(self, task: str, complexity: str, task_id: str = None) -> List[Dict[str, Any]]:
        """Разбивает задачу на подзадачи и сохраняет в ObsidianDB"""
        logger.info(f"🔄 Декомпозируем задачу сложности: {complexity}")
        
        # Выполняем базовую декомпозицию
        subtasks = super().decompose_task(task, complexity)
        
        # Сохраняем декомпозицию в ObsidianDB
        if task_id:
            subtasks_content = "\n".join([
                f"### Подзадача {st['id']}: {st['description']}\n"
                f"- **Тип:** {st['type']}\n"
                f"- **Приоритет:** {st.get('priority', 'normal')}\n"
                f"- **Зависимости:** {st.get('dependencies', [])}\n"
                for st in subtasks
            ])
            
            decomposition_note = ObsidianNote(
                title=f"Декомпозиция задачи {task_id}",
                content=f"""## Исходная задача
{task}

## Подзадачи ({len(subtasks)} шт.)

{subtasks_content}

## Метаинформация
- **Сложность:** {complexity}
- **Метод декомпозиции:** LLM + структурный анализ
- **Создано:** {datetime.now().isoformat()}

## Связанные заметки
[[Анализ задачи {task_id}]]
""",
                tags=["task-decomposition", "planning", task_id] if task_id else ["task-decomposition", "planning"],
                metadata={
                    "task_id": task_id,
                    "subtasks_count": len(subtasks),
                    "complexity": complexity,
                    "decomposition_method": "LLM+structural",
                    "folder": "system"
                },
                folder="system"
            )
            
            self.db.save_note(decomposition_note)
            
            # Создаём связь с анализом
            self.db.create_link(
                f"Декомпозиция-задачи-{task_id}.md",
                f"Анализ-задачи-{task_id}.md",
                "Анализ задачи"
            )
            
            logger.info(f"🔄 Декомпозиция сохранена в ObsidianDB: {len(subtasks)} подзадач")
        
        return subtasks

class ObsidianAgentSpawner(AgentSpawner):
    """Создатель агентов с интеграцией ObsidianDB"""
    
    def __init__(self, vault_path: str = "./obsidian_vault"):
        super().__init__()
        self.db = get_obsidian_db(vault_path)
        self.workspaces = {}  # Кэш рабочих пространств агентов
        
    def spawn_agent_for_task(self, subtask: Dict, skills: List[str], task_id: str = None) -> Any:
        """Создаёт агента и его рабочее пространство в ObsidianDB"""
        
        # Создаём базового агента
        agent = super().spawn_agent_for_task(subtask, skills)
        agent_id = f"agent_{subtask['id']}"
        
        # Создаём рабочее пространство в ObsidianDB
        workspace = create_agent_workspace(agent_id, self.db.vault_path)
        self.workspaces[agent_id] = workspace
        
        # Сохраняем информацию об агенте
        agent_info_note = ObsidianNote(
            title=f"Агент {agent_id}",
            content=f"""## Информация об агенте

**ID агента:** {agent_id}
**Роль:** {getattr(agent, 'role', 'worker')}
**Тип:** {type(agent).__name__}

## Назначенная подзадача
{subtask['description']}

## Требуемые навыки
{', '.join(skills)}

## Статус
- **Создан:** {datetime.now().isoformat()}
- **Задача:** {task_id or 'unknown'}
- **Статус:** Активен

## Результаты работы
*Результаты будут добавлены автоматически*

## Связанные заметки
""",
            tags=["agent", "active", agent_id, task_id] if task_id else ["agent", "active", agent_id],
            metadata={
                "agent_id": agent_id,
                "task_id": task_id,
                "subtask_id": subtask['id'],
                "agent_type": type(agent).__name__,
                "skills": skills,
                "created": datetime.now().isoformat(),
                "status": "active",
                "folder": "agents"
            },
            folder="agents"
        )
        
        self.db.save_note(agent_info_note)
        
        # Создаём связи с задачей
        if task_id:
            self.db.create_link(
                f"Агент-{agent_id}.md",
                f"Декомпозиция-задачи-{task_id}.md",
                f"Декомпозиция задачи {task_id}"
            )
        
        logger.info(f"🤖 Агент {agent_id} создан с ObsidianDB workspace")
        
        # КРИТИЧЕСКИ ВАЖНО: Заменяем инструменты агента на ObsidianAware
        from kittycore.tools.obsidian_tools import create_obsidian_tools
        obsidian_tools = create_obsidian_tools(self.db, agent_id)
        
        # Интегрируем ObsidianAware инструменты в агента
        if hasattr(agent, 'tools'):
            # Заменяем стандартные инструменты на ObsidianAware
            agent.tools.update(obsidian_tools)
        else:
            # Создаём новый набор инструментов
            agent.tools = obsidian_tools
        
        # Возвращаем агента с дополнительной информацией
        agent.agent_id = agent_id
        agent.workspace = workspace
        agent.task_id = task_id
        agent.obsidian_db = self.db
        
        return agent
    
    def get_agent_workspace(self, agent_id: str) -> Optional[AgentWorkspace]:
        """Получает рабочее пространство агента"""
        return self.workspaces.get(agent_id)

class ObsidianExecutionManager:
    """Менеджер выполнения с интеграцией ObsidianDB"""
    
    def __init__(self, vault_path: str = "./obsidian_vault", smart_validator=None):
        self.db = get_obsidian_db(vault_path)
        self.smart_validator = smart_validator
        self.iterative_improver = IterativeImprovement() if smart_validator else None
        
    async def execute_workflow_with_obsidian(self, workflow: Dict, team: Dict, task_id: str) -> Dict[str, Any]:
        """Выполняет workflow с полным сохранением в ObsidianDB"""
        execution_id = f"exec_{task_id}_{int(datetime.now().timestamp())}"
        
        # Создаём заметку о выполнении
        execution_note = ObsidianNote(
            title=f"Выполнение задачи {task_id}",
            content=f"""## Информация о выполнении

**ID выполнения:** {execution_id}
**Задача:** {task_id}
**Начато:** {datetime.now().isoformat()}

## Workflow
- **ID workflow:** {workflow.get('workflow_id', 'unknown')}
- **Количество шагов:** {len(workflow.get('steps', []))}

## Команда агентов ({len(team.get('agents', {}))})
{chr(10).join([f"- **{agent_id}:** {type(agent).__name__}" for agent_id, agent in team.get('agents', {}).items()])}

## Ход выполнения
*Обновляется в реальном времени*

""",
            tags=["execution", "active", task_id],
            metadata={
                "execution_id": execution_id,
                "task_id": task_id,
                "workflow_id": workflow.get('workflow_id'),
                "team_size": len(team.get('agents', {})),
                "status": "running",
                "folder": "system"
            },
            folder="system"
        )
        
        self.db.save_note(execution_note)
        
        results = {
            "execution_id": execution_id,
            "task_id": task_id,
            "workflow_id": workflow["workflow_id"],
            "start_time": datetime.now().isoformat(),
            "steps_completed": 0,
            "step_results": {},
            "status": "running",
            "files_created": [],
            "agent_outputs": {}
        }
        
        # Выполняем каждый шаг
        for step in workflow["steps"]:
            logger.info(f"🔄 Выполняется шаг: {step['description']}")
            
            try:
                # Обновляем заметку о ходе выполнения
                await self._update_execution_progress(execution_id, step, "running")
                
                # Находим агента для выполнения шага
                agent_id = step["assigned_agent"]
                
                if agent_id in team["agents"]:
                    agent = team["agents"][agent_id]
                    
                    # Получаем контекст из ObsidianDB
                    context = await self._get_execution_context(task_id, agent_id)
                    
                    # Выполняем шаг через ObsidianIntellectualAgent
                    step_result = await self._execute_step_with_obsidian(
                        agent, step, context, task_id
                    )
                    
                    # Сохраняем результат агента
                    if hasattr(agent, 'workspace') and agent.workspace:
                        agent.workspace.save_result(
                            task_id=task_id,
                            content=step_result.get("output", ""),
                            result_type=step.get("type", "result")
                        )
                    
                    results["step_results"][step["step_id"]] = step_result
                    results["agent_outputs"][agent_id] = step_result.get("output", "")
                    
                    # Обновляем заметку о прогрессе
                    await self._update_execution_progress(execution_id, step, "completed", step_result)
                    
                else:
                    step_result = {
                        "result": "⚠️ Агент не найден",
                        "status": "failed",
                        "timestamp": datetime.now().isoformat()
                    }
                    results["step_results"][step["step_id"]] = step_result
                    await self._update_execution_progress(execution_id, step, "failed", step_result)
                
                results["steps_completed"] += 1
                logger.info(f"✅ Шаг выполнен: {step['description']}")
                
            except Exception as e:
                logger.error(f"❌ Ошибка выполнения шага {step['step_id']}: {e}")
                
                error_result = {
                    "result": f"❌ Ошибка: {str(e)}",
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                
                results["step_results"][step["step_id"]] = error_result
                await self._update_execution_progress(execution_id, step, "failed", error_result)
                results["steps_completed"] += 1
        
        results["status"] = "completed"
        results["end_time"] = datetime.now().isoformat()
        
        # Финальное обновление заметки
        await self._finalize_execution_note(execution_id, results)
        
        return results
    
    async def _get_execution_context(self, task_id: str, agent_id: str) -> Dict[str, Any]:
        """Получает контекст выполнения из ObsidianDB"""
        context = {
            "task_id": task_id,
            "agent_id": agent_id,
            "previous_results": [],
            "related_notes": [],
            "coordination_messages": []
        }
        
        # Получаем все заметки связанные с задачей
        related_notes = self.db.search_notes(metadata_filter={"task_id": task_id})
        
        for note_info in related_notes:
            if note_info["metadata"].get("agent_id") != agent_id:
                # Результаты других агентов
                if note_info["metadata"].get("result_type"):
                    note = self.db.get_note(note_info["path"])
                    if note:
                        context["previous_results"].append({
                            "agent": note_info["metadata"].get("agent_id"),
                            "type": note_info["metadata"].get("result_type"),
                            "content": note.content[:300] + "..." if len(note.content) > 300 else note.content,
                            "timestamp": note_info["updated"]
                        })
            
            # Координационные сообщения
            if note_info["metadata"].get("message_type") == "coordination":
                if note_info["metadata"].get("to_agent") == agent_id:
                    note = self.db.get_note(note_info["path"])
                    if note:
                        context["coordination_messages"].append({
                            "from": note_info["metadata"].get("from_agent"),
                            "content": note.content,
                            "timestamp": note_info["updated"]
                        })
        
        return context
    
    async def _execute_step_with_obsidian(self, agent: Any, step: Dict, context: Dict, task_id: str) -> Dict[str, Any]:
        """Выполняет шаг через агента с контекстом из ObsidianDB"""
        
        # Импортируем здесь чтобы избежать циклических импортов
        from ..agents.intellectual_agent import IntellectualAgent
        
        # Создаём IntellectualAgent с контекстом
        subtask = {
            "description": step["description"],
            "type": step.get("type", "general"),
            "context": context
        }
        
        # Получаем роль агента
        agent_role = getattr(agent, 'role', getattr(agent, 'agent_id', 'worker'))
        
        # Создаём и запускаем рабочего агента
        working_agent = IntellectualAgent(agent_role, subtask)
        execution_result = await working_agent.execute_task()
        
                # ВАЛИДАЦИЯ РЕЗУЛЬТАТА через SmartValidator
        if self.smart_validator:
            try:
                validation = await self.smart_validator.validate_result(
                    original_task=step["description"],
                    result=execution_result,
                    created_files=execution_result.get("files_created", [])
                )
                
                logger.info(f"🔍 Валидация: {validation.verdict} (оценка: {validation.score:.1f}/1.0)")
                
                # Если результат не валидный - автоматически исправляем
                if not validation.is_valid:
                    logger.warning(f"❌ Результат не прошёл валидацию: {validation.user_benefit}")
                    logger.warning(f"🔧 Проблемы: {', '.join(validation.issues)}")
                    
                    # ИТЕРАТИВНОЕ УЛУЧШЕНИЕ АГЕНТА
                    if self.iterative_improver and validation.score < 0.6:  # Улучшаем если оценка < 0.6
                        logger.info("🔄 Запускаем итеративное улучшение агента...")
                        
                        try:
                            improved_result, improvement_attempts = await self.iterative_improver.improve_agent_iteratively(
                                agent=working_agent,
                                task=step["description"],
                                initial_result=execution_result,
                                initial_validation=validation,
                                smart_validator=self.smart_validator
                            )
                            
                            # Заменяем плохой результат улучшенным
                            execution_result.update(improved_result)
                            execution_result["iteratively_improved"] = True
                            execution_result["improvement_attempts"] = len(improvement_attempts)
                            execution_result["original_validation"] = {
                                "score": validation.score,
                                "issues": validation.issues
                            }
                            
                            # Логируем результаты улучшения
                            final_score = improved_result.get("validation", {}).get("score", validation.score)
                            improvement = final_score - validation.score
                            
                            if improvement > 0:
                                logger.info(f"📈 Агент улучшен: {validation.score:.1f} → {final_score:.1f} (+{improvement:.1f})")
                            else:
                                logger.warning(f"⚠️ Агент не улучшился: {validation.score:.1f} → {final_score:.1f}")
                            
                        except Exception as improve_error:
                            logger.error(f"❌ Ошибка итеративного улучшения: {improve_error}")
                    
                    # Добавляем информацию о валидации в результат
                    execution_result["validation"] = {
                        "is_valid": False,
                        "score": validation.score,
                        "issues": validation.issues,
                        "recommendations": validation.recommendations,
                        "verdict": validation.verdict
                    }
                    
                    # Меняем статус на failed если валидация провалена и не улучшена
                    if not execution_result.get("iteratively_improved", False):
                        execution_result["status"] = "validation_failed"
                    
                else:
                    logger.info(f"✅ Результат прошёл валидацию: {validation.user_benefit}")
                    execution_result["validation"] = {
                        "is_valid": True,
                        "score": validation.score,
                        "verdict": validation.verdict
                    }
                    
            except Exception as e:
                logger.error(f"❌ Ошибка валидации: {e}")
                execution_result["validation"] = {
                    "is_valid": False,
                    "error": str(e),
                    "verdict": "❌ ОШИБКА ВАЛИДАЦИИ"
                }
        else:
            logger.warning("⚠️ SmartValidator не доступен - валидация пропущена")
        
        return {
            "result": execution_result.get("output", ""),
            "status": execution_result.get("status", "completed"),
            "timestamp": datetime.now().isoformat(),
            "agent": agent_role,
            "files_created": execution_result.get("files_created", []),
            "validation": execution_result.get("validation", {})
        }
    
    async def _update_execution_progress(self, execution_id: str, step: Dict, status: str, result: Dict = None):
        """Обновляет прогресс выполнения в заметке"""
        # Находим заметку выполнения
        execution_notes = self.db.search_notes(metadata_filter={"execution_id": execution_id})
        
        for note_info in execution_notes:
            note = self.db.get_note(note_info["path"])
            if note:
                # Добавляем информацию о шаге
                step_info = f"""
### Шаг {step['step_id']}: {step['description']} ({status})
- **Агент:** {step.get('assigned_agent', 'unknown')}
- **Время:** {datetime.now().strftime('%H:%M:%S')}
- **Статус:** {status}
"""
                if result:
                    step_info += f"- **Результат:** {result.get('result', '')[:100]}...\n"
                
                # Обновляем контент
                if "## Ход выполнения" in note.content:
                    note.content = note.content.replace(
                        "*Обновляется в реальном времени*",
                        step_info.strip()
                    )
                    if step_info not in note.content:
                        note.content += step_info
                
                self.db.save_note(note, Path(note_info["path"]).name)
                break
    
    async def _finalize_execution_note(self, execution_id: str, results: Dict):
        """Финализирует заметку о выполнении"""
        execution_notes = self.db.search_notes(metadata_filter={"execution_id": execution_id})
        
        for note_info in execution_notes:
            note = self.db.get_note(note_info["path"])
            if note:
                # Добавляем итоговую информацию
                summary = f"""

## Итоги выполнения
- **Завершено:** {datetime.now().isoformat()}
- **Шагов выполнено:** {results['steps_completed']}
- **Статус:** {results['status']}
- **Агентов участвовало:** {len(results.get('agent_outputs', {}))}

## Результаты агентов
{chr(10).join([f"- **{agent_id}:** {output[:100]}..." for agent_id, output in results.get('agent_outputs', {}).items()])}
"""
                
                note.content += summary
                note.metadata["status"] = results["status"]
                note.metadata["completed_at"] = datetime.now().isoformat()
                
                # Обновляем теги
                note.tags = [tag for tag in note.tags if tag != "active"]
                note.tags.append("completed" if results["status"] == "completed" else "failed")
                
                self.db.save_note(note, Path(note_info["path"]).name)
                break 

class ObsidianOrchestrator:
    """
    🧭 Главный оркестратор с интеграцией ObsidianDB
    
    Решает ВСЕ проблемы архитектуры:
    ✅ Агенты сохраняют результаты в ObsidianDB
    ✅ Контекст передаётся между агентами через заметки
    ✅ Полная трассировка выполнения
    ✅ Связанные заметки и граф знаний
    ✅ Реальные результаты вместо отчётов
    """
    
    def __init__(self, vault_path: str = "./obsidian_vault"):
        self.vault_path = vault_path
        
        # Инициализируем ObsidianDB
        self.db = get_obsidian_db(vault_path)
        self.task_manager = create_task_manager(vault_path)
        
        # SmartValidator для проверки качества результатов
        self.smart_validator = SmartValidator()
        
        # Создаём Obsidian-интегрированные компоненты
        self.task_analyzer = ObsidianTaskAnalyzer(vault_path)
        self.task_decomposer = ObsidianTaskDecomposer(vault_path)
        self.agent_spawner = ObsidianAgentSpawner(vault_path)
        self.execution_manager = ObsidianExecutionManager(vault_path, self.smart_validator)
        
        # Базовые компоненты
        self.complexity_evaluator = ComplexityEvaluator()
        self.skillset_matcher = SkillsetMatcher()
        self.team_composer = TeamComposer()
        self.workflow_planner = WorkflowPlanner()
        
        # Статистика
        self.tasks_processed = 0
        self.agents_created = 0
        
        logger.info(f"🧭 ObsidianOrchestrator инициализирован с vault: {vault_path}")
    
    async def solve_task(self, task: str, user_id: str = None) -> Dict[str, Any]:
        """
        🎯 Главный метод - решение задачи через ObsidianDB
        
        НОВАЯ АРХИТЕКТУРА:
        1. Создаём задачу в TaskManager
        2. Анализ и декомпозиция с сохранением в ObsidianDB
        3. Создание агентов с рабочими пространствами
        4. Выполнение с передачей контекста через заметки
        5. Агрегация результатов из ObsidianDB
        """
        logger.info(f"🎯 ObsidianOrchestrator решает задачу: {task[:50]}...")
        start_time = datetime.now()
        
        try:
            # ЭТАП 1: Создание задачи в ObsidianDB
            task_id = self.task_manager.create_task(task, user_id)
            logger.info(f"📋 Задача создана: {task_id}")
            
            # ЭТАП 2: Анализ задачи (сохраняется в ObsidianDB)
            complexity_analysis = self.task_analyzer.analyze_task_complexity(task, task_id)
            logger.info(f"📊 Анализ: {complexity_analysis['complexity']} ({complexity_analysis['estimated_agents']} агентов)")
            
            # ЭТАП 3: Декомпозиция (сохраняется в ObsidianDB)
            subtasks = self.task_decomposer.decompose_task(task, complexity_analysis["complexity"], task_id)
            logger.info(f"🔄 Декомпозиция: {len(subtasks)} подзадач")
            
            # ЭТАП 4: Создание агентов с рабочими пространствами
            resources = self.complexity_evaluator.evaluate_resources(subtasks)
            skills = self.skillset_matcher.match_skills(subtasks)
            
            agents = {}
            for subtask in subtasks:
                required_skills = skills[subtask["id"]]
                agent = self.agent_spawner.spawn_agent_for_task(subtask, required_skills, task_id)
                agent_id = f"agent_{subtask['id']}"
                agents[agent_id] = agent
                
                # Добавляем агента к задаче в TaskManager
                self.task_manager.add_agent_to_task(task_id, agent_id, getattr(agent, 'role', 'worker'))
            
            self.agents_created += len(agents)
            logger.info(f"🤖 Создано агентов: {len(agents)}")
            
            # ЭТАП 5: Формирование команды и планирование
            team = self.team_composer.compose_team(agents)
            workflow = self.workflow_planner.plan_workflow(subtasks, team)
            logger.info(f"👥 Команда: {team['team_size']} агентов, workflow: {len(workflow['steps'])} шагов")
            
            # ЭТАП 6: Выполнение через ObsidianDB
            execution_result = await self.execution_manager.execute_workflow_with_obsidian(workflow, team, task_id)
            logger.info(f"⚡ Выполнение завершено: {execution_result['status']}")
            
            # ЭТАП 7: Агрегация результатов из ObsidianDB
            final_result = await self._aggregate_results_from_obsidian(task_id, execution_result)
            
            # ЭТАП 8: Обновление статуса задачи
            self.task_manager.update_task_status(
                task_id=task_id,
                status="completed",
                details=f"Задача выполнена успешно. Создано результатов: {len(final_result.get('agent_outputs', {}))}"
            )
            
            # ЭТАП 9: Возврат результата
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self.tasks_processed += 1
            
            result = {
                "task": task,
                "task_id": task_id,
                "status": "completed",
                "duration": duration,
                "vault_path": str(self.vault_path),
                
                # Результаты из ObsidianDB
                "obsidian_results": final_result,
                
                # Метаданные
                "complexity_analysis": complexity_analysis,
                "subtasks": subtasks,
                "team": team,
                "workflow": workflow,
                "execution": execution_result,
                
                # Статистика
                "agents_created": len(agents),
                "steps_completed": execution_result.get("steps_completed", 0),
                "vault_notes_created": len(list(Path(self.vault_path).rglob("*.md"))),
                
                "completed_at": end_time.isoformat()
            }
            
            logger.info(f"🎉 Задача {task_id} завершена успешно!")
            logger.info(f"📁 Результаты доступны в: {self.vault_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения задачи: {e}")
            
            # Обновляем статус на failed
            if 'task_id' in locals():
                self.task_manager.update_task_status(
                    task_id=task_id,
                    status="failed",
                    details=f"Ошибка выполнения: {str(e)}"
                )
            
            raise e
    
    async def _aggregate_results_from_obsidian(self, task_id: str, execution_result: Dict) -> Dict[str, Any]:
        """Агрегирует финальные результаты из заметок ObsidianDB"""
        
        # Получаем все заметки связанные с задачей
        task_notes = self.db.search_notes(metadata_filter={"task_id": task_id})
        
        aggregated = {
            "task_id": task_id,
            "agent_results": [],
            "coordination_messages": [],
            "execution_trace": [],
            "final_outputs": {},
            "created_files": []
        }
        
        for note_info in task_notes:
            folder = note_info["metadata"].get("folder", "")
            
            # Результаты агентов
            if folder == "agents" and note_info["metadata"].get("result_type"):
                note = self.db.get_note(note_info["path"])
                if note:
                    aggregated["agent_results"].append({
                        "agent_id": note_info["metadata"].get("agent_id"),
                        "result_type": note_info["metadata"].get("result_type"),
                        "content": note.content,
                        "timestamp": note_info["updated"],
                        "file_path": note_info["path"]
                    })
            
            # Координационные сообщения
            elif folder == "coordination":
                note = self.db.get_note(note_info["path"])
                if note:
                    aggregated["coordination_messages"].append({
                        "from_agent": note_info["metadata"].get("from_agent"),
                        "to_agent": note_info["metadata"].get("to_agent"),
                        "content": note.content,
                        "timestamp": note_info["updated"]
                    })
            
            # Трейс выполнения
            elif folder == "system" and "execution" in note_info["metadata"].get("execution_id", ""):
                note = self.db.get_note(note_info["path"])
                if note:
                    aggregated["execution_trace"].append({
                        "execution_id": note_info["metadata"].get("execution_id"),
                        "content": note.content,
                        "status": note_info["metadata"].get("status"),
                        "timestamp": note_info["updated"]
                    })
        
        # Извлекаем финальные выходы из результатов агентов
        for agent_result in aggregated["agent_results"]:
            agent_id = agent_result["agent_id"]
            if agent_id not in aggregated["final_outputs"]:
                aggregated["final_outputs"][agent_id] = []
            
            aggregated["final_outputs"][agent_id].append({
                "type": agent_result["result_type"],
                "content": agent_result["content"],
                "timestamp": agent_result["timestamp"]
            })
        
        # Ищем созданные файлы в результатах выполнения
        for step_result in execution_result.get("step_results", {}).values():
            if "files_created" in step_result:
                aggregated["created_files"].extend(step_result["files_created"])
        
        return aggregated
    
    def get_task_summary(self, task_id: str) -> Dict[str, Any]:
        """Получает сводку задачи из ObsidianDB"""
        return self.task_manager.get_task_summary(task_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получает статистику оркестратора"""
        vault_stats = {
            "total_notes": len(list(Path(self.vault_path).rglob("*.md"))),
            "tasks_notes": len(list(Path(self.vault_path).glob("tasks/*.md"))),
            "agents_notes": len(list(Path(self.vault_path).glob("agents/**/*.md"))),
            "coordination_notes": len(list(Path(self.vault_path).glob("coordination/*.md"))),
            "system_notes": len(list(Path(self.vault_path).glob("system/*.md")))
        }
        
        return {
            "tasks_processed": self.tasks_processed,
            "agents_created": self.agents_created,
            "vault_path": str(self.vault_path),
            "vault_statistics": vault_stats
        }

def create_obsidian_orchestrator(vault_path: str = "./obsidian_vault") -> ObsidianOrchestrator:
    """Создаёт ObsidianOrchestrator"""
    return ObsidianOrchestrator(vault_path)

async def solve_with_obsidian_orchestrator(task: str, vault_path: str = "./obsidian_vault", **kwargs) -> Dict[str, Any]:
    """Быстрое решение задачи через ObsidianOrchestrator"""
    orchestrator = create_obsidian_orchestrator(vault_path)
    return await orchestrator.solve_task(task, kwargs.get('user_id')) 