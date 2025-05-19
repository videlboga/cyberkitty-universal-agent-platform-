from fastapi import APIRouter, HTTPException, status, Body, BackgroundTasks, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from loguru import logger
import os
# from app.utils.scheduler import SchedulerService # Больше не нужно, т.к. scheduler_service импортируется
# import requests # Не используется в текущем коде
# from app.api.integration import telegram_plugin as global_telegram_plugin # УДАЛЯЕМ СТАРЫЙ ЦИКЛИЧЕСКИЙ ИМПОРТ

# ИМПОРТИРУЕМ ГЛОБАЛЬНЫЕ ЭКЗЕМПЛЯРЫ ИЗ dependencies.py
from app.core.dependencies import scheduler_service, telegram_plugin as global_telegram_plugin # Используем тот же alias

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

# Настройка логирования (можно оставить, если нужен отдельный лог для этого API)
# os.makedirs("logs", exist_ok=True)
# logger.add("logs/scheduler_api.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

# Инициализация планировщика - УДАЛЕНО, ТЕПЕРЬ ИМПОРТИРУЕТСЯ
# scheduler_service = SchedulerService()

# Модели данных
class TestTaskRequest(BaseModel):
    user_id: str
    name: Optional[str] = None
    message: str = Field(..., description="Текст сообщения для отправки")
    channel: str = Field(default="telegram", description="Канал отправки сообщения")

class SchedulerStatusResponse(BaseModel):
    status: str
    running: bool

class TaskBase(BaseModel):
    name: Optional[str] = None
    user_id: str
    trigger_type: str
    trigger_config: Dict[str, Any]
    action_type: str
    action_config: Dict[str, Any]
    enabled: bool = True

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    action_type: Optional[str] = None
    action_config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None

class Task(TaskBase):
    id: str
    created_at: str

# Маршруты API
@router.get("/status", status_code=status.HTTP_200_OK, response_model=SchedulerStatusResponse)
async def get_scheduler_status():
    if not scheduler_service:
        raise HTTPException(status_code=503, detail="Scheduler service is not available.")
    return {
        "status": "active" if scheduler_service.scheduler_running else "stopped",
        "running": scheduler_service.scheduler_running
    }

@router.post("/start", status_code=status.HTTP_200_OK)
async def start_scheduler():
    if not scheduler_service:
        raise HTTPException(status_code=503, detail="Scheduler service is not available.")
    try:
        if scheduler_service.scheduler_running:
            return {"status": "already_running", "message": "Планировщик уже запущен"}
        await scheduler_service.start()
        logger.info("API: планировщик запущен")
        return {"status": "started", "message": "Планировщик успешно запущен"}
    except Exception as e:
        logger.error(f"Ошибка при запуске планировщика: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при запуске планировщика: {str(e)}")

@router.post("/stop", status_code=status.HTTP_200_OK)
async def stop_scheduler():
    if not scheduler_service:
        raise HTTPException(status_code=503, detail="Scheduler service is not available.")
    try:
        if not scheduler_service.scheduler_running:
            return {"status": "already_stopped", "message": "Планировщик уже остановлен"}
        await scheduler_service.stop()
        logger.info("API: планировщик остановлен")
        return {"status": "stopped", "message": "Планировщик успешно остановлен"}
    except Exception as e:
        logger.error(f"Ошибка при остановке планировщика: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при остановке планировщика: {str(e)}")

