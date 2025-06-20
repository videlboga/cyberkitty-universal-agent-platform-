"""
🏗️ DatabaseTool - Универсальный инструмент для работы с базами данных

Поддерживает SQL (SQLite, PostgreSQL, MySQL) и NoSQL (MongoDB, Redis) базы данных.
"""

import time
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from loguru import logger

from kittycore.tools.base_tool import Tool, ToolResult

# Проверка доступности зависимостей
try:
    from sqlalchemy import create_engine, text, MetaData
    from sqlalchemy.orm import sessionmaker
    SQL_AVAILABLE = True
except ImportError:
    SQL_AVAILABLE = False

try:
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


@dataclass
class DatabaseConnection:
    """Конфигурация подключения к базе данных"""
    db_type: str  # 'sqlite', 'postgresql', 'mysql', 'mongodb', 'redis'
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None
    
    def __post_init__(self):
        """Валидация конфигурации"""
        if not self.connection_string and not self.database:
            if self.db_type == 'sqlite':
                self.database = self.database or 'kittycore.db'
            elif self.db_type in ['postgresql', 'mysql']:
                if not (self.host and self.database):
                    raise ValueError(f"Для {self.db_type} требуются host и database")
            elif self.db_type == 'mongodb':
                self.database = self.database or 'kittycore'
                self.host = self.host or 'localhost'
                self.port = self.port or 27017
            elif self.db_type == 'redis':
                self.host = self.host or 'localhost'
                self.port = self.port or 6379


