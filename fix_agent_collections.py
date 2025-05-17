#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fix_agent_collections.py - Скрипт для проверки и исправления связи между агентами и коллекциями в MongoDB

Этот скрипт позволяет:
1. Проверять связь агентов с коллекциями
2. Исправлять связь, удаляя отсутствующие коллекции или добавляя новые
3. Создавать отсутствующие коллекции
4. Настраивать связь агентов с коллекциями на основе типов агентов

Примеры использования:
- Проверить связь агента с коллекциями:
  python fix_agent_collections.py check agent123

- Исправить связь агента с коллекциями:
  python fix_agent_collections.py fix agent123 --add collection1 collection2 --remove collection3

- Создать отсутствующие коллекции для агента:
  python fix_agent_collections.py fix agent123 --create

- Исправить связь всех агентов с коллекциями:
  python fix_agent_collections.py fix-all

- Исправить связь агента с коллекциями на основе его типа:
  python fix_agent_collections.py fix-by-type agent123 --create

- Исправить связь всех агентов с коллекциями на основе их типов:
  python fix_agent_collections.py fix-all-by-type --create

- Создать новую коллекцию:
  python fix_agent_collections.py create-collection my_collection --type user_data

- Создать отсутствующие коллекции для агента:
  python fix_agent_collections.py create-missing agent123

- Вывести список агентов и коллекций:
  python fix_agent_collections.py list

- Вывести рекомендуемые коллекции для типа агента:
  python fix_agent_collections.py list-recommended expert
