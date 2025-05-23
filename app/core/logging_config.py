from loguru import logger
import sys

def setup_logging():
    """Настраивает глобальный логгер Loguru для всего приложения."""
    
    logger.remove() # Удаляем все предыдущие обработчики, чтобы избежать дублирования

    # Стандартный вывод (консоль) - полезно для разработки и Docker logs
    logger.add(
        sys.stderr, 
        level="INFO", # Или DEBUG, если нужно больше деталей в консоли
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # --- Основные файловые логгеры согласно CursorRules и нашим потребностям ---

    # Общий лог приложения (для сообщений, не попадающих в специализированные логи)
    logger.add(
        "logs/main_app.log", 
        level="INFO", 
        rotation="10 MB", 
        compression="zip", 
        serialize=True, 
        format="{time} {level} {name}:{function}:{line} {message}"
    )

    # Лог ошибок
    logger.add(
        "logs/errors.log", 
        level="ERROR", 
        rotation="10 MB", 
        compression="zip", 
        serialize=True, 
        format="{time} {level} {name}:{function}:{line} {message} {exception}"
    )

    # Лог аудита (пока INFO, можно сделать более специфичным)
    # logger.add(
    #     "logs/audit.log", 
    #     level="INFO", 
    #     rotation="10 MB", 
    #     compression="zip", 
    #     serialize=True, 
    #     format="{time} {level} {name}:{function}:{line} {message}" # Добавить user_id, agent_id и т.д. при записи
    # )

    # Лог выполнения сценариев
    logger.add(
        "logs/scenario_executor.log", 
        level="DEBUG", 
        rotation="10 MB", 
        compression="zip", 
        serialize=True, 
        format="{time} {level} {name}:{function}:{line} {message}"
    )

    # Лог Telegram Plugin
    logger.add(
        "logs/telegram_plugin.log", 
        level="DEBUG", # Ставим DEBUG для детальной отладки
        rotation="10 MB", 
        compression="zip", 
        serialize=True, 
        format="{time} {level} {name}:{function}:{line} {message}"
    )

    # Логи интеграций
    logger.add(
        "logs/llm_integration.log", 
        level="INFO", 
        rotation="10 MB", 
        compression="zip", 
        serialize=True, 
        format="{time} {level} {name}:{function}:{line} {message}"
    )
    logger.add(
        "logs/rag_integration.log", 
        level="INFO", 
        rotation="10 MB", 
        compression="zip", 
        serialize=True, 
        format="{time} {level} {name}:{function}:{line} {message}"
    )
    # logger.add(
    #     "logs/crm_integration.log", 
    #     level="INFO", 
    #     rotation="10 MB", 
    #     compression="zip", 
    #     serialize=True, 
    #     format="{time} {level} {name}:{function}:{line} {message}"
    # ) # Раскомментировать, когда появится CRM

    # Лог запуска агентов (из app/api/runner.py)
    logger.add(
        "logs/agent_launch.log", 
        level="INFO", 
        rotation="10 MB", 
        compression="zip", 
        serialize=True, 
        format="{time} {level} {name}:{function}:{line} {message}"
    )

    # Лог событий StateMachine
    logger.add(
        "logs/events.log", 
        level="INFO", 
        rotation="10 MB", 
        compression="zip", 
        serialize=True, 
        format="{time} {level} {name}:{function}:{line} {message}"
    )
    logger.add(
        "logs/debug_state_machine.log", 
        level="DEBUG", 
        rotation="10 MB", 
        compression="zip", 
        serialize=True, 
        format="{time} {level} {name}:{function}:{line} {message}"
    )

    # Лог безопасности (пока INFO, можно сделать более специфичным)
    # logger.add(
    #     "logs/security.log", 
    #     level="INFO", 
    #     rotation="10 MB", 
    #     compression="zip", 
    #     serialize=True, 
    #     format="{time} {level} {name}:{function}:{line} {message}"
    # )

    # Логи других важных компонентов/плагинов
    logger.add(
        "logs/mongo_storage_plugin.log", 
        level="INFO", 
        rotation="10 MB", 
        compression="zip", 
        serialize=True, 
        format="{time} {level} {name}:{function}:{line} {message}"
    )
    logger.add(
        "logs/scheduling_plugin.log",
        level="INFO", 
        rotation="10 MB", 
        compression="zip", 
        serialize=True, 
        format="{time} {level} {name}:{function}:{line} {message}"
    )
    logger.add(
        "logs/collections_api.log", # Для app.api.collection
        level="INFO", 
        rotation="10 MB", 
        compression="zip", 
        serialize=True, 
        format="{time} {level} {name}:{function}:{line} {message}"
    )
    logger.add(
        "logs/learning_api.log", # Для app.api.learning
        level="INFO", 
        rotation="10 MB", 
        compression="zip", 
        serialize=True, 
        format="{time} {level} {name}:{function}:{line} {message}"
    )

    logger.info("Logging setup complete.")

if __name__ == "__main__":
    # Для тестирования конфигурации логирования
    setup_logging()
    logger.debug("Это debug сообщение.")
    logger.info("Это info сообщение.")
    logger.warning("Это warning сообщение.")
    logger.error("Это error сообщение.")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("Это exception сообщение.") 