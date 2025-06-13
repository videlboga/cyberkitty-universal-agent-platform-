"""
🔍 Vector Memory System - Векторизация Obsidian базы для KittyCore 3.0

Превращаем Obsidian vault в мощную векторную базу знаний:
- ✅ Векторизация заметок и контента  
- ✅ Семантический поиск
- ✅ Кэширование эмбеддингов
- ✅ Автоматическая индексация
- ✅ Поиск по контексту и смыслу

ЦЕЛЬ: Дать агентам супер-поиск по всем знаниям! 🧠
"""

import asyncio
import json
import logging
import hashlib
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import sqlite3

logger = logging.getLogger(__name__)

# === СТРУКТУРЫ ДАННЫХ ===

@dataclass
class VectorDocument:
    """Векторизованный документ"""
    doc_id: str
    file_path: str
    title: str
    content: str
    content_hash: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    chunk_index: int = 0  # Для больших документов разбитых на части
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для сохранения"""
        return {
            "doc_id": self.doc_id,
            "file_path": str(self.file_path),
            "title": self.title,
            "content": self.content,
            "content_hash": self.content_hash,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "chunk_index": self.chunk_index
        }

@dataclass
class SearchResult:
    """Результат векторного поиска"""
    document: VectorDocument
    similarity_score: float
    relevance_context: str
    matched_chunk: Optional[str] = None

# === ПРОСТАЯ ВЕКТОРИЗАЦИЯ ===

class SimpleEmbedding:
    """Простая система векторизации без внешних зависимостей"""
    
    def __init__(self):
        self.vocabulary = {}
        self.idf_weights = {}
        self.vocab_size = 0
        
    def build_vocabulary(self, documents: List[str]):
        """Построить словарь из документов"""
        word_counts = {}
        doc_count = len(documents)
        
        # Подсчёт слов
        for doc in documents:
            words = self._tokenize(doc)
            unique_words = set(words)
            
            for word in unique_words:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Создаём словарь и IDF веса
        self.vocabulary = {word: idx for idx, word in enumerate(word_counts.keys())}
        self.vocab_size = len(self.vocabulary)
        
        # Считаем IDF
        for word, count in word_counts.items():
            self.idf_weights[word] = np.log(doc_count / count)
            
        logger.info(f"🧠 Словарь построен: {self.vocab_size} слов")
    
    def vectorize(self, text: str) -> List[float]:
        """Векторизация текста в TF-IDF вектор"""
        if not self.vocabulary:
            logger.warning("⚠️ Словарь не построен!")
            return [0.0] * 300  # возвращаем нулевой вектор
            
        words = self._tokenize(text)
        word_counts = {}
        
        # Подсчёт частоты слов
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Создаём TF-IDF вектор
        vector = [0.0] * self.vocab_size
        doc_length = len(words)
        
        for word, count in word_counts.items():
            if word in self.vocabulary:
                idx = self.vocabulary[word]
                tf = count / doc_length  # Term Frequency
                idf = self.idf_weights.get(word, 1.0)  # IDF
                vector[idx] = tf * idf
        
        return vector
    
    def _tokenize(self, text: str) -> List[str]:
        """Простая токенизация"""
        # Приводим к нижнему регистру и разбиваем по словам
        words = text.lower().split()
        
        # Очищаем от знаков препинания
        clean_words = []
        for word in words:
            clean_word = ''.join(c for c in word if c.isalnum() or c in 'ёйцукенгшщзхъфывапролджэячсмитьбю')
            if len(clean_word) > 2:  # Игнорируем слишком короткие слова
                clean_words.append(clean_word)
        
        return clean_words
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Косинусное сходство между векторами"""
        if len(vec1) != len(vec2):
            return 0.0
            
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
            
        return dot_product / (magnitude1 * magnitude2)

# === ВЕКТОРНОЕ ХРАНИЛИЩЕ ===

