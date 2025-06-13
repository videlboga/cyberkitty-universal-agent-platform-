#!/usr/bin/env python3
"""
🎭 Critique-Guided Improvement (CGI) - Система "актёр-критик" 

Современный подход к самообучению:
- Актёр выполняет задачи
- Критик даёт детальную обратную связь на естественном языке  
- Система использует критику для улучшения решений
- Непрерывное обучение через reinforcement learning

Принцип: "Критика делает нас лучше" 🎯
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CritiqueType(Enum):
    """Типы критики"""
    PERFORMANCE = "performance"     # Производительность
    QUALITY = "quality"            # Качество результата
    APPROACH = "approach"          # Подход к решению
    EFFICIENCY = "efficiency"      # Эффективность
    USER_SATISFACTION = "user_satisfaction"  # Удовлетворённость пользователя

class CritiqueSeverity(Enum):
    """Серьёзность критики"""
    MINOR = "minor"        # Незначительные замечания
    MODERATE = "moderate"  # Умеренные проблемы
    MAJOR = "major"        # Серьёзные проблемы
    CRITICAL = "critical"  # Критические ошибки

@dataclass
class CritiquePoint:
    """Отдельная точка критики"""
    critique_type: CritiqueType
    severity: CritiqueSeverity
    title: str
    description: str
    evidence: str  # Конкретные примеры/доказательства
    suggestion: str  # Предложение по улучшению
    confidence: float  # Уверенность критика (0.0-1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.critique_type.value,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'evidence': self.evidence,
            'suggestion': self.suggestion,
            'confidence': self.confidence
        }

@dataclass
class TaskExecution:
    """Выполнение задачи актёром"""
    task_id: str
    agent_id: str
    task_description: str
    input_data: Dict[str, Any]
    output_result: Any
    execution_time: float
    timestamp: datetime
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'agent_id': self.agent_id,
            'task_description': self.task_description,
            'input_data': self.input_data,
            'output_result': self.output_result,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context
        }

@dataclass
class DetailedCritique:
    """Детальная критика от критика"""
    execution_id: str
    critic_id: str
    overall_score: float  # Общая оценка (0.0-1.0)
    critique_points: List[CritiquePoint]
    summary: str  # Краткое резюме
    improvement_priority: str  # 'low', 'medium', 'high', 'urgent'
    estimated_impact: float  # Ожидаемое влияние улучшений (0.0-1.0)
    timestamp: datetime
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'execution_id': self.execution_id,
            'critic_id': self.critic_id,
            'overall_score': self.overall_score,
            'critique_points': [cp.to_dict() for cp in self.critique_points],
            'summary': self.summary,
            'improvement_priority': self.improvement_priority,
            'estimated_impact': self.estimated_impact,
            'timestamp': self.timestamp.isoformat()
        }

class CriticAgent:
    """Агент-критик для оценки работы других агентов"""
    
    def __init__(self, critic_id: str, expertise_areas: List[str] = None):
        self.critic_id = critic_id
        self.expertise_areas = expertise_areas or []
        self.critique_history: List[DetailedCritique] = []
        self.evaluation_criteria = self._setup_evaluation_criteria()
        
        logger.info(f"🎭 Инициализирован критик {critic_id} с экспертизой: {self.expertise_areas}")
    
    def _setup_evaluation_criteria(self) -> Dict[str, Dict]:
        """Настроить критерии оценки"""
        return {
            'performance': {
                'execution_time': {'weight': 0.3, 'threshold': 30.0},  # секунды
                'success_rate': {'weight': 0.4, 'threshold': 0.8},
                'resource_usage': {'weight': 0.3, 'threshold': 0.7}
            },
            'quality': {
                'completeness': {'weight': 0.4, 'threshold': 0.9},
                'accuracy': {'weight': 0.4, 'threshold': 0.85},
                'relevance': {'weight': 0.2, 'threshold': 0.8}
            },
            'efficiency': {
                'steps_count': {'weight': 0.3, 'threshold': 10},
                'redundancy': {'weight': 0.4, 'threshold': 0.2},
                'optimization': {'weight': 0.3, 'threshold': 0.7}
            }
        }
    
    async def critique_execution(self, execution: TaskExecution) -> DetailedCritique:
        """Создать детальную критику выполнения задачи"""
        
        logger.info(f"🔍 Критик {self.critic_id} анализирует выполнение {execution.task_id}")
        
        # Анализ производительности
        performance_points = self._analyze_performance(execution)
        
        # Анализ качества
        quality_points = self._analyze_quality(execution)
        
        # Анализ подхода
        approach_points = self._analyze_approach(execution)
        
        # Анализ эффективности
        efficiency_points = self._analyze_efficiency(execution)
        
        # Объединяем все точки критики
        all_critique_points = performance_points + quality_points + approach_points + efficiency_points
        
        # Вычисляем общий балл
        overall_score = self._calculate_overall_score(all_critique_points)
        
        # Определяем приоритет улучшений
        improvement_priority = self._determine_improvement_priority(all_critique_points, overall_score)
        
        # Оцениваем влияние возможных улучшений
        estimated_impact = self._estimate_improvement_impact(all_critique_points)
        
        # Создаем краткое резюме
        summary = self._generate_summary(all_critique_points, overall_score)
        
        critique = DetailedCritique(
            execution_id=execution.task_id,
            critic_id=self.critic_id,
            overall_score=overall_score,
            critique_points=all_critique_points,
            summary=summary,
            improvement_priority=improvement_priority,
            estimated_impact=estimated_impact,
            timestamp=datetime.now()
        )
        
        self.critique_history.append(critique)
        logger.info(f"✅ Критика завершена: балл {overall_score:.2f}, приоритет {improvement_priority}")
        
        return critique
    
    def _analyze_performance(self, execution: TaskExecution) -> List[CritiquePoint]:
        """Анализ производительности"""
        points = []
        
        # Анализ времени выполнения
        if execution.execution_time > self.evaluation_criteria['performance']['execution_time']['threshold']:
            points.append(CritiquePoint(
                critique_type=CritiqueType.PERFORMANCE,
                severity=CritiqueSeverity.MODERATE,
                title="Медленное выполнение",
                description=f"Задача выполнялась {execution.execution_time:.1f}с, что превышает ожидаемое время {self.evaluation_criteria['performance']['execution_time']['threshold']}с",
                evidence=f"execution_time: {execution.execution_time:.2f}s",
                suggestion="Оптимизировать алгоритм, кешировать повторяющиеся операции, использовать параллельную обработку",
                confidence=0.9
            ))
        
        return points
    
    def _analyze_quality(self, execution: TaskExecution) -> List[CritiquePoint]:
        """Анализ качества результата"""
        points = []
        
        # Проверяем полноту результата
        if not execution.output_result or (isinstance(execution.output_result, str) and len(execution.output_result.strip()) < 50):
            points.append(CritiquePoint(
                critique_type=CritiqueType.QUALITY,
                severity=CritiqueSeverity.MAJOR,
                title="Неполный результат",
                description="Результат выполнения задачи кажется неполным или слишком коротким",
                evidence=f"output_length: {len(str(execution.output_result)) if execution.output_result else 0} chars",
                suggestion="Убедиться что задача выполнена полностью, добавить детали и объяснения",
                confidence=0.8
            ))
        
        return points
    
    def _analyze_approach(self, execution: TaskExecution) -> List[CritiquePoint]:
        """Анализ подхода к решению"""
        points = []
        
        # Анализируем контекст выполнения
        context = execution.context
        if 'tools_used' in context:
            tools_count = len(context['tools_used'])
            if tools_count > 10:
                points.append(CritiquePoint(
                    critique_type=CritiqueType.APPROACH,
                    severity=CritiqueSeverity.MINOR,
                    title="Избыточное использование инструментов",
                    description=f"Использовано {tools_count} инструментов, возможно слишком много",
                    evidence=f"tools_used: {context['tools_used']}",
                    suggestion="Планировать последовательность действий заранее, избегать лишних операций",
                    confidence=0.7
                ))
        
        return points
    
    def _analyze_efficiency(self, execution: TaskExecution) -> List[CritiquePoint]:
        """Анализ эффективности"""
        points = []
        
        # Соотношение времени к качеству результата
        time_quality_ratio = execution.execution_time / max(len(str(execution.output_result)), 1)
        if time_quality_ratio > 0.5:  # Больше 0.5 секунды на символ результата
            points.append(CritiquePoint(
                critique_type=CritiqueType.EFFICIENCY,
                severity=CritiqueSeverity.MODERATE,
                title="Низкая эффективность",
                description=f"Соотношение времени к объёму результата неоптимально: {time_quality_ratio:.3f}с/символ",
                evidence=f"time: {execution.execution_time:.2f}s, output_length: {len(str(execution.output_result))}",
                suggestion="Оптимизировать процесс, уменьшить избыточные операции",
                confidence=0.6
            ))
        
        return points
    
    def _calculate_overall_score(self, critique_points: List[CritiquePoint]) -> float:
        """Вычислить общий балл качества"""
        if not critique_points:
            return 1.0
        
        # Вычисляем штрафы по серьёзности
        penalty_weights = {
            CritiqueSeverity.MINOR: 0.05,
            CritiqueSeverity.MODERATE: 0.15,
            CritiqueSeverity.MAJOR: 0.3,
            CritiqueSeverity.CRITICAL: 0.5
        }
        
        total_penalty = 0
        for point in critique_points:
            penalty = penalty_weights[point.severity] * point.confidence
            total_penalty += penalty
        
        # Ограничиваем штраф максимумом 0.9 (минимальный балл 0.1)
        total_penalty = min(total_penalty, 0.9)
        
        return 1.0 - total_penalty
    
    def _determine_improvement_priority(self, critique_points: List[CritiquePoint], overall_score: float) -> str:
        """Определить приоритет улучшений"""
        
        if overall_score < 0.4:
            return "urgent"
        elif overall_score < 0.6:
            return "high"
        elif any(point.severity == CritiqueSeverity.MAJOR for point in critique_points):
            return "medium"
        else:
            return "low"
    
    def _estimate_improvement_impact(self, critique_points: List[CritiquePoint]) -> float:
        """Оценить ожидаемое влияние улучшений"""
        
        if not critique_points:
            return 0.0
        
        # Суммируем потенциальные улучшения
        total_impact = 0
        for point in critique_points:
            if point.severity == CritiqueSeverity.CRITICAL:
                total_impact += 0.4 * point.confidence
            elif point.severity == CritiqueSeverity.MAJOR:
                total_impact += 0.3 * point.confidence
            elif point.severity == CritiqueSeverity.MODERATE:
                total_impact += 0.2 * point.confidence
            else:  # MINOR
                total_impact += 0.1 * point.confidence
        
        return min(total_impact, 1.0)
    
    def _generate_summary(self, critique_points: List[CritiquePoint], overall_score: float) -> str:
        """Сгенерировать краткое резюме критики"""
        
        if not critique_points:
            return f"Отличная работа! Общий балл: {overall_score:.2f}. Замечаний нет."
        
        # Группируем по типам
        by_type = {}
        for point in critique_points:
            ptype = point.critique_type.value
            if ptype not in by_type:
                by_type[ptype] = []
            by_type[ptype].append(point)
        
        summary_parts = [f"Общий балл: {overall_score:.2f}."]
        
        for ptype, points in by_type.items():
            major_count = sum(1 for p in points if p.severity in [CritiqueSeverity.MAJOR, CritiqueSeverity.CRITICAL])
            minor_count = len(points) - major_count
            
            type_summary = f"{ptype.title()}: {major_count} серьёзных"
            if minor_count > 0:
                type_summary += f", {minor_count} незначительных"
            type_summary += " замечаний."
            
            summary_parts.append(type_summary)
        
        return " ".join(summary_parts) 