from fastapi import APIRouter, Request, Query, HTTPException, status, Body
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
import os
from bson import ObjectId
import json
from typing import Any, Dict, List
from app.utils.id_helper import to_object_id, safe_object_id, sanitize_id, sanitize_ids, handle_id_query

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
    """Создать документ в коллекции."""
    if name not in await db.list_collection_names():
        logger.error({"event": "create_item", "error": "collection not found", "name": name})
        raise HTTPException(status_code=404, detail="Collection not found")
    result = await db[name].insert_one(item)
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
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Поддержка поиска как по ObjectId, так и по другим полям (name, slug)
    query = handle_id_query(item_id, db[name])
    doc = await db[name].find_one(query)
    
    if not doc:
        logger.error({"event": "get_item", "error": "not found", "id": item_id})
        raise HTTPException(status_code=404, detail="Item not found")
    
    doc = sanitize_id(doc)  # Используем нашу утилиту
    
    logger.info({"event": "get_item", "collection": name, "id": item_id})
    return doc

@router.patch("/{name}/items/{item_id}", response_model=Dict[str, Any])
async def update_item(name: str, item_id: str, data: Dict[str, Any] = Body(...)):
    """Обновить документ по id."""
    if name not in await db.list_collection_names():
        logger.error({"event": "update_item", "error": "collection not found", "name": name})
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Поддержка поиска как по ObjectId, так и по другим полям (name, slug)
    query = handle_id_query(item_id, db[name])
    
    # Выполняем обновление
    result = await db[name].update_one(query, {"$set": data})
    
    if result.matched_count == 0:
        logger.error({"event": "update_item", "error": "not found", "id": item_id})
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Получаем обновленный документ
    doc = await db[name].find_one(query)
    doc = sanitize_id(doc)  # Используем нашу утилиту
    
    logger.info({"event": "update_item", "collection": name, "id": item_id})
    return doc

@router.delete("/{name}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(name: str, item_id: str):
    """Удалить документ по id."""
    if name not in await db.list_collection_names():
        logger.error({"event": "delete_item", "error": "collection not found", "name": name})
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Поддержка удаления как по ObjectId, так и по другим полям (name, slug)
    query = handle_id_query(item_id, db[name])
    
    result = await db[name].delete_one(query)
    
    if result.deleted_count != 1:
        logger.error({"event": "delete_item", "error": "not found", "id": item_id})
        raise HTTPException(status_code=404, detail="Item not found")
    
    logger.info({"event": "delete_item", "collection": name, "id": item_id})
    return None 