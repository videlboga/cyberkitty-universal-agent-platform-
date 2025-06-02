#!/usr/bin/env python3
"""
📺 ПОЛУЧЕНИЕ ID СООБЩЕНИЙ ИЗ КАНАЛА ONTOBOT
Скрипт для получения реальных ID видео из канала -1002614708769
"""

import asyncio
import json
from datetime import datetime
import aiohttp
from loguru import logger

# Настройка логирования
logger.add("logs/channel_messages.log", 
          format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | CHANNEL | {message}",
          level="INFO", rotation="10 MB", compression="zip")

class ChannelMessageGetter:
    """Получает информацию о сообщениях из канала через Telegram Bot API."""
    
    def __init__(self, bot_token: str = None):
        self.bot_token = bot_token or self._get_bot_token()
        self.channel_id = "-1002614708769"
        
        logger.info("📺 Channel Message Getter инициализирован")
        
    def _get_bot_token(self) -> str:
        """Получает токен бота из переменных окружения или файла."""
        import os
        
        # Пробуем получить из переменных окружения
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if token:
            return token
            
        # Пробуем получить из файла .env
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('TELEGRAM_BOT_TOKEN='):
                        return line.split('=', 1)[1].strip().strip('"\'')
        except FileNotFoundError:
            pass
            
        # Пробуем получить из базы данных через KittyCore
        return self._get_token_from_db()
    
    def _get_token_from_db(self) -> str:
        """Получает токен из базы данных через KittyCore API."""
        # Здесь можно добавить запрос к KittyCore для получения токена
        # Пока возвращаем None, чтобы пользователь ввел токен вручную
        return None
    
    async def get_channel_updates(self, limit: int = 10) -> dict:
        """Получает последние обновления из канала."""
        
        if not self.bot_token:
            logger.error("❌ Токен бота не найден")
            return {"error": "Токен бота не найден"}
        
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        
        logger.info(f"🌐 Запрос обновлений из канала {self.channel_id}")
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "limit": limit,
                    "timeout": 10
                }
                
                async with session.get(url, params=params) as response:
                    result = await response.json()
                    
                    logger.info(f"📥 Получено обновлений: {len(result.get('result', []))}")
                    
                    return result
                    
        except Exception as e:
            logger.error(f"❌ Ошибка получения обновлений: {str(e)}")
            return {"error": str(e)}
    
    async def get_chat_info(self) -> dict:
        """Получает информацию о канале."""
        
        if not self.bot_token:
            logger.error("❌ Токен бота не найден")
            return {"error": "Токен бота не найден"}
        
        url = f"https://api.telegram.org/bot{self.bot_token}/getChat"
        
        logger.info(f"🔍 Получение информации о канале {self.channel_id}")
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "chat_id": self.channel_id
                }
                
                async with session.get(url, params=params) as response:
                    result = await response.json()
                    
                    logger.info(f"📋 Информация о канале получена: {result.get('ok', False)}")
                    
                    return result
                    
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о канале: {str(e)}")
            return {"error": str(e)}
    
    async def send_test_message(self, text: str = "🧪 Тестовое сообщение") -> dict:
        """Отправляет тестовое сообщение в канал для проверки доступа."""
        
        if not self.bot_token:
            logger.error("❌ Токен бота не найден")
            return {"error": "Токен бота не найден"}
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        logger.info(f"📤 Отправка тестового сообщения в канал {self.channel_id}")
        
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "chat_id": self.channel_id,
                    "text": text
                }
                
                async with session.post(url, json=data) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        message_id = result.get('result', {}).get('message_id')
                        logger.info(f"✅ Сообщение отправлено, ID: {message_id}")
                    else:
                        logger.error(f"❌ Ошибка отправки: {result.get('description')}")
                    
                    return result
                    
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения: {str(e)}")
            return {"error": str(e)}
    
    async def check_channel_access(self) -> dict:
        """Проверяет доступ к каналу и возможность получения сообщений."""
        
        logger.info("🔐 Проверка доступа к каналу")
        
        results = {
            "channel_info": await self.get_chat_info(),
            "updates": await self.get_channel_updates(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Анализируем результаты
        channel_accessible = results["channel_info"].get("ok", False)
        updates_available = results["updates"].get("ok", False)
        
        logger.info(f"📊 Результаты проверки:")
        logger.info(f"   Канал доступен: {channel_accessible}")
        logger.info(f"   Обновления доступны: {updates_available}")
        
        if channel_accessible:
            chat_info = results["channel_info"].get("result", {})
            logger.info(f"   Название канала: {chat_info.get('title', 'Неизвестно')}")
            logger.info(f"   Тип: {chat_info.get('type', 'Неизвестно')}")
        
        if updates_available:
            updates = results["updates"].get("result", [])
            logger.info(f"   Количество обновлений: {len(updates)}")
            
            # Ищем сообщения из нашего канала
            channel_messages = []
            for update in updates:
                message = update.get("message", {})
                chat = message.get("chat", {})
                if str(chat.get("id")) == self.channel_id:
                    channel_messages.append({
                        "message_id": message.get("message_id"),
                        "text": message.get("text", "")[:100],
                        "date": message.get("date"),
                        "content_type": self._get_content_type(message)
                    })
            
            logger.info(f"   Сообщений из канала: {len(channel_messages)}")
            results["channel_messages"] = channel_messages
        
        return results
    
    def _get_content_type(self, message: dict) -> str:
        """Определяет тип контента сообщения."""
        if message.get("video"):
            return "video"
        elif message.get("photo"):
            return "photo"
        elif message.get("document"):
            return "document"
        elif message.get("text"):
            return "text"
        else:
            return "other"
    
    async def manual_message_check(self) -> dict:
        """Ручная проверка конкретных ID сообщений."""
        
        logger.info("🔍 Ручная проверка сообщений")
        
        # Пробуем получить сообщения с ID от 1 до 10
        message_results = {}
        
        for msg_id in range(1, 11):
            try:
                # Пробуем переслать сообщение самому себе для проверки
                url = f"https://api.telegram.org/bot{self.bot_token}/forwardMessage"
                
                async with aiohttp.ClientSession() as session:
                    data = {
                        "chat_id": self.channel_id,  # Пересылаем в тот же канал
                        "from_chat_id": self.channel_id,
                        "message_id": msg_id
                    }
                    
                    async with session.post(url, json=data) as response:
                        result = await response.json()
                        
                        if result.get('ok'):
                            logger.info(f"✅ Сообщение {msg_id} существует")
                            message_results[msg_id] = "exists"
                        else:
                            logger.info(f"❌ Сообщение {msg_id} не найдено: {result.get('description', '')}")
                            message_results[msg_id] = "not_found"
                            
            except Exception as e:
                logger.error(f"❌ Ошибка проверки сообщения {msg_id}: {str(e)}")
                message_results[msg_id] = f"error: {str(e)}"
        
        return message_results

async def main():
    """Главная функция для проверки канала."""
    
    print("📺 ПОЛУЧЕНИЕ ID СООБЩЕНИЙ ИЗ КАНАЛА ONTOBOT")
    print("="*60)
    
    # Запрашиваем токен у пользователя
    bot_token = input("🤖 Введите токен Telegram бота (или нажмите Enter для автоопределения): ").strip()
    
    if not bot_token:
        bot_token = None
    
    getter = ChannelMessageGetter(bot_token)
    
    if not getter.bot_token:
        print("❌ Токен бота не найден. Пожалуйста, укажите токен.")
        return
    
    print(f"✅ Токен найден: {getter.bot_token[:10]}...")
    print(f"🎯 Проверяем канал: {getter.channel_id}")
    
    # Проверяем доступ к каналу
    print("\n🔐 Проверка доступа к каналу...")
    access_results = await getter.check_channel_access()
    
    # Сохраняем результаты
    with open("logs/channel_access_results.json", "w", encoding="utf-8") as f:
        json.dump(access_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Результаты сохранены в logs/channel_access_results.json")
    
    # Если есть проблемы с доступом, пробуем ручную проверку
    if not access_results.get("channel_info", {}).get("ok"):
        print("\n🔍 Пробуем ручную проверку сообщений...")
        manual_results = await getter.manual_message_check()
        
        with open("logs/manual_message_check.json", "w", encoding="utf-8") as f:
            json.dump(manual_results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Результаты ручной проверки сохранены в logs/manual_message_check.json")
    
    print("\n✅ Проверка завершена!")

if __name__ == "__main__":
    asyncio.run(main()) 