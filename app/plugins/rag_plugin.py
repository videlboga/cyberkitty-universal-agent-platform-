import os
import requests
from typing import Optional, Dict, Any
from loguru import logger
import uuid

from app.plugins.plugin_base import PluginBase

class RAGPlugin(PluginBase):
    def __init__(self, base_url: str = None):
        super().__init__()
        self.base_url = base_url or os.getenv("RAG_URL", "http://rag.cyberkitty.tech/api")
        logger.info(f"RAG плагин инициализирован с URL: {self.base_url}")

    def search(self, query: str, top_k: int = 5):
        """
        Поиск в базе знаний через внешний RAG-сервис.
        
        Args:
            query: Текстовый запрос
            top_k: Количество результатов
            
        Returns:
            Результаты поиска или None в случае ошибки
        """
        try:
            # Генерация уникального session_hash для каждого запроса
            session_hash = str(uuid.uuid4())[:8]
            
            # Формирование запроса в формате внешнего RAG API
            payload = {
                "data": [query, top_k],
                "fn_index": 0,
                "session_hash": session_hash
            }
            
            # Отправка запроса к внешнему RAG
            resp = requests.post(f"{self.base_url}/predict", json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            # Логирование успешного запроса
            logger.info({"event": "rag_search", "query": query, "response": data})
            
            # Извлечение результатов из ответа
            if "results" in data:
                return data["results"]
            else:
                logger.warning({"event": "rag_unexpected_response", "response": data})
                return "RAG mock response (неожиданный формат ответа)"
                
        except Exception as e:
            logger.error({"event": "rag_search_error", "error": str(e), "query": query})
            return "RAG mock response (ошибка запроса)"

    def answer(self, query: str):
        """Получить ответ на вопрос (алиас для search)"""
        return self.search(query)

    def enrich_links(self, text: str):
        """Обогатить текст ссылками (заглушка)"""
        return text

    def healthcheck(self):
        """
        Проверка доступности RAG-сервиса
        
        Returns:
            bool: True если сервис доступен, иначе False
        """
        try:
            # Простой тестовый запрос для проверки доступности
            payload = {
                "data": ["test", 1],
                "fn_index": 0,
                "session_hash": "healthcheck"
            }
            resp = requests.post(f"{self.base_url}/predict", json=payload, timeout=10)
            return resp.status_code == 200
        except Exception as e:
            logger.error({"event": "rag_healthcheck_error", "error": str(e)})
            return False 