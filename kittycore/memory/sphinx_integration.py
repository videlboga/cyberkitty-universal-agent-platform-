"""
🔍 Sphinx Search Integration - Будущее KittyCore 3.0 Memory System

Экспериментальная интеграция Sphinx Search для революционных возможностей:
✅ Перколяционные индексы для агентных триггеров
✅ HNSW векторные индексы для семантического поиска  
✅ SQL joins для сложных связей памяти
✅ Full-text поиск с произвольными WHERE условиями

Принцип: "Sphinx + A-MEM = Непревзойдённая память агентов" 🚀
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class SphinxMemoryEntry:
    """Запись памяти для Sphinx Search"""
    memory_id: str
    agent_id: str
    content: str
    tags: List[str]
    category: str
    timestamp: datetime
    vector_embedding: Optional[List[float]] = None
    percolation_queries: List[str] = None  # Запросы для перколяции
    
class SphinxAgentMemory:
    """
    Экспериментальная интеграция Sphinx Search в KittyCore 3.0
    
    Революционные возможности:
    🔍 Перколяция: "какие агенты реагируют на событие X?"
    🧠 Векторный поиск: семантическое сходство
    📊 SQL joins: сложные связи между воспоминаниями
    ⚡ Full-text: быстрый поиск по тексту
    """
    
    def __init__(self, sphinx_config_path: str = "sphinx_config"):
        self.config_path = Path(sphinx_config_path)
        self.config_path.mkdir(exist_ok=True)
        
        # Настройки Sphinx
        self.sphinx_host = "localhost"
        self.sphinx_port = 9312
        self.index_name = "kittycore_memory"
        
        self.memory_storage = {}
        self.percolation_rules = {}  # Правила для перколяции
        
        logger.info("🔍 SphinxAgentMemory инициализирован (экспериментально)")
    
    async def create_sphinx_config(self):
        """Создание конфигурации Sphinx для KittyCore"""
        
        config_content = f"""
# === KITTYCORE 3.0 SPHINX CONFIGURATION ===
# Революционная память для агентной системы

# Основной индекс памяти агентов
index {self.index_name}
{{
    # Источник данных - JSON файлы памяти
    type = rt
    path = {self.config_path}/memory_index
    
    # Поля для агентной памяти
    rt_field = content        # Основной контент
    rt_field = agent_id       # ID агента  
    rt_field = category       # Категория памяти
    rt_field = tags          # Теги (JSON массив)
    
    # Атрибуты для фильтрации
    rt_attr_uint = timestamp  # Unix timestamp
    rt_attr_string = agent_id # ID агента
    rt_attr_string = category # Категория
    rt_attr_json = metadata   # Метаданные (JSON)
    
    # ВЕКТОРНЫЕ ИНДЕКСЫ (Sphinx 3.8.1+)
    rt_attr_float_vector = embedding[384]  # Вектор эмбеддинга
    
    # Настройки индексирования
    morphology = stem_ru, stem_en
    min_word_len = 2
    charset_table = 0..9, A..Z->a..z, a..z, _, U+410..U+42F->U+430..U+44F, U+430..U+44F
}}

# ПЕРКОЛЯЦИОННЫЙ ИНДЕКС для агентных триггеров
index {self.index_name}_percolate
{{
    type = percolate
    path = {self.config_path}/percolate_index
    
    # Поля для перколяции
    rt_field = trigger_query    # Запрос-триггер
    rt_field = agent_patterns   # Паттерны агента
    
    # Атрибуты
    rt_attr_string = agent_id   # Какой агент реагирует
    rt_attr_string = action     # Какое действие выполнить
    rt_attr_uint = priority     # Приоритет срабатывания
}}

# Настройки сервера
searchd
{{
    listen = {self.sphinx_port}
    log = {self.config_path}/searchd.log
    query_log = {self.config_path}/query.log
    pid_file = {self.config_path}/searchd.pid
    
    # Максимальные лимиты
    max_matches = 10000
    max_packet_size = 32M
    
    # Поддержка JSON и векторов
    workers = threads
    dist_threads = 8
}}