@router.post("/test-notification", status_code=status.HTTP_200_OK)
async def send_test_notification(request: TestTaskRequest = Body(...)):
    try:
        logger.info(f"Начало обработки запроса test-notification: {request}")
        user_id = request.user_id
        message = request.message
        channel = request.channel
        
        if channel == "telegram":
            if not global_telegram_plugin: # Проверяем импортированный экземпляр
                logger.error("global_telegram_plugin не доступен или не инициализирован корректно.")
                raise HTTPException(status_code=500, detail="TelegramPlugin не инициализирован.")
            try:
                chat_id_str = os.getenv("TEST_TELEGRAM_CHAT_ID")
                # Важно: Убеждаемся, что user_id действительно является chat_id для этого тестового эндпоинта
                # или используем TEST_TELEGRAM_CHAT_ID
                final_chat_id = None
                if user_id.isdigit():
                    final_chat_id = int(user_id)
                elif chat_id_str:
                    final_chat_id = int(chat_id_str)
                
                if final_chat_id is None:
                    logger.error("TEST_TELEGRAM_CHAT_ID не установлен, а user_id не является числом.")
                    raise HTTPException(status_code=500, detail="Не удалось определить chat_id для тестового уведомления.")

                logger.info(f"Попытка отправки сообщения через global_telegram_plugin пользователю {final_chat_id}")
                # Предполагаем, что global_telegram_plugin имеет метод send_message или аналогичный
                # В app.plugins.telegram_plugin.py это handle_step_send_message, который ожидает step_data и context
                # Адаптируем вызов или убедимся, что у плагина есть более простой метод для прямой отправки.
                # Для простоты, если у плагина есть self.app.bot.send_message:
                if hasattr(global_telegram_plugin, 'app') and hasattr(global_telegram_plugin.app, 'bot'):
                    await global_telegram_plugin.app.bot.send_message(chat_id=final_chat_id, text=message)
                    logger.info(f"Сообщение успешно отправлено пользователю {final_chat_id} через global_telegram_plugin.")
                    return {"status": "success", "message": "Сообщение успешно отправлено"}
                else:
                    # Если такого прямого метода нет, можно вызвать handle_step_send_message, 
                    # но это требует подготовки step_data и context.
                    # Это немного сложнее для простого /test-notification.
                    # Пока оставим так, предполагая, что прямой вызов возможен, или этот эндпоинт будет доработан.
                    logger.error("global_telegram_plugin.app.bot.send_message не доступен.")
                    raise HTTPException(status_code=500, detail="Метод отправки сообщения в TelegramPlugin не доступен.")

            except HTTPException: 
                raise
            except Exception as e:
                logger.error(f"Ошибка при обработке отправки сообщения: {e}", exc_info=True)
                return {"status": "error", "message": f"Ошибка при обработке отправки: {str(e)}"}
        else:
            return {"status": "error", "message": f"Канал {channel} не поддерживается"}
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при отправке уведомления: {e}", exc_info=True)
        raise HTTPException(status_code=500,detail=f"Непредвиденная ошибка: {str(e)}")

# CRUD для задач (остаются как есть, но используют импортированный scheduler_service)
@router.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    if not scheduler_service:
        raise HTTPException(status_code=503, detail="Scheduler service is not available.")
    try:
        task_id = await scheduler_service.add_task(task.model_dump()) # Используем model_dump() для Pydantic v2
        task_data = await scheduler_service.get_task(task_id)
        if task_data:
            # Убедимся, что возвращаемый формат соответствует модели Task
            # task_data может содержать _id, created_at как строки или datetime, нужно привести к модели
            # Это должно делаться внутри scheduler_service.get_task или здесь
            return Task(id=str(task_data.get("_id", task_id)), **task_data) # Пример приведения
        else:
            raise HTTPException(status_code=500, detail="Ошибка при создании задачи")
    except Exception as e:
        logger.error(f"Ошибка при создании задачи: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks", response_model=List[Task])
async def get_tasks(user_id: Optional[str] = None):
    if not scheduler_service:
        raise HTTPException(status_code=503, detail="Scheduler service is not available.")
    try:
        if user_id:
            tasks_from_db = await scheduler_service.get_tasks_by_user(user_id)
        else:
            tasks_from_db = await scheduler_service.get_all_tasks()
        
        result = []
        for task_doc in tasks_from_db:
            task_id = str(task_doc.pop("_id")) # MongoDB _id в строку
            # Убедимся, что created_at также строка, если модель этого ожидает
            if "created_at" in task_doc and not isinstance(task_doc["created_at"], str):
                task_doc["created_at"] = str(task_doc["created_at"])
            result.append(Task(id=task_id, **task_doc))
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении задач: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    if not scheduler_service:
        raise HTTPException(status_code=503, detail="Scheduler service is not available.")
    try:
        task_data = await scheduler_service.get_task(task_id)
        if not task_data:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        # Приведение к модели Task
        return Task(id=str(task_data.pop("_id", task_id)), **task_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении задачи: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    if not scheduler_service:
        raise HTTPException(status_code=503, detail="Scheduler service is not available.")
    try:
        update_data = task_update.model_dump(exclude_unset=True) # Pydantic v2, exclude_unset для частичного обновления
        success = await scheduler_service.update_task(task_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        updated_task_data = await scheduler_service.get_task(task_id)
        if not updated_task_data:
             raise HTTPException(status_code=404, detail="Обновленная задача не найдена после обновления")
        return Task(id=str(updated_task_data.pop("_id", task_id)), **updated_task_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении задачи: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    if not scheduler_service:
        raise HTTPException(status_code=503, detail="Scheduler service is not available.")
    try:
        success = await scheduler_service.remove_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        return {"status": "Задача удалена"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении задачи: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/migrate-notifications")
async def migrate_notifications(background_tasks: BackgroundTasks):
    if not scheduler_service:
        raise HTTPException(status_code=503, detail="Scheduler service is not available.")
    try:
        background_tasks.add_task(scheduler_service.migrate_old_notifications)
        return {"status": "Миграция уведомлений запущена"}
    except Exception as e:
        logger.error(f"Ошибка при запуске миграции уведомлений: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 