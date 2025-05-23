from typing import Dict, Any, Callable, Optional
from loguru import logger # <--- РАСКОММЕНТИРОВАНО
import os
from datetime import datetime, timedelta
import uuid
import json

from app.plugins.plugin_base import PluginBase # <--- ОБНОВЛЕННЫЙ ИМПОРТ

# Настройка логирования - УДАЛЯЕМ ЭТИ СТРОКИ
# os.makedirs("logs", exist_ok=True) # <--- РАСКОММЕНТИРОВАНО
# logger.add("logs/scheduling_plugin.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True) # <--- РАСКОММЕНТИРОВАНО

# from app.utils.scheduler import SchedulerService # Закомментировано из-за цикла
from typing import TYPE_CHECKING

class SchedulingPlugin(PluginBase): # <--- ДОБАВЛЕНО НАСЛЕДОВАНИЕ
    def __init__(self, scheduler_service: Any): # <--- УБРАН logger из параметров
        super().__init__() # <--- ВЫЗОВ КОНСТРУКТОРА БАЗОВОГО КЛАССА
        if scheduler_service is None:
            raise ValueError("Экземпляр SchedulerService не может быть None")
        self.scheduler_service = scheduler_service
        # self.logger = logger # <--- УДАЛЕНО (используется глобальный logger модуля)
        logger.info("SchedulingPlugin инициализирован (использует собственный логгер).")

    def register_step_handlers(self, step_handlers: Dict[str, Callable]):
        """Регистрирует обработчики шагов, предоставляемые этим плагином."""
        step_handlers["schedule_scenario_run"] = self.handle_schedule_scenario_run
        logger.info("SchedulingPlugin зарегистрировал обработчик шага: schedule_scenario_run (лог в scheduling_plugin.log)")

    async def handle_schedule_scenario_run(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # Используем глобальный logger модуля
        logger.debug(f"[SchedulingPlugin] handle_schedule_scenario_run called. Incoming step_data: {step_data}")
        logger.debug(f"[SchedulingPlugin] Incoming context: {context}")

        params = step_data.get("params", {})
        if not isinstance(params, dict):
            logger.error(f"[SchedulingPlugin] Ошибка: 'params' не является словарем в step_data: {type(params)}. Full step_data: {step_data}")
            context["__step_error__"] = "Внутренняя ошибка: 'params' шага schedule_scenario_run не является словарем."
            return context

        # Извлекаем параметры из params
        run_in_seconds = params.get("run_in_seconds")
        agent_id_to_run_scenario = params.get("agent_id_to_run_scenario")
        context_to_pass_for_scheduled_task = params.get("context_to_pass", {})
        task_id_output_var = params.get("task_id_output_var")

        user_id = context.get("initiator_user_id")
        chat_id = context.get("chat_id")

        # === НАЧАЛО ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===
        logger.info(f"[SCHEDULING_PLUGIN DEBUG] Перед проверкой. run_in_seconds: {run_in_seconds} (тип: {type(run_in_seconds)})")
        logger.info(f"[SCHEDULING_PLUGIN DEBUG] Перед проверкой. agent_id_to_run_scenario: '{agent_id_to_run_scenario}' (тип: {type(agent_id_to_run_scenario)})")
        logger.info(f"[SCHEDULING_PLUGIN DEBUG] Перед проверкой. user_id (из initiator_user_id): '{user_id}' (тип: {type(user_id)})")
        # === КОНЕЦ ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===

        if run_in_seconds is None or not agent_id_to_run_scenario or user_id is None:
            error_msg = ("schedule_scenario_run: отсутствуют обязательные параметры "
                         "'run_in_seconds', 'agent_id_to_run_scenario', или 'initiator_user_id' отсутствует в контексте.")
            logger.error(error_msg)
            context["__step_error__"] = error_msg
            return context

        try:
            run_in_seconds = int(run_in_seconds)
            if run_in_seconds < 0:
                raise ValueError("run_in_seconds не может быть отрицательным.")
        except ValueError as e:
            error_msg = f"schedule_scenario_run: неверное значение для 'run_in_seconds': {run_in_seconds}. {e}"
            logger.error(error_msg)
            context["__step_error__"] = error_msg
            return context

        try:
            target_datetime = datetime.now() + timedelta(seconds=run_in_seconds)
            
            # Используем context_to_pass_for_scheduled_task напрямую, так как он уже разрешен
            initial_payload_for_runner = {"context": context_to_pass_for_scheduled_task}

            task_config = {
                "id": str(uuid.uuid4()), # Генерируем новый ID для задачи
                "user_id": str(user_id), # Используем initiator_user_id, преобразованный в user_id
                "trigger_type": "once",
                "trigger_config": {
                    "datetime": target_datetime.isoformat(),
                    "margin_seconds": 60 # Позволяем небольшую погрешность
                },
                "action_type": "run_agent",
                "action_config": {
                    "agent_id": agent_id_to_run_scenario,
                    "user_id": str(user_id), # И здесь user_id, который будет использоваться при запуске
                    "chat_id": str(chat_id) if chat_id else None,
                    "initial_payload": initial_payload_for_runner
                },
                "enabled": True,
                "name": f"Scheduled run via agent {agent_id_to_run_scenario} for user {user_id}"
            }

            # Добавляем детальное логирование task_config
            logger.debug(f"Подготовлен task_config для SchedulerService: {json.dumps(task_config, indent=2, default=str)}")

            # === НАЧАЛО ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===
            logger.info(f"[DEBUG SchedulingPlugin] Перед вызовом add_task. user_id (из initiator_user_id): '{user_id}', agent_id_to_run_scenario: '{agent_id_to_run_scenario}', run_in_seconds: {run_in_seconds}")
            # === КОНЕЦ ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===

            # Добавляем задачу через сервис планировщика
            # Важно: add_task должен быть async, если мы его вызываем с await
            added_task_id = await self.scheduler_service.add_task(task_config)
            
            if task_id_output_var and added_task_id:
                context[task_id_output_var] = added_task_id
            
            logger.info(f"Агент '{agent_id_to_run_scenario}' запланирован для запуска сценария пользователем (initiator_user_id) '{user_id}' через {run_in_seconds} сек. Task ID: {added_task_id}")
            context["__step_success_message__"] = f"Agent '{agent_id_to_run_scenario}' scheduled for initiator_user_id '{user_id}'. Task ID: {added_task_id}"

        except Exception as e:
            error_msg = f"Ошибка при планировании запуска для агента '{agent_id_to_run_scenario}': {e}"
            logger.error(error_msg, exc_info=True)
            context["__step_error__"] = error_msg
            if task_id_output_var:
                context[task_id_output_var] = None
            
        return context 