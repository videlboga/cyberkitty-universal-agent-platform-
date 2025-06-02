#!/usr/bin/env python3
"""
🤖 СОЗДАНИЕ КАНАЛА ONTOBOT И ЗАПУСК РЕАЛЬНОГО БОТА
Скрипт для создания канала с токеном 7907324843:AAFjN2H4ud2X6rm7XShrmS3G1l1JnCo4feM
и запуска пользовательского сценария mr_ontobot_main_router
"""

import asyncio
import json
import aiohttp
from datetime import datetime
from loguru import logger

# Настройка логирования
logger.add("logs/ontobot_channel.log", 
          format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | ONTOBOT | {message}",
          level="INFO", rotation="10 MB", compression="zip")

class OntoBotChannelCreator:
    """Создает канал OntoBot и запускает реальный бот."""
    
    def __init__(self):
        self.kittycore_url = "http://localhost:8085"
        self.bot_token = "7907324843:AAFjN2H4ud2X6rm7XShrmS3G1l1JnCo4feM"
        self.channel_id = "ontobot_main"
        self.scenario_id = "mr_ontobot_main_router"
        
        logger.info("🤖 OntoBot Channel Creator инициализирован")
    
    async def check_kittycore_health(self) -> bool:
        """Проверяет доступность KittyCore API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.kittycore_url}/health") as response:
                    if response.status == 200:
                        logger.info("✅ KittyCore API доступен")
                        return True
                    else:
                        logger.error(f"❌ KittyCore API недоступен: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к KittyCore: {e}")
            return False
    
    async def check_bot_token(self) -> dict:
        """Проверяет валидность токена бота."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
                async with session.get(url) as response:
                    result = await response.json()
                    
                    if result.get("ok"):
                        bot_info = result["result"]
                        logger.info(f"✅ Бот найден: @{bot_info.get('username')} ({bot_info.get('first_name')})")
                        return {"success": True, "bot_info": bot_info}
                    else:
                        logger.error(f"❌ Неверный токен бота: {result.get('description')}")
                        return {"success": False, "error": result.get('description')}
        except Exception as e:
            logger.error(f"❌ Ошибка проверки токена: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_channel(self) -> dict:
        """Создает канал OntoBot в KittyCore."""
        try:
            # Данные для создания канала
            channel_data = {
                "step": {
                    "type": "mongo_create_channel_mapping",
                    "params": {
                        "channel_id": self.channel_id,
                        "scenario_id": self.scenario_id,
                        "channel_type": "telegram",
                        "channel_config": {
                            "bot_token": self.bot_token,
                            "description": "OntoBot - диагностика мыслевирусов",
                            "created_by": "create_ontobot_channel.py"
                        },
                        "output_var": "channel_result"
                    }
                },
                "context": {
                    "created_at": datetime.now().isoformat(),
                    "creator": "ontobot_setup"
                }
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.kittycore_url}/api/v1/simple/execute"
                async with session.post(url, json=channel_data) as response:
                    result = await response.json()
                    
                    if result.get("success"):
                        logger.info(f"✅ Канал {self.channel_id} создан успешно")
                        return {"success": True, "result": result}
                    else:
                        logger.error(f"❌ Ошибка создания канала: {result.get('error')}")
                        return {"success": False, "error": result.get('error')}
                        
        except Exception as e:
            logger.error(f"❌ Исключение при создании канала: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_scenario_exists(self) -> bool:
        """Проверяет существование сценария в БД."""
        try:
            find_data = {
                "collection": "scenarios",
                "filter": {"scenario_id": self.scenario_id}
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.kittycore_url}/api/v1/simple/mongo/find"
                async with session.post(url, json=find_data) as response:
                    result = await response.json()
                    
                    if result.get("success") and result.get("data"):
                        logger.info(f"✅ Сценарий {self.scenario_id} найден в БД")
                        return True
                    else:
                        logger.warning(f"⚠️ Сценарий {self.scenario_id} не найден в БД")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Ошибка проверки сценария: {e}")
            return False
    
    async def start_user_scenario(self, user_id: str, chat_id: str, first_name: str = "Тестер") -> dict:
        """Запускает пользовательский сценарий."""
        try:
            # Данные для запуска сценария
            scenario_data = {
                "scenario_id": self.scenario_id,
                "context": {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "telegram_user_id": int(user_id),
                    "telegram_chat_id": int(chat_id),
                    "telegram_first_name": first_name,
                    "telegram_username": f"user_{user_id}",
                    "current_timestamp": datetime.now().isoformat(),
                    "test_mode": False,
                    "real_bot": True
                }
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.kittycore_url}/api/v1/simple/channels/{self.channel_id}/execute"
                async with session.post(url, json=scenario_data) as response:
                    result = await response.json()
                    
                    if result.get("success"):
                        logger.info(f"✅ Сценарий запущен для пользователя {user_id}")
                        return {"success": True, "result": result}
                    else:
                        logger.error(f"❌ Ошибка запуска сценария: {result.get('error')}")
                        return {"success": False, "error": result.get('error')}
                        
        except Exception as e:
            logger.error(f"❌ Исключение при запуске сценария: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_channel_info(self) -> dict:
        """Получает информацию о созданном канале."""
        try:
            find_data = {
                "collection": "channel_mappings",
                "filter": {"channel_id": self.channel_id}
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.kittycore_url}/api/v1/simple/mongo/find"
                async with session.post(url, json=find_data) as response:
                    result = await response.json()
                    
                    if result.get("success") and result.get("data"):
                        channel_info = result["data"][0]
                        logger.info(f"📋 Информация о канале получена")
                        return {"success": True, "channel": channel_info}
                    else:
                        logger.warning(f"⚠️ Канал {self.channel_id} не найден")
                        return {"success": False, "error": "Channel not found"}
                        
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о канале: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_test_message(self, chat_id: str, text: str = "🧪 Тестовое сообщение от OntoBot") -> dict:
        """Отправляет тестовое сообщение через Telegram API."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
                
                async with session.post(url, json=data) as response:
                    result = await response.json()
                    
                    if result.get("ok"):
                        message_id = result["result"]["message_id"]
                        logger.info(f"✅ Тестовое сообщение отправлено: ID {message_id}")
                        return {"success": True, "message_id": message_id}
                    else:
                        logger.error(f"❌ Ошибка отправки: {result.get('description')}")
                        return {"success": False, "error": result.get('description')}
                        
        except Exception as e:
            logger.error(f"❌ Исключение при отправке сообщения: {e}")
            return {"success": False, "error": str(e)}

async def main():
    """Главная функция для создания канала и запуска бота."""
    
    print("🤖 СОЗДАНИЕ КАНАЛА ONTOBOT И ЗАПУСК РЕАЛЬНОГО БОТА")
    print("="*60)
    
    creator = OntoBotChannelCreator()
    
    # 1. Проверяем доступность KittyCore
    print("\n🔍 Проверка KittyCore API...")
    if not await creator.check_kittycore_health():
        print("❌ KittyCore недоступен. Убедитесь, что сервер запущен на порту 8085")
        return
    
    # 2. Проверяем токен бота
    print("\n🤖 Проверка токена бота...")
    bot_check = await creator.check_bot_token()
    if not bot_check["success"]:
        print(f"❌ Проблема с токеном бота: {bot_check['error']}")
        return
    
    bot_info = bot_check["bot_info"]
    print(f"✅ Бот найден: @{bot_info.get('username')} ({bot_info.get('first_name')})")
    
    # 3. Проверяем существование сценария
    print(f"\n📋 Проверка сценария {creator.scenario_id}...")
    if not await creator.check_scenario_exists():
        print("⚠️ Сценарий не найден. Запустите load_scenarios.py для загрузки сценариев")
        load_choice = input("Хотите продолжить без проверки сценария? (y/n): ").strip().lower()
        if load_choice != 'y':
            return
    
    # 4. Создаем канал
    print(f"\n🔧 Создание канала {creator.channel_id}...")
    channel_result = await creator.create_channel()
    if not channel_result["success"]:
        print(f"❌ Ошибка создания канала: {channel_result['error']}")
        return
    
    # 5. Получаем информацию о канале
    print("\n📋 Получение информации о канале...")
    channel_info = await creator.get_channel_info()
    if channel_info["success"]:
        channel = channel_info["channel"]
        print(f"✅ Канал создан:")
        print(f"   - ID: {channel.get('channel_id')}")
        print(f"   - Тип: {channel.get('channel_type')}")
        print(f"   - Сценарий: {channel.get('scenario_id')}")
        print(f"   - Создан: {channel.get('created_at')}")
    
    # 6. Запрашиваем данные пользователя
    print("\n👤 Настройка тестового пользователя:")
    user_id = input("Введите user_id (или нажмите Enter для 123456789): ").strip() or "123456789"
    chat_id = input("Введите chat_id (или нажмите Enter для того же ID): ").strip() or user_id
    first_name = input("Введите имя пользователя (или нажмите Enter для 'Тестер'): ").strip() or "Тестер"
    
    # 7. Отправляем тестовое сообщение
    print(f"\n📤 Отправка тестового сообщения в чат {chat_id}...")
    test_msg = await creator.send_test_message(chat_id, f"🤖 Привет, {first_name}! OntoBot готов к работе!")
    if test_msg["success"]:
        print(f"✅ Тестовое сообщение отправлено (ID: {test_msg['message_id']})")
    else:
        print(f"⚠️ Не удалось отправить тестовое сообщение: {test_msg['error']}")
        print("Возможно, бот не имеет доступа к чату или чат не существует")
    
    # 8. Запускаем пользовательский сценарий
    print(f"\n🚀 Запуск сценария для пользователя {user_id}...")
    scenario_result = await creator.start_user_scenario(user_id, chat_id, first_name)
    
    if scenario_result["success"]:
        result = scenario_result["result"]
        print(f"✅ Сценарий запущен успешно!")
        print(f"   - Сценарий: {result.get('scenario_id')}")
        print(f"   - Финальный контекст: {len(str(result.get('final_context', {})))} символов")
        
        # Показываем финальный контекст
        final_context = result.get('final_context', {})
        if final_context:
            print(f"\n📊 Финальный контекст:")
            for key, value in final_context.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"   - {key}: {value[:100]}...")
                else:
                    print(f"   - {key}: {value}")
    else:
        print(f"❌ Ошибка запуска сценария: {scenario_result['error']}")
    
    # 9. Сохраняем результаты
    results = {
        "timestamp": datetime.now().isoformat(),
        "bot_info": bot_info,
        "channel_info": channel_info.get("channel") if channel_info["success"] else None,
        "test_message": test_msg,
        "scenario_result": scenario_result,
        "user_data": {
            "user_id": user_id,
            "chat_id": chat_id,
            "first_name": first_name
        }
    }
    
    with open("logs/ontobot_channel_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Результаты сохранены в logs/ontobot_channel_results.json")
    
    # 10. Инструкции для пользователя
    print(f"\n🎯 ИНСТРУКЦИИ ДЛЯ ТЕСТИРОВАНИЯ:")
    print(f"1. Откройте Telegram и найдите бота @{bot_info.get('username')}")
    print(f"2. Отправьте команду /start или любое сообщение")
    print(f"3. Бот должен запустить сценарий диагностики мыслевирусов")
    print(f"4. Следуйте инструкциям бота для прохождения диагностики")
    print(f"\n📋 Информация о канале:")
    print(f"   - Channel ID: {creator.channel_id}")
    print(f"   - Scenario ID: {creator.scenario_id}")
    print(f"   - Bot Token: {creator.bot_token[:20]}...")
    
    print(f"\n✅ Настройка завершена! OntoBot готов к работе! 🚀")

if __name__ == "__main__":
    asyncio.run(main()) 