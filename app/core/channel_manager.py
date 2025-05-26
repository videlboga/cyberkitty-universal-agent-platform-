"""
Channel Manager для Universal Agent Platform.
Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!

Управляет каналами:
1. Загружает каналы из БД при старте
2. Запускает поллинг для каждого канала
3. При событии запускает сценарий канала
4. Сценарии ТОЛЬКО из БД
"""

import asyncio
from typing import Dict, List, Optional
from loguru import logger

from app.core.simple_engine import SimpleScenarioEngine
from app.plugins.simple_telegram_plugin import SimpleTelegramPlugin


class ChannelManager:
    """
    Менеджер каналов для автоматического запуска поллинга и выполнения сценариев.
    
    Принципы:
    1. Каналы загружаются из БД при старте
    2. Для каждого канала создается свой Telegram плагин с поллингом
    3. При событии автоматически запускается сценарий канала из БД
    4. Никаких fallback сценариев - только БД
    """
    
    def __init__(self, engine: SimpleScenarioEngine):
        self.engine = engine
        self.channels: Dict[str, Dict] = {}  # channel_id -> channel_data
        self.telegram_plugins: Dict[str, SimpleTelegramPlugin] = {}  # channel_id -> plugin
        self.polling_tasks: Dict[str, asyncio.Task] = {}  # channel_id -> task
        
    async def initialize(self):
        """Инициализация менеджера каналов."""
        logger.info("🚀 Инициализация Channel Manager...")
        
        # Загружаем все каналы из БД
        await self._load_channels_from_db()
        
        # Запускаем поллинг для всех каналов
        await self._start_all_polling()
        
        logger.info(f"✅ Channel Manager инициализирован. Активных каналов: {len(self.channels)}")
        
    async def _load_channels_from_db(self):
        """Загружает все каналы из БД."""
        try:
            # Получаем все маппинги каналов
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
            result_context = await self.engine.execute_step(step, context)
            result = result_context.get("find_result", {})
            
            if result.get("success") and result.get("documents"):
                for channel_doc in result["documents"]:
                    channel_id = channel_doc.get("channel_id")
                    if channel_id:
                        self.channels[channel_id] = channel_doc
                        logger.info(f"📋 Загружен канал: {channel_id}")
                        
                logger.info(f"📋 Загружено каналов из БД: {len(self.channels)}")
            else:
                logger.warning("⚠️ Каналы в БД не найдены")
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки каналов из БД: {e}")
            
    async def _start_all_polling(self):
        """Запускает поллинг для всех каналов."""
        for channel_id, channel_data in self.channels.items():
            await self._start_channel_polling(channel_id, channel_data)
            
    async def _start_channel_polling(self, channel_id: str, channel_data: Dict):
        """Запускает поллинг для конкретного канала."""
        try:
            # Получаем токен из конфигурации канала
            channel_config = channel_data.get("channel_config", {})
            bot_token = channel_config.get("telegram_bot_token")
            
            if not bot_token:
                logger.warning(f"⚠️ Токен не найден для канала {channel_id}, пропускаю")
                return
                
            # Создаем Telegram плагин для канала
            telegram_plugin = SimpleTelegramPlugin(bot_token=bot_token, channel_id=channel_id)
            
            # Устанавливаем обработчики событий
            telegram_plugin.set_command_callback(
                lambda update, context: self._handle_channel_event(channel_id, "command", update, context)
            )
            telegram_plugin.set_message_callback(
                lambda update, context: self._handle_channel_event(channel_id, "message", update, context)
            )
            telegram_plugin.set_callback_query_callback(
                lambda update, context: self._handle_channel_event(channel_id, "callback_query", update, context)
            )
            
            # Инициализируем плагин
            await telegram_plugin._do_initialize()
            
            # Запускаем поллинг в фоновой задаче
            polling_task = asyncio.create_task(telegram_plugin.start_polling())
            
            # Сохраняем плагин и задачу
            self.telegram_plugins[channel_id] = telegram_plugin
            self.polling_tasks[channel_id] = polling_task
            
            logger.info(f"🚀 Поллинг запущен для канала {channel_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска поллинга для канала {channel_id}: {e}")
            
    async def _handle_channel_event(self, channel_id: str, event_type: str, update, context):
        """Обрабатывает событие канала - запускает сценарий из БД."""
        try:
            logger.info(f"📨 Событие {event_type} в канале {channel_id}")
            
            # Получаем данные канала
            channel_data = self.channels.get(channel_id)
            if not channel_data:
                logger.error(f"❌ Данные канала {channel_id} не найдены")
                return
                
            # Получаем scenario_id канала
            scenario_id = channel_data.get("scenario_id")
            if not scenario_id:
                logger.error(f"❌ Сценарий не указан для канала {channel_id}")
                return
                
            # Загружаем сценарий из БД
            scenario = await self._load_scenario_from_db(scenario_id)
            if not scenario:
                logger.error(f"❌ Сценарий {scenario_id} не найден в БД")
                return
                
            # Подготавливаем контекст из события
            event_context = self._extract_context_from_event(update, context, event_type)
            
            # Добавляем информацию о канале
            event_context.update({
                "channel_id": channel_id,
                "scenario_id": scenario_id,
                "event_type": event_type
            })
            
            # Выполняем сценарий
            logger.info(f"🎭 Запуск сценария {scenario_id} для канала {channel_id}")
            final_context = await self.engine.execute_scenario(scenario, event_context)
            
            logger.info(f"✅ Сценарий {scenario_id} выполнен для канала {channel_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки события {event_type} в канале {channel_id}: {e}")
            
    async def _load_scenario_from_db(self, scenario_id: str) -> Optional[Dict]:
        """Загружает сценарий из БД. ТОЛЬКО БД, никаких fallback!"""
        try:
            step = {
                "id": "get_scenario",
                "type": "mongo_get_scenario",
                "params": {
                    "scenario_id": scenario_id,
                    "output_var": "scenario_result"
                }
            }
            context = {}
            result_context = await self.engine.execute_step(step, context)
            
            if result_context.get("scenario_result", {}).get("success"):
                return result_context["scenario_result"]["scenario"]
            else:
                logger.error(f"❌ Сценарий {scenario_id} не найден в БД")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки сценария {scenario_id} из БД: {e}")
            return None
            
    def _extract_context_from_event(self, update, context, event_type: str) -> Dict:
        """Извлекает контекст из Telegram события."""
        event_context = {}
        
        if update.effective_user:
            event_context.update({
                "user_id": str(update.effective_user.id),
                "user_name": update.effective_user.username or update.effective_user.first_name,
                "telegram_user_id": update.effective_user.id,
                "telegram_username": update.effective_user.username,
                "telegram_first_name": update.effective_user.first_name,
                "telegram_last_name": update.effective_user.last_name,
            })
            
        if update.effective_chat:
            event_context.update({
                "chat_id": str(update.effective_chat.id),
                "telegram_chat_id": update.effective_chat.id,
            })
            
        if event_type == "command" and update.message:
            event_context.update({
                "command": update.message.text,
                "message_text": update.message.text,
            })
        elif event_type == "message" and update.message:
            event_context.update({
                "message_text": update.message.text,
            })
        elif event_type == "callback_query" and update.callback_query:
            event_context.update({
                "callback_data": update.callback_query.data,
                "message_id": update.callback_query.message.message_id if update.callback_query.message else None,
            })
            
        return event_context
        
    async def stop_all_polling(self):
        """Останавливает поллинг для всех каналов."""
        logger.info("🛑 Остановка всех каналов...")
        
        for channel_id, task in self.polling_tasks.items():
            try:
                task.cancel()
                await task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"❌ Ошибка остановки поллинга канала {channel_id}: {e}")
                
        for channel_id, plugin in self.telegram_plugins.items():
            try:
                await plugin.stop_polling()
            except Exception as e:
                logger.error(f"❌ Ошибка остановки плагина канала {channel_id}: {e}")
                
        logger.info("🛑 Все каналы остановлены")
        
    async def reload_channels(self):
        """Перезагружает каналы из БД."""
        logger.info("🔄 Перезагрузка каналов...")
        
        # Останавливаем текущие каналы
        await self.stop_all_polling()
        
        # Очищаем состояние
        self.channels.clear()
        self.telegram_plugins.clear()
        self.polling_tasks.clear()
        
        # Загружаем заново
        await self._load_channels_from_db()
        await self._start_all_polling()
        
        logger.info(f"🔄 Каналы перезагружены. Активных: {len(self.channels)}") 