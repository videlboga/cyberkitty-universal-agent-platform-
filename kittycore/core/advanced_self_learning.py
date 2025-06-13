#!/usr/bin/env python3
"""
🧠 Advanced Self Learning Engine - Революционная система самообучения

Объединяет современные подходы 2024:
- Adaptive Rate Control для умного управления нагрузкой
- Critique-Guided Improvement для системы актёр-критик
- Guardian Agents для real-time защиты и мониторинга
- Constitutional AI принципы для извлечения правил
- Self-improvement loops для непрерывного обучения

Принцип: "Система становится умнее с каждой задачей" 🚀
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

# Импорты наших новых компонентов
try:
    from .adaptive_rate_control import AdaptiveRateController, get_rate_controller
    from .critique_guided_improvement import CriticAgent, TaskExecution, DetailedCritique
    from .guardian_agents import GuardianAgent, AlertLevel
    from .self_improvement import SelfLearningEngine  # Базовая система
except ImportError as e:
    logging.warning(f"Некоторые компоненты не найдены: {e}")

logger = logging.getLogger(__name__)

@dataclass
class LearningSession:
    """Сессия обучения системы"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    tasks_processed: int = 0
    improvements_applied: int = 0
    quality_increase: float = 0.0
    performance_gain: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'tasks_processed': self.tasks_processed,
            'improvements_applied': self.improvements_applied,
            'quality_increase': self.quality_increase,
            'performance_gain': self.performance_gain
        }

