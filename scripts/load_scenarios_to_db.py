import os
import json
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure, OperationFailure

# Изменяем получение переменных, чтобы они были обязательными
MONGODB_URI = os.getenv("MONGO_URI") 
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME")

if not MONGODB_URI:
    raise ValueError("Переменная окружения MONGO_URI не установлена.")
if not MONGODB_DATABASE_NAME:
    raise ValueError("Переменная окружения MONGODB_DATABASE_NAME не установлена.")

SCENARIOS_COLLECTION_NAME = "scenarios"
# SCENARIOS_DIR = "scenarios" # Старая версия
SCENARIOS_DIRS = ["scenarios", "scenarios/unit_tests"] # Новый список директорий

def get_mongo_client():
    """Создает и возвращает клиент MongoDB."""
    try:
        client = MongoClient(MONGODB_URI)
        # Проверка соединения
        client.admin.command('ping')
        print(f"Успешное подключение к MongoDB: {MONGODB_URI}")
        return client
    except ConnectionFailure as e:
        print(f"Ошибка подключения к MongoDB: {e}")
        return None

def load_scenarios():
    """Загружает или обновляет сценарии из JSON файлов в MongoDB."""
    client = get_mongo_client()
    if not client:
        return

    db = client[MONGODB_DATABASE_NAME]
    collection = db[SCENARIOS_COLLECTION_NAME]
    
    # if not os.path.exists(SCENARIOS_DIR) or not os.path.isdir(SCENARIOS_DIR): # Старая проверка
    #     print(f"Директория сценариев '{SCENARIOS_DIR}' не найдена.")
    #     return

    all_json_files_with_paths = []
    for s_dir in SCENARIOS_DIRS:
        if not os.path.exists(s_dir) or not os.path.isdir(s_dir):
            print(f"Предупреждение: Директория сценариев '{s_dir}' не найдена или не является директорией. Пропуск.")
            continue
        
        json_files_in_dir = [os.path.join(s_dir, f) for f in os.listdir(s_dir) if f.endswith('.json')]
        if not json_files_in_dir:
            print(f"В директории '{s_dir}' не найдено JSON файлов сценариев.")
        else:
            all_json_files_with_paths.extend(json_files_in_dir)
            print(f"Найдено {len(json_files_in_dir)} JSON файлов в '{s_dir}'.")

    # json_files = [f for f in os.listdir(SCENARIOS_DIR) if f.endswith('.json')] # Старая версия
    if not all_json_files_with_paths: # Новая проверка
        print(f"Не найдено JSON файлов сценариев ни в одной из указанных директорий: {SCENARIOS_DIRS}.")
        return

    operations = []
    loaded_count = 0
    updated_count = 0
    error_count = 0

    # for file_name in json_files: # Старая версия
    #     file_path = os.path.join(SCENARIOS_DIR, file_name)
    for file_path in all_json_files_with_paths: # Новая версия, используем полный путь
        file_name = os.path.basename(file_path) # Получаем только имя файла для логов
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                scenario_data = json.load(f)
            
            if "scenario_id" not in scenario_data:
                print(f"Ошибка: отсутствует 'scenario_id' в файле {file_name}. Пропуск.")
                error_count += 1
                continue
            
            # Используем upsert=True для обновления существующего или вставки нового
            operations.append(
                UpdateOne({"scenario_id": scenario_data["scenario_id"]},
                          {"$set": scenario_data},
                          upsert=True)
            )
            print(f"Подготовлен сценарий '{scenario_data['scenario_id']}' из файла {file_name} для загрузки/обновления.")

        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON в файле {file_name}: {e}. Пропуск.")
            error_count += 1
        except Exception as e:
            print(f"Непредвиденная ошибка при обработке файла {file_name}: {e}. Пропуск.")
            error_count += 1

    if operations:
        try:
            result = collection.bulk_write(operations)
            loaded_count = result.upserted_count + result.inserted_count # inserted_count для старых версий pymongo
            updated_count = result.modified_count
            print(f"\nЗагрузка завершена.")
            print(f"  Новых сценариев загружено: {loaded_count}")
            print(f"  Существующих сценариев обновлено: {updated_count}")
            if error_count > 0:
                print(f"  Ошибок при обработке файлов: {error_count}")
        except OperationFailure as e:
            print(f"Ошибка при массовой записи в MongoDB: {e}")
        except Exception as e:
            print(f"Непредвиденная ошибка при массовой записи: {e}")
    else:
        print("Нет сценариев для загрузки/обновления.")

    client.close()

if __name__ == "__main__":
    print("Запуск скрипта загрузки сценариев в MongoDB...")
    load_scenarios() 