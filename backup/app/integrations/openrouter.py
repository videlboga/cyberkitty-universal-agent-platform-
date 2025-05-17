import httpx
import os
from typing import Any, Dict

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

async def openrouter_chat(prompt: str, model: str = "openai/gpt-3.5-turbo", **kwargs) -> Dict[str, Any]:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        **kwargs
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(OPENROUTER_URL, headers=HEADERS, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()

async def openrouter_models() -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPENROUTER_MODELS_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json() 