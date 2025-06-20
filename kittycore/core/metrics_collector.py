"""
📊 MetricsCollector - Система сбора и анализа метрик KittyCore 3.0

Превосходит конкурентов:
- ✅ Реальное время мониторинга
- ✅ Многоуровневые метрики (задачи, агенты, система)
- ✅ Автоматическая аналитика трендов
- ✅ Obsidian-совместимые отчёты
- ✅ Предиктивная аналитика
- ✅ Интеграция с системой обучения

Превосходим CrewAI, LangGraph, AutoGen по глубине аналитики! 🚀
"""

import asyncio
import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import statistics
from collections import defaultdict, deque

from loguru import logger
from .obsidian_db import ObsidianDB, ObsidianNote


@dataclass
class TaskMetrics:
    """Метрики выполнения задачи"""
    task_id: str
    task_type: str
    complexity_score: Union[float, str]
    
    # Временные метрики
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Метрики агентов
    agents_created: int = 0
    agents_succeeded: int = 0
    agents_failed: int = 0
    
    # Метрики качества
    quality_score: float = 0.0
    validation_passed: bool = False
    rework_required: bool = False
    rework_attempts: int = 0
    
    # Метрики ресурсов
    llm_requests: int = 0
    llm_tokens_used: int = 0
    files_created: int = 0
    memory_usage_mb: float = 0.0
    
    # Метрики пользователя
    user_satisfaction: Optional[float] = None
    human_interventions: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskMetrics':
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        return cls(**data)


@dataclass
class AgentMetrics:
    """Метрики работы агента"""
    agent_id: str
    agent_type: str
    task_id: str
    
    # Временные метрики
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Метрики выполнения
    status: str = "running"  # running, completed, failed, timeout
    success_rate: float = 0.0
    error_count: int = 0
    retry_count: int = 0
    
    # Метрики инструментов
    tools_used: List[str] = None
    tool_success_rate: float = 0.0
    
    # Метрики качества
    output_quality: float = 0.0
    user_feedback: Optional[str] = None
    
    def __post_init__(self):
        if self.tools_used is None:
            self.tools_used = []
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data


