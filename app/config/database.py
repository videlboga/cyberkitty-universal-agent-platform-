#!/usr/bin/env python3
"""
Централизованная конфигурация базы данных для Universal Agent Platform.
Принцип: Одна точка истины для всех настроек БД.
"""

import os
from typing import Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class DatabaseConfig:
    """Конфигурация базы данных."""
    uri: str
    database_name: str
    connection_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Создаёт конфигурацию из переменных окружения."""
        
        # Приоритет переменных окружения
        uri = (
            os.getenv("MONGODB_URI") or 
            os.getenv("MONGO_URI") or 
            os.getenv("MONGODB_URL") or 
            "mongodb://mongo:27017/"
        )
        
        database_name = (
            os.getenv("MONGODB_DATABASE_NAME") or
            os.getenv("MONGODB_DATABASE") or
            os.getenv("MONGO_DATABASE") or
            "universal_agent_platform"
        )
        
        # Дополнительные параметры
        connection_timeout = int(os.getenv("MONGODB_TIMEOUT", "30"))
        retry_attempts = int(os.getenv("MONGODB_RETRY_ATTEMPTS", "3"))
        retry_delay = int(os.getenv("MONGODB_RETRY_DELAY", "5"))
        
        config = cls(
            uri=uri,
            database_name=database_name,
            connection_timeout=connection_timeout,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay
        )
        
        logger.info(f"📊 Database config: {config.uri} -> {config.database_name}")
        return config
    
    def get_connection_string(self) -> str:
        """Возвращает полную строку подключения."""
        if "?" in self.uri:
            return f"{self.uri}&connectTimeoutMS={self.connection_timeout * 1000}"
        else:
            return f"{self.uri}?connectTimeoutMS={self.connection_timeout * 1000}"


# Глобальная конфигурация
DB_CONFIG = DatabaseConfig.from_env() 