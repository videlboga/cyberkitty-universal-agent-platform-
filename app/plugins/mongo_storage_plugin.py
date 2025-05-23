from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection, AsyncIOMotorClient
from typing import Dict, Any, Callable, Optional, Union
from bson import ObjectId
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from loguru import logger
from app.plugins.plugin_base import PluginBase

def _resolve_value_from_context(value: Any, context: Dict[str, Any]) -> Any:
    """Рекурсивно подставляет значения из контекста.
    Если value - строка вида "{var_name}", подставляет context[var_name].
    Если value - словарь, рекурсивно обрабатывает его значения.
    Если value - список, рекурсивно обрабатывает его элементы.
    """
    if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
        var_name = value[1:-1]
        return context.get(var_name, value) # Возвращает оригинальное значение, если переменной нет
    elif isinstance(value, dict):
        return {k: _resolve_value_from_context(v, context) for k, v in value.items()}
    elif isinstance(value, list):
        return [_resolve_value_from_context(item, context) for item in value]
    return value

class MongoStoragePlugin(PluginBase):
    def __init__(self, mongo_client: AsyncIOMotorClient, db_name: str = "main_db"):
        super().__init__()
        self.client = mongo_client
        effective_db_name = db_name if db_name else "default_db"
        self.db = self.client[effective_db_name]

    def register_step_handlers(self, step_handlers: Dict[str, Callable]):
        """Регистрирует обработчики шагов, предоставляемые этим плагином."""
        step_handlers["mongo_insert_one"] = self.handle_insert_one
        step_handlers["mongo_find_one"] = self.handle_find_one
        step_handlers["mongo_update_one"] = self.handle_update_one
        step_handlers["mongo_delete_one"] = self.handle_delete_one
        
        registered_handlers_list = ["mongo_insert_one", "mongo_find_one", "mongo_update_one", "mongo_delete_one"]
        logger.info(f"MongoStoragePlugin зарегистрировал обработчики шагов: {registered_handlers_list}")

    def _get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        if not collection_name:
            logger.error("Имя коллекции не может быть пустым.")
            raise ValueError("Имя коллекции не может быть пустым.")
        return self.db[collection_name]

    async def handle_insert_one(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        logger.info(f"[MongoStoragePlugin.handle_insert_one] ENTRY. step_data: {step_data}")
        logger.info(f"[MongoStoragePlugin.handle_insert_one] context: {context}")
        
        try:
            params = _resolve_value_from_context(step_data.get("params", {}), context)
            logger.info(f"[MongoStoragePlugin.handle_insert_one] resolved params: {params}")
        except Exception as e:
            logger.error(f"[MongoStoragePlugin.handle_insert_one] Error resolving params: {e}", exc_info=True)
            context["__step_error__"] = f"Error resolving params: {str(e)}"
            return
            
        collection_name = params.get("collection_name")
        document = params.get("document")
        output_var = params.get("output_var", "inserted_id")

        logger.info(f"[MongoStoragePlugin.handle_insert_one] collection_name: {collection_name}")
        logger.info(f"[MongoStoragePlugin.handle_insert_one] document: {document}")
        logger.info(f"[MongoStoragePlugin.handle_insert_one] output_var: {output_var}")

        if not collection_name or not document:
            error_msg = "Отсутствуют обязательные параметры: collection_name или document"
            logger.error(f"handle_insert_one: {error_msg}")
            context["__step_error__"] = error_msg
            return
        try:
            collection = self._get_collection(collection_name)
            logger.info(f"[MongoStoragePlugin.handle_insert_one] About to insert document: {document}")
            result: InsertOneResult = await collection.insert_one(document)
            inserted_id = str(result.inserted_id)
            context[output_var] = inserted_id
            logger.info(f"Документ вставлен в '{collection_name}', ID: {inserted_id}")
        except Exception as e:
            logger.error(f"Ошибка при вставке в MongoDB ('{collection_name}'): {e}", exc_info=True)
            context["__step_error__"] = str(e)
            context[output_var] = None

    async def handle_find_one(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        params = _resolve_value_from_context(step_data.get("params", {}), context)
        collection_name = params.get("collection_name")
        query = params.get("query", {})
        output_var = params.get("output_var", "found_document")

        if not collection_name:
            error_msg = "Отсутствует обязательный параметр: collection_name"
            logger.error(f"handle_find_one: {error_msg}")
            context["__step_error__"] = error_msg
            return
        try:
            collection = self._get_collection(collection_name)
            document = await collection.find_one(query)
            if document and "_id" in document:
                document["_id"] = str(document["_id"]) # Сериализация ObjectId
            context[output_var] = document
            logger.info(f"Поиск в '{collection_name}' по запросу {query}. Результат: {'Найден' if document else 'Не найден'}")
        except Exception as e:
            logger.error(f"Ошибка при поиске в MongoDB ('{collection_name}'): {e}", exc_info=True)
            context["__step_error__"] = str(e)
            context[output_var] = None

    async def handle_update_one(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        params = _resolve_value_from_context(step_data.get("params", {}), context)
        collection_name = params.get("collection_name")
        query = params.get("query")
        update_data = params.get("update_data") # Должен быть {$set: {...}, $inc: {...}, ...}
        output_var = params.get("output_var", "update_result") # Например, modified_count

        if not collection_name or not query or not update_data:
            error_msg = "Отсутствуют обязательные параметры: collection_name, query или update_data"
            logger.error(f"handle_update_one: {error_msg}")
            context["__step_error__"] = error_msg
            return
        try:
            collection = self._get_collection(collection_name)
            result: UpdateResult = await collection.update_one(query, update_data)
            context[output_var] = {"matched_count": result.matched_count, "modified_count": result.modified_count}
            logger.info(f"Обновление в '{collection_name}' по запросу {query}. Совпало: {result.matched_count}, Изменено: {result.modified_count}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении в MongoDB ('{collection_name}'): {e}", exc_info=True)
            context["__step_error__"] = str(e)
            context[output_var] = None

    async def handle_delete_one(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        params = _resolve_value_from_context(step_data.get("params", {}), context)
        collection_name = params.get("collection_name")
        query = params.get("query")
        output_var = params.get("output_var", "delete_result") # Например, deleted_count

        if not collection_name or not query:
            error_msg = "Отсутствуют обязательные параметры: collection_name или query"
            logger.error(f"handle_delete_one: {error_msg}")
            context["__step_error__"] = error_msg
            return
        try:
            collection = self._get_collection(collection_name)
            result: DeleteResult = await collection.delete_one(query)
            context[output_var] = {"deleted_count": result.deleted_count}
            logger.info(f"Удаление из '{collection_name}' по запросу {query}. Удалено: {result.deleted_count}")
        except Exception as e:
            logger.error(f"Ошибка при удалении из MongoDB ('{collection_name}'): {e}", exc_info=True)
            context["__step_error__"] = str(e)
            context[output_var] = None

# TODO: Подумать над более сложной и безопасной подстановкой переменных из контекста,
# особенно для filter_query и update_document. Возможно, использовать JSONPath или аналогичный механизм.
# Пока что подстановка очень простая и только для верхнего уровня в handle_mongo_insert_one. 