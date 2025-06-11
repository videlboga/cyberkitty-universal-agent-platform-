"""
Channel Manager для Universal Agent Platform.
Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!

НОВАЯ АРХИТЕКТУРА:
1. ChannelManager - ОТДЕЛЬНЫЙ сервис
2. ОДИН ГЛОБАЛЬНЫЙ движок для ВСЕХ каналов
3. Каналы делят один настроенный движок
4. ChannelManager управляет жизненным циклом каналов

САМОДОСТАТОЧНЫЙ - работает напрямую с API каналов!
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional, Any
from loguru import logger
import traceback
import uuid


class ChannelManager:
    """
    САМОДОСТАТОЧНЫЙ менеджер каналов.
    
    НОВАЯ АРХИТЕКТУРА:
    1. ОДИН ГЛОБАЛЬНЫЙ движок для ВСЕХ каналов
    2. Каналы SHARED ресурсы
    3. Масштабируемость до тысяч каналов
    4. ChannelManager управляет жизненным циклом каналов
    """
    
    def __init__(self, global_engine=None):
        # ПРИНИМАЕМ глобальный движок!
        self.global_engine = global_engine
        self.channels: Dict[str, Dict] = {}  # channel_id -> channel_data
        self.telegram_sessions: Dict[str, aiohttp.ClientSession] = {}  # channel_id -> session
        self.polling_tasks: Dict[str, asyncio.Task] = {}  # channel_id -> task
        self.last_update_ids: Dict[str, int] = {}  # channel_id -> last_update_id
        
    async def initialize(self):
        """Инициализация менеджера каналов."""
        logger.info("🚀 Инициализация МАСШТАБИРУЕМОГО Channel Manager...")
        
        # Убеждаемся что у нас есть глобальный движок
        if not self.global_engine:
            logger.error("❌ Глобальный движок не передан в ChannelManager!")
            raise RuntimeError("Global engine required for ChannelManager")
        
        # Загружаем все каналы из БД
        await self._load_channels_from_db()
        
        # Запускаем поллинг для всех каналов (БЕЗ создания новых движков!)
        await self._start_all_polling()
        
        logger.info(f"✅ МАСШТАБИРУЕМЫЙ Channel Manager инициализирован. Активных каналов: {len(self.channels)}")
        
    async def _load_channels_from_db(self):
        """Загружает все каналы из БД используя ГЛОБАЛЬНЫЙ движок."""
        try:
            # ИСПРАВЛЕНИЕ: Используем ГЛОБАЛЬНЫЙ движок
            if not self.global_engine:
                logger.error("❌ Глобальный движок недоступен для загрузки каналов")
                return
            
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
            result_context = await self.global_engine.execute_step(step, context)
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
        
        # ИСПРАВЛЕНИЕ: Проверяем наличие channel_id в last_update_ids
        if channel_id not in self.last_update_ids:
            self.last_update_ids[channel_id] = 0
            logger.info(f"🔧 Инициализирован last_update_id для канала {channel_id}")
        
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
                                await self._handle_telegram_update(update, channel_id)
                    else:
                        logger.error(f"❌ Ошибка HTTP {response.status} для канала {channel_id}")
                        await asyncio.sleep(5)
                        
            except asyncio.CancelledError:
                logger.info(f"⏹️ Поллинг остановлен для канала {channel_id}")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле поллинга канала {channel_id}: {e}")
                logger.error(f"🔍 ТРАССИРОВКА: {traceback.format_exc()}")
                await asyncio.sleep(5)
    
    async def _handle_telegram_update(self, update: Dict[str, Any], channel_id: str) -> None:
        """Обрабатывает входящее обновление от Telegram"""
        try:
            logger.info(f"🔍 DEBUG LINE 196: Начало обработки обновления для канала {channel_id}")
            update_id = update.get("update_id", "unknown")
            logger.info(f"🔍 DEBUG LINE 198: update_id = {update_id}")
            logger.info(f"📨 Получено обновление в канале {channel_id}: {update_id}")
            
            # КРИТИЧЕСКАЯ ОТЛАДКА: Логируем полную структуру обновления
            logger.info(f"🔍 ПОЛНАЯ СТРУКТУРА UPDATE: {update}")
            
            # Определяем тип события
            event_type = "unknown"
            event_data = {}
            logger.info(f"🔍 DEBUG LINE 207: Определяем тип события")
            
            if "message" in update:
                logger.info(f"🔍 DEBUG LINE 210: Обрабатываем message")
                event_type = "message"
                message = update["message"]
                
                # ОТЛАДКА: Логируем структуру сообщения
                logger.info(f"🔍 ПОЛНАЯ СТРУКТУРА MESSAGE: {message}")
                
                # Обработка контакта
                contact_data = None
                logger.info(f"🔍 DEBUG LINE 219: Проверяем наличие контакта")
                if "contact" in message:
                    logger.info(f"🔍 DEBUG LINE 221: Найден контакт")
                    contact = message["contact"]
                    contact_data = {
                        "phone_number": contact.get("phone_number"),
                        "first_name": contact.get("first_name"),
                        "last_name": contact.get("last_name"),
                        "user_id": contact.get("user_id")
                    }
                    logger.info(f"📞 Получен контакт: {contact_data}")
                else:
                    logger.info(f"🔍 Поле 'contact' НЕ НАЙДЕНО в сообщении. Доступные поля: {list(message.keys())}")
                
                logger.info(f"🔍 DEBUG LINE 233: Создаём event_data")
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
                
                # Добавляем данные контакта если есть
                logger.info(f"🔍 DEBUG LINE 245: Добавляем контакт если есть")
                if contact_data:
                    event_data["contact"] = contact_data
            
            elif "callback_query" in update:
                logger.info(f"🔍 DEBUG LINE 250: Обрабатываем callback_query")
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
            logger.info(f"🔍 DEBUG LINE 264: Вызываем _execute_channel_scenario")
            await self._execute_channel_scenario(channel_id, event_type, event_data)
            logger.info(f"🔍 DEBUG LINE 266: _execute_channel_scenario завершён")
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки обновления в канале {channel_id}: {e}")
            logger.error(f"🔍 DEBUG: Трассировка ошибки: {traceback.format_exc()}")
            logger.error(f"🔍 DEBUG: Полная трассировка: {traceback.format_exc()}")
    
    async def _execute_channel_scenario(self, channel_id: str, event_type: str, event_data: Dict):
        """
        Выполняет сценарий канала при событии.
        
        УЛУЧШЕННАЯ АРХИТЕКТУРА: проверяет сохраненное состояние пользователя!
        """
        try:
            # Получаем данные канала
            channel_data = self.channels.get(channel_id)
            if not channel_data:
                logger.error(f"❌ Данные канала {channel_id} не найдены")
                return
                
            user_id = event_data.get("user_id")
            chat_id = event_data.get("chat_id")
            
            if not user_id or not chat_id:
                logger.error(f"❌ Не удалось извлечь user_id или chat_id из события")
                return
            
            # НОВАЯ ЛОГИКА: Проверяем команду /start для сброса состояния
            message_text = event_data.get("message_text", "")
            if event_type == "message" and message_text.strip() == "/start":
                logger.info(f"🔄 Получена команда /start от пользователя {user_id} - сбрасываю состояние")
                await self._reset_user_state(channel_id, user_id)
                # Запускаем стартовый сценарий как для нового пользователя
                start_scenario_id = channel_data.get("start_scenario_id")
                if not start_scenario_id:
                    logger.error(f"❌ Стартовый сценарий start_scenario_id не указан для канала {channel_id}")
                    return
                    
                logger.info(f"🎭 Запуск стартового сценария {start_scenario_id} после команды /start для пользователя {user_id}")
                await self._start_new_user_scenario(channel_id, event_type, event_data, start_scenario_id)
                return
            
            # ИСПРАВЛЕННАЯ ЛОГИКА: Проверяем сохраненное состояние пользователя
            saved_state = await self._load_user_state(channel_id, user_id)
            
            if saved_state:
                # ЕСТЬ сохраненное состояние - продолжаем сценарий
                logger.info(f"🔄 Продолжаю сценарий для пользователя {user_id} с шага {saved_state.get('current_step')}")
                await self._continue_user_scenario(channel_id, event_type, event_data, saved_state)
            else:
                # Новый пользователь - запускаем стартовый сценарий
                start_scenario_id = channel_data.get("start_scenario_id")
                if not start_scenario_id:
                    logger.error(f"❌ Стартовый сценарий start_scenario_id не указан для канала {channel_id}")
                    return
                    
                logger.info(f"🎭 Запуск стартового сценария {start_scenario_id} для нового пользователя {user_id}")
                await self._start_new_user_scenario(channel_id, event_type, event_data, start_scenario_id)
                
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения сценария канала {channel_id}: {e}")
    
    async def _load_user_state(self, channel_id: str, user_id: str) -> Optional[Dict]:
        """Загружает сохраненное состояние пользователя."""
        try:
            # ИСПРАВЛЕНИЕ: Используем существующий движок канала!
            if not self.global_engine:
                logger.error("❌ Глобальный движок недоступен для загрузки состояния пользователя")
                return None
            
            # Ищем сохраненное состояние пользователя
            step = {
                "id": "load_user_state",
                "type": "mongo_find_documents",
                "params": {
                    "collection": "user_states",
                    "filter": {
                        "channel_id": channel_id,
                        "user_id": user_id
                    },
                    "output_var": "find_result"
                }
            }
            
            context = {}
            result_context = await self.global_engine.execute_step(step, context)
            result = result_context.get("find_result", {})
            
            if result.get("success") and result.get("documents"):
                user_state = result["documents"][0]
                logger.info(f"📋 Загружено состояние пользователя {user_id}: сценарий {user_state.get('scenario_id')}, шаг {user_state.get('current_step')}")
                return user_state
            else:
                logger.info(f"📋 Состояние пользователя {user_id} не найдено - новый пользователь")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки состояния пользователя {user_id}: {e}")
            return None
    
    async def _save_user_state(self, channel_id: str, user_id: str, context: Dict):
        """Сохраняет состояние пользователя."""
        try:
            # ИСПРАВЛЕНИЕ: Используем существующий движок канала!
            if not self.global_engine:
                logger.error("❌ Глобальный движок недоступен для сохранения состояния пользователя")
                return
            
            # Подготавливаем данные для сохранения
            state_data = {
                "channel_id": channel_id,
                "user_id": user_id,
                "scenario_id": context.get("scenario_id"),
                "current_step": context.get("current_step"),
                "waiting_for_input": context.get("waiting_for_input", False),
                "input_step_id": context.get("input_step_id"),
                "context": context,
                "updated_at": "2024-12-29T16:00:00Z"
            }
            
            # Сохраняем состояние (upsert)
            step = {
                "id": "save_user_state",
                "type": "mongo_upsert_document",
                "params": {
                    "collection": "user_states",
                    "filter": {
                        "channel_id": channel_id,
                        "user_id": user_id
                    },
                    "document": state_data,
                    "output_var": "save_result"
                }
            }
            
            save_context = {}
            await self.global_engine.execute_step(step, save_context)
            
            logger.info(f"💾 Состояние пользователя {user_id} сохранено: сценарий {state_data['scenario_id']}, шаг {state_data['current_step']}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения состояния пользователя {user_id}: {e}")
    
    async def _continue_user_scenario(self, channel_id: str, event_type: str, event_data: Dict, saved_state: Dict):
        """
        УПРОЩЕННАЯ логика продолжения сценария.
        
        ПРИНЦИП: Минимум логики в ChannelManager, максимум в SimpleScenarioEngine!
        """
        try:
            user_id = event_data.get("user_id")
            
            # Восстанавливаем контекст из сохраненного состояния
            context = saved_state.get("context", {})
            
            # 🔍 ОТЛАДОЧНОЕ ЛОГИРОВАНИЕ
            logger.info(f"🔍 EVENT_TYPE: {event_type}")
            logger.info(f"🔍 EVENT_DATA: {event_data}")
            logger.info(f"🔍 SAVED_STATE waiting_for_input: {saved_state.get('waiting_for_input')}")
            
            # Добавляем новые данные события
            context.update({
                "channel_id": channel_id,
                "event_type": event_type,
                "telegram_update": {
                    "message" if event_type == "message" else "callback_query": event_data
                },
                **event_data
            })
            
            # ИСПРАВЛЕНИЕ: ВСЕГДА обновляем callback_data при callback_query
            if event_type == "callback_query":
                context["callback_data"] = event_data.get("callback_data", "")
                logger.info(f"🔍 ВСЕГДА ОБНОВЛЯЮ callback_data: {context['callback_data']}")
            
            scenario_id = saved_state.get("scenario_id")
            current_step_id = saved_state.get("current_step")
            
            logger.info(f"🔄 Продолжаю сценарий {scenario_id} с шага {current_step_id} для пользователя {user_id}")
            
            # УПРОЩЕНИЕ: Убираем флаг ожидания ввода и передаем данные
            if saved_state.get("waiting_for_input"):
                if event_type == "message":
                    context["user_input"] = event_data.get("message_text", "")
                    context["message_text"] = event_data.get("message_text", "")
                    # КРИТИЧНО: ВСЕГДА извлекаем контакт в корневой контекст для template_resolver
                    telegram_message = context.get("telegram_update", {}).get("message", {})
                    if "contact" in telegram_message:
                        context["contact"] = telegram_message["contact"]
                        logger.info(f"📞 ИСПРАВЛЕНО: Извлёк контакт в корневой контекст из telegram_update: {telegram_message['contact']}")
                elif event_type == "callback_query":
                    # callback_data уже обновлен выше
                    logger.info(f"🔍 callback_data уже обновлен для waiting_for_input")
                
                context["waiting_for_input"] = False
                context.pop("input_step_id", None)
            
            # УПРОЩЕННАЯ ЛОГИКА: Просто передаем текущий шаг SimpleScenarioEngine
            # Он сам разберется что делать с input/branch/switch_scenario шагами
            context["current_step"] = current_step_id
            context["execution_started"] = True
            
            logger.info(f"📍 Передаю управление SimpleScenarioEngine с шагом: {current_step_id}")
            
            # SimpleScenarioEngine сам решит что делать дальше
            final_context = await self.global_engine.execute_scenario(scenario_id, context)
            
            # Сохраняем обновленное состояние
            await self._save_user_state(channel_id, user_id, final_context)
            
            logger.info(f"✅ Сценарий {scenario_id} продолжен для пользователя {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка продолжения сценария для пользователя {event_data.get('user_id')}: {e}")
    
    async def _start_new_user_scenario(self, channel_id: str, event_type: str, event_data: Dict, start_scenario_id: str):
        """Запускает стартовый сценарий для нового пользователя."""
        try:
            user_id = event_data.get("user_id")
            
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
            
            # КРИТИЧНО: Добавляем контакт в корневой контекст если есть
            telegram_message = context.get("telegram_update", {}).get("message", {})
            if "contact" in telegram_message:
                context["contact"] = telegram_message["contact"]
                logger.info(f"📞 ИСПРАВЛЕНО: Добавил контакт в корневой контекст для нового пользователя из telegram_update: {telegram_message['contact']}")
            
            # Выполняем стартовый сценарий
            final_context = await self.global_engine.execute_scenario(start_scenario_id, context)
            
            # КРИТИЧНО: Всегда сохраняем состояние после выполнения
            if final_context.get("waiting_for_input"):
                logger.info(f"💾 Пользователь {user_id} ждет ввода - сохраняю состояние")
            else:
                logger.info(f"💾 Сценарий завершен для пользователя {user_id} - сохраняю состояние")
            
            await self._save_user_state(channel_id, user_id, final_context)
            
            logger.info(f"✅ Стартовый сценарий {start_scenario_id} выполнен для нового пользователя {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска стартового сценария для пользователя {event_data.get('user_id')}: {e}")
    
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
        Отправляет текстовое сообщение через канал.
        АВТОМАТИЧЕСКИ форматирует разметку и добавляет паузы.
        ПРИНУДИТЕЛЬНО применяет HTML разметку!
        
        Args:
            channel_id: ID канала
            chat_id: ID чата
            text: Текст сообщения
            **kwargs: Дополнительные параметры
        """
        try:
            # ПРИНУДИТЕЛЬНАЯ HTML РАЗМЕТКА - НЕ ЗАВИСИТ ОТ ПАРАМЕТРОВ!
            kwargs["parse_mode"] = "HTML"
            text = self.format_telegram_text(text, "HTML")
            
            # Автоматическая пауза если не указана
            delay_seconds = kwargs.pop("delay_seconds", 1.0)
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)
                logger.info(f"⏰ Пауза {delay_seconds}с перед отправкой сообщения")
            
            channel_data = self.channels.get(channel_id)
            if not channel_data:
                logger.error(f"❌ Канал {channel_id} не найден")
                return {"success": False, "error": f"Канал {channel_id} не найден"}
                
            bot_token = channel_data.get("telegram_bot_token")
            if not bot_token:
                logger.error(f"❌ Токен для канала {channel_id} не найден")
                return {"success": False, "error": f"Токен для канала {channel_id} не найден"}
            
            session = self.telegram_sessions.get(channel_id)
            if not session:
                logger.error(f"❌ Сессия для канала {channel_id} не найдена")
                return {"success": False, "error": f"Сессия для канала {channel_id} не найдена"}
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"  # ПРИНУДИТЕЛЬНО!
            }
            
            # Добавляем дополнительные параметры
            data.update(kwargs)
            # Еще раз убеждаемся что parse_mode HTML
            data["parse_mode"] = "HTML"
            
            logger.info(f"📤 Отправляю сообщение с HTML разметкой в канал {channel_id}: {text[:100]}...")
            
            async with session.post(url, json=data) as response:
                result = await response.json()
                
                if result.get("ok"):
                    logger.info(f"✅ Сообщение отправлено через канал {channel_id} с HTML разметкой")
                    return {"success": True, "result": result["result"]}
                else:
                    error_msg = result.get("description", "Неизвестная ошибка")
                    logger.error(f"❌ Ошибка отправки сообщения: {error_msg}")
                    logger.error(f"🔍 Данные запроса: {data}")
                    return {"success": False, "error": error_msg}
                    
        except Exception as e:
            logger.error(f"❌ Исключение в send_message: {e}")
            logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}

    async def send_buttons(self, channel_id: str, chat_id: str, text: str, buttons: List[List[Dict[str, str]]], **kwargs) -> Dict[str, Any]:
        """
        Отправляет сообщение с inline кнопками.
        Автоматически форматирует разметку и добавляет паузы.
        """
        try:
            # ПРИНУДИТЕЛЬНО устанавливаем HTML разметку
            kwargs["parse_mode"] = "HTML"
            text = self.format_telegram_text(text, "HTML")
            
            # Автоматическая пауза если не указана
            delay_seconds = kwargs.pop("delay_seconds", 1.2)
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)
                logger.info(f"⏰ Пауза {delay_seconds}с перед отправкой кнопок")
            
            channel_data = self.channels.get(channel_id)
            if not channel_data:
                return {"success": False, "error": f"Channel {channel_id} not found"}

            bot_token = channel_data.get("telegram_bot_token")
            if not bot_token:
                return {"success": False, "error": f"Bot token not found for channel {channel_id}"}

            session = self.telegram_sessions.get(channel_id)
            if not session:
                return {"success": False, "error": f"Session not found for channel {channel_id}"}

            # Формируем inline клавиатуру
            inline_keyboard = {
                "inline_keyboard": buttons
            }

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "reply_markup": inline_keyboard
            }
            
            # Добавляем дополнительные параметры
            data.update(kwargs)
            
            logger.info(f"📤 Отправляю кнопки с parse_mode={data.get('parse_mode')}")

            async with session.post(url, json=data) as response:
                result = await response.json()

                if result.get("ok"):
                    logger.info(f"✅ Сообщение с кнопками отправлено через канал {channel_id} с паузой {delay_seconds}с (HTML разметка)")
                    return {"success": True, "result": result["result"]}
                else:
                    error_msg = result.get("description", "Unknown error")
                    logger.error(f"❌ Ошибка отправки сообщения с кнопками: {error_msg}")
                    return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения с кнопками через канал {channel_id}: {e}")
            return {"success": False, "error": str(e)}
    
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

    async def send_document(self, channel_id: str, chat_id: str, document_path: str, caption: str = None, **kwargs) -> Dict[str, Any]:
        """
        Прямая отправка документа через Telegram Bot API.
        
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
            
            # Проверяем существование файла
            if not os.path.exists(document_path):
                return {"success": False, "error": f"File not found: {document_path}"}
            
            # Прямой вызов Telegram Bot API
            url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
            
            # Подготавливаем данные для multipart/form-data
            data = aiohttp.FormData()
            data.add_field('chat_id', chat_id)
            
            if caption:
                data.add_field('caption', caption)
            
            # Добавляем дополнительные параметры
            for key, value in kwargs.items():
                if key not in ['chat_id', 'caption']:
                    data.add_field(key, str(value))
            
            # Добавляем файл
            filename = os.path.basename(document_path)
            with open(document_path, 'rb') as file:
                data.add_field('document', file, filename=filename)
                
                async with session.post(url, data=data) as response:
                    result = await response.json()
                    
                    if result.get("ok"):
                        logger.info(f"✅ Документ отправлен через канал {channel_id}: {filename}")
                        return {"success": True, "result": result["result"]}
                    else:
                        error_msg = result.get("description", "Unknown error")
                        logger.error(f"❌ Ошибка отправки документа: {error_msg}")
                        return {"success": False, "error": error_msg}
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки документа через канал {channel_id}: {e}")
            return {"success": False, "error": str(e)}

    async def forward_message(self, channel_id: str, chat_id: str, from_chat_id: str, message_id: int, **kwargs) -> Dict[str, Any]:
        """
        Прямая пересылка сообщения через Telegram Bot API.
        
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
            url = f"https://api.telegram.org/bot{bot_token}/forwardMessage"
            data = {
                "chat_id": chat_id,
                "from_chat_id": from_chat_id,
                "message_id": message_id,
                **kwargs
            }
            
            async with session.post(url, json=data) as response:
                result = await response.json()
                
                if result.get("ok"):
                    logger.info(f"✅ Сообщение переслано через канал {channel_id}")
                    return {"success": True, "result": result["result"]}
                else:
                    error_msg = result.get("description", "Unknown error")
                    logger.error(f"❌ Ошибка пересылки сообщения: {error_msg}")
                    return {"success": False, "error": error_msg}
            
        except Exception as e:
            logger.error(f"❌ Ошибка пересылки сообщения через канал {channel_id}: {e}")
            return {"success": False, "error": str(e)}

    async def copy_message(self, channel_id: str, chat_id: str, from_chat_id: str, message_id: int, hide_sender: bool = True, remove_caption: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Копирует сообщение со скрытой подписью отправителя.
        Автоматически добавляет паузы для естественного ритма.
        
        Это альтернатива forward_message, которая скрывает информацию об отправителе.
        Идеально для пересылки видео из каналов БЕЗ подписи под видео.
        
        Args:
            remove_caption: Если True, убирает caption (подпись под видео)
        """
        try:
            # Автоматическая пауза если не указана
            delay_seconds = kwargs.pop("delay_seconds", 1.0)
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)
                logger.info(f"⏰ Пауза {delay_seconds}с перед копированием сообщения")
            
            channel_data = self.channels.get(channel_id)
            if not channel_data:
                logger.error(f"❌ Канал {channel_id} не найден")
                return {"success": False, "error": f"Канал {channel_id} не найден"}
                
            bot_token = channel_data.get("telegram_bot_token")
            if not bot_token:
                logger.error(f"❌ Токен для канала {channel_id} не найден")
                return {"success": False, "error": f"Токен для канала {channel_id} не найден"}
            
            # НОВАЯ ЛОГИКА: Убираем caption если требуется
            if remove_caption:
                kwargs.pop("caption", None)  # Убираем если передан
                # Для API нужно явно указать что caption не нужен
                
            # Формируем данные запроса
            payload = {
                "chat_id": chat_id,
                "from_chat_id": from_chat_id,
                "message_id": message_id,
                **kwargs
            }
            
            # УБИРАЕМ CAPTION если нужно
            if remove_caption:
                payload.pop("caption", None)
                # В copyMessage API нет параметра для явного удаления caption
                # Но можно использовать пустую строку
                
            url = f"https://api.telegram.org/bot{bot_token}/copyMessage"
            
            logger.info(f"📋 Копирую сообщение {message_id} из {from_chat_id} в {chat_id} {'БЕЗ подписи' if remove_caption else 'с подписью'}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("ok"):
                            message_result = result.get("result", {})
                            logger.info(f"✅ Сообщение скопировано успешно {'без подписи' if remove_caption else ''}")
                            return {"success": True, "result": message_result}
                        else:
                            error_msg = result.get("description", "Неизвестная ошибка")
                            logger.error(f"❌ Ошибка копирования сообщения: {error_msg}")
                            return {"success": False, "error": error_msg}
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Ошибка HTTP {response.status}: {error_text}")
                        return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                        
        except Exception as e:
            logger.error(f"❌ Исключение в copy_message: {e}")
            return {"success": False, "error": str(e)}

    async def send_message_with_delay(self, channel_id: str, chat_id: str, text: str, delay_seconds: float = 1.5, **kwargs) -> Dict[str, Any]:
        """
        Отправляет сообщение с задержкой для создания естественного ритма общения.
        
        Args:
            delay_seconds: Задержка в секундах перед отправкой сообщения
        """
        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)
            
        return await self.send_message(channel_id, chat_id, text, **kwargs)

    async def send_buttons_with_delay(self, channel_id: str, chat_id: str, text: str, buttons: List[List[Dict[str, str]]], delay_seconds: float = 1.5, **kwargs) -> Dict[str, Any]:
        """
        Отправляет сообщение с кнопками с задержкой.
        """
        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)
            
        return await self.send_buttons(channel_id, chat_id, text, buttons, **kwargs)

    async def copy_message_with_delay(self, channel_id: str, chat_id: str, from_chat_id: str, message_id: int, delay_seconds: float = 1.5, **kwargs) -> Dict[str, Any]:
        """
        Копирует сообщение с задержкой и скрытой подписью отправителя.
        Идеально для пересылки видео без подписи автора.
        """
        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)
            
        return await self.copy_message(channel_id, chat_id, from_chat_id, message_id, **kwargs)

    def format_telegram_text(self, text: str, format_type: str = "HTML") -> str:
        """
        Форматирует текст для Telegram с корректной разметкой.
        
        Args:
            text: Исходный текст с псевдо-Markdown
            format_type: Тип разметки (HTML, MarkdownV2, Markdown)
        """
        if format_type == "HTML":
            # Просто конвертируем Markdown в HTML
            # Telegram API корректно обрабатывает правильную HTML разметку
            text = self._convert_markdown_to_html(text)
            return text
        elif format_type == "MarkdownV2":
            # Для MarkdownV2 экранируем специальные символы кроме тех что используем
            text = self._escape_markdownv2(text)
            return text
        else:
            return text
    
    def _convert_markdown_to_html(self, text: str) -> str:
        """Конвертирует простой Markdown в HTML для Telegram"""
        import re
        # [text](url) -> <a href="url">text</a>
        text = re.sub(r'\[([^\]]+?)\]\(([^\)]+?)\)', r'<a href="\2">\1</a>', text)
        # **жирный** -> <b>жирный</b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # *курсив* -> <i>курсив</i> (но только если не двойная звездочка)
        text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
        # `код` -> <code>код</code>
        text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
        return text
    
    def _escape_markdownv2(self, text: str) -> str:
        """Правильно экранирует текст для MarkdownV2"""
        # Список символов для экранирования в MarkdownV2
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text

    async def send_video_with_caption(self, channel_id: str, chat_id: str, video_file_id: str, caption: str = None, delay_seconds: float = 1.5, **kwargs) -> Dict[str, Any]:
        """
        Отправляет видео с подписью и задержкой.
        
        Args:
            video_file_id: File ID видео в Telegram
            caption: Подпись к видео
            delay_seconds: Задержка перед отправкой
        """
        try:
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

            channel_data = self.channels.get(channel_id)
            if not channel_data:
                return {"success": False, "error": f"Channel {channel_id} not found"}

            bot_token = channel_data.get("telegram_bot_token")
            if not bot_token:
                return {"success": False, "error": f"Bot token not found for channel {channel_id}"}

            session = self.telegram_sessions.get(channel_id)
            if not session:
                return {"success": False, "error": f"Session not found for channel {channel_id}"}

            url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
            data = {
                "chat_id": chat_id,
                "video": video_file_id,
            }
            
            if caption:
                data["caption"] = caption
                
            # Добавляем дополнительные параметры
            data.update(kwargs)

            async with session.post(url, json=data) as response:
                result = await response.json()

                if result.get("ok"):
                    logger.info(f"✅ Видео отправлено через канал {channel_id}")
                    return {"success": True, "result": result["result"]}
                else:
                    error_msg = result.get("description", "Unknown error")
                    logger.error(f"❌ Ошибка отправки видео: {error_msg}")
                    return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"❌ Ошибка отправки видео через канал {channel_id}: {e}")
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
            if not self.global_engine:
                logger.error("❌ Глобальный движок недоступен для загрузки канала")
                return False
            
            # Получаем конкретный канал через MongoDB плагин
            step = {
                "id": "find_channel",
                "type": "mongo_find_documents",
                "params": {
                    "collection": "channels",
                    "filter": {"channel_id": channel_id},
                    "output_var": "find_result"
                }
            }
            context = {}
            result_context = await self.global_engine.execute_step(step, context)
            result = result_context.get("find_result", {})
            
            if result.get("success") and result.get("documents"):
                channel_doc = result["documents"][0]
                self.channels[channel_id] = channel_doc
                
                # НОВИНКА: Создаем HTTP сессию для Telegram каналов (для channel_action)
                if channel_doc.get("channel_type") == "telegram" and channel_doc.get("telegram_bot_token"):
                    if channel_id not in self.telegram_sessions:
                        session = aiohttp.ClientSession()
                        self.telegram_sessions[channel_id] = session
                        logger.info(f"🔌 HTTP сессия создана для канала {channel_id}")
                
                logger.info(f"📋 Загружен канал: {channel_id} (тип: {channel_doc.get('channel_type', 'unknown')})")
                return True
            else:
                logger.warning(f"⚠️ Канал {channel_id} не найден в БД")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки канала {channel_id} из БД: {e}")
            return False
            
    async def _create_channel_engine(self, channel_id: str):
        """Подготавливает канал для работы с глобальным движком."""
        try:
            if channel_id in self.channels:
                logger.info(f"✅ Канал {channel_id} уже готов к работе с глобальным движком")
                return True
                
            logger.info(f"🔧 Подготавливаю канал {channel_id} для работы с глобальным движком")
            
            # ИСПРАВЛЕНИЕ: НЕ создаем новый движок, используем глобальный!
            # Загружаем данные канала из БД если нужно
            success = await self._load_specific_channel(channel_id)
            
            if success:
                logger.info(f"✅ Канал {channel_id} готов к работе с глобальным движком")
                return True
            else:
                logger.error(f"❌ Не удалось подготовить канал {channel_id}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка подготовки канала {channel_id}: {e}")
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
            
            # Очищаем last_update_id для канала
            if channel_id in self.last_update_ids:
                del self.last_update_ids[channel_id]
            
            # ИСПРАВЛЕНИЕ: НЕ удаляем канал из channels - он может быть нужен
            # Канал остается в памяти для возможного перезапуска
            
            logger.info(f"✅ Канал {channel_id} полностью остановлен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки канала {channel_id}: {e}") 

    async def stop_channel(self, channel_id: str) -> bool:
        """
        Публичный метод для остановки канала.
        
        Args:
            channel_id: ID канала для остановки
            
        Returns:
            bool: True если канал успешно остановлен
        """
        try:
            if channel_id not in self.channels:
                logger.warning(f"⚠️ Канал {channel_id} не найден")
                return False
            
            # Удаляем из активных каналов
            if channel_id in self.active_channels:
                del self.active_channels[channel_id]
            
            # Останавливаем поллинг
            await self._stop_channel_polling(channel_id)
            
            logger.info(f"✅ Канал {channel_id} успешно остановлен")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки канала {channel_id}: {e}")
            return False

    async def _reset_user_state(self, channel_id: str, user_id: str):
        """Сбрасывает состояние пользователя (удаляет из БД)."""
        try:
            if not self.global_engine:
                logger.error("❌ Глобальный движок недоступен для сброса состояния пользователя")
                return
            
            # Удаляем состояние пользователя
            step = {
                "id": "reset_user_state",
                "type": "mongo_delete_document",
                "params": {
                    "collection": "user_states",
                    "filter": {
                        "channel_id": channel_id,
                        "user_id": user_id
                    },
                    "output_var": "delete_result"
                }
            }
            
            context = {}
            result_context = await self.global_engine.execute_step(step, context)
            result = result_context.get("delete_result", {})
            
            if result.get("success"):
                logger.info(f"🗑️ Состояние пользователя {user_id} сброшено")
            else:
                logger.warning(f"⚠️ Не удалось сбросить состояние пользователя {user_id}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка сброса состояния пользователя {user_id}: {e}") 