"""

import os
import sys
import json
import logging
import argparse
import requests
from typing import Dict, Any, List, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/fix_agent_collections.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("fix_agent_collections")

# Добавляем вывод логов в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter("%(levelname)s: %(message)s")
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# Конфигурация API и MongoDB
API_BASE_URL = "http://localhost:8000"
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "agent_platform"
MAX_RETRIES = 3

class AgentCollectionFixer:
    """
    Класс для проверки и исправления связи между агентами и коллекциями в MongoDB
    """
    
    def __init__(self, mongo_uri: str = MONGO_URI, db_name: str = DB_NAME, api_base_url: str = API_BASE_URL):
        """
        Инициализация с параметрами подключения
        
        Args:
            mongo_uri: URI для подключения к MongoDB
            db_name: Имя базы данных
            api_base_url: Базовый URL API
        """
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.api_base_url = api_base_url
        self.client = None
        self.db = None
        
    async def connect(self):
        """Подключение к MongoDB"""
        try:
            logger.info(f"Подключение к MongoDB: {self.mongo_uri}")
            self.client = AsyncIOMotorClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            # Проверка соединения
            await self.db.command("ping")
            logger.info("Подключение к MongoDB успешно установлено")
            return True
        except Exception as e:
            logger.error(f"Ошибка при подключении к MongoDB: {str(e)}")
            return False
    
    async def close(self):
        """Закрытие соединения с MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Соединение с MongoDB закрыто")
    
    async def get_all_agents(self) -> List[Dict[str, Any]]:
        """
        Получает список всех агентов из MongoDB
        
        Returns:
            List[Dict[str, Any]]: Список агентов
        """
        try:
            agents_collection = self.db["agents"]
            cursor = agents_collection.find({})
            agents = await cursor.to_list(length=100)
            logger.info(f"Получено {len(agents)} агентов из MongoDB")
            return agents
        except Exception as e:
            logger.error(f"Ошибка при получении агентов из MongoDB: {str(e)}")
            return []
    
    async def get_all_collections(self) -> List[Dict[str, Any]]:
        """
        Получает список всех коллекций из MongoDB (коллекции пользовательских данных)
        
        Returns:
            List[Dict[str, Any]]: Список коллекций
        """
        try:
            # Получаем список коллекций из специальной коллекции collections_metadata
            collections_metadata = self.db["collections_metadata"]
            cursor = collections_metadata.find({})
            collections = await cursor.to_list(length=100)
            logger.info(f"Получено {len(collections)} коллекций из MongoDB")
            return collections
        except Exception as e:
            logger.error(f"Ошибка при получении коллекций из MongoDB: {str(e)}")
            return []
    
    async def create_collection(self, collection_name: str, collection_type: str = "generic") -> bool:
        """
        Создает новую коллекцию и добавляет ее в метаданные
        
        Args:
            collection_name: Имя коллекции
            collection_type: Тип коллекции (generic, user_data, agent_data и т.д.)
            
        Returns:
            bool: True если коллекция успешно создана, иначе False
        """
        try:
            # Проверяем, существует ли уже коллекция
            if await self._check_collection_exists(collection_name):
                logger.info(f"Коллекция {collection_name} уже существует")
                return True
            
            # Создаем коллекцию в базе данных
            await self.db.create_collection(collection_name)
            logger.info(f"Коллекция {collection_name} создана в базе данных")
            
            # Добавляем информацию о коллекции в метаданные
            collections_metadata = self.db["collections_metadata"]
            metadata = {
                "name": collection_name,
                "type": collection_type,
                "created_at": datetime.now().isoformat(),
                "schema": {},  # Пустая схема по умолчанию
                "description": f"Автоматически созданная коллекция {collection_name}"
            }
            
            await collections_metadata.insert_one(metadata)
            logger.info(f"Метаданные коллекции {collection_name} добавлены")
            
            return True
        except Exception as e:
            logger.error(f"Ошибка при создании коллекции {collection_name}: {str(e)}")
            return False
    
    async def check_agent_collections(self, agent_id: str) -> Tuple[bool, List[str], List[str]]:
        """
        Проверяет корректность связи агента с коллекциями
        
        Args:
            agent_id: ID агента
            
        Returns:
            Tuple[bool, List[str], List[str]]: (валидна ли связь, список коллекций агента, список отсутствующих коллекций)
        """
        try:
            # Получаем данные агента
            agents_collection = self.db["agents"]
            agent = await agents_collection.find_one({"id": agent_id})
            
            if not agent:
                logger.warning(f"Агент {agent_id} не найден в базе данных")
                return False, [], []
            
            # Получаем список коллекций агента из конфигурации
            config = agent.get("config", {})
            if not isinstance(config, dict):
                logger.warning(f"Конфигурация агента {agent_id} не является словарем")
                return False, [], []
            
            collections = config.get("collections", [])
            if not isinstance(collections, list):
                logger.warning(f"Список коллекций агента {agent_id} не является массивом")
                return False, [], []
            
            # Проверяем существование каждой коллекции
            missing_collections = []
            for collection_name in collections:
                if not await self._check_collection_exists(collection_name):
                    missing_collections.append(collection_name)
            
            is_valid = len(missing_collections) == 0
            return is_valid, collections, missing_collections
            
        except Exception as e:
            logger.error(f"Ошибка при проверке коллекций агента {agent_id}: {str(e)}")
            return False, [], []
    
    async def _check_collection_exists(self, collection_name: str) -> bool:
        """
        Проверяет существование коллекции
        
        Args:
            collection_name: Имя коллекции
            
        Returns:
            bool: True если коллекция существует, иначе False
        """
        try:
            # Проверяем наличие коллекции в метаданных
            collections_metadata = self.db["collections_metadata"]
            collection_metadata = await collections_metadata.find_one({"name": collection_name})
            
            if collection_metadata:
                return True
            
            # Проверяем наличие коллекции в списке коллекций базы данных
            collection_names = await self.db.list_collection_names()
            return collection_name in collection_names
            
        except Exception as e:
            logger.error(f"Ошибка при проверке существования коллекции {collection_name}: {str(e)}")
            return False
    
    async def fix_agent_collections(self, agent_id: str, collections_to_add: List[str] = None, 
                                  collections_to_remove: List[str] = None, create_missing: bool = False) -> bool:
        """
        Исправляет связь агента с коллекциями
        
        Args:
            agent_id: ID агента
            collections_to_add: Список коллекций для добавления (опционально)
            collections_to_remove: Список коллекций для удаления (опционально)
            create_missing: Создавать отсутствующие коллекции (по умолчанию False)
            
        Returns:
            bool: True если исправление успешно, иначе False
        """
        try:
            # Получаем данные агента
            agents_collection = self.db["agents"]
            agent = await agents_collection.find_one({"id": agent_id})
            
            if not agent:
                logger.warning(f"Агент {agent_id} не найден в базе данных")
                return False
            
            # Получаем текущие коллекции агента
            config = agent.get("config", {})
            if not isinstance(config, dict):
                config = {}
            
            current_collections = config.get("collections", [])
            if not isinstance(current_collections, list):
                current_collections = []
            
            # Обновляем список коллекций
            updated_collections = current_collections.copy()
            
            # Добавляем новые коллекции
            if collections_to_add:
                for collection_name in collections_to_add:
                    # Если нужно создать отсутствующие коллекции
                    if create_missing and not await self._check_collection_exists(collection_name):
                        if await self.create_collection(collection_name):
                            logger.info(f"Создана новая коллекция {collection_name} для агента {agent_id}")
                        else:
                            logger.error(f"Не удалось создать коллекцию {collection_name}")
                            continue  # Пропускаем добавление, если не удалось создать
                    
                    if collection_name not in updated_collections:
                        updated_collections.append(collection_name)
                        logger.info(f"Добавлена коллекция {collection_name} для агента {agent_id}")
            
            # Удаляем коллекции
            if collections_to_remove:
                for collection_name in collections_to_remove:
                    if collection_name in updated_collections:
                        updated_collections.remove(collection_name)
                        logger.info(f"Удалена коллекция {collection_name} для агента {agent_id}")
            
            # Обновляем конфигурацию агента, если список коллекций изменился
            if updated_collections != current_collections:
                config["collections"] = updated_collections
                
                # Обновляем агента в базе данных
                result = await agents_collection.update_one(
                    {"id": agent_id},
                    {"$set": {"config": config}}
                )
                
                if result.modified_count > 0:
                    logger.info(f"Конфигурация агента {agent_id} успешно обновлена")
                    return True
                else:
                    logger.warning(f"Не удалось обновить конфигурацию агента {agent_id}")
                    return False
            else:
                logger.info(f"Список коллекций агента {agent_id} не изменился")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка при исправлении коллекций агента {agent_id}: {str(e)}")
            return False
    
    async def create_missing_collections(self, agent_id: str) -> Tuple[bool, List[str]]:
        """
        Создает отсутствующие коллекции для агента
        
        Args:
            agent_id: ID агента
            
        Returns:
            Tuple[bool, List[str]]: (успех операции, список созданных коллекций)
        """
        try:
            # Проверяем текущие коллекции агента
            is_valid, collections, missing_collections = await self.check_agent_collections(agent_id)
            
            if is_valid:
                logger.info(f"Агент {agent_id} не имеет отсутствующих коллекций")
                return True, []
            
            # Создаем отсутствующие коллекции
            created_collections = []
            for collection_name in missing_collections:
                if await self.create_collection(collection_name):
                    created_collections.append(collection_name)
                    logger.info(f"Создана отсутствующая коллекция {collection_name} для агента {agent_id}")
                else:
                    logger.error(f"Не удалось создать коллекцию {collection_name}")
            
            # Проверяем результат
            success = len(created_collections) == len(missing_collections)
            
            if success:
                logger.info(f"Все отсутствующие коллекции для агента {agent_id} успешно созданы")
            else:
                logger.warning(f"Не все отсутствующие коллекции для агента {agent_id} удалось создать")
            
            return success, created_collections
            
        except Exception as e:
            logger.error(f"Ошибка при создании отсутствующих коллекций для агента {agent_id}: {str(e)}")
            return False, []
    
    async def fix_all_agents_collections(self, create_missing: bool = False) -> Tuple[int, int]:
        """
        Исправляет связь всех агентов с коллекциями
        
        Args:
            create_missing: Создавать отсутствующие коллекции (по умолчанию False)
            
        Returns:
            Tuple[int, int]: (количество успешно исправленных агентов, общее количество агентов)
        """
        try:
            # Получаем список всех агентов
            agents = await self.get_all_agents()
            if not agents:
                logger.error("Не удалось получить список агентов")
                return 0, 0
            
            # Получаем список всех доступных коллекций
            all_collections = await self.get_all_collections()
            available_collections = [collection.get("name") for collection in all_collections if collection.get("name")]
            
            # Счетчики для статистики
            total_agents = len(agents)
            fixed_agents = 0
            
            # Обрабатываем каждого агента
            for agent in agents:
                agent_id = agent.get("id")
                agent_name = agent.get("name", "Без имени")
                
                if not agent_id:
                    logger.warning("Пропуск агента без ID")
                    continue
                
                logger.info(f"Проверка агента {agent_id} ({agent_name})...")
                
                # Проверяем текущие коллекции агента
                is_valid, current_collections, missing_collections = await self.check_agent_collections(agent_id)
                
                if not is_valid:
                    if create_missing:
                        # Создаем отсутствующие коллекции
                        success, created_collections = await self.create_missing_collections(agent_id)
                        if success:
                            logger.info(f"Для агента {agent_id} созданы отсутствующие коллекции: {created_collections}")
                            # После создания коллекций проверяем снова
                            is_valid, _, _ = await self.check_agent_collections(agent_id)
                            if is_valid:
                                fixed_agents += 1
                                continue
                    
                    # Если не нужно создавать коллекции или не удалось их создать,
                    # исправляем связь агента с коллекциями, удаляя отсутствующие коллекции
                    if await self.fix_agent_collections(agent_id, collections_to_remove=missing_collections):
                        fixed_agents += 1
                        logger.info(f"Агент {agent_id} исправлен: удалены отсутствующие коллекции {missing_collections}")
                    else:
                        logger.warning(f"Не удалось исправить агента {agent_id}")
            
            logger.info(f"Исправлено {fixed_agents} из {total_agents} агентов")
            return fixed_agents, total_agents
            
        except Exception as e:
            logger.error(f"Ошибка при исправлении всех агентов: {str(e)}")
            return 0, 0
    
    async def get_recommended_collections(self, agent_type: str) -> List[str]:
        """
        Возвращает стандартные коллекции (тип не учитывается)
        """
        return ["user_profiles", "dialog_history"]
    
    async def fix_agent_collections_by_type(self, agent_id: str, create_missing: bool = False) -> bool:
        """
        Исправляет связь агента с коллекциями (тип не учитывается)
        """
        try:
            agents_collection = self.db["agents"]
            agent = await agents_collection.find_one({"id": agent_id})
            if not agent:
                logger.warning(f"Агент {agent_id} не найден в базе данных")
                return False
            # Получаем рекомендуемые коллекции (без типа)
            recommended_collections = await self.get_recommended_collections(None)
            is_valid, current_collections, missing_collections = await self.check_agent_collections(agent_id)
            collections_to_add = [coll for coll in recommended_collections if coll not in current_collections]
            collections_to_remove = []
            success = await self.fix_agent_collections(
                agent_id, 
                collections_to_add=collections_to_add,
                collections_to_remove=collections_to_remove,
                create_missing=create_missing
            )
            if success:
                logger.info(f"Связь агента {agent_id} с коллекциями исправлена (тип не учитывается)")
            else:
                logger.warning(f"Не удалось исправить связь агента {agent_id} с коллекциями")
            return success
        except Exception as e:
            logger.error(f"Ошибка при исправлении коллекций агента {agent_id}: {str(e)}")
            return False
    
    async def fix_all_agents_collections_by_type(self, create_missing: bool = False) -> Tuple[int, int]:
        """
        Исправляет связь всех агентов с коллекциями (тип не учитывается)
        """
        try:
            agents = await self.get_all_agents()
            if not agents:
                logger.error("Не удалось получить список агентов")
                return 0, 0
            total_agents = len(agents)
            fixed_agents = 0
            for agent in agents:
                agent_id = agent.get("id")
                agent_name = agent.get("name", "Без имени")
                if not agent_id:
                    logger.warning("Пропуск агента без ID")
                    continue
                logger.info(f"Исправление связи агента {agent_id} ({agent_name}) с коллекциями...")
                if await self.fix_agent_collections_by_type(agent_id, create_missing):
                    fixed_agents += 1
                    logger.info(f"Агент {agent_id} успешно исправлен")
                else:
                    logger.warning(f"Не удалось исправить агента {agent_id}")
            logger.info(f"Исправлено {fixed_agents} из {total_agents} агентов")
            return fixed_agents, total_agents
        except Exception as e:
            logger.error(f"Ошибка при исправлении всех агентов: {str(e)}")
            return 0, 0

