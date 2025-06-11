"""
Simple RAG Plugin - Упрощённый плагин для работы с базой знаний

Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
- Только основные функции: поиск в базе знаний
- Минимум зависимостей
- Простая обработка ошибок
- Возврат только нужного контекста
"""

import os
import httpx
from typing import Dict, Any
from loguru import logger

from app.core.base_plugin import BasePlugin


class SimpleRAGPlugin(BasePlugin):
    """Простой плагин для работы с RAG (Retrieval-Augmented Generation)"""
    
    def __init__(self):
        super().__init__("simple_rag")
        self.base_url = os.getenv("RAG_URL", "https://rag.cyberkitty.tech")
        logger.info(f"SimpleRAGPlugin инициализирован с URL: {self.base_url}")
    
    async def _do_initialize(self):
        """Инициализация плагина"""
        logger.info("SimpleRAGPlugin инициализирован")
    
    def register_handlers(self) -> Dict[str, Any]:
        """Регистрация обработчиков шагов"""
        return {
            "rag_search": self._handle_rag_search,
            "rag_answer": self._handle_rag_answer
        }
    
    async def _handle_rag_search(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага rag_search - поиск в базе знаний
        
        Параметры:
        - query: поисковый запрос (обязательно)
        - top_k: количество результатов (опционально, по умолчанию 5)
        - output_var: переменная для сохранения результатов (по умолчанию "rag_results")
        """
        params = step_data.get("params", {})
        
        # Извлекаем параметры с подстановкой из контекста
        query = self._resolve_value(params.get("query", ""), context)
        top_k = params.get("top_k", 5)
        output_var = params.get("output_var", "rag_results")
        
        if not query:
            logger.error("SimpleRAGPlugin: query не указан")
            context[output_var] = {"error": "Query не указан"}
            return context
        
        # Выполняем поиск
        response = await self._make_rag_request("search", {
            "query": query,
            "top_k": top_k
        })
        
        # Сохраняем результат в контекст
        if response.get("success"):
            context[output_var] = response["data"]
            logger.info(f"RAG поиск выполнен: '{query}' -> {len(response['data'])} результатов")
        else:
            context[output_var] = {"error": response.get("error", "Неизвестная ошибка")}
            logger.error(f"Ошибка RAG поиска: {response.get('error')}")
        
        return context
    
    async def _handle_rag_answer(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага rag_answer - получение ответа на вопрос
        
        Параметры:
        - question: вопрос (обязательно)
        - context_size: размер контекста (опционально, по умолчанию 3)
        - output_var: переменная для сохранения ответа (по умолчанию "rag_answer")
        """
        params = step_data.get("params", {})
        
        # Извлекаем параметры с подстановкой из контекста
        question = self._resolve_value(params.get("question", ""), context)
        context_size = params.get("context_size", 3)
        output_var = params.get("output_var", "rag_answer")
        
        if not question:
            logger.error("SimpleRAGPlugin: question не указан")
            context[output_var] = {"error": "Question не указан"}
            return context
        
        # Выполняем запрос на получение ответа
        response = await self._make_rag_request("answer", {
            "question": question,
            "context_size": context_size
        })
        
        # Сохраняем ответ в контекст
        if response.get("success"):
            # Извлекаем только текст ответа, если он есть
            answer_data = response["data"]
            if isinstance(answer_data, dict) and "answer" in answer_data:
                context[output_var] = answer_data["answer"]
            else:
                context[output_var] = answer_data
            logger.info(f"RAG ответ получен для вопроса: '{question}'")
        else:
            context[output_var] = {"error": response.get("error", "Неизвестная ошибка")}
            logger.error(f"Ошибка RAG ответа: {response.get('error')}")
        
        return context
    
    async def _make_rag_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение HTTP запроса к RAG API"""
        
        url = f"{self.base_url}/api/{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {"success": True, "data": data}
                else:
                    error_text = response.text
                    logger.error(f"RAG API ошибка {response.status_code}: {error_text}")
                    return {"success": False, "error": f"API ошибка {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Ошибка запроса к RAG: {e}")
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
        try:
            # Простой тестовый запрос
            response = await self._make_rag_request("search", {
                "query": "test",
                "top_k": 1
            })
            return response.get("success", False)
        except Exception:
            return False 