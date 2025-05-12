import os
import requests
from typing import Optional
from loguru import logger

os.makedirs("logs", exist_ok=True)
logger.add("logs/rag_integration.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

class RAGPlugin:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("RAG_URL", "http://92.242.60.87:5002/api")
        logger.add("logs/rag_integration.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

    def search(self, query: str, top_k: int = 5):
        try:
            resp = requests.post(f"{self.base_url}/search", json={"query": query, "top_k": top_k}, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            logger.info({"event": "rag_search", "query": query, "response": data})
            return data.get("results")
        except Exception as e:
            logger.error({"event": "rag_search_error", "error": str(e), "query": query})
            return None

    def answer(self, query: str):
        return self.search(query)

    def enrich_links(self, text: str):
        return text

    def healthcheck(self):
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=10)
            data = resp.json()
            return data.get("status") == "ok"
        except Exception as e:
            logger.error({"event": "rag_healthcheck_error", "error": str(e)})
            return False 