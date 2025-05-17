from fastapi import APIRouter, HTTPException, status, Body, BackgroundTasks, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from loguru import logger
import os
from app.utils.scheduler import SchedulerService

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/scheduler_api.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

# Инициализация планировщика
scheduler_service = SchedulerService()

# Модели данных
class TestNotificationRequest(BaseModel):
    user_id: str
    notification_type: str = Field(..., description="Тип уведомления: morning, evening, weekly")

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
    """
    Получить текущий статус планировщика
    """
    return {
        "status": "active" if scheduler_service.scheduler_running else "stopped",
        "running": scheduler_service.scheduler_running
    }

@router.post("/start", status_code=status.HTTP_200_OK)
async def start_scheduler():
    """
    Запустить планировщик задач
    """
    try:
        if scheduler_service.scheduler_running:
            return {"status": "already_running", "message": "Планировщик уже запущен"}
        
        await scheduler_service.start()
        logger.info("API: планировщик запущен")
        return {"status": "started", "message": "Планировщик успешно запущен"}
    except Exception as e:
        logger.error(f"Ошибка при запуске планировщика: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при запуске планировщика: {str(e)}"
        )

@router.post("/stop", status_code=status.HTTP_200_OK)
async def stop_scheduler():
    """
    Остановить планировщик задач
    """
    try:
        if not scheduler_service.scheduler_running:
            return {"status": "already_stopped", "message": "Планировщик уже остановлен"}
        
        await scheduler_service.stop()
        logger.info("API: планировщик остановлен")
        return {"status": "stopped", "message": "Планировщик успешно остановлен"}
    except Exception as e:
        logger.error(f"Ошибка при остановке планировщика: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при остановке планировщика: {str(e)}"
        )

@router.post("/test-notification", status_code=status.HTTP_200_OK)
async def send_test_notification(request: TestNotificationRequest = Body(...)):
    """
    Отправить тестовое уведомление указанного типа
    """
    try:
        notification_types = ["morning", "evening", "weekly"]
        
        if request.notification_type not in notification_types:
            raise HTTPException(
                status_code=400,
                detail=f"Неверный тип уведомления. Допустимые типы: {', '.join(notification_types)}"
            )
        
        success = await scheduler_service.send_test_notification(
            request.user_id, 
            request.notification_type
        )
        
        if success:
            logger.info(f"Отправлено тестовое уведомление типа {request.notification_type} пользователю {request.user_id}")
            return {
                "status": "success", 
                "message": f"Тестовое уведомление типа {request.notification_type} успешно отправлено"
            }
        else:
            logger.error(f"Ошибка при отправке тестового уведомления типа {request.notification_type} пользователю {request.user_id}")
            return {
                "status": "error", 
                "message": "Ошибка при отправке тестового уведомления"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при отправке тестового уведомления: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при отправке тестового уведомления: {str(e)}"
        )

@router.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    """Создать новую задачу"""
    try:
        task_id = await scheduler_service.add_task(task.dict())
        task_data = await scheduler_service.get_task(task_id)
        if task_data:
            return {"id": task_id, **task_data}
        else:
            raise HTTPException(status_code=500, detail="Ошибка при создании задачи")
    except Exception as e:
        logger.error(f"Ошибка при создании задачи: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks", response_model=List[Task])
async def get_tasks(user_id: Optional[str] = None):
    """Получить список задач, опционально фильтруя по user_id"""
    try:
        if user_id:
            tasks = await scheduler_service.get_tasks_by_user(user_id)
        else:
            tasks = await scheduler_service.get_all_tasks()
        
        # Преобразуем задачи в формат ответа
        result = []
        for task in tasks:
            task_id = task.pop("id", None)
            if task_id:
                result.append({"id": task_id, **task})
        
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении задач: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Получить задачу по ID"""
    try:
        task = await scheduler_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        return {"id": task_id, **task}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении задачи: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    """Обновить существующую задачу"""
    try:
        # Получаем только непустые поля
        update_data = {k: v for k, v in task_update.dict().items() if v is not None}
        
        # Обновляем задачу
        success = await scheduler_service.update_task(task_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        # Возвращаем обновленную задачу
        task = await scheduler_service.get_task(task_id)
        return {"id": task_id, **task}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении задачи: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Удалить задачу"""
    try:
        success = await scheduler_service.remove_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        return {"status": "Задача удалена"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении задачи: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/migrate-notifications")
async def migrate_notifications(background_tasks: BackgroundTasks):
    """Мигрировать старые уведомления в новый формат задач"""
    try:
        # Запускаем миграцию в фоновом режиме
        background_tasks.add_task(scheduler_service.migrate_old_notifications)
        return {"status": "Миграция уведомлений запущена"}
    except Exception as e:
        logger.error(f"Ошибка при запуске миграции уведомлений: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 