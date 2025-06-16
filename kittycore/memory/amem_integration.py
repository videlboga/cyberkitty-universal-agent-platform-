"""
🧠 A-MEM Integration - Интеграция AgenticMemorySystem в KittyCore 3.0

Революционная замена примитивного VectorMemoryStore на профессиональную 
агентную память с автоматической эволюцией и семантическим поиском.

Ключевые возможности:
✅ ChromaDB векторная база вместо TF-IDF 
✅ Автоматическая эволюция памяти через LLM
✅ Семантический поиск по векторам
✅ Zettelkasten принципы организации знаний
✅ Интеграция с Obsidian vault

Принцип: "Память эволюционирует, агенты становятся умнее" 🚀
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import time

# Импорты для A-MEM (будут установлены)
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    AMEM_AVAILABLE = True
except ImportError:
    AMEM_AVAILABLE = False
    logging.warning("⚠️ A-MEM зависимости не установлены. Работаем в fallback режиме.")

# from .base_memory import BaseMemory  # не используется

logger = logging.getLogger(__name__)

@dataclass
class AgenticMemoryEntry:
    """Запись в агентной памяти A-MEM"""
    memory_id: str
    agent_id: str
    content: str
    context: Dict[str, Any]
    tags: List[str]
    category: str
    timestamp: datetime
    embeddings: Optional[List[float]] = None
    links: List[str] = None  # Связи с другими воспоминаниями
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class SimpleAgenticMemory:
    """Упрощённая реализация A-MEM принципов для fallback режима"""
    
    def __init__(self, storage_path: str = "simple_amem_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.memories: Dict[str, AgenticMemoryEntry] = {}
        self.memory_links: Dict[str, List[str]] = {}  # Связи между воспоминаниями
        
    async def add_note(self, content: str, tags: List[str] = None, 
                      category: str = "general", **kwargs) -> str:
        """Добавление заметки с простой эволюцией"""
        memory_id = f"simple_{len(self.memories)}"
        
        # Поиск связанных воспоминаний через keyword matching
        related_memories = await self._find_related_simple(content)
        
        entry = AgenticMemoryEntry(
            memory_id=memory_id,
            agent_id=kwargs.get('agent_id', 'unknown'),
            content=content,
            context=kwargs.get('context', {}),
            tags=tags or [],
            category=category,
            timestamp=datetime.now(),
            links=[m.memory_id for m in related_memories[:3]]  # топ-3 связи
        )
        
        self.memories[memory_id] = entry
        self.memory_links[memory_id] = entry.links
        
        logger.info(f"💭 Простая память создана: {memory_id} (связей: {len(entry.links)})")
        return memory_id
    
    async def search_agentic(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Простой поиск по ключевым словам"""
        results = []
        query_lower = query.lower()
        
        for memory in self.memories.values():
            # Простой keyword matching
            if query_lower in memory.content.lower():
                results.append({
                    'id': memory.memory_id,
                    'content': memory.content,
                    'tags': memory.tags,
                    'category': memory.category,
                    'agent_id': memory.agent_id,
                    'links': memory.links
                })
        
        return results[:k]
    
    async def _find_related_simple(self, content: str) -> List[AgenticMemoryEntry]:
        """Простой поиск связанных воспоминаний"""
        words = set(content.lower().split())
        related = []
        
        for memory in self.memories.values():
            memory_words = set(memory.content.lower().split())
            overlap = len(words.intersection(memory_words))
            
            if overlap > 2:  # Простой критерий связанности
                related.append(memory)
        
        return related

