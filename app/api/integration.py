from fastapi import APIRouter, Request, Query, Depends, HTTPException, status, Body
from loguru import logger
import os
from app.integrations.openrouter import openrouter_chat, openrouter_models
from fastapi.responses import JSONResponse
from app.plugins.news_plugin import NewsPlugin
from app.integrations.amocrm_client import AmoCRMClient
from app.plugins.rag_plugin import RAGPlugin
from app.plugins.telegram_plugin import TelegramPlugin
from app.plugins.mongo_storage_plugin import MongoStoragePlugin
from app.plugins.scheduling_plugin import SchedulingPlugin
from app.api.scheduler_updated import scheduler_service as global_scheduler_service
from telegram.ext import Application as TelegramApplicationBuilder
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.scenario_repository import ScenarioRepository, get_scenario_repository
from app.db.agent_repository import AgentRepository, get_agent_repository
from app.core.scenario_executor import ScenarioExecutor
from app.models.user import User
from app.models.scenario import Scenario
from app.models.agent import Agent
from app.db.user_repository import UserRepository, get_user_repository
from app.services.auth.utils import get_current_user_id
from typing import Optional, Dict, Any

# Импортируем глобальные экземпляры из app.core.dependencies
from app.core.dependencies import (
    mongo_storage_plugin,
    scheduling_plugin,
    telegram_plugin,
    telegram_app_instance, # Если нужен сам инстанс Application
    rag_plugin_instance, # <--- ДОБАВЛЕНО
    llm_plugin_instance, # <--- ДОБАВЛЕНО
    # API_BASE_URL, # Если используется здесь, лучше тоже из dependencies
    # MONGO_URI, MONGODB_DATABASE_NAME # Аналогично
)

router = APIRouter(prefix="/integration", tags=["integration"])

