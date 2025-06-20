"""
🔍 VectorSearchTool - Семантический поиск и RAG функционал

Первый критичный инструмент для конкуренции с OpenAI/Claude.
Предоставляет векторный поиск, индексацию документов и RAG.
"""

import os
import asyncio
from typing import List, Dict, Optional, Any, Union
from pathlib import Path
import tempfile
import hashlib
from dataclasses import dataclass

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    VECTOR_DEPS_AVAILABLE = True
except ImportError:
    VECTOR_DEPS_AVAILABLE = False

from .base_tool import Tool, ToolResult
from .unified_tool_result import ToolResult


@dataclass
class Document:
    """Документ для векторного поиска"""
    content: str
    metadata: Dict[str, Any]
    id: Optional[str] = None
    score: Optional[float] = None


@dataclass
class SearchMatch:
    """Результат поиска"""
    document: Document
    score: float
    rank: int


class VectorSearchTool(Tool):
    """
    🔍 Семантический поиск и RAG функционал
    
    Возможности:
    - Создание векторных коллекций
    - Индексация документов с метаданными  
    - Семантический поиск
    - RAG pipeline интеграция
    """
    
    def __init__(self, 
                 storage_path: Optional[str] = None,
                 embedding_model: str = "all-MiniLM-L6-v2",
                 collection_name: str = "kittycore_default"):
        """
        Инициализация VectorSearchTool
        
        Args:
            storage_path: Путь для хранения векторной БД
            embedding_model: Модель эмбеддингов 
            collection_name: Имя коллекции по умолчанию
        """
        super().__init__(
            name="vector_search",
            description="Семантический поиск и RAG функционал"  
        )
        
        if not VECTOR_DEPS_AVAILABLE:
            raise ImportError(
                "Векторные зависимости не установлены. Выполните:\n"
                "pip install chromadb sentence-transformers"
            )
        
        self.storage_path = storage_path or os.path.join(tempfile.gettempdir(), "kittycore_vectors")
        self.embedding_model_name = embedding_model
        self.default_collection = collection_name
        
        # Инициализация ChromaDB
        self._init_chroma()
        self._init_embedding_model()
        
    def _init_chroma(self):
        """Инициализация ChromaDB клиента"""
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=self.storage_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            print(f"ChromaDB инициализирован: {self.storage_path}")
            
        except Exception as e:
            print(f"Ошибка инициализации ChromaDB: {e}")
            raise
    
    def _init_embedding_model(self):
        """Инициализация модели эмбеддингов"""
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            print(f"Модель эмбеддингов загружена: {self.embedding_model_name}")
            
        except Exception as e:
            print(f"Ошибка загрузки модели эмбеддингов: {e}")
            raise
    
    def get_available_actions(self) -> List[str]:
        """Доступные действия"""
        return [
            "search_documents",
            "add_documents", 
            "create_collection",
            "list_collections",
            "delete_collection",
            "get_collection_stats",
            "similarity_search",
            "hybrid_search"
        ]
    
    async def search_documents(self, 
                             query: str, 
                             collection_name: Optional[str] = None,
                             top_k: int = 5,
                             filter_metadata: Optional[Dict] = None) -> ToolResult:
        """
        Семантический поиск документов
        
        Args:
            query: Поисковый запрос
            collection_name: Имя коллекции 
            top_k: Количество результатов
            filter_metadata: Фильтр по метаданным
        """
        try:
            collection_name = collection_name or self.default_collection
            
            # Получаем коллекцию
            collection = self.chroma_client.get_collection(collection_name)
            
            # Генерируем эмбеддинг запроса
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Выполняем поиск
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata
            )
            
            # Формируем результаты
            matches = []
            if results['documents'][0]:  # Проверяем что есть результаты
                for i, (doc, metadata, distance, doc_id) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0],
                    results['ids'][0]
                )):
                    score = 1.0 - distance  # Конвертируем distance в score
                    document = Document(
                        content=doc,
                        metadata=metadata or {},
                        id=doc_id,
                        score=score
                    )
                    matches.append(SearchMatch(document=document, score=score, rank=i+1))
            
            result_data = {
                "query": query,
                "collection": collection_name,
                "total_matches": len(matches),
                "matches": [
                    {
                        "rank": match.rank,
                        "score": round(match.score, 4),
                        "content": match.document.content,
                        "metadata": match.document.metadata,
                        "id": match.document.id
                    }
                    for match in matches
                ]
            }
            
            return ToolResult(
                success=True,
                data=result_data)
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e))
    
    async def add_documents(self,
                          documents: List[str],
                          metadatas: Optional[List[Dict]] = None,
                          ids: Optional[List[str]] = None,
                          collection_name: Optional[str] = None) -> ToolResult:
        """
        Добавление документов в векторную базу
        
        Args:
            documents: Список текстов документов
            metadatas: Метаданные для каждого документа
            ids: ID документов (автогенерация если не указано)
            collection_name: Имя коллекции
        """
        try:
            collection_name = collection_name or self.default_collection
            
            # Создаём коллекцию если не существует
            await self.create_collection(collection_name)
            
            # Получаем коллекцию
            collection = self.chroma_client.get_collection(collection_name)
            
            # Генерируем ID если не указаны
            if ids is None:
                ids = [
                    hashlib.md5(doc.encode()).hexdigest()
                    for doc in documents
                ]
            
            # Подготавливаем метаданные
            if metadatas is None:
                metadatas = [{"source": "kittycore"} for _ in documents]
            
            # Генерируем эмбеддинги
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Добавляем в коллекцию
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            result_data = {
                "collection": collection_name,
                "added_count": len(documents),
                "document_ids": ids,
                "embedding_model": self.embedding_model_name
            }
            
            return ToolResult(
                success=True,
                data=result_data)
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e))
    
    async def create_collection(self, 
                              collection_name: str,
                              metadata: Optional[Dict] = None) -> ToolResult:
        """
        Создание новой коллекции
        
        Args:
            collection_name: Имя коллекции
            metadata: Метаданные коллекции
        """
        try:
            # Проверяем существование коллекции
            try:
                existing = self.chroma_client.get_collection(collection_name)
                return ToolResult(
                    success=True,
                    data={"collection": collection_name, "status": "already_exists"})
            except:
                pass  # Коллекция не существует, создаём
            
            # Создаём коллекцию
            collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata=metadata or {"created_by": "kittycore", "model": self.embedding_model_name}
            )
            
            result_data = {
                "collection": collection_name,
                "status": "created",
                "metadata": metadata,
                "embedding_model": self.embedding_model_name
            }
            
            return ToolResult(
                success=True,
                data=result_data)
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e))
    
    async def list_collections(self) -> ToolResult:
        """Список всех коллекций"""
        try:
            collections = self.chroma_client.list_collections()
            
            collection_info = []
            for collection in collections:
                try:
                    count = collection.count()
                    collection_info.append({
                        "name": collection.name,
                        "count": count,
                        "metadata": collection.metadata
                    })
                except:
                    collection_info.append({
                        "name": collection.name,
                        "count": 0,
                        "metadata": {}
                    })
            
            return ToolResult(
                success=True,
                data={"collections": collection_info, "total": len(collection_info)})
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e))
    
    async def get_collection_stats(self, collection_name: str) -> ToolResult:
        """Статистика коллекции"""
        try:
            collection = self.chroma_client.get_collection(collection_name)
            
            stats = {
                "name": collection_name,
                "document_count": collection.count(),
                "metadata": collection.metadata,
                "embedding_model": self.embedding_model_name,
                "storage_path": self.storage_path
            }
            
            return ToolResult(
                success=True,
                data=stats)
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e))
    
    def execute(self, **kwargs) -> ToolResult:
        """Синхронная обёртка для execute_action"""
        action = kwargs.pop('action', 'search_documents')  # Используем pop чтобы убрать из kwargs
        return asyncio.run(self.execute_action(action, **kwargs))
    
    def get_schema(self) -> Dict[str, Any]:
        """JSON Schema для VectorSearchTool"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": self.get_available_actions(),
                    "description": "Действие для выполнения"
                },
                "query": {
                    "type": "string", 
                    "description": "Поисковый запрос"
                },
                "collection_name": {
                    "type": "string",
                    "description": "Имя коллекции"
                },
                "top_k": {
                    "type": "integer",
                    "default": 5,
                    "description": "Количество результатов"
                },
                "documents": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Список документов для добавления"
                },
                "metadatas": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Метаданные документов"
                }
            },
            "required": ["action"]
        }
    
    async def execute_action(self, action: str, **kwargs) -> ToolResult:
        """Выполнение действия инструмента"""
        if action == "search_documents":
            return await self.search_documents(**kwargs)
        elif action == "add_documents":
            return await self.add_documents(**kwargs)
        elif action == "create_collection":
            return await self.create_collection(**kwargs)
        elif action == "list_collections":
            return await self.list_collections()
        elif action == "get_collection_stats":
            return await self.get_collection_stats(**kwargs)
        else:
            return ToolResult(
                success=False,
                error=f"Неизвестное действие: {action}")
    
    def __str__(self) -> str:
        return f"VectorSearchTool(model={self.embedding_model_name}, storage={self.storage_path})"