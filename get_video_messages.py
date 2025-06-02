#!/usr/bin/env python3
"""
📺 ПОЛУЧЕНИЕ ID ВИДЕО СООБЩЕНИЙ ИЗ КАНАЛА ONTOBOT
Скрипт для получения реальных ID видео из канала -1002614708769
"""

import asyncio
import json
from datetime import datetime
import aiohttp
from loguru import logger

# Настройка логирования
logger.add("logs/video_messages.log", 
          format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | VIDEO | {message}",
          level="INFO", rotation="10 MB", compression="zip")

class VideoMessageGetter:
    """Получает ID видео сообщений из канала."""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.channel_id = "-1002614708769"
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        logger.info("📺 Video Message Getter инициализирован")
        
    async def get_channel_history(self, limit: int = 50) -> dict:
        """Получает историю сообщений из канала через getUpdates."""
        
        url = f"{self.base_url}/getUpdates"
        
        logger.info(f"📥 Получение истории канала (лимит: {limit})")
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "limit": limit,
                    "timeout": 30
                }
                
                async with session.get(url, params=params) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        updates = result.get('result', [])
                        logger.info(f"✅ Получено обновлений: {len(updates)}")
                        
                        # Фильтруем сообщения из нашего канала
                        channel_messages = []
                        for update in updates:
                            message = update.get('message', {})
                            chat = message.get('chat', {})
                            
                            if str(chat.get('id')) == self.channel_id:
                                message_info = {
                                    "message_id": message.get('message_id'),
                                    "date": message.get('date'),
                                    "content_type": self._get_content_type(message),
                                    "text": message.get('text', '')[:100],
                                    "caption": message.get('caption', '')[:100]
                                }
                                
                                # Добавляем информацию о видео
                                if message.get('video'):
                                    video = message.get('video', {})
                                    message_info['video'] = {
                                        "file_id": video.get('file_id'),
                                        "duration": video.get('duration'),
                                        "width": video.get('width'),
                                        "height": video.get('height'),
                                        "file_size": video.get('file_size')
                                    }
                                
                                channel_messages.append(message_info)
                        
                        logger.info(f"📺 Найдено сообщений из канала: {len(channel_messages)}")
                        
                        # Сортируем по message_id
                        channel_messages.sort(key=lambda x: x['message_id'])
                        
                        for msg in channel_messages:
                            logger.info(f"   ID {msg['message_id']}: {msg['content_type']} - {msg.get('text', msg.get('caption', 'Без текста'))[:50]}")
                        
                        return {
                            "ok": True,
                            "channel_messages": channel_messages,
                            "total_updates": len(updates)
                        }
                    else:
                        logger.error(f"❌ Ошибка получения обновлений: {result.get('description')}")
                        return result
                        
        except Exception as e:
            logger.error(f"❌ Ошибка получения истории: {str(e)}")
            return {"error": str(e)}
    
    async def check_specific_messages(self, message_ids: list) -> dict:
        """Проверяет существование конкретных ID сообщений."""
        
        logger.info(f"🔍 Проверка конкретных ID сообщений: {message_ids}")
        
        results = {}
        
        for msg_id in message_ids:
            try:
                # Пробуем переслать сообщение в тот же канал для проверки
                url = f"{self.base_url}/forwardMessage"
                
                async with aiohttp.ClientSession() as session:
                    data = {
                        "chat_id": self.channel_id,
                        "from_chat_id": self.channel_id,
                        "message_id": msg_id
                    }
                    
                    async with session.post(url, json=data) as response:
                        result = await response.json()
                        
                        if result.get('ok'):
                            logger.info(f"✅ Сообщение {msg_id} существует")
                            results[msg_id] = {
                                "exists": True,
                                "forwarded_message_id": result.get('result', {}).get('message_id')
                            }
                        else:
                            logger.info(f"❌ Сообщение {msg_id} не найдено: {result.get('description', '')}")
                            results[msg_id] = {
                                "exists": False,
                                "error": result.get('description', 'Unknown error')
                            }
                            
            except Exception as e:
                logger.error(f"❌ Ошибка проверки сообщения {msg_id}: {str(e)}")
                results[msg_id] = {
                    "exists": False,
                    "error": str(e)
                }
        
        return results
    
    async def get_message_by_id(self, message_id: int) -> dict:
        """Получает информацию о конкретном сообщении."""
        
        logger.info(f"📄 Получение информации о сообщении {message_id}")
        
        try:
            # Используем метод copyMessage для получения информации
            url = f"{self.base_url}/copyMessage"
            
            async with aiohttp.ClientSession() as session:
                data = {
                    "chat_id": self.channel_id,
                    "from_chat_id": self.channel_id,
                    "message_id": message_id
                }
                
                async with session.post(url, json=data) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        logger.info(f"✅ Сообщение {message_id} скопировано")
                        return {
                            "exists": True,
                            "copied_message_id": result.get('result', {}).get('message_id')
                        }
                    else:
                        logger.info(f"❌ Сообщение {message_id} не найдено: {result.get('description', '')}")
                        return {
                            "exists": False,
                            "error": result.get('description', 'Unknown error')
                        }
                        
        except Exception as e:
            logger.error(f"❌ Ошибка получения сообщения {message_id}: {str(e)}")
            return {
                "exists": False,
                "error": str(e)
            }
    
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
        elif message.get("animation"):
            return "animation"
        else:
            return "other"

