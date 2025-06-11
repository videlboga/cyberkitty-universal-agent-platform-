"""
🔍 СИСТЕМА БОГАТЫХ ОТЧЁТОВ KITTYCORE 3.0
Детальное логирование каждого действия каждого агента с полными метаданными
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

class ReportLevel(Enum):
    """Уровни детализации отчётов."""
    MINIMAL = "minimal"      # Только результат задачи
    BASIC = "basic"          # + основные действия агентов
    DETAILED = "detailed"    # + параметры и метаданные
    FULL = "full"           # + полный контекст и промежуточные состояния

@dataclass
class AgentAction:
    """Действие одного агента."""
    action_id: str
    agent_id: str
    agent_type: str
    agent_role: str
    
    # Временные метки
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    
    # Статус
    status: str = "running"  # running, success, error, stopped
    error_message: Optional[str] = None
    
    # Данные действия
    action_type: str = ""
    action_description: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    
    # Контекст (для DETAILED и FULL)
    context_before: Optional[Dict[str, Any]] = None
    context_after: Optional[Dict[str, Any]] = None
    
    # Метаданные
    llm_calls: List[Dict[str, Any]] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)

@dataclass
class TaskExecution:
    """Выполнение задачи с полными метаданными."""
    execution_id: str
    task_description: str
    user_id: Optional[str] = None
    
    # Временные метки
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    
    # Статус
    status: str = "running"  # running, completed, error, stopped
    final_result: Optional[str] = None
    error_message: Optional[str] = None
    
    # Анализ задачи
    task_analysis: Dict[str, Any] = field(default_factory=dict)
    task_decomposition: List[Dict[str, Any]] = field(default_factory=list)
    
    # Агенты и действия
    agents_created: List[Dict[str, Any]] = field(default_factory=list)
    agent_actions: List[AgentAction] = field(default_factory=list)
    
    # Результаты
    artifacts_created: List[str] = field(default_factory=list)
    memory_entries: List[Dict[str, Any]] = field(default_factory=list)
    
    # Метрики
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    quality_score: Optional[float] = None
    validation_results: Dict[str, Any] = field(default_factory=dict)

class RichReporter:
    """
    Система богатых отчётов KittyCore 3.0
    
    Отслеживает каждое действие каждого агента с полными метаданными
    """
    
    def __init__(self, report_level: ReportLevel = ReportLevel.DETAILED):
        self.report_level = report_level
        self.active_executions: Dict[str, TaskExecution] = {}
        
    def start_task_execution(self, execution_id: str, task_description: str, 
                           user_id: Optional[str] = None) -> TaskExecution:
        """Начинает отслеживание выполнения задачи"""
        execution = TaskExecution(
            execution_id=execution_id,
            task_description=task_description,
            user_id=user_id
        )
        
        self.active_executions[execution_id] = execution
        return execution
    
    def log_task_analysis(self, execution_id: str, analysis: Dict[str, Any]):
        """Логирует анализ задачи"""
        if execution_id in self.active_executions:
            self.active_executions[execution_id].task_analysis = analysis
    
    def log_task_decomposition(self, execution_id: str, subtasks: List[Dict[str, Any]]):
        """Логирует декомпозицию задачи"""
        if execution_id in self.active_executions:
            self.active_executions[execution_id].task_decomposition = subtasks
    
    def log_agent_created(self, execution_id: str, agent_info: Dict[str, Any]):
        """Логирует создание агента"""
        if execution_id in self.active_executions:
            self.active_executions[execution_id].agents_created.append({
                **agent_info,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
    
    def start_agent_action(self, execution_id: str, action_id: str, 
                          agent_id: str, agent_type: str, agent_role: str,
                          action_type: str, action_description: str,
                          input_data: Optional[Dict[str, Any]] = None,
                          context: Optional[Dict[str, Any]] = None) -> AgentAction:
        """Начинает отслеживание действия агента"""
        
        action = AgentAction(
            action_id=action_id,
            agent_id=agent_id,
            agent_type=agent_type,
            agent_role=agent_role,
            started_at=datetime.now(timezone.utc),
            action_type=action_type,
            action_description=action_description,
            input_data=input_data or {}
        )
        
        # Сохраняем контекст для DETAILED и FULL уровней
        if self.report_level in [ReportLevel.DETAILED, ReportLevel.FULL]:
            action.context_before = self._safe_copy(context or {})
        
        if execution_id in self.active_executions:
            self.active_executions[execution_id].agent_actions.append(action)
        
        return action
    
    def finish_agent_action(self, execution_id: str, action_id: str,
                           output_data: Optional[Dict[str, Any]] = None,
                           context: Optional[Dict[str, Any]] = None,
                           error: Optional[str] = None,
                           llm_calls: Optional[List[Dict[str, Any]]] = None,
                           tools_used: Optional[List[str]] = None,
                           files_created: Optional[List[str]] = None,
                           files_modified: Optional[List[str]] = None):
        """Завершает отслеживание действия агента"""
        
        if execution_id not in self.active_executions:
            return
        
        # Находим действие
        execution = self.active_executions[execution_id]
        action = None
        for a in reversed(execution.agent_actions):
            if a.action_id == action_id and a.finished_at is None:
                action = a
                break
        
        if not action:
            return
        
        # Завершаем действие
        action.finished_at = datetime.now(timezone.utc)
        action.duration_ms = (action.finished_at - action.started_at).total_seconds() * 1000
        
        if error:
            action.status = "error"
            action.error_message = error
        else:
            action.status = "success"
        
        # Сохраняем результаты
        action.output_data = output_data or {}
        action.llm_calls = llm_calls or []
        action.tools_used = tools_used or []
        action.files_created = files_created or []
        action.files_modified = files_modified or []
        
        # Сохраняем контекст после для DETAILED и FULL
        if self.report_level in [ReportLevel.DETAILED, ReportLevel.FULL]:
            action.context_after = self._safe_copy(context or {})
        
        # Обновляем общую статистику выполнения
        if files_created:
            execution.artifacts_created.extend(files_created)
    
    def finish_task_execution(self, execution_id: str, final_result: str,
                             error: Optional[str] = None,
                             quality_score: Optional[float] = None,
                             validation_results: Optional[Dict[str, Any]] = None):
        """Завершает отслеживание выполнения задачи"""
        
        if execution_id not in self.active_executions:
            return
        
        execution = self.active_executions[execution_id]
        execution.finished_at = datetime.now(timezone.utc)
        execution.duration_ms = (execution.finished_at - execution.started_at).total_seconds() * 1000
        
        if error:
            execution.status = "error"
            execution.error_message = error
        else:
            execution.status = "completed"
        
        execution.final_result = final_result
        execution.quality_score = quality_score
        execution.validation_results = validation_results or {}
        
        # Вычисляем метрики производительности
        execution.performance_metrics = self._calculate_metrics(execution)
    
    def _safe_copy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Безопасное копирование данных"""
        try:
            return json.loads(json.dumps(data, default=str))
        except:
            return {"_copy_error": "Failed to serialize data"}
    
    def _calculate_metrics(self, execution: TaskExecution) -> Dict[str, Any]:
        """Вычисляет метрики производительности"""
        actions = execution.agent_actions
        successful_actions = [a for a in actions if a.status == "success"]
        
        durations = [a.duration_ms for a in actions if a.duration_ms is not None]
        
        return {
            "total_actions": len(actions),
            "successful_actions": len(successful_actions),
            "success_rate": len(successful_actions) / len(actions) if actions else 0,
            "avg_action_duration_ms": sum(durations) / len(durations) if durations else 0,
            "max_action_duration_ms": max(durations) if durations else 0,
            "min_action_duration_ms": min(durations) if durations else 0,
            "total_artifacts": len(execution.artifacts_created),
            "agents_count": len(execution.agents_created),
            "llm_calls_total": sum(len(a.llm_calls) for a in actions),
            "tools_used_total": len(set(tool for a in actions for tool in a.tools_used))
        }
    
    def generate_detailed_report(self, execution_id: str) -> str:
        """Генерирует подробный отчёт для файла"""
        if execution_id not in self.active_executions:
            return "Execution not found"
        
        execution = self.active_executions[execution_id]
        
        report = [
            "# 🐱 ДЕТАЛЬНЫЙ ОТЧЁТ KITTYCORE 3.0",
            "=" * 60,
            "",
            f"## 📋 ИНФОРМАЦИЯ О ЗАДАЧЕ",
            f"**ID выполнения:** {execution.execution_id}",
            f"**Задача:** {execution.task_description}",
            f"**Пользователь:** {execution.user_id or 'Неизвестен'}",
            f"**Начато:** {execution.started_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Завершено:** {execution.finished_at.strftime('%Y-%m-%d %H:%M:%S UTC') if execution.finished_at else 'В процессе'}",
            f"**Длительность:** {execution.duration_ms:.0f}мс" if execution.duration_ms else "В процессе",
            f"**Статус:** {execution.status.upper()}",
            ""
        ]
        
        # Анализ задачи
        if execution.task_analysis:
            report.extend([
                "## 🔍 АНАЛИЗ ЗАДАЧИ",
                f"**Тип:** {execution.task_analysis.get('task_type', 'N/A')}",
                f"**Сложность:** {execution.task_analysis.get('complexity', 'N/A')}",
                f"**Домен:** {execution.task_analysis.get('domain', 'N/A')}",
                f"**Требует файлы:** {'Да' if execution.task_analysis.get('requires_files') else 'Нет'}",
                f"**Ожидаемый результат:** {execution.task_analysis.get('expected_output', 'N/A')}",
                ""
            ])
        
        # Декомпозиция задачи
        if execution.task_decomposition:
            report.extend([
                "## 📊 ДЕКОМПОЗИЦИЯ ЗАДАЧИ",
                f"**Всего подзадач:** {len(execution.task_decomposition)}",
                ""
            ])
            for i, subtask in enumerate(execution.task_decomposition, 1):
                report.extend([
                    f"### Подзадача {i}:",
                    f"- **Описание:** {subtask.get('description', 'N/A')}",
                    f"- **Тип:** {subtask.get('type', 'N/A')}",
                    f"- **Приоритет:** {subtask.get('priority', 'N/A')}",
                    ""
                ])
        
        # Созданные агенты
        if execution.agents_created:
            report.extend([
                "## 🤖 СОЗДАННЫЕ АГЕНТЫ",
                f"**Всего агентов:** {len(execution.agents_created)}",
                ""
            ])
            for agent in execution.agents_created:
                report.extend([
                    f"### Агент: {agent.get('type', 'Unknown')}",
                    f"- **Роль:** {agent.get('role', 'N/A')}",
                    f"- **Создан:** {agent.get('created_at', 'N/A')}",
                    f"- **Специализация:** {agent.get('specialization', 'N/A')}",
                    ""
                ])
        
        # Действия агентов
        if execution.agent_actions:
            report.extend([
                "## ⚡ ДЕЙСТВИЯ АГЕНТОВ",
                f"**Всего действий:** {len(execution.agent_actions)}",
                ""
            ])
            
            for action in execution.agent_actions:
                status_emoji = "✅" if action.status == "success" else "❌" if action.status == "error" else "⏳"
                
                report.extend([
                    f"### {status_emoji} {action.action_type}: {action.action_description}",
                    f"- **Агент:** {action.agent_type} ({action.agent_role})",
                    f"- **Начато:** {action.started_at.strftime('%H:%M:%S')}",
                    f"- **Завершено:** {action.finished_at.strftime('%H:%M:%S') if action.finished_at else 'В процессе'}",
                    f"- **Длительность:** {action.duration_ms:.0f}мс" if action.duration_ms else "В процессе",
                    f"- **Статус:** {action.status.upper()}",
                ])
                
                if action.error_message:
                    report.append(f"- **Ошибка:** {action.error_message}")
                
                if action.tools_used:
                    report.append(f"- **Инструменты:** {', '.join(action.tools_used)}")
                
                if action.files_created:
                    report.append(f"- **Создано файлов:** {', '.join(action.files_created)}")
                
                if action.llm_calls:
                    report.append(f"- **LLM вызовов:** {len(action.llm_calls)}")
                
                report.append("")
        
        # Метрики производительности
        if execution.performance_metrics:
            metrics = execution.performance_metrics
            report.extend([
                "## 📈 МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ",
                f"**Успешность:** {metrics.get('success_rate', 0):.1%}",
                f"**Среднее время действия:** {metrics.get('avg_action_duration_ms', 0):.0f}мс",
                f"**Максимальное время:** {metrics.get('max_action_duration_ms', 0):.0f}мс",
                f"**Создано артефактов:** {metrics.get('total_artifacts', 0)}",
                f"**Всего LLM вызовов:** {metrics.get('llm_calls_total', 0)}",
                f"**Уникальных инструментов:** {metrics.get('tools_used_total', 0)}",
                ""
            ])
        
        # Артефакты
        if execution.artifacts_created:
            report.extend([
                "## 📁 СОЗДАННЫЕ АРТЕФАКТЫ",
                ""
            ])
            for artifact in execution.artifacts_created:
                report.append(f"- {artifact}")
            report.append("")
        
        # Результат
        if execution.final_result:
            report.extend([
                "## 🎯 ФИНАЛЬНЫЙ РЕЗУЛЬТАТ",
                execution.final_result,
                ""
            ])
        
        # Оценка качества
        if execution.quality_score is not None:
            report.extend([
                "## ⭐ ОЦЕНКА КАЧЕСТВА",
                f"**Балл качества:** {execution.quality_score:.2f}/1.0",
                ""
            ])
        
        return "\n".join(report)
    
    def generate_ui_summary(self, execution_id: str) -> str:
        """Генерирует краткий отчёт для UI"""
        if execution_id not in self.active_executions:
            return "Выполнение не найдено"
        
        execution = self.active_executions[execution_id]
        
        # Краткая информация
        duration = f"{execution.duration_ms:.0f}мс" if execution.duration_ms else "В процессе"
        status_emoji = "✅" if execution.status == "completed" else "❌" if execution.status == "error" else "⏳"
        
        summary = [
            f"{status_emoji} **{execution.task_description}**",
            f"⏱️ {duration} | 🤖 {len(execution.agents_created)} агентов | ⚡ {len(execution.agent_actions)} действий | 📁 {len(execution.artifacts_created)} файлов"
        ]
        
        if execution.quality_score is not None:
            summary.append(f"⭐ Качество: {execution.quality_score:.2f}")
        
        return "\n".join(summary)

# Глобальный экземпляр reporter
_global_reporter = None

def get_rich_reporter() -> RichReporter:
    """Получить глобальный экземпляр rich reporter"""
    global _global_reporter
    if _global_reporter is None:
        _global_reporter = RichReporter()
    return _global_reporter

def set_report_level(level: ReportLevel):
    """Установить уровень детализации отчётов"""
    global _global_reporter
    if _global_reporter is None:
        _global_reporter = RichReporter(level)
    else:
        _global_reporter.report_level = level 