#!/usr/bin/env python3
"""
Простой планировщик для Universal Agent Platform.
Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!

Функции:
- Создание отложенных задач
- Выполнение задач по расписанию
- Простое хранение в памяти (можно расширить до Redis/MongoDB)
"""

import asyncio
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from loguru import logger

from app.core.base_plugin import BasePlugin


@dataclass
class ScheduledTask:
    """Запланированная задача"""
    id: str
    user_id: str
    chat_id: str
    scenario_id: str
    context: Dict[str, Any]
    execute_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    executed: bool = False
    result: Optional[Dict[str, Any]] = None


class SimpleSchedulerPlugin(BasePlugin):
    """
    Простой планировщик задач.
    
    Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
    - Хранение в памяти (для демо)
    - Простой цикл проверки
    - Минимум зависимостей
    """
    
    def __init__(self):
        super().__init__(name="simple_scheduler")
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.check_interval = 10  # Проверяем каждые 10 секунд
        self._scheduler_task: Optional[asyncio.Task] = None
        
    async def _do_initialize(self):
        """Инициализация планировщика."""
        logger.info("🕐 Инициализация SimpleScheduler Plugin...")
        
        # Запускаем фоновый процесс проверки задач
        await self.start_scheduler()
        
        logger.info("✅ SimpleScheduler Plugin инициализирован")
        
    async def start_scheduler(self):
        """Запускает фоновый планировщик."""
        if self.running:
            return
            
        self.running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("🚀 Планировщик запущен")
        
    async def stop_scheduler(self):
        """Останавливает планировщик."""
        self.running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Планировщик остановлен")
        
    async def _scheduler_loop(self):
        """Основной цикл планировщика."""
        logger.info("🔄 Запуск цикла планировщика")
        
        while self.running:
            try:
                await self._check_and_execute_tasks()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле планировщика: {e}")
                await asyncio.sleep(self.check_interval)
                
        logger.info("🔄 Цикл планировщика завершён")
        
    async def _check_and_execute_tasks(self):
        """Проверяет и выполняет готовые задачи."""
        now = datetime.utcnow()
        ready_tasks = []
        
        # Находим готовые к выполнению задачи
        for task_id, task in self.tasks.items():
            if not task.executed and task.execute_at <= now:
                ready_tasks.append(task)
                
        if ready_tasks:
            logger.info(f"⏰ Найдено {len(ready_tasks)} готовых задач")
            
        # Выполняем задачи
        for task in ready_tasks:
            await self._execute_task(task)
            
    async def _execute_task(self, task: ScheduledTask):
        """Выполняет запланированную задачу."""
        try:
            logger.info(f"🎯 Выполняю задачу {task.id} для пользователя {task.user_id}")
            
            # Получаем движок из контекста (если доступен)
            from app.core.simple_engine import create_engine
            engine = await create_engine()
            
            # Выполняем сценарий
            execution_context = {
                **task.context,
                "user_id": task.user_id,
                "chat_id": task.chat_id,
                "scheduled_task_id": task.id,
                "scheduled_execution": True
            }
            
            result = await engine.execute_scenario(task.scenario_id, execution_context)
            
            # Сохраняем результат
            task.executed = True
            task.result = result
            
            logger.info(f"✅ Задача {task.id} выполнена успешно")
            
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения задачи {task.id}: {e}")
            task.executed = True
            task.result = {"success": False, "error": str(e)}
            
    def register_handlers(self) -> Dict[str, Any]:
        """Регистрирует обработчики планировщика."""
        return {
            "scheduler_create_task": self.create_task,
            "scheduler_list_tasks": self.list_tasks,
            "scheduler_get_task": self.get_task,
            "scheduler_cancel_task": self.cancel_task,
            "scheduler_get_stats": self.get_stats,
        }
        
    async def healthcheck(self) -> bool:
        """Проверяет состояние планировщика."""
        return self.running and self._scheduler_task is not None and not self._scheduler_task.done()
        
    # === ОБРАБОТЧИКИ ===
    
    async def create_task(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создаёт новую запланированную задачу.
        
        Параметры step:
        - user_id: ID пользователя
        - chat_id: ID чата
        - scenario_id: ID сценария для выполнения
        - delay_minutes: Задержка в минутах (по умолчанию 2)
        - task_context: Дополнительный контекст для задачи
        - output_var: Переменная для сохранения результата
        """
        try:
            # Извлекаем параметры
            user_id = self.get_param(step, "user_id", required=True)
            chat_id = self.get_param(step, "chat_id", required=True)
            scenario_id = self.get_param(step, "scenario_id", required=True)
            delay_minutes = self.get_param(step, "delay_minutes", default=2)
            task_context = self.get_param(step, "task_context", default={})
            output_var = self.get_param(step, "output_var")
            
            # Генерируем ID задачи
            task_id = f"task_{user_id}_{datetime.utcnow().timestamp()}"
            
            # Вычисляем время выполнения
            execute_at = datetime.utcnow() + timedelta(minutes=delay_minutes)
            
            # Создаём задачу
            task = ScheduledTask(
                id=task_id,
                user_id=user_id,
                chat_id=chat_id,
                scenario_id=scenario_id,
                context=task_context,
                execute_at=execute_at
            )
            
            # Сохраняем задачу
            self.tasks[task_id] = task
            
            logger.info(f"📅 Создана задача {task_id}: сценарий {scenario_id} через {delay_minutes} мин")
            
            result = {
                "success": True,
                "task_id": task_id,
                "execute_at": execute_at.isoformat(),
                "delay_minutes": delay_minutes,
                "scenario_id": scenario_id
            }
            
            # Сохраняем результат в контекст
            if output_var:
                context[output_var] = result
                
            return context
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания задачи: {e}")
            if self.get_param(step, "output_var"):
                context[self.get_param(step, "output_var")] = {"success": False, "error": str(e)}
            return context
            
    async def list_tasks(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Получает список задач пользователя."""
        try:
            user_id = self.get_param(step, "user_id")
            output_var = self.get_param(step, "output_var")
            
            # Фильтруем задачи
            user_tasks = []
            for task in self.tasks.values():
                if not user_id or task.user_id == user_id:
                    user_tasks.append({
                        "id": task.id,
                        "user_id": task.user_id,
                        "scenario_id": task.scenario_id,
                        "execute_at": task.execute_at.isoformat(),
                        "executed": task.executed,
                        "created_at": task.created_at.isoformat()
                    })
                    
            result = {
                "success": True,
                "tasks": user_tasks,
                "count": len(user_tasks)
            }
            
            if output_var:
                context[output_var] = result
                
            return context
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка задач: {e}")
            if self.get_param(step, "output_var"):
                context[self.get_param(step, "output_var")] = {"success": False, "error": str(e)}
            return context
            
    async def get_task(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Получает информацию о задаче."""
        try:
            task_id = self.get_param(step, "task_id", required=True)
            output_var = self.get_param(step, "output_var")
            
            if task_id not in self.tasks:
                result = {"success": False, "error": "Задача не найдена"}
            else:
                task = self.tasks[task_id]
                result = {
                    "success": True,
                    "task": {
                        "id": task.id,
                        "user_id": task.user_id,
                        "chat_id": task.chat_id,
                        "scenario_id": task.scenario_id,
                        "execute_at": task.execute_at.isoformat(),
                        "executed": task.executed,
                        "created_at": task.created_at.isoformat(),
                        "result": task.result
                    }
                }
                
            if output_var:
                context[output_var] = result
                
            return context
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения задачи: {e}")
            if self.get_param(step, "output_var"):
                context[self.get_param(step, "output_var")] = {"success": False, "error": str(e)}
            return context
            
    async def cancel_task(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Отменяет задачу."""
        try:
            task_id = self.get_param(step, "task_id", required=True)
            output_var = self.get_param(step, "output_var")
            
            if task_id not in self.tasks:
                result = {"success": False, "error": "Задача не найдена"}
            else:
                task = self.tasks[task_id]
                if task.executed:
                    result = {"success": False, "error": "Задача уже выполнена"}
                else:
                    del self.tasks[task_id]
                    result = {"success": True, "message": "Задача отменена"}
                    logger.info(f"🗑️ Задача {task_id} отменена")
                    
            if output_var:
                context[output_var] = result
                
            return context
            
        except Exception as e:
            logger.error(f"❌ Ошибка отмены задачи: {e}")
            if self.get_param(step, "output_var"):
                context[self.get_param(step, "output_var")] = {"success": False, "error": str(e)}
            return context
            
    async def get_stats(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Получает статистику планировщика."""
        try:
            output_var = self.get_param(step, "output_var")
            
            total_tasks = len(self.tasks)
            executed_tasks = sum(1 for task in self.tasks.values() if task.executed)
            pending_tasks = total_tasks - executed_tasks
            
            result = {
                "success": True,
                "stats": {
                    "total_tasks": total_tasks,
                    "executed_tasks": executed_tasks,
                    "pending_tasks": pending_tasks,
                    "scheduler_running": self.running,
                    "check_interval": self.check_interval
                }
            }
            
            if output_var:
                context[output_var] = result
                
            return context
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики: {e}")
            if self.get_param(step, "output_var"):
                context[self.get_param(step, "output_var")] = {"success": False, "error": str(e)}
            return context 