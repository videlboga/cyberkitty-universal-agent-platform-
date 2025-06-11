"""
Telegram Ecosystem Plugin для KittyCore
Полнофункциональная система для управления Telegram ботами и юзерботами

Возможности:
- Создание ботов через @BotFather  
- TON кошельки и платежи
- Stars интеграция
- Юзербот функционал
- Автоматизация каналов/групп
"""

import asyncio
import json
import re
import random
import string
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
import logging
from loguru import logger

from app.core.base_plugin import BasePlugin

try:
    import pyrogram
    from pyrogram import Client, filters
    from pyrogram.types import Message, User, Chat
    from pyrogram.errors import FloodWait, SessionPasswordNeeded
    PYROGRAM_AVAILABLE = True
except ImportError:
    PYROGRAM_AVAILABLE = False
    logger.warning("Pyrogram не установлен, Telegram функции недоступны")

try:
    import aiohttp
    import aiofiles
    ASYNC_LIBS_AVAILABLE = True
except ImportError:
    ASYNC_LIBS_AVAILABLE = False
    logger.warning("Async библиотеки не установлены")


class TelegramEcosystemPlugin(BasePlugin):
    """
    Telegram Ecosystem Plugin - полная автоматизация Telegram
    """
    
    def __init__(self):
        super().__init__()
        self.name = "telegram_ecosystem"
        self.version = "1.0.0"
        self.description = "Полная автоматизация Telegram: боты, юзерботы, платежи"
        
        # Состояние плагина
        self.userbot_sessions: Dict[str, Client] = {}
        self.bot_tokens: Dict[str, str] = {}
        self.active_conversations: Dict[str, Any] = {}
        self.payment_monitors: Dict[str, Any] = {}
        
        # Настройки по умолчанию
        self.default_settings = {
            "api_id": None,
            "api_hash": None,
            "default_bot_token": None,
            "ton_wallet_address": None,
            "stars_enabled": True,
            "userbot_phone": None,
            "log_chat_id": None,
            "auto_create_bots": False,
            "max_concurrent_sessions": 5
        }

    async def initialize(self) -> bool:
        """Инициализация плагина"""
        try:
            if not PYROGRAM_AVAILABLE:
                logger.error("Pyrogram недоступен - плагин не может работать")
                return False
                
            await self._ensure_fresh_settings()
            
            # Проверяем базовые настройки
            settings = self.settings
            if not settings.get("api_id") or not settings.get("api_hash"):
                logger.warning("API ID/Hash не настроены - некоторые функции недоступны")
            
            logger.info(f"🤖 Telegram Ecosystem Plugin v{self.version} инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Telegram Ecosystem Plugin: {e}")
            return False

    # =====================================================
    # СИСТЕМА СОЗДАНИЯ БОТОВ ЧЕРЕЗ @BOTFATHER
    # =====================================================
    
    async def create_bot_via_botfather(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создание бота через @BotFather используя юзербот
        """
        try:
            bot_name = context.get("bot_name", f"AutoBot_{random.randint(1000, 9999)}")
            bot_username = context.get("bot_username", f"autobot_{self._generate_random_string(8)}_bot")
            session_name = context.get("session_name", "default_userbot")
            
            logger.info(f"🤖 Создаю бота: {bot_name} (@{bot_username})")
            
            # Получаем или создаем юзербот сессию
            userbot = await self._get_userbot_session(session_name)
            if not userbot:
                return {"success": False, "error": "Юзербот сессия недоступна"}
            
            # Автоматизация диалога с @BotFather
            bot_token = await self._automate_botfather_dialogue(userbot, bot_name, bot_username)
            
            if bot_token:
                # Сохраняем токен
                self.bot_tokens[bot_username] = bot_token
                await self._save_bot_token(bot_username, bot_token, bot_name)
                
                # Автоматически настраиваем бота
                await self._setup_new_bot(bot_token, bot_name, bot_username)
                
                logger.success(f"✅ Бот @{bot_username} создан и настроен!")
                return {
                    "success": True,
                    "bot_username": bot_username,
                    "bot_token": bot_token,
                    "bot_name": bot_name
                }
            else:
                return {"success": False, "error": "Не удалось получить токен от @BotFather"}
                
        except Exception as e:
            logger.error(f"Ошибка создания бота: {e}")
            return {"success": False, "error": str(e)}

    async def _automate_botfather_dialogue(self, userbot: Client, bot_name: str, bot_username: str) -> Optional[str]:
        """Автоматизация диалога с @BotFather"""
        try:
            # Шаг 1: Отправляем /newbot
            await userbot.send_message("@BotFather", "/newbot")
            await asyncio.sleep(2)
            
            # Шаг 2: Отправляем название бота
            await userbot.send_message("@BotFather", bot_name)
            await asyncio.sleep(2)
            
            # Шаг 3: Отправляем username
            await userbot.send_message("@BotFather", bot_username)
            await asyncio.sleep(3)
            
            # Шаг 4: Получаем последнее сообщение и парсим токен
            async for message in userbot.get_chat_history("@BotFather", limit=1):
                if "congratulations" in message.text.lower() or "поздравляю" in message.text.lower():
                    # Ищем токен в сообщении
                    token_match = re.search(r'(\d+:[A-Za-z0-9_-]+)', message.text)
                    if token_match:
                        return token_match.group(1)
                elif "sorry" in message.text.lower() or "извините" in message.text.lower():
                    logger.warning(f"Ошибка от BotFather: {message.text}")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка диалога с BotFather: {e}")
            return None

    async def _setup_new_bot(self, token: str, name: str, username: str) -> bool:
        """Автоматическая настройка нового бота"""
        try:
            # Создаем клиент бота
            bot_client = Client(
                f"bot_{username}",
                bot_token=token,
                api_id=self.settings.get("api_id"),
                api_hash=self.settings.get("api_hash")
            )
            
            async with bot_client:
                # Устанавливаем команды
                await self._set_bot_commands(bot_client)
                
                # Устанавливаем описание
                await self._set_bot_description(bot_client, name)
                
                # Отправляем уведомление в лог чат
                await self._notify_bot_created(username, name, token)
            
            logger.info(f"✅ Бот @{username} настроен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки бота: {e}")
            return False

    async def _generate_random_string(self, length: int = 8) -> str:
        """Генерация случайной строки"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    # =====================================================
    # СИСТЕМА TON ПЛАТЕЖЕЙ И КОШЕЛЬКОВ
    # =====================================================
    
    async def create_ton_wallet(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создание TON кошелька
        """
        try:
            wallet_name = context.get("wallet_name", f"wallet_{self._generate_random_string(8)}")
            
            logger.info(f"💎 Создаю TON кошелек: {wallet_name}")
            
            # Генерируем seed фразу (24 слова)
            seed_phrase = self._generate_ton_seed()
            
            # Создаем адрес кошелька (симуляция, в реальности нужна TON SDK)
            wallet_address = self._generate_ton_address()
            
            # Сохраняем в БД
            wallet_data = {
                "wallet_name": wallet_name,
                "address": wallet_address,
                "seed_phrase": seed_phrase,  # В реальности - зашифровать!
                "balance": 0.0,
                "created_at": datetime.now().isoformat(),
                "transactions": []
            }
            
            await self._save_wallet_data(wallet_name, wallet_data)
            
            logger.success(f"✅ TON кошелек {wallet_name} создан: {wallet_address}")
            
            return {
                "success": True,
                "wallet_name": wallet_name,
                "address": wallet_address,
                "seed_phrase": seed_phrase  # В боевом режиме - НЕ возвращать!
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания TON кошелька: {e}")
            return {"success": False, "error": str(e)}

    async def send_ton_payment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отправка TON платежа
        """
        try:
            from_wallet = context.get("from_wallet")
            to_address = context.get("to_address") 
            amount = context.get("amount", 0.0)
            memo = context.get("memo", "")
            
            logger.info(f"💸 Отправляю {amount} TON с {from_wallet} на {to_address}")
            
            # Загружаем данные кошелька
            wallet_data = await self._load_wallet_data(from_wallet)
            if not wallet_data:
                return {"success": False, "error": "Кошелек не найден"}
            
            # Проверяем баланс (симуляция)
            if wallet_data.get("balance", 0) < amount:
                return {"success": False, "error": "Недостаточно средств"}
            
            # Симуляция отправки (в реальности - TON SDK)
            transaction_hash = f"tx_{self._generate_random_string(32)}"
            
            # Обновляем баланс
            wallet_data["balance"] -= amount
            wallet_data["transactions"].append({
                "type": "send",
                "amount": amount,
                "to_address": to_address,
                "memo": memo,
                "hash": transaction_hash,
                "timestamp": datetime.now().isoformat()
            })
            
            await self._save_wallet_data(from_wallet, wallet_data)
            
            logger.success(f"✅ TON платеж отправлен: {transaction_hash}")
            
            return {
                "success": True,
                "transaction_hash": transaction_hash,
                "amount": amount,
                "to_address": to_address
            }
            
        except Exception as e:
            logger.error(f"Ошибка отправки TON: {e}")
            return {"success": False, "error": str(e)}

    # =====================================================
    # СИСТЕМА TELEGRAM STARS
    # =====================================================
    
    async def create_stars_invoice(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создание Stars инвойса
        """
        try:
            bot_token = context.get("bot_token")
            chat_id = context.get("chat_id")
            amount = context.get("amount", 1)  # В Stars
            title = context.get("title", "Платеж")
            description = context.get("description", "Оплата услуг")
            
            logger.info(f"⭐ Создаю Stars инвойс: {amount} stars для {chat_id}")
            
            # Получаем бот клиент
            bot_client = await self._get_bot_client(bot_token)
            if not bot_client:
                return {"success": False, "error": "Бот недоступен"}
            
            # Создаем Stars инвойс (симуляция Telegram Bot API)
            invoice_data = {
                "chat_id": chat_id,
                "title": title,
                "description": description,
                "payload": f"stars_payment_{self._generate_random_string(16)}",
                "currency": "XTR",  # Telegram Stars
                "prices": [{"label": title, "amount": amount}]
            }
            
            # В реальности - используем bot.send_invoice()
            invoice_id = f"inv_{self._generate_random_string(16)}"
            
            # Сохраняем инвойс
            await self._save_invoice_data(invoice_id, invoice_data)
            
            logger.success(f"✅ Stars инвойс создан: {invoice_id}")
            
            return {
                "success": True,
                "invoice_id": invoice_id,
                "amount": amount,
                "title": title
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания Stars инвойса: {e}")
            return {"success": False, "error": str(e)}

    async def handle_stars_payment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка успешного Stars платежа
        """
        try:
            payment_data = context.get("payment_data", {})
            invoice_id = payment_data.get("invoice_payload")
            
            logger.info(f"⭐ Обрабатываю Stars платеж: {invoice_id}")
            
            # Загружаем данные инвойса
            invoice_data = await self._load_invoice_data(invoice_id)
            if not invoice_data:
                return {"success": False, "error": "Инвойс не найден"}
            
            # Отмечаем как оплаченный
            invoice_data["status"] = "paid"
            invoice_data["paid_at"] = datetime.now().isoformat()
            invoice_data["payment_data"] = payment_data
            
            await self._save_invoice_data(invoice_id, invoice_data)
            
            # Выполняем пост-платежные действия
            await self._execute_post_payment_actions(invoice_data)
            
            logger.success(f"✅ Stars платеж обработан: {invoice_id}")
            
            return {
                "success": True,
                "invoice_id": invoice_id,
                "status": "paid"
            }
            
        except Exception as e:
            logger.error(f"Ошибка обработки Stars платежа: {e}")
            return {"success": False, "error": str(e)}

    # =====================================================
    # ЮЗЕРБОТ ФУНКЦИОНАЛ И КОНТЕКСТ
    # =====================================================
    
    async def create_userbot_session(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создание юзербот сессии с авторизацией
        """
        try:
            session_name = context.get("session_name", "default_userbot")
            phone_number = context.get("phone_number")
            
            if not phone_number:
                return {"success": False, "error": "Номер телефона обязателен"}
            
            logger.info(f"👤 Создаю юзербот сессию: {session_name}")
            
            # Создаем клиент
            userbot = Client(
                session_name,
                api_id=self.settings.get("api_id"),
                api_hash=self.settings.get("api_hash"),
                phone_number=phone_number
            )
            
            # Авторизация (в реальности нужен код из SMS)
            # await userbot.start()
            
            # Сохраняем сессию
            self.userbot_sessions[session_name] = userbot
            
            # Сохраняем в БД
            session_data = {
                "session_name": session_name,
                "phone_number": phone_number,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "conversations": {},
                "contacts": {}
            }
            
            await self._save_session_data(session_name, session_data)
            
            logger.success(f"✅ Юзербот сессия {session_name} создана")
            
            return {
                "success": True,
                "session_name": session_name,
                "phone_number": phone_number
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания юзербот сессии: {e}")
            return {"success": False, "error": str(e)}

    async def userbot_send_message(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отправка сообщения через юзербот с сохранением контекста
        """
        try:
            session_name = context.get("session_name", "default_userbot")
            chat_id = context.get("chat_id")
            text = context.get("text", "")
            save_context = context.get("save_context", True)
            
            logger.info(f"📤 Отправляю сообщение через {session_name} в {chat_id}")
            
            # Получаем юзербот сессию
            userbot = await self._get_userbot_session(session_name)
            if not userbot:
                return {"success": False, "error": "Юзербот сессия недоступна"}
            
            # Отправляем сообщение
            message = await userbot.send_message(chat_id, text)
            
            # Сохраняем контекст
            if save_context:
                await self._save_message_context(session_name, chat_id, {
                    "type": "outgoing",
                    "text": text,
                    "message_id": message.id,
                    "timestamp": datetime.now().isoformat(),
                    "chat_info": await self._get_chat_info(userbot, chat_id)
                })
            
            logger.success(f"✅ Сообщение отправлено: {message.id}")
            
            return {
                "success": True,
                "message_id": message.id,
                "chat_id": chat_id,
                "text": text
            }
            
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return {"success": False, "error": str(e)}

    async def userbot_get_messages(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Получение сообщений из чата с сохранением контекста
        """
        try:
            session_name = context.get("session_name", "default_userbot")
            chat_id = context.get("chat_id")
            limit = context.get("limit", 10)
            save_context = context.get("save_context", True)
            
            logger.info(f"📥 Получаю сообщения из {chat_id} через {session_name}")
            
            # Получаем юзербот сессию
            userbot = await self._get_userbot_session(session_name)
            if not userbot:
                return {"success": False, "error": "Юзербот сессия недоступна"}
            
            messages = []
            async for message in userbot.get_chat_history(chat_id, limit=limit):
                msg_data = {
                    "message_id": message.id,
                    "text": message.text or "",
                    "from_user": {
                        "id": message.from_user.id if message.from_user else None,
                        "username": message.from_user.username if message.from_user else None,
                        "first_name": message.from_user.first_name if message.from_user else None
                    },
                    "date": message.date.isoformat() if message.date else None,
                    "reply_to": message.reply_to_message_id
                }
                messages.append(msg_data)
                
                # Сохраняем контекст каждого сообщения
                if save_context:
                    await self._save_message_context(session_name, chat_id, {
                        "type": "incoming",
                        "message_data": msg_data,
                        "timestamp": datetime.now().isoformat()
                    })
            
            logger.success(f"✅ Получено {len(messages)} сообщений")
            
            return {
                "success": True,
                "messages": messages,
                "count": len(messages),
                "chat_id": chat_id
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения сообщений: {e}")
            return {"success": False, "error": str(e)}

    async def userbot_create_channel(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создание канала через юзербот
        """
        try:
            session_name = context.get("session_name", "default_userbot")
            title = context.get("title", f"AutoChannel_{random.randint(1000, 9999)}")
            description = context.get("description", "Автоматически созданный канал")
            
            logger.info(f"📢 Создаю канал '{title}' через {session_name}")
            
            # Получаем юзербот сессию
            userbot = await self._get_userbot_session(session_name)
            if not userbot:
                return {"success": False, "error": "Юзербот сессия недоступна"}
            
            # Создаем канал
            channel = await userbot.create_channel(title, description)
            
            # Сохраняем информацию о канале
            channel_data = {
                "channel_id": channel.id,
                "title": title,
                "description": description,
                "username": channel.username,
                "created_at": datetime.now().isoformat(),
                "creator_session": session_name,
                "members_count": 1,
                "posts": []
            }
            
            await self._save_channel_data(channel.id, channel_data)
            
            logger.success(f"✅ Канал создан: @{channel.username} (ID: {channel.id})")
            
            return {
                "success": True,
                "channel_id": channel.id,
                "title": title,
                "username": channel.username,
                "invite_link": f"https://t.me/{channel.username}"
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания канала: {e}")
            return {"success": False, "error": str(e)}

    async def userbot_monitor_chats(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Мониторинг чатов в реальном времени
        """
        try:
            session_name = context.get("session_name", "default_userbot")
            chat_ids = context.get("chat_ids", [])
            keywords = context.get("keywords", [])
            
            logger.info(f"👁️ Начинаю мониторинг чатов через {session_name}")
            
            # Получаем юзербот сессию
            userbot = await self._get_userbot_session(session_name)
            if not userbot:
                return {"success": False, "error": "Юзербот сессия недоступна"}
            
            # Создаем мониторинг (в реальности - обработчик событий)
            monitor_id = f"monitor_{self._generate_random_string(16)}"
            
            monitor_data = {
                "monitor_id": monitor_id,
                "session_name": session_name,
                "chat_ids": chat_ids,
                "keywords": keywords,
                "started_at": datetime.now().isoformat(),
                "status": "active",
                "messages_caught": 0
            }
            
            # Сохраняем мониторинг
            self.active_conversations[monitor_id] = monitor_data
            
            logger.success(f"✅ Мониторинг запущен: {monitor_id}")
            
            return {
                "success": True,
                "monitor_id": monitor_id,
                "chat_ids": chat_ids,
                "keywords": keywords
            }
            
        except Exception as e:
            logger.error(f"Ошибка мониторинга чатов: {e}")
            return {"success": False, "error": str(e)}

    # =====================================================
    # РЕГИСТРАЦИЯ HANDLERS
    # =====================================================
    
    def register_handlers(self) -> Dict[str, Callable]:
        """Регистрация всех handlers плагина"""
        return {
            # Создание ботов
            "telegram_create_bot": self.create_bot_via_botfather,
            "telegram_setup_bot": self._setup_new_bot_handler,
            "telegram_delete_bot": self._delete_bot_handler,
            
            # TON кошельки
            "ton_create_wallet": self.create_ton_wallet,
            "ton_send_payment": self.send_ton_payment,
            "ton_check_balance": self._check_ton_balance,
            "ton_get_transactions": self._get_ton_transactions,
            
            # Stars платежи
            "stars_create_invoice": self.create_stars_invoice,
            "stars_handle_payment": self.handle_stars_payment,
            "stars_check_status": self._check_stars_status,
            
            # Юзербот функции
            "userbot_create_session": self.create_userbot_session,
            "userbot_send_message": self.userbot_send_message,
            "userbot_get_messages": self.userbot_get_messages,
            "userbot_create_channel": self.userbot_create_channel,
            "userbot_monitor_chats": self.userbot_monitor_chats,
            "userbot_join_chat": self._userbot_join_chat,
            "userbot_leave_chat": self._userbot_leave_chat,
            
            # Управление контекстом
            "telegram_save_context": self._save_context_handler,
            "telegram_get_context": self._get_context_handler,
            "telegram_clear_context": self._clear_context_handler,
            
            # Утилиты
            "telegram_get_stats": self._get_telegram_stats,
            "telegram_health_check": self.healthcheck,
        }

    # =====================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # =====================================================
    
    async def _get_userbot_session(self, session_name: str) -> Optional[Client]:
        """Получение юзербот сессии"""
        try:
            if session_name in self.userbot_sessions:
                return self.userbot_sessions[session_name]
            
            # Пытаемся загрузить сессию из БД
            session_data = await self._load_session_data(session_name)
            if session_data:
                userbot = Client(
                    session_name,
                    api_id=self.settings.get("api_id"),
                    api_hash=self.settings.get("api_hash"),
                    phone_number=session_data.get("phone_number")
                )
                self.userbot_sessions[session_name] = userbot
                return userbot
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения юзербот сессии: {e}")
            return None

    async def _get_bot_client(self, token: str) -> Optional[Client]:
        """Получение бот клиента"""
        try:
            bot_client = Client(
                f"bot_{token[:10]}",
                bot_token=token,
                api_id=self.settings.get("api_id"),
                api_hash=self.settings.get("api_hash")
            )
            return bot_client
        except Exception as e:
            logger.error(f"Ошибка создания бот клиента: {e}")
            return None

    # =====================================================
    # МЕТОДЫ РАБОТЫ С БАЗОЙ ДАННЫХ
    # =====================================================
    
    async def _save_bot_token(self, username: str, token: str, name: str):
        """Сохранение токена бота в БД"""
        try:
            bot_data = {
                "username": username,
                "token": token,
                "name": name,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Используем MongoDB плагин для сохранения
            if hasattr(self, 'mongo_collection'):
                await self.mongo_collection.update_one(
                    {"type": "bot_token", "username": username},
                    {"$set": bot_data},
                    upsert=True
                )
            
        except Exception as e:
            logger.error(f"Ошибка сохранения токена бота: {e}")

    async def _save_wallet_data(self, wallet_name: str, wallet_data: Dict):
        """Сохранение данных кошелька"""
        try:
            wallet_data["type"] = "ton_wallet"
            wallet_data["wallet_name"] = wallet_name
            
            if hasattr(self, 'mongo_collection'):
                await self.mongo_collection.update_one(
                    {"type": "ton_wallet", "wallet_name": wallet_name},
                    {"$set": wallet_data},
                    upsert=True
                )
                
        except Exception as e:
            logger.error(f"Ошибка сохранения кошелька: {e}")

    async def _load_wallet_data(self, wallet_name: str) -> Optional[Dict]:
        """Загрузка данных кошелька"""
        try:
            if hasattr(self, 'mongo_collection'):
                result = await self.mongo_collection.find_one({
                    "type": "ton_wallet",
                    "wallet_name": wallet_name
                })
                return result
            return None
            
        except Exception as e:
            logger.error(f"Ошибка загрузки кошелька: {e}")
            return None

    async def _save_session_data(self, session_name: str, session_data: Dict):
        """Сохранение данных сессии"""
        try:
            session_data["type"] = "userbot_session"
            session_data["session_name"] = session_name
            
            if hasattr(self, 'mongo_collection'):
                await self.mongo_collection.update_one(
                    {"type": "userbot_session", "session_name": session_name},
                    {"$set": session_data},
                    upsert=True
                )
                
        except Exception as e:
            logger.error(f"Ошибка сохранения сессии: {e}")

    async def _load_session_data(self, session_name: str) -> Optional[Dict]:
        """Загрузка данных сессии"""
        try:
            if hasattr(self, 'mongo_collection'):
                result = await self.mongo_collection.find_one({
                    "type": "userbot_session",
                    "session_name": session_name
                })
                return result
            return None
            
        except Exception as e:
            logger.error(f"Ошибка загрузки сессии: {e}")
            return None

    async def _save_message_context(self, session_name: str, chat_id: str, context_data: Dict):
        """Сохранение контекста сообщения"""
        try:
            context_data["type"] = "message_context"
            context_data["session_name"] = session_name
            context_data["chat_id"] = str(chat_id)
            context_data["id"] = f"{session_name}_{chat_id}_{context_data.get('message_id', '')}"
            
            if hasattr(self, 'mongo_collection'):
                await self.mongo_collection.insert_one(context_data)
                
        except Exception as e:
            logger.error(f"Ошибка сохранения контекста: {e}")

    def _generate_ton_seed(self) -> str:
        """Генерация TON seed фразы (24 слова)"""
        # В реальности использовать криптографически стойкий генератор
        words = ["abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", 
                "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
                "acoustic", "acquire", "across", "act", "action", "actor", "actress", "actual"]
        return " ".join(random.choices(words, k=24))

    def _generate_ton_address(self) -> str:
        """Генерация TON адреса"""
        # В реальности использовать TON SDK
        return f"EQ{self._generate_random_string(48)}"

    async def healthcheck(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Проверка состояния плагина"""
        try:
            status = {
                "plugin_name": self.name,
                "version": self.version,
                "pyrogram_available": PYROGRAM_AVAILABLE,
                "active_sessions": len(self.userbot_sessions),
                "stored_bot_tokens": len(self.bot_tokens),
                "active_monitors": len(self.active_conversations),
                "settings_configured": bool(
                    self.settings.get("api_id") and self.settings.get("api_hash")
                )
            }
            
            return {"success": True, "status": status}
            
        except Exception as e:
            logger.error(f"Ошибка healthcheck: {e}")
            return {"success": False, "error": str(e)} 