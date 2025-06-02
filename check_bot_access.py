#!/usr/bin/env python3
"""
🔍 ПРОВЕРКА ДОСТУПА БОТА К КАНАЛАМ
Скрипт для проверки доступных каналов и получения информации о боте
"""

import asyncio
import json
from datetime import datetime
import aiohttp
from loguru import logger

# Настройка логирования
logger.add("logs/bot_access_check.log", 
          format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | BOT_ACCESS | {message}",
          level="INFO", rotation="10 MB", compression="zip")

class BotAccessChecker:
    """Проверяет доступ бота к различным каналам и чатам."""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        logger.info("🔍 Bot Access Checker инициализирован")
        
    async def get_me(self) -> dict:
        """Получает информацию о боте."""
        
        url = f"{self.base_url}/getMe"
        
        logger.info("🤖 Получение информации о боте")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        bot_info = result.get('result', {})
                        logger.info(f"✅ Бот найден: @{bot_info.get('username', 'unknown')}")
                        logger.info(f"   ID: {bot_info.get('id')}")
                        logger.info(f"   Имя: {bot_info.get('first_name', 'unknown')}")
                    else:
                        logger.error(f"❌ Ошибка получения информации о боте: {result.get('description')}")
                    
                    return result
                    
        except Exception as e:
            logger.error(f"❌ Ошибка запроса информации о боте: {str(e)}")
            return {"error": str(e)}
    
    async def get_updates(self, limit: int = 100) -> dict:
        """Получает последние обновления."""
        
        url = f"{self.base_url}/getUpdates"
        
        logger.info(f"📥 Получение последних {limit} обновлений")
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "limit": limit,
                    "timeout": 10
                }
                
                async with session.get(url, params=params) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        updates = result.get('result', [])
                        logger.info(f"✅ Получено обновлений: {len(updates)}")
                        
                        # Анализируем чаты
                        chats = {}
                        for update in updates:
                            message = update.get('message', {})
                            chat = message.get('chat', {})
                            
                            if chat:
                                chat_id = chat.get('id')
                                if chat_id not in chats:
                                    chats[chat_id] = {
                                        "id": chat_id,
                                        "type": chat.get('type'),
                                        "title": chat.get('title', chat.get('first_name', 'Unknown')),
                                        "username": chat.get('username'),
                                        "message_count": 0
                                    }
                                chats[chat_id]["message_count"] += 1
                        
                        logger.info(f"📊 Найдено уникальных чатов: {len(chats)}")
                        for chat_id, chat_info in chats.items():
                            logger.info(f"   {chat_id}: {chat_info['title']} ({chat_info['type']}) - {chat_info['message_count']} сообщений")
                        
                        result['analyzed_chats'] = chats
                    else:
                        logger.error(f"❌ Ошибка получения обновлений: {result.get('description')}")
                    
                    return result
                    
        except Exception as e:
            logger.error(f"❌ Ошибка получения обновлений: {str(e)}")
            return {"error": str(e)}
    
    async def try_channel_access(self, channel_id: str) -> dict:
        """Пробует получить доступ к конкретному каналу."""
        
        logger.info(f"🎯 Проверка доступа к каналу {channel_id}")
        
        results = {}
        
        # 1. Пробуем получить информацию о чате
        try:
            url = f"{self.base_url}/getChat"
            async with aiohttp.ClientSession() as session:
                params = {"chat_id": channel_id}
                async with session.get(url, params=params) as response:
                    chat_info = await response.json()
                    results['chat_info'] = chat_info
                    
                    if chat_info.get('ok'):
                        logger.info(f"✅ Информация о канале получена")
                        chat_data = chat_info.get('result', {})
                        logger.info(f"   Название: {chat_data.get('title', 'Unknown')}")
                        logger.info(f"   Тип: {chat_data.get('type', 'Unknown')}")
                        logger.info(f"   Username: @{chat_data.get('username', 'None')}")
                    else:
                        logger.error(f"❌ Ошибка получения информации: {chat_info.get('description')}")
        except Exception as e:
            logger.error(f"❌ Ошибка запроса информации о чате: {str(e)}")
            results['chat_info'] = {"error": str(e)}
        
        # 2. Пробуем получить количество участников
        try:
            url = f"{self.base_url}/getChatMemberCount"
            async with aiohttp.ClientSession() as session:
                params = {"chat_id": channel_id}
                async with session.get(url, params=params) as response:
                    member_count = await response.json()
                    results['member_count'] = member_count
                    
                    if member_count.get('ok'):
                        count = member_count.get('result', 0)
                        logger.info(f"✅ Участников в канале: {count}")
                    else:
                        logger.error(f"❌ Ошибка получения количества участников: {member_count.get('description')}")
        except Exception as e:
            logger.error(f"❌ Ошибка запроса количества участников: {str(e)}")
            results['member_count'] = {"error": str(e)}
        
        # 3. Пробуем получить статус бота в канале
        try:
            url = f"{self.base_url}/getChatMember"
            bot_info = await self.get_me()
            if bot_info.get('ok'):
                bot_id = bot_info.get('result', {}).get('id')
                
                async with aiohttp.ClientSession() as session:
                    params = {"chat_id": channel_id, "user_id": bot_id}
                    async with session.get(url, params=params) as response:
                        member_status = await response.json()
                        results['bot_status'] = member_status
                        
                        if member_status.get('ok'):
                            status_data = member_status.get('result', {})
                            status = status_data.get('status', 'unknown')
                            logger.info(f"✅ Статус бота в канале: {status}")
                        else:
                            logger.error(f"❌ Ошибка получения статуса бота: {member_status.get('description')}")
        except Exception as e:
            logger.error(f"❌ Ошибка запроса статуса бота: {str(e)}")
            results['bot_status'] = {"error": str(e)}
        
        return results
    
    async def check_webhook_info(self) -> dict:
        """Проверяет информацию о webhook."""
        
        url = f"{self.base_url}/getWebhookInfo"
        
        logger.info("🔗 Проверка webhook информации")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        webhook_info = result.get('result', {})
                        webhook_url = webhook_info.get('url', '')
                        
                        if webhook_url:
                            logger.info(f"✅ Webhook установлен: {webhook_url}")
                        else:
                            logger.info("ℹ️ Webhook не установлен (polling режим)")
                        
                        logger.info(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
                        
                        if webhook_info.get('last_error_date'):
                            logger.warning(f"⚠️ Последняя ошибка: {webhook_info.get('last_error_message')}")
                    else:
                        logger.error(f"❌ Ошибка получения webhook информации: {result.get('description')}")
                    
                    return result
                    
        except Exception as e:
            logger.error(f"❌ Ошибка запроса webhook информации: {str(e)}")
            return {"error": str(e)}

async def main():
    """Главная функция для проверки доступа бота."""
    
    print("🔍 ПРОВЕРКА ДОСТУПА БОТА К КАНАЛАМ")
    print("="*50)
    
    bot_token = "7907324843:AAFjN2H4ud2X6rm7XShrmS3G1l1JnCo4feM"
    target_channel = "-1002614708769"
    
    checker = BotAccessChecker(bot_token)
    
    print(f"🤖 Проверяем бота: {bot_token[:10]}...")
    print(f"🎯 Целевой канал: {target_channel}")
    
    # 1. Получаем информацию о боте
    print("\n🤖 Информация о боте:")
    bot_info = await checker.get_me()
    
    # 2. Получаем обновления и анализируем доступные чаты
    print("\n📥 Анализ доступных чатов:")
    updates_info = await checker.get_updates()
    
    # 3. Проверяем доступ к целевому каналу
    print(f"\n🎯 Проверка доступа к каналу {target_channel}:")
    channel_access = await checker.try_channel_access(target_channel)
    
    # 4. Проверяем webhook
    print("\n🔗 Проверка webhook:")
    webhook_info = await checker.check_webhook_info()
    
    # Сохраняем все результаты
    all_results = {
        "bot_info": bot_info,
        "updates_info": updates_info,
        "channel_access": channel_access,
        "webhook_info": webhook_info,
        "timestamp": datetime.now().isoformat()
    }
    
    with open("logs/bot_full_access_check.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Полные результаты сохранены в logs/bot_full_access_check.json")
    
    # Выводим краткую сводку
    print("\n📊 КРАТКАЯ СВОДКА:")
    print("="*30)
    
    if bot_info.get('ok'):
        bot_data = bot_info.get('result', {})
        print(f"✅ Бот активен: @{bot_data.get('username', 'unknown')}")
    else:
        print("❌ Проблемы с ботом")
    
    if updates_info.get('ok'):
        chats = updates_info.get('analyzed_chats', {})
        print(f"📱 Доступно чатов: {len(chats)}")
        
        # Показываем каналы/супергруппы
        channels = {k: v for k, v in chats.items() if v.get('type') in ['channel', 'supergroup']}
        if channels:
            print("📺 Доступные каналы/группы:")
            for chat_id, chat_info in channels.items():
                print(f"   {chat_id}: {chat_info['title']} ({chat_info['type']})")
        else:
            print("❌ Доступных каналов не найдено")
    
    channel_accessible = channel_access.get('chat_info', {}).get('ok', False)
    print(f"🎯 Целевой канал доступен: {'✅ Да' if channel_accessible else '❌ Нет'}")
    
    print("\n✅ Проверка завершена!")

if __name__ == "__main__":
    asyncio.run(main()) 