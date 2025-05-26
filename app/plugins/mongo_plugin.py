#!/usr/bin/env python3
"""
MongoDB Plugin для Universal Agent Platform.
Принцип: Простота в работе с БД.

Обеспечивает:
- Хранение агентов, сценариев и пользователей
- CRUD операции 
- Поиск и фильтрация
"""

import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from loguru import logger

from app.core.base_plugin import BasePlugin
from app.models import ChannelMapping, Scenario, User, ScenarioExecution
from app.config.database import DB_CONFIG


class MongoPlugin(BasePlugin):
    """
    Плагин для работы с MongoDB.
    
    Коллекции:
    - scenarios - сценарии
    - users - пользователи
    - executions - история выполнений
    - channel_mappings - маппинги каналов к сценариям
    """
    
    def __init__(self):
        super().__init__(name="mongo")
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

        self.scenarios_collection = None
        self.users_collection = None
        self.executions_collection = None
        self.channel_mappings_collection = None
        self.channel_mappings_collection = None
        
    async def _do_initialize(self):
        """Инициализация подключения к MongoDB с retry логикой."""
        for attempt in range(DB_CONFIG.retry_attempts):
            try:
                logger.info(f"🔌 Подключение к MongoDB (попытка {attempt + 1}/{DB_CONFIG.retry_attempts})")
                logger.info(f"📊 URI: {DB_CONFIG.uri} -> БД: {DB_CONFIG.database_name}")
                
                # Создаем клиент с таймаутами
                connection_string = DB_CONFIG.get_connection_string()
                self.client = AsyncIOMotorClient(
                    connection_string,
                    serverSelectionTimeoutMS=DB_CONFIG.connection_timeout * 1000,
                    connectTimeoutMS=DB_CONFIG.connection_timeout * 1000,
                    socketTimeoutMS=DB_CONFIG.connection_timeout * 1000
                )
                
                self.db = self.client[DB_CONFIG.database_name]
                
                # Получаем коллекции
                self.scenarios_collection = self.db.scenarios
                self.users_collection = self.db.users
                self.executions_collection = self.db.executions
                self.channel_mappings_collection = self.db.channel_mappings
                
                # Проверяем соединение
                await self.client.admin.command('ismaster')
                
                # Запускаем миграции
                await self._ensure_database_structure()
                
                logger.info("✅ MongoDB подключение установлено")
                return
                
            except Exception as e:
                logger.error(f"❌ Ошибка подключения к MongoDB (попытка {attempt + 1}): {e}")
                
                if attempt < DB_CONFIG.retry_attempts - 1:
                    logger.info(f"⏳ Ожидание {DB_CONFIG.retry_delay} секунд перед повторной попыткой...")
                    await asyncio.sleep(DB_CONFIG.retry_delay)
                else:
                    logger.error("❌ Все попытки подключения к MongoDB исчерпаны")
                    self.client = None
            
    async def _ensure_database_structure(self):
        """Гарантирует корректную структуру БД через миграции."""
        try:
            from app.database.migrations import ensure_database_ready
            await ensure_database_ready()
            logger.info("✅ Структура БД проверена и готова")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось проверить структуру БД: {e}")
            # Fallback - создаём базовые индексы
            await self._create_basic_indexes()
    
    async def _create_basic_indexes(self):
        """Создает минимальные индексы (fallback)."""
        try:
            logger.info("🔧 Создание минимальных индексов...")
            
            # Только уникальные индексы для быстрого поиска
            await self.scenarios_collection.create_index("scenario_id", unique=True)
            await self.users_collection.create_index([("user_id", 1), ("channel_type", 1)], unique=True)
            await self.channel_mappings_collection.create_index("channel_id", unique=True)
            
            logger.info("✅ Минимальные индексы созданы")
            
        except Exception as e:
            logger.warning(f"⚠️ Не удалось создать индексы: {e}")
            
    def register_handlers(self) -> Dict[str, Any]:
        """Регистрирует обработчики для MongoDB операций."""
        return {
            # === УНИВЕРСАЛЬНЫЕ МЕТОДЫ ===
            "mongo_insert_document": self._wrap_handler(self.insert_document),
            "mongo_upsert_document": self._wrap_handler(self.upsert_document),
            "mongo_find_documents": self._wrap_handler(self.find_documents),
            "mongo_find_one_document": self._wrap_handler(self.find_one_document),
            "mongo_update_document": self._wrap_handler(self.update_document),
            "mongo_delete_document": self._wrap_handler(self.delete_document),
            
            # ChannelMapping (новая упрощённая система)
            "mongo_create_channel_mapping": self._wrap_step_handler(self.create_channel_mapping),
            "mongo_get_channel_mapping": self._wrap_step_handler(self.get_channel_mapping),
            "mongo_list_channel_mappings": self._wrap_step_handler(self.list_channel_mappings),
            "mongo_delete_channel_mapping": self._wrap_step_handler(self.delete_channel_mapping),
            
            # Сценарии (совместимость)
            "mongo_create_scenario": self._wrap_handler(self.create_scenario),
            "mongo_get_scenario": self._wrap_step_handler(self.get_scenario_by_id),
            "mongo_get_scenario_by_id": self._wrap_step_handler(self.get_scenario_by_id),
            "mongo_update_scenario": self._wrap_handler(self.update_scenario),
            "mongo_delete_scenario": self._wrap_handler(self.delete_scenario),
            "mongo_list_scenarios": self._wrap_handler(self.list_scenarios),
            
            # Выполнения (совместимость)
            "mongo_create_execution": self._wrap_handler(self.create_execution),
            "mongo_get_execution": self._wrap_handler(self.get_execution),
            "mongo_update_execution": self._wrap_handler(self.update_execution),
            "mongo_list_executions": self._wrap_handler(self.list_executions),
            
            # Дополнительные обработчики
            "mongo_save_scenario": self._wrap_handler(self.save_scenario),
        }
    
    def _wrap_handler(self, handler):
        """Обёртка для обработчиков с сигнатурой (context)."""
        async def wrapper(step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            # Извлекаем параметры из шага
            params = step.get("params", {})
            output_var = params.get("output_var")
            context_key = params.get("context_key")  # Для совместимости с атомарными сценариями
            
            # Объединяем контекст с параметрами
            merged_context = {**context, **params}
            
            # Вызываем оригинальный обработчик
            result = await handler(merged_context)
            
            # Сохраняем результат в контекст
            if output_var:
                context[output_var] = result
            elif context_key:
                context[context_key] = result
            
            return context
            
        return wrapper
    
    def _wrap_step_handler(self, handler):
        """Обёртка для обработчиков с сигнатурой (step, context)."""
        return handler
    
    async def healthcheck(self) -> bool:
        """Проверяет состояние MongoDB подключения."""
        try:
            if not self.client:
                return False
                
            # Пинг БД
            await self.client.admin.command('ismaster')
            return True
            
        except Exception as e:
            logger.error(f"MongoDB healthcheck failed: {e}")
            return False
    
    # === СЦЕНАРИИ ===
    
    async def create_scenario(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Создает новый сценарий."""
        try:
            if not self.client:
                raise Exception("MongoDB не подключен")
                
            # Создаем сценарий из контекста
            scenario_data = {
                "scenario_id": context["scenario_id"],
                "name": context["name"],
                "description": context.get("description"),
                "steps": context["steps"],
                "initial_context": context.get("initial_context", {}),
                "version": 1,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "created_by": context.get("created_by"),
                "usage_count": 0
            }
            
            # Вставляем в БД
            result = await self.scenarios_collection.insert_one(scenario_data)
            db_id = str(result.inserted_id)
            
            logger.info(f"✅ Создан сценарий: {scenario_data['scenario_id']} (DB ID: {db_id})")
            
            return {
                "success": True,
                "scenario_id": scenario_data["scenario_id"],
                "db_id": db_id,
                "scenario": {
                    "id": db_id,
                    "scenario_id": scenario_data["scenario_id"],
                    "name": scenario_data["name"],
                    "description": scenario_data.get("description"),
                    "steps": scenario_data["steps"],
                    "initial_context": scenario_data.get("initial_context", {}),
                    "version": scenario_data["version"],
                    "created_at": scenario_data["created_at"].isoformat(),
                    "updated_at": scenario_data["updated_at"].isoformat(),
                    "created_by": scenario_data.get("created_by"),
                    "is_public": scenario_data.get("is_public", False),
                    "usage_count": scenario_data["usage_count"]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания сценария: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_scenario_by_id(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Получает сценарий по scenario_id."""
        try:
            if not self.client:
                logger.error("MongoDB не подключен")
                return context
                
            # Извлекаем параметры из step (стандартный подход)
            scenario_id = self.get_param(step, "scenario_id", required=True)
            output_var = self.get_param(step, "output_var")
            
            # Поиск сценария (упрощённо)
            scenario_data = await self.scenarios_collection.find_one({
                "scenario_id": scenario_id
            })
            
            if scenario_data:
                # Конвертируем ObjectId в строку
                scenario_data["id"] = str(scenario_data["_id"])
                del scenario_data["_id"]
                
                # Обновляем статистику использования
                await self.scenarios_collection.update_one(
                    {"scenario_id": scenario_id},
                    {
                        "$inc": {"usage_count": 1},
                        "$set": {"last_used": datetime.utcnow()}
                    }
                )
                
                result = {"success": True, "scenario": scenario_data}
            else:
                result = {"success": False, "error": "Сценарий не найден"}
            
            # Сохраняем результат в контекст если указана переменная
            if output_var:
                context[output_var] = result
                
            return context
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения сценария: {e}")
            if self.get_param(step, "output_var"):
                context[self.get_param(step, "output_var")] = {"success": False, "error": str(e)}
            return context
    
    async def list_scenarios(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Получает список сценариев."""
        try:
            if not self.client:
                return {"success": False, "error": "MongoDB не подключен"}
                
            # Простой поиск всех сценариев
            filters = {}
            # Убираем сложные фильтры для упрощения
                
            # Поиск сценариев
            cursor = self.scenarios_collection.find(filters)
            scenarios = []
            
            async for scenario_data in cursor:
                scenario_data["id"] = str(scenario_data["_id"])
                del scenario_data["_id"]
                scenarios.append(scenario_data)
                
            return {
                "success": True,
                "scenarios": scenarios,
                "count": len(scenarios)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка сценариев: {e}")
            return {"success": False, "error": str(e)}
    
    # === ВЫПОЛНЕНИЯ ===
    
    async def create_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Создает запись о выполнении сценария."""
        try:
            if not self.client:
                return {"success": False, "error": "MongoDB не подключен"}
                
            execution_data = {
                "agent_id": context["agent_id"],
                "scenario_id": context["scenario_id"],
                "user_id": context.get("user_id"),
                "chat_id": context.get("chat_id"),
                "started_at": datetime.utcnow(),
                "initial_context": context.get("initial_context", {}),
                "executed_steps": [],
                "current_step": context.get("current_step")
            }
            
            result = await self.executions_collection.insert_one(execution_data)
            execution_id = str(result.inserted_id)
            
            return {
                "success": True,
                "execution_id": execution_id
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания записи выполнения: {e}")
            return {"success": False, "error": str(e)}
    
    # === НЕДОСТАЮЩИЕ МЕТОДЫ ===
    
    async def update_scenario(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Обновляет сценарий."""
        try:
            if not self.client:
                return {"success": False, "error": "MongoDB не подключен"}
                
            scenario_id = context["scenario_id"]
            update_data = context.get("update_data", {})
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.scenarios_collection.update_one(
                {"scenario_id": scenario_id},
                {"$set": update_data}
            )
            
            return {"success": True, "modified_count": result.modified_count}
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления сценария: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_scenario(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Удаляет сценарий (жёсткое удаление для простоты)."""
        try:
            if not self.client:
                return {"success": False, "error": "MongoDB не подключен"}
                
            scenario_id = context["scenario_id"]
            
            # Простое удаление без мягкого удаления
            result = await self.scenarios_collection.delete_one({"scenario_id": scenario_id})
            
            return {"success": True, "deleted_count": result.deleted_count}
            
        except Exception as e:
            logger.error(f"❌ Ошибка удаления сценария: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Получает выполнение по ID."""
        try:
            if not self.client:
                return {"success": False, "error": "MongoDB не подключен"}
                
            execution_id = context["execution_id"]
            
            execution_data = await self.executions_collection.find_one({"_id": ObjectId(execution_id)})
            
            if not execution_data:
                return {"success": False, "error": "Выполнение не найдено"}
                
            execution_data["id"] = str(execution_data["_id"])
            del execution_data["_id"]
            
            return {"success": True, "execution": execution_data}
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения выполнения: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Обновляет выполнение."""
        try:
            if not self.client:
                return {"success": False, "error": "MongoDB не подключен"}
                
            execution_id = context["execution_id"]
            update_data = context.get("update_data", {})
            
            result = await self.executions_collection.update_one(
                {"_id": ObjectId(execution_id)},
                {"$set": update_data}
            )
            
            return {"success": True, "modified_count": result.modified_count}
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления выполнения: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_executions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Получает список выполнений."""
        try:
            if not self.client:
                return {"success": False, "error": "MongoDB не подключен"}
                
            filters = {}
            if "agent_id" in context:
                filters["agent_id"] = context["agent_id"]
            if "scenario_id" in context:
                filters["scenario_id"] = context["scenario_id"]
                
            cursor = self.executions_collection.find(filters).sort("started_at", -1).limit(100)
            executions = []
            
            async for execution_data in cursor:
                execution_data["id"] = str(execution_data["_id"])
                del execution_data["_id"]
                executions.append(execution_data)
                
            return {"success": True, "executions": executions, "count": len(executions)}
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка выполнений: {e}")
            return {"success": False, "error": str(e)}
    
    # === CHANNEL MAPPING (новая упрощённая система) ===
    
    async def create_channel_mapping(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Создаёт новый маппинг канала на сценарий."""
        try:
            if not self.client:
                logger.error("MongoDB не подключен")
                return context
                
            # Извлекаем параметры из step
            channel_id = self.get_param(step, "channel_id", required=True)
            scenario_id = self.get_param(step, "scenario_id", required=True)
            channel_type = self.get_param(step, "channel_type", required=True)
            channel_config = self.get_param(step, "channel_config", default={})
            output_var = self.get_param(step, "output_var")
            
            # Создаём маппинг
            mapping_data = {
                "channel_id": channel_id,
                "scenario_id": scenario_id,
                "channel_type": channel_type,
                "channel_config": channel_config,
                "created_at": datetime.utcnow()
            }
            
            # Используем upsert для обновления существующего маппинга
            result = await self.channel_mappings_collection.replace_one(
                {"channel_id": channel_id},
                mapping_data,
                upsert=True
            )
            
            logger.info(f"✅ Создан/обновлён маппинг: {channel_id} -> {scenario_id}")
            
            mapping_result = {
                "success": True,
                "channel_id": channel_id,
                "scenario_id": scenario_id,
                "channel_type": channel_type,
                "upserted": result.upserted_id is not None
            }
            
            # Сохраняем результат в контекст если указана переменная
            if output_var:
                context[output_var] = mapping_result
                
            return context
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания маппинга: {e}")
            if self.get_param(step, "output_var"):
                context[self.get_param(step, "output_var")] = {"success": False, "error": str(e)}
            return context
    
    async def get_channel_mapping(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Получает маппинг по channel_id."""
        try:
            if not self.client:
                logger.error("MongoDB не подключен")
                return context
                
            # Извлекаем параметры из step
            channel_id = self.get_param(step, "channel_id", required=True)
            output_var = self.get_param(step, "output_var")
            
            # Поиск маппинга
            mapping_data = await self.channel_mappings_collection.find_one({"channel_id": channel_id})
            
            if mapping_data:
                # Конвертируем ObjectId в строку
                mapping_data["id"] = str(mapping_data["_id"])
                del mapping_data["_id"]
                
                result = {"success": True, "mapping": mapping_data}
            else:
                result = {"success": False, "error": "Маппинг не найден"}
            
            # Сохраняем результат в контекст если указана переменная
            if output_var:
                context[output_var] = result
                
            return context
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения маппинга: {e}")
            if self.get_param(step, "output_var"):
                context[self.get_param(step, "output_var")] = {"success": False, "error": str(e)}
            return context
    
    async def list_channel_mappings(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Получает список маппингов."""
        try:
            if not self.client:
                logger.error("MongoDB не подключен")
                return context
                
            # Извлекаем параметры из step
            channel_type = self.get_param(step, "channel_type")
            output_var = self.get_param(step, "output_var")
            
            # Фильтры
            filters = {}
            if channel_type:
                filters["channel_type"] = channel_type
                
            # Поиск маппингов
            cursor = self.channel_mappings_collection.find(filters).sort("created_at", -1)
            mappings = []
            
            async for mapping_data in cursor:
                mapping_data["id"] = str(mapping_data["_id"])
                del mapping_data["_id"]
                mappings.append(mapping_data)
                
            result = {
                "success": True,
                "mappings": mappings,
                "count": len(mappings)
            }
            
            # Сохраняем результат в контекст если указана переменная
            if output_var:
                context[output_var] = result
                
            return context
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка маппингов: {e}")
            if self.get_param(step, "output_var"):
                context[self.get_param(step, "output_var")] = {"success": False, "error": str(e)}
            return context
    
    async def delete_channel_mapping(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Удаляет маппинг по channel_id."""
        try:
            if not self.client:
                logger.error("MongoDB не подключен")
                return context
                
            # Извлекаем параметры из step
            channel_id = self.get_param(step, "channel_id", required=True)
            output_var = self.get_param(step, "output_var")
            
            # Удаление маппинга
            result = await self.channel_mappings_collection.delete_one({"channel_id": channel_id})
            
            mapping_result = {
                "success": True,
                "deleted_count": result.deleted_count
            }
            
            logger.info(f"✅ Удалён маппинг: {channel_id} (удалено: {result.deleted_count})")
            
            # Сохраняем результат в контекст если указана переменная
            if output_var:
                context[output_var] = mapping_result
                
            return context
            
        except Exception as e:
            logger.error(f"❌ Ошибка удаления маппинга: {e}")
            if self.get_param(step, "output_var"):
                context[self.get_param(step, "output_var")] = {"success": False, "error": str(e)}
            return context
    
    # === УНИВЕРСАЛЬНЫЕ МЕТОДЫ ===
    
    async def insert_document(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Универсальная вставка документа в любую коллекцию."""
        try:
            if not self.client:
                return {"success": False, "error": "MongoDB не подключен"}
                
            collection_name = context["collection"]
            document = context["document"]
            
            collection = self.db[collection_name]
            result = await collection.insert_one(document)
            
            logger.info(f"✅ Документ вставлен в {collection_name}: {result.inserted_id}")
            
            return {
                "success": True,
                "inserted_id": str(result.inserted_id),
                "collection": collection_name
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка вставки документа: {e}")
            return {"success": False, "error": str(e)}
    
    async def upsert_document(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Универсальная вставка/обновление документа."""
        try:
            if not self.client:
                return {"success": False, "error": "MongoDB не подключен"}
                
            collection_name = context["collection"]
            filter_query = context["filter"]
            document = context["document"]
            
            collection = self.db[collection_name]
            result = await collection.replace_one(
                filter_query,
                document,
                upsert=True
            )
            
            logger.info(f"✅ Документ upsert в {collection_name}: {'создан' if result.upserted_id else 'обновлён'}")
            
            return {
                "success": True,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None,
                "modified_count": result.modified_count,
                "matched_count": result.matched_count,
                "collection": collection_name
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка upsert документа: {e}")
            return {"success": False, "error": str(e)}
    
    async def find_documents(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Универсальный поиск документов."""
        try:
            if not self.client:
                return {"success": False, "error": "MongoDB не подключен"}
                
            collection_name = context["collection"]
            filter_query = context.get("filter", {})
            limit = context.get("limit", 100)
            sort = context.get("sort")
            
            collection = self.db[collection_name]
            cursor = collection.find(filter_query).limit(limit)
            
            if sort:
                cursor = cursor.sort(sort)
                
            documents = []
            async for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                documents.append(doc)
                
            return {
                "success": True,
                "documents": documents,
                "count": len(documents),
                "collection": collection_name
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска документов: {e}")
            return {"success": False, "error": str(e)}
    
    async def find_one_document(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Универсальный поиск одного документа."""
        try:
            if not self.client:
                return {"success": False, "error": "MongoDB не подключен"}
                
            collection_name = context["collection"]
            filter_query = context["filter"]
            
            collection = self.db[collection_name]
            document = await collection.find_one(filter_query)
            
            if document:
                document["id"] = str(document["_id"])
                del document["_id"]
                
                return {
                    "success": True,
                    "document": document,
                    "collection": collection_name
                }
            else:
                return {
                    "success": False,
                    "error": "Документ не найден",
                    "collection": collection_name
                }
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска документа: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_document(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Универсальное обновление документа."""
        try:
            if not self.client:
                return {"success": False, "error": "MongoDB не подключен"}
                
            collection_name = context["collection"]
            filter_query = context["filter"]
            update_data = context["update"]
            
            collection = self.db[collection_name]
            result = await collection.update_one(filter_query, {"$set": update_data})
            
            logger.info(f"✅ Документ обновлён в {collection_name}: {result.modified_count} изменений")
            
            return {
                "success": True,
                "modified_count": result.modified_count,
                "matched_count": result.matched_count,
                "collection": collection_name
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления документа: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_document(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Универсальное удаление документа."""
        try:
            if not self.client:
                return {"success": False, "error": "MongoDB не подключен"}
                
            collection_name = context["collection"]
            filter_query = context["filter"]
            
            collection = self.db[collection_name]
            result = await collection.delete_one(filter_query)
            
            logger.info(f"✅ Документ удалён из {collection_name}: {result.deleted_count} удалений")
            
            return {
                "success": True,
                "deleted_count": result.deleted_count,
                "collection": collection_name
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка удаления документа: {e}")
            return {"success": False, "error": str(e)}
            
    async def save_scenario(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Сохраняет сценарий в БД."""
        try:
            scenario_data = context.get("scenario")
            if not scenario_data:
                return {"success": False, "error": "scenario data is required"}
            
            # Сохраняем в коллекцию scenarios
            collection = self.db["scenarios"]
            
            # Используем upsert для обновления существующего или создания нового
            filter_query = {"scenario_id": scenario_data["scenario_id"]}
            result = await collection.replace_one(filter_query, scenario_data, upsert=True)
            
            logger.info(f"✅ Сценарий {scenario_data['scenario_id']} сохранен в БД")
            
            return {
                "success": True,
                "scenario_id": scenario_data["scenario_id"],
                "upserted_id": str(result.upserted_id) if result.upserted_id else None,
                "modified_count": result.modified_count
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения сценария: {e}")
            return {"success": False, "error": str(e)}