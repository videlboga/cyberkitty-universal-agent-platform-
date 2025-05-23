import os
import requests
from typing import Optional, Dict, Any, Callable
from loguru import logger

from app.plugins.plugin_base import PluginBase

class RAGPlugin(PluginBase):
    def __init__(self, base_url: str = None):
        super().__init__()
        # Используем правильный базовый URL без /api на конце
        self.base_url = base_url or os.getenv("RAG_URL", "https://rag.cyberkitty.tech")
        logger.info(f"RAG плагин инициализирован с URL: {self.base_url}")

    def register_step_handlers(self, step_handlers: Dict[str, Callable]):
        """Регистрирует обработчики шагов, предоставляемые этим плагином."""
        step_handlers["rag_search"] = self.handle_rag_search
        logger.info(f"RAGPlugin зарегистрировал обработчик шага: rag_search")

    async def handle_rag_search(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Обработчик шага rag_search"""
        logger.info(f"[RAGPlugin.handle_rag_search] ENTRY. step_data: {step_data}")
        logger.info(f"[RAGPlugin.handle_rag_search] context: {context}")
        
        try:
            params = step_data.get("params", {})
            query = self._resolve_value_from_context(params.get("query", ""), context)
            top_k = params.get("top_k", 5)
            output_var = params.get("output_var", "rag_results")
            
            logger.info(f"[RAGPlugin.handle_rag_search] query: {query}, top_k: {top_k}, output_var: {output_var}")
            
            # Выполняем поиск
            results = self.search(query, top_k)
            
            # Сохраняем результат в контекст
            context[output_var] = results
            logger.info(f"RAG поиск выполнен: запрос='{query}', результат сохранен в {output_var}")
            
        except Exception as e:
            logger.error(f"Ошибка в handle_rag_search: {e}", exc_info=True)
            context["__step_error__"] = str(e)
            # Сохраняем пустой результат
            output_var = step_data.get("params", {}).get("output_var", "rag_results")
            context[output_var] = None

    def _resolve_value_from_context(self, value: Any, context: Dict[str, Any]) -> Any:
        """Подставляет значения из контекста в строковые шаблоны."""
        if isinstance(value, str) and "{" in value and "}" in value:
            try:
                return value.format(**context)
            except KeyError as e:
                logger.warning(f"Переменная {e} не найдена в контексте при разрешении '{value}'")
                return value
        return value

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
            # Формирование запроса в правильном формате
            payload = {
                "query": query,
                "top_k": top_k
            }
            
            # Отправка запроса к правильному endpoint
            url = f"{self.base_url}/api/search"
            logger.info(f"Отправляем запрос к RAG: {url}, payload: {payload}")
            
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            # Логирование успешного запроса
            logger.info({"event": "rag_search_success", "query": query, "response_keys": list(data.keys()) if isinstance(data, dict) else "not_dict"})
            
            # Возвращаем весь ответ - пусть пользователь решает что с ним делать
            return data
                
        except Exception as e:
            logger.error({"event": "rag_search_error", "error": str(e), "query": query})
            return f"RAG поиск недоступен: {str(e)}"

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
                "query": "test",
                "top_k": 1
            }
            url = f"{self.base_url}/api/search"
            resp = requests.post(url, json=payload, timeout=10)
            logger.info(f"RAG healthcheck: status_code={resp.status_code}")
            return resp.status_code == 200
        except Exception as e:
            logger.error({"event": "rag_healthcheck_error", "error": str(e)})
            return False 