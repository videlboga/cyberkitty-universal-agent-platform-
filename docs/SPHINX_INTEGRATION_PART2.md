# 🔍 SPHINX SEARCH ИНТЕГРАЦИЯ В KITTYCORE 3.0 - ЧАСТЬ 2

## Техническая архитектура интеграции

### 🏗️ **АРХИТЕКТУРНАЯ СХЕМА**

```
┌─────────────────────────────────────────────────────────────┐
│                   KITTYCORE 3.0 + SPHINX                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌──────────────────────────────┐   │
│  │  UnifiedOrchest │    │       Sphinx Search          │   │
│  │     rator       │◄──►│                              │   │
│  │                 │    │ ┌──────────┐ ┌──────────────┐│   │
│  └─────────────────┘    │ │ Memory   │ │ Percolation  ││   │
│           │              │ │  Index   │ │    Index     ││   │
│           ▼              │ └──────────┘ └──────────────┘│   │
│  ┌─────────────────┐    │                              │   │
│  │   AgentFactory  │    │ ┌──────────┐ ┌──────────────┐│   │
│  │     2.0         │◄──►│ │ Vector   │ │   Analytics  ││   │
│  │                 │    │ │  HNSW    │ │     SQL      ││   │
│  └─────────────────┘    │ └──────────┘ └──────────────┘│   │
│           │              └──────────────────────────────┘   │
│           ▼                             ▲                   │
│  ┌─────────────────┐              ┌─────┴─────┐            │
│  │ A-MEM Enhanced  │◄─────────────┤ Sphinx    │            │
│  │    Memory       │              │ Adapter   │            │
│  │                 │              └───────────┘            │
│  └─────────────────┘                                       │
│           │                                                │
│           ▼                                                │
│  ┌─────────────────┐                                       │
│  │ Obsidian Vault  │                                       │
│  │   Integration   │                                       │
│  └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 **КОМПОНЕНТЫ ИНТЕГРАЦИИ**

### **1. SphinxAdapter - Главный интерфейс**

```python
class SphinxAdapter:
    """Адаптер между KittyCore и Sphinx Search"""
    
    def __init__(self):
        self.sphinx_client = SphinxClient()
        self.memory_index = "kittycore_memory"
        self.percolate_index = "kittycore_memory_percolate"
        self.connection_pool = SphinxConnectionPool(max_connections=10)
    
    # === ОСНОВНЫЕ МЕТОДЫ ===
    
    async def store_agent_memory(self, agent_id: str, content: str, 
                               embedding: List[float], metadata: Dict) -> str:
        """Сохранение памяти агента в Sphinx RT индекс"""
        
    async def semantic_search(self, query_embedding: List[float], 
                            filters: Dict, limit: int = 10) -> List[Dict]:
        """Семантический поиск через HNSW векторы"""
        
    async def create_agent_trigger(self, agent_id: str, pattern: str, 
                                 action: str, priority: int) -> str:
        """Создание перколяционного правила для агента"""
        
    async def find_triggered_agents(self, event: str) -> List[Dict]:
        """Поиск агентов которые должны среагировать на событие"""
        
    async def analytics_query(self, sql: str, params: List) -> List[Dict]:
        """Выполнение аналитических SQL запросов"""
