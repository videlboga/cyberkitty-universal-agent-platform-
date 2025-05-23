from bson import ObjectId, errors
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Optional, Union, Dict, Any, List
from fastapi import HTTPException
from loguru import logger
import pymongo
import json
import os

# Настройка логирования - УДАЛЯЕМ ЭТУ СТРОКУ
# os.makedirs("logs", exist_ok=True)
# logger.add("logs/id_helper_debug.log", format="{time} {level} {message}", level="DEBUG", rotation="1 MB", compression="zip", serialize=False)

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

def ensure_mongo_id(doc):
    """
    Гарантирует, что если в документе есть поле id, то _id будет совпадать с ним (строка).
    Использовать перед вставкой в MongoDB для совместимости с бизнес-логикой.
    """
    if isinstance(doc, dict) and "id" in doc:
        doc["_id"] = doc["id"]
    return doc 

def build_id_query(id_value: str, target_field_name: Optional[str] = None, collection_name_for_guess: Optional[str] = None) -> Dict[str, Any]:
    """
    Строит словарь-запрос MongoDB для поиска по ID.
    Либо по ObjectId (_id), либо по кастомному строковому полю (target_field_name),
    либо по обоим через $or.
    Если target_field_name не указан, пытается угадать его на основе collection_name_for_guess.
    """
    logger.debug(f"build_id_query: начало. id_value='{id_value}', target_field_name='{target_field_name}', collection_name_for_guess='{collection_name_for_guess}'")
    
    query: Dict[str, Any] = {}
    actual_target_field = target_field_name

    if not actual_target_field and collection_name_for_guess:
        logger.warning(f"build_id_query: target_field_name не указан, угадываем по collection_name_for_guess='{collection_name_for_guess}'")
        if collection_name_for_guess == "agents":
            actual_target_field = "agent_id"
        elif collection_name_for_guess == "scenarios":
            actual_target_field = "scenario_id"
        # Добавьте другие коллекции, если необходимо
        if actual_target_field:
            logger.debug(f"build_id_query: Угадано поле '{actual_target_field}' для коллекции '{collection_name_for_guess}'")
        else:
            logger.warning(f"build_id_query: Не удалось угадать target_field_name для коллекции '{collection_name_for_guess}'")

    obj_id = to_object_id(id_value)

    if obj_id and actual_target_field:
        # Ищем по ObjectId ИЛИ по кастомному строковому полю
        query = {"$or": [{actual_target_field: id_value}, {"_id": obj_id}]}
        logger.debug(f"build_id_query: (obj_id ЕСТЬ, actual_target_field='{actual_target_field}') Запрос: {query}")
    elif obj_id:
        # Ищем только по ObjectId
        query = {"_id": obj_id}
        logger.debug(f"build_id_query: (obj_id ЕСТЬ, actual_target_field НЕТ) Запрос: {query}")
    elif actual_target_field:
        # id_value не ObjectId, ищем только по кастомному строковому полю
        query = {actual_target_field: id_value}
        logger.debug(f"build_id_query: (obj_id НЕТ, actual_target_field='{actual_target_field}') Запрос: {query}")
    else:
        # Не можем построить осмысленный запрос, если нет ни ObjectId, ни target_field_name
        # Однако, некоторые могут захотеть искать по строковому _id напрямую.
        # Для безопасности и предсказуемости, если нет явного поля и id_value не ObjectId,
        # вернем запрос, который, скорее всего, ничего не найдет, или можно выбросить ошибку.
        # Пока что, если id_value - строка, попробуем поискать по _id: id_value.
        # Это может быть полезно, если _id хранятся как строки (не рекомендуется).
        logger.warning(f"build_id_query: id_value='{id_value}' не является ObjectId и target_field_name не указан/не угадан. Попытка поиска по _id: '{id_value}'.")
        query = {"_id": id_value} # Может не сработать, если _id должны быть ObjectId

    logger.debug(f"build_id_query: финальный запрос: {query}")
    return query

async def find_one_by_id_flexible(
    id_value: str, 
    collection: AsyncIOMotorCollection, 
    target_field_name: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Ищет один документ в коллекции по ID (ObjectId или кастомное строковое поле).
    Использует build_id_query для построения запроса.
    """
    logger.debug(f"find_one_by_id_flexible: начало. id_value='{id_value}', collection_name='{collection.name}', target_field_name='{target_field_name}'")
    
    # Определяем имя коллекции для возможного угадывания поля в build_id_query, если target_field_name не задан
    collection_name_for_guess = collection.name if not target_field_name else None
    
    query = build_id_query(id_value, target_field_name, collection_name_for_guess)
    logger.critical(f"[find_one_by_id_flexible CRITICAL] Сформирован запрос: {json.dumps(query, default=str)}")
    
    if not query: # Если build_id_query вернул пустой dict, это ошибка
        logger.error(f"find_one_by_id_flexible: build_id_query вернул пустой запрос для id_value='{id_value}', target_field_name='{target_field_name}'")
        return None
        
    try:
        result_doc = await collection.find_one(query)
        if result_doc:
            logger.critical(f"[find_one_by_id_flexible CRITICAL] Результат find_one: {json.dumps(result_doc, indent=2, default=str)}")
        else:
            logger.critical(f"[find_one_by_id_flexible CRITICAL] Результат find_one: Документ НЕ НАЙДЕН по запросу {json.dumps(query, default=str)}")
        return result_doc
    except pymongo.errors.PyMongoError as e:
        logger.critical(f"[find_one_by_id_flexible CRITICAL] Ошибка MongoDB при выполнении find_one с запросом {json.dumps(query, default=str)}: {e}")
        return None
    except Exception as e:
        logger.critical(f"[find_one_by_id_flexible CRITICAL] Непредвиденная ошибка при выполнении find_one с запросом {json.dumps(query, default=str)}: {e}")
        return None

# Старая функция handle_id_query больше не нужна в таком виде, так как ее логика разделена
# между build_id_query и find_one_by_id_flexible.
# Если где-то остался старый вызов, он должен быть заменен.

# async def handle_id_query(id_value: str, collection: AsyncIOMotorCollection, target_field_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
#    # ... (старый код, который был здесь, теперь не нужен)
#    pass # Удаляем старую реализацию или комментируем 