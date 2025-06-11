"""
Простой API для Universal Agent Platform.
Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО! Только один endpoint.

Единственный endpoint: POST /simple/channels/{channel_id}/execute
"""

import os
import asyncio
import json
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from loguru import logger
from datetime import datetime, timezone

from app.simple_dependencies import get_global_engine
from app.core.simple_engine import SimpleScenarioEngine
from app.core.scenario_logger import get_scenario_logger


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
    callback_data: Optional[str] = Field(None, description="Данные callback_query для тестирования")


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
    Приоритет загрузки:
    1. MongoDB (новые сценарии)
    2. YAML файлы (scenarios/yaml/)
    3. Хардкодированные сценарии (legacy)
    
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
        engine = await get_global_engine()
        
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
        # Продолжаем поиск в YAML файлах
    
    # Пытаемся загрузить из YAML файлов
    try:
        from app.core.yaml_scenario_loader import yaml_loader
        from pathlib import Path
        
        yaml_path = Path(f"scenarios/yaml/{scenario_id}.yaml")
        if yaml_path.exists():
            logger.info(f"📄 Сценарий {scenario_id} загружен из YAML: {yaml_path}")
            scenario = yaml_loader.load_from_file(str(yaml_path))
            return scenario
            
    except Exception as e:
        logger.error(f"Ошибка загрузки YAML сценария {scenario_id}: {e}")

    # Если ничего не найдено - ошибка
    raise HTTPException(
        status_code=404, 
        detail=f"Сценарий '{scenario_id}' не найден ни в MongoDB, ни в YAML файлах"
    )


async def _ensure_channel_ready(channel_id: str) -> bool:
    """
    Убеждается что канал готов к работе.
    
    НОВАЯ АРХИТЕКТУРА: автоматически запускает канал если нужно!
    
    Args:
        channel_id: ID канала
        
    Returns:
        bool: True если канал готов
    """
    try:
        from app.simple_main import get_channel_manager
        channel_manager = get_channel_manager()
        
        if not channel_manager:
            logger.warning("ChannelManager не инициализирован")
            return False
        
        # Проверяем есть ли канал в памяти
        if channel_id not in channel_manager.channels:
            logger.info(f"🔄 Канал {channel_id} не загружен, загружаю...")
            # Загружаем канал из БД
            success = await channel_manager._load_specific_channel(channel_id)
            if not success:
                logger.warning(f"⚠️ Канал {channel_id} не найден в БД")
                return False
        
        # ИСПРАВЛЕНИЕ: Канал готов если есть глобальный движок
        if not channel_manager.global_engine:
            logger.error("❌ Глобальный движок недоступен")
            return False
        
        # Запускаем поллинг если нужно (для автономных каналов)
        channel_data = channel_manager.channels.get(channel_id)
        if channel_data and channel_data.get("channel_type") == "telegram":
            if channel_id not in channel_manager.polling_tasks:
                logger.info(f"🚀 Запускаю поллинг для канала {channel_id}")
                await channel_manager._start_channel_polling(channel_id, channel_data)
        
        logger.info(f"✅ Канал {channel_id} готов к работе с глобальным движком")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка подготовки канала {channel_id}: {e}")
        return False


# === ENDPOINTS ===

