#!/usr/bin/env python3
"""
Система миграций для Universal Agent Platform.
Принцип: Автоматическое создание и обновление структуры БД.
"""

import asyncio
from typing import Dict, List, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from loguru import logger

from app.config.database import DB_CONFIG


class DatabaseMigration:
    """Базовый класс для миграций."""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.applied_at: datetime = None
    
    async def up(self, db: AsyncIOMotorDatabase) -> bool:
        """Применяет миграцию."""
        raise NotImplementedError
    
    async def down(self, db: AsyncIOMotorDatabase) -> bool:
        """Откатывает миграцию."""
        raise NotImplementedError


class InitialMigration(DatabaseMigration):
    """Начальная миграция - создание базовой структуры."""
    
    def __init__(self):
        super().__init__("001", "Создание базовой структуры БД")
    
    async def up(self, db: AsyncIOMotorDatabase) -> bool:
        """Создаёт коллекции и индексы."""
        try:
            logger.info("🔧 Создание коллекций...")
            
            # Создаём коллекции
            collections = ["scenarios", "users", "executions", "migrations", "channel_mappings"]
            for collection_name in collections:
                if collection_name not in await db.list_collection_names():
                    await db.create_collection(collection_name)
                    logger.info(f"✅ Коллекция {collection_name} создана")
            
            # Создаём только необходимые индексы
            logger.info("🔧 Создание базовых индексов...")
            
            # Индексы для маппингов каналов
            channel_mappings = db.channel_mappings
            await channel_mappings.create_index("channel_id", unique=True)
            
            # Индексы для сценариев - только уникальные поля  
            scenarios = db.scenarios
            await scenarios.create_index("scenario_id", unique=True)
            
            # Индексы для пользователей - только уникальные
            users = db.users
            await users.create_index([("user_id", 1), ("channel_type", 1)], unique=True)
            
            # Индексы для выполнений - минимальные
            executions = db.executions
            await executions.create_index("channel_id")
            await executions.create_index("scenario_id")
            
            # Индексы для миграций
            migrations = db.migrations
            await migrations.create_index("version", unique=True)
            
            logger.info("✅ Базовая структура БД создана")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания структуры БД: {e}")
            return False
    
    async def down(self, db: AsyncIOMotorDatabase) -> bool:
        """Удаляет созданную структуру."""
        try:
            collections = ["scenarios", "users", "executions", "channel_mappings"]
            for collection_name in collections:
                await db.drop_collection(collection_name)
                logger.info(f"🗑️ Коллекция {collection_name} удалена")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка удаления структуры БД: {e}")
            return False


class MigrationManager:
    """Менеджер миграций."""
    
    def __init__(self):
        self.migrations: List[DatabaseMigration] = [
            InitialMigration(),
        ]
        self.client: AsyncIOMotorClient = None
        self.db: AsyncIOMotorDatabase = None
    
    async def connect(self) -> bool:
        """Подключается к БД."""
        try:
            connection_string = DB_CONFIG.get_connection_string()
            self.client = AsyncIOMotorClient(connection_string)
            self.db = self.client[DB_CONFIG.database_name]
            
            # Проверяем подключение
            await self.client.admin.command('ismaster')
            logger.info(f"✅ Подключение к БД установлено: {DB_CONFIG.database_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к БД: {e}")
            return False
    
    async def disconnect(self):
        """Отключается от БД."""
        if self.client:
            self.client.close()
            logger.info("🔌 Подключение к БД закрыто")
    
    async def get_applied_migrations(self) -> List[str]:
        """Получает список применённых миграций."""
        try:
            if "migrations" not in await self.db.list_collection_names():
                return []
            
            cursor = self.db.migrations.find({}, {"version": 1})
            applied = []
            async for doc in cursor:
                applied.append(doc["version"])
            
            return applied
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения миграций: {e}")
            return []
    
    async def apply_migration(self, migration: DatabaseMigration) -> bool:
        """Применяет миграцию."""
        try:
            logger.info(f"🔧 Применение миграции {migration.version}: {migration.description}")
            
            # Применяем миграцию
            success = await migration.up(self.db)
            
            if success:
                # Записываем в БД
                await self.db.migrations.insert_one({
                    "version": migration.version,
                    "description": migration.description,
                    "applied_at": datetime.utcnow()
                })
                
                logger.info(f"✅ Миграция {migration.version} применена")
                return True
            else:
                logger.error(f"❌ Миграция {migration.version} не применена")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка применения миграции {migration.version}: {e}")
            return False
    
    async def migrate(self) -> bool:
        """Применяет все необходимые миграции."""
        try:
            if not await self.connect():
                return False
            
            applied_migrations = await self.get_applied_migrations()
            logger.info(f"📋 Применённые миграции: {applied_migrations}")
            
            success_count = 0
            for migration in self.migrations:
                if migration.version not in applied_migrations:
                    if await self.apply_migration(migration):
                        success_count += 1
                    else:
                        logger.error(f"❌ Не удалось применить миграцию {migration.version}")
                        break
                else:
                    logger.info(f"⏭️ Миграция {migration.version} уже применена")
            
            logger.info(f"✅ Применено {success_count} новых миграций")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения миграций: {e}")
            return False
        finally:
            await self.disconnect()
    
    async def status(self) -> Dict[str, Any]:
        """Возвращает статус миграций."""
        try:
            if not await self.connect():
                return {"error": "Не удалось подключиться к БД"}
            
            applied_migrations = await self.get_applied_migrations()
            
            status = {
                "database": DB_CONFIG.database_name,
                "total_migrations": len(self.migrations),
                "applied_migrations": len(applied_migrations),
                "pending_migrations": [],
                "applied_list": applied_migrations
            }
            
            for migration in self.migrations:
                if migration.version not in applied_migrations:
                    status["pending_migrations"].append({
                        "version": migration.version,
                        "description": migration.description
                    })
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса миграций: {e}")
            return {"error": str(e)}
        finally:
            await self.disconnect()


# Глобальный менеджер миграций
migration_manager = MigrationManager()


async def ensure_database_ready() -> bool:
    """Гарантирует готовность БД к работе."""
    logger.info("🔧 Проверка готовности БД...")
    return await migration_manager.migrate()


if __name__ == "__main__":
    # Запуск миграций из командной строки
    asyncio.run(ensure_database_ready()) 