async def main_async():
    """Асинхронная основная функция"""
    parser = argparse.ArgumentParser(description="Исправление связи агентов с коллекциями")
    
    # Группа команд
    subparsers = parser.add_subparsers(dest="command", help="Команда")
    
    # Команда check для проверки агента
    check_parser = subparsers.add_parser("check", help="Проверить связь агента с коллекциями")
    check_parser.add_argument("agent_id", help="ID агента")
    
    # Команда fix для исправления агента
    fix_parser = subparsers.add_parser("fix", help="Исправить связь агента с коллекциями")
    fix_parser.add_argument("agent_id", help="ID агента")
    fix_parser.add_argument("--add", nargs="+", help="Коллекции для добавления")
    fix_parser.add_argument("--remove", nargs="+", help="Коллекции для удаления")
    fix_parser.add_argument("--create", action="store_true", help="Создавать отсутствующие коллекции")
    
    # Команда fix-all для исправления всех агентов
    fix_all_parser = subparsers.add_parser("fix-all", help="Исправить связь всех агентов с коллекциями")
    fix_all_parser.add_argument("--create", action="store_true", help="Создавать отсутствующие коллекции")
    
    # Команда fix-by-type для исправления агента по типу
    fix_type_parser = subparsers.add_parser("fix-by-type", help="Исправить связь агента с коллекциями на основе его типа")
    fix_type_parser.add_argument("agent_id", help="ID агента")
    fix_type_parser.add_argument("--create", action="store_true", help="Создавать отсутствующие коллекции")
    
    # Команда fix-all-by-type для исправления всех агентов по типам
    fix_all_type_parser = subparsers.add_parser("fix-all-by-type", help="Исправить связь всех агентов с коллекциями на основе их типов")
    fix_all_type_parser.add_argument("--create", action="store_true", help="Создавать отсутствующие коллекции")
    
    # Команда create-collection для создания новой коллекции
    create_parser = subparsers.add_parser("create-collection", help="Создать новую коллекцию")
    create_parser.add_argument("collection_name", help="Имя коллекции")
    create_parser.add_argument("--type", default="generic", help="Тип коллекции (по умолчанию: generic)")
    
    # Команда create-missing для создания отсутствующих коллекций агента
    create_missing_parser = subparsers.add_parser("create-missing", help="Создать отсутствующие коллекции агента")
    create_missing_parser.add_argument("agent_id", help="ID агента")
    
    # Команда list для просмотра агентов и коллекций
    list_parser = subparsers.add_parser("list", help="Вывести список агентов и коллекций")
    list_parser.add_argument("--agents", action="store_true", help="Вывести только агентов")
    list_parser.add_argument("--collections", action="store_true", help="Вывести только коллекции")
    
    # Команда list-recommended для просмотра рекомендуемых коллекций для типа агента
    list_recommended_parser = subparsers.add_parser("list-recommended", help="Вывести рекомендуемые коллекции для типа агента")
    list_recommended_parser.add_argument("agent_type", help="Тип агента")
    
    # Парсим аргументы
    args = parser.parse_args()
    
    # Создаем экземпляр класса
    fixer = AgentCollectionFixer()
    
    # Подключаемся к MongoDB
    if not await fixer.connect():
        logger.error("Не удалось подключиться к MongoDB")
        return 1
    
    try:
        # Обрабатываем команды
        if args.command == "check":
            # Проверяем связь агента с коллекциями
            is_valid, collections, missing_collections = await fixer.check_agent_collections(args.agent_id)
            
            if is_valid:
                print(f"Агент {args.agent_id} имеет корректную связь с коллекциями:")
                for collection in collections:
                    print(f"  - {collection}")
            else:
                print(f"Агент {args.agent_id} имеет некорректную связь с коллекциями")
                print("Текущие коллекции:")
                for collection in collections:
                    if collection not in missing_collections:
                        print(f"  - {collection}")
                
                if missing_collections:
                    print("Отсутствующие коллекции:")
                    for collection in missing_collections:
                        print(f"  - {collection}")
            
            return 0 if is_valid else 1
            
        elif args.command == "fix":
            # Исправляем связь агента с коллекциями
            success = await fixer.fix_agent_collections(
                args.agent_id, 
                args.add, 
                args.remove, 
                create_missing=args.create
            )
            
            if success:
                print(f"Агент {args.agent_id} успешно исправлен")
            else:
                print(f"Не удалось исправить агента {args.agent_id}")
            
            return 0 if success else 1
            
        elif args.command == "fix-all":
            # Исправляем связь всех агентов с коллекциями
            fixed, total = await fixer.fix_all_agents_collections(create_missing=args.create)
            
            print(f"Исправлено {fixed} из {total} агентов")
            return 0 if fixed > 0 or total == 0 else 1
            
        elif args.command == "fix-by-type":
            # Исправляем связь агента с коллекциями на основе его типа
            success = await fixer.fix_agent_collections_by_type(args.agent_id, create_missing=args.create)
            
            if success:
                print(f"Агент {args.agent_id} успешно исправлен на основе его типа")
            else:
                print(f"Не удалось исправить агента {args.agent_id} на основе его типа")
            
            return 0 if success else 1
            
        elif args.command == "fix-all-by-type":
            # Исправляем связь всех агентов с коллекциями на основе их типов
            fixed, total = await fixer.fix_all_agents_collections_by_type(create_missing=args.create)
            
            print(f"Исправлено {fixed} из {total} агентов на основе их типов")
            return 0 if fixed > 0 or total == 0 else 1
            
        elif args.command == "create-collection":
            # Создаем новую коллекцию
            success = await fixer.create_collection(args.collection_name, args.type)
            
            if success:
                print(f"Коллекция {args.collection_name} успешно создана")
            else:
                print(f"Не удалось создать коллекцию {args.collection_name}")
            
            return 0 if success else 1
            
        elif args.command == "create-missing":
            # Создаем отсутствующие коллекции агента
            success, created_collections = await fixer.create_missing_collections(args.agent_id)
            
            if success:
                if created_collections:
                    print(f"Для агента {args.agent_id} созданы следующие коллекции:")
                    for collection in created_collections:
                        print(f"  - {collection}")
                else:
                    print(f"Агент {args.agent_id} не имеет отсутствующих коллекций")
            else:
                print(f"Не удалось создать все отсутствующие коллекции для агента {args.agent_id}")
            
            return 0 if success else 1
            
        elif args.command == "list-recommended":
            # Выводим рекомендуемые коллекции для типа агента
            collections = await fixer.get_recommended_collections(args.agent_type)
            
            print(f"Рекомендуемые коллекции для агента типа '{args.agent_type}':")
            for collection in collections:
                print(f"  - {collection}")
            
            return 0
            
        elif args.command == "list":
            # Выводим список агентов и коллекций
            if args.agents or not (args.agents or args.collections):
                agents = await fixer.get_all_agents()
                print("\n=== Агенты ===")
                for agent in agents:
                    agent_id = agent.get("id", "unknown")
                    agent_name = agent.get("name", "Без имени")
                    config = agent.get("config", {})
                    collections = config.get("collections", []) if isinstance(config, dict) else []
                    collections_str = ", ".join(collections) if collections else "нет"
                    print(f"ID: {agent_id}, Коллекции: {collections_str}")
            
            if args.collections or not (args.agents or args.collections):
                collections = await fixer.get_all_collections()
                print("\n=== Коллекции ===")
                for collection in collections:
                    collection_name = collection.get("name", "unknown")
                    print(f"Имя: {collection_name}")
            
            return 0
        else:
            # Если команда не указана, выводим справку
            parser.print_help()
            return 1
    
    finally:
        # Закрываем соединение с MongoDB
        await fixer.close()

def main():
    """Основная функция скрипта"""
    try:
        return asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Операция прервана пользователем")
        return 1
    except Exception as e:
        logger.error(f"Необработанное исключение: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 