@router.post("/channels/{channel_id}/execute", response_model=ExecuteResponse)
async def execute_channel_scenario(
    channel_id: str,
    request: ExecuteRequest,
    engine: SimpleScenarioEngine = Depends(get_global_engine)
):
    """
    ЕДИНСТВЕННЫЙ API ENDPOINT для выполнения сценариев каналов.
    
    Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
    Один endpoint для всех каналов и сценариев.
    
    НОВАЯ ЛОГИКА: может работать БЕЗ канала в БД если указан scenario_id!
    """
    try:
        logger.info(f"🚀 Выполнение сценария для канала {channel_id}", 
                   user_id=request.user_id, chat_id=request.chat_id, scenario_id=request.scenario_id)
        
        # Загружаем сценарий (приоритет: scenario_id > канал)
        scenario = None
        
        if request.scenario_id:
            # Прямое выполнение по scenario_id (БЕЗ привязки к каналу)
            logger.info(f"📄 Прямое выполнение сценария {request.scenario_id}")
            scenario = await _load_scenario_direct(request.scenario_id)
        else:
            # Выполнение через канал (нужна подготовка канала)
            logger.info(f"📡 Выполнение через канал {channel_id}")
            channel_ready = await _ensure_channel_ready(channel_id)
            if not channel_ready:
                raise HTTPException(status_code=404, detail=f"Канал {channel_id} не найден и scenario_id не указан")
            scenario = await _load_scenario(channel_id, None)
        
        # Подготавливаем контекст
        context = {
            "channel_id": channel_id,
            "user_id": request.user_id,
            "chat_id": request.chat_id,
            "scenario_id": scenario["scenario_id"]
        }
        
        # Добавляем callback_data для тестирования если есть
        if request.callback_data:
            context["callback_data"] = request.callback_data
        
        # Добавляем дополнительный контекст
        if request.context:
            context.update(request.context)
        
        # Выполняем сценарий
        final_context = await engine.execute_scenario(scenario, context)
        
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


async def _load_scenario_direct(scenario_id: str) -> Dict[str, Any]:
    """
    Загружает сценарий напрямую по scenario_id.
    
    ПРОСТАЯ ЛОГИКА: только scenario_id, без канала!
    Приоритет загрузки:
    1. MongoDB (сценарии)
    2. YAML файлы (scenarios/yaml/)
    
    Args:
        scenario_id: ID сценария
        
    Returns:
        Dict: Сценарий в JSON формате
        
    Raises:
        HTTPException: Если сценарий не найден
    """
    # 1. Пытаемся загрузить из MongoDB
    try:
        engine = await get_global_engine()
        
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
            logger.info(f"📋 Сценарий {scenario_id} загружен из MongoDB")
            return result_context["scenario_result"]["scenario"]
    
    except Exception as e:
        logger.error(f"Ошибка загрузки сценария {scenario_id} из MongoDB: {e}")
    
    # 2. Пытаемся загрузить из YAML файлов
    try:
        from app.core.yaml_scenario_loader import yaml_loader
        from pathlib import Path
        
        yaml_path = Path(f"scenarios/yaml/{scenario_id}.yaml")
        if yaml_path.exists():
            logger.info(f"📄 Сценарий {scenario_id} загружен из YAML: {yaml_path}")
            scenario = yaml_loader.load_from_file(str(yaml_path))
            return scenario
            
    except Exception as e:
        logger.error(f"Ошибка загрузки YAML сценария {scenario_id}: {e}")
    
    # Если ничего не найдено - ошибка
    raise HTTPException(
        status_code=404, 
        detail=f"Сценарий '{scenario_id}' не найден ни в MongoDB, ни в YAML файлах"
    )


@router.get("/health")
async def health_check(engine: SimpleScenarioEngine = Depends(get_global_engine)):
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
async def get_info(engine: SimpleScenarioEngine = Depends(get_global_engine)):
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
    warnings: Optional[List[str]] = Field(None, description="Предупреждения от валидатора")


@router.post("/mongo/find", response_model=MongoResponse)
async def mongo_find(
    request: MongoRequest,
    engine: SimpleScenarioEngine = Depends(get_global_engine)
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
            error=result.get("error"),
            warnings=result.get("warnings", [])
        )
    except Exception as e:
        logger.error(f"Ошибка mongo_find: {e}")
        return MongoResponse(success=False, error=str(e))


@router.post("/mongo/insert", response_model=MongoResponse)
async def mongo_insert(
    request: MongoRequest,
    engine: SimpleScenarioEngine = Depends(get_global_engine)
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
            error=result.get("error"),
            warnings=result.get("warnings", [])
        )
    except Exception as e:
        logger.error(f"Ошибка mongo_insert: {e}")
        return MongoResponse(success=False, error=str(e))