# Индексер
indexer
{{
    mem_limit = 256M
}}
"""
        
        config_file = self.config_path / "sphinx.conf"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content.strip())
            
        logger.info(f"📝 Конфигурация Sphinx создана: {config_file}")
        return config_file
    
    async def add_agent_memory(self, agent_id: str, content: str, 
                              tags: List[str] = None, 
                              category: str = "general",
                              embedding: List[float] = None) -> str:
        """Добавление памяти агента с поддержкой всех возможностей Sphinx"""
        
        memory_id = f"sphinx_{agent_id}_{int(datetime.now().timestamp())}"
        
        # Создание записи памяти
        memory_entry = SphinxMemoryEntry(
            memory_id=memory_id,
            agent_id=agent_id,
            content=content,
            tags=tags or [],
            category=category,
            timestamp=datetime.now(),
            vector_embedding=embedding
        )
        
        # Сохранение в локальном хранилище
        self.memory_storage[memory_id] = memory_entry
        
        # TODO: Реальная вставка в Sphinx RT индекс
        # INSERT INTO kittycore_memory (content, agent_id, category, tags, timestamp, embedding)
        # VALUES (?, ?, ?, ?, ?, ?)
        
        logger.info(f"🧠 Sphinx память добавлена: {memory_id} (агент: {agent_id})")
        return memory_id
    
    async def create_percolation_rule(self, agent_id: str, trigger_pattern: str,
                                    action: str, priority: int = 100):
        """Создание правила перколяции для агента"""
        
        rule_id = f"percolate_{agent_id}_{len(self.percolation_rules)}"
        
        self.percolation_rules[rule_id] = {
            'agent_id': agent_id,
            'pattern': trigger_pattern,
            'action': action,
            'priority': priority
        }
        
        # TODO: Реальная вставка в перколяционный индекс
        # INSERT INTO kittycore_memory_percolate (trigger_query, agent_id, action, priority)
        # VALUES (?, ?, ?, ?)
        
        logger.info(f"🎯 Правило перколяции создано: {rule_id}")
        return rule_id
    
    async def vector_search(self, query_embedding: List[float], 
                           agent_filter: str = None, k: int = 5) -> List[Dict]:
        """Векторный поиск через Sphinx HNSW"""
        
        # TODO: Реальный запрос к Sphinx с векторным поиском
        # SELECT *, DOT(embedding, ?) as similarity 
        # FROM kittycore_memory 
        # WHERE agent_id = ? 
        # ORDER BY similarity DESC 
        # LIMIT ?
        
        # Пока возвращаем моковые результаты
        results = []
        for memory_id, entry in list(self.memory_storage.items())[:k]:
            if not agent_filter or entry.agent_id == agent_filter:
                results.append({
                    'memory_id': memory_id,
                    'content': entry.content,
                    'agent_id': entry.agent_id,
                    'similarity': 0.85,  # Мок симиляритета
                    'tags': entry.tags
                })
                
        logger.info(f"🔍 Векторный поиск: найдено {len(results)} результатов")
        return results
    
    async def percolate_event(self, event_content: str) -> List[Dict]:
        """Перколяция: какие агенты должны отреагировать на событие"""
        
        # TODO: Реальный перколяционный запрос к Sphinx
        # CALL PQ('kittycore_memory_percolate', ?, 0 as docs)
        
        triggered_agents = []
        for rule_id, rule in self.percolation_rules.items():
            # Простая проверка паттерна (в реальности - через Sphinx)
            if rule['pattern'].lower() in event_content.lower():
                triggered_agents.append({
                    'agent_id': rule['agent_id'],
                    'action': rule['action'],
                    'priority': rule['priority'],
                    'rule_id': rule_id
                })
        
        # Сортирука по приоритету
        triggered_agents.sort(key=lambda x: x['priority'], reverse=True)
        
        logger.info(f"⚡ Перколяция: сработало {len(triggered_agents)} правил")
        return triggered_agents
    
    async def full_text_search(self, query: str, filters: Dict = None, 
                              limit: int = 10) -> List[Dict]:
        """Full-text поиск с произвольными WHERE условиями"""
        
        # TODO: Реальный запрос к Sphinx
        # SELECT * FROM kittycore_memory 
        # WHERE MATCH(?) AND category = ? AND timestamp > ?
        # ORDER BY @weight DESC, timestamp DESC 
        # LIMIT ?
        
        results = []
        for memory_id, entry in self.memory_storage.items():
            # Простой поиск по содержимому
            if query.lower() in entry.content.lower():
                # Применение фильтров
                if filters:
                    if filters.get('category') and entry.category != filters['category']:
                        continue
                    if filters.get('agent_id') and entry.agent_id != filters['agent_id']:
                        continue
                
                results.append({
                    'memory_id': memory_id,
                    'content': entry.content,
                    'agent_id': entry.agent_id,
                    'category': entry.category,
                    'weight': 100,  # Мок веса
                    'timestamp': entry.timestamp.isoformat()
                })
                
                if len(results) >= limit:
                    break
        
        logger.info(f"📝 Full-text поиск: найдено {len(results)} результатов")
        return results
    
    async def complex_join_search(self, query: str) -> List[Dict]:
        """Сложный поиск с JOIN между индексами"""
        
        # TODO: Реальный JOIN запрос к Sphinx
        # SELECT m.*, p.action, p.priority
        # FROM kittycore_memory m
        # LEFT JOIN kittycore_memory_percolate p ON m.agent_id = p.agent_id
        # WHERE MATCH(?) AND p.priority > 50
        # ORDER BY p.priority DESC, m.timestamp DESC
        
        logger.info("🔗 Сложный JOIN поиск (экспериментально)")
        return []
    
    def get_sphinx_stats(self) -> Dict[str, Any]:
        """Статистика Sphinx памяти"""
        return {
            'total_memories': len(self.memory_storage),
            'percolation_rules': len(self.percolation_rules),
            'agents_count': len(set(entry.agent_id for entry in self.memory_storage.values())),
            'categories': list(set(entry.category for entry in self.memory_storage.values())),
            'sphinx_version': '3.8.1',
            'features': [
                'HNSW Vector Search',
                'Percolation Indexes', 
                'Full-text Search',
                'SQL Joins',
                'Real-time Updates'
            ]
        }

# === INTEGRATION EXAMPLES ===

async def demo_sphinx_capabilities():
    """Демонстрация возможностей Sphinx для агентов"""
    
    sphinx_memory = SphinxAgentMemory()
    
    # Создание конфигурации
    await sphinx_memory.create_sphinx_config()
    
    # Добавление памяти агентов
    await sphinx_memory.add_agent_memory(
        agent_id="data_analyst",
        content="Провел анализ рынка Битрикс24, выявил 10 топ приложений",
        tags=["market_analysis", "bitrix24", "success"],
        category="analysis_result"
    )
    
    await sphinx_memory.add_agent_memory(
        agent_id="code_generator", 
        content="Создал HTML прототип с формой регистрации",
        tags=["html", "prototype", "frontend"],
        category="code_result"
    )
    
    # Создание правил перколяции
    await sphinx_memory.create_percolation_rule(
        agent_id="security_agent",
        trigger_pattern="безопасность OR уязвимость OR hack",
        action="analyze_security_threat",
        priority=200
    )
    
    await sphinx_memory.create_percolation_rule(
        agent_id="optimization_agent", 
        trigger_pattern="медленно OR performance OR оптимизация",
        action="optimize_performance",
        priority=150
    )
    
    # Тестирование перколяции
    triggered = await sphinx_memory.percolate_event(
        "Обнаружена уязвимость в системе безопасности"
    )
    
    print("🎯 ПЕРКОЛЯЦИЯ - Агенты которые должны среагировать:")
    for agent in triggered:
        print(f"  Agent: {agent['agent_id']} -> Action: {agent['action']}")
    
    # Full-text поиск
    search_results = await sphinx_memory.full_text_search(
        "анализ рынка",
        filters={'category': 'analysis_result'}
    )
    
    print(f"\n📝 FULL-TEXT ПОИСК: найдено {len(search_results)} результатов")
    
    # Статистика
    stats = sphinx_memory.get_sphinx_stats()
    print(f"\n📊 СТАТИСТИКА SPHINX:")
    print(f"  Воспоминаний: {stats['total_memories']}")
    print(f"  Правил перколяции: {stats['percolation_rules']}")
    print(f"  Агентов: {stats['agents_count']}")
    print(f"  Возможности: {', '.join(stats['features'])}")

if __name__ == "__main__":
    asyncio.run(demo_sphinx_capabilities()) 