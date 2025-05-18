from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
import asyncio
from loguru import logger
import os
import inspect
from typing import Dict, Any, List, Callable

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
        self.app.add_handler(MessageHandler(filters._Voice(), self.on_voice))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.on_photo))
        self.app.add_handler(MessageHandler(filters.Document.ALL, self.on_document))
        self.app.add_handler(MessageHandler(filters._Video(), self.on_video))
        self.app.add_handler(MessageHandler(filters._Audio(), self.on_audio))
        self.app.add_handler(MessageHandler(filters.Sticker.ALL, self.on_sticker))
        self.app.add_handler(MessageHandler(filters._Contact(), self.on_contact))
        self.app.add_handler(MessageHandler(filters._Location(), self.on_location))
        self.app.add_handler(CallbackQueryHandler(self.on_callback_query))
        
        logger.info(f"Зарегистрировано {len(self.app.handlers)} обработчиков")

    def register_step_handlers(self, step_handlers: Dict[str, Callable]):
        """Регистрирует обработчики шагов, предоставляемые этим плагином."""
        step_handlers["telegram_send_message"] = self.handle_step_send_message
        # Если в будущем появятся другие обработчики шагов от TelegramPlugin, их можно добавить сюда
        registered_handlers_list = ["telegram_send_message"]
        logger.info(f"TelegramPlugin зарегистрировал обработчики шагов: {registered_handlers_list}")

    async def on_start(self, update: Update, context_ext: CallbackContext):
        """Обработка команды /start: инициирует запуск сценария главного меню."""
        user = update.effective_user
        chat_id = update.effective_chat.id
        logger.info(f"Команда /start от пользователя {user.id} (@{user.username}), chat_id: {chat_id}")
        
        main_menu_scenario_id = os.getenv("MAIN_MENU_SCENARIO_ID", "scenario_main_menu") 

        initial_scenario_context = {
            "user_id": user.id,
            "chat_id": chat_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "trigger": "start_command",
            "message_text": update.message.text
        }
        
        logger.info(f"Запрос на запуск сценария '{main_menu_scenario_id}' для user {user.id} из команды /start.")
        
        scenario_executor = context_ext.bot_data.get("scenario_executor")
        
        if scenario_executor:
            try:
                # Запускаем сценарий. Ответ (финальный контекст) нам здесь обычно не нужен,
                # так как сценарий сам отправит сообщения через telegram_send_message.
                result_context = await scenario_executor.run_scenario_by_id(main_menu_scenario_id, initial_scenario_context)
                if result_context is None:
                    # Это означает, что сценарий не найден или произошла ошибка при его запуске/выполнении
                    logger.error(f"Сценарий '{main_menu_scenario_id}' не был выполнен (возможно, не найден или ошибка внутри). User: {user.id}")
                    await update.message.reply_text(
                        "Не удалось загрузить главное меню. Пожалуйста, попробуйте позже или обратитесь к администратору."
                    )
                # Если сценарий выполнен, он должен был сам отправить ответ. 
                # Ничего дополнительно здесь делать не нужно, если только не логировать финальный контекст.
                # logger.info(f"Сценарий '{main_menu_scenario_id}' завершен для user {user.id}. Финальный контекст: {result_context}")

            except Exception as e:
                logger.error(f"Исключение при попытке запуска сценария '{main_menu_scenario_id}' из on_start: {e}", exc_info=True)
                await update.message.reply_text("Произошла ошибка при запуске главного меню. Попробуйте позже.")
        else:
            logger.error("ScenarioExecutor не найден в context_ext.bot_data. Невозможно запустить сценарий.")
            await update.message.reply_text(
                "Ошибка конфигурации сервера: не удается обработать команду. Пожалуйста, сообщите администратору."
            )
    
    async def on_help(self, update: Update, context_ext: CallbackContext):
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

    async def on_text(self, update: Update, context_ext: CallbackContext):
        """Обработка текстовых сообщений"""
        user = update.effective_user
        text = update.message.text
        logger.info(f"Сообщение от {user.id} (@{user.username}): {text[:50]}")

        # --- Новый блок: обработка через ScenarioExecutor ---
        try:
            # ЗАГЛУШКА: Получение scenario_id и контекста. В будущем это должно приходить из репозитория сессий.
            scenario_id = None # TODO: Заменить на получение из репозитория сессий по user.id
            scenario_context = {"user_id": user.id, "chat_id": update.effective_chat.id} # TODO: Заменить
            
            # Пример: если бы у нас был user_session_repository
            # user_session = await self.user_session_repository.get_session(user.id)
            # if user_session and user_session.active_scenario_id:
            #    scenario_id = user_session.active_scenario_id
            #    scenario_context = user_session.context

            if scenario_id: # Если есть активный сценарий
                logger.info(f"Пользователь {user.id} в сценарии {scenario_id}, передаю в ScenarioExecutor. Текст: {text[:50]}")
                
                # Заглушка для ответа
                await update.message.reply_text(f"Сценарий '{scenario_id}' получил ваш текст: {text[:30]}... (Обработка в разработке)")

            else: # Если нет активного сценария, возможно, запустить сценарий по умолчанию или ответить стандартно
                logger.info(f"Для пользователя {user.id} нет активного сценария. Текст: {text[:50]}")
                await update.message.reply_text(f"Я получил ваше сообщение: {text}. Активного сценария нет.")
            return # Возвращаемся после обработки (или попытки обработки) через сценарий

        except Exception as e:
            logger.error(f"Ошибка при обработке текстового сообщения сценарием: {e}", exc_info=True)
            await update.message.reply_text("[Ошибка] Не удалось обработать ваше сообщение. Попробуйте позже или /start.")
            return
        # --- Конец нового блока ---

        # Этот блок теперь не должен достигаться, если логика выше корректна
        # await update.message.reply_text(f"Я получил ваше сообщение: {text}")

    async def on_voice(self, update: Update, context_ext: CallbackContext):
        """Обработка голосовых сообщений"""
        await update.message.reply_text("Я получил голосовое сообщение, но пока не умею его обрабатывать")

    async def on_photo(self, update: Update, context_ext: CallbackContext):
        """Обработка фотографий"""
        await update.message.reply_text("Я получил фотографию, но пока не умею её обрабатывать")

    async def on_document(self, update: Update, context_ext: CallbackContext):
        """Обработка документов"""
        await update.message.reply_text(f"Я получил документ '{update.message.document.file_name}', но пока не умею его обрабатывать")

    async def on_video(self, update: Update, context_ext: CallbackContext):
        """Обработка видео"""
        await update.message.reply_text("Я получил видео, но пока не умею его обрабатывать")

    async def on_audio(self, update: Update, context_ext: CallbackContext):
        """Обработка аудио"""
        await update.message.reply_text("Я получил аудио, но пока не умею его обрабатывать")

    async def on_sticker(self, update: Update, context_ext: CallbackContext):
        """Обработка стикеров"""
        await update.message.reply_text("👍")

    async def on_contact(self, update: Update, context_ext: CallbackContext):
        """Обработка контактов"""
        contact = update.message.contact
        await update.message.reply_text(f"Контакт получен: {contact.first_name} {contact.phone_number}")

    async def on_location(self, update: Update, context_ext: CallbackContext):
        """Обработка локаций"""
        location = update.message.location
        await update.message.reply_text(f"Локация получена: {location.latitude}, {location.longitude}")

    async def handle_step_send_message(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага сценария для отправки сообщения через Telegram.
        step_data должен содержать:
        - chat_id (или будет взят из context.chat_id)
        - text: текст сообщения
        - parse_mode: str (опционально, e.g., "MarkdownV2", "HTML")
        - inline_keyboard: List[List[Dict[str, str]]] (опционально)
          (e.g. [[{'text': 'Button 1', 'callback_data': 'data1'}]] )
        - reply_keyboard: List[List[Dict[str, str]]] (опционально)
          (e.g. [[{'text': 'Reply Button 1'}]] )
        - message_id_to_edit: int (опционально, для редактирования сообщения)
        """
        params = step_data.get("params", {}) # Получаем вложенный словарь params
        
        chat_id = params.get("chat_id") or context.get("chat_id")
        text = params.get("text")
        inline_keyboard_data = params.get("inline_keyboard")
        reply_keyboard_data = params.get("reply_keyboard")
        message_id_to_edit = params.get("message_id_to_edit")
        parse_mode = params.get("parse_mode")

        if not chat_id or not text:
            logger.error(f"Шаг telegram_send_message: отсутствует chat_id или text. step_data: {step_data}, context: {context}")
            context["telegram_send_error"] = "Missing chat_id or text"
            return context

        final_reply_markup = None

        if inline_keyboard_data:
            buttons = []
            for row_data in inline_keyboard_data:
                button_row = []
                for button_data in row_data:
                    button_row.append(InlineKeyboardButton(text=button_data["text"], callback_data=button_data["callback_data"]))
                buttons.append(button_row)
            final_reply_markup = InlineKeyboardMarkup(buttons)
        
        elif reply_keyboard_data:
            buttons = []
            for row_data in reply_keyboard_data:
                button_row = [button_data["text"] for button_data in row_data]
                buttons.append(button_row)
            
            resize = params.get("resize_keyboard", True)  # Используем params
            one_time = params.get("one_time_keyboard", False) # Используем params
            placeholder = params.get("input_field_placeholder") # Используем params
            selective = params.get("selective", False) # Используем params
            final_reply_markup = ReplyKeyboardMarkup(
                buttons,
                resize_keyboard=resize,
                one_time_keyboard=one_time,
                input_field_placeholder=placeholder,
                selective=selective
            )

        try:
            if message_id_to_edit and final_reply_markup and isinstance(final_reply_markup, InlineKeyboardMarkup):
                await self.app.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id_to_edit,
                    text=text,
                    reply_markup=final_reply_markup,
                    parse_mode=parse_mode
                )
                logger.info(f"Сообщение {message_id_to_edit} отредактировано для chat_id {chat_id}")
            elif message_id_to_edit:
                await self.app.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id_to_edit,
                    text=text,
                    parse_mode=parse_mode
                )
                logger.info(f"Текст сообщения {message_id_to_edit} отредактирован для chat_id {chat_id}")
            else:
                sent_message = await self.app.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=final_reply_markup,
                    parse_mode=parse_mode
                )
                context["sent_message_id"] = sent_message.message_id
                logger.info(f"Сообщение отправлено в chat_id {chat_id}, message_id: {sent_message.message_id}")
            context["telegram_send_success"] = True
        except Exception as e:
            logger.error(f"Ошибка при отправке/редактировании сообщения Telegram в chat_id {chat_id}: {e}")
            context["telegram_send_error"] = str(e)
        
        return context

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

    async def on_callback_query(self, update: Update, context_ext: CallbackContext):
        """Обработка callback-запросов от inline-кнопок"""
        query = update.callback_query
        data = query.data
        user = query.from_user
        chat_id = update.effective_chat.id
        
        logger.info(f"Callback-запрос от {user.id} (@{user.username}), chat_id: {chat_id}, data: {data}")
        
        try:
            await query.answer() # Отвечаем на колбэк как можно раньше

            # Формируем базовый контекст для возможного запуска сценария
            initial_scenario_context = {
                "user_id": user.id,
                "chat_id": chat_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "trigger": "callback_query",
                "callback_data": data
            }
            
            # Новый разбор callback_data
            # Пример формата: "action_type:value,param1:value1,param2:value2"
            # Например: "run_scenario:my_scenario_id,initial_message:Hello"
            #           "continue_event:button_click,value:option1"
            
            action_details = {}
            if ':' in data:
                parts = data.split(',', 1)
                action_key_value = parts[0].split(':', 1)
                action_details["type"] = action_key_value[0] # e.g., "run_scenario" or "event"
                action_details["value"] = action_key_value[1] if len(action_key_value) > 1 else None

                if len(parts) > 1:
                    params_str = parts[1]
                    for param in params_str.split(','):
                        key_val = param.split(':', 1)
                        if len(key_val) == 2:
                            action_details[key_val[0]] = key_val[1]
            else: # Если нет ':', возможно, это простой идентификатор или старый формат
                action_details["type"] = "unknown_format"
                action_details["raw_data"] = data
                logger.warning(f"Callback data '{data}' не соответствует ожидаемому формату 'type:value,params'.")

            logger.info(f"Разобранный callback: {action_details}")

            scenario_executor = context_ext.bot_data.get("scenario_executor")

            if not scenario_executor:
                logger.error("ScenarioExecutor не найден в context_ext.bot_data. Невозможно обработать callback.")
                if query.message:
                    await query.edit_message_text("Ошибка конфигурации сервера. Пожалуйста, сообщите администратору.")
                else:
                    await self.app.bot.send_message(chat_id, "Ошибка конфигурации сервера. Пожалуйста, сообщите администратору.")
                return

            if action_details.get("type") == "run_scenario" and action_details.get("value"):
                scenario_id_to_run = action_details["value"]
                initial_scenario_context.update(action_details) 
                
                logger.info(f"Запрос на запуск сценария '{scenario_id_to_run}' для user {user.id} из callback.")
                try:
                    result_context = await scenario_executor.run_scenario_by_id(scenario_id_to_run, initial_scenario_context)
                    if result_context is None:
                        logger.error(f"Сценарий '{scenario_id_to_run}' не был выполнен из callback. User: {user.id}")
                        if query.message:
                            await query.edit_message_text(f"Не удалось запустить запрошенный сценарий ('{scenario_id_to_run}').")
                        else:
                            await self.app.bot.send_message(chat_id, f"Не удалось запустить запрошенный сценарий ('{scenario_id_to_run}').")
                    # Если сценарий запустился и выполнился, он сам должен был обновить сообщение или отправить новое.
                    # Если мы хотим обязательно отредактировать исходное сообщение (например, убрать кнопки):
                    # elif query.message: 
                    #    await query.edit_message_text(text=f"Сценарий '{scenario_id_to_run}' запущен.")

                except Exception as e:
                    logger.error(f"Исключение при запуске сценария '{scenario_id_to_run}' из callback: {e}", exc_info=True)
                    if query.message:
                        await query.edit_message_text("Произошла ошибка при обработке вашего выбора.")
            
            elif action_details.get("type") == "event": 
                event_name = action_details.get("value")
                logger.info(f"Запрос на передачу события '{event_name}' в текущий сценарий user {user.id} с данными: {action_details}")
                # TODO: Реализовать self.scenario_executor.handle_event(user.id, event_name, action_details)
                # Эта часть требует доработки ScenarioExecutor и системы управления состоянием активного сценария.
                if query.message:
                    await query.edit_message_text(text=f"Событие '{event_name}' получено... (обработка событий в разработке)")
                else:
                    await self.app.bot.send_message(chat_id, text=f"Событие '{event_name}' получено... (обработка событий в разработке)")
            
            else:
                logger.warning(f"Неизвестный или неполный тип действия в callback_data: {data} (детали: {action_details})")
                if query.message:
                    await query.edit_message_text(text=f"Действие по кнопке '{data}' пока не настроено.")
                else:
                    await self.app.bot.send_message(chat_id, text=f"Действие по кнопке '{data}' пока не настроено.")
                
        except Exception as e:
            logger.error(f"Ошибка в on_callback_query при обработке data '{data}': {e}", exc_info=True)
            if query.message:
                try:
                    await query.edit_message_text("Произошла ошибка при обработке вашего выбора.")
                except Exception as edit_e:
                    logger.error(f"Не удалось отредактировать сообщение после ошибки в on_callback_query: {edit_e}")
            else: # Если исходного сообщения нет (маловероятно для callback_query)
                 await self.app.bot.send_message(chat_id, "Произошла ошибка при обработке вашего выбора.")

    async def send_message(self, chat_id: int, text: str) -> bool:
        """Отправляет простое текстовое сообщение в указанный чат."""
        try:
            logger.info(f"[send_message] chat_id={chat_id!r} (type={type(chat_id)}), text={text!r}")
            # Логируем context, если есть в self или через inspect
            frame = inspect.currentframe()
            outer = inspect.getouterframes(frame)
            for f in outer:
                if 'context' in f.frame.f_locals:
                    logger.info(f"[send_message] context: {f.frame.f_locals['context']}")
                    break
            await self.app.bot.send_message(chat_id=chat_id, text=text)
            logger.info(f"Отправлено сообщение в чат {chat_id}")
            return True
        except Exception as e:
            import traceback
            logger.error(f"Ошибка при отправке сообщения в чат {chat_id}: {e}\n{traceback.format_exc()}")
            return False 