class DatabaseTool(Tool):
    """Универсальный инструмент для работы с базами данных"""
    
    def __init__(self, default_connection: Optional[DatabaseConnection] = None):
        super().__init__(
            name="database_tool",
            description="Универсальный инструмент для работы с SQL и NoSQL базами данных"
        )
        
        self.connections: Dict[str, Dict] = {}
        self.default_connection = default_connection
        
        # Проверяем зависимости
        self._check_dependencies()
        
        # Инициализируем подключение по умолчанию
        if self.default_connection:
            self._init_default_connection()
    
    def _check_dependencies(self):
        """Проверка доступности зависимостей"""
        missing = []
        if not SQL_AVAILABLE:
            missing.append("sqlalchemy (для SQL баз)")
        if not MONGODB_AVAILABLE:
            missing.append("pymongo (для MongoDB)")
        if not REDIS_AVAILABLE:
            missing.append("redis (для Redis)")
        
        if missing:
            logger.warning(f"⚠️ Отсутствуют зависимости: {', '.join(missing)}")
    
    def _init_default_connection(self):
        """Инициализация подключения по умолчанию"""
        if not self.default_connection:
            return
        
        try:
            db_type = self.default_connection.db_type
            
            if db_type in ['sqlite', 'postgresql', 'mysql']:
                if not SQL_AVAILABLE:
                    logger.error("❌ SQLAlchemy не установлен для SQL подключения")
                    return
                self._init_sql_connection('default', self.default_connection)
                
            elif db_type == 'mongodb':
                if not MONGODB_AVAILABLE:
                    logger.error("❌ PyMongo не установлен для MongoDB подключения")
                    return
                self._init_mongodb_connection('default', self.default_connection)
                
            elif db_type == 'redis':
                if not REDIS_AVAILABLE:
                    logger.error("❌ Redis не установлен для Redis подключения")
                    return
                self._init_redis_connection('default', self.default_connection)
                
            else:
                logger.error(f"❌ Неподдерживаемый тип базы: {db_type}")
                
            logger.info(f"✅ Подключение по умолчанию инициализировано: {db_type}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации подключения по умолчанию: {e}")
    
    def get_available_actions(self) -> List[str]:
        """Получение списка доступных действий"""
        return [
            "execute_sql", "execute_query", "connect_database", "list_tables",
            "mongodb_find", "mongodb_insert", "mongodb_update", "mongodb_delete",
            "redis_get", "redis_set", "redis_delete", "get_connection_info", "close_connection"
        ]
    
    async def execute_sql(self, 
                         query: str, 
                         connection_name: str = 'default',
                         parameters: Optional[Dict] = None) -> ToolResult:
        """Выполнение SQL запроса"""
        try:
            if connection_name not in self.connections:
                return ToolResult(
                    success=False,
                    error=f"Подключение {connection_name} не найдено"
                )
            
            conn_info = self.connections[connection_name]
            if conn_info['type'] != 'sql':
                return ToolResult(
                    success=False,
                    error=f"Подключение {connection_name} не является SQL"
                )
            
            start_time = time.time()
            
            with conn_info['session_maker']() as session:
                result = session.execute(text(query), parameters or {})
                
                if query.strip().upper().startswith('SELECT'):
                    rows = result.fetchall()
                    data = [dict(row._mapping) for row in rows]
                    affected_rows = len(data)
                else:
                    data = None
                    affected_rows = result.rowcount
                    session.commit()
            
            execution_time = time.time() - start_time
            
            result_data = {
                "query": query,
                "connection": connection_name,
                "affected_rows": affected_rows,
                "execution_time": round(execution_time, 4),
                "data": data
            }
            
            return ToolResult(success=True, data=result_data)
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def connect_database(self, 
                             db_type: str,
                             connection_name: str = 'custom',
                             **kwargs) -> ToolResult:
        """Создание нового подключения к базе данных"""
        try:
            config = DatabaseConnection(db_type=db_type, **kwargs)
            
            if db_type in ['sqlite', 'postgresql', 'mysql']:
                if not SQL_AVAILABLE:
                    return ToolResult(
                        success=False,
                        error="SQLAlchemy не установлен"
                    )
                self._init_sql_connection(connection_name, config)
                
            elif db_type == 'mongodb':
                if not MONGODB_AVAILABLE:
                    return ToolResult(
                        success=False,
                        error="PyMongo не установлен"
                    )
                self._init_mongodb_connection(connection_name, config)
                
            elif db_type == 'redis':
                if not REDIS_AVAILABLE:
                    return ToolResult(
                        success=False,
                        error="Redis не установлен"
                    )
                self._init_redis_connection(connection_name, config)
                
            else:
                return ToolResult(
                    success=False,
                    error=f"Неподдерживаемый тип базы: {db_type}"
                )
            
            return ToolResult(
                success=True,
                data={"connection_name": connection_name, "db_type": db_type}
            )
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _init_sql_connection(self, connection_name: str, config: DatabaseConnection):
        """Инициализация SQL подключения"""
        if config.connection_string:
            engine = create_engine(config.connection_string)
        else:
            if config.db_type == 'sqlite':
                engine = create_engine(f"sqlite:///{config.database}")
            elif config.db_type == 'postgresql':
                engine = create_engine(
                    f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
                )
            elif config.db_type == 'mysql':
                engine = create_engine(
                    f"mysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
                )
        
        session_maker = sessionmaker(bind=engine)
        
        self.connections[connection_name] = {
            'type': 'sql',
            'engine': engine,
            'session_maker': session_maker,
            'config': config
        }
    
    def _init_mongodb_connection(self, connection_name: str, config: DatabaseConnection):
        """Инициализация MongoDB подключения"""
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo не установлен")
        
        if config.connection_string:
            conn_str = config.connection_string
        else:
            if config.username and config.password:
                conn_str = f"mongodb://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
            else:
                conn_str = f"mongodb://{config.host}:{config.port}/"
        
        try:
            client = MongoClient(conn_str)
            client.admin.command('ping')
            database = client[config.database]
            
            self.connections[connection_name] = {
                'type': 'mongodb',
                'client': client,
                'database': database,
                'config': config
            }
            
        except Exception as e:
            raise
    
    def _init_redis_connection(self, connection_name: str, config: DatabaseConnection):
        """Инициализация Redis подключения"""
        if not REDIS_AVAILABLE:
            raise ImportError("Redis не установлен")
        
        try:
            redis_client = redis.Redis(
                host=config.host,
                port=config.port,
                username=config.username,
                password=config.password,
                decode_responses=True
            )
            
            redis_client.ping()
            
            self.connections[connection_name] = {
                'type': 'redis',
                'client': redis_client,
                'config': config
            }
            
        except Exception as e:
            raise
    
    # MongoDB операции
    async def mongodb_find(self, collection: str, filter_query: Optional[Dict] = None,
                          connection_name: str = 'default', limit: Optional[int] = None) -> ToolResult:
        """Поиск документов в MongoDB коллекции"""
        try:
            if connection_name not in self.connections:
                return ToolResult(success=False, error=f"Подключение {connection_name} не найдено")
            
            conn_info = self.connections[connection_name]
            if conn_info['type'] != 'mongodb':
                return ToolResult(success=False, error=f"Подключение {connection_name} не является MongoDB")
            
            db = conn_info['database']
            collection_obj = db[collection]
            
            cursor = collection_obj.find(filter_query or {})
            if limit:
                cursor = cursor.limit(limit)
            
            documents = []
            for doc in cursor:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                documents.append(doc)
            
            return ToolResult(success=True, data={"documents": documents, "count": len(documents)})
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def mongodb_insert(self, collection: str, document: Dict[str, Any], 
                           connection_name: str = 'default') -> ToolResult:
        """Вставка документа в MongoDB коллекцию"""
        try:
            if connection_name not in self.connections:
                return ToolResult(success=False, error=f"Подключение {connection_name} не найдено")
            
            conn_info = self.connections[connection_name]
            if conn_info['type'] != 'mongodb':
                return ToolResult(success=False, error=f"Подключение {connection_name} не является MongoDB")
            
            db = conn_info['database']
            collection_obj = db[collection]
            result = collection_obj.insert_one(document)
            
            return ToolResult(success=True, data={"inserted_id": str(result.inserted_id)})
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def mongodb_update(self, collection: str, filter_query: Dict[str, Any], 
                           update_data: Dict[str, Any], connection_name: str = 'default') -> ToolResult:
        """Обновление документов в MongoDB коллекции"""
        try:
            if connection_name not in self.connections:
                return ToolResult(success=False, error=f"Подключение {connection_name} не найдено")
            
            conn_info = self.connections[connection_name]
            if conn_info['type'] != 'mongodb':
                return ToolResult(success=False, error=f"Подключение {connection_name} не является MongoDB")
            
            db = conn_info['database']
            collection_obj = db[collection]
            result = collection_obj.update_many(filter_query, update_data)
            
            return ToolResult(success=True, data={
                "matched_count": result.matched_count,
                "modified_count": result.modified_count
            })
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def mongodb_delete(self, collection: str, filter_query: Dict[str, Any], 
                           connection_name: str = 'default') -> ToolResult:
        """Удаление документов из MongoDB коллекции"""
        try:
            if connection_name not in self.connections:
                return ToolResult(success=False, error=f"Подключение {connection_name} не найдено")
            
            conn_info = self.connections[connection_name]
            if conn_info['type'] != 'mongodb':
                return ToolResult(success=False, error=f"Подключение {connection_name} не является MongoDB")
            
            db = conn_info['database']
            collection_obj = db[collection]
            result = collection_obj.delete_many(filter_query)
            
            return ToolResult(success=True, data={"deleted_count": result.deleted_count})
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    # Redis операции
    async def redis_get(self, key: str, connection_name: str = 'default') -> ToolResult:
        """Получение значения по ключу из Redis"""
        try:
            if connection_name not in self.connections:
                return ToolResult(success=False, error=f"Подключение {connection_name} не найдено")
            
            conn_info = self.connections[connection_name]
            if conn_info['type'] != 'redis':
                return ToolResult(success=False, error=f"Подключение {connection_name} не является Redis")
            
            redis_client = conn_info['client']
            value = redis_client.get(key)
            
            return ToolResult(success=True, data={"key": key, "value": value, "exists": value is not None})
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def redis_set(self, key: str, value: Union[str, int, float], 
                       connection_name: str = 'default', ttl: Optional[int] = None) -> ToolResult:
        """Установка значения по ключу в Redis"""
        try:
            if connection_name not in self.connections:
                return ToolResult(success=False, error=f"Подключение {connection_name} не найдено")
            
            conn_info = self.connections[connection_name]
            if conn_info['type'] != 'redis':
                return ToolResult(success=False, error=f"Подключение {connection_name} не является Redis")
            
            redis_client = conn_info['client']
            
            if ttl:
                result = redis_client.setex(key, ttl, value)
            else:
                result = redis_client.set(key, value)
            
            return ToolResult(success=True, data={"key": key, "value": value, "success": bool(result)})
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def redis_delete(self, key: str, connection_name: str = 'default') -> ToolResult:
        """Удаление ключа из Redis"""
        try:
            if connection_name not in self.connections:
                return ToolResult(success=False, error=f"Подключение {connection_name} не найдено")
            
            conn_info = self.connections[connection_name]
            if conn_info['type'] != 'redis':
                return ToolResult(success=False, error=f"Подключение {connection_name} не является Redis")
            
            redis_client = conn_info['client']
            deleted_count = redis_client.delete(key)
            
            return ToolResult(success=True, data={"key": key, "deleted": deleted_count > 0})
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def get_connection_info(self, connection_name: str = 'default') -> ToolResult:
        """Информация о подключении"""
        if connection_name not in self.connections:
            return ToolResult(success=False, error=f"Подключение {connection_name} не найдено")
        
        conn_info = self.connections[connection_name]
        return ToolResult(success=True, data={
            "connection_name": connection_name,
            "type": conn_info['type'],
            "config": conn_info['config'].__dict__
        })
    
    async def close_connection(self, connection_name: str) -> ToolResult:
        """Закрытие подключения к базе данных"""
        try:
            if connection_name not in self.connections:
                return ToolResult(
                    success=False,
                    error=f"Подключение {connection_name} не найдено"
                )
            
            conn_info = self.connections[connection_name]
            
            # Закрываем подключение в зависимости от типа
            if conn_info['type'] == 'sql':
                conn_info['engine'].dispose()
            elif conn_info['type'] == 'mongodb':
                conn_info['client'].close()
            elif conn_info['type'] == 'redis':
                conn_info['client'].close()
            
            # Удаляем из списка подключений
            del self.connections[connection_name]
            
            return ToolResult(
                success=True,
                data={"connection_name": connection_name}
            )
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    async def execute_action(self, action: str, **kwargs) -> ToolResult:
        """Выполнение действия инструмента"""
        action_map = {
            "execute_sql": self.execute_sql,
            "execute_query": self.execute_sql,
            "connect_database": self.connect_database,
            "list_tables": self.list_tables,
            "mongodb_find": self.mongodb_find,
            "mongodb_insert": self.mongodb_insert,
            "mongodb_update": self.mongodb_update,
            "mongodb_delete": self.mongodb_delete,
            "redis_get": self.redis_get,
            "redis_set": self.redis_set,
            "redis_delete": self.redis_delete,
            "get_connection_info": self.get_connection_info,
            "close_connection": self.close_connection,
        }
        
        if action in action_map:
            return await action_map[action](**kwargs)
        else:
            return ToolResult(
                success=False,
                error=f"Неизвестное действие: {action}",
                metadata={"available_actions": self.get_available_actions()}
            )
    
    async def execute(self, query: str, **kwargs) -> ToolResult:
        """Универсальный метод выполнения запросов"""
        return await self.execute_sql(query, **kwargs)
    
    async def list_tables(self, connection_name: str = 'default') -> ToolResult:
        """Получение списка таблиц"""
        try:
            if connection_name not in self.connections:
                return ToolResult(
                    success=False,
                    error=f"Подключение {connection_name} не найдено"
                )
            
            conn_info = self.connections[connection_name]
            if conn_info['type'] != 'sql':
                return ToolResult(
                    success=False,
                    error=f"Подключение {connection_name} не является SQL"
                )
            
            # Получаем метаданные
            metadata = MetaData()
            metadata.reflect(bind=conn_info['engine'])
            
            tables = []
            for table_name in metadata.tables.keys():
                table = metadata.tables[table_name]
                tables.append({
                    "name": table_name,
                    "columns": len(table.columns),
                    "column_names": [col.name for col in table.columns]
                })
            
            return ToolResult(
                success=True,
                data={"tables": tables, "total_tables": len(tables)}
            )
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def get_schema(self) -> dict:
        """Схема инструмента"""
        return {
            "name": "DatabaseTool",
            "description": self.description,
            "supported_databases": ["sqlite", "postgresql", "mysql", "mongodb", "redis"],
            "actions": self.get_available_actions(),
            "connections": len(self.connections)
        }


def create_database_tool(db_type: str = 'sqlite', **kwargs) -> DatabaseTool:
    """Фабричная функция для создания DatabaseTool"""
    config = DatabaseConnection(db_type=db_type, **kwargs)
    return DatabaseTool(default_connection=config)


def create_sqlite_tool(database: str = 'kittycore.db') -> DatabaseTool:
    """Быстрое создание SQLite инструмента"""
    return create_database_tool('sqlite', database=database)