"""
Simple HTTP Plugin - Упрощённый плагин для внешних HTTP запросов

Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
- Только основные HTTP методы: GET, POST, PUT, DELETE
- Минимум зависимостей
- Простая обработка ошибок
- Возврат только нужного контекста
"""

import os
import httpx
from typing import Dict, Any, Optional
from loguru import logger

from app.core.base_plugin import BasePlugin


class SimpleHTTPPlugin(BasePlugin):
    """Простой плагин для HTTP запросов"""
    
    def __init__(self):
        super().__init__("simple_http")
        self.default_timeout = 30.0
        self.default_headers = {
            "User-Agent": "Universal-Agent-Platform/1.0",
            "Content-Type": "application/json"
        }
        logger.info("SimpleHTTPPlugin инициализирован")
    
    async def _do_initialize(self):
        """Инициализация плагина"""
        logger.info("SimpleHTTPPlugin готов к работе")
    
    def register_handlers(self) -> Dict[str, Any]:
        """Регистрация обработчиков шагов"""
        return {
            "http_get": self._handle_http_get,
            "http_post": self._handle_http_post,
            "http_put": self._handle_http_put,
            "http_delete": self._handle_http_delete,
            "http_request": self._handle_http_request  # Универсальный
        }
    
    async def _handle_http_get(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик GET запроса
        
        Параметры:
        - url: URL для запроса (обязательно)
        - headers: дополнительные заголовки (опционально)
        - params: параметры запроса (опционально)
        - timeout: тайм-аут в секундах (опционально)
        - output_var: переменная для сохранения ответа (по умолчанию "http_response")
        """
        params = step_data.get("params", {})
        
        url = self._resolve_value(params.get("url", ""), context)
        headers = params.get("headers", {})
        query_params = params.get("params", {})
        timeout = params.get("timeout", self.default_timeout)
        output_var = params.get("output_var", "http_response")
        
        if not url:
            logger.error("SimpleHTTPPlugin: URL не указан")
            context[output_var] = {"success": False, "error": "URL не указан"}
            return context
        
        # Выполняем GET запрос
        response = await self._make_request("GET", url, headers=headers, params=query_params, timeout=timeout)
        context[output_var] = response
        
        return context
    
    async def _handle_http_post(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик POST запроса
        
        Параметры:
        - url: URL для запроса (обязательно)
        - data: данные для отправки (опционально)
        - json: JSON данные для отправки (опционально)
        - headers: дополнительные заголовки (опционально)
        - timeout: тайм-аут в секундах (опционально)
        - output_var: переменная для сохранения ответа (по умолчанию "http_response")
        """
        params = step_data.get("params", {})
        
        url = self._resolve_value(params.get("url", ""), context)
        data = params.get("data")
        json_data = params.get("json")
        headers = params.get("headers", {})
        timeout = params.get("timeout", self.default_timeout)
        output_var = params.get("output_var", "http_response")
        
        if not url:
            logger.error("SimpleHTTPPlugin: URL не указан")
            context[output_var] = {"success": False, "error": "URL не указан"}
            return context
        
        # Выполняем POST запрос
        response = await self._make_request("POST", url, headers=headers, data=data, json=json_data, timeout=timeout)
        context[output_var] = response
        
        return context
    
    async def _handle_http_put(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик PUT запроса"""
        params = step_data.get("params", {})
        
        url = self._resolve_value(params.get("url", ""), context)
        data = params.get("data")
        json_data = params.get("json")
        headers = params.get("headers", {})
        timeout = params.get("timeout", self.default_timeout)
        output_var = params.get("output_var", "http_response")
        
        if not url:
            context[output_var] = {"success": False, "error": "URL не указан"}
            return context
        
        response = await self._make_request("PUT", url, headers=headers, data=data, json=json_data, timeout=timeout)
        context[output_var] = response
        
        return context
    
    async def _handle_http_delete(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработчик DELETE запроса"""
        params = step_data.get("params", {})
        
        url = self._resolve_value(params.get("url", ""), context)
        headers = params.get("headers", {})
        timeout = params.get("timeout", self.default_timeout)
        output_var = params.get("output_var", "http_response")
        
        if not url:
            context[output_var] = {"success": False, "error": "URL не указан"}
            return context
        
        response = await self._make_request("DELETE", url, headers=headers, timeout=timeout)
        context[output_var] = response
        
        return context
    
    async def _handle_http_request(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Универсальный обработчик HTTP запроса
        
        Параметры:
        - method: HTTP метод (GET, POST, PUT, DELETE)
        - url: URL для запроса (обязательно)
        - headers: заголовки (опционально)
        - params: параметры запроса для GET (опционально)
        - data: данные для отправки (опционально)
        - json: JSON данные для отправки (опционально)
        - timeout: тайм-аут в секундах (опционально)
        - output_var: переменная для сохранения ответа (по умолчанию "http_response")
        """
        params = step_data.get("params", {})
        
        method = params.get("method", "GET").upper()
        url = self._resolve_value(params.get("url", ""), context)
        headers = params.get("headers", {})
        query_params = params.get("params", {})
        data = params.get("data")
        json_data = params.get("json")
        timeout = params.get("timeout", self.default_timeout)
        output_var = params.get("output_var", "http_response")
        
        if not url:
            context[output_var] = {"success": False, "error": "URL не указан"}
            return context
        
        response = await self._make_request(
            method, url, 
            headers=headers, 
            params=query_params, 
            data=data, 
            json=json_data, 
            timeout=timeout
        )
        context[output_var] = response
        
        return context
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Выполнение HTTP запроса"""
        
        # Подготавливаем заголовки
        headers = {**self.default_headers}
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        
        # Логируем запрос
        logger.info(f"🌐 HTTP {method} запрос: {url}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=kwargs.get("params"),
                    data=kwargs.get("data"),
                    json=kwargs.get("json"),
                    timeout=kwargs.get("timeout", self.default_timeout)
                )
                
                # Пытаемся распарсить JSON, если не получается - возвращаем текст
                try:
                    response_data = response.json()
                except:
                    response_data = response.text
                
                result = {
                    "success": response.status_code < 400,
                    "status_code": response.status_code,
                    "data": response_data,
                    "headers": dict(response.headers),
                    "url": str(response.url)
                }
                
                if response.status_code >= 400:
                    result["error"] = f"HTTP {response.status_code}: {response.reason_phrase}"
                    logger.error(f"❌ HTTP ошибка {response.status_code}: {url}")
                else:
                    logger.info(f"✅ HTTP {method} успешно: {url} -> {response.status_code}")
                
                return result
                
        except Exception as e:
            logger.error(f"❌ Ошибка HTTP запроса: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": 0,
                "data": None
            }
    
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
        try:
            # Простой тестовый запрос к httpbin
            response = await self._make_request("GET", "https://httpbin.org/status/200", timeout=5.0)
            return response.get("success", False)
        except Exception:
            return False 