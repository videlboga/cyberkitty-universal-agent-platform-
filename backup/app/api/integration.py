from fastapi import APIRouter, Request, Query
from loguru import logger
import os
from app.integrations.openrouter import openrouter_chat, openrouter_models
from fastapi.responses import JSONResponse
from app.plugins.news_plugin import NewsPlugin
from app.integrations.amocrm_client import AmoCRMClient
from app.plugins.rag_plugin import RAGPlugin
from app.plugins.telegram_plugin import TelegramPlugin
from telegram.ext import Application

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

if not TELEGRAM_BOT_TOKEN:
    logger.warning("TELEGRAM_BOT_TOKEN не найден в переменных окружения. Используется тестовый токен.")
    # Тестовый токен для разработки
    TELEGRAM_BOT_TOKEN = "8020429038:AAEvO8SW0sD5u7ZSdizYruy8JpXXDrjVuxI"
    TEST_TELEGRAM_CHAT_ID = 648981358

telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
telegram_plugin = TelegramPlugin(telegram_app)

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
    ok = await telegram_plugin.healthcheck()
    return {"status": "ok" if ok else "error"} 