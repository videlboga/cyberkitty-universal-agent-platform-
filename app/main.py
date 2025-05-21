import os # os нужен для makedirs и path
from loguru import logger # loguru импортируем первым
import logging # Добавил для настройки logging
import threading # <--- ДОБАВЛЕНО для запуска polling в отдельном потоке
import asyncio # Убедимся, что asyncio импортирован

# Настройка логирования для main ДО ВСЕХ ОСТАЛЬНЫХ ИМПОРТОВ
log_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "main_app.log")
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
logger.add(log_file_path, format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip", serialize=True)
logger.info("!!!!!!!!!!!!!!!!! MAIN.PY LOGGER INITIALIZED !!!!!!!!!!!!!!!!!!") # Тестовый лог после инициализации

from dotenv import load_dotenv
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api import agent, scenario, runner, integration, learning, scheduler_updated, user # Добавляем user
from app.core.dependencies import (
    db_client, 
    scheduler_service,             # Используем этот экземпляр
    telegram_app_instance, 
    telegram_plugin, 
    scenario_executor_instance, 
    plugin_manager_instance      # <--- ДОБАВЛЕНО для использования в lifespan
)
import asyncio
from typing import Optional, List, Dict, Any
from telegram import Update # Update остается здесь
from telegram.ext import CallbackContext, CallbackQueryHandler # CallbackContext и CallbackQueryHandler из telegram.ext
from telegram.ext import Application, ApplicationBuilder, CommandHandler # <--- ИЗМЕНЕНИЕ: добавлен Application

# Определяем путь к файлу .env или .env.local в корне проекта
# (app/main.py -> app/ -> корень)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_local_path = os.path.join(project_root, '.env.local')
dotenv_path = os.path.join(project_root, '.env')

loaded_from = None
if os.path.exists(dotenv_local_path):
    load_dotenv(dotenv_path=dotenv_local_path)
    loaded_from = dotenv_local_path
elif os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path) # load_dotenv также может просто искать .env по умолчанию
    loaded_from = dotenv_path

if loaded_from:
    logger.info(f"Loaded environment variables from: {loaded_from}")
else:
    logger.warning("No .env or .env.local file found in project root. Using system environment variables and defaults.")

# Глобальные переменные для хранения экземпляров, инициализируемых в lifespan
# telegram_app_instance: Optional[Application] = None # УДАЛЯЕМ, будем использовать импортированный
telegram_polling_thread: Optional[threading.Thread] = None 

# --- Удаляем run_polling_blocking ---
# def run_polling_blocking():
#     # !!!!! НАЧАЛО РАДИКАЛЬНОГО ТЕСТА ВНУТРИ ПОТОКА !!!!!
# ... весь код run_polling_blocking до конца ...
#     # !!!!! КОНЕЦ РАДИКАЛЬНОГО ТЕСТА ВНУТРИ ПОТОКА !!!!!

