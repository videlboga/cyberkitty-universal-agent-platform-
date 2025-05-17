from bson import ObjectId
from typing import Optional, Union, Dict, Any, List
from fastapi import HTTPException

def to_object_id(id_value: Any) -> Optional[ObjectId]:
    """
    Безопасно преобразует строку или другое значение в ObjectId.
    
    Args:
        id_value: Значение для преобразования (строка, ObjectId или None)
        
    Returns:
        ObjectId или None, если преобразование невозможно
    """
    if id_value is None:
        return None
        
    if isinstance(id_value, ObjectId):
        return id_value
        
    try:
        # Если передан специальный id (например, "manager", "coach"), 
        # попробуем найти его по имени (не как ObjectId)
        if isinstance(id_value, str) and len(id_value) != 24 and not id_value.isalnum():
            return id_value
            
        # Пытаемся преобразовать в ObjectId
        return ObjectId(id_value)
    except Exception:
        return None

def safe_object_id(id_value: Any) -> ObjectId:
    """
    Безопасно преобразует строку в ObjectId с выбросом исключения при неудаче.
    
    Args:
        id_value: Значение для преобразования
        
    Returns:
        ObjectId
        
    Raises:
        HTTPException: если преобразование невозможно
    """
    obj_id = to_object_id(id_value)
    if obj_id is None:
        raise HTTPException(status_code=400, 
                           detail=f"Некорректный формат ID: '{id_value}'. "
                                  f"Требуется 24-символьная hex-строка.")
    return obj_id

def sanitize_id(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Преобразует _id в документе MongoDB в строку id для совместимости с JSON.
    
    Args:
        doc: Документ MongoDB
        
    Returns:
        Документ с преобразованным id
    """
    if doc is None:
        return {}
        
    result = dict(doc)
    if "_id" in result:
        result["id"] = str(result.pop("_id"))
    return result

def sanitize_ids(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Преобразует _id в списке документов MongoDB в строки id для совместимости с JSON.
    
    Args:
        docs: Список документов MongoDB
        
    Returns:
        Список документов с преобразованными id
    """
    return [sanitize_id(doc) for doc in docs]

def handle_id_query(id_or_name: str, collection):
    """
    Обрабатывает запрос по ID или имени объекта.
    
    Args:
        id_or_name: ID или имя объекта
        collection: Коллекция MongoDB для поиска
        
    Returns:
        Запрос для MongoDB (filter dict)
    """
    obj_id = to_object_id(id_or_name)
    
    # Проверяем, является ли id_or_name ObjectId
    if obj_id and isinstance(obj_id, ObjectId):
        # Если ObjectId, то ищем по _id
        return {"_id": obj_id}
    else:
        # Ищем сначала по _id как есть (для строковых ID),
        # затем по имени или slug
        return {"$or": [
            {"_id": id_or_name},
            {"name": id_or_name}, 
            {"slug": id_or_name}
        ]}

def ensure_mongo_id(doc):
    """
    Гарантирует, что если в документе есть поле id, то _id будет совпадать с ним (строка).
    Использовать перед вставкой в MongoDB для совместимости с бизнес-логикой.
    """
    if isinstance(doc, dict) and "id" in doc:
        doc["_id"] = doc["id"]
    return doc 