```

### **2. SphinxMemoryStore - Хранилище памяти**

```python
class SphinxMemoryStore:
    """Sphinx-based хранилище для агентной памяти"""
    
    # Схема индекса памяти
    MEMORY_INDEX_SCHEMA = {
        'fields': {
            'content': 'rt_field',      # Основной контент
            'agent_id': 'rt_field',     # ID агента
            'category': 'rt_field',     # Категория памяти  
            'tags': 'rt_field'          # Теги (JSON)
        },
        'attributes': {
            'timestamp': 'rt_attr_uint',           # Unix timestamp
            'agent_id_attr': 'rt_attr_string',     # ID агента (атрибут)
            'category_attr': 'rt_attr_string',     # Категория (атрибут)
            'metadata': 'rt_attr_json',            # Метаданные
            'embedding': 'rt_attr_float_vector[384]', # Вектор эмбеддинга
            'success_score': 'rt_attr_float',      # Оценка успешности
            'team_id': 'rt_attr_string'            # ID команды
        }
    }
    
    async def insert_memory(self, memory_data: Dict) -> str:
        """Вставка новой памяти в RT индекс"""
        sql = f"""
        INSERT INTO {self.memory_index} 
        (content, agent_id, category, tags, timestamp, agent_id_attr, 
         category_attr, metadata, embedding, success_score, team_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
    async def update_memory(self, memory_id: str, updates: Dict) -> bool:
        """Обновление существующей памяти"""
        
    async def delete_memory(self, memory_id: str) -> bool:
        """Удаление памяти (soft delete через metadata)"""
```

### **3. SphinxPercolator - Система триггеров**

```python
class SphinxPercolator:
    """Управление перколяционными правилами агентов"""
    
    # Схема перколяционного индекса
    PERCOLATE_INDEX_SCHEMA = {
        'fields': {
            'trigger_query': 'rt_field',    # Запрос-триггер
            'agent_patterns': 'rt_field'    # Дополнительные паттерны
        },
        'attributes': {
            'agent_id': 'rt_attr_string',   # Какой агент
            'action': 'rt_attr_string',     # Какое действие
            'priority': 'rt_attr_uint',     # Приоритет (200=критический)
            'conditions': 'rt_attr_json',   # Дополнительные условия
            'active': 'rt_attr_bool'        # Активность правила
        }
    }
    
    async def add_trigger_rule(self, agent_id: str, pattern: str, 
                             action: str, priority: int = 100) -> str:
        """Добавление правила перколяции"""
        
    async def percolate_event(self, event_content: str, 
                            context: Dict = None) -> List[Dict]:
        """Поиск агентов для события через перколяцию"""
        sql = "CALL PQ(?, ?, 0 as docs)"
        
    async def update_rule(self, rule_id: str, updates: Dict) -> bool:
        """Обновление правила перколяции"""
        
    async def deactivate_rule(self, rule_id: str) -> bool:
        """Деактивация правила"""
```

### **4. SphinxAnalytics - Аналитический движок**

```python
class SphinxAnalytics:
    """Аналитические запросы по памяти агентов"""
    
    async def agent_performance_report(self, days: int = 7) -> Dict:
        """Отчёт по производительности агентов"""
        sql = """
        SELECT 
            agent_id_attr as agent_id,
            COUNT(*) as total_memories,
            AVG(success_score) as avg_success,
            COUNT(DISTINCT category_attr) as categories_used,
            MAX(timestamp) as last_activity
        FROM kittycore_memory 
        WHERE timestamp > UNIX_TIMESTAMP() - ?
        GROUP BY agent_id_attr
        ORDER BY avg_success DESC, total_memories DESC
        """
        
    async def memory_similarity_analysis(self, memory_id: str) -> List[Dict]:
        """Поиск похожих воспоминаний через векторы"""
        
    async def team_collaboration_stats(self, team_id: str) -> Dict:
        """Статистика командной работы агентов"""
        
    async def category_trends(self, period: str = "7d") -> List[Dict]:
        """Тренды по категориям задач"""
        
    async def success_pattern_analysis(self) -> Dict:
        """Анализ паттернов успешных решений"""
```

---

## 🔌 **ИНТЕГРАЦИЯ С СУЩЕСТВУЮЩИМИ КОМПОНЕНТАМИ**

### **Обновление UnifiedOrchestrator**

```python
class UnifiedOrchestrator:
    def __init__(self):
        # ... существующий код ...
        
        # Новая Sphinx интеграция
        self.sphinx_adapter = SphinxAdapter()
        self.sphinx_memory = SphinxMemoryStore()
        self.sphinx_percolator = SphinxPercolator()
        self.sphinx_analytics = SphinxAnalytics()
        
        # Fallback на A-MEM если Sphinx недоступен
        self.memory_fallback = get_enhanced_memory_system()
    
    async def execute_task(self, task: str) -> Dict:
        """Выполнение задачи с Sphinx интеграцией"""
        
        # 1. Перколяция: найти агентов для задачи
        triggered_agents = await self.sphinx_percolator.percolate_event(task)
        
        # 2. Семантический поиск похожих задач
        task_embedding = await self.get_task_embedding(task)
        similar_memories = await self.sphinx_adapter.semantic_search(
            task_embedding, 
            filters={'category': 'task_solution'},
            limit=5
        )
        
        # 3. Создание агентов с учётом найденного опыта
        agents = await self.create_smart_agents(triggered_agents, similar_memories)
        
        # 4. Выполнение + сохранение результатов в Sphinx
        results = await self.execute_with_agents(agents)
        await self.save_execution_memory(task, agents, results)
        
        return results
```

### **Обновление AgentFactory**

```python
class AgentFactory:
    async def create_agent_with_sphinx_memory(self, agent_type: str, 
                                            task_context: Dict) -> Agent:
        """Создание агента с доступом к Sphinx памяти"""
        
        # Получение релевантного опыта из Sphinx
        agent_memories = await self.sphinx_adapter.semantic_search(
            query_embedding=task_context['embedding'],
            filters={'agent_id': agent_type, 'success_score': {'$gt': 0.7}},
            limit=10
        )
        
        # Создание агента с предзагруженной памятью
        agent = Agent(
            agent_id=f"{agent_type}_{uuid.uuid4()}",
            agent_type=agent_type,
            sphinx_memory=self.sphinx_adapter,
            preloaded_memories=agent_memories
        )
        
        # Регистрация триггеров агента в перколяторе
        await self.register_agent_triggers(agent)
        
        return agent
        
    async def register_agent_triggers(self, agent: Agent):
        """Регистрация перколяционных правил для агента"""
        triggers = agent.get_trigger_patterns()
        
        for pattern, action, priority in triggers:
            await self.sphinx_percolator.add_trigger_rule(
                agent_id=agent.agent_id,
                pattern=pattern,
                action=action,
                priority=priority
            )
```

---

## 📊 **СХЕМА ДАННЫХ SPHINX**

### **Индекс памяти агентов (kittycore_memory)**

```sql
-- Основной RT индекс для хранения памяти агентов
CREATE TABLE kittycore_memory (
    -- Полнотекстовые поля
    content TEXT,                    -- Основной контент памяти
    agent_id TEXT,                   -- ID агента (поисковое поле)
    category TEXT,                   -- Категория памяти
    tags TEXT,                       -- Теги в JSON формате
    
    -- Атрибуты для фильтрации
    timestamp BIGINT,                -- Unix timestamp создания
    agent_id_attr STRING,            -- ID агента (атрибут для фильтрации)
    category_attr STRING,            -- Категория (атрибут)
    team_id STRING,                  -- ID команды
    metadata JSON,                   -- Произвольные метаданные
    
    -- Векторный индекс
    embedding FLOAT_VECTOR[384],     -- Эмбеддинг для семантического поиска
    
    -- Скоринг и аналитика
    success_score FLOAT,             -- Оценка успешности (0.0-1.0)
    confidence FLOAT,                -- Уверенность в решении
    execution_time INTEGER,          -- Время выполнения (мс)
    
    -- Связи
    parent_memory_id STRING,         -- Родительская память
    related_memories JSON            -- Связанные воспоминания
);
```

### **Перколяционный индекс (kittycore_memory_percolate)**

```sql
-- Перколяционный индекс для агентных триггеров
CREATE TABLE kittycore_memory_percolate (
    -- Поля для перколяции
    trigger_query TEXT,              -- Запрос-триггер
    agent_patterns TEXT,             -- Дополнительные паттерны
    
    -- Атрибуты
    agent_id STRING,                 -- Какой агент должен среагировать
    action STRING,                   -- Какое действие выполнить
    priority INTEGER,                -- Приоритет срабатывания
    conditions JSON,                 -- Дополнительные условия
    active BOOLEAN,                  -- Активность правила
    created_at BIGINT,               -- Время создания
    last_triggered BIGINT            -- Последнее срабатывание
);
```

---

## 🔮 **ВЫВОД ЧАСТИ 2**

**Техническая архитектура обеспечивает:**

- 🏗️ **Модульность**: чистые интерфейсы между компонентами
- 🔄 **Fallback**: работа без Sphinx через A-MEM
- 📈 **Масштабируемость**: горизонтальное масштабирование через Sphinx
- 🛡️ **Надёжность**: connection pooling и error handling
- ⚡ **Производительность**: оптимизированные индексы и запросы

**Следующая часть:**
- **ЧАСТЬ 3**: План поэтапного внедрения 