# Новая функция для запуска polling в потоке, используя импортированный telegram_app_instance
def _start_telegram_polling_thread_blocking(app_instance: Application):
    """
    Запускает Telegram polling в блокирующем режиме внутри текущего потока.
    Эта функция предназначена для вызова в отдельном потоке (threading.Thread).
    """
    if not app_instance:
        logger.error("ПОТОК TELEGRAM: app_instance не передан. Polling не будет запущен.")
        return

    thread_name = threading.current_thread().name
    logger.info(f"ПОТОК TELEGRAM ({thread_name}): Начало функции _start_telegram_polling_thread_blocking для app_instance (id: {id(app_instance)}).")
    
    original_add_signal_handler = None
    original_remove_signal_handler = None
    loop = None # Определим loop здесь, чтобы он был доступен в finally

    try:
        logging.getLogger("telegram.ext.Application").setLevel(logging.DEBUG)
        logging.getLogger("telegram.ext.ExtBot").setLevel(logging.DEBUG)
        logging.getLogger("telegram.request").setLevel(logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.DEBUG)
        logger.info(f"ПОТОК TELEGRAM ({thread_name}): Уровни DEBUG для логгеров PTB/HTTPX установлены.")

        logger.info(f"ПОТОК TELEGRAM ({thread_name}): Создание и установка нового event loop для потока...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        logger.info(f"ПОТОК TELEGRAM ({thread_name}): Новый event loop ({id(loop)}) создан и установлен.")

        # --- НАЧАЛО MONKEY-PATCHING ---
        if hasattr(loop, 'add_signal_handler') and hasattr(loop, 'remove_signal_handler'): 
            logger.warning(f"ПОТОК TELEGRAM ({thread_name}): Применяем monkey-patch для add_signal_handler и remove_signal_handler.")
            
            original_add_signal_handler = loop.add_signal_handler
            original_remove_signal_handler = loop.remove_signal_handler

            def dummy_signal_handler_for_add(*args, **kwargs):
                logger.info(f"ПОТОК TELEGRAM ({thread_name}): dummy_add_signal_handler ({id(dummy_signal_handler_for_add)}) вызван с {args}, {kwargs}. Ничего не делаем.")
                return

            def dummy_signal_handler_for_remove(*args, **kwargs):
                logger.info(f"ПОТОК TELEGRAM ({thread_name}): dummy_remove_signal_handler ({id(dummy_signal_handler_for_remove)}) вызван с {args}, {kwargs}. Возвращаем True.")
                return True

            loop.add_signal_handler = dummy_signal_handler_for_add
            loop.remove_signal_handler = dummy_signal_handler_for_remove 
            logger.info(f"ПОТОК TELEGRAM ({thread_name}): add_signal_handler заменен на {id(loop.add_signal_handler)}, remove_signal_handler на {id(loop.remove_signal_handler)}")
        else:
            logger.info(f"ПОТОК TELEGRAM ({thread_name}): loop не имеет add_signal_handler/remove_signal_handler, monkey-patch не применяется (вероятно, не Unix).")
        # --- КОНЕЦ MONKEY-PATCHING ---

        logger.info(f"ПОТОК TELEGRAM ({thread_name}): ПЕРЕД вызовом asyncio.run(app_instance.run_polling())...")
        asyncio.run(app_instance.run_polling(drop_pending_updates=True))
        
        logger.info(f"ПОТОК TELEGRAM ({thread_name}): ПОСЛЕ вызова asyncio.run(app_instance.run_polling()). Polling ЗАВЕРШИЛСЯ НОРМАЛЬНО (что необычно).")

    except Exception as e:
        logger.opt(exception=True).error(f"ПОТОК TELEGRAM ({thread_name}): Ошибка в _start_telegram_polling_thread_blocking: {e}")
    finally:
        # --- ВОССТАНОВЛЕНИЕ ОРИГИНАЛЬНЫХ ОБРАБОТЧИКОВ ---
        if original_add_signal_handler and loop and hasattr(loop, 'add_signal_handler'):
            if loop.add_signal_handler.__name__ == 'dummy_signal_handler_for_add':
                 logger.warning(f"ПОТОК TELEGRAM ({thread_name}): Восстанавливаем оригинальный add_signal_handler.")
                 loop.add_signal_handler = original_add_signal_handler
            else:
                 logger.error(f"ПОТОК TELEGRAM ({thread_name}): НЕ МОГУ ВОССТАНОВИТЬ add_signal_handler - он был изменен кем-то еще!")

        if original_remove_signal_handler and loop and hasattr(loop, 'remove_signal_handler'):
            if loop.remove_signal_handler.__name__ == 'dummy_signal_handler_for_remove':
                logger.warning(f"ПОТОК TELEGRAM ({thread_name}): Восстанавливаем оригинальный remove_signal_handler.")
                loop.remove_signal_handler = original_remove_signal_handler
            else:
                logger.error(f"ПОТОК TELEGRAM ({thread_name}): НЕ МОГУ ВОССТАНОВИТЬ remove_signal_handler - он был изменен кем-то еще!")
        # --- КОНЕЦ ВОССТАНОВЛЕНИЯ ---
        logger.critical(f"ПОТОК TELEGRAM ({thread_name}): функция _start_telegram_polling_thread_blocking ЗАВЕРШЕНА (блок finally).")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_polling_thread 
    
    logger.critical("!!!!!!!!!!!!!! LIFESPAN: НАЧАЛО ФУНКЦИИ lifespan !!!!!!!!!!!!!!")
    logger.info("Application startup event commencing (lifespan).")

    # Используем импортированные экземпляры
    # scheduler_service УЖЕ импортирован и доступен
    # plugin_manager_instance УЖЕ импортирован и доступен

    if db_client:
        logger.info("Закрытие соединения с MongoDB (lifespan)...")
        # db_client.close() # Закрывать будем при shutdown
        logger.info("Соединение с MongoDB НЕ закрыто на старте (будет закрыто при shutdown).")
    else:
        logger.error("db_client is None, cannot close MongoDB connection.")

    if telegram_app_instance: # Используем импортированный экземпляр
        logger.info(f"Lifespan: Используем импортированный telegram_app_instance (id: {id(telegram_app_instance)}).")
        if "scenario_executor" in telegram_app_instance.bot_data:
            logger.info(f"Lifespan: scenario_executor (id: {id(telegram_app_instance.bot_data['scenario_executor'])}) найден в bot_data telegram_app_instance.")
        else:
            # Это может быть нормально, если executor добавляется позже или не всегда нужен в bot_data до старта polling
            logger.warning("Lifespan: scenario_executor НЕ НАЙДЕН в bot_data telegram_app_instance на момент старта lifespan.")
    else:
        logger.error("Lifespan: telegram_app_instance (импортированный из dependencies) отсутствует! Polling НЕ БУДЕТ запущен.")

    if plugin_manager_instance:
        logger.info(f"Lifespan: PluginManager instance (id: {id(plugin_manager_instance)}) существует. Зарегистрированные плагины: {list(plugin_manager_instance.get_all_plugins().keys())}")
    else:
        logger.warning("Lifespan: plugin_manager_instance отсутствует.")
    
    if telegram_plugin:
        logger.info(f"Lifespan: telegram_plugin instance (id: {id(telegram_plugin)}) существует.")
    else:
        logger.warning("Lifespan: telegram_plugin отсутствует.")
    
    if scenario_executor_instance:
        logger.info(f"Lifespan: scenario_executor_instance (id: {id(scenario_executor_instance)}) существует.")
    else:
        logger.warning("Lifespan: scenario_executor_instance отсутствует.")

    # --- Запуск Telegram Polling в отдельном потоке ---
    if telegram_app_instance: # Проверяем, что экземпляр из dependencies существует
        logger.info("Lifespan: Условие для запуска Telegram polling thread пройдено (telegram_app_instance существует). Запускаем поток...")
        telegram_polling_thread = threading.Thread(
            target=_start_telegram_polling_thread_blocking, 
            args=(telegram_app_instance,), # Передаем экземпляр в поток
            daemon=True,
            name="TelegramPollingThread" # Даем потоку имя
        )
        telegram_polling_thread.start()
        logger.info(f"Lifespan: Поток Telegram polling ЗАПУЩЕН (is_alive: {telegram_polling_thread.is_alive()}). Имя потока: {telegram_polling_thread.name}")
    else:
        logger.error("Lifespan: telegram_app_instance (импортированный) отсутствует. Поток Telegram НЕ ЗАПУЩЕН.")

    yield 

    logger.info("Application shutdown event commencing (lifespan).")
    # --- Остановка Telegram Polling ---
    if telegram_polling_thread and telegram_polling_thread.is_alive():
        logger.info(f"Lifespan Shutdown: Попытка остановить Telegram polling (для app_instance id: {id(telegram_app_instance) if telegram_app_instance else 'N/A'})...")
        
        async def do_stop_polling_gracefully():
            if telegram_app_instance and hasattr(telegram_app_instance, 'is_running') and telegram_app_instance.is_running:
                logger.info(f"Lifespan Shutdown (async): Вызов await telegram_app_instance.stop_polling() для app_instance (id: {id(telegram_app_instance)})...")
                try:
                    await telegram_app_instance.stop_polling()
                    logger.info(f"Lifespan Shutdown (async): await telegram_app_instance.stop_polling() для app_instance (id: {id(telegram_app_instance)}) завершен.")
                except Exception as e_stop:
                    logger.opt(exception=True).error(f"Lifespan Shutdown (async): Ошибка при вызове telegram_app_instance.stop_polling(): {e_stop}")
            elif telegram_app_instance:
                logger.info(f"Lifespan Shutdown (async): telegram_app_instance (id: {id(telegram_app_instance)}) не запущен (is_running=False), stop_polling() не вызывается.")
            else:
                logger.warning("Lifespan Shutdown (async): telegram_app_instance отсутствует, stop_polling() не может быть вызван.")

        try:
            loop = asyncio.get_event_loop_policy().get_event_loop() # Получаем текущий цикл событий FastAPI
            if loop.is_running(): # Если он еще работает
                logger.info(f"Lifespan Shutdown: Запуск do_stop_polling_gracefully через run_coroutine_threadsafe в цикле {id(loop)}.")
                future = asyncio.run_coroutine_threadsafe(do_stop_polling_gracefully(), loop)
                future.result(timeout=10) # Ждем результат с таймаутом
                logger.info(f"Lifespan Shutdown: future.result() для do_stop_polling_gracefully() получен.")
            else: # Если основной цикл уже остановлен, пытаемся запустить в новом
                logger.warning(f"Lifespan Shutdown: Основной event loop ({id(loop)}) не запущен. Пытаемся запустить do_stop_polling_gracefully через asyncio.run().")
                asyncio.run(do_stop_polling_gracefully())
            logger.info(f"Lifespan Shutdown: Попытка остановить polling через do_stop_polling_gracefully() выполнена.")
        except Exception as e_stop_wrapper:
            logger.opt(exception=True).error(f"Lifespan Shutdown: Ошибка при попытке остановить polling через do_stop_polling_gracefully(): {e_stop_wrapper}")

        logger.info(f"Lifespan Shutdown: Ожидание завершения потока {telegram_polling_thread.name} (join)...")
        telegram_polling_thread.join(timeout=15) 
        if telegram_polling_thread.is_alive():
            logger.warning(f"Lifespan Shutdown: Поток {telegram_polling_thread.name} все еще жив после join(15).")
        else:
            logger.info(f"Lifespan Shutdown: Поток {telegram_polling_thread.name} успешно завершен.")
            
    elif telegram_polling_thread:
        logger.info(f"Lifespan Shutdown: Поток {telegram_polling_thread.name} уже не жив.")
    else:
        logger.info("Lifespan Shutdown: Поток Telegram polling не был запущен или уже не существует.")

    # Остановка SchedulerService
    if scheduler_service:
        logger.info("Попытка остановить SchedulerService (lifespan)...")
        await scheduler_service.stop()
        logger.info("SchedulerService остановлен (lifespan).")
    
    # Закрытие клиента MongoDB
    if db_client:
        logger.info("Закрытие соединения с MongoDB (при shutdown lifespan)...")
        db_client.close()
        logger.info("Соединение с MongoDB закрыто (при shutdown lifespan).")
    
    logger.info("Application shutdown complete (lifespan).")

# Переносим создание FastAPI app и подключение роутеров сюда, в самый конец файла.

logger.critical("!!!!!!!!!!!!!! MAIN.PY: ПЕРЕД СОЗДАНИЕМ ЭКЗЕМПЛЯРА FastAPI !!!!!!!!!!!!!!") # <--- НОВЫЙ ЛОГ

app = FastAPI(
    title="Universal Agent Platform API",
    version="0.1.0",
    description="API for managing agents, scenarios, and their execution.",
    lifespan=lifespan # lifespan привязывается здесь
)

# Подключение роутеров API
logger.info("MAIN.PY: Подключение API роутеров...")
app.include_router(agent.router, prefix="/api/v1")
app.include_router(scenario.router, prefix="/api/v1")
app.include_router(runner.router, prefix="/api/v1")
app.include_router(integration.router, prefix="/api/v1")
app.include_router(learning.router, prefix="/api/v1")
app.include_router(scheduler_updated.router, prefix="/api/v1") # Обновленный роутер для планировщика
app.include_router(user.router, prefix="/api/v1") # Добавляем роутер user
logger.info("MAIN.PY: API роутеры подключены.")

# Обработчики исключений должны быть здесь же или после подключения роутеров
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.opt(exception=True).error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

logger.info("MAIN.PY: Экземпляр FastAPI 'app' полностью сконфигурирован.")

# if __name__ == "__main__":
#     import uvicorn
#     logger.info("Starting Uvicorn directly from main.py (likely for debugging)")
#     uvicorn.run(app, host="0.0.0.0", port=8000) 