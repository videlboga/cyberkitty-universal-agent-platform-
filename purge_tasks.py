import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def check_mongodb_connection(uri):
    """Проверяет подключение к MongoDB"""
    print(f"Попытка подключения к {uri}...")
    try:
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        db_name = client.get_default_database().name
        print(f"Успешное подключение к MongoDB: {uri}")
        return client, db_name
    except Exception as e:
        print(f"Ошибка подключения к MongoDB {uri}: {e}")
        return None, None

async def purge_tasks_collection():
    """Полностью очищает коллекцию задач (выжигает огнём 'now')"""
    print("ЗАПУСК ОЧИСТКИ БАЗЫ ДАННЫХ! Удаление всех задач...")
    
    # Пробуем различные варианты подключения к MongoDB
    mongodb_uris = [
        os.getenv("MONGO_URI", "mongodb://mongo:27017/agent_platform"),
        "mongodb://mongo:27017/agent_platform",
        "mongodb://localhost:27017/agent_platform"
    ]
    
    client = None
    db_name = None
    
    # Пробуем подключиться к MongoDB с разными URI
    for uri in mongodb_uris:
        client, db_name = await check_mongodb_connection(uri)
        if client:
            break
    
    if not client:
        print("Не удалось подключиться к MongoDB. Проверьте настройки подключения.")
        return
    
    db = client[db_name]
    
    # Список коллекций для очистки
    collections_to_purge = [
        "scheduled_tasks",
        "tasks",
        "scheduler_tasks"
    ]
    
    for collection_name in collections_to_purge:
        if collection_name in await db.list_collection_names():
            collection = db[collection_name]
            
            # Получаем количество документов перед удалением
            count_before = await collection.count_documents({})
            print(f"Коллекция {collection_name}: найдено {count_before} документов")
            
            # Удаляем все документы
            if count_before > 0:
                result = await collection.delete_many({})
                print(f"Коллекция {collection_name}: удалено {result.deleted_count} документов")
            else:
                print(f"Коллекция {collection_name} уже пуста")
    
    print("ОЧИСТКА ЗАВЕРШЕНА! Все задачи удалены из базы данных.")

# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(purge_tasks_collection()) 