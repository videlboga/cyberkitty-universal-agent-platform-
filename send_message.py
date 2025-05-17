import os
import asyncio
from telegram import Bot
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Получение токена бота из переменной окружения или из значения по умолчанию
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8020429038:AAEvO8SW0sD5u7ZSdizYruy8JpXXDrjVuxI")

async def send_message(chat_id: int, text: str):
    """
    Отправить сообщение через Telegram бот напрямую
    
    Args:
        chat_id: ID чата
        text: Текст сообщения
    """
    try:
        logger.info(f"Попытка отправки сообщения пользователю {chat_id}")
        
        # Инициализация бота
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Отправка сообщения
        await bot.send_message(chat_id=chat_id, text=text)
        
        logger.info(f"Сообщение успешно отправлено пользователю {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        return False

async def main():
    """Основная функция для отправки тестового сообщения"""
    chat_id = 648981358
    message = "Тестовое сообщение MVP без планировщика - прямой вызов Bot API"
    
    success = await send_message(chat_id, message)
    if success:
        print("Сообщение успешно отправлено!")
    else:
        print("Ошибка при отправке сообщения")

if __name__ == "__main__":
    asyncio.run(main()) 