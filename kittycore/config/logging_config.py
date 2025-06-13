"""
🔧 СИСТЕМА ЛОГИРОВАНИЯ KITTYCORE 3.0
Настройка loguru согласно CursorRules
"""

import sys
from pathlib import Path
from loguru import logger

def setup_kittycore_logging():
    """Настраивает систему логирования KittyCore 3.0"""
    
    # Удаляем стандартные обработчики
    logger.remove()
    
    # Создаём папку logs если её нет
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Консольный вывод (для разработки)
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # === ЛОГИ СОГЛАСНО CURSORRULES ===
    
    # Логи оркестратора
    logger.add(
        "logs/orchestrator.log",
        level="INFO",
        rotation="10 MB",
        compression="gz",
        serialize=True,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        filter=lambda record: "orchestrator" in record.get("name", "").lower()
    )
    
    # Логи агентов
    logger.add(
        "logs/agents.log", 
        level="INFO",
        rotation="10 MB",
        compression="gz",
        serialize=True,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        filter=lambda record: any(keyword in record.get("name", "").lower() 
                                for keyword in ["agent", "factory", "intellectual"])
    )
    
    # Логи памяти
    logger.add(
        "logs/memory.log",
        level="INFO", 
        rotation="10 MB",
        compression="gz",
        serialize=True,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        filter=lambda record: "memory" in record.get("name", "").lower()
    )
    
    # Логи человеческого вмешательства
    logger.add(
        "logs/human.log",
        level="INFO",
        rotation="10 MB", 
        compression="gz",
        serialize=True,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        filter=lambda record: any(keyword in record.get("name", "").lower()
                                for keyword in ["human", "collaboration", "obsidian"])
    )
    
    # Логи самообучения
    logger.add(
        "logs/improvement.log",
        level="INFO",
        rotation="10 MB",
        compression="gz", 
        serialize=True,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        filter=lambda record: any(keyword in record.get("name", "").lower()
                                for keyword in ["improvement", "validator", "fixer"])
    )
    
    # Общий лог системы
    logger.add(
        "logs/kittycore.log",
        level="DEBUG",
        rotation="50 MB",
        compression="gz",
        serialize=True,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"
    )
    
    # Лог ошибок
    logger.add(
        "logs/errors.log",
        level="ERROR",
        rotation="10 MB", 
        compression="gz",
        serialize=True,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message} | {exception}"
    )
    
    logger.info("🔧 Система логирования KittyCore 3.0 настроена")
    logger.info("📁 Логи сохраняются в папку logs/")

# Автоматическая настройка при импорте
setup_kittycore_logging() 