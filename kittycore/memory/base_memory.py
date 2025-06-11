"""
Memory - Система памяти для AI агентов

Простая, но эффективная система памяти с поддержкой:
- Краткосрочной памяти (сессия)
- Долгосрочной памяти (постоянная)
- Семантического поиска
- Контекстного отзыва
"""

import json
import hashlib
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class Memory(ABC):
    """Базовый класс для системы памяти"""
    
    @abstractmethod
    def store(self, input_text: str, output_text: str, context: Dict[str, Any] = None) -> None:
        """Сохранить информацию в память"""
        pass
    
    @abstractmethod
    def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Найти релевантные воспоминания"""
        pass
    
    @abstractmethod
    def has_relevant_context(self, query: str) -> bool:
        """Проверить есть ли релевантный контекст"""
        pass
    
    @abstractmethod
    def get_relevant_context(self, query: str) -> str:
        """Получить релевантный контекст"""
        pass
    
    @abstractmethod
    def get_summary(self) -> str:
        """Получить краткую сводку памяти"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Очистить память"""
        pass


class SimpleMemory(Memory):
    """
    Простая память в оперативной памяти
    
    Хранит всё в списках, без постоянства.
    Подходит для простых случаев и тестирования.
    """
    
    def __init__(self, max_entries: int = 100):
        self.max_entries = max_entries
        self.memories = []
        self.created_at = datetime.now()
    
    def store(self, input_text: str, output_text: str, context: Dict[str, Any] = None) -> None:
        """Сохранить в память"""
        memory_entry = {
            "id": self._generate_id(input_text, output_text),
            "input": input_text,
            "output": output_text,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "accessed_count": 0
        }
        
        self.memories.append(memory_entry)
        
        # Ограничиваем размер памяти
        if len(self.memories) > self.max_entries:
            self.memories = self.memories[-self.max_entries:]
        
        logger.debug(f"Сохранено в память: {len(input_text)} символов")
    
    def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Найти похожие воспоминания"""
        query_lower = query.lower()
        
        # Простой поиск по ключевым словам
        relevant = []
        for memory in self.memories:
            score = self._calculate_relevance(query_lower, memory)
            if score > 0:
                memory_copy = memory.copy()
                memory_copy["relevance_score"] = score
                relevant.append(memory_copy)
        
        # Сортируем по релевантности
        relevant.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Обновляем счетчик доступа
        for memory in relevant[:limit]:
            original_memory = next(
                m for m in self.memories if m["id"] == memory["id"]
            )
            original_memory["accessed_count"] += 1
        
        return relevant[:limit]
    
    def has_relevant_context(self, query: str) -> bool:
        """Есть ли релевантный контекст"""
        relevant = self.recall(query, limit=1)
        return len(relevant) > 0 and relevant[0]["relevance_score"] > 0.3
    
    def get_relevant_context(self, query: str) -> str:
        """Получить релевантный контекст как строку"""
        relevant = self.recall(query, limit=3)
        
        if not relevant:
            return ""
        
        context_parts = []
        for memory in relevant:
            context_parts.append(
                f"Previous: {memory['input']} -> {memory['output']}"
            )
        
        return "\n".join(context_parts)
    
    def get_summary(self) -> str:
        """Сводка памяти"""
        total = len(self.memories)
        if total == 0:
            return "Память пуста"
        
        recent = len([
            m for m in self.memories 
            if datetime.fromisoformat(m["timestamp"]) > datetime.now() - timedelta(hours=1)
        ])
        
        return f"Память: {total} записей, {recent} за последний час"
    
    def clear(self) -> None:
        """Очистить память"""
        self.memories = []
        logger.info("Память очищена")
    
    def _generate_id(self, input_text: str, output_text: str) -> str:
        """Генерировать уникальный ID для записи"""
        content = f"{input_text}:{output_text}:{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def _calculate_relevance(self, query: str, memory: Dict) -> float:
        """Вычислить релевантность воспоминания"""
        query_words = set(query.split())
        
        # Поиск в input
        input_words = set(memory["input"].lower().split())
        input_overlap = len(query_words.intersection(input_words))
        
        # Поиск в output
        output_words = set(memory["output"].lower().split())
        output_overlap = len(query_words.intersection(output_words))
        
        # Поиск в контексте
        context_overlap = 0
        if memory["context"]:
            context_text = " ".join(str(v) for v in memory["context"].values())
            context_words = set(context_text.lower().split())
            context_overlap = len(query_words.intersection(context_words))
        
        # Взвешенная оценка
        total_overlap = input_overlap * 2 + output_overlap * 1 + context_overlap * 0.5
        max_possible = len(query_words) * 2
        
        if max_possible == 0:
            return 0
        
        return min(1.0, total_overlap / max_possible)


class PersistentMemory(Memory):
    """
    Постоянная память с SQLite
    
    Сохраняет данные между сессиями, поддерживает поиск и индексы.
    """
    
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self._init_database()
        logger.info(f"Инициализирована постоянная память: {db_path}")
    
    def _init_database(self) -> None:
        """Инициализировать базу данных"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    input_text TEXT NOT NULL,
                    output_text TEXT NOT NULL,
                    context TEXT,
                    timestamp TEXT NOT NULL,
                    accessed_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON memories(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_input_text 
                ON memories(input_text)
            """)
    
    def store(self, input_text: str, output_text: str, context: Dict[str, Any] = None) -> None:
        """Сохранить в постоянную память"""
        memory_id = self._generate_id(input_text, output_text)
        context_json = json.dumps(context or {})
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO memories 
                (id, input_text, output_text, context, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (memory_id, input_text, output_text, context_json, datetime.now().isoformat()))
        
        logger.debug(f"Сохранено в постоянную память: {memory_id}")
    
    def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Найти в постоянной памяти"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Простой поиск FTS (если включен) или LIKE
            cursor = conn.execute("""
                SELECT * FROM memories 
                WHERE input_text LIKE ? OR output_text LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            
            memories = []
            for row in cursor:
                memory = dict(row)
                memory["context"] = json.loads(memory["context"] or "{}")
                memories.append(memory)
                
                # Обновляем счетчик доступа
                conn.execute("""
                    UPDATE memories SET accessed_count = accessed_count + 1
                    WHERE id = ?
                """, (memory["id"],))
            
            return memories
    
    def has_relevant_context(self, query: str) -> bool:
        """Проверить наличие релевантного контекста"""
        relevant = self.recall(query, limit=1)
        return len(relevant) > 0
    
    def get_relevant_context(self, query: str) -> str:
        """Получить релевантный контекст"""
        relevant = self.recall(query, limit=3)
        
        if not relevant:
            return ""
        
        context_parts = []
        for memory in relevant:
            context_parts.append(
                f"Previous: {memory['input_text']} -> {memory['output_text']}"
            )
        
        return "\n".join(context_parts)
    
    def get_summary(self) -> str:
        """Сводка постоянной памяти"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM memories")
            total = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT COUNT(*) FROM memories 
                WHERE datetime(timestamp) > datetime('now', '-1 hour')
            """)
            recent = cursor.fetchone()[0]
            
            return f"Постоянная память: {total} записей, {recent} за последний час"
    
    def clear(self) -> None:
        """Очистить постоянную память"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memories")
        
        logger.info("Постоянная память очищена")
    
    def _generate_id(self, input_text: str, output_text: str) -> str:
        """Генерировать ID для записи"""
        content = f"{input_text}:{output_text}"
        return hashlib.md5(content.encode()).hexdigest()[:16]


# Удобные алиасы для разных типов памяти
Memory = SimpleMemory  # По умолчанию простая память 