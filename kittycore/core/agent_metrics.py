"""
📊 Agent Metrics System - Система метрик агентов KittyCore 3.0

Отслеживание производительности агентов для улучшения качества результатов:
- ✅ Метрики выполнения задач
- ✅ Качество результатов
- ✅ Время выполнения  
- ✅ Ошибки и успехи
- ✅ Координация в команде

ЦЕЛЬ: Превратить агентов-халтурщиков в профессионалов! 🎯
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

# === ТИПЫ И ПЕРЕЧИСЛЕНИЯ ===

class TaskStatus(Enum):
    """Статусы выполнения задач"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"  
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class QualityScore(Enum):
    """Уровни качества результатов"""
    EXCELLENT = 5  # 0.9-1.0 - Отличный результат
    GOOD = 4       # 0.7-0.89 - Хороший результат  
    AVERAGE = 3    # 0.5-0.69 - Средний результат
    POOR = 2       # 0.3-0.49 - Плохой результат
    TERRIBLE = 1   # 0.0-0.29 - Ужасный результат

# === БАЗОВЫЕ СТРУКТУРЫ ДАННЫХ ===

@dataclass
class TaskMetric:
    """Метрики выполнения одной задачи"""
    task_id: str
    agent_id: str
    task_description: str
    status: TaskStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    quality_score: float = 0.0
    success_rate: float = 0.0
    artifacts_created: int = 0
    errors_count: int = 0
    retries_count: int = 0
    memory_usage_mb: float = 0.0
    llm_calls: int = 0
    tools_used: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    
    def complete_task(self, quality_score: float, artifacts: int = 0, errors: List[str] = None):
        """Завершить задачу с результатами"""
        self.end_time = datetime.now()
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        self.quality_score = quality_score
        self.success_rate = 1.0 if quality_score >= 0.7 else 0.0
        self.artifacts_created = artifacts
        self.errors_count = len(errors or [])
        self.error_messages = errors or []
        self.status = TaskStatus.COMPLETED if quality_score >= 0.3 else TaskStatus.FAILED

@dataclass  
class AgentPerformanceMetrics:
    """Совокупные метрики производительности агента"""
    agent_id: str
    agent_type: str
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_quality: float = 0.0
    average_duration: float = 0.0
    success_rate: float = 0.0
    total_artifacts: int = 0
    total_errors: int = 0
    total_llm_calls: int = 0
    preferred_tools: List[str] = field(default_factory=list)
    error_patterns: Dict[str, int] = field(default_factory=dict)
    quality_trend: List[float] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_from_task(self, task_metric: TaskMetric):
        """Обновить метрики на основе выполненной задачи"""
        self.total_tasks += 1
        
        if task_metric.status == TaskStatus.COMPLETED:
            self.completed_tasks += 1
        elif task_metric.status == TaskStatus.FAILED:
            self.failed_tasks += 1
            
        # Обновляем средние значения
        self.average_quality = self._update_average(
            self.average_quality, task_metric.quality_score, self.total_tasks
        )
        self.average_duration = self._update_average(
            self.average_duration, task_metric.duration_seconds, self.total_tasks  
        )
        
        self.success_rate = self.completed_tasks / self.total_tasks if self.total_tasks > 0 else 0.0
        self.total_artifacts += task_metric.artifacts_created
        self.total_errors += task_metric.errors_count
        self.total_llm_calls += task_metric.llm_calls
        
        # Обновляем инструменты и ошибки
        self.preferred_tools.extend(task_metric.tools_used)
        for error in task_metric.error_messages:
            self.error_patterns[error] = self.error_patterns.get(error, 0) + 1
            
        # Тренд качества (последние 10 задач)
        self.quality_trend.append(task_metric.quality_score)
        if len(self.quality_trend) > 10:
            self.quality_trend.pop(0)
            
        self.last_updated = datetime.now()
    
    def _update_average(self, current_avg: float, new_value: float, count: int) -> float:
        """Обновить скользящее среднее"""
        if count == 1:
            return new_value
        return ((current_avg * (count - 1)) + new_value) / count
    
    def get_quality_grade(self) -> QualityScore:
        """Получить оценку качества агента"""
        if self.average_quality >= 0.9:
            return QualityScore.EXCELLENT
        elif self.average_quality >= 0.7:
            return QualityScore.GOOD  
        elif self.average_quality >= 0.5:
            return QualityScore.AVERAGE
        elif self.average_quality >= 0.3:
            return QualityScore.POOR
        else:
            return QualityScore.TERRIBLE

