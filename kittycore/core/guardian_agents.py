#!/usr/bin/env python3
"""
👮 Guardian Agents - Система защиты и мониторинга

Современные охранные агенты:
- Real-time мониторинг качества работы агентов
- Автоматическое обнаружение и предотвращение проблем
- Немедленная корректировка поведения при отклонениях
- Система алертов и автоматических действий

Принцип: "Предотвратить проблему лучше чем исправлять" 🛡️
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Уровни алертов"""
    INFO = "info"
    WARNING = "warning"  
    ERROR = "error"
    CRITICAL = "critical"

class InterventionType(Enum):
    """Типы вмешательств"""
    PAUSE_AGENT = "pause_agent"           # Приостановить агента
    REDUCE_PRIORITY = "reduce_priority"   # Снизить приоритет
    REDIRECT_TASK = "redirect_task"       # Перенаправить задачу
    EMERGENCY_STOP = "emergency_stop"     # Экстренная остановка
    PARAMETER_ADJUST = "parameter_adjust" # Корректировка параметров

@dataclass
class QualityThreshold:
    """Пороговые значения качества"""
    metric_name: str
    min_value: float
    max_value: float
    time_window: int  # секунды
    violation_limit: int  # сколько нарушений разрешено

@dataclass
class GuardianAlert:
    """Алерт от Guardian Agent"""
    alert_id: str
    guardian_id: str
    level: AlertLevel
    agent_id: str
    metric_name: str
    current_value: float
    threshold_value: float
    message: str
    context: Dict[str, Any]
    timestamp: datetime
    auto_handled: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.alert_id,
            'guardian_id': self.guardian_id,
            'level': self.level.value,
            'agent_id': self.agent_id,
            'metric_name': self.metric_name,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'message': self.message,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'auto_handled': self.auto_handled
        }

@dataclass
class InterventionAction:
    """Действие по вмешательству"""
    action_id: str
    intervention_type: InterventionType
    target_agent: str
    parameters: Dict[str, Any]
    reason: str
    timestamp: datetime
    success: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'action_id': self.action_id,
            'intervention_type': self.intervention_type.value,
            'target_agent': self.target_agent,
            'parameters': self.parameters,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat(),
            'success': self.success
        }