async def main():
    """Главная функция для получения ID видео сообщений."""
    
    print("📺 ПОЛУЧЕНИЕ ID ВИДЕО СООБЩЕНИЙ ИЗ КАНАЛА ONTOBOT")
    print("="*60)
    
    bot_token = "7907324843:AAFjN2H4ud2X6rm7XShrmS3G1l1JnCo4feM"
    
    getter = VideoMessageGetter(bot_token)
    
    print(f"🤖 Бот: @CyberKittyTest_bot")
    print(f"📺 Канал: {getter.channel_id}")
    
    # 1. Получаем историю сообщений
    print("\n📥 Получение истории сообщений...")
    history = await getter.get_channel_history()
    
    if history.get('ok'):
        messages = history.get('channel_messages', [])
        print(f"✅ Найдено сообщений: {len(messages)}")
        
        # Показываем все сообщения
        print("\n📋 СПИСОК СООБЩЕНИЙ:")
        print("-" * 50)
        
        video_messages = []
        for msg in messages:
            content_type = msg['content_type']
            msg_id = msg['message_id']
            text = msg.get('text', msg.get('caption', 'Без текста'))[:50]
            
            print(f"ID {msg_id:2d}: {content_type:8s} - {text}")
            
            if content_type == 'video':
                video_messages.append(msg_id)
        
        print(f"\n🎬 Найдено видео сообщений: {len(video_messages)}")
        if video_messages:
            print(f"📺 ID видео: {video_messages}")
            
            # Обновляем сценарии с реальными ID
            video_mapping = {
                "mr_ontobot_main_router": video_messages[0] if len(video_messages) > 0 else 2,
                "mr_ontobot_diagnostic_ya_ya": video_messages[1] if len(video_messages) > 1 else 3,
                "mr_ontobot_diagnostic_ya_delo": video_messages[2] if len(video_messages) > 2 else 4,
                "mr_ontobot_diagnostic_ya_relations": video_messages[3] if len(video_messages) > 3 else 5
            }
            
            print(f"\n🔄 РЕКОМЕНДУЕМОЕ СОПОСТАВЛЕНИЕ:")
            print("-" * 40)
            for scenario, msg_id in video_mapping.items():
                print(f"{scenario}: message_id = {msg_id}")
    
    # 2. Проверяем конкретные ID (1-10)
    print(f"\n🔍 Проверка ID сообщений 1-10...")
    check_results = await getter.check_specific_messages(list(range(1, 11)))
    
    existing_ids = [msg_id for msg_id, info in check_results.items() if info.get('exists')]
    print(f"✅ Существующие ID: {existing_ids}")
    
    # Сохраняем результаты
    all_results = {
        "channel_history": history,
        "message_check": check_results,
        "video_messages": video_messages if 'video_messages' in locals() else [],
        "timestamp": datetime.now().isoformat()
    }
    
    with open("logs/video_messages_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Результаты сохранены в logs/video_messages_results.json")
    print("\n✅ Получение ID завершено!")

if __name__ == "__main__":
    asyncio.run(main()) 