@router.post("/mongo/update", response_model=MongoResponse)
async def mongo_update(
    request: MongoRequest,
    engine: SimpleScenarioEngine = Depends(get_global_engine)
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
            error=result.get("error"),
            warnings=result.get("warnings", [])
        )
    except Exception as e:
        logger.error(f"Ошибка mongo_update: {e}")
        return MongoResponse(success=False, error=str(e))


@router.post("/mongo/delete", response_model=MongoResponse)
async def mongo_delete(
    request: MongoRequest,
    engine: SimpleScenarioEngine = Depends(get_global_engine)
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
            error=result.get("error"),
            warnings=result.get("warnings", [])
        )
    except Exception as e:
        logger.error(f"Ошибка mongo_delete: {e}")
        return MongoResponse(success=False, error=str(e))


@router.post("/mongo/save-scenario", response_model=MongoResponse)
async def mongo_save_scenario(
    request: MongoRequest,
    engine: SimpleScenarioEngine = Depends(get_global_engine)
):
    """Сохранение сценария в MongoDB без валидации."""
    try:
        if not request.document:
            raise ValueError("document с данными сценария обязателен")
            
        scenario_data = request.document
        
        logger.info(f"💾 Сохраняем сценарий {scenario_data.get('scenario_id', 'unknown')} без валидации")
        
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
        
        logger.info(f"✅ Сценарий сохранён успешно")
        
        # Обработчик выполнился успешно, если мы дошли до этой точки
        return MongoResponse(
            success=True,
            data={"scenario_id": scenario_data.get("scenario_id")},
            error=None,
            warnings=None
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
    engine: SimpleScenarioEngine = Depends(get_global_engine)
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


# === УПРАВЛЕНИЕ КАНАЛАМИ ===

@router.post("/channels/{channel_id}/start")
async def start_channel(channel_id: str):
    """
    Явно запускает канал.
    
    ПРИМЕЧАНИЕ: execute endpoint теперь автоматически запускает каналы!
    Этот endpoint нужен только для предварительного запуска.
    """
    try:
        logger.info(f"📡 Явный запуск канала {channel_id}")
        
        channel_ready = await _ensure_channel_ready(channel_id)
        
        if channel_ready:
            # Получаем информацию о канале
            from app.simple_main import get_channel_manager
            channel_manager = get_channel_manager()
            channel_data = channel_manager.channels.get(channel_id, {})
            
            return {
                "success": True, 
                "message": f"Канал {channel_id} запущен",
                "channel_type": channel_data.get("channel_type"),
                "start_scenario_id": channel_data.get("start_scenario_id"),
                "auto_polling": channel_id in channel_manager.polling_tasks
            }
        else:
            return {"success": False, "error": f"Не удалось запустить канал {channel_id}"}
            
    except Exception as e:
        logger.error(f"❌ Ошибка запуска канала {channel_id}: {e}")
        return {"success": False, "error": str(e)}

@router.post("/channels/{channel_id}/stop")
async def stop_channel(channel_id: str):
    """Останавливает конкретный канал."""
    try:
        from app.simple_main import get_channel_manager
        channel_manager = get_channel_manager()
        
        if not channel_manager:
            return {"success": False, "error": "ChannelManager не инициализирован"}
        
        await channel_manager._stop_channel_polling(channel_id)
        
        return {"success": True, "message": f"Канал {channel_id} остановлен"}
        
    except Exception as e:
        logger.error(f"❌ Ошибка остановки канала {channel_id}: {e}")
        return {"success": False, "error": str(e)}

@router.post("/channels/{channel_id}/restart")
async def restart_channel(channel_id: str):
    """Перезапускает конкретный канал."""
    try:
        from app.simple_main import get_channel_manager
        channel_manager = get_channel_manager()
        
        if not channel_manager:
            return {"success": False, "error": "ChannelManager не инициализирован"}
        
        # Останавливаем
        await channel_manager._stop_channel_polling(channel_id)
        
        # Перезагружаем из БД
        await channel_manager._load_specific_channel(channel_id)
        
        # Пересоздаем движок
        await channel_manager._create_channel_engine(channel_id)
        
        # Запускаем заново
        channel_data = channel_manager.channels.get(channel_id)
        if channel_data:
            await channel_manager._start_channel_polling(channel_id, channel_data)
            return {
                "success": True, 
                "message": f"Канал {channel_id} перезапущен",
                "channel_type": channel_data.get("channel_type"),
                "start_scenario_id": channel_data.get("start_scenario_id")
            }
        else:
            return {"success": False, "error": f"Канал {channel_id} не найден в БД"}
            
    except Exception as e:
        logger.error(f"❌ Ошибка перезапуска канала {channel_id}: {e}")
        return {"success": False, "error": str(e)}

@router.get("/channels")
async def list_channels():
    """
    Получает список всех каналов.
    
    Returns:
        Dict: Список каналов с их статусами
    """
    try:
        from app.simple_main import get_channel_manager
        channel_manager = get_channel_manager()
        
        if not channel_manager:
            return {"success": False, "error": "ChannelManager не инициализирован"}
        
        channels_info = []
        for channel_id, channel_data in channel_manager.channels.items():
            channels_info.append({
                "channel_id": channel_id,
                "type": channel_data.get("channel_type", "unknown"),
                "status": "active" if channel_id in channel_manager.active_channels else "inactive",
                "description": channel_data.get("description", ""),
                "config": channel_data.get("config", {})
            })
        
        return {
            "success": True,
            "channels": channels_info,
            "total": len(channels_info)
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения списка каналов: {e}")
        return {"success": False, "error": str(e)}

@router.post("/channels/reload")
async def reload_channels():
    """
    Динамически перезагружает все каналы из базы данных.
    
    Returns:
        Dict: Результат перезагрузки каналов
    """
    try:
        from app.simple_main import get_channel_manager
        channel_manager = get_channel_manager()
        
        if not channel_manager:
            return {"success": False, "error": "ChannelManager не инициализирован"}
        
        logger.info("🔄 Начинаю динамическую перезагрузку каналов...")
        
        # Останавливаем все активные каналы
        stopped_channels = []
        for channel_id in list(channel_manager.active_channels.keys()):
            try:
                await channel_manager.stop_channel(channel_id)
                stopped_channels.append(channel_id)
                logger.info(f"⏹️ Канал {channel_id} остановлен")
            except Exception as e:
                logger.error(f"Ошибка остановки канала {channel_id}: {e}")
        
        # Очищаем кэш каналов
        channel_manager.channels.clear()
        channel_manager.active_channels.clear()
        
        # Перезагружаем каналы из БД
        await channel_manager._load_channels_from_db()
        
        # Запускаем поллинг для всех каналов
        started_channels = []
        for channel_id, channel_data in channel_manager.channels.items():
            try:
                await channel_manager._start_channel_polling(channel_id, channel_data)
                started_channels.append(channel_id)
                logger.info(f"🚀 Канал {channel_id} запущен")
            except Exception as e:
                logger.error(f"Ошибка запуска канала {channel_id}: {e}")
        
        logger.info(f"✅ Перезагрузка каналов завершена. Остановлено: {len(stopped_channels)}, Запущено: {len(started_channels)}")
        
        return {
            "success": True,
            "message": "Каналы успешно перезагружены",
            "stopped_channels": stopped_channels,
            "started_channels": started_channels,
            "total_channels": len(channel_manager.channels)
        }
        
    except Exception as e:
        logger.error(f"Ошибка перезагрузки каналов: {e}")
        return {"success": False, "error": str(e)}

@router.post("/channels/{channel_id}/reload")
async def reload_specific_channel(channel_id: str):
    """
    Динамически перезагружает конкретный канал из базы данных.
    
    Args:
        channel_id: ID канала для перезагрузки
        
    Returns:
        Dict: Результат перезагрузки канала
    """
    try:
        from app.simple_main import get_channel_manager
        channel_manager = get_channel_manager()
        
        if not channel_manager:
            return {"success": False, "error": "ChannelManager не инициализирован"}
        
        logger.info(f"🔄 Начинаю перезагрузку канала {channel_id}...")
        
        # Останавливаем канал если он активен
        if channel_id in channel_manager.active_channels:
            try:
                await channel_manager.stop_channel(channel_id)
                logger.info(f"⏹️ Канал {channel_id} остановлен")
            except Exception as e:
                logger.error(f"Ошибка остановки канала {channel_id}: {e}")
        
        # Удаляем из кэша
        if channel_id in channel_manager.channels:
            del channel_manager.channels[channel_id]
        
        # Перезагружаем канал из БД
        success = await channel_manager._load_specific_channel(channel_id)
        
        if not success:
            return {
                "success": False, 
                "error": f"Канал {channel_id} не найден в базе данных"
            }
        
        # Запускаем канал
        channel_data = channel_manager.channels.get(channel_id)
        if channel_data:
            try:
                await channel_manager._start_channel_polling(channel_id, channel_data)
                logger.info(f"🚀 Канал {channel_id} запущен")
                
                return {
                    "success": True,
                    "message": f"Канал {channel_id} успешно перезагружен",
                    "channel_data": {
                        "channel_id": channel_id,
                        "type": channel_data.get("channel_type", "unknown"),
                        "status": "active",
                        "description": channel_data.get("description", "")
                    }
                }
            except Exception as e:
                logger.error(f"Ошибка запуска канала {channel_id}: {e}")
                return {
                    "success": False,
                    "error": f"Канал загружен, но не удалось запустить: {str(e)}"
                }
        else:
            return {
                "success": False,
                "error": f"Канал {channel_id} загружен, но данные недоступны"
            }
        
    except Exception as e:
        logger.error(f"Ошибка перезагрузки канала {channel_id}: {e}")
        return {"success": False, "error": str(e)}

@router.post("/api/v1/simple/amocrm/setup")
async def setup_amocrm_plugin(
    settings_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Настройка AmoCRM плагина.
    
    Автоматически:
    1. Сохраняет настройки в MongoDB
    2. Инициализирует плагин
    3. Загружает карту полей
    4. Тестирует подключение
    
    Payload:
    {
        "domain": "example.amocrm.ru",
        "client_id": "your_client_id", 
        "client_secret": "your_client_secret",
        "redirect_uri": "your_redirect_uri",
        "access_token": "your_access_token",
        "refresh_token": "your_refresh_token"
    }
    """
    try:
        # 1. Валидация обязательных полей
        required_fields = ["domain", "client_id", "client_secret", "access_token"]
        missing_fields = [field for field in required_fields if not settings_data.get(field)]
        
        if missing_fields:
            return {
                "success": False,
                "error": f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
            }
        
        # 2. Создаем движок для выполнения операций
        engine = await get_global_engine()
        
        # 3. Сохраняем настройки в MongoDB
        save_settings_step = {
            "id": "save_amocrm_settings",
            "type": "mongo_upsert_document",
            "params": {
                "collection": "plugin_settings",
                "filter": {"plugin_name": "simple_amocrm"},
                "document": {
                    "plugin_name": "simple_amocrm",
                    "settings": settings_data,
                    "updated_at": datetime.now().isoformat(),
                    "enabled": True
                }
            }
        }
        
        context = {}
        await engine.execute_step(save_settings_step, context)
        
        # 4. Получаем свежий экземпляр плагина из движка
        if "simple_amocrm" not in engine.plugins:
            return {
                "success": False,
                "error": "AmoCRM плагин не зарегистрирован в движке"
            }
        
        amocrm_plugin = engine.plugins["simple_amocrm"]
        
        # 5. Форсируем обновление настроек плагина
        await amocrm_plugin._ensure_fresh_settings()
        
        # 6. Тестируем подключение
        healthcheck_result = await amocrm_plugin.healthcheck()
        
        if not healthcheck_result:
            # Получаем детали ошибки из плагина
            test_step = {
                "id": "test_connection",
                "type": "amocrm_get_account",
                "params": {}
            }
            
            test_context = {}
            try:
                await engine.execute_step(test_step, test_context)
                test_success = test_context.get("amocrm_get_account", {}).get("success", False)
                if not test_success:
                    return {
                        "success": False,
                        "error": "Не удалось подключиться к AmoCRM. Проверьте настройки.",
                        "details": test_context.get("amocrm_get_account", {})
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Ошибка тестирования подключения: {str(e)}"
                }
        
        # 7. Загружаем карту полей для всех сущностей
        field_mapping = {}
        entities = ["contacts", "leads", "companies"]
        
        for entity in entities:
            try:
                load_fields_step = {
                    "id": f"load_{entity}_fields",
                    "type": "amocrm_get_custom_fields",
                    "params": {
                        "entity_type": entity,
                        "output_var": f"{entity}_fields"
                    }
                }
                
                fields_context = {}
                await engine.execute_step(load_fields_step, fields_context)
                
                fields_result = fields_context.get(f"{entity}_fields", {})
                if fields_result.get("success"):
                    field_mapping[entity] = fields_result.get("data", [])
                else:
                    logger.warning(f"Не удалось загрузить поля для {entity}: {fields_result.get('error')}")
                    field_mapping[entity] = []
                    
            except Exception as e:
                logger.error(f"Ошибка загрузки полей для {entity}: {e}")
                field_mapping[entity] = []
        
        # 8. Сохраняем карту полей в MongoDB
        save_fields_step = {
            "id": "save_field_mapping",
            "type": "mongo_upsert_document", 
            "params": {
                "collection": "amocrm_field_mapping",
                "filter": {"domain": settings_data["domain"]},
                "document": {
                    "domain": settings_data["domain"],
                    "field_mapping": field_mapping,
                    "updated_at": datetime.now().isoformat()
                }
            }
        }
        
        await engine.execute_step(save_fields_step, context)
        
        # 9. Финальная проверка
        final_healthcheck = await amocrm_plugin.healthcheck()
        
        return {
            "success": True,
            "message": "AmoCRM плагин успешно настроен",
            "details": {
                "domain": settings_data["domain"],
                "healthcheck_passed": final_healthcheck,
                "field_mapping_loaded": len(field_mapping),
                "entities_mapped": list(field_mapping.keys()),
                "total_fields": sum(len(fields) for fields in field_mapping.values())
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка настройки AmoCRM: {e}")
        return {
            "success": False,
            "error": f"Ошибка настройки AmoCRM: {str(e)}"
        }

@router.get("/api/v1/simple/amocrm/status")
async def get_amocrm_status() -> Dict[str, Any]:
    """
    Получение текущего статуса AmoCRM плагина.
    
    Возвращает:
    - Состояние настроек
    - Результат healthcheck
    - Информацию о карте полей
    - Статистику использования
    """
    try:
        # Создаем движок
        engine = await get_global_engine()
        
        if "simple_amocrm" not in engine.plugins:
            return {
                "success": False,
                "error": "AmoCRM плагин не зарегистрирован"
            }
        
        amocrm_plugin = engine.plugins["simple_amocrm"]
        
        # Получаем настройки из MongoDB
        get_settings_step = {
            "id": "get_amocrm_settings",
            "type": "mongo_find_one_document",
            "params": {
                "collection": "plugin_settings",
                "filter": {"plugin_name": "simple_amocrm"},
                "output_var": "settings_doc"
            }
        }
        
        context = {}
        await engine.execute_step(get_settings_step, context)
        
        settings_doc = context.get("settings_doc", {}).get("data")
        has_settings = bool(settings_doc)
        
        # Проверяем healthcheck
        healthcheck_result = await amocrm_plugin.healthcheck()
        
        # Получаем карту полей
        get_fields_step = {
            "id": "get_field_mapping",
            "type": "mongo_find_one_document",
            "params": {
                "collection": "amocrm_field_mapping",
                "filter": {"domain": settings_doc.get("settings", {}).get("domain") if settings_doc else ""},
                "output_var": "fields_doc"
            }
        }
        
        await engine.execute_step(get_fields_step, context)
        
        fields_doc = context.get("fields_doc", {}).get("data")
        has_field_mapping = bool(fields_doc)
        
        field_stats = {}
        if fields_doc:
            field_mapping = fields_doc.get("field_mapping", {})
            field_stats = {
                entity: len(fields) 
                for entity, fields in field_mapping.items()
            }
        
        # Формируем ответ
        status = {
            "success": True,
            "plugin_registered": True,
            "has_settings": has_settings,
            "healthcheck_passed": healthcheck_result,
            "has_field_mapping": has_field_mapping,
            "domain": settings_doc.get("settings", {}).get("domain") if settings_doc else None,
            "settings_updated": settings_doc.get("updated_at") if settings_doc else None,
            "fields_updated": fields_doc.get("updated_at") if fields_doc else None,
            "field_stats": field_stats
        }
        
        # Добавляем рекомендации
        recommendations = []
        if not has_settings:
            recommendations.append("Настройте AmoCRM через /api/v1/simple/amocrm/setup")
        elif not healthcheck_result:
            recommendations.append("Проверьте настройки подключения к AmoCRM")
        elif not has_field_mapping:
            recommendations.append("Обновите карту полей через /api/v1/simple/amocrm/setup")
        
        status["recommendations"] = recommendations
        status["ready_for_use"] = has_settings and healthcheck_result and has_field_mapping
        
        return status
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения статуса AmoCRM: {e}")
        return {
            "success": False,
            "error": f"Ошибка получения статуса: {str(e)}"
        }

@router.get("/scenario-logs/active")
async def get_active_scenario_logs():
    """Получение списка активных выполнений сценариев."""
    try:
        scenario_logger = get_scenario_logger()
        active_scenarios = scenario_logger.get_active_scenarios()
        
        # Конвертируем в сериализуемый формат
        result = []
        for scenario_log in active_scenarios:
            result.append({
                "execution_id": scenario_log.execution_id,
                "scenario_id": scenario_log.scenario_id,
                "user_id": scenario_log.user_id,
                "chat_id": scenario_log.chat_id,
                "channel_id": scenario_log.channel_id,
                "status": scenario_log.status,
                "started_at": scenario_log.started_at.isoformat(),
                "duration_ms": (datetime.now(timezone.utc) - scenario_log.started_at).total_seconds() * 1000,
                "total_steps": scenario_log.total_steps,
                "completed_steps": scenario_log.completed_steps,
                "current_step": scenario_log.steps[-1].step_id if scenario_log.steps else None
            })
        
        return {
            "success": True,
            "active_scenarios": result,
            "count": len(result)
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения активных логов сценариев: {e}")
        return {
            "success": False,
            "error": str(e),
            "active_scenarios": [],
            "count": 0
        }

@router.get("/scenario-logs/{execution_id}")
async def get_scenario_log_details(execution_id: str):
    """Получение детальной информации о выполнении сценария."""
    try:
        scenario_logger = get_scenario_logger()
        status = scenario_logger.get_scenario_status(execution_id)
        
        if not status:
            return {
                "success": False,
                "error": f"Выполнение {execution_id} не найдено или завершено",
                "log": None
            }
        
        # Получаем полный лог из активных сценариев
        active_scenarios = scenario_logger.get_active_scenarios()
        scenario_log = None
        
        for log in active_scenarios:
            if log.execution_id == execution_id:
                scenario_log = log
                break
        
        if not scenario_log:
            return {
                "success": False,
                "error": f"Детали выполнения {execution_id} не найдены",
                "log": None
            }
        
        # Конвертируем в сериализуемый формат
        steps_data = []
        for step in scenario_log.steps:
            step_data = {
                "step_id": step.step_id,
                "step_type": step.step_type,
                "started_at": step.started_at.isoformat(),
                "finished_at": step.finished_at.isoformat() if step.finished_at else None,
                "duration_ms": step.duration_ms,
                "status": step.status,
                "error_message": step.error_message
            }
            
            # Добавляем детали если есть
            if step.step_params:
                step_data["params"] = step.step_params
            if step.context_changes:
                step_data["context_changes"] = step.context_changes
                
            steps_data.append(step_data)
        
        result = {
            "execution_id": scenario_log.execution_id,
            "scenario_id": scenario_log.scenario_id,
            "user_id": scenario_log.user_id,
            "chat_id": scenario_log.chat_id,
            "channel_id": scenario_log.channel_id,
            "status": scenario_log.status,
            "started_at": scenario_log.started_at.isoformat(),
            "finished_at": scenario_log.finished_at.isoformat() if scenario_log.finished_at else None,
            "duration_ms": scenario_log.duration_ms,
            "total_steps": scenario_log.total_steps,
            "completed_steps": scenario_log.completed_steps,
            "initial_context": scenario_log.initial_context,
            "final_context": scenario_log.final_context,
            "steps": steps_data,
            "performance_metrics": scenario_log.performance_metrics
        }
        
        return {
            "success": True,
            "log": result
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения деталей лога сценария: {e}")
        return {
            "success": False,
            "error": str(e),
            "log": None
        }

@router.get("/scenario-logs/history")
async def get_scenario_logs_history(
    limit: int = 50,
    scenario_id: Optional[str] = None,
    user_id: Optional[str] = None,
    engine: SimpleScenarioEngine = Depends(get_global_engine)
):
    """Получение истории выполнения сценариев из MongoDB."""
    try:
        mongo_plugin = engine.plugins.get("mongo")
        if not mongo_plugin:
            return {
                "success": False,
                "error": "MongoDB плагин недоступен",
                "logs": []
            }
        
        # Формируем фильтр
        filter_query = {}
        if scenario_id:
            filter_query["scenario_id"] = scenario_id
        if user_id:
            filter_query["user_id"] = user_id
        
        # Запрашиваем логи из MongoDB
        context = {
            "collection": "scenario_execution_logs",
            "filter": filter_query,
            "limit": limit,
            "sort": {"started_at": -1}  # Сортировка по убыванию даты
        }
        
        result = await mongo_plugin.find_documents(context)
        
        if result.get("success"):
            logs = result.get("documents", [])
            
            # Обрабатываем логи для удобного отображения
            processed_logs = []
            for log in logs:
                processed_log = {
                    "execution_id": log.get("execution_id"),
                    "scenario_id": log.get("scenario_id"),
                    "user_id": log.get("user_id"),
                    "chat_id": log.get("chat_id"),
                    "channel_id": log.get("channel_id"),
                    "status": log.get("status"),
                    "started_at": log.get("started_at"),
                    "finished_at": log.get("finished_at"),
                    "duration_ms": log.get("duration_ms"),
                    "total_steps": log.get("total_steps"),
                    "completed_steps": log.get("completed_steps"),
                    "performance_metrics": log.get("performance_metrics", {})
                }
                processed_logs.append(processed_log)
            
            return {
                "success": True,
                "logs": processed_logs,
                "count": len(processed_logs),
                "filter": filter_query
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Ошибка запроса к MongoDB"),
                "logs": []
            }
        
    except Exception as e:
        logger.error(f"Ошибка получения истории логов сценариев: {e}")
        return {
            "success": False,
            "error": str(e),
            "logs": []
        } 