"""
Simple LLM Plugin - Упрощённый плагин для работы с языковыми моделями

Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
- Только основные функции: отправка запросов и получение ответов
- Минимум зависимостей
- Простая обработка ошибок
- Возврат только нужного контекста
"""

import os
import json
import httpx
from typing import Dict, Any, Optional
from loguru import logger

from app.core.base_plugin import BasePlugin


class SimpleLLMPlugin(BasePlugin):
    """Простой плагин для работы с LLM через OpenRouter API"""
    
    def __init__(self):
        super().__init__("simple_llm")
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.default_model = os.getenv("LLM_DEFAULT_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
        
        if not self.api_key:
            logger.warning("SimpleLLMPlugin: OPENROUTER_API_KEY не найден")
        else:
            logger.info(f"SimpleLLMPlugin инициализирован с моделью: {self.default_model}")
    
    async def _do_initialize(self):
        """Инициализация плагина"""
        logger.info("SimpleLLMPlugin инициализирован")
    
    def register_handlers(self) -> Dict[str, Any]:
        """Регистрация обработчиков шагов"""
        return {
            "llm_query": self._handle_llm_query,
            "llm_chat": self._handle_llm_chat
        }
    
    async def _handle_llm_query(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага llm_query - простой запрос к LLM
        
        Параметры:
        - prompt: текст запроса (обязательно)
        - model: модель (опционально, по умолчанию из env)
        - system_prompt: системный промпт (опционально)
        - temperature: температура (опционально, по умолчанию 0.7)
        - max_tokens: максимум токенов (опционально, по умолчанию 500)
        - output_var: переменная для сохранения ответа (по умолчанию "llm_response")
        """
        params = step_data.get("params", {})
        
        # Извлекаем параметры с подстановкой из контекста
        prompt = self._resolve_value(params.get("prompt", ""), context)
        model = params.get("model", self.default_model)
        system_prompt = self._resolve_value(params.get("system_prompt", ""), context)
        temperature = params.get("temperature", 0.7)
        max_tokens = params.get("max_tokens", 500)
        output_var = params.get("output_var", "llm_response")
        
        if not prompt:
            logger.error("SimpleLLMPlugin: prompt не указан")
            context[output_var] = {"error": "Prompt не указан"}
            return context
        
        # Выполняем запрос
        response = await self._make_llm_request(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Сохраняем только нужную часть ответа в контекст
        if response.get("success"):
            context[output_var] = response["content"]
            logger.info(f"LLM ответ сохранён в {output_var}: {response['content'][:100]}...")
        else:
            context[output_var] = {"error": response.get("error", "Неизвестная ошибка")}
            logger.error(f"Ошибка LLM: {response.get('error')}")
        
        return context
    
    async def _handle_llm_chat(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага llm_chat - чат с историей сообщений
        
        Параметры:
        - messages: список сообщений [{"role": "user/assistant", "content": "..."}]
        - model: модель (опционально)
        - temperature: температура (опционально)
        - max_tokens: максимум токенов (опционально)
        - output_var: переменная для сохранения ответа (по умолчанию "llm_response")
        """
        params = step_data.get("params", {})
        
        messages = params.get("messages", [])
        model = params.get("model", self.default_model)
        temperature = params.get("temperature", 0.7)
        max_tokens = params.get("max_tokens", 500)
        output_var = params.get("output_var", "llm_response")
        
        if not messages:
            logger.error("SimpleLLMPlugin: messages не указаны")
            context[output_var] = {"error": "Messages не указаны"}
            return context
        
        # Разрешаем плейсхолдеры в сообщениях
        resolved_messages = []
        for msg in messages:
            resolved_msg = {
                "role": msg.get("role", "user"),
                "content": self._resolve_value(msg.get("content", ""), context)
            }
            resolved_messages.append(resolved_msg)
        
        # Выполняем запрос
        response = await self._make_llm_request(
            messages=resolved_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Сохраняем ответ
        if response.get("success"):
            context[output_var] = response["content"]
            logger.info(f"LLM чат ответ сохранён в {output_var}")
        else:
            context[output_var] = {"error": response.get("error", "Неизвестная ошибка")}
            logger.error(f"Ошибка LLM чата: {response.get('error')}")
        
        return context
    
    async def _make_llm_request(self, prompt: str = None, messages: list = None, 
                               model: str = None, system_prompt: str = None,
                               temperature: float = 0.7, max_tokens: int = 500) -> Dict[str, Any]:
        """Выполнение HTTP запроса к LLM API"""
        
        if not self.api_key:
            return {"success": False, "error": "API ключ не настроен"}
        
        # Формируем сообщения
        if messages:
            request_messages = messages
        elif prompt:
            request_messages = []
            if system_prompt:
                request_messages.append({"role": "system", "content": system_prompt})
            request_messages.append({"role": "user", "content": prompt})
        else:
            return {"success": False, "error": "Не указан prompt или messages"}
        
        # Формируем payload
        payload = {
            "model": model or self.default_model,
            "messages": request_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Выполняем HTTP запрос
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://universal-agent-platform.local",
                        "X-Title": "Universal Agent Platform"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Извлекаем только текст ответа
                    if data.get("choices") and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"]
                        return {"success": True, "content": content}
                    else:
                        return {"success": False, "error": "Пустой ответ от API"}
                else:
                    error_text = response.text
                    logger.error(f"LLM API ошибка {response.status_code}: {error_text}")
                    return {"success": False, "error": f"API ошибка {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Ошибка запроса к LLM: {e}")
            return {"success": False, "error": str(e)}
    
    def _resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Простая подстановка значений из контекста"""
        if isinstance(value, str) and "{" in value and "}" in value:
            try:
                return value.format(**context)
            except (KeyError, ValueError) as e:
                logger.warning(f"Не удалось разрешить '{value}': {e}")
                return value
        return value
    
    async def healthcheck(self) -> bool:
        """Проверка здоровья плагина"""
        if not self.api_key:
            return False
        
        try:
            # Простой тестовый запрос
            response = await self._make_llm_request(
                prompt="test",
                max_tokens=1
            )
            return response.get("success", False)
        except Exception:
            return False 