# === СИСТЕМА СБОРА МЕТРИК ===

class MetricsCollector:
    """Центральный сборщик метрик агентов"""
    
    def __init__(self, storage_path: str = "metrics_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Хранилища метрик
        self.task_metrics: Dict[str, TaskMetric] = {}
        self.agent_metrics: Dict[str, AgentPerformanceMetrics] = {}
        self.team_metrics: Dict[str, Dict] = {}
        
        # Настройки
        self.auto_save_interval = 60  # секунд
        self.last_save = time.time()
        
        logger.info(f"📊 MetricsCollector инициализирован: {storage_path}")
    
    def start_task_tracking(self, task_id: str, agent_id: str, task_description: str) -> TaskMetric:
        """Начать отслеживание задачи"""
        task_metric = TaskMetric(
            task_id=task_id,
            agent_id=agent_id, 
            task_description=task_description,
            status=TaskStatus.PENDING,
            start_time=datetime.now()
        )
        
        self.task_metrics[task_id] = task_metric
        logger.info(f"📊 Начато отслеживание задачи {task_id} для агента {agent_id}")
        
        return task_metric
    
    def update_task_progress(self, task_id: str, status: TaskStatus, **kwargs):
        """Обновить прогресс задачи"""
        if task_id not in self.task_metrics:
            logger.warning(f"⚠️ Задача {task_id} не найдена в метриках")
            return
            
        task_metric = self.task_metrics[task_id]
        task_metric.status = status
        
        # Обновляем дополнительные поля
        for key, value in kwargs.items():
            if hasattr(task_metric, key):
                setattr(task_metric, key, value)
        
        logger.debug(f"📊 Обновлён статус задачи {task_id}: {status.value}")
    
    def complete_task(
        self, 
        task_id: str, 
        quality_score: float, 
        artifacts_created: int = 0,
        errors: List[str] = None,
        tools_used: List[str] = None,
        llm_calls: int = 0
    ):
        """Завершить отслеживание задачи"""
        if task_id not in self.task_metrics:
            logger.warning(f"⚠️ Задача {task_id} не найдена для завершения")
            return
            
        task_metric = self.task_metrics[task_id]
        task_metric.complete_task(quality_score, artifacts_created, errors or [])
        
        # Дополнительные данные
        if tools_used:
            task_metric.tools_used = tools_used
        task_metric.llm_calls = llm_calls
        
        # Обновляем метрики агента
        self._update_agent_metrics(task_metric)
        
        logger.info(f"✅ Задача {task_id} завершена. Качество: {quality_score:.2f}")
    
    def _update_agent_metrics(self, task_metric: TaskMetric):
        """Обновить совокупные метрики агента"""
        agent_id = task_metric.agent_id
        
        if agent_id not in self.agent_metrics:
            # Пытаемся определить тип агента
            agent_type = self._detect_agent_type(agent_id)
            self.agent_metrics[agent_id] = AgentPerformanceMetrics(
                agent_id=agent_id,
                agent_type=agent_type
            )
        
        self.agent_metrics[agent_id].update_from_task(task_metric)
        
        # Автосохранение
        if time.time() - self.last_save > self.auto_save_interval:
            asyncio.create_task(self.save_metrics())
    
    def _detect_agent_type(self, agent_id: str) -> str:
        """Определить тип агента по ID"""
        if "nova" in agent_id.lower():
            return "NovaAgent" 
        elif "artemis" in agent_id.lower():
            return "ArtemisAgent"
        elif "cipher" in agent_id.lower():
            return "CipherAgent"
        elif "ada" in agent_id.lower():
            return "AdaAgent"
        elif "analyst" in agent_id.lower():
            return "AnalystAgent"
        elif "developer" in agent_id.lower():
            return "DeveloperAgent"
        elif "tester" in agent_id.lower():
            return "TesterAgent"
        else:
            return "UnknownAgent"
    
    def get_agent_performance(self, agent_id: str) -> Optional[AgentPerformanceMetrics]:
        """Получить метрики производительности агента"""
        return self.agent_metrics.get(agent_id)
    
    def get_top_agents(self, limit: int = 5) -> List[AgentPerformanceMetrics]:
        """Получить топ агентов по качеству"""
        sorted_agents = sorted(
            self.agent_metrics.values(),
            key=lambda x: (x.average_quality, x.success_rate, -x.average_duration),
            reverse=True
        )
        return sorted_agents[:limit]
    
    def get_worst_agents(self, limit: int = 5) -> List[AgentPerformanceMetrics]:
        """Получить худших агентов (для улучшения)"""
        sorted_agents = sorted(
            self.agent_metrics.values(),
            key=lambda x: (x.average_quality, x.success_rate, x.average_duration)
        )
        return sorted_agents[:limit]
    
    async def save_metrics(self):
        """Сохранить метрики в файлы"""
        try:
            # Сохраняем метрики агентов
            agent_file = self.storage_path / "agent_metrics.json"
            agent_data = {}
            for agent_id, metrics in self.agent_metrics.items():
                # Преобразуем dataclass в словарь
                data = asdict(metrics)
                # Преобразуем datetime в строку
                data['last_updated'] = data['last_updated'].isoformat() if isinstance(data['last_updated'], datetime) else str(data['last_updated'])
                agent_data[agent_id] = data
            
            with open(agent_file, 'w', encoding='utf-8') as f:
                json.dump(agent_data, f, indent=2, ensure_ascii=False)
            
            # Сохраняем метрики задач
            tasks_file = self.storage_path / "task_metrics.json"
            tasks_data = {}
            for task_id, metric in self.task_metrics.items():
                data = asdict(metric)
                # Преобразуем enum в строку
                data['status'] = data['status'].value if hasattr(data['status'], 'value') else str(data['status'])
                # Преобразуем datetime в строку
                data['start_time'] = data['start_time'].isoformat() if isinstance(data['start_time'], datetime) else str(data['start_time'])
                if data['end_time']:
                    data['end_time'] = data['end_time'].isoformat() if isinstance(data['end_time'], datetime) else str(data['end_time'])
                tasks_data[task_id] = data
            
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
            
            self.last_save = time.time()
            logger.debug("💾 Метрики сохранены")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения метрик: {e}")

    def get_global_statistics(self) -> Dict[str, Any]:
        """Получить глобальную статистику системы"""
        total_tasks = sum(agent.total_tasks for agent in self.agent_metrics.values())
        total_agents = len(self.agent_metrics)
        
        if total_tasks == 0:
            avg_quality = 0.0
            success_rate = 0.0
        else:
            total_quality = sum(
                agent.average_quality * agent.total_tasks 
                for agent in self.agent_metrics.values()
            )
            avg_quality = total_quality / total_tasks
            
            successful_tasks = sum(
                agent.completed_tasks 
                for agent in self.agent_metrics.values()
            )
            success_rate = successful_tasks / total_tasks
        
        return {
            "total_agents": total_agents,
            "total_tasks": total_tasks,
            "average_quality": avg_quality,
            "success_rate": success_rate,
            "active_agents": len([a for a in self.agent_metrics.values() if a.total_tasks > 0]),
            "total_artifacts": sum(agent.total_artifacts for agent in self.agent_metrics.values()),
            "total_errors": sum(agent.total_errors for agent in self.agent_metrics.values())
        }

# === ГЛОБАЛЬНЫЙ СБОРЩИК МЕТРИК ===

# Единственный экземпляр сборщика метрик
_global_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Получить глобальный сборщик метрик"""
    global _global_metrics_collector
    if _global_metrics_collector is None:
        _global_metrics_collector = MetricsCollector()
    return _global_metrics_collector 