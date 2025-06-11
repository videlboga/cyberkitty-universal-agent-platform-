#!/usr/bin/env python3
"""
🧬 SelfImprovement - Система самообучения KittyCore 3.0

Ключевые особенности:
- Анализ производительности агентов
- Эволюция агентов на основе результатов  
- Оптимизация рабочих процессов
- Извлечение знаний из опыта
- Адаптация системы под задачи

Принцип: "Система становится умнее с каждой задачей" 🚀
"""

import json
import time
import hashlib
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import random
from enum import Enum

# === НОВЫЕ КОМПОНЕНТЫ ДЛЯ ПРОДВИНУТОЙ СИСТЕМЫ ОБРАТНОЙ СВЯЗИ ===

@dataclass
class FeedbackEntry:
    """Запись обратной связи"""
    agent_id: str
    task_id: str
    feedback_type: str  # 'success', 'failure', 'quality', 'performance'
    score: float  # 0.0 - 1.0
    context: Dict[str, Any]
    user_feedback: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class LearningPattern:
    """Паттерн обучения"""
    pattern_id: str
    description: str
    triggers: List[str]  # Что вызывает этот паттерн
    actions: List[str]   # Какие действия нужно предпринять
    success_rate: float
    usage_count: int = 0
    
class FeedbackLoop:
    """Современная система обратной связи для непрерывного обучения"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.feedback_history: List[FeedbackEntry] = []
        self.learning_patterns: Dict[str, LearningPattern] = {}
        self.performance_trends: Dict[str, List[float]] = {}
        self.quality_threshold = 0.7  # Минимальный порог качества
        
    async def record_feedback(self, task_id: str, feedback_type: str, 
                            score: float, context: Dict[str, Any],
                            user_feedback: Optional[str] = None):
        """Записать обратную связь"""
        
        feedback = FeedbackEntry(
            agent_id=self.agent_id,
            task_id=task_id,
            feedback_type=feedback_type,
            score=score,
            context=context,
            user_feedback=user_feedback
        )
        
        self.feedback_history.append(feedback)
        
        # Обновить тренды производительности
        if feedback_type not in self.performance_trends:
            self.performance_trends[feedback_type] = []
        self.performance_trends[feedback_type].append(score)
        
        # Ограничить историю трендов
        if len(self.performance_trends[feedback_type]) > 100:
            self.performance_trends[feedback_type] = self.performance_trends[feedback_type][-100:]
            
        # Автоматически обнаружить паттерны
        await self._detect_learning_patterns(feedback)
        
        logger.info(f"🔄 Записана обратная связь: {feedback_type}={score:.2f} для задачи {task_id}")
        
    async def _detect_learning_patterns(self, feedback: FeedbackEntry):
        """Автоматическое обнаружение паттернов обучения"""
        
        # Анализ последних 10 записей
        recent_feedback = self.feedback_history[-10:]
        
        if len(recent_feedback) < 5:
            return
            
        # Паттерн: Снижение качества
        if feedback.feedback_type == 'quality':
            recent_scores = [f.score for f in recent_feedback if f.feedback_type == 'quality']
            if len(recent_scores) >= 3:
                trend = sum(recent_scores[-3:]) / 3
                if trend < self.quality_threshold:
                    pattern_id = f"quality_degradation_{feedback.agent_id}"
                    if pattern_id not in self.learning_patterns:
                        self.learning_patterns[pattern_id] = LearningPattern(
                            pattern_id=pattern_id,
                            description="Снижение качества работы агента",
                            triggers=["low_quality_score", "user_complaints"],
                            actions=["retrain_model", "adjust_parameters", "review_data"],
                            success_rate=0.0
                        )
                        logger.warning(f"⚠️ Обнаружен паттерн снижения качества для агента {self.agent_id}")
        
        # Паттерн: Повторяющиеся ошибки
        error_contexts = [f.context.get('error_type') for f in recent_feedback 
                         if f.feedback_type == 'failure' and 'error_type' in f.context]
        
        if error_contexts:
            from collections import Counter
            error_counts = Counter(error_contexts)
            for error_type, count in error_counts.items():
                if count >= 3:  # Одна и та же ошибка 3+ раз
                    pattern_id = f"recurring_error_{error_type}"
                    if pattern_id not in self.learning_patterns:
                        self.learning_patterns[pattern_id] = LearningPattern(
                            pattern_id=pattern_id,
                            description=f"Повторяющаяся ошибка: {error_type}",
                            triggers=[f"error_type:{error_type}"],
                            actions=["create_error_handler", "update_training", "add_validation"],
                            success_rate=0.0
                        )
                        logger.warning(f"⚠️ Обнаружен паттерн повторяющихся ошибок: {error_type}")
    
    def get_improvement_recommendations(self) -> List[Dict[str, Any]]:
        """Получить рекомендации по улучшению"""
        
        recommendations = []
        
        # Анализ трендов производительности
        for metric, scores in self.performance_trends.items():
            if len(scores) >= 5:
                recent_avg = sum(scores[-5:]) / 5
                overall_avg = sum(scores) / len(scores)
                
                if recent_avg < overall_avg * 0.9:  # Снижение на 10%+
                    recommendations.append({
                        'type': 'performance_decline',
                        'metric': metric,
                        'severity': 'high' if recent_avg < overall_avg * 0.8 else 'medium',
                        'description': f"Снижение производительности в метрике {metric}",
                        'actions': [
                            'Проверить качество входных данных',
                            'Обновить модель агента',
                            'Пересмотреть параметры'
                        ]
                    })
        
        # Рекомендации на основе паттернов
        for pattern in self.learning_patterns.values():
            if pattern.usage_count > 0 and pattern.success_rate < 0.5:
                recommendations.append({
                    'type': 'pattern_based',
                    'pattern_id': pattern.pattern_id,
                    'severity': 'high',
                    'description': pattern.description,
                    'actions': pattern.actions
                })
        
        return recommendations
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Получить статистику обучения"""
        
        if not self.feedback_history:
            return {'total_feedback': 0, 'avg_score': 0.0, 'trends': {}}
        
        total_feedback = len(self.feedback_history)
        avg_score = sum(f.score for f in self.feedback_history) / total_feedback
        
        # Статистика по типам обратной связи
        feedback_by_type = {}
        for feedback in self.feedback_history:
            if feedback.feedback_type not in feedback_by_type:
                feedback_by_type[feedback.feedback_type] = []
            feedback_by_type[feedback.feedback_type].append(feedback.score)
        
        type_stats = {}
        for ftype, scores in feedback_by_type.items():
            type_stats[ftype] = {
                'count': len(scores),
                'avg_score': sum(scores) / len(scores),
                'trend': 'improving' if len(scores) >= 2 and scores[-1] > scores[0] else 'stable'
            }
        
        return {
            'total_feedback': total_feedback,
            'avg_score': avg_score,
            'feedback_types': type_stats,
            'patterns_detected': len(self.learning_patterns),
            'last_feedback': self.feedback_history[-1].timestamp.isoformat() if self.feedback_history else None
        }

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Метрика производительности агента"""
    name: str
    value: float
    timestamp: datetime
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context
        }

@dataclass
class ImprovementAction:
    """Действие по улучшению агента"""
    action_type: str  # 'prompt_optimization', 'tool_creation', 'parameter_tuning'
    description: str
    implementation: str  # Код или инструкции
    expected_improvement: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class PerformanceTracker:
    """Отслеживание производительности агента"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.metrics: List[PerformanceMetric] = []
        self.baseline_metrics: Dict[str, float] = {}
        
    def record_metric(self, name: str, value: float, context: Dict[str, Any] = None):
        """Записать метрику производительности"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            context=context or {}
        )
        self.metrics.append(metric)
        
        # Установить базовую метрику если её нет
        if name not in self.baseline_metrics:
            self.baseline_metrics[name] = value
            
        logger.info(f"📊 Метрика {name}: {value} (базовая: {self.baseline_metrics[name]})")
        
    def get_improvement_rate(self, metric_name: str, window_size: int = 10) -> float:
        """Получить скорость улучшения метрики"""
        recent_metrics = [m for m in self.metrics[-window_size:] if m.name == metric_name]
        
        if len(recent_metrics) < 2:
            return 0.0
            
        baseline = self.baseline_metrics.get(metric_name, recent_metrics[0].value)
        current = recent_metrics[-1].value
        
        return (current - baseline) / baseline if baseline != 0 else 0.0
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Получить сводку производительности"""
        summary = {}
        
        for metric_name in self.baseline_metrics.keys():
            improvement = self.get_improvement_rate(metric_name)
            recent_values = [m.value for m in self.metrics[-5:] if m.name == metric_name]
            
            summary[metric_name] = {
                'baseline': self.baseline_metrics[metric_name],
                'current': recent_values[-1] if recent_values else 0,
                'improvement_rate': improvement,
                'trend': 'improving' if improvement > 0.05 else 'stable' if improvement > -0.05 else 'declining'
            }
            
        return summary

