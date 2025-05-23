from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext, TypeHandler, Application
import asyncio
from loguru import logger
import os
import inspect
from typing import Dict, Any, List, Callable, Optional
import json
from fastapi import Request
from fastapi.responses import JSONResponse
from telegram import Bot
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from httpx import ConnectTimeout, ReadTimeout, RemoteProtocolError

from app.plugins.plugin import PluginBase
from app.core.utils import resolve_string_template, _resolve_value_from_context # resolve_placeholders_in_structure_recursive
# from app.core.config import settings as app_settings # <-- УДАЛЯЕМ ЭТОТ ИМПОРТ
# from app.core.scenario_executor import ScenarioExecutor # Убираем прямой импорт из-за цикличности
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.scenario_executor import ScenarioExecutor

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/telegram_plugin.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)
# logger.add("logs/all_telegram_updates.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip", serialize=True) # Временно отключаем

# async def log_all_updates(update: Update, context: CallbackContext): # Временно отключаем
#     logger.debug(f"[ALL_UPDATES] Received update: {update.to_json()}")

# Импортируем _resolve_value_from_context из scenario_executor
# Это создаст циклическую зависимость, если scenario_executor импортирует TelegramPlugin.
# Лучше вынести _resolve_value_from_context в отдельный utils файл.
# ПОКА ЗАКОММЕНТИРУЕМ, и будем ожидать, что executor передаст функцию или сам обработает параметры
# from app.core.scenario_executor import _resolve_value_from_context, resolve_string_template
# Временное решение: скопируем функции сюда, чтобы избежать цикл. зависимостей на данном этапе.

def _resolve_value_from_context(value: Any, context: Dict[str, Any], depth=0, max_depth=10) -> Any:
    if depth > max_depth:
        logger.warning(f"Max recursion depth reached in _resolve_value_from_context for value: {value}")
        return value

    if isinstance(value, str):
        # Сначала обрабатываем шаблоны Jinja-стиля с двойными скобками {{ }}
        if "{{" in value and "}}" in value:
            return resolve_string_template(value, context)
        # Затем обрабатываем одинарные скобки {key} для обратной совместимости
        elif value.startswith("{") and value.endswith("}"):
            key_path = value[1:-1]
            parts = key_path.split('.')
            current_value = context
            resolved_successfully = True
            for part in parts:
                if isinstance(current_value, dict) and part in current_value:
                    current_value = current_value[part]
                elif isinstance(current_value, list):
                    try:
                        idx = int(part)
                        if 0 <= idx < len(current_value):
                            current_value = current_value[idx]
                        else:
                            resolved_successfully = False
                            break
                    except ValueError:
                        resolved_successfully = False
                        break
                else:
                    resolved_successfully = False
                    break
            
            if resolved_successfully:
                if isinstance(current_value, str) and current_value.startswith("{") and current_value.endswith("}") and current_value != value:
                    return _resolve_value_from_context(current_value, context, depth + 1, max_depth)
                return current_value
            else:
                return resolve_string_template(value, context)
        else:
            # Обычная строка без шаблонов
            return value

    elif isinstance(value, dict):
        return {k: _resolve_value_from_context(v, context, depth + 1, max_depth) for k, v in value.items()}
    elif isinstance(value, list):
        return [_resolve_value_from_context(item, context, depth + 1, max_depth) for item in value]
    return value

def resolve_string_template(template_str: str, ctx: Dict[str, Any]) -> str:
    import re
    # Сначала ищем шаблоны с двойными скобками {{ variable_name }}
    double_braces_pattern = r"\{\{\s*([^{}]+)\s*\}\}"
    placeholders = re.findall(double_braces_pattern, template_str)
    resolved_str = template_str
    
    for placeholder in placeholders:
        key_path = placeholder.strip()
        parts = key_path.split('.')
        current_value = ctx
        resolved_successfully = True
        for part in parts:
            if isinstance(current_value, dict) and part in current_value:
                current_value = current_value[part]
            elif isinstance(current_value, list):
                try:
                    idx = int(part)
                    if 0 <= idx < len(current_value):
                        current_value = current_value[idx]
                    else:
                        resolved_successfully = False
                        break
                except ValueError:
                    resolved_successfully = False
                    break
            else:
                resolved_successfully = False
                break
        
        if resolved_successfully:
            replacement_value = str(current_value)
            # Заменяем с учетом возможных пробелов
            pattern_to_replace = r"\{\{\s*" + re.escape(placeholder.strip()) + r"\s*\}\}"
            resolved_str = re.sub(pattern_to_replace, replacement_value, resolved_str)
    
    # Также обрабатываем одинарные скобки для обратной совместимости
    single_braces_pattern = r"\{([^{}]+)\}"
    single_placeholders = re.findall(single_braces_pattern, resolved_str)
    
    for placeholder in single_placeholders:
        key_path = placeholder
        parts = key_path.split('.')
        current_value = ctx
        resolved_successfully = True
        for part in parts:
            if isinstance(current_value, dict) and part in current_value:
                current_value = current_value[part]
            elif isinstance(current_value, list):
                try:
                    idx = int(part)
                    if 0 <= idx < len(current_value):
                        current_value = current_value[idx]
                    else:
                        resolved_successfully = False
                        break
                except ValueError:
                    resolved_successfully = False
                    break
            else:
                resolved_successfully = False
                break
        
        if resolved_successfully:
            replacement_value = str(current_value)
            resolved_str = resolved_str.replace(f"{{{placeholder}}}", replacement_value)
    
    return resolved_str

