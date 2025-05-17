from app.api.integration import telegram_app, telegram_plugin, TELEGRAM_BOT_TOKEN
import os
import sys
import asyncio
from loguru import logger

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/telegram_bot.log", format="{time} {level} {message}", level="INFO", 
          rotation="10 MB", compression="zip", serialize=True)

async def main():
    """Запуск Telegram-бота в асинхронном режиме с обработкой ошибок и логированием."""
    try:
        bot_info = await telegram_app.bot.get_me()
        logger.info(f"Бот запущен: @{bot_info.username} (ID: {bot_info.id})")
        logger.info(f"Обработчики: {len(telegram_app.handlers)}")
        
        # Проверка обработчиков (диагностика)
        for handler in telegram_app.handlers:
            logger.info(f"- {handler.__class__.__name__}")
        
        await telegram_app.initialize()
        await telegram_app.start()
        await telegram_app.updater.start_polling()
        
        logger.info("Бот успешно запущен и ожидает сообщения")
        
        # Бесконечный цикл для поддержания работы бота
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        sys.exit(1)
    finally:
        # Корректное завершение при остановке скрипта
        await telegram_app.stop()
        await telegram_app.shutdown()

if __name__ == "__main__":
    try:
        # Информация о боте перед запуском
        logger.info(f"Запуск бота с токеном: {TELEGRAM_BOT_TOKEN[:6]}...{TELEGRAM_BOT_TOKEN[-6:]}")
        
        # Запуск асинхронного main
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1) 