class ToolCreator:
    """Автономное создание инструментов агентом"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.created_tools: List[Dict[str, Any]] = []
        
    def analyze_need_for_tool(self, task_context: Dict[str, Any]) -> Optional[str]:
        """Анализ необходимости создания нового инструмента"""
        
        # Простая эвристика для определения потребности в инструменте
        error_patterns = task_context.get('errors', [])
        repeated_tasks = task_context.get('repeated_tasks', [])
        
        if len(error_patterns) > 3:
            return f"error_handler_for_{hashlib.md5(str(error_patterns).encode()).hexdigest()[:8]}"
            
        if len(repeated_tasks) > 5:
            return f"automation_tool_for_{hashlib.md5(str(repeated_tasks).encode()).hexdigest()[:8]}"
            
        return None
        
    def create_tool(self, tool_name: str, purpose: str, implementation: str) -> Dict[str, Any]:
        """Создать новый инструмент"""
        
        tool = {
            'name': tool_name,
            'purpose': purpose,
            'implementation': implementation,
            'created_at': datetime.now().isoformat(),
            'usage_count': 0,
            'effectiveness_score': 0.0
        }
        
        self.created_tools.append(tool)
        logger.info(f"🛠️ Создан инструмент: {tool_name} для {purpose}")
        
        return tool
        
    def suggest_tool_improvements(self, tool_name: str) -> List[str]:
        """Предложить улучшения для существующего инструмента"""
        
        tool = next((t for t in self.created_tools if t['name'] == tool_name), None)
        if not tool:
            return []
            
        suggestions = []
        
        if tool['usage_count'] > 10 and tool['effectiveness_score'] < 0.7:
            suggestions.append("Оптимизировать алгоритм для повышения эффективности")
            
        if tool['usage_count'] > 50:
            suggestions.append("Добавить кэширование для ускорения работы")
            
        return suggestions

class SelfOptimizer:
    """Система самооптимизации агента"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.optimization_history: List[ImprovementAction] = []
        
    def analyze_performance_gaps(self, performance_summary: Dict[str, Any]) -> List[str]:
        """Анализ пробелов в производительности"""
        
        gaps = []
        
        for metric_name, data in performance_summary.items():
            if data['trend'] == 'declining':
                gaps.append(f"Снижение производительности в {metric_name}")
                
            if data['improvement_rate'] < 0.1:  # Менее 10% улучшения
                gaps.append(f"Медленное улучшение в {metric_name}")
                
        return gaps
        
    def generate_improvement_plan(self, gaps: List[str], context: Dict[str, Any]) -> List[ImprovementAction]:
        """Генерация плана улучшений"""
        
        actions = []
        
        for gap in gaps:
            if "снижение производительности" in gap.lower():
                action = ImprovementAction(
                    action_type="parameter_tuning",
                    description=f"Настройка параметров для исправления: {gap}",
                    implementation="Автоматическая настройка гиперпараметров",
                    expected_improvement=0.15,
                    timestamp=datetime.now()
                )
                actions.append(action)
                
            elif "медленное улучшение" in gap.lower():
                action = ImprovementAction(
                    action_type="prompt_optimization",
                    description=f"Оптимизация промптов для: {gap}",
                    implementation="Рефакторинг системных промптов",
                    expected_improvement=0.20,
                    timestamp=datetime.now()
                )
                actions.append(action)
                
        return actions
        
    def implement_improvement(self, action: ImprovementAction) -> bool:
        """Реализация улучшения"""
        
        try:
            logger.info(f"🔧 Реализация улучшения: {action.description}")
            
            # Здесь будет реальная реализация улучшений
            # Пока что просто логируем
            
            self.optimization_history.append(action)
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка при реализации улучшения: {e}")
            return False

