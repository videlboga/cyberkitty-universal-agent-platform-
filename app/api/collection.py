from fastapi import APIRouter, HTTPException, status, Body
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
import os
from bson import ObjectId
from typing import Any, Dict, List

router = APIRouter(prefix="/db/collections", tags=["collections"])

os.makedirs("logs", exist_ok=True)
logger.add("logs/audit.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)
logger.add("logs/errors.log", format="{time} {level} {message}", level="ERROR", rotation="10 MB", compression="zip", serialize=True)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/universal_agent")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_collection(data: Dict[str, Any] = Body(...)):
    """Создать новую коллекцию по имени."""
    name = data.get("name")
    if not name:
        logger.error({"event": "create_collection", "error": "name required", "data": data})
        raise HTTPException(status_code=400, detail="name required")
    if name in await db.list_collection_names():
        logger.warning({"event": "create_collection", "error": "already exists", "name": name})
        raise HTTPException(status_code=409, detail="Collection already exists")
    await db.create_collection(name)
    logger.info({"event": "create_collection", "name": name})
    return {"status": "ok", "name": name}

@router.get("/", response_model=List[str])
async def list_collections():
    """Получить список всех коллекций."""
    names = await db.list_collection_names()
    logger.info({"event": "list_collections", "count": len(names)})
    return names

@router.post("/{name}/items", status_code=status.HTTP_201_CREATED)
async def create_item(name: str, item: Dict[str, Any] = Body(...)):
    """Создать документ в коллекции."""
    if name not in await db.list_collection_names():
        logger.error({"event": "create_item", "error": "collection not found", "name": name})
        raise HTTPException(status_code=404, detail="Collection not found")
    result = await db[name].insert_one(item)
    logger.info({"event": "create_item", "collection": name, "id": str(result.inserted_id)})
    return {"id": str(result.inserted_id), **item}

@router.get("/{name}/items", response_model=List[Dict[str, Any]])
async def list_items(name: str, skip: int = 0, limit: int = 100):
    """Получить все документы коллекции."""
    if name not in await db.list_collection_names():
        logger.error({"event": "list_items", "error": "collection not found", "name": name})
        raise HTTPException(status_code=404, detail="Collection not found")
    docs = await db[name].find().skip(skip).limit(limit).to_list(length=limit)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    logger.info({"event": "list_items", "collection": name, "count": len(docs)})
    return docs

@router.get("/{name}/items/{item_id}", response_model=Dict[str, Any])
async def get_item(name: str, item_id: str):
    """Получить документ по id."""
    if name not in await db.list_collection_names():
        logger.error({"event": "get_item", "error": "collection not found", "name": name})
        raise HTTPException(status_code=404, detail="Collection not found")
    doc = await db[name].find_one({"_id": ObjectId(item_id)})
    if not doc:
        logger.error({"event": "get_item", "error": "not found", "id": item_id})
        raise HTTPException(status_code=404, detail="Item not found")
    doc["id"] = str(doc.pop("_id"))
    logger.info({"event": "get_item", "collection": name, "id": item_id})
    return doc

@router.patch("/{name}/items/{item_id}", response_model=Dict[str, Any])
async def update_item(name: str, item_id: str, data: Dict[str, Any] = Body(...)):
    """Обновить документ по id."""
    if name not in await db.list_collection_names():
        logger.error({"event": "update_item", "error": "collection not found", "name": name})
        raise HTTPException(status_code=404, detail="Collection not found")
    await db[name].update_one({"_id": ObjectId(item_id)}, {"$set": data})
    doc = await db[name].find_one({"_id": ObjectId(item_id)})
    if not doc:
        logger.error({"event": "update_item", "error": "not found", "id": item_id})
        raise HTTPException(status_code=404, detail="Item not found")
    doc["id"] = str(doc.pop("_id"))
    logger.info({"event": "update_item", "collection": name, "id": item_id})
    return doc

@router.delete("/{name}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(name: str, item_id: str):
    """Удалить документ по id."""
    if name not in await db.list_collection_names():
        logger.error({"event": "delete_item", "error": "collection not found", "name": name})
        raise HTTPException(status_code=404, detail="Collection not found")
    result = await db[name].delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count != 1:
        logger.error({"event": "delete_item", "error": "not found", "id": item_id})
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info({"event": "delete_item", "collection": name, "id": item_id})
    return None 