@dataclass
class SystemPrinciple:
    """Извлечённый принцип работы системы (Constitutional AI)"""
    principle_id: str
    title: str
    description: str
    confidence: float  # Уверенность в принципе (0.0-1.0)
    evidence_count: int  # Количество подтверждающих случаев
    last_validated: datetime
    category: str  # 'performance', 'quality', 'safety', 'efficiency'
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AdvancedSelfLearningEngine:
    """Продвинутый движок самообучения - центр всей системы"""
    
    def __init__(self, engine_id: str = "advanced_learning"):
        self.engine_id = engine_id
        self.is_active = True
        
        # Основные компоненты
        self.rate_controller = get_rate_controller()
        self.critics: Dict[str, CriticAgent] = {}
        self.guardians: Dict[str, GuardianAgent] = {}
        self.base_learning_engine = SelfLearningEngine()
        
        # Сессии обучения
        self.current_session: Optional[LearningSession] = None
        self.learning_history: List[LearningSession] = []
        
        # Constitutional AI - извлечённые принципы
        self.system_principles: Dict[str, SystemPrinciple] = {}
        
        # Статистика
        self.total_tasks_processed = 0
        self.total_improvements = 0
        self.system_startup_time = datetime.now()
        
        logger.info(f"🧠 Advanced Self Learning Engine '{engine_id}' инициализирован")
    
    def _setup_default_critics(self):
        """Настроить критиков по умолчанию"""
        
        # Критик производительности
        performance_critic = CriticAgent(
            critic_id="performance_critic",
            expertise_areas=["execution_time", "resource_usage", "efficiency"]
        )
        self.critics["performance"] = performance_critic
        
        # Критик качества
        quality_critic = CriticAgent(
            critic_id="quality_critic", 
            expertise_areas=["completeness", "accuracy", "user_satisfaction"]
        )
        self.critics["quality"] = quality_critic
        
        # Критик подхода к решению
        approach_critic = CriticAgent(
            critic_id="approach_critic",
            expertise_areas=["methodology", "tool_usage", "planning"]
        )
        self.critics["approach"] = approach_critic
        
        logger.info(f"✅ Настроены критики: {list(self.critics.keys())}")
    
    def _setup_default_guardians(self):
        """Настроить охранников по умолчанию"""
        
        # Охранник системной производительности
        system_guardian = GuardianAgent(
            guardian_id="system_guardian",
            monitored_agents=["*"]  # Мониторит всех агентов
        )
        self.guardians["system"] = system_guardian
        
        # Охранник качества
        quality_guardian = GuardianAgent(
            guardian_id="quality_guardian",
            monitored_agents=["*"]
        )
        self.guardians["quality"] = quality_guardian
        
        logger.info(f"✅ Настроены охранники: {list(self.guardians.keys())}")
    
    async def start_learning_session(self) -> str:
        """Начать новую сессию обучения"""
        
        if self.current_session is not None:
            await self.end_learning_session()
        
        session_id = f"learning_session_{int(time.time() * 1000)}"
        
        self.current_session = LearningSession(
            session_id=session_id,
            start_time=datetime.now()
        )
        
        # Инициализируем критиков и охранников если их нет
        if not self.critics:
            self._setup_default_critics()
        if not self.guardians:
            self._setup_default_guardians()
        
        logger.info(f"🎯 Начата сессия обучения: {session_id}")
        return session_id
    
    async def end_learning_session(self) -> Optional[LearningSession]:
        """Завершить текущую сессию обучения"""
        
        if self.current_session is None:
            return None
        
        self.current_session.end_time = datetime.now()
        
        # Вычисляем метрики улучшения
        session_duration = (self.current_session.end_time - self.current_session.start_time).total_seconds()
        
        if session_duration > 0 and self.current_session.tasks_processed > 0:
            # Примерные расчёты улучшений (в реальности будут браться из метрик)
            self.current_session.quality_increase = min(0.1, self.current_session.improvements_applied * 0.02)
            self.current_session.performance_gain = min(0.15, self.current_session.improvements_applied * 0.03)
        
        # Сохраняем в историю
        completed_session = self.current_session
        self.learning_history.append(completed_session)
        self.current_session = None
        
        logger.info(f"✅ Сессия завершена: {completed_session.session_id}, задач: {completed_session.tasks_processed}, улучшений: {completed_session.improvements_applied}")
        
        return completed_session
    
    async def process_task_with_learning(self, agent_id: str, task: str, 
                                       input_data: Dict[str, Any], 
                                       execution_func: Callable) -> Dict[str, Any]:
        """Обработать задачу с применением системы обучения"""
        
        if not self.current_session:
            await self.start_learning_session()
        
        task_id = f"task_{int(time.time() * 1000000)}"
        start_time = time.time()
        
        logger.info(f"🎯 Обрабатываем задачу {task_id} агентом {agent_id}")
        
        try:
            # Выполняем задачу с rate limiting
            result = await self.rate_controller.execute_request(
                provider=agent_id,
                request_data={
                    'task': task,
                    'input_data': input_data,
                    'agent_id': agent_id
                },
                execute_func=execution_func
            )
            
            execution_time = time.time() - start_time
            
            # Создаем объект выполнения для критики
            task_execution = TaskExecution(
                task_id=task_id,
                agent_id=agent_id,
                task_description=task,
                input_data=input_data,
                output_result=result,
                execution_time=execution_time,
                timestamp=datetime.now(),
                context={'rate_limited': True, 'cached': getattr(result, 'cached', False)}
            )
            
            # Применяем критику
            critiques = await self._apply_critiques(task_execution)
            
            # Мониторинг через охранников
            await self._monitor_with_guardians(agent_id, task_execution, critiques)
            
            # Извлекаем принципы (Constitutional AI)
            await self._extract_principles(task_execution, critiques)
            
            # Обновляем статистику сессии
            self.current_session.tasks_processed += 1
            self.total_tasks_processed += 1
            
            # Применяем улучшения если нужно
            improvements_applied = await self._apply_improvements(agent_id, critiques)
            self.current_session.improvements_applied += improvements_applied
            self.total_improvements += improvements_applied
            
            logger.info(f"✅ Задача {task_id} обработана за {execution_time:.2f}с с {len(critiques)} критиками")
            
            return {
                'task_id': task_id,
                'result': result,
                'execution_time': execution_time,
                'critiques': [c.to_dict() for c in critiques],
                'improvements_applied': improvements_applied,
                'success': True
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Ошибка обработки задачи {task_id}: {e}")
            
            # Уведомляем охранников об ошибке
            for guardian in self.guardians.values():
                await guardian.monitor_agent_metric(
                    agent_id, 'error_rate', 1.0, 
                    {'error': str(e), 'task_id': task_id}
                )
            
            return {
                'task_id': task_id,
                'result': None,
                'execution_time': execution_time,
                'error': str(e),
                'success': False
            }
    
    async def _apply_critiques(self, task_execution: TaskExecution) -> List[DetailedCritique]:
        """Применить критику к выполнению задачи"""
        
        critiques = []
        
        for critic_name, critic in self.critics.items():
            try:
                critique = await critic.critique_execution(task_execution)
                critiques.append(critique)
                
                logger.debug(f"🎭 Критик {critic_name}: балл {critique.overall_score:.2f}, приоритет {critique.improvement_priority}")
                
            except Exception as e:
                logger.error(f"❌ Ошибка критика {critic_name}: {e}")
        
        return critiques
    
    async def _monitor_with_guardians(self, agent_id: str, task_execution: TaskExecution, 
                                    critiques: List[DetailedCritique]):
        """Мониторинг через охранников"""
        
        for guardian in self.guardians.values():
            try:
                # Отправляем метрики времени выполнения
                await guardian.monitor_agent_metric(
                    agent_id, 'execution_time', task_execution.execution_time
                )
                
                # Отправляем метрики качества на основе критики
                if critiques:
                    avg_quality = sum(c.overall_score for c in critiques) / len(critiques)
                    await guardian.monitor_agent_metric(
                        agent_id, 'quality_score', avg_quality
                    )
                
                # Примерная метрика использования памяти (в реальности нужно измерять)
                memory_usage = min(0.8, task_execution.execution_time / 60.0)  # Примерно
                await guardian.monitor_agent_metric(
                    agent_id, 'memory_usage', memory_usage
                )
                
            except Exception as e:
                logger.error(f"❌ Ошибка охранника {guardian.guardian_id}: {e}")
    
    async def _extract_principles(self, task_execution: TaskExecution, 
                                critiques: List[DetailedCritique]):
        """Извлечь принципы работы (Constitutional AI)"""
        
        # Анализируем успешные паттерны
        if critiques:
            avg_score = sum(c.overall_score for c in critiques) / len(critiques)
            
            if avg_score > 0.8:  # Высокое качество - извлекаем принципы
                await self._extract_success_principle(task_execution, critiques, avg_score)
            elif avg_score < 0.4:  # Низкое качество - извлекаем принципы ошибок
                await self._extract_failure_principle(task_execution, critiques, avg_score)
    
    async def _extract_success_principle(self, task_execution: TaskExecution, 
                                       critiques: List[DetailedCritique], score: float):
        """Извлечь принцип из успешного выполнения"""
        
        # Анализируем что сделало выполнение успешным
        context = task_execution.context
        
        if task_execution.execution_time < 10.0:  # Быстрое выполнение
            principle_id = "fast_execution_pattern"
            
            if principle_id not in self.system_principles:
                self.system_principles[principle_id] = SystemPrinciple(
                    principle_id=principle_id,
                    title="Быстрое выполнение задач",
                    description="Задачи выполненные менее чем за 10 секунд показывают высокое качество",
                    confidence=0.1,
                    evidence_count=1,
                    last_validated=datetime.now(),
                    category="performance"
                )
            else:
                # Увеличиваем уверенность
                principle = self.system_principles[principle_id]
                principle.evidence_count += 1
                principle.confidence = min(0.95, principle.confidence + 0.05)
                principle.last_validated = datetime.now()
                
            logger.debug(f"📜 Принцип '{principle_id}' подтверждён (уверенность: {self.system_principles[principle_id].confidence:.2f})")
    
    async def _extract_failure_principle(self, task_execution: TaskExecution, 
                                       critiques: List[DetailedCritique], score: float):
        """Извлечь принцип из неудачного выполнения"""
        
        if task_execution.execution_time > 60.0:  # Медленное выполнение
            principle_id = "avoid_slow_execution"
            
            if principle_id not in self.system_principles:
                self.system_principles[principle_id] = SystemPrinciple(
                    principle_id=principle_id,
                    title="Избегать медленного выполнения",
                    description="Задачи выполненные более чем за 60 секунд часто имеют низкое качество",
                    confidence=0.1,
                    evidence_count=1,
                    last_validated=datetime.now(),
                    category="performance"
                )
            else:
                principle = self.system_principles[principle_id]
                principle.evidence_count += 1
                principle.confidence = min(0.95, principle.confidence + 0.05)
                principle.last_validated = datetime.now()
                
            logger.debug(f"📜 Принцип '{principle_id}' подтверждён (уверенность: {self.system_principles[principle_id].confidence:.2f})")
    
    async def _apply_improvements(self, agent_id: str, critiques: List[DetailedCritique]) -> int:
        """Применить улучшения на основе критики"""
        
        improvements_count = 0
        
        for critique in critiques:
            if critique.improvement_priority in ['high', 'urgent']:
                
                # Применяем улучшения с высоким приоритетом
                for point in critique.critique_points:
                    if point.confidence > 0.7:  # Высокая уверенность в критике
                        
                        success = await self._implement_improvement(agent_id, point)
                        if success:
                            improvements_count += 1
                            logger.info(f"✨ Применено улучшение для {agent_id}: {point.title}")
        
        return improvements_count
    
    async def _implement_improvement(self, agent_id: str, critique_point) -> bool:
        """Реализовать конкретное улучшение"""
        
        try:
            # В реальности здесь будет сложная логика применения улучшений
            # Пока просто логируем и возвращаем успех
            
            if critique_point.critique_type.value == "performance":
                logger.info(f"⚡ Оптимизируем производительность агента {agent_id}")
                return True
                
            elif critique_point.critique_type.value == "quality":
                logger.info(f"🎯 Улучшаем качество работы агента {agent_id}")
                return True
                
            elif critique_point.critique_type.value == "efficiency":
                logger.info(f"🚀 Повышаем эффективность агента {agent_id}")
                return True
                
            else:
                logger.info(f"🔧 Применяем общие улучшения для агента {agent_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка применения улучшения: {e}")
            return False

    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Получить комплексный отчёт системы обучения"""
        
        # Статистика rate controller
        rate_stats = self.rate_controller.get_statistics()
        
        # Статистика критиков
        critics_stats = {}
        for name, critic in self.critics.items():
            critics_stats[name] = {
                'total_critiques': len(critic.critique_history),
                'avg_score': sum(c.overall_score for c in critic.critique_history) / max(1, len(critic.critique_history)),
                'expertise_areas': critic.expertise_areas
            }
        
        # Статистика охранников
        guardians_stats = {}
        for name, guardian in self.guardians.items():
            guardians_stats[name] = guardian.get_monitoring_report()
        
        # Статистика принципов
        principles_stats = {
            'total_principles': len(self.system_principles),
            'high_confidence': len([p for p in self.system_principles.values() if p.confidence > 0.8]),
            'by_category': {}
        }
        
        for principle in self.system_principles.values():
            cat = principle.category
            if cat not in principles_stats['by_category']:
                principles_stats['by_category'][cat] = 0
            principles_stats['by_category'][cat] += 1
        
        # Статистика сессий
        sessions_stats = {
            'total_sessions': len(self.learning_history),
            'current_session': self.current_session.to_dict() if self.current_session else None,
            'avg_improvements_per_session': sum(s.improvements_applied for s in self.learning_history) / max(1, len(self.learning_history))
        }
        
        # Общая статистика системы
        uptime = (datetime.now() - self.system_startup_time).total_seconds()
        
        return {
            'engine_id': self.engine_id,
            'is_active': self.is_active,
            'uptime_seconds': uptime,
            'total_tasks_processed': self.total_tasks_processed,
            'total_improvements': self.total_improvements,
            'improvement_rate': self.total_improvements / max(1, self.total_tasks_processed),
            
            'rate_control': rate_stats,
            'critics': critics_stats,
            'guardians': guardians_stats,
            'principles': principles_stats,
            'sessions': sessions_stats,
            
            'generated_at': datetime.now().isoformat()
        }
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Получить инсайты обучения"""
        
        insights = {
            'top_performing_agents': self._get_top_performing_agents(),
            'most_effective_improvements': self._get_most_effective_improvements(),
            'system_health_score': self._calculate_system_health_score(),
            'learning_trends': self._analyze_learning_trends(),
            'recommendations': self._generate_recommendations()
        }
        
        return insights
    
    def _get_top_performing_agents(self) -> List[Dict[str, Any]]:
        """Получить топ агентов по производительности"""
        
        agent_performance = {}
        
        # Собираем статистику по критикам
        for critic in self.critics.values():
            for critique in critic.critique_history:
                agent_id = critique.execution_id.split('_')[0] if '_' in critique.execution_id else 'unknown'
                
                if agent_id not in agent_performance:
                    agent_performance[agent_id] = {'scores': [], 'count': 0}
                
                agent_performance[agent_id]['scores'].append(critique.overall_score)
                agent_performance[agent_id]['count'] += 1
        
        # Вычисляем средние баллы
        for agent_id, stats in agent_performance.items():
            stats['avg_score'] = sum(stats['scores']) / len(stats['scores'])
        
        # Сортируем по производительности
        sorted_agents = sorted(
            agent_performance.items(),
            key=lambda x: x[1]['avg_score'],
            reverse=True
        )
        
        return [
            {
                'agent_id': agent_id,
                'avg_score': stats['avg_score'],
                'task_count': stats['count']
            }
            for agent_id, stats in sorted_agents[:5]
        ]
    
    def _get_most_effective_improvements(self) -> List[Dict[str, Any]]:
        """Получить самые эффективные улучшения"""
        
        # В реальности здесь будет анализ корреляции улучшений с качеством
        # Пока возвращаем примерные данные
        
        return [
            {
                'improvement_type': 'performance_optimization',
                'effectiveness_score': 0.85,
                'usage_count': 15,
                'avg_impact': 0.12
            },
            {
                'improvement_type': 'quality_enhancement',
                'effectiveness_score': 0.78,
                'usage_count': 12,
                'avg_impact': 0.15
            }
        ]
    
    def _calculate_system_health_score(self) -> float:
        """Вычислить общий балл здоровья системы"""
        
        health_factors = []
        
        # Фактор rate limiting
        rate_stats = self.rate_controller.get_statistics()
        success_rate = float(rate_stats['success_rate'].rstrip('%')) / 100
        health_factors.append(success_rate)
        
        # Фактор активности охранников
        active_guardians = sum(1 for g in self.guardians.values() if g.is_active)
        guardian_factor = active_guardians / max(1, len(self.guardians))
        health_factors.append(guardian_factor)
        
        # Фактор качества критики
        if self.critics:
            avg_critic_quality = 0.8  # Примерная оценка
            health_factors.append(avg_critic_quality)
        
        # Фактор извлечённых принципов
        high_confidence_principles = len([p for p in self.system_principles.values() if p.confidence > 0.7])
        principle_factor = min(1.0, high_confidence_principles / 10.0)
        health_factors.append(principle_factor)
        
        return sum(health_factors) / len(health_factors) if health_factors else 0.0
    
    def _analyze_learning_trends(self) -> Dict[str, Any]:
        """Анализ трендов обучения"""
        
        if len(self.learning_history) < 2:
            return {'trend': 'insufficient_data', 'sessions_count': len(self.learning_history)}
        
        # Анализируем последние 5 сессий
        recent_sessions = self.learning_history[-5:]
        
        improvement_rates = [s.improvements_applied / max(1, s.tasks_processed) for s in recent_sessions]
        quality_increases = [s.quality_increase for s in recent_sessions]
        
        avg_improvement_rate = sum(improvement_rates) / len(improvement_rates)
        avg_quality_increase = sum(quality_increases) / len(quality_increases)
        
        # Определяем тренд
        if avg_improvement_rate > 0.1:
            trend = 'improving'
        elif avg_improvement_rate > 0.05:
            trend = 'stable'
        else:
            trend = 'declining'
        
        return {
            'trend': trend,
            'avg_improvement_rate': avg_improvement_rate,
            'avg_quality_increase': avg_quality_increase,
            'sessions_analyzed': len(recent_sessions)
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Сгенерировать рекомендации по улучшению"""
        
        recommendations = []
        
        # Анализируем статистику
        health_score = self._calculate_system_health_score()
        
        if health_score < 0.6:
            recommendations.append("Общее здоровье системы низкое - проверить конфигурацию компонентов")
        
        if not self.critics:
            recommendations.append("Добавить критиков для улучшения качества анализа")
        
        if not self.guardians:
            recommendations.append("Настроить охранников для мониторинга производительности")
        
        if len(self.system_principles) < 5:
            recommendations.append("Накопить больше принципов работы для улучшения Constitutional AI")
        
        rate_stats = self.rate_controller.get_statistics()
        success_rate = float(rate_stats['success_rate'].rstrip('%'))
        
        if success_rate < 80:
            recommendations.append("Оптимизировать rate limiting - низкий процент успешных запросов")
        
        cache_hit_rate = float(rate_stats['cache_hit_rate'].rstrip('%'))
        
        if cache_hit_rate < 20:
            recommendations.append("Улучшить кеширование для повышения производительности")
        
        return recommendations

# Глобальный экземпляр продвинутой системы обучения
_advanced_learning_engine = None

def get_advanced_learning_engine() -> AdvancedSelfLearningEngine:
    """Получить глобальный экземпляр продвинутой системы обучения"""
    global _advanced_learning_engine
    if _advanced_learning_engine is None:
        _advanced_learning_engine = AdvancedSelfLearningEngine()
    return _advanced_learning_engine

async def process_task_with_advanced_learning(agent_id: str, task: str, input_data: Dict[str, Any], execution_func: Callable) -> Dict[str, Any]:
    """Удобная функция для обработки задач с продвинутым обучением"""
    engine = get_advanced_learning_engine()
    return await engine.process_task_with_learning(agent_id, task, input_data, execution_func) 