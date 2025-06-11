"""
📞 CommunicationTools - Инструменты коммуникации для KittyCore 3.0

Реальные инструменты для связи:
- Email отправка (если настроен SMTP)
- Telegram (заглушки)
- Уведомления
- Простая интеграция с API
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from .base_tool import Tool, ToolResult

# Импорт мощного Telegram инструмента
try:
    from ..telegram_tools import TelegramTool as PowerfulTelegramTool
    POWERFUL_TELEGRAM_AVAILABLE = True
except ImportError:
    # Fallback если мощный инструмент недоступен
    PowerfulTelegramTool = Tool
    POWERFUL_TELEGRAM_AVAILABLE = False


class EmailTool(Tool):
    """Инструмент отправки email"""
    
    def __init__(self, smtp_config: Optional[Dict] = None):
        super().__init__(
            name="email_tool",
            description="Отправка email сообщений через SMTP"
        )
        self.smtp_config = smtp_config or {}
    
    def execute(self, operation: str = "send", to: str = None, subject: str = None, 
               body: str = None, **kwargs) -> ToolResult:
        """Выполнить email операцию"""
        try:
            if operation == "send":
                return self._send_email(to, subject, body, **kwargs)
            elif operation == "validate_config":
                return self._validate_config()
            else:
                return ToolResult(
                    success=False,
                    error=f"Неизвестная операция: {operation}"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка email операции: {str(e)}"
            )
    
    def _send_email(self, to: str, subject: str, body: str, **kwargs) -> ToolResult:
        """Отправить email"""
        if not all([to, subject, body]):
            return ToolResult(
                success=False,
                error="Требуются параметры: to, subject, body"
            )
        
        # Заглушка - в production настроить SMTP
        return ToolResult(
            success=True,
            data={
                "operation": "send_email",
                "to": to,
                "subject": subject,
                "body_length": len(body),
                "status": "simulated_send",
                "note": "Для реальной отправки настройте SMTP конфигурацию"
            }
        )
    
    def _validate_config(self) -> ToolResult:
        """Проверить конфигурацию"""
        return ToolResult(
            success=True,
            data={
                "operation": "validate_config",
                "valid": False,
                "note": "SMTP конфигурация не настроена"
            }
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["send", "validate_config"],
                    "description": "Email операция",
                    "default": "send"
                },
                "to": {
                    "type": "string",
                    "description": "Email получателя"
                },
                "subject": {
                    "type": "string",
                    "description": "Тема сообщения"
                },
                "body": {
                    "type": "string",
                    "description": "Текст сообщения"
                }
            },
            "required": []
        }


class TelegramTool(PowerfulTelegramTool):
    """Мощный Telegram инструмент KittyCore 3.0 - ПОЛНАЯ ЭКОСИСТЕМА!
    
    🚀 Возможности:
    - Создание ботов через @BotFather автоматически  
    - TON кошельки и платежи
    - Telegram Stars интеграция
    - Юзерботы с Pyrogram
    - Управление каналами/группами
    - Мониторинг чатов
    """
    
    def __init__(self, bot_token: Optional[str] = None):
        if POWERFUL_TELEGRAM_AVAILABLE:
            # Используем мощный инструмент как основу
            super().__init__()
            # Переопределяем имя для совместимости
            self.name = "telegram_tool"
        else:
            # Fallback к базовому Tool
            Tool.__init__(self, 
                name="telegram_tool",
                description="Базовый Telegram инструмент (мощный недоступен)"
            )
        
        # Добавляем совместимость со старым API
        self.bot_token = bot_token
        if not self.bot_token:
            import os
            self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    def execute(self, operation: str = "send_message", chat_id: str = None, 
               text: str = None, **kwargs) -> ToolResult:
        """Выполнить Telegram операцию - используем МОЩНЫЙ базовый класс!"""
        
        # Маппинг старых операций на новые действия мощного инструмента
        operation_mapping = {
            "send_message": "send_message",
            "get_me": "get_bot_info", 
            "get_updates": "get_messages",
            "send_photo": "send_message",  # В мощном инструменте это через send_message
            "send_document": "send_message", # В мощном инструменте это через send_message  
            "delete_message": "send_message", # В мощном инструменте это через API
            "validate_token": "health_check"
        }
        
        # Используем мощный базовый инструмент или fallback
        if POWERFUL_TELEGRAM_AVAILABLE and operation in operation_mapping:
            action = operation_mapping[operation]
            
            # Подготавливаем параметры для мощного инструмента
            params = {
                "action": action,
                "chat_id": chat_id,
                "message": text,
                **kwargs
            }
            
            return super().execute(**params)
        elif not POWERFUL_TELEGRAM_AVAILABLE:
            return ToolResult(
                success=False,
                error="Мощный Telegram инструмент недоступен. Установите pyrogram: pip install pyrogram",
                data={
                    "operation": operation,
                    "required_dependencies": ["pyrogram", "aiohttp", "aiofiles"],
                    "telegram_tools_path": "kittycore.telegram_tools"
                }
            )
        else:
            return ToolResult(
                success=False,
                error=f"Операция {operation} не поддерживается. Используйте мощный API: create_bot, create_userbot, send_ton, create_stars_invoice и др."
            )
    
    # Все методы унаследованы от PowerfulTelegramTool!
    # Доступны операции: create_bot, create_userbot, send_ton, create_stars_invoice и многое другое!
    
    def get_schema(self) -> Dict[str, Any]:
        """Унаследованная схема от мощного Telegram инструмента + совместимость"""
        
        if POWERFUL_TELEGRAM_AVAILABLE:
            # Получаем полную схему от PowerfulTelegramTool
            base_schema = super().get_schema()
            
            # Добавляем совместимость со старыми операциями
            base_schema["properties"]["operation"] = {
                "type": "string",
                "enum": [
                    # Старые совместимые операции
                    "send_message", "get_me", "get_updates", 
                    "send_photo", "send_document", "delete_message", "validate_token",
                    # МОЩНЫЕ операции от PowerfulTelegramTool
                    "create_bot", "setup_bot", "delete_bot",
                    "create_ton_wallet", "send_ton", "check_ton_balance", 
                    "create_stars_invoice", "handle_stars_payment",
                    "create_userbot", "create_channel", "join_channel", "monitor_chats",
                    "health_check"
                ],
                "description": "🚀 МОЩНАЯ Telegram операция - полная экосистема!"
            }
            
            # Добавляем старые параметры для совместимости
            base_schema["properties"].update({
                "text": {
                    "type": "string", 
                    "description": "Текст сообщения (совместимость)"
                },
                "parse_mode": {
                    "type": "string",
                    "enum": ["HTML", "Markdown"],
                    "description": "Режим парсинга текста",
                    "default": "HTML"
                }
            })
            
            return base_schema
        else:
            # Fallback схема
            return {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["send_message", "get_me"],
                        "description": "Базовая Telegram операция (мощный инструмент недоступен)"
                    },
                    "chat_id": {
                        "type": "string",
                        "description": "ID чата"
                    },
                    "text": {
                        "type": "string",
                        "description": "Текст сообщения"
                    }
                },
                "required": []
            }


class NotificationTool(Tool):
    """Простые уведомления в консоль и файлы"""
    
    def __init__(self):
        super().__init__(
            name="notification_tool",
            description="Простые уведомления в консоль и файлы"
        )
    
    def execute(self, operation: str = "console", message: str = None, 
               level: str = "info", **kwargs) -> ToolResult:
        """Выполнить уведомление"""
        try:
            if operation == "console":
                return self._console_notification(message, level)
            elif operation == "file":
                return self._file_notification(message, kwargs.get("filename", "notifications.log"))
            elif operation == "json_log":
                return self._json_log_notification(message, level, **kwargs)
            else:
                return ToolResult(
                    success=False,
                    error=f"Неизвестная операция: {operation}"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка уведомления: {str(e)}"
            )
    
    def _console_notification(self, message: str, level: str) -> ToolResult:
        """Уведомление в консоль"""
        if not message:
            return ToolResult(
                success=False,
                error="Сообщение не указано"
            )
        
        # Форматирование по уровню
        level_formats = {
            "info": f"ℹ️  {message}",
            "warning": f"⚠️  {message}",
            "error": f"❌ {message}",
            "success": f"✅ {message}",
            "debug": f"🔍 {message}"
        }
        
        formatted_message = level_formats.get(level.lower(), f"📝 {message}")
        
        print(formatted_message)
        
        return ToolResult(
            success=True,
            data={
                "operation": "console_notification",
                "message": message,
                "level": level,
                "formatted": formatted_message
            }
        )
    
    def _file_notification(self, message: str, filename: str) -> ToolResult:
        """Уведомление в файл"""
        if not message:
            return ToolResult(
                success=False,
                error="Сообщение не указано"
            )
        
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            return ToolResult(
                success=True,
                data={
                    "operation": "file_notification",
                    "message": message,
                    "filename": filename,
                    "timestamp": timestamp
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка записи в файл: {str(e)}"
            )
    
    def _json_log_notification(self, message: str, level: str, **kwargs) -> ToolResult:
        """Структурированное JSON логирование"""
        if not message:
            return ToolResult(
                success=False,
                error="Сообщение не указано"
            )
        
        try:
            from datetime import datetime
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message,
                "source": "KittyCore",
                "metadata": kwargs
            }
            
            filename = kwargs.get("filename", "notifications.json")
            
            # Добавляем к существующему файлу или создаем новый
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = []
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []
            
            logs.append(log_entry)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            
            return ToolResult(
                success=True,
                data={
                    "operation": "json_log_notification",
                    "log_entry": log_entry,
                    "filename": filename,
                    "total_logs": len(logs)
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка JSON логирования: {str(e)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["console", "file", "json_log"],
                    "description": "Тип уведомления",
                    "default": "console"
                },
                "message": {
                    "type": "string",
                    "description": "Текст уведомления"
                },
                "level": {
                    "type": "string",
                    "enum": ["info", "warning", "error", "success", "debug"],
                    "description": "Уровень уведомления",
                    "default": "info"
                },
                "filename": {
                    "type": "string",
                    "description": "Имя файла для записи",
                    "default": "notifications.log"
                }
            },
            "required": ["message"]
        } 