os.makedirs("logs", exist_ok=True)
logger.add("logs/llm_integration.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)
logger.add("logs/rag_integration.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)
logger.add("logs/crm_integration.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)
logger.add("logs/telegram_integration.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

news_plugin = NewsPlugin()
rag_plugin = RAGPlugin()

# Получаем настройки Telegram из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TEST_TELEGRAM_CHAT_ID = int(os.getenv("TEST_TELEGRAM_CHAT_ID", "0"))

# --- Инициализация ScenarioExecutor и его зависимостей ---
# Удаляем локальную инициализацию db_client, scenario_repo, agent_repo, т.к. они создаются через Depends в get_scenario_executor
# Удаляем инициализацию mongo_storage_plugin, scheduling_plugin, telegram_plugin, т.к. они импортируются

# API_BASE_URL для ScenarioExecutor будет браться из app.core.dependencies или передан напрямую
# MONGO_URI, MONGODB_DATABASE_NAME также
# Предположим, что API_BASE_URL есть в app.core.dependencies
from app.core.dependencies import API_BASE_URL as CORE_API_BASE_URL # Чтобы не конфликтовать с переменной в этом файле, если она есть

# Инициализация ScenarioExecutor теперь происходит внутри get_scenario_executor
# Локальный экземпляр scenario_executor здесь больше не нужен
# scenario_executor = ScenarioExecutor(...) 

# --- Связывание ScenarioExecutor с telegram_app --- 
# Эту логику лучше перенести в main.py, в startup_event, после того как все инициализировано
# if telegram_app_instance:
#     # get_scenario_executor нужно будет вызвать или адаптировать для получения экземпляра ScenarioExecutor
#     # Это становится сложнее, так как get_scenario_executor - это зависимость FastAPI
#     # Проще передавать сам telegram_app_instance в ScenarioExecutor, если ему это нужно для регистрации обработчиков
#     # Либо ScenarioExecutor должен иметь метод для регистрации себя в bot_data, который вызывается в main.py
#     # Пока что закомментируем, т.к. это требует более глубокой переработки
#     # telegram_app_instance.bot_data["scenario_executor"] = ??? 
#     logger.info("Связывание ScenarioExecutor с telegram_app_instance.bot_data должно происходить в main.py")
# else:
#     logger.warning("telegram_app_instance не был инициализирован, ScenarioExecutor не добавлен в bot_data.")

# Зависимость для получения ScenarioExecutor
# Эта функция теперь будет использовать глобальные плагины
async def get_scenario_executor_dependency(
    user_id: str = Depends(get_current_user_id),
    scenario_repo_dep: ScenarioRepository = Depends(get_scenario_repository),
    agent_repo_dep: AgentRepository = Depends(get_agent_repository),
    user_repo_dep: UserRepository = Depends(get_user_repository)
    # Глобальные плагины будут подставлены напрямую
):
    plugins = {}
    if mongo_storage_plugin:
        plugins["mongo_storage"] = mongo_storage_plugin
    if scheduling_plugin:
        plugins["scheduling"] = scheduling_plugin
    if telegram_plugin:
        plugins["telegram"] = telegram_plugin # Передаем глобальный экземпляр
    
    # Прочие плагины, если они управляются глобально и нужны executor'у
    # if news_plugin: plugins["news"] = news_plugin (если news_plugin тоже глобальный)
    # if rag_plugin: plugins["rag"] = rag_plugin (если rag_plugin тоже глобальный)

    # Передаем глобальные плагины напрямую в конструктор ScenarioExecutor
    # если они требуются и доступны глобально.
    # В текущей версии конструктора ScenarioExecutor они передаются через словарь plugins,
    # но для примера, если бы они были отдельными аргументами:
    # mongo_storage_plugin_instance = mongo_storage_plugin, 
    # scheduling_plugin_instance = scheduling_plugin,
    # telegram_plugin_instance = telegram_plugin
    # Вместо этого, мы передадим их через словарь `plugins` в сам ScenarioExecutor, 
    # а он уже внутри своего __init__ разберет их и сохранит.
    # Однако, конструктор ScenarioExecutor ожидает telegram_plugin, mongo_storage_plugin, scheduling_plugin как именованные аргументы.

    return ScenarioExecutor(
        scenario_repo=scenario_repo_dep,  # ИЗМЕНЕНО
        agent_repo=agent_repo_dep,        # ИЗМЕНЕНО
        # user_repository=user_repo_dep, # УБРАНО
        # plugins=plugins, # Пока закомментируем, т.к. конструктор ожидает плагины именованными аргументами
        api_base_url=CORE_API_BASE_URL, # Используем импортированный из core.dependencies
        # user_id=user_id, # УБРАНО
        # Явное указание плагинов, которые ожидает конструктор ScenarioExecutor
        telegram_plugin=telegram_plugin, # Глобальный экземпляр
        mongo_storage_plugin=mongo_storage_plugin, # Глобальный экземпляр
        scheduling_plugin=scheduling_plugin, # Глобальный экземпляр
        rag_plugin=rag_plugin_instance, # <--- ДОБАВЛЕНО
        llm_plugin=llm_plugin_instance  # <--- ДОБАВЛЕНО
    )

@router.get("/llm/models")
async def llm_models():
    """Получить список моделей OpenRouter с полной информацией (цены, инструменты и т.д.)"""
    try:
        models = await openrouter_models()
        return models
    except Exception as e:
        logger.error({"event": "llm_models_error", "error": str(e)})
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/llm/query")
async def llm_query(request: Request):
    data = await request.json()
    prompt = data.get("prompt")
    use_openrouter = data.get("use_openrouter", False)
    model = data.get("model", "openai/gpt-3.5-turbo")
    extra = {k: v for k, v in data.items() if k not in {"prompt", "use_openrouter", "model"}}
    if use_openrouter:
        try:
            result = await openrouter_chat(prompt, model=model, **extra)
            logger.bind(integration="llm").info({"request": data, "response": result})
            return result
        except Exception as e:
            logger.bind(integration="llm").error({"request": data, "error": str(e)})
            return JSONResponse(status_code=500, content={"error": str(e)})
    logger.bind(integration="llm").info({"request": data, "response": "mock"})
    return {"result": "LLM mock response", "input": data}

@router.post("/rag/query")
async def rag_query(request: Request):
    data = await request.json()
    query = data.get("query")
    top_k = data.get("top_k", 5)
    
    if not query:
        logger.bind(integration="rag").error({"error": "query is required", "request": data})
        return JSONResponse(status_code=400, content={"error": "query is required"})
    
    try:
        if not rag_plugin.healthcheck():
            logger.bind(integration="rag").warning({"event": "rag_mock_fallback", "query": query})
            return {"result": "RAG mock response (сервис недоступен)", "input": data}
        
        results = rag_plugin.search(query, top_k=top_k)
        logger.bind(integration="rag").info({"event": "rag_query", "query": query, "results": results})
        return {"result": results, "input": data}
    except Exception as e:
        logger.bind(integration="rag").error({"event": "rag_error", "error": str(e), "query": query})
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/crm/query")
async def crm_query(request: Request):
    data = await request.json()
    logger.bind(integration="crm").info({"request": data})
    return {"result": "CRM mock response", "input": data}

@router.post("/crm/amocrm/query")
async def crm_amocrm_query(request: Request):
    data = await request.json()
    logger.bind(integration="crm").info({"crm": "amocrm", "request": data})
    return {"result": "amoCRM mock response", "input": data}

@router.get("/crm/amocrm/fields")
async def crm_amocrm_fields(entity: str = "leads"):
    """Получить структуру всех полей amoCRM для выбранной сущности (leads, contacts, companies и т.д.)"""
    client = AmoCRMClient()
    try:
        fields = client.get_fields(entity)
        logger.bind(integration="crm").info({"crm": "amocrm", "entity": entity, "fields_count": len(fields)})
        return fields
    except Exception as e:
        logger.bind(integration="crm").error({"crm": "amocrm", "entity": entity, "error": str(e)})
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/news/latest")
async def news_latest(topic: str = None):
    """Получить последние новости (mock)"""
    result = news_plugin.latest(topic)
    logger.bind(integration="news").info({"event": "news_latest", "topic": topic, "result": result})
    return result

@router.get("/news/search")
async def news_search(query: str):
    """Поиск новостей по запросу (mock)"""
    result = news_plugin.search(query)
    logger.bind(integration="news").info({"event": "news_search", "query": query, "result": result})
    return result

@router.post("/telegram/send")
async def telegram_send(request: Request):
    data = await request.json()
    chat_id = data.get("chat_id")
    text = data.get("text")
    if not chat_id or not text:
        logger.bind(integration="telegram").error({"error": "chat_id and text required", "request": data})
        return JSONResponse(status_code=400, content={"error": "chat_id and text required"})
    try:
        await telegram_plugin.app.bot.send_message(chat_id=chat_id, text=text)
        logger.bind(integration="telegram").info({"event": "telegram_send", "chat_id": chat_id, "text": text})
        return {"status": "ok", "chat_id": chat_id, "text": text}
    except Exception as e:
        logger.bind(integration="telegram").error({"event": "telegram_send_error", "error": str(e), "chat_id": chat_id})
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/telegram/health")
async def telegram_health():
    if not telegram_plugin:
        return {"status": "error", "detail": "TelegramPlugin не инициализирован"}
    ok = await telegram_plugin.healthcheck()
    return {"status": "ok" if ok else "error"}

@router.post("/telegram/send_test")
async def send_telegram_test_message(
    user_id_query: str = Query(..., description="User ID (должен быть chat_id для этого теста)"),
    message: str = Query("Тестовое сообщение из API", description="Текст сообщения"),
):
    if not telegram_plugin: # Используем глобальный telegram_plugin из dependencies
        logger.error("TelegramPlugin не инициализирован.")
        raise HTTPException(status_code=503, detail="TelegramPlugin сервис не доступен")
    try:
        chat_id = int(user_id_query)
    except ValueError:
        raise HTTPException(status_code=400, detail="user_id_query должен быть числовым chat_id")
    try:
        # Адаптируем вызов к handle_step_send_message или используем прямой метод, если есть
        if hasattr(telegram_plugin, 'app') and hasattr(telegram_plugin.app, 'bot'):
            await telegram_plugin.app.bot.send_message(chat_id=chat_id, text=message)
            return {"status": "success", "detail": "Сообщение отправлено через app.bot.send_message"}
        else:
            # Попытка через handle_step_send_message (требует правильной структуры step_data)
            result = await telegram_plugin.handle_step_send_message(
                step_data={"params": {"chat_id": chat_id, "text": message}},
                context={"user_id": str(chat_id)} # Контекст может быть нужен для логики внутри плагина
            )
            if result.get("status") == "success" or result.get("telegram_send_status") == "success":
                return result
            else:
                error_detail = result.get("error", "Неизвестная ошибка при отправке через handle_step_send_message")
                raise HTTPException(status_code=500, detail=error_detail)
    except Exception as e:
        logger.error(f"Исключение при отправке тестового сообщения Telegram: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@router.post("/mongodb/save_test")
async def save_to_mongodb_test(
    collection_name: str = Query("test_collection", description="Имя коллекции"),
    document_data: Dict[str, Any] = Body(..., example={"test_key": "test_value"}, description="Документ для сохранения")
):
    """
    Сохраняет тестовый документ в MongoDB через MongoStoragePlugin.
    """
    if not mongo_storage_plugin: # Используем глобальный mongo_storage_plugin из dependencies
        raise HTTPException(status_code=503, detail="MongoStoragePlugin сервис не доступен")
    
    try:
        result = await mongo_storage_plugin.save_document(
            step_data={"collection_name": collection_name, "document": document_data},
            context={}
        )
        if result.get("status") == "success":
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Ошибка сохранения документа"))
    except Exception as e:
        logger.error(f"Ошибка при тестовом сохранении в MongoDB: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Экспорт telegram_app больше не нужен из этого файла
# telegram_app = telegram_app_instance # УДАЛЕНО 