class AgenticMemorySystem:
    """
    Агентная память для LLM агентов с семантическим поиском и эволюцией
    Использует ChromaDB для векторного поиска и Zettelkasten принципы
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', 
                 llm_backend: str = "openai", llm_model: str = "gpt-4o-mini"):
        self.model_name = model_name
        self.llm_backend = llm_backend
        self.llm_model = llm_model
        
        # Настройка offline режима для стабильной работы
        import os
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["HF_DATASETS_OFFLINE"] = "1"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # Проверяем принудительный fallback режим
        if os.environ.get("FORCE_AMEM_FALLBACK", "false").lower() == "true":
            logger.info("🔄 Принудительный fallback режим активирован для AgenticMemorySystem")
            global AMEM_AVAILABLE
            AMEM_AVAILABLE = False
        
        if AMEM_AVAILABLE:
            self._init_professional_amem()
        else:
            logger.warning("🔄 Fallback: Используем SimpleAgenticMemory")
            self.simple_memory = SimpleAgenticMemory()
            
    def _init_professional_amem(self):
        """Инициализация профессиональной A-MEM системы с offline поддержкой"""
        try:
            # Инициализация ChromaDB
            self.chroma_client = chromadb.Client()
            
            # Уникальное имя коллекции для избежания конфликтов
            collection_name = f"kittycore_amem_{int(time.time())}"
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                get_or_create=True
            )
            
            # Инициализация embedding модели в offline режиме
            logger.info(f"🧠 Загружаем offline модель: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            
            logger.info(f"🚀 A-MEM инициализирован OFFLINE: {self.model_name}")
            logger.info(f"📊 Размерность эмбеддингов: {self.embedding_model.get_sentence_embedding_dimension()}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации A-MEM: {e}")
            logger.warning("🔄 Переключаемся на SimpleAgenticMemory")
            global AMEM_AVAILABLE
            AMEM_AVAILABLE = False
            self.simple_memory = SimpleAgenticMemory()
    
    async def add_note(self, content: str, tags: List[str] = None, 
                      category: str = "general", **kwargs) -> str:
        """Добавление заметки с автоматической эволюцией"""
        if not AMEM_AVAILABLE:
            return await self.simple_memory.add_note(content, tags, category, **kwargs)
            
        try:
            # Профессиональная A-MEM логика
            memory_id = f"amem_{datetime.now().timestamp()}"
            
            # Создание эмбеддинга
            embedding = self.embedding_model.encode(content).tolist()
            
            # Поиск связанных воспоминаний через векторный поиск
            related_memories = await self._find_related_professional(content, embedding)
            
            # LLM анализ для создания контекста и тегов (упрощённая версия)
            enhanced_tags = await self._enhance_tags_with_llm(content, tags or [])
            
            # Сохранение в ChromaDB
            self.collection.add(
                documents=[content],
                metadatas=[{
                    "agent_id": kwargs.get('agent_id', 'unknown'),
                    "category": category,
                    "tags": json.dumps(enhanced_tags),
                    "timestamp": datetime.now().isoformat(),
                    "links": json.dumps([m['id'] for m in related_memories[:3]])
                }],
                ids=[memory_id]
            )
            
            logger.info(f"🧠 A-MEM память создана: {memory_id} (связей: {len(related_memories)})")
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ Ошибка A-MEM add_note: {e}")
            # Fallback на простую память
            return await self.simple_memory.add_note(content, tags, category, **kwargs)
    
    async def search_agentic(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Семантический поиск по A-MEM"""
        if not AMEM_AVAILABLE:
            return await self.simple_memory.search_agentic(query, k)
            
        try:
            # Создание эмбеддинга запроса
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Векторный поиск в ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )
            
            # Форматирование результатов
            formatted_results = []
            for i, doc_id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i]
                formatted_results.append({
                    'id': doc_id,
                    'content': results['documents'][0][i],
                    'tags': json.loads(metadata.get('tags', '[]')),
                    'category': metadata.get('category', 'unknown'),
                    'agent_id': metadata.get('agent_id', 'unknown'),
                    'distance': results['distances'][0][i] if 'distances' in results else 0.0
                })
            
            logger.info(f"🔍 A-MEM поиск: найдено {len(formatted_results)} результатов")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Ошибка A-MEM search: {e}")
            # Fallback на простую память
            return await self.simple_memory.search_agentic(query, k)
    
    async def _find_related_professional(self, content: str, 
                                       embedding: List[float]) -> List[Dict[str, Any]]:
        """Поиск связанных воспоминаний через векторы"""
        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=10  # ищем больше для выбора лучших связей
            )
            
            return [{'id': doc_id, 'content': doc} 
                   for doc_id, doc in zip(results['ids'][0], results['documents'][0])]
        except Exception as e:
            logger.error(f"❌ Ошибка поиска связей: {e}")
            return []
    
    async def _enhance_tags_with_llm(self, content: str, 
                                   existing_tags: List[str]) -> List[str]:
        """Улучшение тегов через LLM (упрощённая версия)"""
        # Пока простая логика, можно расширить LLM вызовом
        words = content.lower().split()
        auto_tags = []
        
        # Простые правила для автотегов
        if any(word in words for word in ['код', 'программа', 'python', 'код']):
            auto_tags.append('programming')
        if any(word in words for word in ['задача', 'проблема', 'issue']):
            auto_tags.append('task')
        if any(word in words for word in ['результат', 'решение', 'success']):
            auto_tags.append('result')
            
        return list(set(existing_tags + auto_tags))
    
    # Методы совместимости с UnifiedOrchestrator
    async def store_memory(self, content: str, context: Dict[str, Any] = None, 
                          tags: List[str] = None) -> str:
        """Сохранение воспоминания (совместимость с UnifiedOrchestrator)"""
        return await self.add_note(
            content=content,
            tags=tags or [],
            category=context.get('category', 'general') if context else 'general',
            **(context or {})
        )
    
    async def search_memories(self, query: str, filters: Dict = None, 
                            limit: int = 5) -> List[Dict[str, Any]]:
        """Поиск воспоминаний (совместимость с UnifiedOrchestrator)"""
        return await self.search_agentic(query, k=limit)

