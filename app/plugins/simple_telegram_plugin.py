"""
Упрощённый Telegram плагин для Universal Agent Platform.
Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!

Объединяет в себе:
1. Получение сообщений от Telegram
2. Определение сценариев для команд
3. Выполнение Telegram шагов
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, Callable, Any, Optional, List
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, MessageHandler, CommandHandler, CallbackQueryHandler, filters
from app.core.base_plugin import BasePlugin
from loguru import logger


class SimpleTelegramPlugin(BasePlugin):
    """
    Упрощённый Telegram плагин.
    
    Принципы:
    1. Один класс для всего Telegram функционала
    2. Прямая работа с движком без лишних слоёв
    3. Простая логика выбора сценариев
    4. Минимум зависимостей
    """
    
    def __init__(self, bot_token: str = None, channel_id: str = None):
        super().__init__("simple_telegram")
        
        # Получаем токен из параметра или переменной окружения
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.channel_id = channel_id or "telegram_bot"  # Дефолтный channel_id
        self.bot: Optional[Bot] = None
        self.application: Optional[Application] = None
        self._polling_task: Optional[asyncio.Task] = None
        
        # Маппинг команд на сценарии
        self._command_scenarios = {
            "/start": "registration",
            "/help": "help", 
            "/menu": "main_menu"
        }
        
        # Дефолтный сценарий для неизвестных команд
        self._default_scenario = "main_menu"
        
        # Callbacks (оставляем для совместимости)
        self.command_callback: Optional[Callable] = None
        self.message_callback: Optional[Callable] = None
        self.callback_query_callback: Optional[Callable] = None
        
    async def _do_initialize(self):
        """Инициализация Telegram бота."""
        # Загружаем настройки из БД
        await self._load_settings_from_db()
            
        if not self.bot_token:
            # В тестовом режиме без реального бота
            self.logger.warning("⚠️ Telegram бот работает в ограниченном режиме - токен не найден в БД")
            self.logger.info("💡 Для настройки используйте: POST /admin/plugins/telegram/settings")
            self.bot = None
            self.application = None
            return
            
        try:
            # Создаем Application для polling
            self.application = Application.builder().token(self.bot_token).build()
            self.bot = self.application.bot
            
            # Проверяем что бот работает
            bot_info = await self.bot.get_me()
            self.logger.info(f"Telegram бот инициализирован: @{bot_info.username}")
            
            # Регистрируем обработчики
            self._setup_handlers()
            
        except Exception as e:
            self.logger.warning(f"Не удалось инициализировать Telegram бота: {e}, работаю в тестовом режиме")
            self.bot = None
            self.application = None
            
    def _setup_handlers(self):
        """Настраивает обработчики для polling."""
        if not self.application:
            self.logger.warning("Application не доступен для регистрации обработчиков")
            return
            
        try:
            # Обработчик команд (например, /start)
            self.application.add_handler(
                CommandHandler(["start", "help"], self._handle_command)
            )
            self.logger.info("✅ Обработчик команд зарегистрирован")
            
            # Обработчик обычных сообщений
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
            )
            self.logger.info("✅ Обработчик сообщений зарегистрирован")
            
            # Обработчик callback_query от кнопок
            self.application.add_handler(
                CallbackQueryHandler(self._handle_callback_query)
            )
            self.logger.info("✅ Обработчик callback_query зарегистрирован")
            
            # Проверяем количество обработчиков
            handlers_count = len(self.application.handlers[0]) if self.application.handlers else 0
            self.logger.info(f"📊 Всего обработчиков зарегистрировано: {handlers_count}")
            
            # Сохраняем количество обработчиков для других экземпляров
            self._handlers_count = handlers_count
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка регистрации обработчиков: {e}")
            
        self.logger.info("Telegram handlers зарегистрированы")
    
    async def _load_settings_from_db(self):
        """Загружает настройки Telegram из MongoDB"""
        try:
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                self.logger.warning("MongoDB плагин недоступен для загрузки настроек Telegram")
                return
                
            mongo_plugin = self.engine.plugins['mongo']
            
            # Загружаем настройки Telegram
            settings_result = await mongo_plugin._find_one("plugin_settings", {"plugin_name": "telegram"})
            
            if settings_result and settings_result.get("success") and settings_result.get("document"):
                settings = settings_result["document"]
                self.bot_token = settings.get("bot_token")
                webhook_url = settings.get("webhook_url")
                webhook_secret = settings.get("webhook_secret")
                
                self.logger.info("✅ Настройки Telegram загружены из БД")
            else:
                self.logger.info("⚠️ Настройки Telegram не найдены в БД")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки настроек Telegram из БД: {e}")
    
    # === МЕТОДЫ ДЛЯ НАСТРОЙКИ ЧЕРЕЗ API ===
    
    async def save_settings_to_db(self, bot_token: str, webhook_url: str = None, webhook_secret: str = None) -> Dict[str, Any]:
        """Сохраняет настройки Telegram в MongoDB (для использования через API)"""
        try:
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                return {"success": False, "error": "MongoDB недоступен"}
                
            mongo_plugin = self.engine.plugins['mongo']
            
            settings_doc = {
                "plugin_name": "telegram",
                "bot_token": bot_token,
                "webhook_url": webhook_url,
                "webhook_secret": webhook_secret,
                "updated_at": datetime.now().isoformat()
            }
            
            # Используем upsert для обновления или создания
            result = await mongo_plugin._update_one(
                "plugin_settings", 
                {"plugin_name": "telegram"}, 
                {"$set": settings_doc},
                upsert=True
            )
            
            if result.get("success"):
                # Обновляем настройки в плагине
                old_token = self.bot_token
                self.bot_token = bot_token
                
                # Переинициализируем бота если токен изменился
                if old_token != bot_token:
                    if self.application:
                        await self.stop_polling()
                    await self._do_initialize()
                
                self.logger.info("✅ Настройки Telegram сохранены в БД и применены")
                return {"success": True, "message": "Настройки сохранены"}
            else:
                error_msg = result.get('error', 'неизвестная ошибка')
                self.logger.warning(f"⚠️ Не удалось сохранить настройки Telegram в БД: {error_msg}")
                return {"success": False, "error": error_msg}
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения настроек Telegram в БД: {e}")
            return {"success": False, "error": str(e)}
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Возвращает текущие настройки плагина"""
        return {
            "bot_token": "***" if self.bot_token else None,
            "bot_token_set": bool(self.bot_token),
            "bot_initialized": bool(self.bot),
            "polling_active": bool(self._polling_task and not self._polling_task.done()),
            "configured": bool(self.bot_token)
        }
    
    async def update_bot_token(self, new_token: str, scenario_id: str = None):
        """Обновляет токен бота в БД и переинициализирует бота."""
        try:
            if not hasattr(self, 'engine') or not self.engine:
                self.logger.error("Движок недоступен для обновления токена")
                return False
                
            # Обновляем маппинг канала с новым токеном
            step = {
                "id": "update_channel_config",
                "type": "mongo_create_channel_mapping",
                "params": {
                    "channel_id": self.channel_id,
                    "scenario_id": scenario_id or "default_scenario",
                    "channel_type": "telegram",
                    "channel_config": {
                        "bot_token": new_token,
                        "webhook_url": None,
                        "allowed_updates": ["message", "callback_query"]
                    },
                    "output_var": "update_result"
                }
            }
            
            context = {}
            result_context = await self.engine.execute_step(step, context)
            
            update_result = result_context.get("update_result", {})
            if update_result.get("success"):
                # Обновляем токен в плагине
                self.bot_token = new_token
                
                # Останавливаем старого бота если есть
                if self.application:
                    await self.stop_polling()
                
                # Переинициализируем бота с новым токеном
                await self._do_initialize()
                
                self.logger.info(f"✅ Токен бота обновлен для канала {self.channel_id}")
                return True
            else:
                self.logger.error(f"❌ Не удалось обновить токен в БД: {update_result}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления токена: {e}")
            return False
    
    async def start_polling(self):
        """Запускает polling для получения сообщений."""
        if not self.application:
            self.logger.warning("Polling недоступен в тестовом режиме")
            return
            
        try:
            self.logger.info("🚀 Запуск Telegram polling...")
            
            # Останавливаем существующий поллинг если есть
            if self._polling_task and not self._polling_task.done():
                self.logger.info("⏹️ Останавливаю существующий поллинг...")
                self._polling_task.cancel()
                try:
                    await self._polling_task
                except asyncio.CancelledError:
                    pass
                    
            # Правильный способ запуска polling в asyncio
            await self.application.initialize()
            await self.application.start()
            
            # Запускаем polling в отдельной задаче
            import asyncio
            polling_task = asyncio.create_task(
                self.application.updater.start_polling(
                    poll_interval=1.0,
                    timeout=10,
                    drop_pending_updates=True,  # Игнорируем старые сообщения чтобы избежать конфликтов
                    allowed_updates=["message", "callback_query"]
                )
            )
            
            self.logger.info("✅ Telegram polling запущен успешно")
            
            # Сохраняем задачу для возможности остановки
            self._polling_task = polling_task
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка polling: {e}")
            if "Conflict" in str(e):
                self.logger.error("🚨 Конфликт: другой экземпляр бота уже запущен!")
                self.logger.error("💡 Попробуйте перезапустить контейнер API")
            
    async def stop_polling(self):
        """Останавливает polling."""
        if self.application:
            await self.application.stop()
            self.logger.info("Telegram polling остановлен")
            
    def set_message_callback(self, callback: Callable):
        """Устанавливает callback для обработки входящих сообщений."""
        self.message_callback = callback
        
    def set_command_callback(self, callback: Callable):
        """Устанавливает callback для обработки команд."""
        self.command_callback = callback
        
    def set_callback_query_callback(self, callback: Callable):
        """Устанавливает callback для обработки callback_query."""
        self.callback_query_callback = callback
    
    async def _handle_command(self, update: Update, context):
        """Внутренний обработчик команд с прямым выполнением сценариев."""
        try:
            command = update.message.text
            user = update.effective_user
            chat = update.effective_chat
            
            self.logger.info(f"📱 Получена команда {command} от пользователя {user.first_name} (ID: {user.id})")
            
            # Формируем контекст для обработки
            telegram_context = {
                "command": command,
                "user_id": str(user.id),
                "user_name": user.first_name or "Пользователь",
                "user_username": user.username,
                "chat_id": str(chat.id),
                "chat_type": chat.type,
                "message_text": command,
                "is_command": True
            }
            
            # Определяем сценарий для команды
            scenario_id = self._get_scenario_for_command(command)
            if scenario_id:
                await self._execute_scenario(scenario_id, telegram_context)
            
            # Вызываем внешний callback если есть (для совместимости)
            if self.command_callback:
                await self.command_callback(telegram_context)
                
        except Exception as e:
            self.logger.error(f"Ошибка обработки команды: {e}")
            
    async def _handle_message(self, update: Update, context):
        """Внутренний обработчик сообщений с прямым выполнением сценариев."""
        try:
            message = update.message
            user = update.effective_user
            chat = update.effective_chat
            
            self.logger.info(f"💬 Получено сообщение '{message.text}' от {user.first_name} (ID: {user.id})")
            
            # Формируем контекст для обработки
            telegram_context = {
                "user_id": str(user.id),
                "user_name": user.first_name or "Пользователь", 
                "user_username": user.username,
                "chat_id": str(chat.id),
                "chat_type": chat.type,
                "message_text": message.text,
                "is_command": False
            }
            
            # Для обычных сообщений - дефолтный сценарий
            await self._execute_scenario(self._default_scenario, telegram_context)
            
            # Вызываем внешний callback если есть (для совместимости)
            if self.message_callback:
                await self.message_callback(telegram_context)
                
        except Exception as e:
            self.logger.error(f"Ошибка обработки сообщения: {e}")
            
    async def _handle_callback_query(self, update: Update, context):
        """Внутренний обработчик callback_query с прямым выполнением сценариев."""
        try:
            query = update.callback_query
            user = update.effective_user
            chat = update.effective_chat
            
            self.logger.info(f"🔘 Получен callback '{query.data}' от {user.first_name} (ID: {user.id})")
            
            # Подтверждаем получение callback
            await query.answer()
            
            # Формируем контекст для обработки
            telegram_context = {
                "user_id": str(user.id),
                "user_name": user.first_name or "Пользователь",
                "user_username": user.username,
                "chat_id": str(chat.id),
                "chat_type": chat.type,
                "callback_data": query.data,
                "message_id": str(query.message.message_id) if query.message else None,
                "is_callback": True
            }
            
            # Определяем сценарий из callback данных
            scenario_id = self._get_scenario_for_callback(query.data)
            if scenario_id:
                await self._execute_scenario(scenario_id, telegram_context)
            
            # Вызываем внешний callback если есть (для совместимости)
            if self.callback_query_callback:
                await self.callback_query_callback(telegram_context)
                
        except Exception as e:
            self.logger.error(f"Ошибка обработки callback: {e}")
            
    def _get_scenario_for_command(self, command: str) -> Optional[str]:
        """Определяет сценарий для команды."""
        scenario_id = self._command_scenarios.get(command)
        if scenario_id:
            self.logger.info(f"🎯 Команда {command} -> сценарий {scenario_id}")
            return scenario_id
        else:
            self.logger.info(f"🎯 Неизвестная команда {command} -> дефолтный сценарий {self._default_scenario}")
            return self._default_scenario
            
    def _get_scenario_for_callback(self, callback_data: str) -> Optional[str]:
        """Определяет сценарий из callback данных."""
        # Формат callback: scenario_id:action или просто scenario_id
        if ":" in callback_data:
            scenario_id = callback_data.split(":")[0]
        else:
            scenario_id = callback_data
        self.logger.info(f"🎯 Callback {callback_data} -> сценарий {scenario_id}")
        return scenario_id
        
    async def _execute_scenario(self, scenario_id: str, telegram_context: Dict[str, Any]):
        """Выполняет сценарий через API с channel_id."""
        try:
            self.logger.info(f"🚀 Выполнение сценария {scenario_id}")
            
            # Формируем channel_id для Telegram бота
            channel_id = "telegram_bot"
            
            # Подготавливаем контекст выполнения
            execution_context = {
                **telegram_context,  # Весь Telegram контекст
                "scenario_id": scenario_id,
                "execution_started_at": asyncio.get_event_loop().time()
            }
            
            # Выполняем сценарий через движок с использованием channel_id
            if hasattr(self, 'engine') and self.engine:
                # Используем API-подобный подход с channel_id
                from app.api.simple import _load_scenario
                
                # Загружаем сценарий для канала
                scenario = await _load_scenario(channel_id, scenario_id)
                
                # Выполняем сценарий
                result = await self.engine.execute_scenario(scenario, execution_context)
                self.logger.info(f"✅ Сценарий {scenario_id} выполнен успешно")
            else:
                self.logger.error(f"❌ Движок не доступен для выполнения сценария {scenario_id}")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка выполнения сценария {scenario_id}: {e}")
            
    def register_handlers(self) -> Dict[str, Callable]:
        """Регистрирует обработчики Telegram шагов."""
        return {
            "telegram_send_message": self.handle_send_message,
            "telegram_edit_message": self.handle_edit_message,
            "telegram_send_buttons": self.handle_send_buttons,
            "telegram_update_token": self.handle_update_token,
            "telegram_load_token": self.handle_load_token,
            "telegram_start_polling": self.handle_start_polling,
        }
        
    async def healthcheck(self) -> bool:
        """Проверяет здоровье Telegram бота."""
        try:
            if not self.bot:
                return False
                
            # Простая проверка - получаем информацию о боте
            await self.bot.get_me()
            return True
            
        except Exception as e:
            self.logger.error(f"Telegram healthcheck failed: {e}")
            return False
            
    # === ОБРАБОТЧИКИ ШАГОВ ===
    
    async def handle_send_message(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отправляет простое сообщение в Telegram.
        
        Пример шага:
        {
            "id": "send1",
            "type": "telegram_send_message",
            "params": {
                "chat_id": "{chat_id}",
                "text": "Привет, {user_name}!",
                "parse_mode": "HTML",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "Кнопка", "callback_data": "action"}]
                    ]
                }
            }
        }
        """
        self.log_step_start(step)
        
        try:
            # Валидируем обязательные параметры
            self.validate_required_params(step, ["chat_id", "text"])
            
            # Получаем параметры
            chat_id = self.get_param(step, "chat_id", required=True)
            text = self.get_param(step, "text", required=True)
            parse_mode = self.get_param(step, "parse_mode", default="HTML")
            reply_markup_data = self.get_param(step, "reply_markup", default=None)
            
            # Подставляем переменные
            resolved_chat_id = self.resolve_template(str(chat_id), context)
            resolved_text = self.resolve_template(text, context)
            
            # Валидируем что chat_id не None
            if resolved_chat_id == "None" or resolved_chat_id is None or resolved_chat_id == "{chat_id}":
                raise ValueError(f"chat_id не найден в контексте. Доступные ключи: {list(context.keys())}")
            
            # Создаем reply_markup если есть
            reply_markup = None
            if reply_markup_data and "inline_keyboard" in reply_markup_data:
                keyboard = []
                for row in reply_markup_data["inline_keyboard"]:
                    keyboard_row = []
                    for button in row:
                        keyboard_row.append(InlineKeyboardButton(
                            text=button["text"],
                            callback_data=button["callback_data"]
                        ))
                    keyboard.append(keyboard_row)
                reply_markup = InlineKeyboardMarkup(keyboard)
            
            if self.bot is None:
                # Тестовый режим - симулируем отправку
                self.logger.info(f"[ТЕСТ] Отправка сообщения в чат {resolved_chat_id}: {resolved_text}")
                if reply_markup_data:
                    self.logger.info(f"[ТЕСТ] С кнопками: {reply_markup_data}")
                message_id = 12345  # Тестовый message_id
            else:
                # Реальная отправка сообщения
                message = await self.bot.send_message(
                    chat_id=int(resolved_chat_id),
                    text=resolved_text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
                message_id = message.message_id
            
            # Обновляем контекст
            result = self.update_context(context, {
                "message_id": message_id,
                "sent_text": resolved_text,
                "sent_to_chat": resolved_chat_id,
                "sent_with_buttons": reply_markup_data is not None
            }, prefix="telegram_")
            
            self.log_step_success(step, f"Message sent to {resolved_chat_id}")
            return result
            
        except Exception as e:
            self.log_step_error(step, e)
            raise
            
    async def handle_edit_message(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Редактирует сообщение в Telegram.
        
        Пример шага:
        {
            "id": "edit1",
            "type": "telegram_edit_message",
            "params": {
                "chat_id": "{chat_id}",
                "message_id": "{telegram_message_id}",
                "text": "Обновленный текст",
                "parse_mode": "HTML"
            }
        }
        """
        self.log_step_start(step)
        
        try:
            # Валидируем обязательные параметры
            self.validate_required_params(step, ["chat_id", "message_id", "text"])
            
            # Получаем параметры
            chat_id = self.get_param(step, "chat_id", required=True)
            message_id = self.get_param(step, "message_id", required=True) 
            text = self.get_param(step, "text", required=True)
            parse_mode = self.get_param(step, "parse_mode", default="HTML")
            
            # Подставляем переменные
            resolved_chat_id = self.resolve_template(str(chat_id), context)
            resolved_message_id = self.resolve_template(str(message_id), context)
            resolved_text = self.resolve_template(text, context)
            
            # Валидируем что chat_id не None
            if resolved_chat_id == "None" or resolved_chat_id is None or resolved_chat_id == "{chat_id}":
                raise ValueError(f"chat_id не найден в контексте. Доступные ключи: {list(context.keys())}")
            
            if self.bot is None:
                # Тестовый режим - симулируем редактирование
                self.logger.info(f"[ТЕСТ] Редактирование сообщения {resolved_message_id} в чате {resolved_chat_id}: {resolved_text}")
            else:
                # Реальное редактирование сообщения
                await self.bot.edit_message_text(
                    chat_id=int(resolved_chat_id),
                    message_id=int(resolved_message_id),
                    text=resolved_text,
                    parse_mode=parse_mode
                )
            
            # Обновляем контекст
            result = self.update_context(context, {
                "edited_text": resolved_text,
                "edited_message_id": resolved_message_id
            }, prefix="telegram_")
            
            self.log_step_success(step, f"Message {resolved_message_id} edited in {resolved_chat_id}")
            return result
            
        except Exception as e:
            self.log_step_error(step, e)
            raise
            
    async def handle_send_buttons(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отправляет сообщение с inline кнопками.
        
        Пример шага:
        {
            "id": "buttons1",
            "type": "telegram_send_buttons",
            "params": {
                "chat_id": "{chat_id}",
                "text": "Выберите действие:",
                "buttons": [
                    [{"text": "Кнопка 1", "callback_data": "action1"}],
                    [{"text": "Кнопка 2", "callback_data": "action2"}]
                ]
            }
        }
        """
        self.log_step_start(step)
        
        try:
            # Валидируем обязательные параметры
            self.validate_required_params(step, ["chat_id", "text", "buttons"])
            
            # Получаем параметры
            chat_id = self.get_param(step, "chat_id", required=True)
            text = self.get_param(step, "text", required=True)
            buttons = self.get_param(step, "buttons", required=True)
            parse_mode = self.get_param(step, "parse_mode", default="HTML")
            
            # Подставляем переменные
            resolved_chat_id = self.resolve_template(str(chat_id), context)
            resolved_text = self.resolve_template(text, context)
            
            # Валидируем что chat_id не None
            if resolved_chat_id == "None" or resolved_chat_id is None or resolved_chat_id == "{chat_id}":
                raise ValueError(f"chat_id не найден в контексте. Доступные ключи: {list(context.keys())}")
            
            if self.bot is None:
                # Тестовый режим - симулируем отправку с кнопками
                self.logger.info(f"[ТЕСТ] Отправка сообщения с кнопками в чат {resolved_chat_id}: {resolved_text}")
                self.logger.info(f"[ТЕСТ] Кнопки: {buttons}")
                message_id = 12346  # Тестовый message_id
            else:
                # Создаем клавиатуру
                keyboard = []
                for row in buttons:
                    keyboard_row = []
                    for button in row:
                        keyboard_row.append(InlineKeyboardButton(
                            text=button["text"],
                            callback_data=button["callback_data"]
                        ))
                    keyboard.append(keyboard_row)
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Отправляем сообщение с кнопками
                message = await self.bot.send_message(
                    chat_id=int(resolved_chat_id),
                    text=resolved_text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
                message_id = message.message_id
            
            # Обновляем контекст
            result = self.update_context(context, {
                "message_id": message_id,
                "sent_text": resolved_text,
                "sent_to_chat": resolved_chat_id,
                "sent_buttons": buttons
            }, prefix="telegram_")
            
            self.log_step_success(step, f"Message with buttons sent to {resolved_chat_id}")
            return result
            
        except Exception as e:
            self.log_step_error(step, e)
            raise
            
    def _create_inline_keyboard(self, buttons: List[List[Dict]], context: Dict[str, Any]) -> InlineKeyboardMarkup:
        """
        Создает inline клавиатуру из конфигурации.
        
        Args:
            buttons: Массив рядов кнопок
            context: Контекст для подстановки переменных
            
        Returns:
            InlineKeyboardMarkup: Готовая клавиатура
        """
        keyboard = []
        
        for row in buttons:
            keyboard_row = []
            for button in row:
                text = self.resolve_template(button.get("text", ""), context)
                callback_data = self.resolve_template(button.get("callback_data", ""), context)
                
                keyboard_row.append(
                    InlineKeyboardButton(text=text, callback_data=callback_data)
                )
            keyboard.append(keyboard_row)
            
        return InlineKeyboardMarkup(keyboard)
    
    async def handle_start_polling(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Запускает Telegram polling как шаг сценария.
        
        Пример шага:
        {
            "id": "start_polling",
            "type": "telegram_start_polling",
            "params": {
                "token": "{telegram_token}",
                "handlers": {
                    "/start": "atomic_01_user_check",
                    "message": "message_handler",
                    "callback_query": "callback_handler"
                },
                "channel_id": "{channel_id}"
            }
        }
        """
        self.log_step_start(step)
        
        try:
            # Получаем параметры
            token = self.get_param(step, "token", default=self.bot_token)
            handlers = self.get_param(step, "handlers", default={})
            channel_id = self.get_param(step, "channel_id", default=self.channel_id)
            
            # Подставляем переменные
            if token:
                resolved_token = self.resolve_template(str(token), context)
                if resolved_token != self.bot_token:
                    # Обновляем токен если изменился
                    self.bot_token = resolved_token
                    await self._do_initialize()
            
            # Обновляем маппинг команд на сценарии
            if handlers:
                self._command_scenarios.update(handlers)
                self.logger.info(f"Обновлен маппинг команд: {self._command_scenarios}")
            
            # Запускаем polling
            if not self._polling_task or self._polling_task.done():
                await self.start_polling()
                
                # Подсчитываем количество зарегистрированных обработчиков
                handlers_count = 0
                if self.application and self.application.handlers:
                    handlers_count = len(self.application.handlers[0])  # Группа обработчиков по умолчанию
                elif hasattr(self, '_handlers_count'):
                    handlers_count = self._handlers_count  # Используем сохраненное значение
                
                # Обновляем контекст
                result = self.update_context(context, {
                    "polling_started": True,
                    "channel_id": channel_id,
                    "handlers_count": handlers_count,
                    "bot_token_set": bool(self.bot_token)
                }, prefix="telegram_")
                
                self.log_step_success(step, f"Polling started for channel {channel_id}")
                return result
            else:
                # Polling уже запущен
                result = self.update_context(context, {
                    "polling_already_running": True,
                    "channel_id": channel_id
                }, prefix="telegram_")
                
                self.log_step_success(step, f"Polling already running for channel {channel_id}")
                return result
                
        except Exception as e:
            self.log_step_error(step, e)
            # Обновляем контекст с ошибкой
            result = self.update_context(context, {
                "polling_error": str(e),
                "polling_started": False
            }, prefix="telegram_")
            return result
    
    # === ОБРАБОТЧИКИ УПРАВЛЕНИЯ ТОКЕНАМИ ===
    
    async def handle_update_token(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обновляет токен бота в БД.
        
        Пример шага:
        {
            "id": "update_token",
            "type": "telegram_update_token",
            "params": {
                "bot_token": "1234567890:ABCDEF...",
                "scenario_id": "main_scenario"
            }
        }
        """
        self.log_step_start(step)
        
        try:
            # Валидируем обязательные параметры
            self.validate_required_params(step, ["bot_token"])
            
            # Получаем параметры
            bot_token = self.get_param(step, "bot_token", required=True)
            scenario_id = self.get_param(step, "scenario_id")
            
            # Подставляем переменные
            resolved_token = self.resolve_template(bot_token, context)
            resolved_scenario_id = self.resolve_template(scenario_id or "default_scenario", context)
            
            # Обновляем токен
            success = await self.update_bot_token(resolved_token, resolved_scenario_id)
            
            # Обновляем контекст
            result = self.update_context(context, {
                "token_updated": success,
                "new_token_set": success,
                "channel_id": self.channel_id
            }, prefix="telegram_")
            
            if success:
                self.log_step_success(step, f"Token updated for channel {self.channel_id}")
            else:
                self.log_step_error(step, "Failed to update token")
                
            return result
            
        except Exception as e:
            self.log_step_error(step, e)
            raise
    
    async def handle_load_token(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Загружает токен бота из БД.
        
        Пример шага:
        {
            "id": "load_token",
            "type": "telegram_load_token",
            "params": {
                "channel_id": "telegram_bot"
            }
        }
        """
        self.log_step_start(step)
        
        try:
            # Получаем параметры
            channel_id = self.get_param(step, "channel_id", default=self.channel_id)
            
            # Подставляем переменные
            resolved_channel_id = self.resolve_template(channel_id, context)
            
            # Сохраняем старый channel_id
            old_channel_id = self.channel_id
            self.channel_id = resolved_channel_id
            
            # Загружаем токен
            await self._load_token_from_db()
            
            # Обновляем контекст
            result = self.update_context(context, {
                "token_loaded": bool(self.bot_token),
                "channel_id": self.channel_id,
                "bot_token_available": bool(self.bot_token)
            }, prefix="telegram_")
            
            if self.bot_token:
                self.log_step_success(step, f"Token loaded for channel {self.channel_id}")
            else:
                self.log_step_error(step, f"No token found for channel {self.channel_id}")
                # Восстанавливаем старый channel_id если токен не найден
                self.channel_id = old_channel_id
                
            return result
            
        except Exception as e:
            self.log_step_error(step, e)
            raise


# === ПРИМЕР ИСПОЛЬЗОВАНИЯ ===

async def example_usage():
    """Пример использования SimpleTelegramPlugin."""
    from app.core.simple_engine import SimpleScenarioEngine
    
    # Создаем движок
    engine = SimpleScenarioEngine()
    
    # Создаем и регистрируем плагин
    plugin = SimpleTelegramPlugin()
    await plugin.initialize()
    engine.register_plugin(plugin)
    
    # Пример сценария
    scenario = {
        "scenario_id": "telegram_demo",
        "steps": [
            {
                "id": "start",
                "type": "start",
                "next_step": "send_welcome"
            },
            {
                "id": "send_welcome",
                "type": "telegram_send_message",
                "params": {
                    "chat_id": "{chat_id}",
                    "text": "🎉 Добро пожаловать, {user_name}!"
                },
                "next_step": "send_buttons"
            },
            {
                "id": "send_buttons",
                "type": "telegram_send_buttons",
                "params": {
                    "chat_id": "{chat_id}",
                    "text": "Что хотите сделать?",
                    "buttons": [
                        [{"text": "📊 Статистика", "callback_data": "stats"}],
                        [{"text": "⚙️ Настройки", "callback_data": "settings"}],
                        [{"text": "❓ Помощь", "callback_data": "help"}]
                    ]
                },
                "next_step": "end"
            },
            {
                "id": "end",
                "type": "end"
            }
        ]
    }
    
    # Контекст
    context = {
        "chat_id": "123456789",
        "user_name": "Иван"
    }
    
    # Выполняем сценарий
    result = await engine.execute_scenario(scenario, context)
    print("Результат:", result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage()) 