class SelfImprovingAgent:
    """Саморазвивающийся агент"""
    
    def __init__(self, agent_id: str, base_agent: Any):
        self.agent_id = agent_id
        self.base_agent = base_agent
        
        # Компоненты самооценки
        self.performance_tracker = PerformanceTracker(agent_id)
        self.tool_creator = ToolCreator(agent_id)
        self.self_optimizer = SelfOptimizer(agent_id)
        
        # Настройки самооценки
        self.evaluation_interval = 10  # Каждые 10 задач
        self.task_counter = 0
        
        logger.info(f"🧠 Инициализирован саморазвивающийся агент: {agent_id}")
        
    def run_with_self_improvement(self, task: str, context: Dict[str, Any] = None) -> Any:
        """Выполнить задачу с самооценкой и улучшением"""
        
        start_time = time.time()
        context = context or {}
        
        try:
            # Выполнить основную задачу
            result = self.base_agent.run(task)
            
            # Записать метрики производительности
            execution_time = time.time() - start_time
            self.performance_tracker.record_metric(
                "execution_time", 
                execution_time,
                {"task": task, "success": True}
            )
            
            # Оценить качество результата (простая эвристика)
            quality_score = self._evaluate_result_quality(result, task)
            self.performance_tracker.record_metric(
                "quality_score",
                quality_score,
                {"task": task, "result_length": len(str(result))}
            )
            
            self.task_counter += 1
            
            # Периодическая самооценка и улучшение
            if self.task_counter % self.evaluation_interval == 0:
                self._perform_self_evaluation(context)
                
            return result
            
        except Exception as e:
            # Записать ошибку как метрику
            self.performance_tracker.record_metric(
                "error_rate",
                1.0,
                {"task": task, "error": str(e)}
            )
            
            # Проанализировать необходимость создания инструмента для обработки ошибок
            tool_name = self.tool_creator.analyze_need_for_tool({
                'errors': [str(e)],
                'task': task
            })
            
            if tool_name:
                self.tool_creator.create_tool(
                    tool_name,
                    f"Обработка ошибок типа: {type(e).__name__}",
                    f"try-except блок для {type(e).__name__}"
                )
                
            raise
            
    def _evaluate_result_quality(self, result: Any, task: str) -> float:
        """Простая оценка качества результата"""
        
        # Проверка на моковый ответ
        result_str = str(result)
        if "mock response" in result_str.lower() or "hello from kittycore" in result_str.lower():
            # Для моков возвращаем случайную вариацию вокруг базового значения
            return 0.4 + random.uniform(-0.1, 0.1)  # 0.3-0.5 диапазон
        
        # Базовая эвристика для реальных ответов
        if result is None:
            return 0.0
            
        # Длина ответа (не слишком короткий, не слишком длинный)
        length_score = min(len(result_str) / 100, 1.0) if len(result_str) < 1000 else 0.8
        
        # Наличие структуры (простая проверка)
        structure_score = 0.8 if any(char in result_str for char in ['\n', '.', ',']) else 0.5
        
        # Проверка на содержательность
        content_score = 0.9 if len(result_str.split()) > 10 else 0.6
        
        return (length_score + structure_score + content_score) / 3
        
    def _perform_self_evaluation(self, context: Dict[str, Any]):
        """Выполнить самооценку и улучшение"""
        
        logger.info(f"🔍 Выполнение самооценки агента {self.agent_id}")
        
        # Получить сводку производительности
        performance_summary = self.performance_tracker.get_performance_summary()
        
        # Проанализировать пробелы
        gaps = self.self_optimizer.analyze_performance_gaps(performance_summary)
        
        if gaps:
            logger.info(f"📉 Обнаружены пробелы в производительности: {gaps}")
            
            # Сгенерировать план улучшений
            improvement_plan = self.self_optimizer.generate_improvement_plan(gaps, context)
            
            # Реализовать улучшения
            for action in improvement_plan:
                success = self.self_optimizer.implement_improvement(action)
                if success:
                    logger.info(f"✅ Улучшение реализовано: {action.description}")
                    
        else:
            logger.info("✨ Производительность агента стабильна")
            
    def get_self_improvement_report(self) -> Dict[str, Any]:
        """Получить отчёт о самооценке"""
        
        return {
            'agent_id': self.agent_id,
            'task_count': self.task_counter,
            'performance_summary': self.performance_tracker.get_performance_summary(),
            'created_tools': len(self.tool_creator.created_tools),
            'optimizations_applied': len(self.self_optimizer.optimization_history),
            'last_evaluation': datetime.now().isoformat()
        }