class TelegramPlugin(PluginBase):
    def __init__(self, app: Application):
        super().__init__()
        self.app: Application = app
        self.updater: Optional[Updater] = app.updater # Updater теперь берется из переданного app
        self.bot_info: Optional[Bot] = None
        self.scenario_executor: Optional['ScenarioExecutor'] = None # Будет установлено позже
        self.is_polling = False
        self.polling_task: Optional[asyncio.Task] = None
        self.user_states: Dict[int, Dict[str, Any]] = {}  # Состояние пользователя для многошаговых диалогов
        self.message_id_map: Dict[str, int] = {} # Для хранения message_id context_id -> message_id
        self.handlers_added: bool = False # <--- НОВЫЙ ФЛАГ
        logger.info(f"TelegramPlugin __init__ (id:{id(self)}) completed. self.app (id:{id(self.app)}) set from argument.")

    async def async_initialize(self):
        logger.info(f"TelegramPlugin async_initialize (id:{id(self)}): Начало асинхронной инициализации...")
        
        if not self.app:
            logger.error(f"TelegramPlugin async_initialize (id:{id(self)}): self.app отсутствует. Инициализация невозможна.")
            return

        # Убираем проверку self.app.initialized, т.к. атрибут отсутствует в объекте Application
        # if not self.app.initialized: 
        try:
            logger.info(f"TelegramPlugin async_initialize (id:{id(self)}): Вызов self.app.initialize() (id_app: {id(self.app)})...")
            await self.app.initialize()
            logger.info(f"TelegramPlugin async_initialize (id:{id(self)}): self.app.initialize() успешно завершен.")
        except Exception as e_app_init:
            logger.error(f"TelegramPlugin async_initialize (id:{id(self)}): Ошибка при self.app.initialize(): {e_app_init}", exc_info=True)
            return # Не можем продолжать без инициализированного app
        # else:
        #    logger.info(f"TelegramPlugin async_initialize (id:{id(self)}): self.app (id:{id(self.app)}) уже был инициализирован.")

        # Обновляем updater на случай, если он изменился или не был установлен в __init__
        self.updater = self.app.updater
        if not self.updater:
            logger.error(f"TelegramPlugin async_initialize (id:{id(self)}): self.app.updater is None ПОСЛЕ инициализации self.app! polling и добавление хендлеров могут быть невозможны.")
            # Не прерываем, т.к. add_handlers может быть уже вызван, а polling управляется из main.py

        try:
            self.bot_info = await self.app.bot.get_me()
            logger.info(f"TelegramPlugin async_initialize (id:{id(self)}): Bot info: {self.bot_info.username} (ID: {self.bot_info.id})")
        except Exception as e_get_me:
            logger.error(f"TelegramPlugin async_initialize (id:{id(self)}): Ошибка при получении bot_info: {e_get_me}", exc_info=True)
            # Не критично для добавления хендлеров, но важно для работы

        # Добавляем executor в bot_data этого инстанса app, если он еще не там
        from app.core.dependencies import scenario_executor_instance # Поздний импорт
        if scenario_executor_instance:
            if "scenario_executor" not in self.app.bot_data or self.app.bot_data["scenario_executor"] != scenario_executor_instance:
                self.app.bot_data["scenario_executor"] = scenario_executor_instance
                logger.info(f"TelegramPlugin async_initialize (id:{id(self)}): scenario_executor (id: {id(scenario_executor_instance)}) добавлен/обновлен в self.app.bot_data (id_app: {id(self.app)}).")
            else:
                logger.info(f"TelegramPlugin async_initialize (id:{id(self)}): scenario_executor уже присутствует и совпадает в self.app.bot_data.")
        else:
            logger.warning(f"TelegramPlugin async_initialize (id:{id(self)}): scenario_executor_instance отсутствует, не могу добавить/проверить в self.app.bot_data.")

        # Хендлеры теперь добавляются в dependencies.py сразу после создания плагина.
        # Здесь мы просто проверяем флаг.
        if not self.handlers_added:
            logger.warning(f"TelegramPlugin async_initialize (id:{id(self)}): self.handlers_added = False. Это НЕОЖИДАННО, т.к. add_handlers() должен был быть вызван из dependencies.py. Попытка вызвать add_handlers() сейчас...")
            self.add_handlers() # На всякий случай, если что-то пошло не так
        else:
            logger.info(f"TelegramPlugin async_initialize (id:{id(self)}): self.handlers_added = True. Хендлеры УЖЕ были добавлены ранее.")
            
        logger.info(f"TelegramPlugin async_initialize (id:{id(self)}): Завершение асинхронной инициализации.")

    def add_handlers(self):
        if not self.app:
            logger.error(f"TelegramPlugin add_handlers (id:{id(self)}): Application (self.app) не инициализирован. Невозможно добавить обработчики.")
            return
        
        if self.handlers_added:
            logger.warning(f"TelegramPlugin add_handlers (id:{id(self)}): Попытка повторного добавления обработчиков, когда self.handlers_added=True. Пропускаю.")
            return

        logger.info(f"TelegramPlugin add_handlers (id:{id(self)}): Попытка добавления обработчиков к self.app (id: {id(self.app)}).")

        self.app.add_handler(CommandHandler("start", self.handle_start_command, block=False))
        self.app.add_handler(CommandHandler("superdupertestcommand123", self.handle_super_test_command, block=False)) # <--- РЕГИСТРАЦИЯ НОВОГО ОБРАБОТЧИКА
        # self.app.add_handler(CommandHandler("test_message_id", self.test_message_id_command)) # ВРЕМЕННО ОТКЛЮЧИМ
        # self.app.add_handler(CommandHandler("status", self.handle_status_command)) # ВРЕМЕННО ОТКЛЮЧИМ
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))

        # Используем группу -1 для повышения приоритета этого обработчика
        # self.app.add_handler(CallbackQueryHandler(lambda u, c: self._dispatch_callback_query(u, c)), group=-1) # Старая версия
        self.app.add_handler(CallbackQueryHandler(self.on_callback_query), group=-1) # Явно указываем self.on_callback_query
        logger.info(f"TelegramPlugin add_handlers (id:{id(self)}): CallbackQueryHandler добавлен с self.on_callback_query (группа -1). self.app id: {id(self.app)}")

        # ОТЛАДКА: Проверяем наличие self.logger перед определением all_updates_handler_debug
        if hasattr(self, 'logger') and self.logger is not None:
            logger.info(f"TelegramPlugin add_handlers (id:{id(self)}): self.logger СУЩЕСТВУЕТ перед all_updates_handler_debug. Тип: {{type(self.logger)}}")
        else:
            logger.error(f"TelegramPlugin add_handlers (id:{id(self)}): self.logger НЕ СУЩЕСТВУЕТ или None перед all_updates_handler_debug!")

        # Добавляем "сырой" обработчик всех обновлений с высоким приоритетом
        # async def all_updates_handler_debug(update: Update, context: CallbackContext):
        #     self.logger.critical(f"!!!!!!!!!!!!!! [RAW_UPDATE_HANDLER] ПОЛУЧЕНО ОБНОВЛЕНИЕ: {update.to_json()} !!!!!!!!!!!!!!")
        #     # print(f"!!!!!!!!!!!!!! [RAW_UPDATE_HANDLER VIA PRINT] ПОЛУЧЕНО ОБНОВЛЕНИЕ: {update.to_json()} !!!!!!!!!!!!!!") # Возвращаем на self.logger
        #     # Важно: этот обработчик ничего не должен делать, кроме логирования,
        #     # чтобы не мешать другим обработчикам, если они все же сработают.
        #     # Не используйте context.application.stop() или другие подобные вызовы здесь.
        #     # Также важно не бросать исключения из этого обработчика, чтобы не нарушить работу PTB.
        #     # Просто логируем и позволяем обновлению идти дальше по цепочке.
        #     pass # Явный pass, чтобы показать, что больше ничего не делаем

        # self.app.add_handler(TypeHandler(Update, all_updates_handler_debug), group=-2) # Группа -2 для еще более высокого приоритета
        # self.logger.critical(f"TelegramPlugin add_handlers (id:{id(self)}): TypeHandler для ВСЕХ обновлений добавлен в группу -2.") # Закомментировано, так как сам обработчик закомментирован

        self.handlers_added = True # <--- УСТАНАВЛИВАЕМ ФЛАГ
        logger.info(f"TelegramPlugin add_handlers (id:{id(self)}): Флаг self.handlers_added установлен в True.")

        # Логируем все зарегистрированные обработчики для этого инстанса self.app
        # ... existing code ...

    async def handle_super_test_command(self, update: Update, context: CallbackContext): # <--- НОВЫЙ МЕТОД
        logger.info("🚀 SUPER_DUPER_TEST_COMMAND: Запуск LLM тестового сценария")
        if update.effective_chat:
            try:
                # Получаем scenario_executor из context.bot_data
                scenario_executor = context.bot_data.get("scenario_executor")
                if not scenario_executor:
                    logger.error("ScenarioExecutor не найден в context.bot_data")
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="❌ Ошибка: ScenarioExecutor не найден"
                    )
                    return

                # Запускаем LLM тестовый сценарий
                chat_id = str(update.effective_chat.id)
                initial_context = {
                    "chat_id": chat_id,
                    "user_telegram_id": update.effective_user.id,
                    "username": update.effective_user.username or update.effective_user.first_name
                }
                
                logger.info(f"🤖 Запуск LLM сценария 'llm_test_telegram' для chat_id: {chat_id}")
                
                result = await scenario_executor.run_scenario_by_id(
                    scenario_id="llm_test_telegram",
                    initial_context=initial_context
                )
                
                if result and result.get("success"):
                    logger.info(f"✅ LLM сценарий успешно выполнен: {result.get('message', 'OK')}")
                else:
                    logger.error(f"❌ Ошибка выполнения LLM сценария: {result}")
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"❌ Ошибка выполнения LLM сценария: {result.get('message', 'Неизвестная ошибка')}"
                    )
                    
            except Exception as e:
                logger.error(f"Ошибка при запуске LLM сценария в handle_super_test_command для chat_id {update.effective_chat.id}: {e}", exc_info=True)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ Ошибка при запуске LLM тестового сценария: {str(e)}"
                )
        else:
            logger.warning("Не удалось определить effective_chat для ответа на /superdupertestcommand123")

    async def handle_start_command(self, update: Update, context: CallbackContext):
        """Обрабатывает команду /start."""
        logger.info(f"!!!!!!!!!!!!!! TELEGRAM_PLUGIN: handle_start_command ВЫЗВАН! update.message.text: {update.message.text}") # МОЙ НОВЫЙ ЛОГ - ОСТАВЛЕН ПО ПРОСЬБЕ
        logger.info("HANDLE_START_COMMAND CALLED") # Изменено с critical и убраны "!!!"
        logger.info(f"Команда /start получена от user_id: {update.effective_user.id}, chat_id: {update.effective_chat.id}")
        
        if update.effective_chat:
            try:
                keyboard = [[InlineKeyboardButton("Тестовая кнопка", callback_data="test_button_callback")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, 
                    text="Привет! Нажми тестовую кнопку:",
                    reply_markup=reply_markup
                )
                logger.info(f"Сообщение с тестовой кнопкой на /start успешно отправлено в chat_id: {update.effective_chat.id}")
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения с кнопкой в handle_start_command для chat_id {update.effective_chat.id}: {e}", exc_info=True)
            logger.info("Message with button should have been sent (or error logged)") # Изменено с critical и убраны "!!!"
        else:
            logger.warning(f"Не удалось определить effective_chat для ответа на /start. Update: {{update.to_json()}}") # Исправлено экранирование
            logger.warning("EFFECTIVE_CHAT WAS NONE") # Изменено с critical и убраны "!!!"

    async def on_callback_query(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        # Сразу отвечаем на callback, чтобы убрать "часики" на кнопке
        await query.answer("Получено") # Можно добавить текст, который всплывет у пользователя

        logger.info("ON_CALLBACK_QUERY_CALLED_SUCCESSFULLY")
        
        user_id = query.from_user.id
        username = query.from_user.username or query.from_user.first_name
        chat_id = query.message.chat.id if query.message else None # query.message может быть None для inline-режима
        message_id = query.message.message_id if query.message else None
        callback_data = query.data
        message_text = query.message.text if query.message else "N/A (inline)"

        logger.info(
            f"[TELEGRAM_PLUGIN] Получен callback_query от user {user_id} (@{username}) "
            f"для message_id: {message_id} в chat_id: {chat_id}. Data: '{callback_data}'. "
            f"Текст сообщения: '{message_text}'"
        )

        if query.data == "test_button_callback":
            logger.info(f"[TELEGRAM_PLUGIN] Обработка тестового callback 'test_button_callback' от user {user_id}.")
            if chat_id:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"Кнопка 'test_button_callback' была нажата пользователем @{username}!"
                    )
                    logger.info(f"[TELEGRAM_PLUGIN] Ответное сообщение на test_button_callback отправлено в chat_id {chat_id}.")
                except Exception as e:
                    logger.error(f"[TELEGRAM_PLUGIN] Ошибка при отправке ответного сообщения на test_button_callback: {e}", exc_info=True)
            else:
                logger.warning("[TELEGRAM_PLUGIN] Не могу отправить ответ на test_button_callback, так как chat_id неизвестен (возможно, inline query).")
            return # Завершаем обработку, так как это специфический тестовый callback

        scenario_executor = context.bot_data.get("scenario_executor")
        if not scenario_executor:
            logger.error("[TELEGRAM_PLUGIN] ScenarioExecutor не найден в context.bot_data. Невозможно обработать callback.")
            return

        if not message_id: 
            logger.warning(f"[TELEGRAM_PLUGIN] message_id не определен для callback_query. Data: '{callback_data}'. Невозможно найти ожидание по message_id.")
            return

        found_expectation = False
        instance_id_to_resume = None
        
        logger.debug(f"[TELEGRAM_PLUGIN] Поиск ожидания для message_id: {message_id}. Всего зарегистрировано ожиданий: {len(scenario_executor.waiting_for_input_events)}")
        
        # Преобразуем message_id из query.message в int для сравнения, если он еще не int
        try:
            current_message_id = int(message_id)
        except (ValueError, TypeError) as e:
            logger.error(f"[TELEGRAM_PLUGIN] Не удалось преобразовать current_message_id '{message_id}' в int. Ошибка: {e}")
            return
            
        for instance_id, expectation in list(scenario_executor.waiting_for_input_events.items()):
            try:
                expectation_message_id = int(expectation.get("message_id"))
            except (ValueError, TypeError, AttributeError) as e:
                logger.warning(f"[TELEGRAM_PLUGIN] Не удалось преобразовать или получить message_id из ожидания (instance: {instance_id}). Ожидание: {expectation}. Ошибка: {e}")
                continue

            logger.debug(f"[TELEGRAM_PLUGIN] Проверка ожидания: Instance ID: {instance_id}, Ожидаемый message_id: {expectation_message_id}, Текущий message_id: {current_message_id}")
            if expectation_message_id == current_message_id:
                logger.info(
                    f"[TELEGRAM_PLUGIN] Найдено ожидание ввода для scenario_instance_id: {instance_id} "
                    f"по message_id: {current_message_id}. Данные callback: '{callback_data}'"
                )
                instance_id_to_resume = instance_id
                found_expectation = True
                break

        if not found_expectation:
            logger.warning(
                f"[TELEGRAM_PLUGIN] Не найдено активного ожидания ввода для message_id: {message_id} "
                f"(user: {user_id}, data: '{callback_data}') или ожидание уже было обработано. "
                f"Текущие ожидания: {scenario_executor.waiting_for_input_events}"
            )
            return

        if instance_id_to_resume:
            logger.info(f"[TELEGRAM_PLUGIN] Попытка возобновить scenario_instance_id: {instance_id_to_resume} с данными '{callback_data}'.")
            
            full_received_input = {
                "value": callback_data, 
                "telegram_message_id": message_id,
                "telegram_chat_id": chat_id, 
                "telegram_user_id": user_id,
                "telegram_username": username,
                "telegram_first_name": query.from_user.first_name,
                "telegram_last_name": query.from_user.last_name,
                "raw_telegram_callback_payload": query.to_dict() 
            }
            
            resume_result = await scenario_executor.resume_scenario(instance_id_to_resume, full_received_input)
            
            if resume_result and resume_result.get("status") == "success":
                logger.info(
                    f"[TELEGRAM_PLUGIN] Сценарий {instance_id_to_resume} успешно возобновлен. "
                    f"Результат: {resume_result.get('message', 'OK')}, "
                    # f"Финальный контекст сценария (часть): {str(resume_result.get('final_context', {}))[:200]}" # Можно раскомментировать для отладки
                )
            
            elif resume_result: 
                logger.error(
                    f"[TELEGRAM_PLUGIN] Ошибка при возобновлении сценария {instance_id_to_resume} с данными '{callback_data}'. "
                    f"Результат: {resume_result}"
                )
            else: 
                logger.error(
                    f"[TELEGRAM_PLUGIN] Не удалось возобновить сценарий {instance_id_to_resume} с данными '{callback_data}'. "
                    f"Метод resume_scenario не вернул результат."
                )
        else:
            logger.error("[TELEGRAM_PLUGIN] Логическая ошибка: found_expectation было True, но instance_id_to_resume не установлен.")

    async def handle_text_message(self, update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        text = update.message.text

        logger.info(f"[TELEGRAM_PLUGIN] Получено текстовое сообщение от user {user_id} в chat {chat_id}: '{text}'")

        # TODO: Реализовать логику обработки текстовых сообщений.
        # Возможные варианты:
        # 1. Если активен сценарий, ожидающий текстового ввода от этого пользователя,
        #    возобновить его с полученным текстом.
        # 2. Если нет активного сценария, попытаться запустить сценарий по умолчанию или NLP-обработку.
        # 3. Просто ответить, что команда не распознана, если нет другой логики.

        # Пример простой заглушки ответа:
        # await context.bot.send_message(
        #     chat_id=chat_id,
        #     text=f"Вы написали: '{text}'. Обработка таких сообщений пока не реализована."
        # )

        # Если есть сценарий, ожидающий ввода (хотя текущая система больше на callback_query):
        # scenario_executor = context.bot_data.get("scenario_executor")
        # if scenario_executor:
        #     # Нужно будет доработать логику ожидания и возобновления для текстовых сообщений
        #     # Например, по user_id/chat_id, если сценарий явно ждет TEXT_INPUT
        #     pass 
        pass # Пока ничего не делаем

    async def send_message(self, chat_id, text, buttons_data=None, reply_markup=None):
        """Отправить простое сообщение или сообщение с кнопками."""
        logger.critical(f"TELEGRAM_PLUGIN: SEND_MESSAGE ENTERED. Chat_id: {chat_id}, Text: '{text}', Buttons_data: {buttons_data}")

        actual_reply_markup = None
        if buttons_data:
            inline_keyboard = []
            for row_data in buttons_data:
                inline_row = []
                for button_dict in row_data:
                    btn_text = str(button_dict.get("text", "Button"))
                    btn_callback_data = str(button_dict.get("callback_data", ""))
                    inline_row.append(InlineKeyboardButton(btn_text, callback_data=btn_callback_data))
                inline_keyboard.append(inline_row)
            if inline_keyboard:
                actual_reply_markup = InlineKeyboardMarkup(inline_keyboard)
        elif reply_markup:
            actual_reply_markup = reply_markup

        message_sent = None
        try:
            logger.info(f"TELEGRAM_PLUGIN: Попытка отправки сообщения через self.app.bot.send_message. Chat ID: {chat_id}")
            message_sent = await self.app.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=actual_reply_markup,
                parse_mode='HTML'  # Можно убрать или заменить на ParseMode.HTML, если используется enum
            )
            if message_sent:
                logger.critical(f"TELEGRAM_PLUGIN: УСПЕШНАЯ ОТПРАВКА БОТОМ! Message ID: {message_sent.message_id} в чат {chat_id}.")
            else:
                logger.error(f"TELEGRAM_PLUGIN: self.app.bot.send_message вернул None или False для чата {chat_id}.")
        except Exception as e:
            logger.error(f"TELEGRAM_PLUGIN: ОШИБКА при вызове self.app.bot.send_message для чата {chat_id}: {e}", exc_info=True)
            # Важно! Если здесь происходит raise, то ScenarioExecutor должен это поймать
            # Если не делать raise, то ScenarioExecutor не узнает об ошибке, если только message_sent не будет None

        return message_sent

    async def edit_message_text(self, chat_id, message_id, text, buttons_data=None):
        """Редактировать сообщение с текстом и кнопками."""
        logger.critical(f"TELEGRAM_PLUGIN: EDIT_MESSAGE_TEXT ENTERED. Chat_id: {chat_id}, Message_id: {message_id}, Text: '{text}', Buttons_data: {buttons_data}")

        actual_reply_markup = None
        if buttons_data:
            inline_keyboard = []
            for row_data in buttons_data:
                inline_row = []
                for button_dict in row_data:
                    btn_text = str(button_dict.get("text", "Button"))
                    btn_callback_data = str(button_dict.get("callback_data", ""))
                    inline_row.append(InlineKeyboardButton(btn_text, callback_data=btn_callback_data))
                inline_keyboard.append(inline_row)
            if inline_keyboard:
                actual_reply_markup = InlineKeyboardMarkup(inline_keyboard)

        message_edited = None
        try:
            logger.info(f"TELEGRAM_PLUGIN: Попытка редактирования сообщения через self.app.bot.edit_message_text. Chat ID: {chat_id}, Message_id: {message_id}")
            message_edited = await self.app.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=actual_reply_markup,
                parse_mode='HTML'  # Можно убрать или заменить на ParseMode.HTML, если используется enum
            )
            if message_edited:
                logger.critical(f"TELEGRAM_PLUGIN: УСПЕШНОЕ РЕДАКТИРОВАНИЕ СООБЩЕНИЯ! Message ID: {message_edited.message_id} в чат {chat_id}.")
            else:
                logger.error(f"TELEGRAM_PLUGIN: self.app.bot.edit_message_text вернул None или False для чата {chat_id} и message_id {message_id}.")
        except Exception as e:
            logger.error(f"TELEGRAM_PLUGIN: ОШИБКА при вызове self.app.bot.edit_message_text для чата {chat_id} и message_id {message_id}: {e}", exc_info=True)
            # Важно! Если здесь происходит raise, то ScenarioExecutor должен это поймать
            # Если не делать raise, то ScenarioExecutor не узнает об ошибке, если только message_edited не будет None

        return message_edited

    def register_input_expectation(self, chat_id: Any, scenario_instance_id: str, step_id: str, output_var: str, message_id_with_buttons: int = None):
        """Регистрирует, что сценарий ожидает callback_data для указанного chat_id."""
        # Этот метод, похоже, не используется ScenarioExecutor'ом напрямую для регистрации ожиданий input.
        # ScenarioExecutor сам управляет self.waiting_for_input_events.
        # Оставим его, если он используется где-то еще, но для текущей проблемы он нерелевантен.
        # Вместо self.waiting_for_input будет использоваться scenario_executor.waiting_for_input_events
        logger.warning("Вызов TelegramPlugin.register_input_expectation. Этот метод может быть устаревшим.")
        # self.waiting_for_input[str(chat_id)] = {
        #     "scenario_instance_id": scenario_instance_id,
        #     "step_id": step_id,
        #     "output_var": output_var,
        #     "message_id_with_buttons": message_id_with_buttons
        # }
        # logger.info(f"Зарегистрировано ожидание ввода для chat_id {chat_id}: scenario_instance_id={scenario_instance_id}, step_id={step_id}, output_var={output_var}, message_id_with_buttons={message_id_with_buttons}")

    def clear_input_expectation(self, chat_id: Any):
        """Удаляет ожидание ввода для chat_id."""
        # Аналогично register_input_expectation, этот метод может быть устаревшим.
        logger.warning("Вызов TelegramPlugin.clear_input_expectation. Этот метод может быть устаревшим.")
        # if str(chat_id) in self.waiting_for_input:
        #     del self.waiting_for_input[str(chat_id)]
        #     logger.info(f"Ожидание ввода для chat_id {chat_id} очищено.")

    # ++++++++++++++++++++ НОВЫЕ МЕТОДЫ ДЛЯ РЕГИСТРАЦИИ И ОБРАБОТКИ ШАГОВ ++++++++++++++++++++
    
    def register_step_handlers(self, step_handlers_dict: Dict[str, Callable]):
        """Регистрирует обработчики шагов, предоставляемые этим плагином."""
        step_handlers_dict['telegram_send_message'] = self.handle_step_send_message
        step_handlers_dict['telegram_edit_message'] = self.handle_step_edit_message
        # Добавьте другие обработчики, если они есть, например, для специфичных Telegram действий
        logger.info("TelegramPlugin: Зарегистрированы обработчики для 'telegram_send_message' и 'telegram_edit_message'.")

    async def handle_step_send_message(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Обрабатывает шаг 'telegram_send_message' из сценария. Возвращает None (без паузы)."""
        params = step_data.get("params", {})
        
        # Используем ту же логику fallback что и в ScenarioExecutor.telegram_send_message
        chat_id_template = params.get("chat_id", context.get("telegram_chat_id", context.get("chat_id")))
        text_template = params.get("text")
        
        # Разрешаем значения
        resolved_chat_id = _resolve_value_from_context(chat_id_template, context)
        resolved_text = _resolve_value_from_context(text_template, context)
        
        # Правильно обрабатываем кнопки из params
        buttons_data_template = params.get("buttons_data")
        buttons_layout_template = params.get("buttons_layout")
        inline_keyboard_template = params.get("inline_keyboard")  # Для совместимости со старыми сценариями
        
        resolved_buttons_data = None
        if buttons_data_template:
            resolved_buttons_data = _resolve_value_from_context(buttons_data_template, context)
        elif inline_keyboard_template:
            # Поддержка старого формата inline_keyboard 
            resolved_buttons_data = _resolve_value_from_context(inline_keyboard_template, context)
        
        resolved_buttons_layout = None
        if buttons_layout_template:
            resolved_buttons_layout = _resolve_value_from_context(buttons_layout_template, context)
        
        logger.info(f"[TELEGRAM_PLUGIN][HANDLE_STEP_SEND_MESSAGE] ChatID: {resolved_chat_id}, Text: '{resolved_text}', Buttons: {resolved_buttons_data}")

        if not resolved_chat_id or not resolved_text:
            error_msg = "[TELEGRAM_PLUGIN][HANDLE_STEP_SEND_MESSAGE] Отсутствует chat_id или text."
            logger.error(error_msg)
            context["_step_error"] = error_msg
            return None

        # Преобразуем кнопки в формат для send_message
        formatted_buttons_data = None
        if resolved_buttons_data and resolved_buttons_layout:
            formatted_buttons_data = self._format_buttons_for_telegram(resolved_buttons_data, resolved_buttons_layout)
        elif resolved_buttons_data:
            # Если нет layout, используем resolved_buttons_data как есть (предполагая что это уже массив массивов)
            if isinstance(resolved_buttons_data, list) and len(resolved_buttons_data) > 0:
                if isinstance(resolved_buttons_data[0], list):
                    # Уже правильный формат [[{},{}], [{}]]
                    formatted_buttons_data = resolved_buttons_data
                else:
                    # Формат [{},{},{}] - каждую кнопку в отдельной строке
                    formatted_buttons_data = [[button] for button in resolved_buttons_data]

        message_sent = await self.send_message(
            chat_id=resolved_chat_id,
            text=resolved_text,
            buttons_data=formatted_buttons_data
        )

        if message_sent:
            context["telegram_last_message_id"] = message_sent.message_id
            context["telegram_last_message_text"] = resolved_text
            if formatted_buttons_data:
                 context["message_id_with_buttons"] = message_sent.message_id
                 logger.debug(f"[TELEGRAM_PLUGIN][HANDLE_STEP_SEND_MESSAGE] Сохранено message_id_with_buttons: {message_sent.message_id}")
        else:
            error_msg = f"[TELEGRAM_PLUGIN][HANDLE_STEP_SEND_MESSAGE] Сообщение не было отправлено в chat_id {resolved_chat_id}."
            logger.error(error_msg)
            context["_step_error"] = error_msg
        return None
    
    def _format_buttons_for_telegram(self, buttons_data, buttons_layout):
        """Преобразует кнопки и layout в формат для Telegram API"""
        if not buttons_data or not buttons_layout:
            return None
            
        formatted_rows = []
        button_index = 0
        
        for row_count in buttons_layout:
            if button_index >= len(buttons_data):
                break
            row = []
            for _ in range(row_count):
                if button_index < len(buttons_data):
                    row.append(buttons_data[button_index])
                    button_index += 1
            if row:
                formatted_rows.append(row)
        
        return formatted_rows

    async def handle_step_edit_message(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает шаг 'telegram_edit_message' из сценария."""
        params = step_data.get("params", {})

        resolved_chat_id = _resolve_value_from_context(params.get("chat_id"), context)
        # Для редактирования нужен message_id, который должен быть в контексте (например, telegram_last_message_id или message_id_with_buttons)
        # или передан явно в параметрах шага.
        # Если message_id передается в params, то params.get("message_id"). 
        # Если он из контекста, то context.get(params.get("message_id_context_var", "telegram_last_message_id"))
        
        message_id_source = params.get("message_id") # Может быть прямым значением или плейсхолдером
        if not message_id_source: # Если не указан в params, пытаемся взять из контекста по умолчанию
            message_id_source = "{message_id_with_buttons}" # По умолчанию используем это, если оно есть
            # Можно сделать это настраиваемым через "message_id_context_var": "my_var_with_msg_id"

        resolved_message_id = _resolve_value_from_context(message_id_source, context)
        resolved_text = _resolve_value_from_context(params.get("text"), context)
        resolved_buttons_data = _resolve_value_from_context(params.get("inline_keyboard"), context)

        logger.info(f"[TELEGRAM_PLUGIN][HANDLE_STEP_EDIT_MESSAGE] ChatID: {resolved_chat_id}, MessageID: {resolved_message_id}, Text: '{resolved_text}', Buttons: {resolved_buttons_data}")

        if not resolved_chat_id or not resolved_message_id or not resolved_text:
            error_msg = "[TELEGRAM_PLUGIN][HANDLE_STEP_EDIT_MESSAGE] Отсутствует chat_id, message_id или text."
            logger.error(error_msg)
            context["_step_error"] = error_msg
            return context

        message_edited = await self.edit_message_text(
            chat_id=resolved_chat_id,
            message_id=resolved_message_id,
            text=resolved_text,
            buttons_data=resolved_buttons_data
        )

        if message_edited:
            # Контекст можно обновить аналогично send_message, если нужно
            context["telegram_last_edited_message_id"] = message_edited.message_id 
        else:
            error_msg = f"[TELEGRAM_PLUGIN][HANDLE_STEP_EDIT_MESSAGE] Сообщение message_id {resolved_message_id} в chat_id {resolved_chat_id} не было отредактировано."
            logger.error(error_msg)
            context["_step_error"] = error_msg
            
        return context
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 