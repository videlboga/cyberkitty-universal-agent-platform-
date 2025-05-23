import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional
from loguru import logger

from app.plugins.plugin_base import PluginBase


class SchedulerPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.scheduled_tasks = {}
        self.running_tasks = {}
        
    def register_step_handlers(self, step_handlers: Dict[str, Callable]):
        """Регистрирует обработчики шагов, предоставляемые этим плагином."""
        step_handlers["schedule_delay"] = self.handle_schedule_delay
        step_handlers["schedule_at"] = self.handle_schedule_at
        step_handlers["schedule_periodic"] = self.handle_schedule_periodic
        step_handlers["cancel_schedule"] = self.handle_cancel_schedule
        logger.info(f"SchedulerPlugin зарегистрировал обработчики шагов: schedule_delay, schedule_at, schedule_periodic, cancel_schedule")

    async def handle_schedule_delay(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Планирует выполнение сценария через указанное время."""
        params = step_data.get("params", {})
        
        delay_seconds = params.get("delay_seconds", 0)
        delay_minutes = params.get("delay_minutes", 0)
        delay_hours = params.get("delay_hours", 0)
        
        scenario_id = params.get("scenario_id")
        agent_id = params.get("agent_id")
        target_context = params.get("context", {})
        
        total_delay = delay_seconds + (delay_minutes * 60) + (delay_hours * 3600)
        
        if not scenario_id:
            logger.error("schedule_delay: scenario_id is required")
            return None
            
        task_id = f"delay_{scenario_id}_{datetime.now().timestamp()}"
        
        logger.info(f"Scheduling scenario {scenario_id} to run in {total_delay} seconds")
        
        # Создаём задачу
        async def delayed_execution():
            await asyncio.sleep(total_delay)
            await self._execute_scenario(scenario_id, agent_id, target_context)
            
        task = asyncio.create_task(delayed_execution())
        self.running_tasks[task_id] = task
        
        # Сохраняем ID задачи в контекст
        output_var = params.get("output_var", "scheduled_task_id")
        context[output_var] = task_id
        
        return None

    async def handle_schedule_at(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Планирует выполнение сценария в определённое время."""
        params = step_data.get("params", {})
        
        target_time_str = params.get("target_time")  # ISO format: "2024-12-01T15:30:00"
        scenario_id = params.get("scenario_id")
        agent_id = params.get("agent_id")
        target_context = params.get("context", {})
        
        if not scenario_id or not target_time_str:
            logger.error("schedule_at: scenario_id and target_time are required")
            return None
            
        try:
            target_time = datetime.fromisoformat(target_time_str)
            current_time = datetime.now()
            
            if target_time <= current_time:
                logger.warning(f"Target time {target_time} is in the past, executing immediately")
                await self._execute_scenario(scenario_id, agent_id, target_context)
                return None
                
            delay_seconds = (target_time - current_time).total_seconds()
            
            task_id = f"at_{scenario_id}_{target_time.timestamp()}"
            
            logger.info(f"Scheduling scenario {scenario_id} to run at {target_time}")
            
            async def timed_execution():
                await asyncio.sleep(delay_seconds)
                await self._execute_scenario(scenario_id, agent_id, target_context)
                
            task = asyncio.create_task(timed_execution())
            self.running_tasks[task_id] = task
            
            output_var = params.get("output_var", "scheduled_task_id")
            context[output_var] = task_id
            
        except ValueError as e:
            logger.error(f"Invalid target_time format: {target_time_str}, error: {e}")
            
        return None

    async def handle_schedule_periodic(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Планирует периодическое выполнение сценария."""
        params = step_data.get("params", {})
        
        interval_seconds = params.get("interval_seconds", 0)
        interval_minutes = params.get("interval_minutes", 0) 
        interval_hours = params.get("interval_hours", 0)
        max_runs = params.get("max_runs", -1)  # -1 = бесконечно
        
        scenario_id = params.get("scenario_id")
        agent_id = params.get("agent_id")
        target_context = params.get("context", {})
        
        total_interval = interval_seconds + (interval_minutes * 60) + (interval_hours * 3600)
        
        if not scenario_id or total_interval <= 0:
            logger.error("schedule_periodic: scenario_id and valid interval are required")
            return None
            
        task_id = f"periodic_{scenario_id}_{datetime.now().timestamp()}"
        
        logger.info(f"Scheduling periodic scenario {scenario_id} every {total_interval} seconds, max_runs: {max_runs}")
        
        async def periodic_execution():
            runs_count = 0
            while max_runs == -1 or runs_count < max_runs:
                await self._execute_scenario(scenario_id, agent_id, target_context)
                runs_count += 1
                
                if max_runs != -1 and runs_count >= max_runs:
                    break
                    
                await asyncio.sleep(total_interval)
                
            logger.info(f"Periodic task {task_id} completed after {runs_count} runs")
            
        task = asyncio.create_task(periodic_execution())
        self.running_tasks[task_id] = task
        
        output_var = params.get("output_var", "scheduled_task_id")
        context[output_var] = task_id
        
        return None

    async def handle_cancel_schedule(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Отменяет запланированную задачу."""
        params = step_data.get("params", {})
        
        task_id = params.get("task_id")
        if not task_id:
            task_id = context.get("scheduled_task_id")
            
        if not task_id:
            logger.error("cancel_schedule: task_id is required")
            return None
            
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.cancel()
            del self.running_tasks[task_id]
            logger.info(f"Cancelled scheduled task: {task_id}")
            
            output_var = params.get("output_var", "cancellation_result")
            context[output_var] = "cancelled"
        else:
            logger.warning(f"Task {task_id} not found in running tasks")
            output_var = params.get("output_var", "cancellation_result")
            context[output_var] = "not_found"
            
        return None

    async def _execute_scenario(self, scenario_id: str, agent_id: Optional[str], target_context: Dict[str, Any]):
        """Выполняет сценарий (здесь нужна интеграция с ScenarioExecutor)."""
        logger.info(f"Executing scheduled scenario: {scenario_id} with agent: {agent_id}")
        
        # Заглушка для выполнения сценария
        # В реальной реализации здесь должен быть вызов ScenarioExecutor
        # Пример: await self.scenario_executor.execute_scenario(scenario_id, agent_id, target_context)
        
        logger.info(f"Scheduled scenario {scenario_id} execution completed")

    async def healthcheck(self) -> Dict[str, Any]:
        """Проверка состояния планировщика."""
        return {
            "status": "healthy",
            "active_tasks": len(self.running_tasks),
            "task_ids": list(self.running_tasks.keys())
        } 