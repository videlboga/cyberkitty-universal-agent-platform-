#!/usr/bin/env python3
"""
🤖 TELEGRAM MOCK SERVER
Симуляция Telegram Bot API для автотестов OntoBot сценариев

Возможности:
- Полная имитация Telegram Bot API
- Сохранение истории сообщений
- Симуляция пользовательских действий
- Webhook поддержка для тестирования
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from loguru import logger

# Настройка логирования
logger.add(
    "logs/telegram_mock.log",
    rotation="10 MB",
    retention="7 days",
    compression="gz",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | MOCK | {message}",
    level="DEBUG"
)

# === МОДЕЛИ ДАННЫХ ===

@dataclass
class MockUser:
    """Мок пользователя Telegram."""
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: str = "ru"
    is_bot: bool = False

@dataclass
class MockChat:
    """Мок чата Telegram."""
    id: int
    type: str = "private"  # private, group, supergroup, channel
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

@dataclass
class MockMessage:
    """Мок сообщения Telegram."""
    message_id: int
    date: int
    chat: MockChat
    from_user: MockUser
    text: Optional[str] = None
    reply_markup: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в формат Telegram API."""
        return {
            "message_id": self.message_id,
            "date": self.date,
            "chat": asdict(self.chat),
            "from": asdict(self.from_user),
            "text": self.text,
            "reply_markup": self.reply_markup
        }

@dataclass
class MockCallbackQuery:
    """Мок callback query Telegram."""
    id: str
    from_user: MockUser
    message: MockMessage
    data: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в формат Telegram API."""
        return {
            "id": self.id,
            "from": asdict(self.from_user),
            "message": self.message.to_dict(),
            "data": self.data
        }

@dataclass
class MockUpdate:
    """Мок update Telegram."""
    update_id: int
    message: Optional[MockMessage] = None
    callback_query: Optional[MockCallbackQuery] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в формат Telegram API."""
        result = {"update_id": self.update_id}
        if self.message:
            result["message"] = self.message.to_dict()
        if self.callback_query:
            result["callback_query"] = self.callback_query.to_dict()
        return result

# === TELEGRAM MOCK SERVER ===

