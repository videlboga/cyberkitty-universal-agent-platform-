from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
import asyncio

class TelegramPlugin:
    def __init__(self, app):
        self.app = app
        self.add_handlers()

    def add_handlers(self):
        self.app.add_handler(CommandHandler("start", self.on_start))
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

    async def on_start(self, update: Update, context):
        """Обработка команды /start: отправка меню выбора агента с inline-кнопками"""
        buttons = [
            [InlineKeyboardButton("Коуч", callback_data="agent_coach")],
            [InlineKeyboardButton("Лайфхакер", callback_data="agent_lifehacker")],
            [InlineKeyboardButton("Ментор", callback_data="agent_mentor")],
            [InlineKeyboardButton("Дайджест", callback_data="agent_digest")],
            [InlineKeyboardButton("Эксперт", callback_data="agent_expert")],
        ]
        markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            "Выберите агента:",
            reply_markup=markup
        )

    async def on_text(self, update: Update, context):
        """Обработка текстовых сообщений"""
        pass

    async def on_voice(self, update: Update, context):
        pass

    async def on_photo(self, update: Update, context):
        pass

    async def on_document(self, update: Update, context):
        pass

    async def on_video(self, update: Update, context):
        pass

    async def on_audio(self, update: Update, context):
        pass

    async def on_sticker(self, update: Update, context):
        pass

    async def on_contact(self, update: Update, context):
        pass

    async def on_location(self, update: Update, context):
        pass

    async def healthcheck(self):
        """Асинхронная проверка работоспособности Telegram-бота через get_me
        Returns:
            bool: True если бот отвечает, иначе False
        """
        try:
            me = await self.app.bot.get_me()
            return True if me else False
        except Exception:
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
        # TODO: интеграция с flow-сценарием, обработка переходов
        await query.answer()
        await query.edit_message_text(text=f"Вы выбрали: {data}") 