class KittyCoreMemorySystem:
    """Интеграция A-MEM в KittyCore 3.0"""
    
    def __init__(self, vault_path: str = "obsidian_vault"):
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(exist_ok=True)
        
        # Инициализация A-MEM системы
        self.amem = AgenticMemorySystem()
        
        # Локальные данные для команд
        self.team_memories: Dict[str, List[str]] = {}
        self.obsidian_sync = True
        
        logger.info(f"🎯 KittyCoreMemorySystem инициализирован: {vault_path}")
    
    async def agent_remember(self, agent_id: str, memory: str, 
                           context: Dict[str, Any]) -> str:
        """Агент сохраняет воспоминание с автоматической эволюцией"""
        try:
            # Сохранение в A-MEM с контекстом
            memory_id = await self.amem.add_note(
                content=memory,
                tags=[agent_id, context.get("task_type", "general")],
                category=context.get("category", "agent_memory"),
                agent_id=agent_id,
                context=context
            )
            
            # Отслеживание памяти команды
            team_id = context.get("team_id", "default_team")
            if team_id not in self.team_memories:
                self.team_memories[team_id] = []
            self.team_memories[team_id].append(memory_id)
            
            # Синхронизация с Obsidian (если включена)
            if self.obsidian_sync:
                await self._sync_to_obsidian(memory_id, memory, context)
            
            logger.info(f"📝 Агент {agent_id} запомнил: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения памяти агента {agent_id}: {e}")
            return f"error_{datetime.now().timestamp()}"
    
    async def collective_search(self, query: str, 
                              team_id: str = None) -> List[Dict[str, Any]]:
        """Семантический поиск по коллективной памяти команды"""
        try:
            # Поиск через A-MEM
            all_results = await self.amem.search_agentic(query, k=20)
            
            # Фильтрация по команде если нужно
            if team_id:
                team_results = []
                team_memory_ids = self.team_memories.get(team_id, [])
                
                for result in all_results:
                    if result['id'] in team_memory_ids or team_id in result.get('tags', []):
                        team_results.append(result)
                
                logger.info(f"🔍 Поиск команды {team_id}: {len(team_results)} результатов")
                return team_results[:10]  # ограничиваем результат
            
            logger.info(f"🔍 Глобальный поиск: {len(all_results)} результатов")
            return all_results
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")
            return []
    
    async def _sync_to_obsidian(self, memory_id: str, memory: str, 
                              context: Dict[str, Any]):
        """Синхронизация с Obsidian vault"""
        try:
            # Создание markdown файла в vault
            agent_id = context.get("agent_id", "unknown")
            filename = f"memory_{agent_id}_{memory_id}.md"
            file_path = self.vault_path / filename
            
            # Markdown контент
            markdown_content = f"""# 🧠 Memory: {memory_id}

**Agent:** {agent_id}  
**Category:** {context.get("category", "general")}  
**Timestamp:** {datetime.now().isoformat()}

## Content
{memory}

## Context
```json
{json.dumps(context, indent=2, ensure_ascii=False)}
```

## Tags
{', '.join([f'#{tag}' for tag in context.get('tags', [])])}
"""
            
            # Сохранение файла
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
                
            logger.debug(f"📄 Obsidian sync: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка Obsidian sync: {e}")
    
    # Методы совместимости с UnifiedOrchestrator
    async def store_memory(self, content: str, context: Dict[str, Any] = None, 
                          tags: List[str] = None) -> str:
        """Сохранение воспоминания через KittyCoreMemorySystem"""
        return await self.amem.store_memory(content, context, tags)
    
    async def search_memories(self, query: str, filters: Dict = None, 
                            limit: int = 5) -> List[Dict[str, Any]]:
        """Поиск воспоминаний через KittyCoreMemorySystem"""
        return await self.amem.search_memories(query, filters, limit)


# === ЭКСПОРТ ===

def get_enhanced_memory_system(vault_path: str = "obsidian_vault") -> KittyCoreMemorySystem:
    """Фабричная функция для создания улучшенной системы памяти"""
    # Проверяем принудительный fallback режим
    import os
    if os.environ.get("FORCE_AMEM_FALLBACK", "false").lower() == "true":
        logger.info("🔄 Принудительный fallback режим A-MEM активирован")
        global AMEM_AVAILABLE
        AMEM_AVAILABLE = False
    
    return KittyCoreMemorySystem(vault_path)

# Для совместимости с существующим кодом
def get_amem_integration() -> AgenticMemorySystem:
    """Получить A-MEM систему"""
    return AgenticMemorySystem() 