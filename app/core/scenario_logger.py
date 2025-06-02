"""
🔍 СИСТЕМА ЛОГИРОВАНИЯ СЦЕНАРИЕВ
Детальное логирование каждого шага выполнения сценариев с поддержкой:
- Структурированных логов в файлы
- Сохранения в MongoDB для анализа
- Разных уровней детализации
- Метрик производительности
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from loguru import logger
from enum import Enum

class LogLevel(Enum):
    """Уровни детализации логирования."""
    MINIMAL = "minimal"      # Только начало/конец сценария
    BASIC = "basic"          # + каждый шаг
    DETAILED = "detailed"    # + параметры и результаты
    FULL = "full"           # + полный контекст на каждом шаге

@dataclass
class StepLog:
    """Лог одного шага выполнения."""
    step_id: str
    step_type: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: str = "running"  # running, success, error, stopped
    error_message: Optional[str] = None
    
    # Данные шага
    step_params: Dict[str, Any] = field(default_factory=dict)
    step_result: Dict[str, Any] = field(default_factory=dict)
    
    # Контекст (только для DETAILED и FULL уровней)
    context_before: Optional[Dict[str, Any]] = None
    context_after: Optional[Dict[str, Any]] = None
    context_changes: Optional[Dict[str, Any]] = None

@dataclass
class ScenarioLog:
    """Лог выполнения всего сценария."""
    execution_id: str
    scenario_id: str
    user_id: Optional[str] = None
    chat_id: Optional[str] = None
    channel_id: Optional[str] = None
    
    # Временные метки
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    
    # Статус
    status: str = "running"  # running, completed, error, stopped
    final_status: Optional[str] = None
    error_message: Optional[str] = None
    
    # Контекст
    initial_context: Dict[str, Any] = field(default_factory=dict)
    final_context: Dict[str, Any] = field(default_factory=dict)
    
    # Шаги
    steps: List[StepLog] = field(default_factory=list)
    total_steps: int = 0
    completed_steps: int = 0
    
    # Метрики
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

class ScenarioLogger:
    """
    Система логирования выполнения сценариев.
    
    Поддерживает:
    - Разные уровни детализации
    - Логирование в файлы и MongoDB
    - Метрики производительности
    - Анализ выполнения
    """
    
    def __init__(self, log_level: LogLevel = LogLevel.BASIC, mongo_plugin=None):
        self.log_level = log_level
        self.mongo_plugin = mongo_plugin
        self.active_scenarios: Dict[str, ScenarioLog] = {}
        
        # Настройка логгера для сценариев
        self.logger = logger.bind(component="ScenarioLogger")
        
        # Добавляем специальный файл для логов сценариев
        logger.add(
            "logs/scenario_execution.log",
            rotation="50 MB",
            retention="30 days",
            compression="gz",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | SCENARIO | {message}",
            level="INFO",
            filter=lambda record: record.get("extra", {}).get("component") == "ScenarioLogger"
        )
    
    def start_scenario(self, 
                      execution_id: str,
                      scenario_id: str,
                      initial_context: Dict[str, Any],
                      user_id: Optional[str] = None,
                      chat_id: Optional[str] = None,
                      channel_id: Optional[str] = None) -> ScenarioLog:
        """Начинает логирование выполнения сценария."""
        
        scenario_log = ScenarioLog(
            execution_id=execution_id,
            scenario_id=scenario_id,
            user_id=user_id,
            chat_id=chat_id,
            channel_id=channel_id,
            initial_context=self._safe_copy_context(initial_context)
        )
        
        self.active_scenarios[execution_id] = scenario_log
        
        # Логируем начало
        self.logger.info(
            f"🎬 НАЧАЛО СЦЕНАРИЯ {scenario_id}",
            execution_id=execution_id,
            scenario_id=scenario_id,
            user_id=user_id,
            chat_id=chat_id,
            channel_id=channel_id,
            log_level=self.log_level.value,
            initial_context_size=len(initial_context)
        )
        
        if self.log_level in [LogLevel.DETAILED, LogLevel.FULL]:
            self.logger.debug(
                f"📋 Начальный контекст сценария {scenario_id}",
                execution_id=execution_id,
                initial_context=initial_context
            )
        
        return scenario_log
    
    def start_step(self, 
                   execution_id: str,
                   step: Dict[str, Any],
                   context: Dict[str, Any]) -> Optional[StepLog]:
        """Начинает логирование выполнения шага."""
        
        if execution_id not in self.active_scenarios:
            self.logger.warning(f"⚠️ Попытка логировать шаг для неизвестного сценария {execution_id}")
            return None
        
        scenario_log = self.active_scenarios[execution_id]
        step_id = step.get("id", "unknown")
        step_type = step.get("type", "unknown")
        
        step_log = StepLog(
            step_id=step_id,
            step_type=step_type,
            started_at=datetime.now(timezone.utc)
        )
        
        # Сохраняем параметры шага (для DETAILED и FULL)
        if self.log_level in [LogLevel.DETAILED, LogLevel.FULL]:
            step_log.step_params = self._safe_copy_context(step.get("params", {}))
            step_log.context_before = self._safe_copy_context(context)
        
        scenario_log.steps.append(step_log)
        scenario_log.total_steps = len(scenario_log.steps)
        
        # Логируем начало шага
        if self.log_level != LogLevel.MINIMAL:
            self.logger.info(
                f"▶️ ШАГ {step_id} ({step_type})",
                execution_id=execution_id,
                scenario_id=scenario_log.scenario_id,
                step_id=step_id,
                step_type=step_type,
                step_number=len(scenario_log.steps)
            )
            
            if self.log_level == LogLevel.FULL:
                self.logger.debug(
                    f"📊 Контекст перед шагом {step_id}",
                    execution_id=execution_id,
                    step_id=step_id,
                    context=context
                )
        
        return step_log
    
    def finish_step(self, 
                    execution_id: str,
                    step_id: str,
                    result_context: Dict[str, Any],
                    error: Optional[Exception] = None) -> bool:
        """Завершает логирование выполнения шага."""
        
        if execution_id not in self.active_scenarios:
            return False
        
        scenario_log = self.active_scenarios[execution_id]
        
        # Находим последний шаг с данным ID
        step_log = None
        for s in reversed(scenario_log.steps):
            if s.step_id == step_id and s.finished_at is None:
                step_log = s
                break
        
        if not step_log:
            self.logger.warning(f"⚠️ Не найден активный шаг {step_id} для завершения")
            return False
        
        # Завершаем шаг
        step_log.finished_at = datetime.now(timezone.utc)
        step_log.duration_ms = (step_log.finished_at - step_log.started_at).total_seconds() * 1000
        
        if error:
            step_log.status = "error"
            step_log.error_message = str(error)
        else:
            step_log.status = "success"
            scenario_log.completed_steps += 1
        
        # Сохраняем результат и изменения контекста
        if self.log_level in [LogLevel.DETAILED, LogLevel.FULL]:
            step_log.context_after = self._safe_copy_context(result_context)
            step_log.context_changes = self._calculate_context_changes(
                step_log.context_before or {},
                result_context
            )
        
        # Логируем завершение шага
        if self.log_level != LogLevel.MINIMAL:
            status_emoji = "✅" if step_log.status == "success" else "❌"
            self.logger.info(
                f"{status_emoji} ШАГ {step_id} завершен ({step_log.duration_ms:.1f}ms)",
                execution_id=execution_id,
                scenario_id=scenario_log.scenario_id,
                step_id=step_id,
                step_type=step_log.step_type,
                status=step_log.status,
                duration_ms=step_log.duration_ms,
                error=step_log.error_message
            )
            
            if self.log_level == LogLevel.FULL and step_log.context_changes:
                self.logger.debug(
                    f"🔄 Изменения контекста в шаге {step_id}",
                    execution_id=execution_id,
                    step_id=step_id,
                    context_changes=step_log.context_changes
                )
        
        return True
    
    def finish_scenario(self, 
                       execution_id: str,
                       final_context: Dict[str, Any],
                       final_status: str = "completed",
                       error: Optional[Exception] = None) -> Optional[ScenarioLog]:
        """Завершает логирование выполнения сценария."""
        
        if execution_id not in self.active_scenarios:
            return None
        
        scenario_log = self.active_scenarios[execution_id]
        
        # Завершаем сценарий
        scenario_log.finished_at = datetime.now(timezone.utc)
        scenario_log.duration_ms = (scenario_log.finished_at - scenario_log.started_at).total_seconds() * 1000
        scenario_log.final_context = self._safe_copy_context(final_context)
        scenario_log.final_status = final_status
        
        if error:
            scenario_log.status = "error"
            scenario_log.error_message = str(error)
        else:
            scenario_log.status = final_status
        
        # Вычисляем метрики производительности
        scenario_log.performance_metrics = self._calculate_performance_metrics(scenario_log)
        
        # Логируем завершение сценария
        status_emoji = "🎉" if scenario_log.status == "completed" else "💥" if scenario_log.status == "error" else "⏸️"
        self.logger.info(
            f"{status_emoji} СЦЕНАРИЙ {scenario_log.scenario_id} завершен",
            execution_id=execution_id,
            scenario_id=scenario_log.scenario_id,
            status=scenario_log.status,
            duration_ms=scenario_log.duration_ms,
            total_steps=scenario_log.total_steps,
            completed_steps=scenario_log.completed_steps,
            success_rate=f"{(scenario_log.completed_steps / max(scenario_log.total_steps, 1) * 100):.1f}%",
            error=scenario_log.error_message
        )
        
        # Сохраняем в MongoDB если доступен
        if self.mongo_plugin:
            asyncio.create_task(self._save_to_mongo(scenario_log))
        
        # Удаляем из активных
        del self.active_scenarios[execution_id]
        
        return scenario_log
    
    def get_active_scenarios(self) -> List[ScenarioLog]:
        """Возвращает список активных сценариев."""
        return list(self.active_scenarios.values())
    
    def get_scenario_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Возвращает статус выполнения сценария."""
        if execution_id not in self.active_scenarios:
            return None
        
        scenario_log = self.active_scenarios[execution_id]
        return {
            "execution_id": execution_id,
            "scenario_id": scenario_log.scenario_id,
            "status": scenario_log.status,
            "progress": f"{scenario_log.completed_steps}/{scenario_log.total_steps}",
            "duration_ms": (datetime.now(timezone.utc) - scenario_log.started_at).total_seconds() * 1000,
            "current_step": scenario_log.steps[-1].step_id if scenario_log.steps else None
        }
    
    def _safe_copy_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Безопасно копирует контекст, исключая несериализуемые объекты."""
        try:
            # Пробуем сериализовать в JSON и обратно для проверки
            json_str = json.dumps(context, default=str, ensure_ascii=False)
            return json.loads(json_str)
        except Exception as e:
            self.logger.warning(f"⚠️ Ошибка копирования контекста: {e}")
            return {"_error": "Context serialization failed", "_original_keys": list(context.keys())}
    
    def _calculate_context_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """Вычисляет изменения в контексте."""
        changes = {
            "added": {},
            "modified": {},
            "removed": []
        }
        
        # Добавленные ключи
        for key, value in after.items():
            if key not in before:
                changes["added"][key] = value
        
        # Измененные ключи
        for key, value in after.items():
            if key in before and before[key] != value:
                changes["modified"][key] = {
                    "before": before[key],
                    "after": value
                }
        
        # Удаленные ключи
        for key in before:
            if key not in after:
                changes["removed"].append(key)
        
        return changes
    
    def _calculate_performance_metrics(self, scenario_log: ScenarioLog) -> Dict[str, Any]:
        """Вычисляет метрики производительности сценария."""
        if not scenario_log.steps:
            return {}
        
        step_durations = [s.duration_ms for s in scenario_log.steps if s.duration_ms is not None]
        
        metrics = {
            "total_duration_ms": scenario_log.duration_ms,
            "steps_count": len(scenario_log.steps),
            "success_rate": scenario_log.completed_steps / len(scenario_log.steps) * 100,
            "avg_step_duration_ms": sum(step_durations) / len(step_durations) if step_durations else 0,
            "max_step_duration_ms": max(step_durations) if step_durations else 0,
            "min_step_duration_ms": min(step_durations) if step_durations else 0,
            "slowest_step": None,
            "fastest_step": None
        }
        
        # Находим самый медленный и быстрый шаги
        if step_durations:
            max_duration = max(step_durations)
            min_duration = min(step_durations)
            
            for step in scenario_log.steps:
                if step.duration_ms == max_duration:
                    metrics["slowest_step"] = {"id": step.step_id, "type": step.step_type, "duration_ms": max_duration}
                if step.duration_ms == min_duration:
                    metrics["fastest_step"] = {"id": step.step_id, "type": step.step_type, "duration_ms": min_duration}
        
        return metrics
    
    async def _save_to_mongo(self, scenario_log: ScenarioLog):
        """Сохраняет лог сценария в MongoDB."""
        try:
            if not self.mongo_plugin:
                return
            
            # Конвертируем в словарь для сохранения
            log_data = asdict(scenario_log)
            
            # Преобразуем datetime в ISO строки
            log_data["started_at"] = scenario_log.started_at.isoformat()
            if scenario_log.finished_at:
                log_data["finished_at"] = scenario_log.finished_at.isoformat()
            
            for step in log_data["steps"]:
                step["started_at"] = datetime.fromisoformat(step["started_at"].replace("Z", "+00:00")).isoformat()
                if step["finished_at"]:
                    step["finished_at"] = datetime.fromisoformat(step["finished_at"].replace("Z", "+00:00")).isoformat()
            
            # Сохраняем в коллекцию scenario_execution_logs
            context = {
                "collection": "scenario_execution_logs",
                "document": log_data
            }
            
            await self.mongo_plugin.insert_document(context)
            
            self.logger.debug(
                f"💾 Лог сценария {scenario_log.scenario_id} сохранен в MongoDB",
                execution_id=scenario_log.execution_id
            )
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения лога в MongoDB: {e}")

# === ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР ===
_global_scenario_logger: Optional[ScenarioLogger] = None

def get_scenario_logger() -> ScenarioLogger:
    """Возвращает глобальный экземпляр логгера сценариев."""
    global _global_scenario_logger
    if _global_scenario_logger is None:
        _global_scenario_logger = ScenarioLogger()
    return _global_scenario_logger

def initialize_scenario_logger(log_level: LogLevel = LogLevel.BASIC, mongo_plugin=None):
    """Инициализирует глобальный логгер сценариев."""
    global _global_scenario_logger
    _global_scenario_logger = ScenarioLogger(log_level=log_level, mongo_plugin=mongo_plugin)
    return _global_scenario_logger 