class VectorMemoryStore:
    """Векторное хранилище для семантического поиска"""
    
    def __init__(self, storage_path: str = "vector_memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Компоненты системы
        self.embedding_model = SimpleEmbedding()
        self.documents: Dict[str, VectorDocument] = {}
        
        # База данных для хранения
        self.db_path = self.storage_path / "vector_store.db"
        self._init_database()
        
        # Кэш для быстрого поиска
        self.document_cache = {}
        self.is_indexed = False
        
        logger.info(f"🔍 VectorMemoryStore инициализирован: {storage_path}")
    
    def _init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT PRIMARY KEY,
                file_path TEXT,
                title TEXT,
                content TEXT,
                content_hash TEXT,
                embedding TEXT,
                metadata TEXT,
                created_at TEXT,
                updated_at TEXT,
                chunk_index INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_hash ON documents(content_hash)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_file_path ON documents(file_path)
        """)
        
        conn.commit()
        conn.close()
        
        logger.debug("📊 База данных векторов инициализирована")
    
    async def index_documents(self, documents_path: Path) -> int:
        """Индексирование документов из папки"""
        indexed_count = 0
        all_texts = []
        
        # Сначала собираем все тексты для построения словаря
        for file_path in documents_path.rglob("*.md"):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    all_texts.append(content)
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось прочитать {file_path}: {e}")
        
        # Строим словарь
        if all_texts:
            self.embedding_model.build_vocabulary(all_texts)
        
        # Теперь индексируем документы
        for file_path in documents_path.rglob("*.md"):
            if file_path.is_file():
                if await self._index_document(file_path):
                    indexed_count += 1
        
        self.is_indexed = True
        logger.info(f"✅ Проиндексировано {indexed_count} документов")
        return indexed_count
    
    async def _index_document(self, file_path: Path) -> bool:
        """Индексирование одного документа"""
        try:
            content = file_path.read_text(encoding='utf-8')
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Проверяем, нужно ли переиндексировать
            if await self._document_exists(str(file_path), content_hash):
                return False
            
            # Создаём документ
            doc_id = self._generate_doc_id(file_path, content_hash)
            title = self._extract_title(content, file_path)
            
            # Разбиваем большие документы на части
            chunks = self._split_content(content)
            
            for i, chunk in enumerate(chunks):
                chunk_doc = VectorDocument(
                    doc_id=f"{doc_id}_{i}",
                    file_path=str(file_path),
                    title=title,
                    content=chunk,
                    content_hash=content_hash,
                    chunk_index=i,
                    metadata={
                        "file_name": file_path.name,
                        "file_size": len(content),
                        "chunk_count": len(chunks)
                    }
                )
                
                # Векторизуем
                chunk_doc.embedding = self.embedding_model.vectorize(chunk)
                
                # Сохраняем
                await self._save_document(chunk_doc)
                self.documents[chunk_doc.doc_id] = chunk_doc
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка индексации {file_path}: {e}")
            return False
    
    async def search(self, query: str, limit: int = 5, min_similarity: float = 0.1) -> List[SearchResult]:
        """Семантический поиск документов"""
        if not self.is_indexed:
            await self._load_documents_from_db()
        
        if not self.documents:
            logger.warning("⚠️ Нет проиндексированных документов")
            return []
        
        # Векторизуем запрос
        query_vector = self.embedding_model.vectorize(query)
        
        # Ищем похожие документы
        results = []
        for doc in self.documents.values():
            if doc.embedding:
                similarity = self.embedding_model.cosine_similarity(query_vector, doc.embedding)
                
                if similarity >= min_similarity:
                    # Создаём контекст релевантности
                    context = self._create_relevance_context(query, doc.content)
                    
                    results.append(SearchResult(
                        document=doc,
                        similarity_score=similarity,
                        relevance_context=context,
                        matched_chunk=self._extract_relevant_chunk(query, doc.content)
                    ))
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        logger.info(f"🔍 Найдено {len(results)} результатов для '{query[:50]}...'")
        return results[:limit]
    
    def _create_relevance_context(self, query: str, content: str, context_length: int = 200) -> str:
        """Создать контекст релевантности"""
        query_words = set(self.embedding_model._tokenize(query))
        content_words = self.embedding_model._tokenize(content)
        
        # Найти лучшее место в контенте
        best_position = 0
        best_score = 0
        
        for i in range(len(content_words) - 10):
            window = content_words[i:i+10]
            score = sum(1 for word in window if word in query_words)
            
            if score > best_score:
                best_score = score
                best_position = i
        
        # Создать контекст вокруг лучшего места
        start_char = max(0, content.find(' '.join(content_words[best_position:best_position+1])) - context_length//2)
        end_char = min(len(content), start_char + context_length)
        
        context = content[start_char:end_char].strip()
        
        # Добавляем многоточие если контекст обрезан
        if start_char > 0:
            context = "..." + context
        if end_char < len(content):
            context = context + "..."
            
        return context
    
    def _extract_relevant_chunk(self, query: str, content: str, chunk_size: int = 300) -> str:
        """Извлечь наиболее релевантный кусок текста"""
        if len(content) <= chunk_size:
            return content
            
        query_words = set(self.embedding_model._tokenize(query))
        
        # Разбиваем на потенциальные куски
        sentences = content.split('.')
        best_chunk = ""
        best_score = 0
        
        for i in range(len(sentences)):
            # Берём несколько предложений
            chunk_sentences = sentences[i:i+3]
            chunk = '. '.join(chunk_sentences)
            
            if len(chunk) > chunk_size:
                chunk = chunk[:chunk_size] + "..."
            
            # Считаем релевантность
            chunk_words = set(self.embedding_model._tokenize(chunk))
            score = len(query_words.intersection(chunk_words))
            
            if score > best_score:
                best_score = score
                best_chunk = chunk
        
        return best_chunk or content[:chunk_size]
    
    async def _document_exists(self, file_path: str, content_hash: str) -> bool:
        """Проверить существование документа с таким хэшем"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 1 FROM documents 
            WHERE file_path = ? AND content_hash = ?
            LIMIT 1
        """, (file_path, content_hash))
        
        exists = cursor.fetchone() is not None
        conn.close()
        
        return exists
    
    async def _save_document(self, document: VectorDocument):
        """Сохранить документ в базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO documents 
            (doc_id, file_path, title, content, content_hash, embedding, metadata, created_at, updated_at, chunk_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            document.doc_id,
            document.file_path,
            document.title,
            document.content,
            document.content_hash,
            json.dumps(document.embedding),
            json.dumps(document.metadata),
            document.created_at.isoformat(),
            document.updated_at.isoformat(),
            document.chunk_index
        ))
        
        conn.commit()
        conn.close()
    
    async def _load_documents_from_db(self):
        """Загрузить документы из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM documents")
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            doc_id, file_path, title, content, content_hash, embedding_json, metadata_json, created_at, updated_at, chunk_index = row
            
            document = VectorDocument(
                doc_id=doc_id,
                file_path=file_path,
                title=title,
                content=content,
                content_hash=content_hash,
                embedding=json.loads(embedding_json) if embedding_json else None,
                metadata=json.loads(metadata_json) if metadata_json else {},
                created_at=datetime.fromisoformat(created_at),
                updated_at=datetime.fromisoformat(updated_at),
                chunk_index=chunk_index
            )
            
            self.documents[doc_id] = document
        
        self.is_indexed = len(self.documents) > 0
        logger.info(f"📚 Загружено {len(self.documents)} документов из базы")
    
    def _generate_doc_id(self, file_path: Path, content_hash: str) -> str:
        """Генерировать ID документа"""
        path_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
        return f"doc_{path_hash}_{content_hash[:8]}"
    
    def _extract_title(self, content: str, file_path: Path) -> str:
        """Извлечь заголовок из содержимого"""
        lines = content.split('\n')
        
        # Ищем первый заголовок markdown
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
            elif line.startswith('## '):
                return line[3:].strip()
        
        # Если заголовка нет, используем имя файла
        return file_path.stem
    
    def _split_content(self, content: str, max_chunk_size: int = 1000) -> List[str]:
        """Разбить контент на куски"""
        if len(content) <= max_chunk_size:
            return [content]
        
        chunks = []
        sentences = content.split('.')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) > max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # Если одно предложение слишком длинное
                    chunks.append(sentence[:max_chunk_size])
                    current_chunk = sentence[max_chunk_size:]
            else:
                current_chunk += sentence + "."
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks or [content]

# === ГЛОБАЛЬНОЕ ХРАНИЛИЩЕ ===

_global_vector_store = None

def get_vector_store() -> VectorMemoryStore:
    """Получить глобальное векторное хранилище"""
    global _global_vector_store
    if _global_vector_store is None:
        _global_vector_store = VectorMemoryStore()
    return _global_vector_store 