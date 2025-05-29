"""
Channel Manager для Universal Agent Platform.
Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!

НОВАЯ АРХИТЕКТУРА:
1. ChannelManager - ОТДЕЛЬНЫЙ сервис
2. Каждый канал = ОТДЕЛЬНЫЙ экземпляр движка
3. Движок НЕ ЗНАЕТ о каналах
4. ChannelManager создает движки для каналов

САМОДОСТАТОЧНЫЙ - работает напрямую с API каналов!
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from loguru import logger


class ChannelManager:
    """
    САМОДОСТАТОЧНЫЙ менеджер каналов.
    
    НОВАЯ АРХИТЕКТУРА:
    1. Каждый канал = отдельный экземпляр движка
    2. Каналы ИЗОЛИРОВАНЫ друг от друга
    3. Движок НЕ ЗНАЕТ о каналах
    4. ChannelManager управляет жизненным циклом каналов
    """
    
    def __init__(self):
        # НЕ ПРИНИМАЕМ движок в конструкторе!
        # Создаем свои экземпляры для каждого канала
        self.channels: Dict[str, Dict] = {}  # channel_id -> channel_data
        self.channel_engines: Dict[str, Any] = {}  # channel_id -> engine
        self.telegram_sessions: Dict[str, aiohttp.ClientSession] = {}  # channel_id -> session
        self.polling_tasks: Dict[str, asyncio.Task] = {}  # channel_id -> task
        self.last_update_ids: Dict[str, int] = {}  # channel_id -> last_update_id
        
    async def initialize(self):
        """Инициализация менеджера каналов."""
        logger.info("🚀 Инициализация САМОДОСТАТОЧНОГО Channel Manager...")
        
        # Загружаем все каналы из БД
        await self._load_channels_from_db()
        
        # Создаем движки для каждого канала
        await self._create_channel_engines()
        
        # Запускаем поллинг для всех каналов
        await self._start_all_polling()
        
        logger.info(f"✅ САМОДОСТАТОЧНЫЙ Channel Manager инициализирован. Активных каналов: {len(self.channels)}")
        
    async def _load_channels_from_db(self):
        """Загружает все каналы из БД."""
        try:
            # Создаем временный движок для загрузки каналов из БД
            from app.core.simple_engine import create_engine
            temp_engine = await create_engine()
            
            # Получаем все маппинги каналов через MongoDB плагин
            step = {
                "id": "find_channels",
                "type": "mongo_find_documents",
                "params": {
                    "collection": "channel_mappings",
                    "filter": {},
                    "output_var": "find_result"
                }
            }
            context = {}
            result_context = await temp_engine.execute_step(step, context)
            result = result_context.get("find_result", {})
            
            if result.get("success") and result.get("documents"):
                for channel_doc in result["documents"]:
                    channel_id = channel_doc.get("channel_id")
                    if channel_id:
                        self.channels[channel_id] = channel_doc
                        logger.info(f"📋 Загружен канал: {channel_id} (тип: {channel_doc.get('channel_type', 'unknown')})")
                        
                logger.info(f"📋 Загружено каналов из БД: {len(self.channels)}")
            else:
                logger.warning("⚠️ Каналы в БД не найдены")
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки каналов из БД: {e}")
            
    async def _create_channel_engines(self):
        """Создает отдельный движок для каждого канала."""
        for channel_id, channel_data in self.channels.items():
            try:
                logger.info(f"🔧 Создаю движок для канала {channel_id}")
                
                # Создаем ОТДЕЛЬНЫЙ движок для канала
                from app.core.simple_engine import create_engine
                channel_engine = await create_engine()
                
                self.channel_engines[channel_id] = channel_engine
                
                logger.info(f"✅ Движок создан для канала {channel_id}")
                
            except Exception as e:
                logger.error(f"❌ Ошибка создания движка для канала {channel_id}: {e}")
                
    async def _start_all_polling(self):
        """Запускает поллинг для всех каналов."""
        for channel_id, channel_data in self.channels.items():
            await self._start_channel_polling(channel_id, channel_data)
            
    async def _start_channel_polling(self, channel_id: str, channel_data: Dict):
        """
        САМОДОСТАТОЧНЫЙ запуск поллинга для конкретного канала.
        
        НОВАЯ АРХИТЕКТУРА: токен напрямую из канала!
        """
        try:
            channel_type = channel_data.get("channel_type", "unknown")
            
            logger.info(f"🚀 Запуск поллинга для канала {channel_id} (тип: {channel_type})")
            
            if channel_type == "telegram":
                # НОВАЯ АРХИТЕКТУРА: передаем весь канал, а не пустые config/settings
                await self._start_telegram_polling_direct(channel_id, channel_data)
            else:
                logger.warning(f"⚠️ Неподдерживаемый тип канала: {channel_type}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска поллинга для канала {channel_id}: {e}")
    
    async def _start_telegram_polling_direct(self, channel_id: str, channel_data: Dict):
        """
        ПРЯМОЙ запуск Telegram поллинга через Bot API.
        
        БЕЗ ПЛАГИНОВ! БЕЗ УНИВЕРСАЛЬНЫХ ХЕНДЛЕРОВ!
        """
        try:
            # ОТЛАДКА: логируем все данные канала
            logger.info(f"🔍 ОТЛАДКА: Данные канала {channel_id}: {channel_data}")
            
            # НОВАЯ АРХИТЕКТУРА: токен берется напрямую из канала
            bot_token = channel_data.get("telegram_bot_token")
            
            logger.info(f"🔍 ОТЛАДКА: Найденный токен для {channel_id}: {bot_token}")
            
            if not bot_token:
                logger.warning(f"⚠️ Токен telegram_bot_token не найден для канала {channel_id}, пропускаю")
                return
            
            # Создаем HTTP сессию для канала
            session = aiohttp.ClientSession()
            self.telegram_sessions[channel_id] = session
            self.last_update_ids[channel_id] = 0
            
            # Запускаем поллинг в фоновой задаче
            polling_task = asyncio.create_task(
                self._telegram_polling_loop(channel_id, bot_token, session)
            )
            self.polling_tasks[channel_id] = polling_task
            
            logger.info(f"✅ Прямой Telegram поллинг запущен для канала {channel_id} с токеном {bot_token[:20]}...")
                
        except Exception as e:
            logger.error(f"❌ Ошибка _start_telegram_polling_direct для канала {channel_id}: {e}")
    
    async def _telegram_polling_loop(self, channel_id: str, bot_token: str, session: aiohttp.ClientSession):
        """
        Основной цикл поллинга Telegram Bot API.
        
        ПРЯМАЯ работа с API без плагинов!
        """
        base_url = f"https://api.telegram.org/bot{bot_token}"
        
        logger.info(f"🔄 Запуск цикла поллинга для канала {channel_id}")
        
        while True:
            try:
                # Получаем обновления
                params = {
                    "offset": self.last_update_ids[channel_id] + 1,
                    "timeout": 30,
                    "allowed_updates": ["message", "callback_query"]
                }
                
                async with session.get(f"{base_url}/getUpdates", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("ok") and data.get("result"):
                            for update in data["result"]:
                                # Обновляем last_update_id
                                self.last_update_ids[channel_id] = update["update_id"]
                                
                                # Обрабатываем обновление
                                await self._handle_telegram_update(channel_id, update)
                    else:
                        logger.error(f"❌ Ошибка HTTP {response.status} для канала {channel_id}")
                        await asyncio.sleep(5)
                        
            except asyncio.CancelledError:
                logger.info(f"⏹️ Поллинг остановлен для канала {channel_id}")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле поллинга канала {channel_id}: {e}")
                await asyncio.sleep(5)
    
    async def _handle_telegram_update(self, channel_id: str, update: Dict):
        """
        Обрабатывает Telegram обновление.
        
        ПРЯМАЯ обработка без плагинов!
        """
        try:
            logger.info(f"📨 Получено обновление в канале {channel_id}: {update.get('update_id')}")
            
            # Определяем тип события
            event_type = "unknown"
            event_data = {}
            
            if "message" in update:
                event_type = "message"
                message = update["message"]
                event_data = {
                    "user_id": str(message.get("from", {}).get("id", "")),
                    "chat_id": str(message.get("chat", {}).get("id", "")),
                    "message_text": message.get("text", ""),
                    "telegram_user_id": message.get("from", {}).get("id"),
                    "telegram_username": message.get("from", {}).get("username"),
                    "telegram_first_name": message.get("from", {}).get("first_name"),
                    "telegram_last_name": message.get("from", {}).get("last_name"),
                    "telegram_chat_id": message.get("chat", {}).get("id"),
                }
                
            elif "callback_query" in update:
                event_type = "callback_query"
                callback = update["callback_query"]
                event_data = {
                    "user_id": str(callback.get("from", {}).get("id", "")),
                    "chat_id": str(callback.get("message", {}).get("chat", {}).get("id", "")),
                    "callback_data": callback.get("data", ""),
                    "message_id": callback.get("message", {}).get("message_id"),
                    "telegram_user_id": callback.get("from", {}).get("id"),
                    "telegram_username": callback.get("from", {}).get("username"),
                    "telegram_first_name": callback.get("from", {}).get("first_name"),
                    "telegram_last_name": callback.get("from", {}).get("last_name"),
                    "telegram_chat_id": callback.get("message", {}).get("chat", {}).get("id"),
                }
            
            # Запускаем сценарий канала
            await self._execute_channel_scenario(channel_id, event_type, event_data)
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки обновления в канале {channel_id}: {e}")
    
    async def _execute_channel_scenario(self, channel_id: str, event_type: str, event_data: Dict):
        """
        Выполняет стартовый сценарий канала при событии.
        
        НОВАЯ АРХИТЕКТУРА: используется start_scenario_id!
        """
        try:
            # Получаем данные канала
            channel_data = self.channels.get(channel_id)
            if not channel_data:
                logger.error(f"❌ Данные канала {channel_id} не найдены")
                return
                
            # НОВАЯ АРХИТЕКТУРА: получаем start_scenario_id канала
            start_scenario_id = channel_data.get("start_scenario_id")
            if not start_scenario_id:
                logger.error(f"❌ Стартовый сценарий start_scenario_id не указан для канала {channel_id}")
                return
                
            # Подготавливаем контекст с данными Telegram
            context = {
                "channel_id": channel_id,
                "scenario_id": start_scenario_id,
                "event_type": event_type,
                "telegram_update": {
                    "message" if event_type == "message" else "callback_query": event_data
                },
                **event_data
            }
            
            # Выполняем стартовый сценарий НАПРЯМУЮ через движок
            logger.info(f"🎭 Запуск стартового сценария {start_scenario_id} для канала {channel_id}")
            final_context = await self.channel_engines[channel_id].execute_scenario(start_scenario_id, context)
            
            logger.info(f"✅ Стартовый сценарий {start_scenario_id} выполнен для канала {channel_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения стартового сценария для канала {channel_id}: {e}")
            
    async def stop_all_polling(self):
        """Останавливает поллинг для всех каналов."""
        logger.info("🛑 Остановка всех каналов...")
        
        # Останавливаем задачи поллинга
        for channel_id, task in self.polling_tasks.items():
            try:
                task.cancel()
                await task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"❌ Ошибка остановки поллинга канала {channel_id}: {e}")
        
        # Закрываем HTTP сессии
        for channel_id, session in self.telegram_sessions.items():
            try:
                await session.close()
            except Exception as e:
                logger.error(f"❌ Ошибка закрытия сессии канала {channel_id}: {e}")
                
        logger.info("🛑 Все каналы остановлены")
        
    async def reload_channels(self):
        """Перезагружает каналы из БД."""
        logger.info("🔄 Перезагрузка каналов...")
        
        # Останавливаем текущие каналы
        await self.stop_all_polling()
        
        # Очищаем состояние
        self.channels.clear()
        self.telegram_sessions.clear()
        self.polling_tasks.clear()
        self.last_update_ids.clear()
        
        # Загружаем заново
        await self._load_channels_from_db()
        await self._start_all_polling()
        
        logger.info(f"🔄 Каналы перезагружены. Активных: {len(self.channels)}")
        
    # ===== ПРЯМЫЕ МЕТОДЫ РАБОТЫ С TELEGRAM API =====
    
    async def send_message(self, channel_id: str, chat_id: str, text: str, **kwargs) -> Dict[str, Any]:
        """
        Прямая отправка сообщения через Telegram Bot API.
        
        НОВАЯ АРХИТЕКТУРА: токен берется из канала!
        """
        try:
            channel_data = self.channels.get(channel_id)
            if not channel_data:
                return {"success": False, "error": f"Channel {channel_id} not found"}
            
            # НОВАЯ АРХИТЕКТУРА: токен напрямую из канала
            bot_token = channel_data.get("telegram_bot_token")
            
            if not bot_token:
                return {"success": False, "error": f"Bot token not found for channel {channel_id}"}
            
            session = self.telegram_sessions.get(channel_id)
            if not session:
                return {"success": False, "error": f"Session not found for channel {channel_id}"}
            
            # Прямой вызов Telegram Bot API
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                **kwargs
            }
            
            async with session.post(url, json=data) as response:
                result = await response.json()
                
                if result.get("ok"):
                    logger.info(f"✅ Сообщение отправлено через канал {channel_id}")
                    return {"success": True, "result": result["result"]}
                else:
                    error_msg = result.get("description", "Unknown error")
                    logger.error(f"❌ Ошибка отправки сообщения: {error_msg}")
                    return {"success": False, "error": error_msg}
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения через канал {channel_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_buttons(self, channel_id: str, chat_id: str, text: str, buttons: List[List[Dict[str, str]]], **kwargs) -> Dict[str, Any]:
        """
        Прямая отправка сообщения с кнопками через Telegram Bot API.
        """
        reply_markup = {
            "inline_keyboard": buttons
        }
        
        return await self.send_message(
            channel_id=channel_id,
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            **kwargs
        )
    
    async def edit_message(self, channel_id: str, chat_id: str, message_id: int, text: str, **kwargs) -> Dict[str, Any]:
        """
        Прямое редактирование сообщения через Telegram Bot API.
        
        НОВАЯ АРХИТЕКТУРА: токен берется из канала!
        """
        try:
            channel_data = self.channels.get(channel_id)
            if not channel_data:
                return {"success": False, "error": f"Channel {channel_id} not found"}
            
            # НОВАЯ АРХИТЕКТУРА: токен напрямую из канала
            bot_token = channel_data.get("telegram_bot_token")
            
            if not bot_token:
                return {"success": False, "error": f"Bot token not found for channel {channel_id}"}
            
            session = self.telegram_sessions.get(channel_id)
            if not session:
                return {"success": False, "error": f"Session not found for channel {channel_id}"}
            
            # Прямой вызов Telegram Bot API
            url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
            data = {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                **kwargs
            }
            
            async with session.post(url, json=data) as response:
                result = await response.json()
                
                if result.get("ok"):
                    logger.info(f"✅ Сообщение отредактировано через канал {channel_id}")
                    return {"success": True, "result": result["result"]}
                else:
                    error_msg = result.get("description", "Unknown error")
                    logger.error(f"❌ Ошибка редактирования сообщения: {error_msg}")
                    return {"success": False, "error": error_msg}
            
        except Exception as e:
            logger.error(f"❌ Ошибка редактирования сообщения через канал {channel_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_active_channels(self) -> List[str]:
        """Возвращает список активных каналов"""
        return list(self.channels.keys())
    
    def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Возвращает информацию о канале"""
        return self.channels.get(channel_id)
    
    async def _load_specific_channel(self, channel_id: str):
        """Загружает конкретный канал из БД."""
        try:
            # Создаем временный движок для загрузки канала из БД
            from app.core.simple_engine import create_engine
            temp_engine = await create_engine()
            
            # Получаем конкретный канал через MongoDB плагин
            step = {
                "id": "find_channel",
                "type": "mongo_find_documents",
                "params": {
                    "collection": "channel_mappings",
                    "filter": {"channel_id": channel_id},
                    "output_var": "find_result"
                }
            }
            context = {}
            result_context = await temp_engine.execute_step(step, context)
            result = result_context.get("find_result", {})
            
            if result.get("success") and result.get("documents"):
                channel_doc = result["documents"][0]
                self.channels[channel_id] = channel_doc
                logger.info(f"📋 Загружен канал: {channel_id} (тип: {channel_doc.get('channel_type', 'unknown')})")
                return True
            else:
                logger.warning(f"⚠️ Канал {channel_id} не найден в БД")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки канала {channel_id} из БД: {e}")
            return False
            
    async def _create_channel_engine(self, channel_id: str):
        """Создает движок для конкретного канала."""
        try:
            if channel_id not in self.channels:
                logger.error(f"❌ Канал {channel_id} не загружен")
                return False
                
            logger.info(f"🔧 Создаю движок для канала {channel_id}")
            
            # Создаем ОТДЕЛЬНЫЙ движок для канала
            from app.core.simple_engine import create_engine
            channel_engine = await create_engine()
            
            self.channel_engines[channel_id] = channel_engine
            
            logger.info(f"✅ Движок создан для канала {channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания движка для канала {channel_id}: {e}")
            return False
            
    async def _stop_channel_polling(self, channel_id: str):
        """Останавливает поллинг для конкретного канала."""
        try:
            # Останавливаем задачу поллинга
            if channel_id in self.polling_tasks:
                task = self.polling_tasks[channel_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                del self.polling_tasks[channel_id]
                logger.info(f"⏹️ Поллинг остановлен для канала {channel_id}")
            
            # Закрываем HTTP сессию
            if channel_id in self.telegram_sessions:
                session = self.telegram_sessions[channel_id]
                await session.close()
                del self.telegram_sessions[channel_id]
                logger.info(f"🔌 Сессия закрыта для канала {channel_id}")
            
            # Удаляем из активных каналов
            if channel_id in self.channels:
                del self.channels[channel_id]
            
            if channel_id in self.channel_engines:
                del self.channel_engines[channel_id]
                
            if channel_id in self.last_update_ids:
                del self.last_update_ids[channel_id]
                
            logger.info(f"✅ Канал {channel_id} полностью остановлен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки канала {channel_id}: {e}") 