class TelegramMockServer:
    """
    Мок сервер Telegram Bot API.
    
    Симулирует все основные методы Telegram API:
    - sendMessage
    - editMessageText
    - sendDocument
    - answerCallbackQuery
    - getUpdates
    """
    
    def __init__(self):
        self.app = FastAPI(title="Telegram Mock Server", version="1.0.0")
        self.messages: List[MockMessage] = []
        self.updates: List[MockUpdate] = []
        self.users: Dict[int, MockUser] = {}
        self.chats: Dict[int, MockChat] = {}
        self.message_counter = 1
        self.update_counter = 1
        self.callback_counter = 1
        self.webhook_url: Optional[str] = None
        
        # Настройка роутов
        self._setup_routes()
        
        logger.info("🤖 Telegram Mock Server инициализирован")
    
    def _setup_routes(self):
        """Настраивает API роуты."""
        
        @self.app.get("/")
        async def root():
            return {
                "ok": True,
                "result": {
                    "server": "Telegram Mock Server",
                    "version": "1.0.0",
                    "messages_count": len(self.messages),
                    "updates_count": len(self.updates),
                    "users_count": len(self.users)
                }
            }
        
        @self.app.post("/bot{token}/sendMessage")
        async def send_message(token: str, request: Request):
            """Симуляция sendMessage."""
            data = await request.json()
            
            chat_id = int(data.get("chat_id"))
            text = data.get("text", "")
            parse_mode = data.get("parse_mode")
            reply_markup = data.get("reply_markup")
            
            # Создаем или получаем чат
            chat = self._get_or_create_chat(chat_id)
            
            # Создаем пользователя бота
            bot_user = MockUser(
                id=0,
                first_name="OntoBot",
                username="mr_ontobot",
                is_bot=True
            )
            
            # Создаем сообщение
            message = MockMessage(
                message_id=self.message_counter,
                date=int(time.time()),
                chat=chat,
                from_user=bot_user,
                text=text,
                reply_markup=reply_markup
            )
            
            self.messages.append(message)
            self.message_counter += 1
            
            logger.info(f"📤 Отправлено сообщение в чат {chat_id}: {text[:50]}...")
            
            return {
                "ok": True,
                "result": message.to_dict()
            }
        
        @self.app.post("/bot{token}/editMessageText")
        async def edit_message_text(token: str, request: Request):
            """Симуляция editMessageText."""
            data = await request.json()
            
            chat_id = int(data.get("chat_id"))
            message_id = int(data.get("message_id"))
            text = data.get("text", "")
            reply_markup = data.get("reply_markup")
            
            # Находим сообщение для редактирования
            for message in self.messages:
                if message.chat.id == chat_id and message.message_id == message_id:
                    message.text = text
                    message.reply_markup = reply_markup
                    
                    logger.info(f"✏️ Отредактировано сообщение {message_id} в чате {chat_id}")
                    
                    return {
                        "ok": True,
                        "result": message.to_dict()
                    }
            
            raise HTTPException(status_code=400, detail="Message not found")
        
        @self.app.post("/bot{token}/sendDocument")
        async def send_document(token: str, request: Request):
            """Симуляция sendDocument."""
            data = await request.json()
            
            chat_id = int(data.get("chat_id"))
            document = data.get("document")
            caption = data.get("caption", "")
            
            chat = self._get_or_create_chat(chat_id)
            bot_user = MockUser(id=0, first_name="OntoBot", is_bot=True)
            
            message = MockMessage(
                message_id=self.message_counter,
                date=int(time.time()),
                chat=chat,
                from_user=bot_user,
                text=f"📄 Документ: {document}\n{caption}"
            )
            
            self.messages.append(message)
            self.message_counter += 1
            
            logger.info(f"📄 Отправлен документ в чат {chat_id}: {document}")
            
            return {
                "ok": True,
                "result": message.to_dict()
            }
        
        @self.app.post("/bot{token}/answerCallbackQuery")
        async def answer_callback_query(token: str, request: Request):
            """Симуляция answerCallbackQuery."""
            data = await request.json()
            
            callback_query_id = data.get("callback_query_id")
            text = data.get("text", "")
            show_alert = data.get("show_alert", False)
            
            logger.info(f"✅ Ответ на callback {callback_query_id}: {text}")
            
            return {
                "ok": True,
                "result": True
            }
        
        @self.app.get("/bot{token}/getUpdates")
        async def get_updates(token: str, offset: int = 0, limit: int = 100):
            """Симуляция getUpdates."""
            
            # Возвращаем updates начиная с offset
            result_updates = []
            for update in self.updates:
                if update.update_id >= offset:
                    result_updates.append(update.to_dict())
                    if len(result_updates) >= limit:
                        break
            
            logger.debug(f"📥 getUpdates: offset={offset}, возвращено {len(result_updates)} updates")
            
            return {
                "ok": True,
                "result": result_updates
            }
        
        @self.app.post("/bot{token}/setWebhook")
        async def set_webhook(token: str, request: Request):
            """Симуляция setWebhook."""
            data = await request.json()
            
            self.webhook_url = data.get("url", "")
            
            logger.info(f"🔗 Webhook установлен: {self.webhook_url}")
            
            return {
                "ok": True,
                "result": True,
                "description": "Webhook was set"
            }
        
        @self.app.post("/bot{token}/deleteWebhook")
        async def delete_webhook(token: str):
            """Симуляция deleteWebhook."""
            self.webhook_url = None
            
            logger.info("🗑️ Webhook удален")
            
            return {
                "ok": True,
                "result": True,
                "description": "Webhook was deleted"
            }
        
        # === ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ДЛЯ ТЕСТИРОВАНИЯ ===
        
        @self.app.get("/mock/stats")
        async def get_mock_stats():
            """Статистика мок сервера."""
            return {
                "messages_count": len(self.messages),
                "updates_count": len(self.updates),
                "users_count": len(self.users),
                "chats_count": len(self.chats),
                "webhook_url": self.webhook_url
            }
        
        @self.app.get("/mock/messages")
        async def get_messages(chat_id: Optional[int] = None, limit: int = 50):
            """Получение истории сообщений."""
            messages = self.messages
            
            if chat_id:
                messages = [m for m in messages if m.chat.id == chat_id]
            
            # Последние сообщения
            messages = messages[-limit:]
            
            return {
                "messages": [m.to_dict() for m in messages],
                "count": len(messages)
            }
        
        @self.app.post("/mock/simulate_user_message")
        async def simulate_user_message(request: Request):
            """Симуляция сообщения от пользователя."""
            data = await request.json()
            
            user_id = int(data.get("user_id"))
            chat_id = int(data.get("chat_id", user_id))
            text = data.get("text", "")
            first_name = data.get("first_name", "Тестовый")
            username = data.get("username")
            
            # Создаем или получаем пользователя и чат
            user = self._get_or_create_user(user_id, first_name, username)
            chat = self._get_or_create_chat(chat_id, first_name)
            
            # Создаем сообщение от пользователя
            message = MockMessage(
                message_id=self.message_counter,
                date=int(time.time()),
                chat=chat,
                from_user=user,
                text=text
            )
            
            # Создаем update
            update = MockUpdate(
                update_id=self.update_counter,
                message=message
            )
            
            self.messages.append(message)
            self.updates.append(update)
            self.message_counter += 1
            self.update_counter += 1
            
            logger.info(f"👤 Симуляция сообщения от пользователя {user_id}: {text}")
            
            # Если установлен webhook, отправляем update
            if self.webhook_url:
                await self._send_webhook_update(update)
            
            return {
                "ok": True,
                "result": update.to_dict()
            }
        
        @self.app.post("/mock/simulate_callback_query")
        async def simulate_callback_query(request: Request):
            """Симуляция callback query от пользователя."""
            data = await request.json()
            
            user_id = int(data.get("user_id"))
            chat_id = int(data.get("chat_id", user_id))
            callback_data = data.get("callback_data", "")
            message_id = int(data.get("message_id", self.message_counter - 1))
            first_name = data.get("first_name", "Тестовый")
            username = data.get("username")
            
            # Создаем или получаем пользователя и чат
            user = self._get_or_create_user(user_id, first_name, username)
            chat = self._get_or_create_chat(chat_id, first_name)
            
            # Находим исходное сообщение
            original_message = None
            for msg in self.messages:
                if msg.message_id == message_id and msg.chat.id == chat_id:
                    original_message = msg
                    break
            
            if not original_message:
                # Создаем фиктивное сообщение
                original_message = MockMessage(
                    message_id=message_id,
                    date=int(time.time()) - 60,
                    chat=chat,
                    from_user=MockUser(id=0, first_name="OntoBot", is_bot=True),
                    text="Кнопочное сообщение"
                )
            
            # Создаем callback query
            callback_query = MockCallbackQuery(
                id=str(self.callback_counter),
                from_user=user,
                message=original_message,
                data=callback_data
            )
            
            # Создаем update
            update = MockUpdate(
                update_id=self.update_counter,
                callback_query=callback_query
            )
            
            self.updates.append(update)
            self.callback_counter += 1
            self.update_counter += 1
            
            logger.info(f"🔘 Симуляция callback от пользователя {user_id}: {callback_data}")
            
            # Если установлен webhook, отправляем update
            if self.webhook_url:
                await self._send_webhook_update(update)
            
            return {
                "ok": True,
                "result": update.to_dict()
            }
        
        @self.app.delete("/mock/clear")
        async def clear_mock_data():
            """Очистка всех данных мок сервера."""
            self.messages.clear()
            self.updates.clear()
            self.users.clear()
            self.chats.clear()
            self.message_counter = 1
            self.update_counter = 1
            self.callback_counter = 1
            
            logger.info("🧹 Данные мок сервера очищены")
            
            return {
                "ok": True,
                "result": "Mock data cleared"
            }
    
    def _get_or_create_user(self, user_id: int, first_name: str, username: Optional[str] = None) -> MockUser:
        """Создает или получает пользователя."""
        if user_id not in self.users:
            self.users[user_id] = MockUser(
                id=user_id,
                first_name=first_name,
                username=username
            )
        return self.users[user_id]
    
    def _get_or_create_chat(self, chat_id: int, first_name: Optional[str] = None) -> MockChat:
        """Создает или получает чат."""
        if chat_id not in self.chats:
            self.chats[chat_id] = MockChat(
                id=chat_id,
                type="private",
                first_name=first_name
            )
        return self.chats[chat_id]
    
    async def _send_webhook_update(self, update: MockUpdate):
        """Отправляет update на webhook URL."""
        if not self.webhook_url:
            return
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=update.to_dict(),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        logger.debug(f"📡 Update отправлен на webhook: {update.update_id}")
                    else:
                        logger.warning(f"⚠️ Ошибка webhook: {response.status}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки webhook: {e}")

# === ЗАПУСК СЕРВЕРА ===

async def start_mock_server():
    """Запуск Mock Server."""
    
    mock_server = TelegramMockServer()
    
    config = uvicorn.Config(
        mock_server.app,  # Исправил: используем mock_server.app вместо app
        host="127.0.0.1", 
        port=8082,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    
    logger.info("🚀 Запуск Telegram Mock Server на 127.0.0.1:8082")
    
    try:
        await server.serve()
    except Exception as e:
        logger.error(f"❌ Ошибка запуска сервера: {e}")

if __name__ == "__main__":
    asyncio.run(start_mock_server()) 