from typing import Dict, Any, Callable, Optional
from loguru import logger # <--- РАСКОММЕНТИРОВАНО
import os
from datetime import datetime, timedelta
import uuid
import json

os.makedirs("logs", exist_ok=True) # <--- РАСКОММЕНТИРОВАНО
logger.add("logs/scheduling_plugin.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True) # <--- РАСКОММЕНТИРОВАНО

class SchedulingPlugin:
    def __init__(self, scheduler_service: Any): # <--- УБРАН logger из параметров
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

        # Извлекаем параметры напрямую из step_data, так как это уже resolved_params
        run_in_seconds = step_data.get("run_in_seconds")
        scenario_id_to_run = step_data.get("scenario_id_to_run")
        # context_to_pass уже должен быть разрешен _resolve_value_from_context в ScenarioExecutor
        context_to_pass_for_scheduled_task = step_data.get("context_to_pass", {})
        task_id_output_var = step_data.get("task_id_output_var")

        # user_id = context.get("user_id") # СТАРЫЙ СПОСОБ
        user_id = context.get("initiator_user_id") # НОВЫЙ СПОСОБ
        chat_id = context.get("chat_id")

        # === НАЧАЛО ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===
        logger.info(f"[SCHEDULING_PLUGIN DEBUG] Перед проверкой. run_in_seconds: {run_in_seconds} (тип: {type(run_in_seconds)})")
        logger.info(f"[SCHEDULING_PLUGIN DEBUG] Перед проверкой. scenario_id_to_run: '{scenario_id_to_run}' (тип: {type(scenario_id_to_run)})")
        logger.info(f"[SCHEDULING_PLUGIN DEBUG] Перед проверкой. user_id (из initiator_user_id): '{user_id}' (тип: {type(user_id)})")
        # === КОНЕЦ ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===

        if run_in_seconds is None or not scenario_id_to_run or user_id is None:
            error_msg = ("schedule_scenario_run: отсутствуют обязательные параметры "
                         "'run_in_seconds', 'scenario_id_to_run', или 'initiator_user_id' отсутствует в контексте.") # ИЗМЕНЕНО
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
                    "agent_id": scenario_id_to_run, # Это ID сценария, который будет запущен планировщиком
                    "user_id": str(user_id), # И здесь user_id, который будет использоваться при запуске
                    "chat_id": str(chat_id) if chat_id else None,
                    "initial_payload": initial_payload_for_runner
                },
                "enabled": True,
                "name": f"Scheduled run of scenario {scenario_id_to_run} for user {user_id}"
            }

            # Добавляем детальное логирование task_config
            logger.debug(f"Подготовлен task_config для SchedulerService: {json.dumps(task_config, indent=2, default=str)}")

            # === НАЧАЛО ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===
            logger.info(f"[DEBUG SchedulingPlugin] Перед вызовом add_task. user_id (из initiator_user_id): '{user_id}', scenario_id_to_run: '{scenario_id_to_run}', run_in_seconds: {run_in_seconds}") # ИЗМЕНЕНО
            # === КОНЕЦ ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===

            # Добавляем задачу через сервис планировщика
            # Важно: add_task должен быть async, если мы его вызываем с await
            added_task_id = await self.scheduler_service.add_task(task_config)
            
            if task_id_output_var and added_task_id:
                context[task_id_output_var] = added_task_id
            
            logger.info(f"Сценарий '{scenario_id_to_run}' запланирован для пользователя (initiator_user_id) '{user_id}' через {run_in_seconds} сек. Task ID: {added_task_id}") # ИЗМЕНЕНО
            context["__step_success_message__"] = f"Scenario '{scenario_id_to_run}' scheduled for initiator_user_id '{user_id}'. Task ID: {added_task_id}" # ИЗМЕНЕНО

        except Exception as e:
            error_msg = f"Ошибка при планировании сценария '{scenario_id_to_run}': {e}"
            logger.error(error_msg, exc_info=True)
            context["__step_error__"] = error_msg
            if task_id_output_var:
                context[task_id_output_var] = None
            
        return context 