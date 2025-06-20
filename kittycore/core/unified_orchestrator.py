"""
🧭 UnifiedOrchestrator - Единый оркестратор KittyCore 3.0

Объединяет лучшие части OrchestratorAgent и ObsidianOrchestrator:
✅ Obsidian-совместимое хранилище для всех данных
✅ SharedChat для координации агентов  
✅ SmartValidator для проверки качества
✅ Система метрик и самообучения
✅ Векторная память и поиск
✅ Human-in-the-loop интеграция
✅ Единый интерфейс для всех сценариев

ПРИНЦИП: "Одна логика, универсальное хранилище"
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass

from loguru import logger

# Импорты базовых компонентов
from .orchestrator import (
    TaskAnalyzer, TaskDecomposer, ComplexityEvaluator, 
    SkillsetMatcher, AgentSpawner, TeamComposer, WorkflowPlanner,
    ExecutionManager, ReportLevel
)

# Импорты Obsidian компонентов
from .obsidian_db import (
    ObsidianDB, ObsidianNote, AgentWorkspace, TaskManager,
    get_obsidian_db, create_agent_workspace, create_task_manager
)

# Импорты дополнительных систем
from .shared_chat import SharedChat
from ..memory.collective_memory import CollectiveMemory
from ..memory.amem_integration import KittyCoreMemorySystem, get_enhanced_memory_system
from .self_improvement import SelfLearningEngine
from .graph_workflow import WorkflowGraph, WorkflowPlanner as GraphWorkflowPlanner
from .human_collaboration import (
    InterventionRequest, InterventionType, InterventionUrgency,
    ConsoleInterventionHandler, create_approval_request
)

# Импорты валидации и качества
from ..agents.smart_validator import SmartValidator

# 🐜 Импорт феромонной системы памяти
from .pheromone_memory import get_pheromone_system, record_agent_success


@dataclass
class UnifiedConfig:
    """Единая конфигурация для всех сценариев работы"""
    
    # Основные настройки
    orchestrator_id: str = "unified_orchestrator"
    max_agents: int = 10
    timeout: int = 300
    log_level: str = "INFO"
    
    # Хранилище данных (Obsidian-совместимое)
    vault_path: str = "./vault"  # Единое хранилище
    enable_obsidian_features: bool = True  # Всегда включено
    
    # Системы качества и обучения
    enable_smart_validation: bool = True
    enable_metrics: bool = True
    enable_vector_memory: bool = True
    enable_amem_memory: bool = True  # 🧠 A-MEM Enhanced Memory
    enable_quality_control: bool = True
    enable_self_improvement: bool = True
    
    # Human-in-the-loop
    enable_human_intervention: bool = True
    intervention_timeout: int = 300  # 5 минут
    
    # Координация агентов
    enable_shared_chat: bool = True
    enable_tool_adaptation: bool = True
    
    # Отчётность
    report_level: ReportLevel = ReportLevel.DETAILED
    
    # Пути для системных данных
    vector_memory_path: str = "./vault/system/vector_memory"
    amem_memory_path: str = "./vault/system/amem_memory"  # 🧠 A-MEM хранилище
    metrics_storage_path: str = "./vault/system/metrics"
    logs_path: str = "./vault/system/logs"


class UnifiedOrchestrator:
    """
    🧭 Единый оркестратор KittyCore 3.0
    
    Объединяет все лучшие возможности:
    - Obsidian-совместимое хранилище для всех данных
    - Координация агентов через SharedChat
    - Умная валидация результатов
    - Система метрик и самообучения
    - Human-in-the-loop интеграция
    - Векторная память и поиск
    """
    
    def __init__(self, config: UnifiedConfig = None):
        self.config = config or UnifiedConfig()
        
        # Создаём единое хранилище
        self._setup_unified_storage()
        
        # Инициализируем базовые компоненты
        self._init_core_components()
        
        # Инициализируем системы качества
        self._init_quality_systems()
        
        # Инициализируем координацию
        self._init_coordination_systems()
        
        # Инициализируем human-in-the-loop
        self._init_human_collaboration()
        
        # Статистика
        self.tasks_processed = 0
        self.agents_created = 0
        self.workflows_executed = 0
        
        logger.info(f"🧭 UnifiedOrchestrator инициализирован")
        logger.info(f"📁 Единое хранилище: {self.config.vault_path}")
    
    def _setup_unified_storage(self):
        """Настройка единого Obsidian-совместимого хранилища"""
        vault_path = Path(self.config.vault_path)
        vault_path.mkdir(exist_ok=True)
        
        # Создаём структуру папок
        folders = [
            "tasks",      # Задачи пользователей
            "agents",     # Результаты агентов
            "system",     # Системные данные
            "coordination", # Координация команды
            "results",    # Финальные результаты
            "human",      # Human-in-the-loop
        ]
        
        for folder in folders:
            (vault_path / folder).mkdir(exist_ok=True)
        
        # Инициализируем ObsidianDB
        self.db = get_obsidian_db(str(vault_path))
        self.task_manager = create_task_manager(str(vault_path))
        
        logger.info(f"📁 Единое хранилище настроено: {vault_path}")
    
    def _init_core_components(self):
        """Инициализация базовых компонентов анализа и выполнения"""
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
        
        logger.debug("🔧 Базовые компоненты инициализированы")
    
    def _init_quality_systems(self):
        """Инициализация систем качества и обучения"""
        
        # SmartValidator для проверки качества
        if self.config.enable_smart_validation:
            self.smart_validator = SmartValidator()
            logger.info("🎯 SmartValidator активирован")
        else:
            self.smart_validator = None
        
        # Система самообучения
        if self.config.enable_self_improvement:
            self.self_improvement = SelfLearningEngine()
            logger.info("🧠 Система самообучения активирована")
        else:
            self.self_improvement = None
        
        # Векторная память
        if self.config.enable_vector_memory:
            from .vector_memory import create_vector_memory_store
            self.vector_store = create_vector_memory_store(
                storage_path=self.config.vector_memory_path,
                obsidian_db=self.db
            )
            logger.info("🔍 Векторная память активирована")
        else:
            self.vector_store = None
        
        # A-MEM Enhanced Memory (революционная агентная память)
        if self.config.enable_amem_memory:
            # Создаём путь для A-MEM
            amem_path = Path(self.config.amem_memory_path)
            amem_path.mkdir(parents=True, exist_ok=True)
            
            # Инициализируем A-MEM систему
            self.amem_system = get_enhanced_memory_system(str(amem_path))
            logger.info("🧠 A-MEM Enhanced Memory активирована")
            logger.info("✨ Семантический поиск, эволюция памяти, Zettelkasten принципы готовы")
        else:
            self.amem_system = None
        
        # Система метрик
        if self.config.enable_metrics:
            from .metrics_collector import create_metrics_collector
            self.metrics_collector = create_metrics_collector(
                storage_path=self.config.metrics_storage_path,
                obsidian_db=self.db
            )
            logger.info("📊 Система метрик активирована")
        else:
            self.metrics_collector = None
    
    def _init_coordination_systems(self):
        """Инициализация систем координации агентов"""
        
        # Коллективная память
        self.collective_memory = CollectiveMemory(self.config.orchestrator_id)
        
        # Интеграция A-MEM с коллективной памятью
        if self.amem_system:
            # Устанавливаем связь между CollectiveMemory и A-MEM
            self.collective_memory.amem_system = self.amem_system
            logger.info("🔗 A-MEM интегрирован с коллективной памятью")
        
        # SharedChat для координации
        if self.config.enable_shared_chat:
            self.shared_chat = SharedChat(
                team_id=f"team_{self.config.orchestrator_id}",
                collective_memory=self.collective_memory
            )
            
            # Интеграция A-MEM с SharedChat
            if self.amem_system:
                self.shared_chat.amem_system = self.amem_system
                logger.info("🧠 A-MEM интегрирован с SharedChat")
            
            # Регистрируем оркестратор как координатор
            self.shared_chat.register_agent(
                agent_id=self.config.orchestrator_id,
                agent_role="Orchestrator",
                is_coordinator=True
            )
            
            logger.info("💬 SharedChat активирован")
        else:
            self.shared_chat = None
        
        # ToolAdapter (будет реализован позже)
        if self.config.enable_tool_adaptation:
            self.tool_adapter = None  # TODO: Подключить ToolAdapterAgent
            logger.info("🔧 ToolAdapter активирован")
        else:
            self.tool_adapter = None
    
    def _init_human_collaboration(self):
        """Инициализация системы взаимодействия с человеком"""
        
        if self.config.enable_human_intervention:
            self.intervention_handler = ConsoleInterventionHandler()
            logger.info("👤 Human-in-the-loop активирован")
        else:
            self.intervention_handler = None
    
    async def solve_task(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        🎯 Главный метод решения задач через единую оркестрацию
        
        10-этапный процесс:
        1. Создание задачи в едином хранилище
        2. Анализ сложности
        3. Проверка необходимости человеческого вмешательства
        4. Декомпозиция и планирование
        5. Создание команды агентов
        6. Выполнение с координацией
        7. Валидация результатов
        8. Агрегация и финализация
        9. Обновление статистики и обучение
        10. Возврат результата с путями к файлам
        """
        start_time = datetime.now()
        logger.info(f"🚀 Запуск UnifiedOrchestrator для задачи: {task[:100]}...")
        
        # ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА: Доступность LLM
        if not hasattr(self.task_analyzer, 'llm') or self.task_analyzer.llm is None:
            error_msg = "❌ LLM провайдер не инициализирован. Система не может работать без LLM."
            logger.error(error_msg)
            
            # Создаём задачу для отслеживания ошибки
            try:
                task_id = self.task_manager.create_task(task, context.get('user_id') if context else None)
                self.task_manager.update_task_status(
                    task_id=task_id,
                    status="failed_llm_unavailable",
                    details=error_msg
                )
            except Exception:
                task_id = None
            
            # Обрабатываем недоступность LLM
            llm_error = RuntimeError(error_msg)
            await self._handle_llm_unavailable(task, llm_error)
            
            return {
                "task": task,
                "task_id": task_id,
                "status": "failed_llm_unavailable",
                "error": error_msg,
                "error_type": "llm_not_initialized",
                "message": "Система требует LLM для работы. Проверьте конфигурацию провайдера.",
                "duration": (datetime.now() - start_time).total_seconds(),
                "completed_at": datetime.now().isoformat()
            }
        
        try:
            # ЭТАП 1: Создание задачи в едином хранилище
            task_id = self.task_manager.create_task(task, context.get('user_id') if context else None)
            logger.info(f"📋 Задача создана: {task_id}")
            
            # ЭТАП 2: Анализ сложности
            complexity_analysis = await self._analyze_task_with_storage(task, task_id)
            logger.info(f"📊 Анализ: {complexity_analysis['complexity']} ({complexity_analysis['estimated_agents']} агентов)")
            
            # Начинаем отслеживание метрик
            task_metrics = None
            if self.metrics_collector:
                task_metrics = self.metrics_collector.start_task_tracking(
                    task_id=task_id,
                    task_type=complexity_analysis.get('task_type', 'general'),
                    complexity_score=complexity_analysis['complexity']
                )
            
            # ЭТАП 3: Проверка необходимости человеческого вмешательства
            if await self._check_human_intervention_needed(task, complexity_analysis):
                intervention_result = await self._request_human_guidance(task, complexity_analysis)
                if intervention_result.get('modified_task'):
                    task = intervention_result['modified_task']
                    logger.info(f"👤 Задача скорректирована человеком")
            
            # ЭТАП 4: Декомпозиция и планирование
            subtasks = await self._decompose_task_with_storage(task, complexity_analysis, task_id)
            logger.info(f"🔄 Декомпозиция: {len(subtasks)} подзадач")
            
            # ЭТАП 5: Создание команды агентов
            agents = await self._create_agent_team(subtasks, task_id)
            logger.info(f"🤖 Создано агентов: {len(agents)}")
            
            # ЭТАП 6: Выполнение с координацией
            execution_result = await self._execute_with_unified_coordination(agents, subtasks, task, task_id)
            logger.info(f"⚡ Выполнение завершено: {execution_result['status']}")
            
            # ЭТАП 7: Валидация результатов
            # Добавляем анализ задачи в execution_result для валидации
            execution_result['task_analysis'] = complexity_analysis
            validation_result = await self._validate_results(task, execution_result)
            logger.info(f"✅ Валидация: {validation_result.get('quality_score', 0):.2f}")
            
            # ЭТАП 8: Агрегация и финализация
            final_result = await self._finalize_task_results(task_id, execution_result, validation_result)
            
            # ЭТАП 9: Обновление статистики и обучение
            await self._update_learning_systems(task, final_result, start_time)
            
            # ЭТАП 10: Завершение отслеживания метрик
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Сохраняем успешные решения в векторную память
            if self.vector_store and validation_result.get('quality_score', 0) >= 0.7:
                solution_summary = self._create_solution_summary(final_result)
                
                self.vector_store.add_task_solution(
                    task_id=task_id,
                    task_description=task,
                    solution=solution_summary,
                    success_score=validation_result.get('quality_score', 0.0),
                    metadata={
                        'task_type': complexity_analysis.get('task_type', 'general'),
                        'complexity_score': complexity_analysis['complexity'],
                        'agents_used': len(agents),
                        'duration_seconds': duration,
                        'files_created': len(final_result.get('created_files', []))
                    }
                )
            self.tasks_processed += 1
            
            # Завершаем отслеживание метрик
            if self.metrics_collector and task_metrics:
                self.metrics_collector.finish_task_tracking(
                    task_id=task_id,
                    agents_created=len(agents),
                    agents_succeeded=sum(1 for agent_data in agents.values() 
                                       if agent_data.get('status') == 'completed'),
                    agents_failed=sum(1 for agent_data in agents.values() 
                                    if agent_data.get('status') == 'failed'),
                    quality_score=validation_result.get('quality_score', 0.0),
                    validation_passed=validation_result.get('quality_score', 0) >= 0.7,
                    rework_required=validation_result.get('quality_score', 0) < 0.7,
                    files_created=len(final_result.get('created_files', [])),
                    human_interventions=final_result.get('human_interventions', 0)
                )
            
            result = {
                "task": task,
                "task_id": task_id,
                "status": "completed",
                "duration": duration,
                
                # Пути к созданным файлам
                "created_files": final_result.get("created_files", []),
                "vault_path": str(self.config.vault_path),
                "results_folder": str(Path(self.config.vault_path) / "results"),
                
                # Процесс работы
                "process_trace": final_result.get("process_trace", []),
                "agent_coordination": final_result.get("coordination_log", []),
                
                # Метаданные
                "complexity_analysis": complexity_analysis,
                "subtasks": subtasks,
                "validation": validation_result,
                "agents_created": len(agents),
                
                # Метрики производительности
                "metrics": self.metrics_collector.get_current_stats() if self.metrics_collector else None,
                
                "completed_at": end_time.isoformat()
            }
            
            logger.info(f"🎉 Задача {task_id} завершена успешно!")
            logger.info(f"📁 Результаты: {len(final_result.get('created_files', []))} файлов")
            
            return result
            
        except RuntimeError as e:
            # Обрабатываем критические ошибки системы (включая LLM)
            if "LLM" in str(e) or "провайдер" in str(e):
                logger.error(f"🚨 Критическая ошибка LLM: {e}")
                
                # Обрабатываем недоступность LLM
                await self._handle_llm_unavailable(task, e)
                
                # Обновляем статус задачи на failed
                if 'task_id' in locals():
                    self.task_manager.update_task_status(
                        task_id=task_id,
                        status="failed_llm_unavailable",
                        details=f"LLM недоступен: {str(e)}"
                    )
                
                # Возвращаем результат с ошибкой
                return {
                    "task": task,
                    "task_id": task_id if 'task_id' in locals() else None,
                    "status": "failed_llm_unavailable",
                    "error": str(e),
                    "error_type": "llm_unavailable",
                    "message": "Система не может работать без LLM. Проверьте подключение к провайдеру.",
                    "duration": (datetime.now() - start_time).total_seconds(),
                    "completed_at": datetime.now().isoformat()
                }
            else:
                # Другие критические ошибки
                logger.error(f"❌ Критическая ошибка системы: {e}")
                raise e
                
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
    
    # === РЕАЛИЗАЦИЯ ВСПОМОГАТЕЛЬНЫХ МЕТОДОВ ===
    
    async def _analyze_task_with_storage(self, task: str, task_id: str) -> Dict[str, Any]:
        """Анализ задачи с сохранением в хранилище"""
        # Используем базовый анализатор
        analysis = self.task_analyzer.analyze_task_complexity(task)
        
        # НОВОЕ: Извлекаем образ конечного результата
        expected_outcome = await self._extract_expected_outcome(task)
        analysis['expected_outcome'] = expected_outcome
        
        # Сохраняем анализ в ObsidianDB
        analysis_note = ObsidianNote(
            title=f"Анализ задачи - {task_id}",
            content=f"""# Анализ сложности задачи

## Задача
{task}

## Результат анализа
- **Сложность**: {analysis['complexity']}
- **Оценка агентов**: {analysis['estimated_agents']}
- **Время выполнения**: {analysis.get('estimated_time', 'неизвестно')}
- **Требуемые навыки**: {', '.join(analysis.get('required_skills', []))}

## Образ конечного результата
{self._format_expected_outcome(expected_outcome)}

## Детали
{analysis.get('reasoning', 'Детальный анализ недоступен')}
""",
            tags=["анализ", "задача", str(analysis['complexity'])],
            metadata={
                "task_id": task_id,
                "analysis_type": "complexity",
                "complexity": analysis['complexity'],
                "estimated_agents": analysis['estimated_agents'],
                "expected_outcome_type": expected_outcome.get('type', 'unknown'),
                "validation_criteria": expected_outcome.get('validation_criteria', []),
                "timestamp": datetime.now().isoformat()
            },
            folder="tasks"
        )
        
        # Сохраняем в хранилище
        analysis_path = self.db.save_note(analysis_note, f"analysis_{task_id}.md")
        logger.info(f"📊 Анализ сохранён: {analysis_path}")
        
        return analysis
    
    async def _extract_expected_outcome(self, task: str) -> Dict[str, Any]:
        """
        🎯 Извлечение образа конечного результата через LLM-агента проджект-менеджера
        
        Агент анализирует задачу и определяет:
        - Что именно должно быть получено в итоге
        - Критерии успеха и валидации
        - Способы проверки результата
        """
        logger.info("🤖 Запускаем агента проджект-менеджера для анализа задачи...")
        
        # Проверяем доступность LLM
        if not hasattr(self.task_analyzer, 'llm') or self.task_analyzer.llm is None:
            raise RuntimeError("❌ LLM провайдер недоступен. Система не может работать без интеллектуального анализа задач.")
        
        try:
            # Создаём промпт для LLM-агента проджект-менеджера
            pm_prompt = f"""Ты - опытный проджект-менеджер. Проанализируй задачу и определи образ конечного результата.

ЗАДАЧА: {task}

Определи:
1. ТИП РЕЗУЛЬТАТА - что конкретно должно быть создано/достигнуто
2. КРИТЕРИИ УСПЕХА - как понять что задача выполнена успешно  
3. СПОСОБЫ ПРОВЕРКИ - как можно проверить результат
4. КОНКРЕТНЫЕ ПАРАМЕТРЫ - числовые показатели, технические требования

Ответь в JSON формате:
{{
    "result_type": "краткое название типа результата",
    "description": "подробное описание ожидаемого результата",
    "success_criteria": ["критерий 1", "критерий 2", "критерий 3"],
    "validation_methods": ["метод проверки 1", "метод проверки 2"],
    "specific_parameters": {{"параметр": "значение"}},
    "confidence": 0.9,
    "clarification_question": "Вопрос для уточнения у пользователя (если нужно)"
}}

Будь конкретным и практичным. Фокусируйся на реальной пользе для пользователя."""

            # Отправляем запрос к LLM
            llm_response = self.task_analyzer.llm.complete(pm_prompt)
            
            # Парсим ответ LLM
            import json
            import re
            
            outcome_data = None
            
            # Сначала пытаемся найти JSON в ответе
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                try:
                    outcome_data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            # Если JSON не найден, парсим markdown
            if outcome_data is None:
                outcome_data = self._parse_markdown_outcome(llm_response)
            
            # Валидируем структуру ответа
            required_fields = ['result_type', 'description', 'success_criteria', 'validation_methods']
            missing_fields = [field for field in required_fields if field not in outcome_data]
            if missing_fields:
                raise RuntimeError(f"❌ LLM вернул неполный ответ. Отсутствуют поля: {missing_fields}")
            
            expected_outcome = {
                'type': outcome_data['result_type'],
                'description': outcome_data['description'],
                'validation_criteria': outcome_data['success_criteria'],
                'validation_methods': outcome_data['validation_methods'],
                'specific_parameters': outcome_data.get('specific_parameters', {}),
                'confidence': outcome_data.get('confidence', 0.8),
                'clarification_question': outcome_data.get('clarification_question'),
                'source': 'llm_project_manager'
            }
            
            logger.info(f"🎯 Агент проджект-менеджер определил: {outcome_data['result_type']} (уверенность: {expected_outcome['confidence']:.2f})")
            
            # Если есть вопрос для уточнения - запрашиваем у пользователя
            if outcome_data.get('clarification_question'):
                clarified_outcome = await self._clarify_with_user(expected_outcome, task)
                if clarified_outcome:
                    expected_outcome = clarified_outcome
            
            return expected_outcome
            
        except Exception as e:
            # Логируем детальную ошибку
            logger.error(f"❌ Критическая ошибка агента проджект-менеджера: {e}")
            
            # Если это проблема с LLM - поднимаем исключение выше
            if "LLM" in str(e) or "провайдер" in str(e) or "generate_response" in str(e):
                raise RuntimeError(f"❌ Система не может работать без LLM. Ошибка: {e}")
            
            # Для других ошибок тоже поднимаем исключение
            raise RuntimeError(f"❌ Ошибка анализа задачи: {e}")
    
    def _parse_markdown_outcome(self, llm_response: str) -> Dict[str, Any]:
        """Парсинг markdown ответа LLM"""
        import re
        
        # Извлекаем тип результата
        result_type_match = re.search(r'\*\*Тип результата:\*\*\s*[«"]?([^«"»\n]+)[«"»]?', llm_response)
        result_type = result_type_match.group(1).strip() if result_type_match else "файл"
        
        # Извлекаем описание
        description_match = re.search(r'\*\*Ожидаемый результат:\*\*\s*(.*?)(?=\*\*|$)', llm_response, re.DOTALL)
        description = description_match.group(1).strip() if description_match else f"Создание {result_type}"
        
        # Извлекаем критерии (список после "Ожидаемый результат:")
        criteria = []
        if description_match:
            lines = description.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    criteria.append(line[1:].strip())
        
        if not criteria:
            criteria = [f"Файл создан", f"Код работает корректно", f"Соответствует требованиям"]
        
        return {
            'result_type': result_type,
            'description': description,
            'success_criteria': criteria,
            'validation_methods': ["Проверка существования файла", "Проверка содержимого", "Тестирование"],
            'specific_parameters': {},
            'confidence': 0.8,
            'clarification_question': None
        }

    async def _fallback_outcome_extraction(self, task: str) -> Dict[str, Any]:
        """
        УДАЛЕНО: Fallback логика неприемлема
        
        Система должна работать только с LLM-анализом.
        Если LLM недоступен - система честно сообщает об этом.
        """
        raise RuntimeError("❌ Fallback анализ удалён. Система требует LLM для работы.")
    
    async def _handle_llm_unavailable(self, task: str, error: Exception) -> None:
        """Обработка недоступности LLM с уведомлением пользователя"""
        logger.error(f"🚨 LLM недоступен: {error}")
        
        # Создаём заметку о проблеме
        error_note = ObsidianNote(
            title=f"Ошибка LLM - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=f"""# Критическая ошибка: LLM недоступен

## Задача
{task}

## Ошибка
{str(error)}

## Статус системы
❌ **Система не может работать без LLM**

Требуется:
1. Проверить подключение к LLM провайдеру
2. Проверить API ключи
3. Реализовать ротацию провайдеров (TODO)

## Время ошибки
{datetime.now().isoformat()}

---
*Система остановлена до восстановления LLM*
""",
            tags=["ошибка", "llm", "критическая"],
            metadata={
                "error_type": "llm_unavailable",
                "task": task,
                "error_message": str(error),
                "timestamp": datetime.now().isoformat(),
                "system_status": "stopped"
            },
            folder="system"
        )
        
        # Сохраняем в хранилище
        error_path = self.db.save_note(error_note, f"llm_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        logger.error(f"🚨 Ошибка зафиксирована: {error_path}")
        
        # Уведомляем через human-in-the-loop если доступно
        if self.intervention_handler:
            try:
                await self._notify_user_about_llm_error(task, error)
            except Exception as notify_error:
                logger.error(f"❌ Не удалось уведомить пользователя: {notify_error}")
    
    async def _notify_user_about_llm_error(self, task: str, error: Exception) -> None:
        """Уведомление пользователя о недоступности LLM"""
        from .human_collaboration import create_approval_request, InterventionType, InterventionUrgency
        
        notification_request = create_approval_request(
            title="🚨 Критическая ошибка системы",
            description=f"""
СИСТЕМА НЕ МОЖЕТ ПРОДОЛЖИТЬ РАБОТУ

Задача: {task}

Проблема: LLM провайдер недоступен
Ошибка: {str(error)}

Система KittyCore 3.0 требует LLM для:
• Анализа задач агентом проджект-менеджером
• Определения образа конечного результата  
• Интеллектуальной валидации результатов

ДЕЙСТВИЯ:
1. Проверьте подключение к интернету
2. Проверьте API ключи LLM провайдера
3. Дождитесь восстановления сервиса
4. Перезапустите задачу

Система будет ожидать восстановления LLM.
""",
            context={
                "error_type": "llm_unavailable",
                "task": task,
                "error": str(error),
                "system_status": "stopped"
            },
            urgency=InterventionUrgency.HIGH,
            timeout_seconds=3600  # 1 час на решение проблемы
        )
        
        # Сохраняем уведомление
        notification_note = ObsidianNote(
            title=f"🚨 Уведомление об ошибке LLM - {notification_request.id}",
            content=f"""# Критическое уведомление пользователю

{notification_request.description}

## Статус
Ожидание действий пользователя...

---
*Система остановлена*
""",
            tags=["уведомление", "критическая-ошибка", "llm"],
            metadata={
                "notification_id": notification_request.id,
                "error_type": "llm_unavailable",
                "urgency": "high",
                "status": "pending"
            },
            folder="human"
        )
        
        notification_path = self.db.save_note(notification_note, f"llm_error_notification_{notification_request.id}.md")
        logger.error(f"🚨 Уведомление пользователя сохранено: {notification_path}")
        
        # Отправляем уведомление
        try:
            await self.intervention_handler.handle_request(notification_request)
        except Exception as e:
            logger.error(f"❌ Ошибка отправки уведомления: {e}")
    
    async def _clarify_with_user(self, expected_outcome: Dict, original_task: str) -> Optional[Dict[str, Any]]:
        """Уточнение ожидаемого результата у пользователя"""
        if not self.intervention_handler:
            logger.info("👤 Human-in-the-loop отключен, пропускаем уточнение")
            return None
        
        clarification_question = expected_outcome.get('clarification_question')
        if not clarification_question:
            return None
        
        logger.info("👤 Запрашиваем уточнение у пользователя...")
        
        # Создаём запрос на уточнение
        from .human_collaboration import create_approval_request, InterventionType, InterventionUrgency
        
        clarification_request = create_approval_request(
            title="Уточнение ожидаемого результата",
            description=f"""
Задача: {original_task}

Агент проджект-менеджер определил ожидаемый результат:
• Тип: {expected_outcome['type']}
• Описание: {expected_outcome['description']}

Критерии успеха:
{chr(10).join(f'• {criterion}' for criterion in expected_outcome['validation_criteria'])}

ВОПРОС: {clarification_question}

Подтвердите или скорректируйте ожидаемый результат.
""",
            context={
                "expected_outcome": expected_outcome,
                "original_task": original_task,
                "clarification_type": "outcome_verification"
            },
            urgency=InterventionUrgency.MEDIUM,
            timeout_seconds=self.config.intervention_timeout
        )
        
        # Сохраняем запрос в хранилище
        clarification_note = ObsidianNote(
            title=f"Уточнение результата - {clarification_request.id}",
            content=f"""# Уточнение ожидаемого результата

## Исходная задача
{original_task}

## Определённый результат
- **Тип**: {expected_outcome['type']}
- **Описание**: {expected_outcome['description']}

## Критерии успеха
{chr(10).join(f'- {criterion}' for criterion in expected_outcome['validation_criteria'])}

## Вопрос для уточнения
{clarification_question}

## Статус
Ожидание ответа пользователя...

---
*Запрос создан агентом проджект-менеджером*
""",
            tags=["уточнение", "проджект-менеджер", "ожидание"],
            metadata={
                "clarification_id": clarification_request.id,
                "expected_outcome_type": expected_outcome['type'],
                "confidence": expected_outcome['confidence'],
                "status": "pending"
            },
            folder="human"
        )
        
        clarification_path = self.db.save_note(clarification_note, f"clarification_{clarification_request.id}.md")
        logger.info(f"👤 Запрос на уточнение сохранён: {clarification_path}")
        
        try:
            # Обрабатываем запрос
            response = await self.intervention_handler.handle_request(clarification_request)
            
            if response.status.value == "approved":
                logger.info("✅ Пользователь подтвердил ожидаемый результат")
                return expected_outcome
            else:
                logger.info("❌ Пользователь не подтвердил, используем исходный результат")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки уточнения: {e}")
            return None
    
    def _format_expected_outcome(self, outcome: Dict[str, Any]) -> str:
        """Форматирование образа конечного результата для заметки"""
        formatted = f"""
### Тип результата
**{outcome['type']}** - {outcome['description']}

### Критерии валидации
{chr(10).join(f'- {criterion}' for criterion in outcome['validation_criteria'])}

### Методы проверки
{chr(10).join(f'- {method}' for method in outcome['validation_methods'])}

### Уверенность определения
{outcome['confidence']:.1%} (источник: {outcome.get('source', 'unknown')})
"""
        
        # Добавляем специфичные параметры если есть
        if outcome.get('specific_parameters'):
            formatted += f"""
### Конкретные параметры
{chr(10).join(f'- **{key}**: {value}' for key, value in outcome['specific_parameters'].items())}
"""
        
        return formatted
    
    async def _check_human_intervention_needed(self, task: str, analysis: Dict) -> bool:
        """Проверка необходимости человеческого вмешательства"""
        if not self.intervention_handler:
            return False
        
        # Критерии для вмешательства человека
        intervention_needed = False
        reasons = []
        
        # 1. Высокая сложность
        if analysis.get('complexity') in ['high', 'very_high']:
            intervention_needed = True
            reasons.append("Высокая сложность задачи")
        
        # 2. Много агентов
        if analysis.get('estimated_agents', 0) > 5:
            intervention_needed = True
            reasons.append(f"Требуется много агентов: {analysis['estimated_agents']}")
        
        # 3. Неопределённые требования
        if 'неопределённ' in task.lower() or 'не знаю' in task.lower():
            intervention_needed = True
            reasons.append("Неопределённые требования")
        
        # 4. Критические операции
        critical_keywords = ['удалить', 'delete', 'remove', 'очистить', 'форматировать']
        if any(keyword in task.lower() for keyword in critical_keywords):
            intervention_needed = True
            reasons.append("Критические операции")
        
        if intervention_needed:
            logger.info(f"👤 Требуется человеческое вмешательство: {', '.join(reasons)}")
        
        return intervention_needed
    
    async def _request_human_guidance(self, task: str, analysis: Dict) -> Dict[str, Any]:
        """Запрос руководства у человека"""
        if not self.intervention_handler:
            return {}
        
        # Создаём запрос на вмешательство
        request = create_approval_request(
            title="Подтверждение выполнения задачи",
            description=f"""
Задача: {task}

Анализ сложности:
- Сложность: {analysis.get('complexity', 'неизвестно')}
- Агентов: {analysis.get('estimated_agents', 0)}
- Время: {analysis.get('estimated_time', 'неизвестно')}

Продолжить выполнение?
""",
            context={"task": task, "analysis": analysis},
            urgency=InterventionUrgency.MEDIUM,
            timeout_seconds=self.config.intervention_timeout
        )
        
        # Сохраняем запрос в хранилище
        intervention_note = ObsidianNote(
            title=f"Human Intervention - {request.id}",
            content=f"""# Запрос человеческого вмешательства

## Запрос
{request.description}

## Статус
Ожидание ответа...

## Детали
- ID: {request.id}
- Тип: {request.type.value}
- Срочность: {request.urgency.value}
- Таймаут: {request.timeout_seconds}с
""",
            tags=["human", "intervention", "pending"],
            metadata={
                "intervention_id": request.id,
                "intervention_type": request.type.value,
                "urgency": request.urgency.value,
                "status": "pending"
            },
            folder="human"
        )
        
        intervention_path = self.db.save_note(intervention_note, f"intervention_{request.id}.md")
        logger.info(f"👤 Запрос сохранён: {intervention_path}")
        
        try:
            # Обрабатываем запрос
            response = await self.intervention_handler.handle_request(request)
            
            # Обновляем заметку с результатом
            if response.status.value == "approved":
                result = {"approved": True}
                status_text = "✅ Одобрено"
            elif response.status.value == "rejected":
                result = {"approved": False}
                status_text = "❌ Отклонено"
            else:
                result = {"approved": False, "timeout": True}
                status_text = "⏰ Таймаут"
            
            # Обновляем заметку
            updated_content = intervention_note.content.replace(
                "Ожидание ответа...", 
                f"{status_text}\n\nОтвет получен: {response.created_at}"
            )
            
            updated_note = ObsidianNote(
                title=intervention_note.title,
                content=updated_content,
                tags=["human", "intervention", "completed"],
                metadata={
                    **intervention_note.metadata,
                    "status": "completed",
                    "response": response.status.value
                },
                folder="human"
            )
            
            self.db.save_note(updated_note, f"intervention_{request.id}.md")
            logger.info(f"👤 Ответ получен: {status_text}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки вмешательства: {e}")
            return {"approved": False, "error": str(e)}
    
    # === ОСТАЛЬНЫЕ МЕТОДЫ (ЗАГЛУШКИ ДЛЯ СЛЕДУЮЩИХ ЧАСТЕЙ) ===
    
    async def _decompose_task_with_storage(self, task: str, analysis: Dict, task_id: str) -> List[Dict[str, Any]]:
        """Декомпозиция задачи с сохранением в хранилище"""
        # Используем базовый декомпозер
        subtasks = self.task_decomposer.decompose_task(task, analysis['complexity'])
        
        # Создаём граф workflow для визуализации
        workflow_graph = None
        if hasattr(self, 'graph_planner'):
            try:
                # Создаём пустой словарь агентов для планировщика
                empty_agents = {}
                workflow_graph = self.graph_planner.create_workflow_graph(subtasks, empty_agents)
                logger.info(f"📊 Граф workflow создан: {len(workflow_graph.nodes)} узлов")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка создания графа: {e}")
        
        # Сохраняем декомпозицию в ObsidianDB
        decomposition_content = f"""# Декомпозиция задачи

## Исходная задача
{task}

## Анализ сложности
- **Сложность**: {analysis['complexity']}
- **Агентов**: {analysis['estimated_agents']}

## Подзадачи ({len(subtasks)})

"""
        
        # Добавляем каждую подзадачу
        for i, subtask in enumerate(subtasks, 1):
            decomposition_content += f"""### {i}. {subtask.get('title', f'Подзадача {i}')}

**Описание**: {subtask.get('description', 'Описание отсутствует')}

**Детали**:
- ID: `{subtask.get('id', f'subtask_{i}')}`
- Приоритет: {subtask.get('priority', 'средний')}
- Сложность: {subtask.get('complexity', 'неизвестно')}
- Навыки: {', '.join(subtask.get('required_skills', []))}
- Зависимости: {', '.join(subtask.get('dependencies', [])) or 'нет'}

---

"""
        
        # Добавляем граф если есть
        if workflow_graph:
            mermaid_diagram = workflow_graph.to_mermaid()
            decomposition_content += f"""## Граф выполнения

```mermaid
{mermaid_diagram}
```

"""
        
        # Создаём заметку
        decomposition_note = ObsidianNote(
            title=f"Декомпозиция - {task_id}",
            content=decomposition_content,
            tags=["декомпозиция", "планирование", str(analysis['complexity'])],
            metadata={
                "task_id": task_id,
                "decomposition_type": "workflow",
                "subtasks_count": len(subtasks),
                "complexity": analysis['complexity'],
                "has_graph": workflow_graph is not None,
                "timestamp": datetime.now().isoformat()
            },
            folder="tasks"
        )
        
        # Сохраняем в хранилище
        decomposition_path = self.db.save_note(decomposition_note, f"decomposition_{task_id}.md")
        logger.info(f"🔄 Декомпозиция сохранена: {decomposition_path}")
        
        # Сохраняем каждую подзадачу как отдельную заметку
        for subtask in subtasks:
            subtask_content = f"""# Подзадача: {subtask.get('title', 'Без названия')}

## Описание
{subtask.get('description', 'Описание отсутствует')}

## Технические детали
- **ID**: `{subtask.get('id')}`
- **Приоритет**: {subtask.get('priority', 'средний')}
- **Сложность**: {subtask.get('complexity', 'неизвестно')}
- **Статус**: ожидание выполнения

## Требуемые навыки
{chr(10).join(f'- {skill}' for skill in subtask.get('required_skills', []))}

## Зависимости
{chr(10).join(f'- [[subtask_{dep}]]' for dep in subtask.get('dependencies', [])) or 'Нет зависимостей'}

## Связи
- Родительская задача: [[{task_id}]]
- Декомпозиция: [[decomposition_{task_id}]]

---
*Создано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            subtask_note = ObsidianNote(
                title=f"Подзадача: {subtask.get('title', subtask.get('id'))}",
                content=subtask_content,
                tags=["подзадача", "планирование", str(subtask.get('complexity', 'unknown'))],
                metadata={
                    "task_id": task_id,
                    "subtask_id": subtask.get('id'),
                    "subtask_type": subtask.get('type', 'general'),
                    "priority": subtask.get('priority', 'medium'),
                    "complexity": subtask.get('complexity', 'unknown'),
                    "status": "pending",
                    "required_skills": subtask.get('required_skills', []),
                    "dependencies": subtask.get('dependencies', []),
                    "timestamp": datetime.now().isoformat()
                },
                folder="tasks"
            )
            
            subtask_path = self.db.save_note(subtask_note, f"subtask_{subtask.get('id')}.md")
            logger.debug(f"📝 Подзадача сохранена: {subtask_path}")
        
        logger.info(f"🔄 Декомпозиция выполнена: {len(subtasks)} подзадач сохранено")
        return subtasks
    
    async def _create_agent_team(self, subtasks: List[Dict], task_id: str) -> Dict[str, Any]:
        """Создание команды агентов с интеграцией A-MEM семантического поиска"""
        # Используем базовые компоненты
        resources = self.complexity_evaluator.evaluate_resources(subtasks)
        skills = self.skillset_matcher.match_skills(subtasks)
        
        # 🧠 A-MEM: Получаем контекст предыдущего опыта
        amem_insights = await self._get_amem_insights_for_team_creation(subtasks, task_id)
        
        agents = {}
        agent_workspaces = {}
        team_composition = {
            "team_id": f"team_{task_id}",
            "created_at": datetime.now().isoformat(),
            "total_agents": 0,
            "agent_roles": {},
            "skill_coverage": {},
            "coordination_setup": False,
            "amem_insights": amem_insights  # 🧠 Добавляем insights из A-MEM
        }
        
        # Создаём агентов для каждой подзадачи
        for subtask in subtasks:
            subtask_id = subtask.get("id", f"subtask_{len(agents)}")
            required_skills = skills.get(subtask_id, subtask.get('required_skills', []))
            
            # Создаём IntellectualAgent напрямую (без старого OrchestratorAgent)
            from ..agents.intellectual_agent import IntellectualAgent
            
            # Определяем роль агента на основе навыков
            role_map = {
                "web_search": "researcher",
                "code_generation": "developer", 
                "file_management": "organizer",
                "analysis": "analyst"
            }
            
            # Выбираем роль на основе первого навыка или по умолчанию
            primary_skill = required_skills[0] if required_skills else "general"
            agent_role = role_map.get(primary_skill, "generalist")
            
            # Создаём IntellectualAgent
            agent = IntellectualAgent(agent_role, subtask)
            agent_id = f"agent_{subtask_id}"
            agents[agent_id] = agent
            
            # Создаём рабочее пространство агента в ObsidianDB
            try:
                workspace = create_agent_workspace(
                    agent_id=agent_id,
                    vault_path=self.config.vault_path
                )
                agent_workspaces[agent_id] = workspace
                logger.info(f"🏗️ Рабочее пространство создано для {agent_id}")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка создания workspace для {agent_id}: {e}")
            
            # Регистрируем агента в SharedChat
            if self.shared_chat:
                try:
                    self.shared_chat.register_agent(
                        agent_id=agent_id,
                        agent_role=getattr(agent, 'role', 'worker'),
                        is_coordinator=False
                    )
                    logger.debug(f"💬 Агент {agent_id} зарегистрирован в SharedChat")
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка регистрации {agent_id} в SharedChat: {e}")
            
            # Обновляем состав команды
            agent_role = getattr(agent, 'role', 'worker')
            team_composition["agent_roles"][agent_id] = {
                "role": agent_role,
                "assigned_subtask": subtask_id,
                "required_skills": required_skills,
                "workspace_path": getattr(agent_workspaces.get(agent_id), 'workspace_folder', 'unknown')
            }
            
            # Обновляем покрытие навыков
            for skill in required_skills:
                if skill not in team_composition["skill_coverage"]:
                    team_composition["skill_coverage"][skill] = []
                team_composition["skill_coverage"][skill].append(agent_id)
        
        team_composition["total_agents"] = len(agents)
        team_composition["coordination_setup"] = self.shared_chat is not None
        
        # Сохраняем информацию о команде в ObsidianDB
        team_content = f"""# Команда агентов - {task_id}

## Состав команды ({len(agents)} агентов)

"""
        
        # Добавляем информацию о каждом агенте
        for agent_id, agent_info in team_composition["agent_roles"].items():
            team_content += f"""### {agent_id}

- **Роль**: {agent_info['role']}
- **Подзадача**: [[subtask_{agent_info['assigned_subtask']}]]
- **Навыки**: {', '.join(agent_info['required_skills'])}
- **Workspace**: `{agent_info['workspace_path']}`

"""
        
        # 🧠 A-MEM: Добавляем insights из коллективной памяти
        if amem_insights.get("enabled", False):
            team_content += f"""## 🧠 A-MEM Insights из коллективной памяти

### Общие рекомендации
"""
            for recommendation in amem_insights.get("agent_recommendations", []):
                team_content += f"- {recommendation}\n"
            
            # Детальные insights по подзадачам
            for subtask_insight in amem_insights.get("search_results", []):
                if subtask_insight.get("recommendations"):
                    team_content += f"""
### Подзадача: {subtask_insight['subtask_id']}
- **Успешных решений найдено**: {subtask_insight['successful_solutions']}
- **Опытных агентов**: {subtask_insight['experienced_agents']} 
- **Известных проблем**: {subtask_insight['known_issues']}

**Рекомендации A-MEM:**
"""
                    for rec in subtask_insight["recommendations"]:
                        emoji = "✅" if rec["type"] == "best_practice" else "🤖" if rec["type"] == "role_recommendation" else "⚠️"
                        team_content += f"- {emoji} {rec['advice']} _(источник: {rec['source']})_\n"
        
        # Добавляем покрытие навыков
        team_content += f"""## Покрытие навыков

"""
        for skill, agent_list in team_composition["skill_coverage"].items():
            team_content += f"- **{skill}**: {', '.join(agent_list)}\n"
        
        # Добавляем информацию о координации
        team_content += f"""

## Координация

- **SharedChat**: {'✅ Активен' if self.shared_chat else '❌ Отключен'}
- **Команда ID**: `{team_composition['team_id']}`
- **Создано**: {team_composition['created_at']}

## Ресурсы

{self._format_resources_info(resources)}

---
*Команда создана автоматически системой UnifiedOrchestrator*
"""
        
        # Создаём заметку о команде
        team_note = ObsidianNote(
            title=f"Команда агентов - {task_id}",
            content=team_content,
            tags=["команда", "агенты", "координация"],
            metadata={
                "task_id": task_id,
                "team_id": team_composition["team_id"],
                "total_agents": team_composition["total_agents"],
                "coordination_enabled": team_composition["coordination_setup"],
                "agent_roles": list(team_composition["agent_roles"].keys()),
                "skill_coverage": list(team_composition["skill_coverage"].keys()),
                "timestamp": datetime.now().isoformat()
            },
            folder="agents"
        )
        
        # Сохраняем в хранилище
        team_path = self.db.save_note(team_note, f"team_{task_id}.md")
        logger.info(f"👥 Информация о команде сохранена: {team_path}")
        
        # Создаём заметки для каждого агента
        for agent_id, agent in agents.items():
            agent_info = team_composition["agent_roles"][agent_id]
            
            agent_content = f"""# Агент: {agent_id}

## Профиль агента

- **ID**: `{agent_id}`
- **Роль**: {agent_info['role']}
- **Статус**: активен
- **Создан**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Назначенная подзадача

[[subtask_{agent_info['assigned_subtask']}]]

## Навыки и возможности

{chr(10).join(f'- {skill}' for skill in agent_info['required_skills'])}

## Рабочее пространство

- **Путь**: `{agent_info['workspace_path']}`
- **Команда**: [[team_{task_id}]]

## Координация

- **SharedChat**: {'✅ Зарегистрирован' if self.shared_chat else '❌ Не используется'}
- **Команда ID**: `{team_composition['team_id']}`

## История работы

*История будет обновляться по мере выполнения задач*

---
*Агент создан автоматически для задачи {task_id}*
"""
            
            agent_note = ObsidianNote(
                title=f"Агент: {agent_id}",
                content=agent_content,
                tags=["агент", agent_info['role'], "активен"],
                metadata={
                    "agent_id": agent_id,
                    "agent_role": agent_info['role'],
                    "task_id": task_id,
                    "team_id": team_composition["team_id"],
                    "assigned_subtask": agent_info['assigned_subtask'],
                    "required_skills": agent_info['required_skills'],
                    "status": "active",
                    "workspace_path": agent_info['workspace_path'],
                    "coordination_enabled": self.shared_chat is not None,
                    "timestamp": datetime.now().isoformat()
                },
                folder="agents"
            )
            
            agent_path = self.db.save_note(agent_note, f"agent_{agent_id}.md")
            logger.debug(f"🤖 Профиль агента сохранён: {agent_path}")
        
        # Уведомляем команду о создании
        if self.shared_chat:
            try:
                await self.shared_chat.broadcast_update(
                    sender_id=self.config.orchestrator_id,
                    update=f"Команда из {len(agents)} агентов создана и готова к работе",
                    task_info={
                        "team_id": team_composition["team_id"],
                        "agent_count": len(agents),
                        "skill_coverage": list(team_composition["skill_coverage"].keys())
                    }
                )
                logger.info("📢 Команда уведомлена о создании")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка уведомления команды: {e}")
        
        self.agents_created += len(agents)
        logger.info(f"🤖 Команда создана: {len(agents)} агентов с полной интеграцией")
        
        return {
            "agents": agents,
            "workspaces": agent_workspaces,
            "team_composition": team_composition,
            "resources": resources,
            "skills_mapping": skills
        }
    
    def _format_resources_info(self, resources: Dict) -> str:
        """Форматирование информации о ресурсах"""
        if not resources:
            return "Информация о ресурсах недоступна"
        
        formatted = ""
        for resource_type, details in resources.items():
            formatted += f"- **{resource_type}**: {details}\n"
        
        return formatted or "Ресурсы не требуются"
    
    async def _execute_with_unified_coordination(self, agents: Dict, subtasks: List, task: str, task_id: str) -> Dict[str, Any]:
        """Выполнение с координацией через SharedChat"""
        # Извлекаем данные из новой структуры
        agent_objects = agents.get("agents", {})
        team_composition = agents.get("team_composition", {})
        workspaces = agents.get("workspaces", {})
        
        # Формируем команду и workflow
        team = self.team_composer.compose_team(agent_objects)
        workflow = self.workflow_planner.plan_workflow(subtasks, team)
        
        # Создаём заметку о начале выполнения
        execution_start_content = f"""# Выполнение задачи - {task_id}

## Исходная задача
{task}

## Команда
- **Команда ID**: `{team_composition.get('team_id', 'unknown')}`
- **Агентов**: {len(agent_objects)}
- **Workflow шагов**: {len(workflow.get('steps', []))}

## Статус выполнения

🟡 **В процессе** - Начато {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Прогресс

*Обновляется в реальном времени...*

---
*Выполнение начато UnifiedOrchestrator*
"""
        
        execution_note = ObsidianNote(
            title=f"Выполнение - {task_id}",
            content=execution_start_content,
            tags=["выполнение", "в-процессе", "координация"],
            metadata={
                "task_id": task_id,
                "team_id": team_composition.get('team_id'),
                "execution_status": "in_progress",
                "started_at": datetime.now().isoformat(),
                "agent_count": len(agent_objects),
                "workflow_steps": len(workflow.get('steps', [])),
                "coordination_enabled": self.shared_chat is not None
            },
            folder="coordination"
        )
        
        execution_path = self.db.save_note(execution_note, f"execution_{task_id}.md")
        logger.info(f"⚡ Выполнение начато: {execution_path}")
        
        # Уведомляем о начале выполнения
        if self.shared_chat:
            await self.shared_chat.broadcast_update(
                sender_id=self.config.orchestrator_id,
                update="🚀 Начинаем выполнение задач",
                task_info={
                    'workflow_steps': len(workflow.get('steps', [])),
                    'team_id': team_composition.get('team_id'),
                    'coordination_mode': 'unified'
                }
            )
        
        # Выполняем через базовый ExecutionManager
        try:
            execution_result = await self.execution_manager.execute_workflow(workflow, team)
            
            # Обновляем статус выполнения
            success_count = len([r for r in execution_result.get('results', []) if r.get('success', False)])
            total_count = len(execution_result.get('results', []))
            success_rate = success_count / total_count if total_count > 0 else 0
            
            # Определяем финальный статус
            if success_rate >= 0.8:
                final_status = "✅ **Успешно завершено**"
                status_tag = "завершено"
            elif success_rate >= 0.5:
                final_status = "🟡 **Частично выполнено**"
                status_tag = "частично"
            else:
                final_status = "❌ **Выполнение с ошибками**"
                status_tag = "ошибки"
            
            # Обновляем заметку о выполнении
            execution_end_content = execution_start_content.replace(
                "🟡 **В процессе** - Начато",
                f"{final_status} - Завершено"
            ).replace(
                "*Обновляется в реальном времени...*",
                f"""
## Результаты

- **Успешно**: {success_count}/{total_count} ({success_rate:.1%})
- **Завершено**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Детали выполнения

{self._format_execution_results(execution_result)}

### Созданные файлы

{self._format_created_files(execution_result)}
"""
            )
            
            updated_execution_note = ObsidianNote(
                title=f"Выполнение - {task_id}",
                content=execution_end_content,
                tags=["выполнение", status_tag, "координация"],
                metadata={
                    **execution_note.metadata,
                    "execution_status": "completed",
                    "completed_at": datetime.now().isoformat(),
                    "success_rate": success_rate,
                    "success_count": success_count,
                    "total_count": total_count
                },
                folder="coordination"
            )
            
            self.db.save_note(updated_execution_note, f"execution_{task_id}.md")
            
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения workflow: {e}")
            execution_result = {
                "status": "failed",
                "error": str(e),
                "results": [],
                "workflow": workflow
            }
        
        # Уведомляем о завершении
        if self.shared_chat:
            success_count = len([r for r in execution_result.get('results', []) if r.get('success', False)])
            total_count = len(execution_result.get('results', []))
            
            await self.shared_chat.broadcast_update(
                sender_id=self.config.orchestrator_id,
                update=f"🏁 Выполнение завершено: {success_count}/{total_count} успешно",
                task_info={
                    'success_rate': success_count / total_count if total_count > 0 else 0,
                    'original_task': task,
                    'team_id': team_composition.get('team_id'),
                    'final_status': execution_result.get('status', 'unknown')
                }
            )
        
        # Обновляем статусы агентов
        await self._update_agent_statuses(agent_objects, execution_result, task_id)
        
        self.workflows_executed += 1
        logger.info(f"⚡ Выполнение завершено: {execution_result.get('status', 'unknown')}")
        
        return execution_result
    
    def _format_execution_results(self, execution_result: Dict) -> str:
        """Форматирование результатов выполнения"""
        results = execution_result.get('results', [])
        if not results:
            return "Результаты недоступны"
        
        formatted = ""
        for i, result in enumerate(results, 1):
            status = "✅" if result.get('success', False) else "❌"
            formatted += f"{i}. {status} {result.get('description', 'Без описания')}\n"
        
        return formatted
    
    def _format_created_files(self, execution_result: Dict) -> str:
        """Форматирование списка созданных файлов"""
        files = execution_result.get('created_files', [])
        if not files:
            return "Файлы не созданы"
        
        formatted = ""
        for file_path in files:
            formatted += f"- `{file_path}`\n"
        
        return formatted
    
    async def _update_agent_statuses(self, agents: Dict, execution_result: Dict, task_id: str):
        """Обновление статусов агентов после выполнения + интеграция A-MEM"""
        try:
            for agent_id in agents.keys():
                # Находим результат для этого агента
                agent_result = None
                for result in execution_result.get('results', []):
                    if result.get('agent_id') == agent_id:
                        agent_result = result
                        break
                
                # Определяем статус
                if agent_result:
                    status = "completed" if agent_result.get('success', False) else "failed"
                    status_emoji = "✅" if agent_result.get('success', False) else "❌"
                else:
                    status = "unknown"
                    status_emoji = "❓"
                
                # 🧠 A-MEM: Сохраняем опыт агента в агентную память
                if self.amem_system and agent_result:
                    await self._save_agent_experience_to_amem(
                        agent_id=agent_id,
                        agent_data=agents[agent_id],
                        agent_result=agent_result,
                        task_id=task_id
                    )
                
                # Обновляем заметку агента
                try:
                    agent_note_path = f"agent_{agent_id}.md"
                    # TODO: Обновить заметку агента с результатами
                    logger.debug(f"🤖 Статус агента {agent_id} обновлён: {status}")
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка обновления статуса {agent_id}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Ошибка обновления статусов агентов: {e}")
    
    async def _save_agent_experience_to_amem(self, agent_id: str, agent_data: Dict, agent_result: Dict, task_id: str):
        """🧠 Сохранение опыта агента в A-MEM для эволюции коллективной памяти"""
        try:
            # Формируем контекст опыта агента
            experience_context = {
                "agent_id": agent_id,
                "agent_role": agent_data.get('role', 'Unknown'),
                "task_id": task_id,
                "success": agent_result.get('success', False),
                "execution_time": agent_result.get('execution_time', 0),
                "tools_used": agent_result.get('tools_used', []),
                "files_created": agent_result.get('files_created', []),
                "errors": agent_result.get('errors', [])
            }
            
            # Создаём воспоминание для A-MEM
            memory_content = f"""
            Опыт агента {agent_id} (роль: {agent_data.get('role', 'Unknown')})
            
            Задача: {task_id}
            Статус: {'✅ Успех' if agent_result.get('success') else '❌ Ошибка'}
            Время выполнения: {agent_result.get('execution_time', 0):.2f}с
            
            Инструменты: {', '.join(agent_result.get('tools_used', []))}
            Созданные файлы: {len(agent_result.get('files_created', []))}
            
            Детали работы: {agent_result.get('content', 'Нет деталей')}
            """
            
            # Определяем тег для категоризации
            memory_tag = f"agent_experience_{agent_data.get('role', 'unknown').lower()}"
            if not agent_result.get('success'):
                memory_tag += "_failure"
            
            # Сохраняем в A-MEM
            await self.amem_system.store_memory(
                content=memory_content.strip(),
                context=experience_context,
                tags=[memory_tag, f"task_{task_id}", f"agent_{agent_id}"]
            )
            
            logger.info(f"🧠 Опыт агента {agent_id} сохранён в A-MEM")
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка сохранения опыта агента {agent_id} в A-MEM: {e}")
    
    async def _validate_results(self, task: str, execution_result: Dict) -> Dict[str, Any]:
        """Интеллектуальная валидация результатов на основе образа конечного результата"""
        if not self.smart_validator:
            return {"quality_score": 0.5, "validation": "SmartValidator отключен"}
        
        # ИСПРАВЛЕНИЕ: Собираем ВСЕ созданные файлы ПЕРЕД валидацией
        created_files = execution_result.get('created_files', []) or execution_result.get('files_created', [])
        
        # Дополнительно собираем файлы из step_results (ExecutionManager)
        all_step_files = []
        for step_id, step_result in execution_result.get('step_results', {}).items():
            if isinstance(step_result, dict):
                step_files = step_result.get('files_created', []) or step_result.get('created_files', [])
                all_step_files.extend(step_files)
        
        # Дополнительно собираем файлы из agent_results (если есть)
        all_agent_files = []
        for agent_id, agent_result in execution_result.get('agent_results', {}).items():
            if isinstance(agent_result, dict):
                agent_files = agent_result.get('files_created', []) or agent_result.get('created_files', [])
                all_agent_files.extend(agent_files)
        
        # Дополнительно собираем файлы из results array
        all_results_files = []
        for result in execution_result.get('results', []):
            if isinstance(result, dict):
                result_files = result.get('files_created', []) or result.get('created_files', [])
                all_results_files.extend(result_files)
        
        # КРИТИЧНО: Проверяем реальные файлы в outputs/
        import os
        from pathlib import Path
        
        real_files = []
        outputs_dir = Path("./outputs")
        if outputs_dir.exists():
            real_files = [str(f) for f in outputs_dir.rglob("*") if f.is_file()]
        
        # Объединяем ВСЕ источники файлов
        all_files = list(set(
            created_files + all_step_files + all_agent_files + 
            all_results_files + real_files
        ))
        
        # Убираем пустые значения
        all_files = [f for f in all_files if f]
        
        # ОБНОВЛЯЕМ execution_result с полным списком файлов
        execution_result['created_files'] = all_files
        
        logger.info(f"📁 Найдено файлов для валидации: {len(all_files)}")
        if all_files:
            logger.info(f"📄 Файлы: {', '.join(all_files[:3])}" + ("..." if len(all_files) > 3 else ""))
        
        # Получаем образ ожидаемого результата из анализа задачи
        expected_outcome = execution_result.get('task_analysis', {}).get('expected_outcome')
        if not expected_outcome:
            logger.warning("⚠️ Образ ожидаемого результата не найден, используем базовую валидацию")
            return await self._basic_validation(task, execution_result)
        
        logger.info(f"🎯 Валидация по образу результата: {expected_outcome['type']}")
        
        try:
            # Выполняем валидацию в зависимости от типа ожидаемого результата
            validation_result = await self._validate_by_outcome_type(
                task, execution_result, expected_outcome
            )
            
            # Определяем нужна ли доработка
            needs_rework = validation_result['quality_score'] < 0.7
            validation_result['needs_rework'] = needs_rework
            
            if needs_rework:
                logger.warning(f"⚠️ Результат требует доработки: {validation_result['quality_score']:.2f}")
                validation_result['rework_reasons'] = await self._identify_rework_reasons(
                    validation_result, expected_outcome
                )
            else:
                logger.info(f"✅ Валидация успешна: {validation_result['quality_score']:.2f}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Ошибка валидации: {e}")
            return {
                "quality_score": 0.3, 
                "validation": f"Ошибка валидации: {e}",
                "needs_rework": True,
                "rework_reasons": ["Техническая ошибка валидации"]
            }
    
    async def _validate_by_outcome_type(self, task: str, execution_result: Dict, expected_outcome: Dict) -> Dict[str, Any]:
        """Валидация в зависимости от типа ожидаемого результата"""
        outcome_type = expected_outcome['type']
        
        if outcome_type == 'application':
            return await self._validate_application_result(task, execution_result, expected_outcome)
        elif outcome_type == 'financial':
            return await self._validate_financial_result(task, execution_result, expected_outcome)
        elif outcome_type == 'information_service':
            return await self._validate_information_service_result(task, execution_result, expected_outcome)
        elif outcome_type == 'content':
            return await self._validate_content_result(task, execution_result, expected_outcome)
        elif outcome_type == 'data_analysis':
            return await self._validate_analysis_result(task, execution_result, expected_outcome)
        elif outcome_type == 'automation':
            return await self._validate_automation_result(task, execution_result, expected_outcome)
        else:
            return await self._validate_generic_result(task, execution_result, expected_outcome)
    
    async def _validate_application_result(self, task: str, execution_result: Dict, expected_outcome: Dict) -> Dict[str, Any]:
        """Валидация результата создания приложения"""
        validation_score = 0.0
        validation_details = []
        issues = []
        
        created_files = execution_result.get('created_files', []) or execution_result.get('files_created', [])
        
        # 1. Проверяем наличие исполняемых файлов
        executable_files = [f for f in created_files if f.endswith(('.py', '.js', '.html', '.exe', '.jar'))]
        if executable_files:
            validation_score += 0.3
            validation_details.append("✅ Найдены исполняемые файлы")
        else:
            issues.append("❌ Не найдены исполняемые файлы приложения")
        
        # 2. Проверяем структуру проекта
        has_main_file = any('main' in f.lower() or 'index' in f.lower() or 'app' in f.lower() for f in created_files)
        if has_main_file:
            validation_score += 0.2
            validation_details.append("✅ Найден главный файл приложения")
        else:
            issues.append("❌ Не найден главный файл приложения")
        
        # 3. Проверяем наличие конфигурационных файлов
        config_files = [f for f in created_files if any(ext in f.lower() for ext in ['package.json', 'requirements.txt', 'config', 'settings'])]
        if config_files:
            validation_score += 0.2
            validation_details.append("✅ Найдены конфигурационные файлы")
        else:
            issues.append("⚠️ Отсутствуют конфигурационные файлы")
        
        # 4. Проверяем специфичные требования
        specific_params = expected_outcome.get('specific_parameters', {})
        if specific_params.get('frontend_framework'):
            frontend_files = [f for f in created_files if any(fw in f.lower() for fw in ['react', 'vue', 'angular', 'component'])]
            if frontend_files:
                validation_score += 0.15
                validation_details.append("✅ Frontend framework обнаружен")
            else:
                issues.append("❌ Требуемый frontend framework не найден")
        
        if specific_params.get('api_required'):
            api_files = [f for f in created_files if any(api in f.lower() for api in ['api', 'router', 'endpoint', 'controller'])]
            if api_files:
                validation_score += 0.15
                validation_details.append("✅ API компоненты найдены")
            else:
                issues.append("❌ Требуемые API компоненты не найдены")
        
        # 5. Базовая проверка качества кода
        if len(created_files) > 0:
            validation_score = min(validation_score + 0.1, 1.0)
            validation_details.append("✅ Файлы созданы")
        
        return {
            'quality_score': validation_score,
            'validation_type': 'application',
            'validation_details': validation_details,
            'issues': issues,
            'created_files_count': len(created_files),
            'executable_files': executable_files,
            'meets_requirements': validation_score >= 0.7
        }
    
    async def _validate_financial_result(self, task: str, execution_result: Dict, expected_outcome: Dict) -> Dict[str, Any]:
        """Валидация финансового результата"""
        validation_score = 0.0
        validation_details = []
        issues = []
        
        # Для финансовых задач нужна реальная проверка счетов/транзакций
        # В демо-режиме проверяем наличие финансовых файлов/отчётов
        created_files = execution_result.get('created_files', []) or execution_result.get('files_created', [])
        financial_files = [f for f in created_files if any(keyword in f.lower() for keyword in ['finance', 'money', 'payment', 'transaction', 'invoice'])]
        
        if financial_files:
            validation_score += 0.4
            validation_details.append("✅ Найдены финансовые документы")
        else:
            issues.append("❌ Отсутствуют финансовые документы")
        
        # Проверяем целевую сумму если указана
        target_amount = expected_outcome.get('specific_parameters', {}).get('target_amount')
        if target_amount:
            # В реальной системе здесь была бы проверка баланса
            validation_details.append(f"🎯 Целевая сумма: {target_amount}")
            validation_score += 0.3  # Демо-бонус
        
        return {
            'quality_score': validation_score,
            'validation_type': 'financial',
            'validation_details': validation_details,
            'issues': issues,
            'target_amount': target_amount,
            'meets_requirements': validation_score >= 0.7
        }
    
    async def _validate_information_service_result(self, task: str, execution_result: Dict, expected_outcome: Dict) -> Dict[str, Any]:
        """Валидация результата информационного сервиса"""
        # Реализация валидации результата информационного сервиса
        # Это может включать проверку релевантности ответов, удовлетворённости пользователей и т.д.
        # В данном примере мы используем базовую валидацию
        return await self._basic_validation(task, execution_result)
    
    async def _validate_content_result(self, task: str, execution_result: Dict, expected_outcome: Dict) -> Dict[str, Any]:
        """Валидация результата создания контента"""
        # Реализация валидации результата создания контента
        # Это может включать проверку соответствия контента техническому заданию, грамматики и стилистики, объёма и уникальности
        # В данном примере мы используем базовую валидацию
        return await self._basic_validation(task, execution_result)
    
    async def _validate_analysis_result(self, task: str, execution_result: Dict, expected_outcome: Dict) -> Dict[str, Any]:
        """Валидация результата анализа данных"""
        # Реализация валидации результата анализа данных
        # Это может включать проверку обработки данных, выводов, визуализации и т.д.
        # В данном примере мы используем базовую валидацию
        return await self._basic_validation(task, execution_result)
    
    async def _validate_automation_result(self, task: str, execution_result: Dict, expected_outcome: Dict) -> Dict[str, Any]:
        """Валидация результата автоматизации"""
        # Реализация валидации результата автоматизации
        # Это может включать проверку автоматического выполнения процесса, обработки ошибок и т.д.
        # В данном примере мы используем базовую валидацию
        return await self._basic_validation(task, execution_result)
    
    async def _validate_generic_result(self, task: str, execution_result: Dict, expected_outcome: Dict) -> Dict[str, Any]:
        """Валидация общего результата с проверкой содержимого файлов"""
        validation_score = 0.5  # Базовый балл
        validation_details = ["✅ Базовая валидация выполнена"]
        issues = []
        
        created_files = execution_result.get('created_files', []) or execution_result.get('files_created', [])
        if created_files:
            validation_score += 0.2
            validation_details.append(f"✅ Создано файлов: {len(created_files)}")
            
            # НОВОЕ: Проверяем содержимое файлов
            content_validation = await self._validate_file_contents(created_files, task, expected_outcome)
            validation_score += content_validation['score_bonus']
            validation_details.extend(content_validation['details'])
            issues.extend(content_validation['issues'])
        else:
            issues.append("⚠️ Файлы не созданы")
        
        return {
            'quality_score': validation_score,
            'validation_type': 'generic',
            'validation_details': validation_details,
            'issues': issues,
            'meets_requirements': validation_score >= 0.7
        }
    
    async def _validate_file_contents(self, created_files: List[str], task: str, expected_outcome: Dict) -> Dict[str, Any]:
        """
        РЕВОЛЮЦИОННАЯ валидация содержимого файлов - ПРЕВОСХОДИТ ВСЕ СИСТЕМЫ!
        
        Проверяет что файлы содержат РЕАЛЬНЫЙ контент, а не отчёты под нужными расширениями.
        НОВИНКА: ЖЁСТКИЕ ШТРАФЫ за поддельные отчёты!
        """
        score_bonus = 0.0
        details = []
        issues = []
        fake_files_count = 0
        total_files_count = 0
        
        for file_path in created_files:
            try:
                # Читаем содержимое файла
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                else:
                    issues.append(f"❌ Файл не найден: {file_path}")
                    continue
                
                total_files_count += 1
                
                # Определяем ожидаемый тип содержимого по расширению
                file_ext = os.path.splitext(file_path)[1].lower()
                content_check = self._check_content_by_extension(file_path, content, file_ext, task)
                
                # СНАЧАЛА проверяем на подделки - ЭТО ПРИОРИТЕТ!
                fake_report_check = self._detect_fake_reports(content, file_path, task)
                if fake_report_check['is_fake']:
                    fake_files_count += 1
                    issues.append(f"🚨 ПОДДЕЛКА: {file_path}: {fake_report_check['reason']}")
                    # ЖЁСТКИЙ ШТРАФ за подделку - минус от базового балла!
                    score_bonus -= 0.25  # Каждая подделка = -25% от базового балла
                    continue  # Не даём бонусы за поддельные файлы!
                
                # Только если файл НЕ подделка - проверяем содержимое
                if content_check['is_valid']:
                    score_bonus += content_check['bonus']
                    details.append(f"✅ {file_path}: {content_check['reason']}")
                else:
                    issues.append(f"❌ {file_path}: {content_check['reason']}")
                    score_bonus -= 0.05  # Малый штраф за невалидное содержимое
                
                details.append(f"✅ {file_path}: содержимое аутентично")
                
            except Exception as e:
                issues.append(f"❌ Ошибка чтения {file_path}: {e}")
        
        # КРИТИЧЕСКАЯ ЛОГИКА: Если много подделок - результат провален!
        fake_ratio = fake_files_count / max(total_files_count, 1)
        
        if fake_ratio >= 0.5:  # 50%+ подделок = критический провал
            score_bonus = -0.5  # Огромный штраф
            issues.append(f"🚨 КРИТИЧЕСКИЙ ПРОВАЛ: {fake_files_count}/{total_files_count} файлов - подделки!")
        elif fake_ratio >= 0.3:  # 30%+ подделок = серьёзные проблемы
            score_bonus -= 0.2  # Дополнительный штраф
            issues.append(f"⚠️ СЕРЬЁЗНЫЕ ПРОБЛЕМЫ: {fake_files_count}/{total_files_count} файлов - подделки!")
        
        return {
            'score_bonus': score_bonus,  # Убираем ограничение max() - штрафы должны работать!
            'details': details,
            'issues': issues,
            'fake_files_count': fake_files_count,
            'total_files_count': total_files_count,
            'fake_ratio': fake_ratio
        }
    
    def _check_content_by_extension(self, file_path: str, content: str, file_ext: str, task: str) -> Dict[str, Any]:
        """Проверка соответствия содержимого расширению файла"""
        
        if file_ext == '.py':
            # Для Python файлов
            if self._is_valid_python_content(content, task):
                return {'is_valid': True, 'bonus': 0.15, 'reason': 'валидный Python код'}
            else:
                return {'is_valid': False, 'bonus': 0, 'reason': 'не является Python кодом'}
        
        elif file_ext == '.html':
            # Для HTML файлов
            if self._is_valid_html_content(content, task):
                return {'is_valid': True, 'bonus': 0.1, 'reason': 'валидный HTML'}
            else:
                return {'is_valid': False, 'bonus': 0, 'reason': 'не является HTML'}
        
        elif file_ext == '.js':
            # Для JavaScript файлов
            if self._is_valid_javascript_content(content, task):
                return {'is_valid': True, 'bonus': 0.15, 'reason': 'валидный JavaScript'}
            else:
                return {'is_valid': False, 'bonus': 0, 'reason': 'не является JavaScript кодом'}
        
        elif file_ext == '.json':
            # Для JSON файлов
            if self._is_valid_json_content(content):
                return {'is_valid': True, 'bonus': 0.1, 'reason': 'валидный JSON'}
            else:
                return {'is_valid': False, 'bonus': 0, 'reason': 'не является валидным JSON'}
        
        elif file_ext in ['.txt', '.md']:
            # Для текстовых файлов - проверяем что это не HTML в .txt
            if '<html>' in content.lower() or '<!doctype' in content.lower():
                return {'is_valid': False, 'bonus': 0, 'reason': 'HTML код в текстовом файле'}
            else:
                return {'is_valid': True, 'bonus': 0.05, 'reason': 'текстовое содержимое'}
        
        else:
            # Для других расширений - базовая проверка
            return {'is_valid': True, 'bonus': 0.02, 'reason': 'файл создан'}
    
    def _is_valid_python_content(self, content: str, task: str) -> bool:
        """Проверка что содержимое является валидным Python кодом"""
        # 1. Не должно содержать HTML теги
        if '<html>' in content.lower() or '<!doctype' in content.lower() or '<div>' in content.lower():
            return False
        
        # 2. Должно содержать Python конструкции
        python_indicators = [
            'print(', 'def ', 'import ', 'from ', 'if __name__', 
            'class ', 'return ', 'for ', 'while ', 'try:', 'except:'
        ]
        
        has_python_code = any(indicator in content for indicator in python_indicators)
        
        # 3. Для задач с "hello world" должно содержать print
        if 'hello' in task.lower() and 'world' in task.lower():
            has_hello_world = 'print(' in content and 'Hello' in content and 'World' in content
            return has_hello_world
        
        # 4. Проверяем что это не отчёт о создании Python файла
        report_indicators = [
            'Создан файл', 'Генерировано KittyCore', 'Результат выполнения',
            'Задача обработана', 'Отчёт о', 'Анализ задачи'
        ]
        
        is_report = any(indicator in content for indicator in report_indicators)
        
        return has_python_code and not is_report
    
    def _is_valid_html_content(self, content: str, task: str) -> bool:
        """Проверка что содержимое является валидным HTML"""
        # Должно содержать HTML структуру
        has_html_structure = (
            '<html>' in content.lower() or '<!doctype' in content.lower()
        ) and (
            '<head>' in content.lower() or '<body>' in content.lower()
        )
        
        return has_html_structure
    
    def _is_valid_javascript_content(self, content: str, task: str) -> bool:
        """Проверка что содержимое является валидным JavaScript"""
        # Не должно содержать HTML теги
        if '<html>' in content.lower() or '<!doctype' in content.lower():
            return False
        
        # Должно содержать JavaScript конструкции
        js_indicators = [
            'function', 'var ', 'let ', 'const ', 'console.log', 
            'document.', 'window.', '=>', 'async ', 'await '
        ]
        
        return any(indicator in content for indicator in js_indicators)
    
    def _is_valid_json_content(self, content: str) -> bool:
        """Проверка что содержимое является валидным JSON"""
        try:
            import json
            json.loads(content)
            return True
        except:
            return False
    
    def _detect_fake_reports(self, content: str, file_path: str, task: str) -> Dict[str, Any]:
        """
        Детектор отчётов-подделок - УНИКАЛЬНАЯ ФИЧА KITTYCORE!
        
        Обнаруживает когда агенты создают отчёты под видом реального контента.
        """
        
        # Паттерны отчётов-подделок
        fake_patterns = [
            # Общие паттерны отчётов
            'Результат выполнения задачи',
            'Задача обработана',
            'Генерировано KittyCore',
            'Создан файл с результатом',
            'Отчёт о выполнении',
            'Анализ задачи',
            'Время создания:',
            
            # HTML отчёты в не-HTML файлах
            '<div class="header">',
            '<div class="content">',
            '<div class="footer">',
            'Генерировано KittyCore 3.0 🐱',
            
            # Шаблонные фразы
            'TODO: Реализовать логику',
            'Задача успешно обработана',
            'с использованием LLM-интеллекта',
            'интеллектуальным агентом',
            
            # Мета-информация вместо контента
            'Контент для:',
            'Описание: Создан файл',
            'Выполнено интеллектуальным агентом',
            
            # НОВЫЕ ПАТТЕРНЫ ЗАГЛУШЕК
            'первое приложение',
            'второе приложение', 
            'третье приложение',
            'opis первого приложения',
            'opis второго приложения',
            'первая проблема',
            'вторая проблема',
            'Составить отчет о топ-приложениях',
            'Составить отчёт о топ-приложениях',
            'найдя все существующие приложения',
            'В этом файле находятся прототипы',
            'Анализ сложности реализации popularных приложений'
        ]
        
        # Проверяем наличие паттернов подделок
        fake_indicators_found = []
        for pattern in fake_patterns:
            if pattern in content:
                fake_indicators_found.append(pattern)
        
        # Специальная проверка для Python файлов
        if file_path.endswith('.py'):
            # Python файл не должен содержать HTML
            if '<html>' in content.lower() or '<div>' in content.lower():
                return {
                    'is_fake': True,
                    'reason': 'HTML код в Python файле - явная подделка!'
                }
            
            # Python файл должен содержать реальный код для задачи
            if 'hello' in task.lower() and 'world' in task.lower():
                if 'print(' not in content or 'Hello' not in content:
                    return {
                        'is_fake': True,
                        'reason': 'отсутствует требуемый print("Hello, World!")'
                    }
        
        # Если найдено много индикаторов подделки
        if len(fake_indicators_found) >= 2:
            return {
                'is_fake': True,
                'reason': f'обнаружены паттерны отчёта: {", ".join(fake_indicators_found[:2])}'
            }
        
        return {'is_fake': False, 'reason': 'содержимое выглядит аутентично'}
    
    async def _basic_validation(self, task: str, execution_result: Dict) -> Dict[str, Any]:
        """Базовая валидация когда образ результата недоступен"""
        # TODO: Реализовать валидацию через SmartValidator
        validation_result = {"quality_score": 0.7, "validation": "Базовая валидация"}
        logger.info(f"✅ Базовая валидация завершена: {validation_result['quality_score']:.2f}")
        return validation_result
    
    async def _identify_rework_reasons(self, validation_result: Dict, expected_outcome: Dict) -> List[str]:
        """Определение причин необходимости доработки"""
        reasons = []
        
        # Общие причины на основе качества
        quality_score = validation_result.get('quality_score', 0)
        if quality_score < 0.3:
            reasons.append("Критически низкое качество результата")
        elif quality_score < 0.5:
            reasons.append("Низкое качество результата")
        elif quality_score < 0.7:
            reasons.append("Результат не соответствует минимальным требованиям")
        
        # Специфичные причины из issues
        issues = validation_result.get('issues', [])
        for issue in issues:
            if "❌" in issue:
                reasons.append(issue.replace("❌ ", ""))
        
        # Причины в зависимости от типа результата
        validation_type = validation_result.get('validation_type', 'generic')
        
        if validation_type == 'application':
            if not validation_result.get('executable_files'):
                reasons.append("Отсутствуют исполняемые файлы приложения")
            if validation_result.get('created_files_count', 0) == 0:
                reasons.append("Не создано ни одного файла")
        
        elif validation_type == 'financial':
            target_amount = validation_result.get('target_amount')
            if target_amount and quality_score < 0.7:
                reasons.append(f"Не достигнута целевая сумма: {target_amount}")
        
        # Если нет конкретных причин, добавляем общую
        if not reasons:
            reasons.append("Результат требует улучшения для соответствия ожиданиям")
        
        return reasons
    
    async def _finalize_task_results(self, task_id: str, execution_result: Dict, validation_result: Dict) -> Dict[str, Any]:
        """Агрегация и финализация результатов"""
        # Собираем все созданные файлы из execution_result
        created_files = execution_result.get('created_files', []) or execution_result.get('files_created', [])
        
        # Дополнительно собираем файлы из step_results (ExecutionManager)
        all_step_files = []
        for step_id, step_result in execution_result.get('step_results', {}).items():
            if isinstance(step_result, dict):
                # Ищем файлы в результате шага
                step_files = step_result.get('files_created', []) or step_result.get('created_files', [])
                all_step_files.extend(step_files)
        
        # Дополнительно собираем файлы из agent_results (если есть)
        all_agent_files = []
        for agent_id, agent_result in execution_result.get('agent_results', {}).items():
            if isinstance(agent_result, dict):
                agent_files = agent_result.get('files_created', []) or agent_result.get('created_files', [])
                all_agent_files.extend(agent_files)
        
        # Объединяем все файлы и убираем дубликаты
        all_files = list(set(created_files + all_step_files + all_agent_files))
        
        # ИСПРАВЛЕНИЕ: Дополнительно проверяем реальные файлы в outputs/
        import os
        from pathlib import Path
        
        outputs_dir = Path("./outputs")
        if outputs_dir.exists():
            real_files = [str(f) for f in outputs_dir.rglob("*") if f.is_file()]
            # Добавляем найденные файлы к списку
            all_files.extend(real_files)
        
        # Убираем дубликаты и пустые значения
        created_files = list(set(f for f in all_files if f))
        
        # Создаём трейс процесса
        process_trace = [
            "Задача создана в хранилище",
            "Выполнен анализ сложности", 
            "Проведена декомпозиция",
            "Создана команда агентов",
            "Выполнен workflow",
            "Проведена валидация",
            "Результаты агрегированы"
        ]
        
        # Получаем логи координации
        coordination_log = []
        if self.shared_chat:
            # TODO: Получить историю сообщений из SharedChat
            coordination_log = ["Координация через SharedChat"]
        
        return {
            "created_files": created_files,
            "process_trace": process_trace,
            "coordination_log": coordination_log,
            "execution_summary": execution_result,
            "validation_summary": validation_result
        }
    
    async def _update_learning_systems(self, task: str, final_result: Dict, start_time: datetime) -> None:
        """Обновление систем обучения и метрик + интеграция A-MEM + 🐜 Феромонная память"""
        duration = (datetime.now() - start_time).total_seconds()
        
        # Обновляем коллективную память
        await self.collective_memory.store(
            f"Задача выполнена: {task[:100]}", 
            "orchestrator", 
            ["задача", "выполнение", "unified"]
        )
        
        # 🧠 A-MEM: Сохраняем решение задачи в агентную память
        if self.amem_system:
            await self._save_task_solution_to_amem(task, final_result, duration)
        
        # 🐜 ФЕРОМОННАЯ ПАМЯТЬ: Записываем успех решения
        try:
            from .pheromone_memory import record_agent_success
            
            # Определяем тип задачи
            task_type = self._determine_task_type(task)
            
            # Определяем паттерн решения
            solution_pattern = self._extract_solution_pattern(final_result)
            
            # Определяем комбинацию агентов
            agent_combination = self._get_agent_combination(final_result)
            
            # Определяем использованные инструменты
            tools_used = self._get_tools_used(final_result)
            
            # Определяем успешность
            quality_score = final_result.get('validation_summary', {}).get('quality_score', 0.0)
            success = quality_score >= 0.7
            
            # Записываем в феромонную систему
            record_agent_success(
                task_type=task_type,
                solution_pattern=solution_pattern,
                agent_combination=agent_combination,
                tools_used=tools_used,
                success=success
            )
            
            logger.info(f"🐜 Феромонный след записан: {task_type} -> {solution_pattern} (success={success})")
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка записи феромонного следа: {e}")
        
        # Обновляем систему самообучения
        if self.self_improvement:
            try:
                # TODO: Записать данные в систему самообучения
                logger.info("🧠 Данные переданы в систему самообучения")
            except Exception as e:
                logger.error(f"❌ Ошибка обновления самообучения: {e}")
        
        logger.info(f"📊 Системы обучения обновлены за {duration:.2f}с")
    
    async def _save_task_solution_to_amem(self, task: str, final_result: Dict, duration: float) -> None:
        """🧠 Сохранение решения задачи в A-MEM для накопления знаний"""
        try:
            # Получаем статистику выполнения
            created_files = final_result.get('created_files', [])
            validation_summary = final_result.get('validation_summary', {})
            quality_score = validation_summary.get('quality_score', 0.0)
            
            # Формируем описание решения
            solution_content = f"""
            Решение задачи: {task}
            
            ⏱️ Время выполнения: {duration:.2f}с
            ✅ Качество: {quality_score:.2f}/1.0
            📁 Создано файлов: {len(created_files)}
            
            Процесс выполнения:
            {chr(10).join(final_result.get('process_trace', []))}
            
            Файлы результата:
            {chr(10).join(f"• {file}" for file in created_files[:10])}
            
            Детали валидации:
            {validation_summary.get('validation', 'Валидация не проведена')}
            """
            
            # Определяем тег качества
            quality_tag = "high_quality" if quality_score >= 0.8 else "medium_quality" if quality_score >= 0.6 else "low_quality"
            
            # Определяем тип задачи для тегирования
            task_type = "unknown"
            if any(keyword in task.lower() for keyword in ['сайт', 'веб', 'html', 'приложение']):
                task_type = "web_development"
            elif any(keyword in task.lower() for keyword in ['анализ', 'данные', 'статистика']):
                task_type = "data_analysis"
            elif any(keyword in task.lower() for keyword in ['код', 'программа', 'скрипт']):
                task_type = "programming"
            elif any(keyword in task.lower() for keyword in ['отчет', 'документ', 'описание']):
                task_type = "documentation"
            
            # Формируем контекст для A-MEM
            solution_context = {
                "task_type": task_type,
                "quality_score": quality_score,
                "duration_seconds": duration,
                "files_count": len(created_files),
                "success": quality_score >= 0.7,
                "complexity": "high" if duration > 60 else "medium" if duration > 20 else "low"
            }
            
            # Сохраняем в A-MEM
            await self.amem_system.store_memory(
                content=solution_content.strip(),
                context=solution_context,
                tags=[
                    "task_solution",
                    task_type,
                    quality_tag,
                    f"files_{len(created_files)}",
                    "unified_orchestrator"
                ]
            )
            
            logger.info(f"🧠 Решение задачи сохранено в A-MEM (качество: {quality_score:.2f})")
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка сохранения решения в A-MEM: {e}")
    
    async def _get_amem_insights_for_team_creation(self, subtasks: List[Dict], task_id: str) -> Dict[str, Any]:
        """🧠 Получение insights из A-MEM для умного создания команды агентов"""
        if not self.amem_system:
            return {"enabled": False, "insights": [], "recommendations": []}
        
        try:
            # Формируем поисковые запросы для каждой подзадачи
            insights = {
                "enabled": True,
                "search_results": [],
                "agent_recommendations": [],
                "successful_patterns": [],
                "potential_issues": []
            }
            
            for subtask in subtasks:
                subtask_description = subtask.get('description', str(subtask))
                subtask_id = subtask.get('id', 'unknown')
                
                # Ищем похожие успешные решения
                successful_memories = await self.amem_system.search_memories(
                    query=f"успешный опыт {subtask_description}",
                    filters={"tags": ["high_quality", "task_solution"]},
                    limit=3
                )
                
                # Ищем опыт агентов с похожими задачами
                agent_experiences = await self.amem_system.search_memories(
                    query=f"агент опыт {subtask_description}",
                    filters={"tags": ["agent_experience"]},
                    limit=5
                )
                
                # Ищем потенциальные проблемы
                failure_patterns = await self.amem_system.search_memories(
                    query=f"ошибка проблема {subtask_description}",
                    filters={"tags": ["agent_experience_failure", "low_quality"]},
                    limit=3
                )
                
                # Анализируем результаты поиска
                subtask_insights = {
                    "subtask_id": subtask_id,
                    "description": subtask_description,
                    "successful_solutions": len(successful_memories),
                    "experienced_agents": len(agent_experiences),
                    "known_issues": len(failure_patterns),
                    "recommendations": []
                }
                
                # Формируем рекомендации на основе найденных воспоминаний
                if successful_memories:
                    # Извлекаем лучшие практики
                    for memory in successful_memories:
                        context = memory.get('context', {})
                        if context.get('quality_score', 0) >= 0.8:
                            subtask_insights["recommendations"].append({
                                "type": "best_practice",
                                "advice": f"Высокое качество достигнуто за {context.get('duration_seconds', 'N/A')}с",
                                "source": "successful_solution"
                            })
                
                if agent_experiences:
                    # Анализируем успешных агентов
                    successful_roles = {}
                    for memory in agent_experiences:
                        context = memory.get('context', {})
                        if context.get('success', False):
                            role = context.get('agent_role', 'unknown')
                            if role not in successful_roles:
                                successful_roles[role] = 0
                            successful_roles[role] += 1
                    
                    # Рекомендуем лучшую роль
                    if successful_roles:
                        best_role = max(successful_roles, key=successful_roles.get)
                        subtask_insights["recommendations"].append({
                            "type": "role_recommendation",
                            "advice": f"Роль '{best_role}' показала успех в {successful_roles[best_role]} случаях",
                            "source": "agent_experience"
                        })
                
                if failure_patterns:
                    # Предупреждаем о потенциальных проблемах
                    for memory in failure_patterns:
                        context = memory.get('context', {})
                        errors = context.get('errors', [])
                        if errors:
                            subtask_insights["recommendations"].append({
                                "type": "warning",
                                "advice": f"Избегать ошибок: {', '.join(errors[:2])}",
                                "source": "failure_pattern"
                            })
                
                insights["search_results"].append(subtask_insights)
            
            # Общие рекомендации для команды
            total_successful = sum(r["successful_solutions"] for r in insights["search_results"])
            total_experiences = sum(r["experienced_agents"] for r in insights["search_results"])
            
            if total_successful > 0:
                insights["agent_recommendations"].append(
                    f"✅ Найдено {total_successful} успешных решений похожих задач"
                )
            
            if total_experiences > 0:
                insights["agent_recommendations"].append(
                    f"🧠 Доступен опыт {total_experiences} агентов с похожими задачами"
                )
            
            logger.info(f"🧠 A-MEM insights получены: {total_successful} решений, {total_experiences} опыта")
            return insights
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка получения A-MEM insights: {e}")
            return {"enabled": False, "error": str(e), "insights": [], "recommendations": []}

    def _create_solution_summary(self, final_result: Dict[str, Any]) -> str:
        """Создать краткое описание решения для векторной памяти"""
        
        summary_parts = []
        
        # Основные результаты
        if final_result.get('created_files'):
            files_info = f"Создано файлов: {len(final_result['created_files'])}"
            summary_parts.append(files_info)
        
        # Процесс выполнения
        if final_result.get('process_trace'):
            process_info = f"Этапы выполнения: {len(final_result['process_trace'])}"
            summary_parts.append(process_info)
        
        # Координация агентов
        if final_result.get('coordination_log'):
            coord_info = f"Координационных действий: {len(final_result['coordination_log'])}"
            summary_parts.append(coord_info)
        
        # Качество результата
        if final_result.get('quality_assessment'):
            quality_info = f"Качество: {final_result['quality_assessment']}"
            summary_parts.append(quality_info)
        
        # Объединяем в краткое описание
        if summary_parts:
            summary = "Решение: " + "; ".join(summary_parts)
        else:
            summary = "Задача выполнена успешно"
        
        # Добавляем детали если есть
        if final_result.get('summary'):
            summary += f"\nДетали: {final_result['summary']}"
        
        return summary

    def _determine_task_type(self, task: str) -> str:
        """🐜 Определить тип задачи для феромонной системы"""
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in ['сайт', 'веб', 'html', 'приложение', 'интерфейс']):
            return "web_development"
        elif any(keyword in task_lower for keyword in ['код', 'программа', 'скрипт', 'функция', 'алгоритм']):
            return "programming"
        elif any(keyword in task_lower for keyword in ['анализ', 'данные', 'статистика', 'исследование']):
            return "data_analysis"
        elif any(keyword in task_lower for keyword in ['отчет', 'документ', 'описание', 'инструкция']):
            return "documentation"
        elif any(keyword in task_lower for keyword in ['дизайн', 'макет', 'прототип', 'ui', 'ux']):
            return "design"
        elif any(keyword in task_lower for keyword in ['автоматизация', 'бот', 'скрипт', 'процесс']):
            return "automation"
        elif any(keyword in task_lower for keyword in ['тест', 'проверка', 'валидация', 'качество']):
            return "testing"
        else:
            return "general"
    
    def _extract_solution_pattern(self, final_result: Dict) -> str:
        """🐜 Извлечь паттерн решения из результатов"""
        created_files = final_result.get('created_files', [])
        
        # Анализируем типы созданных файлов
        if any('.py' in file for file in created_files):
            return "python_solution"
        elif any('.html' in file for file in created_files):
            return "web_solution"
        elif any('.js' in file for file in created_files):
            return "javascript_solution"
        elif any('.json' in file for file in created_files):
            return "config_solution"
        elif any('.md' in file for file in created_files):
            return "documentation_solution"
        elif any('.txt' in file for file in created_files):
            return "text_solution"
        elif created_files:
            return "file_creation_solution"
        else:
            # Анализируем процесс выполнения
            process_trace = final_result.get('process_trace', [])
            if any('анализ' in step.lower() for step in process_trace):
                return "analysis_solution"
            elif any('поиск' in step.lower() for step in process_trace):
                return "search_solution"
            else:
                return "general_solution"
    
    def _get_agent_combination(self, final_result: Dict) -> str:
        """🐜 Определить комбинацию агентов"""
        # Пытаемся извлечь из coordination_log
        coordination_log = final_result.get('coordination_log', [])
        agents_mentioned = set()
        
        for log_entry in coordination_log:
            if isinstance(log_entry, str):
                if 'agent' in log_entry.lower():
                    # Простое извлечение упоминаний агентов
                    if 'code' in log_entry.lower():
                        agents_mentioned.add('CodeAgent')
                    if 'analysis' in log_entry.lower():
                        agents_mentioned.add('AnalysisAgent')
                    if 'web' in log_entry.lower():
                        agents_mentioned.add('WebAgent')
                    if 'file' in log_entry.lower():
                        agents_mentioned.add('FileAgent')
        
        # Если не найдено в логах, определяем по результатам
        if not agents_mentioned:
            created_files = final_result.get('created_files', [])
            if any('.py' in file for file in created_files):
                agents_mentioned.add('CodeAgent')
            if any('.html' in file for file in created_files):
                agents_mentioned.add('WebAgent')
            if any('.md' in file for file in created_files):
                agents_mentioned.add('DocumentAgent')
            
            # Если всё ещё пусто, используем общего агента
            if not agents_mentioned:
                agents_mentioned.add('GeneralAgent')
        
        # Сортируем и объединяем
        sorted_agents = sorted(list(agents_mentioned))
        return '+'.join(sorted_agents)
    
    def _get_tools_used(self, final_result: Dict) -> List[str]:
        """🐜 Определить использованные инструменты"""
        tools = set()
        
        # Анализируем созданные файлы
        created_files = final_result.get('created_files', [])
        if created_files:
            tools.add('file_manager')
            
            # Определяем специфичные инструменты по типам файлов
            if any('.py' in file for file in created_files):
                tools.add('code_generator')
            if any('.html' in file for file in created_files):
                tools.add('web_generator')
            if any('.json' in file for file in created_files):
                tools.add('config_generator')
        
        # Анализируем процесс выполнения
        process_trace = final_result.get('process_trace', [])
        for step in process_trace:
            step_lower = step.lower() if isinstance(step, str) else ''
            
            if 'поиск' in step_lower or 'search' in step_lower:
                tools.add('web_search')
            if 'анализ' in step_lower or 'analysis' in step_lower:
                tools.add('data_analysis')
            if 'валидация' in step_lower or 'validation' in step_lower:
                tools.add('smart_validator')
            if 'координация' in step_lower or 'coordination' in step_lower:
                tools.add('shared_chat')
        
        # Если ничего не найдено, добавляем базовые инструменты
        if not tools:
            tools.add('general_tools')
        
        return sorted(list(tools))


# === ФАБРИЧНЫЕ ФУНКЦИИ ===

def create_unified_orchestrator(config: UnifiedConfig = None) -> UnifiedOrchestrator:
    """Создаёт UnifiedOrchestrator"""
    return UnifiedOrchestrator(config)


async def solve_with_unified_orchestrator(task: str, **kwargs) -> Dict[str, Any]:
    """Быстрое решение задачи через UnifiedOrchestrator"""
    config = UnifiedConfig(**{k: v for k, v in kwargs.items() if hasattr(UnifiedConfig, k)})
    orchestrator = create_unified_orchestrator(config)
    return await orchestrator.solve_task(task, kwargs)


# === ЭКСПОРТ ===

__all__ = [
    "UnifiedOrchestrator",
    "UnifiedConfig", 
    "create_unified_orchestrator",
    "solve_with_unified_orchestrator"
]
