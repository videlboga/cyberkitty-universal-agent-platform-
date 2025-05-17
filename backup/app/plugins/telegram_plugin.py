from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
import asyncio
from loguru import logger
import os

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/telegram_plugin.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

class TelegramPlugin:
    def __init__(self, app):
        self.app = app
        self.add_handlers()
        logger.info("Telegram Plugin инициализирован")

    def add_handlers(self):
        # Обработчики команд
        self.app.add_handler(CommandHandler("start", self.on_start))
        self.app.add_handler(CommandHandler("help", self.on_help))
        
        # Обработчики различных типов сообщений
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_text))
        self.app.add_handler(MessageHandler(filters.VOICE, self.on_voice))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.on_photo))
        self.app.add_handler(MessageHandler(filters.Document.ALL, self.on_document))
        self.app.add_handler(MessageHandler(filters.VIDEO, self.on_video))
        self.app.add_handler(MessageHandler(filters.AUDIO, self.on_audio))
        self.app.add_handler(MessageHandler(filters.Sticker.ALL, self.on_sticker))
        self.app.add_handler(MessageHandler(filters.CONTACT, self.on_contact))
        self.app.add_handler(MessageHandler(filters.LOCATION, self.on_location))
        self.app.add_handler(CallbackQueryHandler(self.on_callback_query))
        
        logger.info(f"Зарегистрировано {len(self.app.handlers)} обработчиков")

    async def on_start(self, update: Update, context):
        """Обработка команды /start: отправка меню выбора агента с inline-кнопками"""
        user = update.effective_user
        logger.info(f"Команда /start от пользователя {user.id} (@{user.username})")
        
        buttons = [
            [InlineKeyboardButton("Коуч", callback_data="agent_coach")],
            [InlineKeyboardButton("Лайфхакер", callback_data="agent_lifehacker")],
            [InlineKeyboardButton("Ментор", callback_data="agent_mentor")],
            [InlineKeyboardButton("Дайджест", callback_data="agent_digest")],
            [InlineKeyboardButton("Эксперт", callback_data="agent_expert")],
        ]
        markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            f"Привет, {user.first_name}! Выберите агента:",
            reply_markup=markup
        )
    
    async def on_help(self, update: Update, context):
        """Обработка команды /help: отправка справки"""
        text = """
*Доступные команды:*
/start - Выбрать агента
/help - Эта справка

*Доступные агенты:*
• Коуч - подскажет, как достичь ваших целей
• Лайфхакер - поделится полезными советами
• Ментор - поможет в обучении
• Дайджест - соберет новости по вашим интересам
• Эксперт - ответит на сложные вопросы
        """
        await update.message.reply_text(text, parse_mode="Markdown")

    async def on_text(self, update: Update, context):
        """Обработка текстовых сообщений"""
        user = update.effective_user
        text = update.message.text
        logger.info(f"Сообщение от {user.id} (@{user.username}): {text[:50]}")
        
        # Простой ответ для MVP
        await update.message.reply_text(f"Я получил ваше сообщение: {text}")

    async def on_voice(self, update: Update, context):
        """Обработка голосовых сообщений"""
        await update.message.reply_text("Я получил голосовое сообщение, но пока не умею его обрабатывать")

    async def on_photo(self, update: Update, context):
        """Обработка фотографий"""
        await update.message.reply_text("Я получил фотографию, но пока не умею её обрабатывать")

    async def on_document(self, update: Update, context):
        """Обработка документов"""
        await update.message.reply_text(f"Я получил документ '{update.message.document.file_name}', но пока не умею его обрабатывать")

    async def on_video(self, update: Update, context):
        """Обработка видео"""
        await update.message.reply_text("Я получил видео, но пока не умею его обрабатывать")

    async def on_audio(self, update: Update, context):
        """Обработка аудио"""
        await update.message.reply_text("Я получил аудио, но пока не умею его обрабатывать")

    async def on_sticker(self, update: Update, context):
        """Обработка стикеров"""
        await update.message.reply_text("👍")

    async def on_contact(self, update: Update, context):
        """Обработка контактов"""
        contact = update.message.contact
        await update.message.reply_text(f"Контакт получен: {contact.first_name} {contact.phone_number}")

    async def on_location(self, update: Update, context):
        """Обработка локаций"""
        location = update.message.location
        await update.message.reply_text(f"Локация получена: {location.latitude}, {location.longitude}")

    async def healthcheck(self):
        """Асинхронная проверка работоспособности Telegram-бота через get_me
        Returns:
            bool: True если бот отвечает, иначе False
        """
        try:
            me = await self.app.bot.get_me()
            return True if me else False
        except Exception as e:
            logger.error(f"Ошибка healthcheck: {e}")
            return False

    async def send_reply_keyboard(self, chat_id, text, buttons, resize_keyboard=True, one_time_keyboard=True):
        """Отправить сообщение с ReplyKeyboardMarkup (обычные кнопки)"""
        markup = ReplyKeyboardMarkup(buttons, resize_keyboard=resize_keyboard, one_time_keyboard=one_time_keyboard)
        await self.app.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

    async def send_inline_keyboard(self, chat_id, text, buttons):
        """Отправить сообщение с InlineKeyboardMarkup (inline-кнопки)"""
        markup = InlineKeyboardMarkup(buttons)
        await self.app.bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

    async def on_callback_query(self, update: Update, context):
        """Обработка callback-запросов от inline-кнопок"""
        query = update.callback_query
        data = query.data
        user = query.from_user
        
        logger.info(f"Callback-запрос от {user.id} (@{user.username}): {data}")
        
        try:
            # Получаем DialogStateManager для работы с состоянием
            from app.utils.dialog_state import DialogStateManager
            dialog_state = DialogStateManager()
            
            # Получаем состояние пользователя
            state = await dialog_state.get_state(user.id)
            
            # Импортируем AgentManagerPlugin
            from app.plugins.agent_manager_plugin import AgentManagerPlugin
            agent_manager = AgentManagerPlugin()
            
            # Создаем базовый контекст
            context_data = {
                "user_id": user.id,
                "chat_id": update.effective_chat.id,
                "callback_data": data,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
            
            # Если callback начинается с "agent:", это выбор агента
            if data.startswith("agent:"):
                await query.answer(f"Выбран агент: {data.split(':', 1)[1]}")
                
                # Обрабатываем callback через AgentManagerPlugin
                updated_context = await agent_manager.process_callback(data, context_data)
                
                # Отправляем приветственное сообщение
                if "welcome_message" in updated_context:
                    await query.edit_message_text(updated_context["welcome_message"])
                    
                # Обновляем состояние
                await dialog_state.update_step(user.id, "agent_active", updated_context)
                
            # Если callback = "menu", возвращаемся в главное меню
            elif data == "menu":
                await query.answer("Возврат в главное меню")
                
                # Обрабатываем callback через AgentManagerPlugin
                updated_context = await agent_manager.process_callback(data, context_data)
                
                # Получаем информацию о меню
                if "agent_menu" in updated_context:
                    menu = updated_context["agent_menu"]
                    text = menu.get("text", "Выберите агента:")
                    reply_markup = menu.get("reply_markup")
                    
                    # Создаем клавиатуру
                    keyboard = []
                    for row in reply_markup.get("inline_keyboard", []):
                        keyboard_row = []
                        for btn in row:
                            keyboard_row.append(InlineKeyboardButton(btn[0], callback_data=btn[1]))
                        keyboard.append(keyboard_row)
                    
                    # Отправляем меню
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
                    
                # Обновляем состояние
                await dialog_state.update_step(user.id, "agent_menu", updated_context)
            
            # Другие типы callback
            else:
                await query.answer("Обработка команды...")
                await query.edit_message_text(f"Команда выбрана: {data}")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке callback: {e}")
            await query.answer("Произошла ошибка при обработке команды")
            await query.edit_message_text("Произошла ошибка. Пожалуйста, попробуйте снова /start")

    async def send_message(self, chat_id: int, text: str) -> bool:
        """
        Отправляет сообщение через Telegram
        
        Args:
            chat_id: ID чата
            text: Текст сообщения
            
        Returns:
            bool: True если сообщение отправлено успешно, иначе False
        """
        try:
            await self.app.bot.send_message(chat_id=chat_id, text=text)
            logger.info(f"Отправлено сообщение в чат {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")
            return False 