# Фабрика для создания саморазвивающихся агентов
def create_self_improving_agent(agent_id: str, base_agent: Any) -> SelfImprovingAgent:
    """Создать саморазвивающегося агента"""
    return SelfImprovingAgent(agent_id, base_agent)

# Пример использования
if __name__ == "__main__":
    # Демонстрация системы самооценки
    
    class MockAgent:
        def run(self, task: str) -> str:
            return f"Результат для задачи: {task}"
    
    # Создать саморазвивающегося агента
    base_agent = MockAgent()
    smart_agent = create_self_improving_agent("demo_agent", base_agent)
    
    # Выполнить несколько задач для демонстрации
    for i in range(15):
        result = smart_agent.run_with_self_improvement(f"Задача {i+1}")
        print(f"Задача {i+1}: {result}")
        
    # Получить отчёт о самооценке
    report = smart_agent.get_self_improvement_report()
    print("\n📊 Отчёт о самооценке:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

@dataclass
class PerformanceMetrics:
    """Метрики производительности агента"""
    agent_id: str
    task_count: int = 0
    success_rate: float = 0.0
    avg_duration: float = 0.0
    efficiency_score: float = 0.0
    last_updated: datetime = None

class PerformanceAnalytics:
    """Аналитика производительности агентов"""
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.task_history: List[Dict] = []
    
    def record_task_result(self, agent_id: str, task: str, duration: float, success: bool):
        """Записать результат выполнения задачи"""
        if agent_id not in self.metrics:
            self.metrics[agent_id] = PerformanceMetrics(agent_id=agent_id)
        
        metrics = self.metrics[agent_id]
        metrics.task_count += 1
        
        # Обновляем успешность
        old_success_rate = metrics.success_rate
        metrics.success_rate = (old_success_rate * (metrics.task_count - 1) + (1.0 if success else 0.0)) / metrics.task_count
        
        # Обновляем среднее время
        old_avg = metrics.avg_duration
        metrics.avg_duration = (old_avg * (metrics.task_count - 1) + duration) / metrics.task_count
        
        # Вычисляем эффективность
        metrics.efficiency_score = metrics.success_rate * (1.0 / max(0.1, metrics.avg_duration))
        metrics.last_updated = datetime.now()
        
        # Сохраняем в историю
        self.task_history.append({
            "agent_id": agent_id,
            "task": task,
            "duration": duration,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })

    def get_top_performers(self, limit: int = 5) -> List[PerformanceMetrics]:
        """Получить топ агентов по производительности"""
        sorted_metrics = sorted(
            self.metrics.values(),
            key=lambda m: m.efficiency_score,
            reverse=True
        )
        return sorted_metrics[:limit]
    
    def get_improvement_suggestions(self, agent_id: str) -> List[str]:
        """Получить рекомендации по улучшению агента"""
        if agent_id not in self.metrics:
            return ["Недостаточно данных для анализа"]
        
        metrics = self.metrics[agent_id]
        suggestions = []
        
        if metrics.success_rate < 0.8:
            suggestions.append("Улучшить алгоритм решения задач")
        
        if metrics.avg_duration > 10.0:
            suggestions.append("Оптимизировать скорость выполнения")
        
        if metrics.task_count < 5:
            suggestions.append("Необходимо больше практики")
        
        return suggestions if suggestions else ["Агент работает отлично!"]

class AgentEvolution:
    """Эволюция агентов на основе производительности"""
    
    def __init__(self, analytics: PerformanceAnalytics):
        self.analytics = analytics
        self.evolution_history: List[Dict] = []
    
    def evolve_agent(self, agent_id: str) -> Dict[str, Any]:
        """Эволюционировать агента на основе его производительности"""
        if agent_id not in self.analytics.metrics:
            return {"status": "no_data", "message": "Недостаточно данных"}
        
        metrics = self.analytics.metrics[agent_id]
        suggestions = self.analytics.get_improvement_suggestions(agent_id)
        
        evolution = {
            "agent_id": agent_id,
            "before": {
                "success_rate": metrics.success_rate,
                "avg_duration": metrics.avg_duration,
                "efficiency": metrics.efficiency_score
            },
            "improvements": suggestions,
            "evolved_at": datetime.now().isoformat(),
            "status": "evolved"
        }
        
        self.evolution_history.append(evolution)
        return evolution 

class SelfImprovementEngine:
    """Основной движок самообучения"""
    
    def __init__(self):
        self.analytics = PerformanceAnalytics()
        self.evolution = AgentEvolution(self.analytics)

    async def record_task_execution(self, agent_id: str, task: str, duration: float, success: bool):
        """Записать выполнение задачи"""
        self.analytics.record_task_result(agent_id, task, duration, success)
        logger.info(f"📊 Записан результат задачи для агента {agent_id}: success={success}, duration={duration:.2f}s")

    async def auto_improve_agent(self, agent_id: str):
        """Автоматическое улучшение агента"""
        evolution_result = self.evolution.evolve_agent(agent_id)
        logger.info(f"🧬 Эволюция агента {agent_id}: {evolution_result}")
        return evolution_result

    def get_system_report(self) -> Dict[str, Any]:
        """Получить отчет о системе"""
        top_performers = self.analytics.get_top_performers()
        
        return {
            "top_performers": [asdict(performer) for performer in top_performers],
            "total_agents": len(self.analytics.metrics),
            "report_time": datetime.now().isoformat()
        }

# === СИСТЕМА АВТОМАТИЧЕСКОГО СОЗДАНИЯ ДАТАСЕТОВ ===

@dataclass
class DatasetExample:
    """Пример для датасета обучения"""
    input_data: Dict[str, Any]
    expected_output: Any
    actual_output: Any
    quality_score: float
    context: Dict[str, Any]
    timestamp: datetime
    
    def to_training_format(self) -> Dict[str, Any]:
        """Преобразовать в формат для обучения"""
        return {
            'input': self.input_data,
            'output': self.expected_output,
            'quality': self.quality_score,
            'context': self.context
        }

class AutoDatasetCreator:
    """Автоматическое создание датасетов из обратной связи"""
    
    def __init__(self, agent_id: str, min_quality_score: float = 0.8):
        self.agent_id = agent_id
        self.min_quality_score = min_quality_score
        self.high_quality_examples: List[DatasetExample] = []
        self.failure_examples: List[DatasetExample] = []
        self.edge_case_examples: List[DatasetExample] = []
        
    async def process_feedback_for_dataset(self, feedback: FeedbackEntry, 
                                         input_data: Dict[str, Any],
                                         actual_output: Any,
                                         expected_output: Any = None):
        """Обработать обратную связь для создания датасета"""
        
        # Создать пример
        example = DatasetExample(
            input_data=input_data,
            expected_output=expected_output or actual_output,
            actual_output=actual_output,
            quality_score=feedback.score,
            context=feedback.context,
            timestamp=feedback.timestamp
        )
        
        # Категоризировать пример
        if feedback.score >= self.min_quality_score:
            self.high_quality_examples.append(example)
            logger.info(f"✅ Добавлен высококачественный пример (score: {feedback.score:.2f})")
            
            # Ограничить размер датасета
            if len(self.high_quality_examples) > 1000:
                # Удалить самые старые примеры
                self.high_quality_examples = sorted(
                    self.high_quality_examples, 
                    key=lambda x: x.quality_score, 
                    reverse=True
                )[:800]
                
        elif feedback.score < 0.3:
            self.failure_examples.append(example)
            logger.warning(f"❌ Добавлен пример ошибки (score: {feedback.score:.2f})")
            
            # Ограничить размер
            if len(self.failure_examples) > 200:
                self.failure_examples = self.failure_examples[-150:]
                
        else:
            # Средние примеры могут быть edge cases
            self.edge_case_examples.append(example)
            
            if len(self.edge_case_examples) > 300:
                self.edge_case_examples = self.edge_case_examples[-200:]
    
    def get_few_shot_examples(self, max_examples: int = 5) -> List[Dict[str, Any]]:
        """Получить примеры для few-shot промптинга"""
        
        if not self.high_quality_examples:
            return []
        
        # Отсортировать по качеству и взять лучшие
        best_examples = sorted(
            self.high_quality_examples,
            key=lambda x: x.quality_score,
            reverse=True
        )[:max_examples]
        
        return [example.to_training_format() for example in best_examples]
    
    def create_training_dataset(self) -> Dict[str, Any]:
        """Создать полный датасет для обучения"""
        
        return {
            'agent_id': self.agent_id,
            'created_at': datetime.now().isoformat(),
            'high_quality_examples': [ex.to_training_format() for ex in self.high_quality_examples],
            'failure_examples': [ex.to_training_format() for ex in self.failure_examples],
            'edge_case_examples': [ex.to_training_format() for ex in self.edge_case_examples],
            'statistics': {
                'total_examples': len(self.high_quality_examples) + len(self.failure_examples) + len(self.edge_case_examples),
                'high_quality_count': len(self.high_quality_examples),
                'failure_count': len(self.failure_examples),
                'edge_case_count': len(self.edge_case_examples),
                'avg_quality_score': sum(ex.quality_score for ex in self.high_quality_examples) / len(self.high_quality_examples) if self.high_quality_examples else 0
            }
        }
    
    def get_dataset_statistics(self) -> Dict[str, Any]:
        """Получить статистику датасета"""
        
        total_examples = len(self.high_quality_examples) + len(self.failure_examples) + len(self.edge_case_examples)
        
        if total_examples == 0:
            return {'status': 'empty', 'total_examples': 0}
        
        # Анализ временных трендов
        all_examples = self.high_quality_examples + self.failure_examples + self.edge_case_examples
        recent_examples = [ex for ex in all_examples if (datetime.now() - ex.timestamp).days <= 7]
        
        return {
            'status': 'active',
            'total_examples': total_examples,
            'high_quality_ratio': len(self.high_quality_examples) / total_examples,
            'failure_ratio': len(self.failure_examples) / total_examples,
            'recent_examples_count': len(recent_examples),
            'avg_quality_overall': sum(ex.quality_score for ex in all_examples) / total_examples,
            'ready_for_training': len(self.high_quality_examples) >= 10,  # Минимум для обучения
            'last_update': max(ex.timestamp for ex in all_examples).isoformat() if all_examples else None
        }

# === СИСТЕМА REAL-TIME МОНИТОРИНГА И АДАПТАЦИИ ===

@dataclass
class AlertRule:
    """Правило для создания алертов"""
    rule_id: str
    name: str
    condition: str  # 'performance_drop', 'error_spike', 'quality_decline'
    threshold: float
    severity: str  # 'low', 'medium', 'high', 'critical'
    enabled: bool = True

@dataclass
class SystemAlert:
    """Системный алерт"""
    alert_id: str
    rule_id: str
    message: str
    severity: str
    agent_id: str
    data: Dict[str, Any]
    timestamp: datetime
    acknowledged: bool = False

class RealTimeMonitor:
    """Real-time мониторинг системы самообучения"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: List[SystemAlert] = []
        self.metrics_buffer: Dict[str, List[float]] = {}
        self.baseline_metrics: Dict[str, float] = {}
        self.monitoring_window = 10  # последние N измерений
        
        # Настроить базовые правила алертов
        self._setup_default_alert_rules()
    
    def _setup_default_alert_rules(self):
        """Настроить стандартные правила алертов"""
        
        self.alert_rules = {
            'performance_drop': AlertRule(
                rule_id='performance_drop',
                name='Снижение производительности',
                condition='performance_drop',
                threshold=0.15,  # 15% снижение
                severity='high'
            ),
            'error_spike': AlertRule(
                rule_id='error_spike',
                name='Всплеск ошибок',
                condition='error_spike', 
                threshold=0.3,  # 30% ошибок
                severity='critical'
            ),
            'quality_decline': AlertRule(
                rule_id='quality_decline',
                name='Снижение качества',
                condition='quality_decline',
                threshold=0.7,  # Качество ниже 70%
                severity='medium'
            )
        }
    
    async def record_metric(self, metric_name: str, value: float):
        """Записать метрику для мониторинга"""
        
        if metric_name not in self.metrics_buffer:
            self.metrics_buffer[metric_name] = []
            
        self.metrics_buffer[metric_name].append(value)
        
        # Ограничить размер буфера
        if len(self.metrics_buffer[metric_name]) > self.monitoring_window:
            self.metrics_buffer[metric_name] = self.metrics_buffer[metric_name][-self.monitoring_window:]
            
        # Установить базовую метрику
        if metric_name not in self.baseline_metrics:
            self.baseline_metrics[metric_name] = value
        else:
            # Постепенно обновлять базовую метрику (экспоненциальное сглаживание)
            alpha = 0.1
            self.baseline_metrics[metric_name] = (
                alpha * value + (1 - alpha) * self.baseline_metrics[metric_name]
            )
        
        # Проверить алерты
        await self._check_alerts(metric_name, value)
    
    async def _check_alerts(self, metric_name: str, current_value: float):
        """Проверить условия алертов"""
        
        if len(self.metrics_buffer[metric_name]) < 3:
            return  # Недостаточно данных
            
        recent_values = self.metrics_buffer[metric_name]
        baseline = self.baseline_metrics[metric_name]
        
        # Проверить каждое правило
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
                
            alert_triggered = False
            alert_data = {}
            
            if rule.condition == 'performance_drop':
                # Снижение производительности
                recent_avg = sum(recent_values[-3:]) / 3
                if baseline > 0 and (baseline - recent_avg) / baseline >= rule.threshold:
                    alert_triggered = True
                    alert_data = {
                        'baseline': baseline,
                        'current_avg': recent_avg,
                        'drop_percentage': (baseline - recent_avg) / baseline
                    }
                    
            elif rule.condition == 'error_spike':
                # Всплеск ошибок (для метрик ошибок)
                if 'error' in metric_name.lower() or 'failure' in metric_name.lower():
                    recent_avg = sum(recent_values[-3:]) / 3
                    if recent_avg >= rule.threshold:
                        alert_triggered = True
                        alert_data = {
                            'error_rate': recent_avg,
                            'threshold': rule.threshold
                        }
                        
            elif rule.condition == 'quality_decline':
                # Снижение качества
                if 'quality' in metric_name.lower():
                    recent_avg = sum(recent_values[-3:]) / 3
                    if recent_avg <= rule.threshold:
                        alert_triggered = True
                        alert_data = {
                            'quality_score': recent_avg,
                            'threshold': rule.threshold
                        }
            
            if alert_triggered:
                await self._create_alert(rule, alert_data)
    
    async def _create_alert(self, rule: AlertRule, data: Dict[str, Any]):
        """Создать алерт"""
        
        # Проверить, нет ли уже активного алерта для этого правила
        existing_alert = next(
            (alert for alert in self.active_alerts 
             if alert.rule_id == rule.rule_id and not alert.acknowledged),
            None
        )
        
        if existing_alert:
            return  # Алерт уже существует
            
        alert = SystemAlert(
            alert_id=f"alert_{rule.rule_id}_{int(time.time())}",
            rule_id=rule.rule_id,
            message=f"{rule.name}: {data}",
            severity=rule.severity,
            agent_id=self.agent_id,
            data=data,
            timestamp=datetime.now()
        )
        
        self.active_alerts.append(alert)
        logger.warning(f"🚨 АЛЕРТ [{rule.severity.upper()}]: {alert.message}")
        
        # Автоматические действия по алертам
        await self._handle_alert_actions(alert)
    
    async def _handle_alert_actions(self, alert: SystemAlert):
        """Автоматические действия по алертам"""
        
        if alert.severity == 'critical':
            # Критические алерты требуют немедленного внимания
            logger.critical(f"🔥 КРИТИЧЕСКИЙ АЛЕРТ для агента {self.agent_id}: {alert.message}")
            
        elif alert.severity == 'high':
            # Высокие алерты - запланировать проверку
            logger.error(f"⚠️ ВЫСОКИЙ АЛЕРТ для агента {self.agent_id}: {alert.message}")
            
    def acknowledge_alert(self, alert_id: str):
        """Подтвердить алерт"""
        
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                logger.info(f"✅ Алерт {alert_id} подтверждён")
                break
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Получить статус мониторинга"""
        
        active_alerts_count = len([a for a in self.active_alerts if not a.acknowledged])
        
        # Анализ трендов метрик
        metric_trends = {}
        for metric_name, values in self.metrics_buffer.items():
            if len(values) >= 3:
                recent_trend = 'stable'
                if values[-1] > values[-3] * 1.1:
                    recent_trend = 'improving'
                elif values[-1] < values[-3] * 0.9:
                    recent_trend = 'declining'
                    
                metric_trends[metric_name] = {
                    'trend': recent_trend,
                    'current': values[-1],
                    'baseline': self.baseline_metrics.get(metric_name, 0),
                    'buffer_size': len(values)
                }
        
        return {
            'agent_id': self.agent_id,
            'status': 'healthy' if active_alerts_count == 0 else 'issues_detected',
            'active_alerts': active_alerts_count,
            'total_alerts': len(self.active_alerts),
            'monitored_metrics': list(self.metrics_buffer.keys()),
            'metric_trends': metric_trends,
            'alert_rules_count': len(self.alert_rules),
            'last_check': datetime.now().isoformat()
        } 

# === ИНТЕГРИРОВАННЫЙ ДВИЖОК САМООБУЧЕНИЯ 3.0 ===

class SelfLearningEngine:
    """🧠 Современный движок самообучения с feedback loops и real-time мониторингом"""
    
    def __init__(self):
        # Основные компоненты
        self.feedback_loops: Dict[str, FeedbackLoop] = {}
        self.dataset_creators: Dict[str, AutoDatasetCreator] = {}
        self.monitors: Dict[str, RealTimeMonitor] = {}
        
        # Статистика системы
        self.total_feedback_processed = 0
        self.total_patterns_detected = 0
        self.total_improvements_made = 0
        self.system_health_score = 1.0
        
        logger.info("🚀 Инициализирован SelfLearningEngine 3.0")
    
    def get_or_create_agent_components(self, agent_id: str) -> tuple[FeedbackLoop, AutoDatasetCreator, RealTimeMonitor]:
        """Получить или создать компоненты для агента"""
        
        if agent_id not in self.feedback_loops:
            self.feedback_loops[agent_id] = FeedbackLoop(agent_id)
            self.dataset_creators[agent_id] = AutoDatasetCreator(agent_id)
            self.monitors[agent_id] = RealTimeMonitor(agent_id)
            logger.info(f"🔧 Созданы компоненты самообучения для агента {agent_id}")
        
        return (
            self.feedback_loops[agent_id],
            self.dataset_creators[agent_id], 
            self.monitors[agent_id]
        )
    
    async def record_agent_execution(self, agent_id: str, task_id: str, 
                                   input_data: Dict[str, Any], output: Any,
                                   execution_time: float, success: bool,
                                   quality_score: float = None,
                                   user_feedback: str = None):
        """🔄 Записать выполнение агента с полным контекстом"""
        
        feedback_loop, dataset_creator, monitor = self.get_or_create_agent_components(agent_id)
        
        # Определить тип обратной связи
        if not success:
            feedback_type = 'failure'
            score = 0.0
        elif quality_score is not None:
            feedback_type = 'quality'
            score = quality_score
        else:
            feedback_type = 'success'
            score = 1.0 if success else 0.0
        
        # Создать контекст
        context = {
            'execution_time': execution_time,
            'task_complexity': len(str(input_data)),  # Простая эвристика
            'output_length': len(str(output)),
            'timestamp': datetime.now().isoformat()
        }
        
        if not success and 'error' in str(output).lower():
            context['error_type'] = 'execution_error'
        
        # Записать обратную связь
        await feedback_loop.record_feedback(
            task_id=task_id,
            feedback_type=feedback_type,
            score=score,
            context=context,
            user_feedback=user_feedback
        )
        
        # Обновить датасет
        await dataset_creator.process_feedback_for_dataset(
            feedback=FeedbackEntry(
                agent_id=agent_id,
                task_id=task_id,
                feedback_type=feedback_type,
                score=score,
                context=context,
                user_feedback=user_feedback
            ),
            input_data=input_data,
            actual_output=output
        )
        
        # Мониторинг метрик
        await monitor.record_metric('success_rate', 1.0 if success else 0.0)
        await monitor.record_metric('execution_time', execution_time)
        if quality_score is not None:
            await monitor.record_metric('quality_score', quality_score)
        
        self.total_feedback_processed += 1
        
        # Обновить счетчик паттернов
        patterns_before = len(feedback_loop.learning_patterns)
        # patterns_after будет обновлен автоматически в feedback_loop
        
        logger.info(f"📝 Записано выполнение агента {agent_id}: {feedback_type}={score:.2f}")
    
    async def get_agent_improvement_plan(self, agent_id: str) -> Dict[str, Any]:
        """📊 Получить план улучшений для агента"""
        
        if agent_id not in self.feedback_loops:
            return {'status': 'no_data', 'message': 'Недостаточно данных для анализа'}
        
        feedback_loop = self.feedback_loops[agent_id]
        dataset_creator = self.dataset_creators[agent_id]
        monitor = self.monitors[agent_id]
        
        # Собрать рекомендации
        recommendations = feedback_loop.get_improvement_recommendations()
        
        # Статистика обучения
        learning_stats = feedback_loop.get_learning_statistics()
        
        # Статистика датасета
        dataset_stats = dataset_creator.get_dataset_statistics()
        
        # Статус мониторинга
        monitoring_status = monitor.get_monitoring_status()
        
        # Few-shot примеры для улучшения промптов
        few_shot_examples = dataset_creator.get_few_shot_examples(max_examples=3)
        
        return {
            'agent_id': agent_id,
            'status': 'analyzed',
            'recommendations': recommendations,
            'learning_statistics': learning_stats,
            'dataset_statistics': dataset_stats,
            'monitoring_status': monitoring_status,
            'few_shot_examples': few_shot_examples,
            'improvement_priority': self._calculate_improvement_priority(
                learning_stats, dataset_stats, monitoring_status
            ),
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_improvement_priority(self, learning_stats: Dict, dataset_stats: Dict, 
                                      monitoring_status: Dict) -> str:
        """Вычислить приоритет улучшений"""
        
        # Высокий приоритет
        if monitoring_status['active_alerts'] > 0:
            return 'high'
        
        if learning_stats.get('avg_score', 1.0) < 0.6:
            return 'high'
            
        # Средний приоритет
        if not dataset_stats.get('ready_for_training', False):
            return 'medium'
            
        if learning_stats.get('patterns_detected', 0) > 0:
            return 'medium'
        
        # Низкий приоритет
        return 'low'
    
    async def auto_improve_all_agents(self) -> Dict[str, Any]:
        """🔄 Автоматическое улучшение всех агентов"""
        
        improvements = {}
        total_improved = 0
        
        for agent_id in self.feedback_loops.keys():
            try:
                improvement_plan = await self.get_agent_improvement_plan(agent_id)
                
                if improvement_plan['status'] == 'analyzed':
                    priority = improvement_plan['improvement_priority']
                    
                    if priority in ['high', 'medium']:
                        # Выполнить автоматические улучшения
                        applied_improvements = await self._apply_auto_improvements(agent_id, improvement_plan)
                        improvements[agent_id] = {
                            'priority': priority,
                            'applied': applied_improvements,
                            'status': 'improved'
                        }
                        total_improved += 1
                    else:
                        improvements[agent_id] = {
                            'priority': priority,
                            'status': 'no_action_needed'
                        }
                        
            except Exception as e:
                logger.error(f"❌ Ошибка при улучшении агента {agent_id}: {e}")
                improvements[agent_id] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        self.total_improvements_made += total_improved
        
        return {
            'total_agents_analyzed': len(improvements),
            'total_agents_improved': total_improved,
            'improvements': improvements,
            'system_health': self._calculate_system_health(),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _apply_auto_improvements(self, agent_id: str, improvement_plan: Dict[str, Any]) -> List[str]:
        """Применить автоматические улучшения"""
        
        applied = []
        
        # Обновить few-shot примеры
        few_shot_examples = improvement_plan.get('few_shot_examples', [])
        if few_shot_examples:
            applied.append('updated_few_shot_examples')
            logger.info(f"✅ Обновлены few-shot примеры для агента {agent_id}")
        
        # Подтвердить алерты низкого приоритета
        monitor = self.monitors[agent_id]
        for alert in monitor.active_alerts:
            if alert.severity in ['low', 'medium'] and not alert.acknowledged:
                monitor.acknowledge_alert(alert.alert_id)
                applied.append(f'acknowledged_alert_{alert.rule_id}')
        
        return applied
    
    def _calculate_system_health(self) -> float:
        """Вычислить общее здоровье системы"""
        
        if not self.feedback_loops:
            return 1.0
        
        total_score = 0
        agent_count = 0
        
        for agent_id, feedback_loop in self.feedback_loops.items():
            stats = feedback_loop.get_learning_statistics()
            agent_score = stats.get('avg_score', 0.5)
            
            # Учесть активные алерты
            monitor = self.monitors.get(agent_id)
            if monitor:
                active_alerts = monitor.get_monitoring_status()['active_alerts']
                if active_alerts > 0:
                    agent_score *= 0.8  # Снизить оценку при наличии алертов
            
            total_score += agent_score
            agent_count += 1
        
        self.system_health_score = total_score / agent_count if agent_count > 0 else 1.0
        return self.system_health_score
    
    def get_system_overview(self) -> Dict[str, Any]:
        """📈 Получить обзор всей системы самообучения"""
        
        total_agents = len(self.feedback_loops)
        total_datasets = len(self.dataset_creators)
        total_monitoring = len(self.monitors)
        
        # Агрегированная статистика
        total_feedback = sum(len(fl.feedback_history) for fl in self.feedback_loops.values())
        total_patterns = sum(len(fl.learning_patterns) for fl in self.feedback_loops.values())
        total_alerts = sum(len(m.active_alerts) for m in self.monitors.values())
        
        # Статистика датасетов
        total_examples = sum(
            len(dc.high_quality_examples) + len(dc.failure_examples) + len(dc.edge_case_examples)
            for dc in self.dataset_creators.values()
        )
        
        return {
            'system_status': 'healthy' if self.system_health_score > 0.7 else 'needs_attention',
            'system_health_score': round(self.system_health_score, 3),
            'agents': {
                'total': total_agents,
                'with_feedback': len([fl for fl in self.feedback_loops.values() if fl.feedback_history]),
                'with_datasets': len([dc for dc in self.dataset_creators.values() if dc.high_quality_examples]),
                'monitored': total_monitoring
            },
            'feedback': {
                'total_processed': total_feedback,
                'patterns_detected': total_patterns,
                'active_alerts': total_alerts
            },
            'datasets': {
                'total_examples': total_examples,
                'agents_ready_for_training': len([
                    dc for dc in self.dataset_creators.values() 
                    if len(dc.high_quality_examples) >= 10
                ])
            },
            'performance': {
                'total_improvements_made': self.total_improvements_made,
                'avg_feedback_per_agent': round(total_feedback / total_agents, 1) if total_agents > 0 else 0
            },
            'last_updated': datetime.now().isoformat()
        } 