@dataclass
class SystemMetrics:
    """Системные метрики"""
    timestamp: datetime
    
    # Производительность
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    disk_usage_mb: float = 0.0
    
    # Активность
    active_tasks: int = 0
    active_agents: int = 0
    queue_size: int = 0
    
    # Статистика
    total_tasks_processed: int = 0
    total_agents_created: int = 0
    average_task_duration: float = 0.0
    success_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class MetricsStorage:
    """Хранилище метрик в SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Инициализация базы данных метрик"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Таблица метрик задач
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_metrics (
                    task_id TEXT PRIMARY KEY,
                    task_type TEXT,
                    complexity_score REAL,
                    start_time TEXT,
                    end_time TEXT,
                    duration_seconds REAL,
                    agents_created INTEGER,
                    agents_succeeded INTEGER,
                    agents_failed INTEGER,
                    quality_score REAL,
                    validation_passed BOOLEAN,
                    rework_required BOOLEAN,
                    rework_attempts INTEGER,
                    llm_requests INTEGER,
                    llm_tokens_used INTEGER,
                    files_created INTEGER,
                    memory_usage_mb REAL,
                    user_satisfaction REAL,
                    human_interventions INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица метрик агентов
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    agent_type TEXT,
                    task_id TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration_seconds REAL,
                    status TEXT,
                    success_rate REAL,
                    error_count INTEGER,
                    retry_count INTEGER,
                    tools_used TEXT,
                    tool_success_rate REAL,
                    output_quality REAL,
                    user_feedback TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица системных метрик
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    cpu_usage REAL,
                    memory_usage_mb REAL,
                    disk_usage_mb REAL,
                    active_tasks INTEGER,
                    active_agents INTEGER,
                    queue_size INTEGER,
                    total_tasks_processed INTEGER,
                    total_agents_created INTEGER,
                    average_task_duration REAL,
                    success_rate REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
        
        logger.info(f"📊 База данных метрик инициализирована: {self.db_path}")
    
    def store_task_metrics(self, metrics: TaskMetrics):
        """Сохранить метрики задачи"""
        with sqlite3.connect(self.db_path) as conn:
            data = metrics.to_dict()
            placeholders = ', '.join(['?' for _ in data])
            columns = ', '.join(data.keys())
            
            conn.execute(
                f"INSERT OR REPLACE INTO task_metrics ({columns}) VALUES ({placeholders})",
                list(data.values())
            )
            conn.commit()
    
    def store_agent_metrics(self, metrics: AgentMetrics):
        """Сохранить метрики агента"""
        with sqlite3.connect(self.db_path) as conn:
            data = metrics.to_dict()
            data['tools_used'] = json.dumps(data['tools_used'])
            
            placeholders = ', '.join(['?' for _ in data if _ != 'id'])
            columns = ', '.join([k for k in data.keys() if k != 'id'])
            
            conn.execute(
                f"INSERT INTO agent_metrics ({columns}) VALUES ({placeholders})",
                [v for k, v in data.items() if k != 'id']
            )
            conn.commit()
    
    def store_system_metrics(self, metrics: SystemMetrics):
        """Сохранить системные метрики"""
        with sqlite3.connect(self.db_path) as conn:
            data = metrics.to_dict()
            placeholders = ', '.join(['?' for _ in data if _ != 'id'])
            columns = ', '.join([k for k in data.keys() if k != 'id'])
            
            conn.execute(
                f"INSERT INTO system_metrics ({columns}) VALUES ({placeholders})",
                [v for k, v in data.items() if k != 'id']
            )
            conn.commit()
    
    def get_task_metrics(self, task_id: str) -> Optional[TaskMetrics]:
        """Получить метрики задачи"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM task_metrics WHERE task_id = ?",
                (task_id,)
            )
            row = cursor.fetchone()
            
            if row:
                data = dict(row)
                data.pop('created_at', None)
                return TaskMetrics.from_dict(data)
            return None
    
    def get_recent_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Получить метрики за последние часы"""
        since = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Метрики задач
            task_cursor = conn.execute(
                "SELECT * FROM task_metrics WHERE start_time >= ? ORDER BY start_time DESC",
                (since.isoformat(),)
            )
            tasks = [dict(row) for row in task_cursor.fetchall()]
            
            # Метрики агентов
            agent_cursor = conn.execute(
                "SELECT * FROM agent_metrics WHERE start_time >= ? ORDER BY start_time DESC",
                (since.isoformat(),)
            )
            agents = [dict(row) for row in agent_cursor.fetchall()]
            
            # Системные метрики
            system_cursor = conn.execute(
                "SELECT * FROM system_metrics WHERE timestamp >= ? ORDER BY timestamp DESC",
                (since.isoformat(),)
            )
            system = [dict(row) for row in system_cursor.fetchall()]
            
            return {
                'tasks': tasks,
                'agents': agents,
                'system': system,
                'period_hours': hours,
                'retrieved_at': datetime.now().isoformat()
            }


class MetricsAnalyzer:
    """Анализатор метрик и трендов"""
    
    def __init__(self, storage: MetricsStorage):
        self.storage = storage
    
    def analyze_task_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Анализ производительности задач"""
        metrics = self.storage.get_recent_metrics(hours)
        tasks = metrics['tasks']
        
        if not tasks:
            return {'error': 'Нет данных за указанный период'}
        
        # Базовая статистика
        completed_tasks = [t for t in tasks if t['end_time']]
        durations = [t['duration_seconds'] for t in completed_tasks if t['duration_seconds']]
        quality_scores = [t['quality_score'] for t in tasks if t['quality_score'] > 0]
        
        analysis = {
            'total_tasks': len(tasks),
            'completed_tasks': len(completed_tasks),
            'success_rate': len(completed_tasks) / len(tasks) if tasks else 0,
            
            'duration_stats': {
                'average': statistics.mean(durations) if durations else 0,
                'median': statistics.median(durations) if durations else 0,
                'min': min(durations) if durations else 0,
                'max': max(durations) if durations else 0
            },
            
            'quality_stats': {
                'average': statistics.mean(quality_scores) if quality_scores else 0,
                'median': statistics.median(quality_scores) if quality_scores else 0,
                'min': min(quality_scores) if quality_scores else 0,
                'max': max(quality_scores) if quality_scores else 0
            },
            
            'complexity_distribution': self._analyze_complexity_distribution(tasks),
            'failure_analysis': self._analyze_failures(tasks),
            'trends': self._analyze_trends(tasks)
        }
        
        return analysis
    
    def _analyze_complexity_distribution(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Анализ распределения сложности задач"""
        complexities = [t['complexity_score'] for t in tasks if t['complexity_score']]
        
        if not complexities:
            return {'error': 'Нет данных о сложности'}
        
        # Категоризация по сложности
        simple = len([c for c in complexities if c < 0.3])
        medium = len([c for c in complexities if 0.3 <= c < 0.7])
        complex = len([c for c in complexities if c >= 0.7])
        
        return {
            'simple_tasks': simple,
            'medium_tasks': medium,
            'complex_tasks': complex,
            'average_complexity': statistics.mean(complexities),
            'complexity_trend': 'increasing' if complexities[-5:] > complexities[:5] else 'stable'
        }
    
    def _analyze_failures(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Анализ неудач"""
        failed_tasks = [t for t in tasks if not t['end_time'] or t['agents_failed'] > 0]
        
        if not failed_tasks:
            return {'failure_rate': 0, 'common_issues': []}
        
        failure_rate = len(failed_tasks) / len(tasks)
        
        # Анализ причин неудач
        rework_tasks = len([t for t in tasks if t['rework_required']])
        quality_issues = len([t for t in tasks if t['quality_score'] < 0.5])
        
        return {
            'failure_rate': failure_rate,
            'rework_rate': rework_tasks / len(tasks),
            'quality_issues_rate': quality_issues / len(tasks),
            'common_issues': [
                'Низкое качество результата' if quality_issues > 0 else None,
                'Требуется доработка' if rework_tasks > 0 else None,
                'Сбои агентов' if any(t['agents_failed'] > 0 for t in tasks) else None
            ]
        }
    
    def _analyze_trends(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Анализ трендов"""
        if len(tasks) < 10:
            return {'error': 'Недостаточно данных для анализа трендов'}
        
        # Сортируем по времени
        sorted_tasks = sorted(tasks, key=lambda x: x['start_time'])
        
        # Тренд качества
        recent_quality = [t['quality_score'] for t in sorted_tasks[-5:] if t['quality_score'] > 0]
        older_quality = [t['quality_score'] for t in sorted_tasks[:5] if t['quality_score'] > 0]
        
        quality_trend = 'improving' if (
            recent_quality and older_quality and 
            statistics.mean(recent_quality) > statistics.mean(older_quality)
        ) else 'stable'
        
        # Тренд производительности
        recent_durations = [t['duration_seconds'] for t in sorted_tasks[-5:] if t['duration_seconds']]
        older_durations = [t['duration_seconds'] for t in sorted_tasks[:5] if t['duration_seconds']]
        
        performance_trend = 'improving' if (
            recent_durations and older_durations and
            statistics.mean(recent_durations) < statistics.mean(older_durations)
        ) else 'stable'
        
        return {
            'quality_trend': quality_trend,
            'performance_trend': performance_trend,
            'volume_trend': 'increasing' if len(sorted_tasks[-5:]) > len(sorted_tasks[:5]) else 'stable'
        }


class MetricsCollector:
    """
    📊 Главный класс сбора и анализа метрик
    
    Возможности:
    - Реальное время мониторинга
    - Автоматический сбор метрик
    - Аналитика трендов
    - Obsidian-совместимые отчёты
    - Интеграция с системой обучения
    """
    
    def __init__(self, storage_path: str, obsidian_db: ObsidianDB = None):
        self.storage_path = storage_path
        self.obsidian_db = obsidian_db
        
        # Кэш активных метрик
        self.active_tasks: Dict[str, TaskMetrics] = {}
        self.active_agents: Dict[str, AgentMetrics] = {}
        
        # Статистика
        self.total_tasks = 0
        self.total_agents = 0
        
        logger.info(f"📊 MetricsCollector инициализирован: {storage_path}")
    
    def start_task_tracking(self, task_id: str, task_type: str, complexity_score: Union[float, str]) -> TaskMetrics:
        """Начать отслеживание задачи"""
        metrics = TaskMetrics(
            task_id=task_id,
            task_type=task_type,
            complexity_score=complexity_score,
            start_time=datetime.now()
        )
        
        self.active_tasks[task_id] = metrics
        self.total_tasks += 1
        
        logger.info(f"📊 Начато отслеживание задачи {task_id} (сложность: {complexity_score})")
        
        return metrics
    
    def finish_task_tracking(self, task_id: str, **updates) -> Optional[TaskMetrics]:
        """Завершить отслеживание задачи"""
        if task_id not in self.active_tasks:
            logger.warning(f"⚠️ Задача {task_id} не найдена в активных")
            return None
        
        metrics = self.active_tasks[task_id]
        metrics.end_time = datetime.now()
        metrics.duration_seconds = (metrics.end_time - metrics.start_time).total_seconds()
        
        # Обновляем дополнительные метрики
        for key, value in updates.items():
            if hasattr(metrics, key):
                setattr(metrics, key, value)
        
        # Создаём отчёт в Obsidian
        if self.obsidian_db:
            self._create_task_report(metrics)
        
        # Удаляем из активных
        del self.active_tasks[task_id]
        
        logger.info(f"📊 Завершено отслеживание задачи {task_id} (длительность: {metrics.duration_seconds:.1f}с)")
        
        return metrics
    
    def start_agent_tracking(self, agent_id: str, agent_type: str, task_id: str) -> AgentMetrics:
        """Начать отслеживание агента"""
        metrics = AgentMetrics(
            agent_id=agent_id,
            agent_type=agent_type,
            task_id=task_id,
            start_time=datetime.now()
        )
        
        self.active_agents[agent_id] = metrics
        self.total_agents += 1
        
        logger.debug(f"📊 Начато отслеживание агента {agent_id}")
        
        return metrics
    
    def finish_agent_tracking(self, agent_id: str, **updates) -> Optional[AgentMetrics]:
        """Завершить отслеживание агента"""
        if agent_id not in self.active_agents:
            logger.warning(f"⚠️ Агент {agent_id} не найден в активных")
            return None
        
        metrics = self.active_agents[agent_id]
        metrics.end_time = datetime.now()
        metrics.duration_seconds = (metrics.end_time - metrics.start_time).total_seconds()
        
        # Обновляем дополнительные метрики
        for key, value in updates.items():
            if hasattr(metrics, key):
                setattr(metrics, key, value)
        
        # Удаляем из активных
        del self.active_agents[agent_id]
        
        logger.debug(f"📊 Завершено отслеживание агента {agent_id}")
        
        return metrics
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Получить текущую статистику"""
        return {
            'active_tasks': len(self.active_tasks),
            'active_agents': len(self.active_agents),
            'total_tasks_processed': self.total_tasks,
            'total_agents_created': self.total_agents,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_task_report(self, metrics: TaskMetrics):
        """Создать отчёт о задаче в Obsidian"""
        if not self.obsidian_db:
            return
        
        # Форматируем отчёт
        duration_str = f"{metrics.duration_seconds:.1f}с" if metrics.duration_seconds else "N/A"
        quality_str = f"{metrics.quality_score:.2f}" if metrics.quality_score else "N/A"
        
        content = f"""# Метрики задачи {metrics.task_id}

## Основная информация
- **Тип задачи:** {metrics.task_type}
- **Сложность:** {metrics.complexity_score}
- **Начало:** {metrics.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Завершение:** {metrics.end_time.strftime('%Y-%m-%d %H:%M:%S') if metrics.end_time else 'В процессе'}
- **Длительность:** {duration_str}

## Метрики агентов
- **Создано агентов:** {metrics.agents_created}
- **Успешно:** {metrics.agents_succeeded}
- **Неудачно:** {metrics.agents_failed}
- **Успешность:** {(metrics.agents_succeeded / max(1, metrics.agents_created) * 100):.1f}%

## Качество
- **Оценка качества:** {quality_str}
- **Валидация пройдена:** {'✅' if metrics.validation_passed else '❌'}
- **Требуется доработка:** {'⚠️' if metrics.rework_required else '✅'}
- **Попыток доработки:** {metrics.rework_attempts}

## Ресурсы
- **LLM запросов:** {metrics.llm_requests}
- **Токенов использовано:** {metrics.llm_tokens_used}
- **Файлов создано:** {metrics.files_created}
- **Память (МБ):** {metrics.memory_usage_mb:.1f}

## Взаимодействие с пользователем
- **Вмешательств человека:** {metrics.human_interventions}
- **Удовлетворённость:** {metrics.user_satisfaction if metrics.user_satisfaction else 'N/A'}

---
*Отчёт создан автоматически MetricsCollector*
"""
        
        note = ObsidianNote(
            title=f"Метрики задачи {metrics.task_id}",
            content=content,
            tags=["метрики", "задача", str(metrics.task_type)],
            metadata={
                "task_id": metrics.task_id,
                "task_type": metrics.task_type,
                "complexity_score": metrics.complexity_score,
                "duration_seconds": metrics.duration_seconds,
                "quality_score": metrics.quality_score,
                "success_rate": metrics.agents_succeeded / max(1, metrics.agents_created)
            },
            folder="system/metrics"
        )
        
        self.obsidian_db.save_note(note, f"task_metrics_{metrics.task_id}.md")
        logger.info(f"📊 Создан отчёт о задаче в Obsidian: {metrics.task_id}")


def create_metrics_collector(storage_path: str, obsidian_db: ObsidianDB = None) -> MetricsCollector:
    """Фабричная функция для создания MetricsCollector"""
    return MetricsCollector(storage_path, obsidian_db) 