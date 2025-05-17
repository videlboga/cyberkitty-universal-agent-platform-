import os
import asyncio
import uvicorn
from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from loguru import logger
from telegram import Bot

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/test_local_api.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

app = FastAPI(title="Test API for Telegram Notifications")

# Создаем модель для запроса тестового уведомления
class TestNotificationRequest(BaseModel):
    user_id: str
    message: str = Field(..., description="Текст сообщения для отправки")
    channel: str = Field(default="telegram", description="Канал отправки сообщения")

# Получаем токен из переменной окружения или используем значение из файла .env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8020429038:AAEvO8SW0sD5u7ZSdizYruy8JpXXDrjVuxI")

@app.get("/health")
async def health():
    """Простой healthcheck для проверки работы API"""
    logger.info("Healthcheck запрошен")
    return {"status": "ok"}

@app.post("/test-notification")
async def send_test_notification(request: TestNotificationRequest = Body(...)):
    """
    Отправить тестовое уведомление с указанным сообщением напрямую через Bot API
    """
    try:
        # Логируем начало запроса для отладки
        logger.info(f"Начало обработки запроса test-notification: {request}")
        
        # Получаем параметры запроса
        user_id = request.user_id
        message = request.message
        channel = request.channel
        
        # Используем только прямую отправку через Bot API
        if channel == "telegram":
            try:
                # Преобразуем user_id в int, если это строка с числом
                chat_id = int(user_id) if user_id.isdigit() else int(os.getenv("TEST_TELEGRAM_CHAT_ID", 648981358))
                
                # Логируем попытку отправки
                logger.info(f"Попытка прямой отправки сообщения через Bot API пользователю {chat_id}")
                
                # Инициализируем бота
                bot = Bot(token=TELEGRAM_BOT_TOKEN)
                
                # Отправляем сообщение
                await bot.send_message(chat_id=chat_id, text=message)
                
                # Логируем успешную отправку
                logger.info(f"Сообщение успешно отправлено пользователю {chat_id}")
                
                return {"status": "success", "message": "Сообщение успешно отправлено"}
                    
            except Exception as e:
                logger.error(f"Ошибка при прямой отправке сообщения: {e}")
                return {"status": "error", "message": f"Ошибка при отправке: {str(e)}"}
        else:
            # Пока поддерживаем только Telegram
            return {"status": "error", "message": f"Канал {channel} не поддерживается"}
            
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при отправке уведомления: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Непредвиденная ошибка: {str(e)}"
        )

# Запуск сервера при выполнении скрипта напрямую
if __name__ == "__main__":
    print("Запуск тестового API-сервера на http://localhost:8001")
    print("Доступные эндпоинты:")
    print("  - GET /health - проверка работоспособности")
    print("  - POST /test-notification - отправка тестового уведомления")
    print("\nДля остановки нажмите Ctrl+C")
    uvicorn.run(app, host="0.0.0.0", port=8001) 