"""
Простой API для Universal Agent Platform.
Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО! Только один endpoint.

Единственный endpoint: POST /simple/channels/{channel_id}/execute
"""

import os
import asyncio
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from loguru import logger

from app.core.simple_engine import SimpleScenarioEngine, create_engine


def safe_serialize_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Безопасная сериализация контекста без циклических ссылок.
    
    Args:
        context: Исходный контекст
        
    Returns:
        Dict: Очищенный контекст без циклических ссылок
    """
    def is_serializable(obj):
        """Проверяет, можно ли объект сериализовать в JSON."""
        try:
            json.dumps(obj)
            return True
        except (TypeError, ValueError):
            return False
    
    safe_context = {}
    
    for key, value in context.items():
        if is_serializable(value):
            safe_context[key] = value
        else:
            # Для несериализуемых объектов сохраняем только строковое представление
            safe_context[key] = f"<non-serializable: {type(value).__name__}>"
    
    return safe_context


# === СХЕМЫ ДАННЫХ ===

class ExecuteRequest(BaseModel):
    """Запрос на выполнение сценария канала."""
    user_id: Optional[str] = Field(None, description="ID пользователя")
    chat_id: Optional[str] = Field(None, description="ID чата в Telegram")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Дополнительный контекст")
    scenario_id: Optional[str] = Field(None, description="Конкретный сценарий для выполнения")


class ExecuteResponse(BaseModel):
    """Ответ выполнения сценария."""
    success: bool = Field(description="Успешно ли выполнен сценарий")
    scenario_id: str = Field(description="ID выполненного сценария")
    final_context: Dict[str, Any] = Field(description="Финальный контекст")
    message: Optional[str] = Field(None, description="Сообщение о результате")
    error: Optional[str] = Field(None, description="Ошибка, если произошла")


# === ROUTER ===

router = APIRouter(prefix="/simple", tags=["simple"])


# === ЗАГРУЗКА СЦЕНАРИЕВ ===

async def _load_scenario(channel_id: str, scenario_id: str = None) -> Dict[str, Any]:
    """
    Загружает сценарий для канала.
    
    Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
    Использует ChannelMapping вместо сложной модели Agent.
    
    Args:
        channel_id: ID канала
        scenario_id: Конкретный сценарий (опционально)
        
    Returns:
        Dict: Сценарий в JSON формате
        
    Raises:
        HTTPException: Если сценарий не найден
    """
    # Сначала пытаемся загрузить из MongoDB
    try:
        engine = await create_engine()
        
        # Если указан конкретный scenario_id, ищем его
        if scenario_id:
            step = {
                "id": "get_scenario",
                "type": "mongo_get_scenario",
                "params": {
                    "scenario_id": scenario_id,
                    "output_var": "scenario_result"
                }
            }
            context = {}
            result_context = await engine.execute_step(step, context)
            if result_context.get("scenario_result", {}).get("success"):
                return result_context["scenario_result"]["scenario"]
        
        # Иначе ищем маппинг канала и его сценарий
        step = {
            "id": "get_mapping",
            "type": "mongo_get_channel_mapping",
            "params": {
                "channel_id": channel_id,
                "output_var": "mapping_result"
            }
        }
        context = {}
        result_context = await engine.execute_step(step, context)
        
        if result_context.get("mapping_result", {}).get("success"):
            mapping = result_context["mapping_result"]["mapping"]
            mapping_scenario_id = mapping.get("scenario_id")
            
            if mapping_scenario_id:
                # Загружаем сценарий из маппинга
                scenario_step = {
                    "id": "get_scenario",
                    "type": "mongo_get_scenario_by_id",
                    "params": {
                        "scenario_id": mapping_scenario_id,
                        "output_var": "scenario_result"
                    }
                }
                scenario_context = {}
                scenario_result_context = await engine.execute_step(scenario_step, scenario_context)
                
                if scenario_result_context.get("scenario_result", {}).get("success"):
                    return scenario_result_context["scenario_result"]["scenario"]
    
    except Exception as e:
        logger.error(f"Ошибка загрузки сценария из MongoDB: {e}")
        # Если сценарий не найден в БД - ошибка
        raise HTTPException(
            status_code=404, 
            detail=f"Сценарий '{scenario_id}' не найден в базе данных"
        )
    
    # Определяем какой сценарий загружать
    if scenario_id:
        
        # Специальные сценарии для переключения
        if scenario_id == "user_registration_complete":
            return {
                "scenario_id": "user_registration_complete",
                "description": "Завершение регистрации обычного пользователя",
                "initial_context": {
                    "user_type": "user",
                    "registration_complete": True
                },
                "steps": [
                    {
                        "id": "start",
                        "type": "start",
                        "params": {
                            "message": "Завершаем регистрацию обычного пользователя"
                        },
                        "next_step": "success_message"
                    },
                    {
                        "id": "success_message",
                        "type": "telegram_send_message",
                        "params": {
                            "chat_id": "{chat_id}",
                            "text": "✅ <b>Регистрация завершена!</b>\n\nПривет, {user_name}! Вы зарегистрированы как обычный пользователь.\n\n🎯 Доступные возможности:\n• Выполнение сценариев\n• Получение уведомлений\n• Базовые команды бота\n\nИспользуйте /help для получения списка команд.",
                            "parse_mode": "HTML"
                        },
                        "next_step": "main_menu"
                    },
                    {
                        "id": "main_menu",
                        "type": "telegram_send_buttons",
                        "params": {
                            "chat_id": "{chat_id}",
                            "text": "Что хотите сделать?",
                            "buttons": [
                                [{"text": "🚀 Запустить сценарий", "callback_data": "run_scenario"}],
                                [{"text": "📊 Мой профиль", "callback_data": "my_profile"}],
                                [{"text": "❓ Помощь", "callback_data": "help"}]
                            ]
                        },
                        "next_step": "end"
                    },
                    {
                        "id": "end",
                        "type": "end",
                        "params": {
                            "message": "Регистрация пользователя завершена успешно"
                        }
                    }
                ]
            }
        elif scenario_id == "admin_registration_complete":
            return {
                "scenario_id": "admin_registration_complete",
                "description": "Завершение регистрации администратора",
                "initial_context": {
                    "user_type": "admin",
                    "registration_complete": True
                },
                "steps": [
                    {
                        "id": "start",
                        "type": "start",
                        "params": {
                            "message": "Завершаем регистрацию администратора"
                        },
                        "next_step": "success_message"
                    },
                    {
                        "id": "success_message",
                        "type": "telegram_send_message",
                        "params": {
                            "chat_id": "{chat_id}",
                            "text": "👑 <b>Регистрация администратора завершена!</b>\n\nДобро пожаловать, {user_name}! У вас есть полный доступ к системе.\n\n🔧 Административные возможности:\n• Управление ботом\n• Просмотр статистики\n• Создание сценариев\n• Управление пользователями\n• Все пользовательские функции\n\nИспользуйте /admin для доступа к панели администратора.",
                            "parse_mode": "HTML"
                        },
                        "next_step": "admin_menu"
                    },
                    {
                        "id": "admin_menu",
                        "type": "telegram_send_buttons",
                        "params": {
                            "chat_id": "{chat_id}",
                            "text": "Панель администратора:",
                            "buttons": [
                                [{"text": "📊 Статистика", "callback_data": "admin_stats"}],
                                [{"text": "👥 Пользователи", "callback_data": "admin_users"}],
                                [{"text": "🎭 Сценарии", "callback_data": "admin_scenarios"}],
                                [{"text": "⚙️ Настройки", "callback_data": "admin_settings"}],
                                [{"text": "🚀 Запустить сценарий", "callback_data": "run_scenario"}]
                            ]
                        },
                        "next_step": "end"
                    },
                    {
                        "id": "end",
                        "type": "end",
                        "params": {
                            "message": "Регистрация администратора завершена успешно"
                        }
                    }
                ]
            }
        else:
            # Если сценарий не найден в БД - ошибка
            raise HTTPException(
                status_code=404, 
                detail=f"Сценарий '{scenario_id}' не найден в базе данных"
            )
    
    # Если ничего не найдено - ошибка
    raise HTTPException(
        status_code=404, 
        detail=f"Сценарий для канала '{channel_id}' не найден"
    )


# === ENDPOINTS ===

@router.post("/channels/{channel_id}/execute", response_model=ExecuteResponse)
async def execute_channel_scenario(
    channel_id: str,
    request: ExecuteRequest,
    engine: SimpleScenarioEngine = Depends(create_engine)
):
    """
    ЕДИНСТВЕННЫЙ API ENDPOINT для выполнения сценариев каналов.
    
    Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
    Один endpoint для всех каналов и сценариев.
    Использует ChannelMapping вместо сложной модели Agent.
    """
    try:
        logger.info(f"🚀 Выполнение сценария для канала {channel_id}", 
                   user_id=request.user_id, chat_id=request.chat_id)
        
        # Загружаем сценарий
        scenario = await _load_scenario(channel_id, request.scenario_id)
        
        # Подготавливаем контекст
        context = {
            "channel_id": channel_id,
            "user_id": request.user_id,
            "chat_id": request.chat_id,
            "scenario_id": scenario["scenario_id"]
        }
        
        # Добавляем дополнительный контекст
        if request.context:
            context.update(request.context)
        
        # Выполняем сценарий
        final_context = await engine.execute_scenario(scenario, context)
        
        # УПРОЩЕНО: Переключение сценариев теперь обрабатывается внутри движка
        # Никаких дополнительных проверок не требуется
        
        logger.info(f"✅ Сценарий {scenario['scenario_id']} успешно выполнен")
        
        # Безопасная сериализация контекста
        safe_context = safe_serialize_context(final_context)
        
        return ExecuteResponse(
            success=True,
            scenario_id=scenario["scenario_id"],
            final_context=safe_context,
            message=f"Сценарий '{scenario['scenario_id']}' выполнен успешно"
        )
        
    except HTTPException:
        # Перебрасываем HTTP ошибки как есть
        raise
        
    except Exception as e:
        logger.error(f"❌ Ошибка выполнения сценария для канала {channel_id}: {e}")
        
        return ExecuteResponse(
            success=False,
            scenario_id=request.scenario_id or "unknown",
            final_context={},
            error=str(e)
        )


@router.get("/health")
async def health_check(engine: SimpleScenarioEngine = Depends(create_engine)):
    """Проверка здоровья системы."""
    try:
        is_healthy = await engine.healthcheck()
        
        if is_healthy:
            return {
                "status": "healthy",
                "registered_plugins": engine.get_registered_plugins(),
                "registered_handlers": engine.get_registered_handlers()
            }
        else:
            raise HTTPException(status_code=503, detail="Engine healthcheck failed")
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")


@router.get("/info")
async def get_info(engine: SimpleScenarioEngine = Depends(create_engine)):
    """Информация о системе."""
    return {
        "platform": "Universal Agent Platform - Simplified Architecture",
        "version": "2.0.0-simplified",
        "engine": "SimpleScenarioEngine",
        "registered_plugins": engine.get_registered_plugins(),
        "registered_handlers": engine.get_registered_handlers(),
        "principles": [
            "Простота превыше всего",
            "Один движок для всех сценариев", 
            "Минимум зависимостей",
            "Явная передача контекста"
        ]
    }

# === MONGODB ENDPOINTS ===

class MongoRequest(BaseModel):
    """Запрос для MongoDB операций."""
    collection: str = Field(description="Название коллекции")
    filter: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Фильтр для поиска")
    document: Optional[Dict[str, Any]] = Field(None, description="Документ для вставки/обновления")
    scenario_id: Optional[str] = Field(None, description="ID сценария")


class MongoResponse(BaseModel):
    """Ответ MongoDB операции."""
    success: bool = Field(description="Успешно ли выполнена операция")
    data: Optional[Any] = Field(None, description="Данные результата")
    error: Optional[str] = Field(None, description="Ошибка, если произошла")


@router.post("/mongo/find", response_model=MongoResponse)
async def mongo_find(
    request: MongoRequest,
    engine: SimpleScenarioEngine = Depends(create_engine)
):
    """Поиск документов в MongoDB."""
    try:
        step = {
            "id": "find_docs",
            "type": "mongo_find_documents",
            "params": {
                "collection": request.collection,
                "filter": request.filter,
                "output_var": "find_result"
            }
        }
        context = {}
        result_context = await engine.execute_step(step, context)
        
        # Результат находится в переменной find_result
        result = result_context.get("find_result", {})
        
        return MongoResponse(
            success=result.get("success", False),
            data=result.get("documents", []),
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Ошибка mongo_find: {e}")
        return MongoResponse(success=False, error=str(e))


@router.post("/mongo/insert", response_model=MongoResponse)
async def mongo_insert(
    request: MongoRequest,
    engine: SimpleScenarioEngine = Depends(create_engine)
):
    """Вставка документа в MongoDB."""
    try:
        step = {
            "id": "insert_doc",
            "type": "mongo_insert_document",
            "params": {
                "collection": request.collection,
                "document": request.document,
                "output_var": "insert_result"
            }
        }
        context = {}
        result_context = await engine.execute_step(step, context)
        
        # Результат находится в переменной insert_result
        result = result_context.get("insert_result", {})
        
        return MongoResponse(
            success=result.get("success", False),
            data=result.get("inserted_id"),
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Ошибка mongo_insert: {e}")
        return MongoResponse(success=False, error=str(e))


@router.post("/mongo/update", response_model=MongoResponse)
async def mongo_update(
    request: MongoRequest,
    engine: SimpleScenarioEngine = Depends(create_engine)
):
    """Обновление документа в MongoDB."""
    try:
        step = {
            "id": "update_doc",
            "type": "mongo_update_document",
            "params": {
                "collection": request.collection,
                "filter": request.filter,
                "update": request.document,
                "output_var": "update_result"
            }
        }
        context = {}
        result_context = await engine.execute_step(step, context)
        
        # Результат находится в переменной update_result
        result = result_context.get("update_result", {})
        
        return MongoResponse(
            success=result.get("success", False),
            data={
                "modified_count": result.get("modified_count", 0),
                "matched_count": result.get("matched_count", 0)
            },
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Ошибка mongo_update: {e}")
        return MongoResponse(success=False, error=str(e))


@router.post("/mongo/delete", response_model=MongoResponse)
async def mongo_delete(
    request: MongoRequest,
    engine: SimpleScenarioEngine = Depends(create_engine)
):
    """Удаление документа из MongoDB."""
    try:
        step = {
            "id": "delete_doc",
            "type": "mongo_delete_document",
            "params": {
                "collection": request.collection,
                "filter": request.filter,
                "output_var": "delete_result"
            }
        }
        context = {}
        result_context = await engine.execute_step(step, context)
        
        # Результат находится в переменной delete_result
        result = result_context.get("delete_result", {})
        
        return MongoResponse(
            success=result.get("success", False),
            data={"deleted_count": result.get("deleted_count", 0)},
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Ошибка mongo_delete: {e}")
        return MongoResponse(success=False, error=str(e))


@router.post("/mongo/save-scenario", response_model=MongoResponse)
async def mongo_save_scenario(
    request: MongoRequest,
    engine: SimpleScenarioEngine = Depends(create_engine)
):
    """Сохранение сценария в MongoDB."""
    try:
        if not request.document:
            raise ValueError("document с данными сценария обязателен")
            
        scenario_data = request.document
        
        # Создаем step для обработчика
        step = {
            "id": "save_scenario",
            "type": "mongo_save_scenario",
            "params": {
                "scenario": scenario_data
            }
        }
        context = {}
        result_context = await engine.execute_step(step, context)
        
        # Обработчик выполнился успешно, если мы дошли до этой точки
        return MongoResponse(
            success=True,
            data={"scenario_id": scenario_data.get("scenario_id")},
            error=None
        )
    except Exception as e:
        logger.error(f"Ошибка mongo_save_scenario: {e}")
        return MongoResponse(success=False, error=str(e))


# === EXECUTE ENDPOINT ===

class StepRequest(BaseModel):
    """Запрос для выполнения одного шага."""
    step: Dict[str, Any] = Field(description="Данные шага")
    context: Dict[str, Any] = Field(default_factory=dict, description="Контекст выполнения")


class StepResponse(BaseModel):
    """Ответ выполнения шага."""
    success: bool = Field(description="Успешно ли выполнен шаг")
    context: Dict[str, Any] = Field(description="Обновленный контекст")
    error: Optional[str] = Field(None, description="Ошибка, если произошла")


@router.post("/execute", response_model=StepResponse)
async def execute_step(
    request: StepRequest,
    engine: SimpleScenarioEngine = Depends(create_engine)
):
    """Выполнение одного шага сценария."""
    try:
        result_context = await engine.execute_step(request.step, request.context)
        
        # Безопасная сериализация контекста
        safe_context = safe_serialize_context(result_context)
        
        return StepResponse(
            success=True,
            context=safe_context
        )
    except Exception as e:
        logger.error(f"Ошибка execute_step: {e}")
        return StepResponse(
            success=False,
            context=request.context,
            error=str(e)
        ) 