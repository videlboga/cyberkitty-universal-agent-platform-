"""
TelegramChannelHandler - обработчик для конкретного Telegram канала
"""

import asyncio
from typing import Dict, Any, Optional, List
from loguru import logger
import aiohttp
import json


class TelegramChannelHandler:
    """
    Обработчик для работы с конкретным Telegram каналом
    
    Инкапсулирует:
    - Bot API токен
    - Методы отправки сообщений
    - Управление polling/webhook
    - Обработка callback_query
    """
    
    def __init__(self, channel_id: str, bot_token: str):
        """
        Args:
            channel_id: ID канала в системе
            bot_token: Telegram Bot API токен
        """
        self.channel_id = channel_id
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.session: Optional[aiohttp.ClientSession] = None
        self.polling_task: Optional[asyncio.Task] = None
        self.last_update_id = 0
        
        logger.info(f"🤖 TelegramChannelHandler создан для канала {channel_id}")
    
    async def initialize(self):
        """Инициализация HTTP сессии"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info(f"🔗 HTTP сессия создана для канала {self.channel_id}")
    
    async def cleanup(self):
        """Очистка ресурсов"""
        if self.polling_task and not self.polling_task.done():
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
        
        if self.session:
            await self.session.close()
            self.session = None
        
        logger.info(f"🧹 Ресурсы очищены для канала {self.channel_id}")
    
    async def send_message(self, chat_id: str, text: str, **kwargs) -> Dict[str, Any]:
        """
        Отправка текстового сообщения
        
        Args:
            chat_id: ID чата
            text: Текст сообщения
            **kwargs: Дополнительные параметры (parse_mode, reply_markup и т.д.)
        
        Returns:
            Dict с результатом API вызова
        """
        await self.initialize()
        
        data = {
            "chat_id": chat_id,
            "text": text,
            **kwargs
        }
        
        try:
            async with self.session.post(f"{self.base_url}/sendMessage", json=data) as response:
                result = await response.json()
                
                if result.get("ok"):
                    logger.info(f"✅ Сообщение отправлено в чат {chat_id} через канал {self.channel_id}")
                    return {"success": True, "result": result["result"]}
                else:
                    error_msg = result.get("description", "Unknown error")
                    logger.error(f"❌ Ошибка отправки сообщения: {error_msg}")
                    return {"success": False, "error": error_msg}
                    
        except Exception as e:
            logger.error(f"❌ Исключение при отправке сообщения: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_buttons(self, chat_id: str, text: str, buttons: List[List[Dict[str, str]]], **kwargs) -> Dict[str, Any]:
        """
        Отправка сообщения с inline кнопками
        
        Args:
            chat_id: ID чата
            text: Текст сообщения
            buttons: Массив кнопок [[{"text": "Кнопка", "callback_data": "data"}]]
            **kwargs: Дополнительные параметры
        
        Returns:
            Dict с результатом API вызова
        """
        reply_markup = {
            "inline_keyboard": buttons
        }
        
        return await self.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            **kwargs
        )
    
    async def edit_message(self, chat_id: str, message_id: int, text: str, **kwargs) -> Dict[str, Any]:
        """
        Редактирование сообщения
        
        Args:
            chat_id: ID чата
            message_id: ID сообщения
            text: Новый текст
            **kwargs: Дополнительные параметры
        
        Returns:
            Dict с результатом API вызова
        """
        await self.initialize()
        
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            **kwargs
        }
        
        try:
            async with self.session.post(f"{self.base_url}/editMessageText", json=data) as response:
                result = await response.json()
                
                if result.get("ok"):
                    logger.info(f"✅ Сообщение {message_id} отредактировано в чате {chat_id}")
                    return {"success": True, "result": result["result"]}
                else:
                    error_msg = result.get("description", "Unknown error")
                    logger.error(f"❌ Ошибка редактирования сообщения: {error_msg}")
                    return {"success": False, "error": error_msg}
                    
        except Exception as e:
            logger.error(f"❌ Исключение при редактировании сообщения: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_polling(self, update_handler=None):
        """
        Запуск polling для получения обновлений
        
        Args:
            update_handler: Функция для обработки обновлений
        """
        if self.polling_task and not self.polling_task.done():
            logger.warning(f"⚠️ Polling уже запущен для канала {self.channel_id}")
            return
        
        self.polling_task = asyncio.create_task(self._polling_loop(update_handler))
        logger.info(f"🔄 Polling запущен для канала {self.channel_id}")
    
    async def stop_polling(self):
        """Остановка polling"""
        if self.polling_task and not self.polling_task.done():
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
            logger.info(f"⏹️ Polling остановлен для канала {self.channel_id}")
    
    async def _polling_loop(self, update_handler):
        """Основной цикл polling"""
        await self.initialize()
        
        while True:
            try:
                # Получаем обновления
                data = {
                    "offset": self.last_update_id + 1,
                    "timeout": 30,
                    "allowed_updates": ["message", "callback_query"]
                }
                
                async with self.session.post(f"{self.base_url}/getUpdates", json=data) as response:
                    result = await response.json()
                    
                    if result.get("ok"):
                        updates = result.get("result", [])
                        
                        for update in updates:
                            self.last_update_id = update["update_id"]
                            
                            if update_handler:
                                try:
                                    await update_handler(update, self.channel_id)
                                except Exception as e:
                                    logger.error(f"❌ Ошибка в update_handler: {e}")
                    else:
                        logger.error(f"❌ Ошибка getUpdates: {result.get('description')}")
                        await asyncio.sleep(5)
                        
            except asyncio.CancelledError:
                logger.info(f"🛑 Polling отменен для канала {self.channel_id}")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в polling loop: {e}")
                await asyncio.sleep(5)
    
    async def get_me(self) -> Dict[str, Any]:
        """
        Получение информации о боте
        
        Returns:
            Dict с информацией о боте
        """
        await self.initialize()
        
        try:
            async with self.session.get(f"{self.base_url}/getMe") as response:
                result = await response.json()
                
                if result.get("ok"):
                    return {"success": True, "result": result["result"]}
                else:
                    error_msg = result.get("description", "Unknown error")
                    return {"success": False, "error": error_msg}
                    
        except Exception as e:
            logger.error(f"❌ Ошибка getMe: {e}")
            return {"success": False, "error": str(e)}
    
    async def healthcheck(self) -> bool:
        """
        Проверка работоспособности канала
        
        Returns:
            bool: True если канал работает
        """
        try:
            result = await self.get_me()
            if result.get("success"):
                logger.info(f"✅ Healthcheck OK для канала {self.channel_id}")
                return True
            else:
                logger.error(f"❌ Healthcheck FAIL для канала {self.channel_id}: {result.get('error')}")
                return False
        except Exception as e:
            logger.error(f"❌ Healthcheck ERROR для канала {self.channel_id}: {e}")
            return False 