class GuardianAgent:
    """Агент-охранник для мониторинга других агентов"""
    
    def __init__(self, guardian_id: str, monitored_agents: List[str] = None):
        self.guardian_id = guardian_id
        self.monitored_agents = monitored_agents or []
        self.quality_thresholds: Dict[str, QualityThreshold] = {}
        self.metric_history: Dict[str, List[Dict]] = {}
        self.alert_history: List[GuardianAlert] = []
        self.intervention_history: List[InterventionAction] = []
        self.is_active = True
        
        # Настройка базовых пороговых значений
        self._setup_default_thresholds()
        
        logger.info(f"👮 Guardian Agent {guardian_id} инициализирован для агентов: {self.monitored_agents}")
    
    def _setup_default_thresholds(self):
        """Настроить базовые пороговые значения"""
        
        # Пороги для производительности
        self.quality_thresholds['execution_time'] = QualityThreshold(
            metric_name='execution_time',
            min_value=0.1,    # минимум 0.1 секунды
            max_value=120.0,  # максимум 2 минуты
            time_window=300,  # окно 5 минут
            violation_limit=3 # максимум 3 нарушения
        )
        
        # Пороги для качества
        self.quality_thresholds['quality_score'] = QualityThreshold(
            metric_name='quality_score',
            min_value=0.6,    # минимальный балл качества
            max_value=1.0,
            time_window=600,  # окно 10 минут
            violation_limit=2
        )
        
        # Пороги для использования ресурсов
        self.quality_thresholds['memory_usage'] = QualityThreshold(
            metric_name='memory_usage',
            min_value=0.0,
            max_value=0.8,    # максимум 80% памяти
            time_window=180,  # окно 3 минуты
            violation_limit=5
        )
    
    async def monitor_agent_metric(self, agent_id: str, metric_name: str, value: float, context: Dict[str, Any] = None):
        """Мониторинг метрики агента"""
        
        if not self.is_active or agent_id not in self.monitored_agents:
            return
        
        timestamp = datetime.now()
        
        # Сохраняем в историю метрик
        metric_key = f"{agent_id}:{metric_name}"
        if metric_key not in self.metric_history:
            self.metric_history[metric_key] = []
        
        self.metric_history[metric_key].append({
            'value': value,
            'timestamp': timestamp,
            'context': context or {}
        })
        
        # Ограничиваем историю (последние 1000 записей)
        if len(self.metric_history[metric_key]) > 1000:
            self.metric_history[metric_key] = self.metric_history[metric_key][-1000:]
        
        # Проверяем пороговые значения
        await self._check_thresholds(agent_id, metric_name, value, context)
        
        logger.debug(f"📊 Guardian {self.guardian_id}: метрика {metric_name}={value:.3f} для агента {agent_id}")
    
    async def _check_thresholds(self, agent_id: str, metric_name: str, value: float, context: Dict[str, Any]):
        """Проверить пороговые значения"""
        
        if metric_name not in self.quality_thresholds:
            return
        
        threshold = self.quality_thresholds[metric_name]
        violation = False
        violation_type = None
        
        # Проверяем нарушения
        if value < threshold.min_value:
            violation = True
            violation_type = "below_minimum"
        elif value > threshold.max_value:
            violation = True
            violation_type = "above_maximum"
        
        if violation:
            # Подсчитываем нарушения в временном окне
            violations_count = self._count_recent_violations(agent_id, metric_name, threshold.time_window)
            
            if violations_count >= threshold.violation_limit:
                # Создаем алерт
                await self._create_alert(agent_id, metric_name, value, threshold, violation_type, context)
                
                # Автоматическое вмешательство если критично
                if violations_count >= threshold.violation_limit * 2:
                    await self._auto_intervene(agent_id, metric_name, value, threshold, context)
    
    def _count_recent_violations(self, agent_id: str, metric_name: str, time_window: int) -> int:
        """Подсчитать недавние нарушения"""
        
        metric_key = f"{agent_id}:{metric_name}"
        if metric_key not in self.metric_history:
            return 0
        
        threshold = self.quality_thresholds[metric_name]
        cutoff_time = datetime.now() - timedelta(seconds=time_window)
        
        violations = 0
        for record in self.metric_history[metric_key]:
            if record['timestamp'] > cutoff_time:
                value = record['value']
                if value < threshold.min_value or value > threshold.max_value:
                    violations += 1
        
        return violations
    
    async def _create_alert(self, agent_id: str, metric_name: str, value: float, 
                          threshold: QualityThreshold, violation_type: str, context: Dict[str, Any]):
        """Создать алерт"""
        
        # Определяем уровень алерта
        if metric_name == 'quality_score' and value < 0.3:
            level = AlertLevel.CRITICAL
        elif metric_name == 'execution_time' and value > threshold.max_value * 2:
            level = AlertLevel.ERROR
        elif value < threshold.min_value * 0.5 or value > threshold.max_value * 1.5:
            level = AlertLevel.WARNING
        else:
            level = AlertLevel.INFO
        
        alert_id = f"alert_{int(time.time() * 1000000)}"
        
        alert = GuardianAlert(
            alert_id=alert_id,
            guardian_id=self.guardian_id,
            level=level,
            agent_id=agent_id,
            metric_name=metric_name,
            current_value=value,
            threshold_value=threshold.max_value if violation_type == "above_maximum" else threshold.min_value,
            message=f"Агент {agent_id}: {metric_name} = {value:.3f} ({violation_type})",
            context=context,
            timestamp=datetime.now()
        )
        
        self.alert_history.append(alert)
        
        logger.warning(f"🚨 {level.value.upper()}: {alert.message}")
        
        return alert
    
    async def _auto_intervene(self, agent_id: str, metric_name: str, value: float, 
                            threshold: QualityThreshold, context: Dict[str, Any]):
        """Автоматическое вмешательство"""
        
        action_id = f"intervention_{int(time.time() * 1000000)}"
        
        # Выбираем тип вмешательства на основе метрики
        if metric_name == 'execution_time' and value > threshold.max_value * 3:
            # Слишком медленное выполнение - приостанавливаем агента
            intervention = InterventionAction(
                action_id=action_id,
                intervention_type=InterventionType.PAUSE_AGENT,
                target_agent=agent_id,
                parameters={'duration': 300, 'reason': 'slow_execution'},
                reason=f"Время выполнения {value:.1f}с превышает лимит в 3 раза",
                timestamp=datetime.now()
            )
            
        elif metric_name == 'quality_score' and value < 0.2:
            # Очень низкое качество - экстренная остановка
            intervention = InterventionAction(
                action_id=action_id,
                intervention_type=InterventionType.EMERGENCY_STOP,
                target_agent=agent_id,
                parameters={'immediate': True},
                reason=f"Критически низкое качество: {value:.2f}",
                timestamp=datetime.now()
            )
            
        elif metric_name == 'memory_usage' and value > 0.9:
            # Высокое потребление памяти - снижаем приоритет
            intervention = InterventionAction(
                action_id=action_id,
                intervention_type=InterventionType.REDUCE_PRIORITY,
                target_agent=agent_id,
                parameters={'new_priority': 'low', 'memory_limit': 0.7},
                reason=f"Превышение лимита памяти: {value:.1%}",
                timestamp=datetime.now()
            )
            
        else:
            # Общая корректировка параметров
            intervention = InterventionAction(
                action_id=action_id,
                intervention_type=InterventionType.PARAMETER_ADJUST,
                target_agent=agent_id,
                parameters={'metric': metric_name, 'adjustment': 'conservative'},
                reason=f"Нарушение пороговых значений {metric_name}",
                timestamp=datetime.now()
            )
        
        # Выполняем вмешательство
        success = await self._execute_intervention(intervention)
        intervention.success = success
        
        self.intervention_history.append(intervention)
        
        if success:
            logger.warning(f"🛡️ Автоматическое вмешательство выполнено: {intervention.intervention_type.value} для {agent_id}")
        else:
            logger.error(f"❌ Не удалось выполнить вмешательство: {intervention.intervention_type.value} для {agent_id}")
        
        return intervention
    
    async def _execute_intervention(self, intervention: InterventionAction) -> bool:
        """Выполнить вмешательство"""
        
        try:
            if intervention.intervention_type == InterventionType.PAUSE_AGENT:
                # Логика приостановки агента
                logger.info(f"⏸️ Приостанавливаем агента {intervention.target_agent} на {intervention.parameters.get('duration', 300)}с")
                return True
                
            elif intervention.intervention_type == InterventionType.EMERGENCY_STOP:
                # Логика экстренной остановки
                logger.warning(f"🛑 Экстренная остановка агента {intervention.target_agent}")
                return True
                
            elif intervention.intervention_type == InterventionType.REDUCE_PRIORITY:
                # Логика снижения приоритета
                logger.info(f"📉 Снижаем приоритет агента {intervention.target_agent}")
                return True
                
            elif intervention.intervention_type == InterventionType.PARAMETER_ADJUST:
                # Логика корректировки параметров
                logger.info(f"⚙️ Корректируем параметры агента {intervention.target_agent}")
                return True
                
            else:
                logger.error(f"❓ Неизвестный тип вмешательства: {intervention.intervention_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения вмешательства: {e}")
            return False
    
    def get_monitoring_report(self) -> Dict[str, Any]:
        """Получить отчёт мониторинга"""
        
        # Статистика по алертам
        alert_stats = {}
        for level in AlertLevel:
            alert_stats[level.value] = len([a for a in self.alert_history if a.level == level])
        
        # Статистика по вмешательствам
        intervention_stats = {}
        for itype in InterventionType:
            intervention_stats[itype.value] = len([i for i in self.intervention_history if i.intervention_type == itype])
        
        # Недавние проблемы (последние 24 часа)
        cutoff = datetime.now() - timedelta(hours=24)
        recent_alerts = [a for a in self.alert_history if a.timestamp > cutoff]
        recent_interventions = [i for i in self.intervention_history if i.timestamp > cutoff]
        
        return {
            'guardian_id': self.guardian_id,
            'monitored_agents': self.monitored_agents,
            'is_active': self.is_active,
            'alert_stats': alert_stats,
            'intervention_stats': intervention_stats,
            'recent_alerts_count': len(recent_alerts),
            'recent_interventions_count': len(recent_interventions),
            'total_metrics_tracked': sum(len(history) for history in self.metric_history.values()),
            'last_activity': max([a.timestamp for a in self.alert_history], default=datetime.now()).isoformat()
        } 