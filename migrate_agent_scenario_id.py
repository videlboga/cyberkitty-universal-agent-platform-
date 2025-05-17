#!/usr/bin/env python3
import argparse
import logging
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError
import os

# Настройка логирования
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "migration_agent_scenario_id.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("agent_scenario_id_migration")
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(console_handler)

DEFAULT_MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/universal_agent")
DEFAULT_DB_NAME = DEFAULT_MONGO_URI.split("/")[-1] # Пытаемся извлечь имя БД из URI

def migrate_agents(db, dry_run=False):
    agents_collection = db["agents"]
    updated_count = 0
    processed_count = 0
    errors_count = 0
    
    operations = []

    logger.info(f"Начало миграции агентов. Dry-run: {dry_run}")

    try:
        for agent_doc in agents_collection.find({}):
            processed_count += 1
            agent_id = agent_doc.get("_id")
            config = agent_doc.get("config")
            current_top_level_scenario_id = agent_doc.get("scenario_id")

            if isinstance(config, dict) and "scenario_id" in config:
                scenario_id_in_config = config.get("scenario_id")
                
                if scenario_id_in_config is not None:
                    # Определяем, нужно ли обновление
                    needs_update = False
                    update_set = {}
                    update_unset = {}

                    if current_top_level_scenario_id != scenario_id_in_config:
                        update_set["scenario_id"] = scenario_id_in_config
                        needs_update = True
                    
                    # Удаляем scenario_id из config в любом случае, если он там есть
                    update_unset["config.scenario_id"] = ""
                    needs_update = True # Даже если scenario_id уже был на верхнем уровне, конфиг надо почистить

                    if needs_update:
                        op_parts = []
                        if update_set:
                            op_parts.append(f"SET scenario_id='{scenario_id_in_config}'")
                        if update_unset:
                            op_parts.append("UNSET config.scenario_id")
                        
                        logger.info(f"Агент ID: {agent_id}. Обнаружен scenario_id='{scenario_id_in_config}' в config. Действия: {', '.join(op_parts)}.")
                        
                        if not dry_run:
                            mongo_update_op = {}
                            if update_set:
                                mongo_update_op["$set"] = update_set
                            if update_unset:
                                mongo_update_op["$unset"] = update_unset
                            
                            operations.append(UpdateOne({"_id": agent_id}, mongo_update_op))
                        updated_count +=1 # Считаем как "кандидат на обновление" в dry-run
                    else:
                        logger.info(f"Агент ID: {agent_id}. scenario_id='{scenario_id_in_config}' уже на верхнем уровне и совпадает. Только чистка config.scenario_id.")
                        # Если только чистка config.scenario_id
                        if not dry_run:
                             operations.append(UpdateOne({"_id": agent_id}, {"$unset": {"config.scenario_id": ""}}))
                        updated_count +=1


                else: # scenario_id_in_config is None
                    logger.info(f"Агент ID: {agent_id}. scenario_id в config имеет значение None. Удаляем config.scenario_id.")
                    if not dry_run:
                        operations.append(UpdateOne({"_id": agent_id}, {"$unset": {"config.scenario_id": ""}}))
                    updated_count +=1
            
            elif current_top_level_scenario_id is not None:
                 logger.debug(f"Агент ID: {agent_id}. scenario_id уже на верхнем уровне ('{current_top_level_scenario_id}'), в config нет scenario_id. Пропускаем.")
            else:
                logger.debug(f"Агент ID: {agent_id}. Нет scenario_id ни в config, ни на верхнем уровне. Пропускаем.")

        if not dry_run and operations:
            logger.info(f"Выполнение {len(operations)} операций обновления...")
            result = agents_collection.bulk_write(operations)
            actual_updated_count = result.modified_count
            logger.info(f"Bulk write выполнен. Модифицировано документов: {actual_updated_count}")
            # В dry-run updated_count это количество запланированных, не фактически обновленных
            # После реального выполнения, updated_count лучше взять из result
            updated_count = actual_updated_count 
        elif dry_run:
             logger.info(f"Dry-run: {updated_count} агентов были бы обновлены.")


    except PyMongoError as e:
        logger.error(f"Ошибка MongoDB во время миграции: {e}")
        errors_count += 1 # Считаем общую ошибку, если цикл прервался
    except Exception as e:
        logger.error(f"Неожиданная ошибка во время миграции: {e}", exc_info=True)
        errors_count +=1

    logger.info(f"Миграция завершена. Всего обработано: {processed_count}. Обновлено/запланировано к обновлению: {updated_count}. Ошибок: {errors_count}.")
    return updated_count, errors_count

def main():
    parser = argparse.ArgumentParser(description="Миграция поля scenario_id для агентов из config в поле верхнего уровня.")
    parser.add_argument("--uri", default=DEFAULT_MONGO_URI, help=f"MongoDB URI (default: {DEFAULT_MONGO_URI})")
    parser.add_argument("--db", default=None, help="Имя базы данных (если не указано, будет извлечено из URI)")
    parser.add_argument("--dry-run", action="store_true", help="Запустить в режиме dry-run без реальных изменений в БД.")
    
    args = parser.parse_args()

    db_name = args.db
    if not db_name:
        try:
            # Пытаемся извлечь имя БД из URI, если оно там есть
            path_part = args.uri.split("//", 1)[-1].split("/", 1)[-1]
            if '?' in path_part: # Убираем параметры запроса
                path_part = path_part.split('?')[0]
            if path_part and path_part != args.uri: # Если что-то удалось извлечь и это не весь URI
                 db_name = path_part
            else: # Если не удалось извлечь, используем запасное имя
                db_name = "universal_agent" # Или другое имя по умолчанию
                logger.warning(f"Не удалось извлечь имя БД из URI '{args.uri}'. Используется '{db_name}'. Укажите --db явно, если это неверно.")
        except Exception:
            db_name = "universal_agent" # Фоллбек
            logger.warning(f"Ошибка при извлечении имени БД из URI '{args.uri}'. Используется '{db_name}'. Укажите --db явно, если это неверно.")


    logger.info(f"Подключение к MongoDB: {args.uri}, База данных: {db_name}")

    try:
        client = MongoClient(args.uri)
        db = client[db_name]
        
        # Проверка соединения
        client.admin.command('ping') 
        logger.info("Успешное подключение к MongoDB.")

    except PyMongoError as e:
        logger.error(f"Не удалось подключиться к MongoDB: {e}")
        return
    except Exception as e:
        logger.error(f"Не удалось инициализировать MongoDB клиент: {e}")
        return

    updated_count, errors_count = migrate_agents(db, args.dry_run)

    if errors_count > 0:
        logger.error("Миграция завершилась с ошибками.")
    elif not args.dry_run:
        logger.info(f"Миграция успешно завершена. Обновлено документов: {updated_count}.")
    else:
        logger.info(f"Dry-run миграции успешно завершен. {updated_count} документов были бы обновлены.")

if __name__ == "__main__":
    main() 