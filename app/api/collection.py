from fastapi import APIRouter, Request, Query, HTTPException, status, Body
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
import os
from bson import ObjectId
import json
from typing import Any, Dict, List
from app.utils.id_helper import sanitize_id, sanitize_ids, ensure_mongo_id, build_id_query, find_one_by_id_flexible

router = APIRouter(prefix="/db/collections", tags=["collections"])

os.makedirs("logs", exist_ok=True)
logger.add("logs/collections.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)
logger.add("logs/errors.log", format="{time} {level} {message}", level="ERROR", rotation="10 MB", compression="zip", serialize=True)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/universal_agent")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_collection(data: Dict[str, Any] = Body(...)):
    """Создать коллекцию."""
    name = data.get("name")
    if not name:
        logger.error({"event": "create_collection", "error": "name required"})
        raise HTTPException(status_code=400, detail="'name' field is required")
    
    if name in await db.list_collection_names():
        logger.error({"event": "create_collection", "error": "already exists", "name": name})
        raise HTTPException(status_code=400, detail="Collection already exists")
    
    await db.create_collection(name)
    logger.info({"event": "create_collection", "name": name})
    return {"name": name}

@router.get("/", response_model=List[str])
async def list_collections():
    """Получить список всех коллекций."""
    collections = await db.list_collection_names()
    logger.info({"event": "list_collections", "count": len(collections)})
    return collections

@router.post("/{name}/items", status_code=status.HTTP_201_CREATED)
async def create_item(name: str, item: Dict[str, Any] = Body(...)):
    """Создать документ в коллекции. _id будет совпадать с id, если id присутствует."""
    if name not in await db.list_collection_names():
        logger.error({"event": "create_item", "error": "collection not found", "name": name})
        raise HTTPException(status_code=404, detail="Collection not found")
    # Централизовано: всегда ensure_mongo_id
    result = await db[name].insert_one(ensure_mongo_id(item))
    item_id = str(result.inserted_id)
    logger.info({"event": "create_item", "collection": name, "id": item_id})
    return {"id": item_id}

@router.get("/{name}/items", response_model=List[Dict[str, Any]])
async def list_items(name: str, skip: int = 0, limit: int = 100, filter: str = Query(None)):
    """Получить все документы коллекции."""
    if name not in await db.list_collection_names():
        logger.error({"event": "list_items", "error": "collection not found", "name": name})
        raise HTTPException(status_code=404, detail="Collection not found")
    
    query = {}
    if filter:
        try:
            query = json.loads(filter)
        except json.JSONDecodeError:
            logger.error({"event": "list_items", "error": "invalid filter", "filter": filter})
            raise HTTPException(status_code=400, detail="Invalid filter JSON")
    
    docs = await db[name].find(query).skip(skip).limit(limit).to_list(length=limit)
    docs = sanitize_ids(docs)  # Используем нашу утилиту
    
    logger.info({"event": "list_items", "collection": name, "count": len(docs)})
    return docs

@router.get("/{name}/items/{item_id}", response_model=Dict[str, Any])
async def get_item(name: str, item_id: str):
    """Получить документ по id."""
    if name not in await db.list_collection_names():
        logger.error({"event": "get_item", "error": "collection not found", "name": name})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    
    # Используем find_one_by_id_flexible
    doc = await find_one_by_id_flexible(item_id, db[name], target_field_name=None)
    
    if not doc:
        logger.error({"event": "get_item", "error": "not found", "id": item_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    # sanitize_id здесь не нужен, так как find_one_by_id_flexible уже должен возвращать санитайженный документ, если он содержит _id
    # Однако, если find_one_by_id_flexible возвращает сырой документ, то sanitize_id нужен.
    # Предполагаем, что find_one_by_id_flexible возвращает документ, который может потребовать sanitize_id.
    doc_sanitized = sanitize_id(doc) 
    
    logger.info({"event": "get_item", "collection": name, "id": item_id})
    return doc_sanitized

@router.patch("/{name}/items/{item_id}", response_model=Dict[str, Any])
async def update_item(name: str, item_id: str, data: Dict[str, Any] = Body(...)):
    """Обновить документ по id. _id будет совпадать с id, если id присутствует."""
    if name not in await db.list_collection_names():
        logger.error({"event": "update_item", "error": "collection not found", "name": name})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    query = build_id_query(item_id, target_field_name=None, collection_name_for_guess=name)
    if not query:
        logger.error({"event": "update_item", "error": "invalid item_id format for query", "id": item_id})
        raise HTTPException(status_code=400, detail="Invalid item_id format for query")

    update_data = ensure_mongo_id(data) # Убедимся, что _id корректный, если он есть в data
    result = await db[name].update_one(query, {"$set": update_data})
    
    if result.matched_count == 0:
        logger.error({"event": "update_item", "error": "not found", "id": item_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    # После успешного обновления, снова найдем документ для возврата
    updated_doc = await find_one_by_id_flexible(item_id, db[name], target_field_name=None)
    if not updated_doc:
         logger.error({"event": "update_item", "error": "not found after update", "id": item_id})
         raise HTTPException(status_code=404, detail="Item not found after update")

    # sanitize_id здесь не нужен, так как find_one_by_id_flexible уже должен возвращать санитайженный документ
    # Однако, для консистентности, если find_one_by_id_flexible возвращает сырой документ...
    doc_sanitized = sanitize_id(updated_doc)
    
    logger.info({"event": "update_item", "collection": name, "id": item_id})
    return doc_sanitized

@router.delete("/{name}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(name: str, item_id: str):
    """Удалить документ по id."""
    if name not in await db.list_collection_names():
        logger.error({"event": "delete_item", "error": "collection not found", "name": name})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    
    query = build_id_query(item_id, target_field_name=None, collection_name_for_guess=name)
    if not query:
        logger.error({"event": "delete_item", "error": "invalid item_id format for query", "id": item_id})
        raise HTTPException(status_code=400, detail="Invalid item_id format for query")
        
    result = await db[name].delete_one(query)
    
    if result.deleted_count != 1:
        logger.error({"event": "delete_item", "error": "not found or not deleted", "id": item_id})
        raise HTTPException(status_code=404, detail="Item not found or not deleted")
    
    logger.info({"event": "delete_item", "collection": name, "id": item_id})
    return Response(status_code=status.HTTP_204_NO_CONTENT) # Возвращаем Response для 204 