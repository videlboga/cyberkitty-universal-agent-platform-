import httpx
import os
from typing import Any, Dict
from loguru import logger
from datetime import datetime

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

# Проверка наличия API ключа
if not OPENROUTER_API_KEY:
    logger.error("OPENROUTER_API_KEY не найден в переменных окружения")
else:
    logger.info(f"OPENROUTER_API_KEY найден: {OPENROUTER_API_KEY[:5]}...{OPENROUTER_API_KEY[-5:] if OPENROUTER_API_KEY and len(OPENROUTER_API_KEY) > 10 else ''}")

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": os.getenv("OPENROUTER_REFERER", "http://localhost:8000"),
    "X-Title": os.getenv("OPENROUTER_X_TITLE", "Universal Agent System")
}

async def openrouter_chat(
    prompt: str = None, 
    model: str = "openai/gpt-3.5-turbo", 
    messages: list = None,
    **kwargs
) -> Dict[str, Any]:
    if not OPENROUTER_API_KEY:
        logger.error("Невозможно выполнить запрос к OpenRouter: отсутствует API ключ")
        return {"error": "API key not found"}
    
    try:
        # Определяем messages для запроса
        if messages:
            # Если передан messages, используем его
            request_messages = messages
            logger.debug(f"Отправка запроса к OpenRouter: модель={model}, кол-во сообщений={len(messages)}")
        elif prompt:
            # Если передан prompt, создаем messages из него
            request_messages = [{"role": "user", "content": prompt}]
            logger.debug(f"Отправка запроса к OpenRouter: модель={model}, длина промпта={len(prompt)}")
        else:
            logger.error("Не указан ни prompt, ни messages для запроса к OpenRouter")
            return {"error": "Either prompt or messages must be provided"}
        
        payload = {
            "model": model,
            "messages": request_messages,
            **kwargs
        }
        
        # --- Новый блок: логируем curl-команду ---
        import json as _json
        # Формируем заголовки для curl как строку
        headers_for_curl = ""
        # Добавляем стандартные заголовки, которые всегда есть в HEADERS
        headers_for_curl += f"-H 'Authorization: Bearer {OPENROUTER_API_KEY}' "
        headers_for_curl += f"-H 'Content-Type: application/json' "
        # Добавляем опциональные заголовки из константы HEADERS, если они там есть
        if "HTTP-Referer" in HEADERS:
            headers_for_curl += f"-H 'HTTP-Referer: {HEADERS['HTTP-Referer']}' "
        if "X-Title" in HEADERS:
            headers_for_curl += f"-H 'X-Title: {HEADERS['X-Title']}' "
        
        curl_cmd = (
            f"curl -X POST {OPENROUTER_URL} "
            f"{headers_for_curl.strip()} " # Убираем лишний пробел в конце, если есть
            f"-d '{_json.dumps(payload, ensure_ascii=False)}'"
        )
        with open("logs/llm_curl.log", "a", encoding="utf-8") as f:
            f.write(f"\n[{model}] {datetime.now().isoformat()}\n{curl_cmd}\n")
        # --- Конец блока ---
        async with httpx.AsyncClient() as client:
            resp = await client.post(OPENROUTER_URL, headers=HEADERS, json=payload, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            logger.debug("Запрос к OpenRouter выполнен успешно")
            return result
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenRouter: {e}")
        return {"error": str(e)}

async def openrouter_models() -> Dict[str, Any]:
    if not OPENROUTER_API_KEY:
        logger.error("Невозможно получить список моделей OpenRouter: отсутствует API ключ")
        return {"error": "API key not found"}
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(OPENROUTER_MODELS_URL, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            logger.debug("Список моделей OpenRouter получен успешно")
            return result
    except Exception as e:
        logger.error(f"Ошибка при получении списка моделей OpenRouter: {e}")
        return {"error": str(e)} 