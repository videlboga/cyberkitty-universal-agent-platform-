import os
import json
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple
from loguru import logger
from datetime import datetime, time, timedelta, timezone
import asyncio
import requests
import httpx
import pytz
from app.utils.dialog_state import DialogStateManager
from app.utils.user_profile import UserProfileManager
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.id_helper import ensure_mongo_id
from apscheduler.jobstores.mongodb import MongoDBJobStore

class SchedulerService:
    """
    Универсальный сервис планировщика для запуска задач по расписанию.
    
    Поддерживает различные типы триггеров:
    - daily: ежедневно в указанное время
    - weekly: еженедельно в указанный день и время
    - monthly: ежемесячно в указанный день и время
    - once: однократно в указанное время
    - interval: с указанным интервалом
    
    Поддерживает различные типы действий:
    - run_agent: запуск агента с указанным контекстом
    - send_notification: отправка уведомления через Telegram
    - api_call: произвольный вызов API
    """
    
    def __init__(self, scenario_executor_instance, api_base_url: str = None, mongo_uri: str = None):
        """
        Инициализация сервиса планировщика
        
        Args:
            api_base_url: Базовый URL API для работы с коллекциями и агентами
            mongo_uri: URI для подключения к MongoDB
        """
        # Получаем значения из переменных окружения, если они не указаны явно
        self.api_base_url = api_base_url or os.getenv("API_URL", "http://localhost:8000")
        self.mongo_uri = mongo_uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGODB_DATABASE_NAME", "agent_platform")
        
        # Логируем используемые значения для диагностики
        logger.info(f"SchedulerService: используется API URL: {self.api_base_url}")
        logger.info(f"SchedulerService: используется MongoDB URI: {self.mongo_uri}")
        logger.info(f"SchedulerService: используется MongoDB DATABASE NAME: {self.db_name}")
        
        self.mongo_client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.mongo_client[self.db_name]
        self.dialog_state_manager = DialogStateManager(self.api_base_url)
        self.user_profile_manager = UserProfileManager(self.api_base_url)
        self.scheduler_running = False
        self.scheduled_tasks = {}
        self.task_history = {}
        self.collection_name = "scheduled_tasks"
        logger.info("Универсальный SchedulerService инициализирован")
    
    async def start(self):
        """Запускает планировщик задач"""
        if self.scheduler_running:
            logger.warning("Планировщик уже запущен")
            return
            
        self.scheduler_running = True
        
        # Загружаем задачи из базы данных
        await self._load_tasks_from_db()
        
        # Исправляем задачи с значением 'now'
        await self.fix_now_datetime_in_tasks()
        
        # Запускаем цикл планировщика в отдельной задаче
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        logger.info("Планировщик запущен")
    
    async def stop(self):
        """Остановка планировщика"""
        self.scheduler_running = False
        logger.info("Планировщик остановлен")
    
    async def _scheduler_loop(self):
        """
        Основной цикл планировщика
        """
        while self.scheduler_running:
            try:
                # Получаем текущее время с timezone
                now = datetime.now(timezone.utc)
                
                # Проверяем каждую задачу
                for task_id, task in list(self.scheduled_tasks.items()):
                    try:
                        # Проверяем, должен ли сработать триггер
                        if await self._should_trigger(task, now):
                            logger.info(f"Задача {task_id}: триггер сработал, проверка _was_recently_executed...")
                            was_recent = self._was_recently_executed(task_id, task, now)
                            logger.info(f"Задача {task_id}: _was_recently_executed вернула: {was_recent}")
                            if not was_recent:
                                logger.info(f"Задача {task_id}: ЗАПУСК _execute_action")
                                # Запускаем действие задачи
                                await self._execute_action(task)
                                # Отмечаем задачу как выполненную
                                self._mark_executed(task_id, now)
                                logger.info(f"Задача {task_id}: _execute_action и _mark_executed ВЫПОЛНЕНЫ")
                            else:
                                logger.info(f"Задача {task_id}: ПРОПУСК _execute_action из-за _was_recently_executed")
                    except Exception as e:
                        logger.error(f"Ошибка при обработке задачи {task_id}: {e}")
                
                # Ждем до следующей проверки
                await asyncio.sleep(60)  # Проверяем каждую минуту
                
            except Exception as e:
                logger.error(f"Ошибка в цикле планировщика: {e}")
                await asyncio.sleep(60)  # Ждем 1 минуту перед повторной попыткой
    
    def _parse_datetime(self, datetime_str: str) -> datetime:
        """
        Парсит строку datetime с учетом timezone
        
        Args:
            datetime_str: Строка с датой и временем
            
        Returns:
            datetime: Объект datetime с timezone
        """
        try:
            # Пробуем сначала ISO формат
            dt = datetime.fromisoformat(datetime_str)
            if dt.tzinfo is None:
                # Если timezone не указан, используем UTC
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            try:
                # Пробуем стандартный формат
                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                # Добавляем UTC timezone
                return dt.replace(tzinfo=timezone.utc)
            except ValueError as e:
                raise ValueError(f"Неверный формат даты и времени: {datetime_str}") from e

    async def _should_trigger(self, task: Dict[str, Any], now: datetime) -> bool:
        """
        Проверяет, должен ли сработать триггер задачи
        
        Args:
            task: Конфигурация задачи
            now: Текущее время (с timezone)
            
        Returns:
            bool: True если триггер должен сработать
        """
        if not task.get("enabled", True):
            return False
        
        trigger_type = task.get("trigger_type")
        trigger_config = task.get("trigger_config", {})
        
        if not trigger_type or not trigger_config:
            return False
        
        if trigger_type == "once":
            datetime_str = trigger_config.get("datetime")
            task_id = task.get("id", "неизвестно")
            
            if not datetime_str:
                logger.warning(f"Задача {task_id}: отсутствует параметр datetime в конфигурации триггера")
                return False
            
            try:
                # Обработка специального значения "now"
                if datetime_str == "now":
                    logger.info(f"Задача {task_id}: обнаружено значение datetime = 'now', заменяем на текущее время")
                    
                    # Получаем текущее время в формате ISO с timezone
                    current_time = now.replace(microsecond=0).isoformat()
                    
                    # Если задача имеет ID, обновляем ее конфигурацию
                    if task_id != "неизвестно":
                        # Сохраняем старые параметры конфигурации
                        updated_config = trigger_config.copy()
                        updated_config["datetime"] = current_time
                        
                        # Запускаем асинхронное обновление в базе данных без ожидания результата
                        asyncio.create_task(self._update_task_in_db(task_id, {
                            "trigger_config": updated_config
                        }))
                        
                        # Обновляем локальную копию задачи
                        if task_id in self.scheduled_tasks and "trigger_config" in self.scheduled_tasks[task_id]:
                            self.scheduled_tasks[task_id]["trigger_config"]["datetime"] = current_time
                        
                        logger.info(f"Задача {task_id}: значение 'now' заменено на {current_time}")
                    
                    # Сигнализируем о необходимости запуска задачи
                    return True
                
                # Парсим datetime с учетом timezone
                target_datetime = self._parse_datetime(datetime_str)
                
                # Вычисляем разницу в секундах между текущим и целевым временем
                diff_seconds = (now - target_datetime).total_seconds()
                margin_seconds = trigger_config.get("margin_seconds", 300)  # 5 минут по умолчанию
                
                # Проверяем, находится ли текущее время в пределах допустимой погрешности
                is_valid_time_window = 0 <= diff_seconds <= margin_seconds
                
                if is_valid_time_window:
                    logger.info(f"Задача {task_id}: триггер 'once' сработал (целевое время: {target_datetime}, разница: {diff_seconds} сек.)")
                
                return is_valid_time_window
                
            except ValueError as e:
                logger.error(f"Ошибка при обработке триггера once: {e}")
                return False
            
        elif trigger_type == "daily":
            # Ежедневный триггер
            time_str = trigger_config.get("time", "09:00")
            target_time = self._parse_time(time_str)
            margin_minutes = trigger_config.get("margin_minutes", 5)
            
            return self._is_time_match(now.time(), target_time, margin_minutes)
            
        elif trigger_type == "weekly":
            # Еженедельный триггер
            day = trigger_config.get("day", "monday").lower()
            time_str = trigger_config.get("time", "10:00")
            target_time = self._parse_time(time_str)
            margin_minutes = trigger_config.get("margin_minutes", 5)
            
            current_day = now.strftime("%A").lower()
            return current_day == day and self._is_time_match(now.time(), target_time, margin_minutes)
            
        elif trigger_type == "monthly":
            # Ежемесячный триггер
            day = trigger_config.get("day", 1)
            time_str = trigger_config.get("time", "10:00")
            target_time = self._parse_time(time_str)
            margin_minutes = trigger_config.get("margin_minutes", 5)
            
            return now.day == day and self._is_time_match(now.time(), target_time, margin_minutes)
            
        elif trigger_type == "interval":
            # Триггер с интервалом
            interval_minutes = trigger_config.get("interval_minutes", 60)  # 60 минут по умолчанию
            start_time = trigger_config.get("start_time")
            task_id = task.get("id", "неизвестно")
            
            # Если указано время начала, проверяем, прошло ли оно
            if start_time:
                try:
                    # Парсинг start_time в разных форматах с проверкой на валидность
                    try:
                        # Сначала пробуем fromisoformat
                        start_datetime = self._parse_datetime(start_time)
                    except ValueError:
                        try:
                            # Если не получилось, пробуем стандартный strptime
                            start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                        except ValueError:
                            # Если и это не сработало, логируем ошибку и используем текущее время
                            logger.error(f"Задача {task_id}: невозможно преобразовать start_time '{start_time}' в допустимый формат. Используем текущее время.")
                            start_datetime = now
                    
                    if now < start_datetime:
                        logger.info(f"Задача {task_id}: еще не наступило время запуска (start_time: {start_datetime})")
                        return False
                except Exception as e:
                    logger.error(f"Задача {task_id}: ошибка при обработке start_time: {e}")
                    # Продолжаем выполнение, игнорируя start_time
            
            # Проверяем, прошло ли достаточно времени с последнего выполнения
            last_execution = self._get_last_execution_time(task.get("id"))
            if last_execution:
                elapsed_minutes = (now - last_execution).total_seconds() / 60
                should_trigger = elapsed_minutes >= interval_minutes
                
                if should_trigger:
                    logger.info(f"Задача {task_id}: триггер 'interval' сработал (прошло {elapsed_minutes:.1f} мин. из {interval_minutes} мин.)")
                
                return should_trigger
            
            # Если задача еще не выполнялась, выполняем ее сейчас
            logger.info(f"Задача {task_id}: первый запуск задачи с интервальным триггером")
            return True
            
        # Неизвестный тип триггера
        logger.warning(f"Задача {task.get('id', 'неизвестно')}: неизвестный тип триггера: {trigger_type}")
        return False
    
    def _parse_time(self, time_str: str) -> time:
        """
        Преобразует строку времени в объект time
        
        Args:
            time_str: Строка времени в формате "HH:MM"
            
        Returns:
            time: Объект времени
        """
        try:
            hours, minutes = map(int, time_str.split(":"))
            return time(hours, minutes)
        except Exception:
            # В случае ошибки возвращаем время по умолчанию (9:00)
            logger.warning(f"Ошибка при парсинге времени: {time_str}, используется время по умолчанию (09:00)")
            return time(9, 0)
    
    def _is_time_match(self, current_time: time, target_time: time, margin_minutes: int = 5) -> bool:
        """
        Проверяет, соответствует ли текущее время целевому с учетом погрешности
        
        Args:
            current_time: Текущее время
            target_time: Целевое время
            margin_minutes: Погрешность в минутах
            
        Returns:
            bool: True если время соответствует, иначе False
        """
        # Преобразуем всё в минуты для удобства сравнения
        current_minutes = current_time.hour * 60 + current_time.minute
        target_minutes = target_time.hour * 60 + target_time.minute
        
        # Проверка с учетом погрешности
        return abs(current_minutes - target_minutes) <= margin_minutes
    
    def _was_recently_executed(self, task_id: str, task: Dict[str, Any], now: datetime) -> bool:
        """
        Проверяет, не была ли задача недавно выполнена
        
        Args:
            task_id: ID задачи
            task: Конфигурация задачи
            now: Текущее время (с timezone)
            
        Returns:
            bool: True если задача была недавно выполнена
        """
        last_execution = self._get_last_execution_time(task_id)
        if not last_execution:
            logger.info(f"Задача {task_id} (_was_recently_executed): нет last_execution, возвращаем False")
            return False
        
        # Получаем интервал между выполнениями
        trigger_config = task.get("trigger_config", {})
        min_interval = trigger_config.get("min_interval_minutes", 1)  # 1 минута по умолчанию
        
        # Вычисляем разницу во времени
        time_diff = (now - last_execution).total_seconds() / 60
        
        result = time_diff < min_interval
        logger.info(f"Задача {task_id} (_was_recently_executed): last_execution: {last_execution}, min_interval: {min_interval}, time_diff: {time_diff:.2f} мин, результат: {result}")
        return result
    
    def _get_last_execution_time(self, task_id: str) -> Optional[datetime]:
        """
        Получает время последнего выполнения задачи
        
        Args:
            task_id: ID задачи
            
        Returns:
            Optional[datetime]: Время последнего выполнения или None
        """
        if task_id not in self.task_history:
            return None
        
        return self.task_history[task_id]
    
    def _mark_executed(self, task_id: str, execution_time: datetime):
        """
        Отмечает задачу как выполненную
        
        Args:
            task_id: ID задачи
            execution_time: Время выполнения (с timezone)
        """
        self.task_history[task_id] = execution_time
        
        # Для одноразовых задач отключаем их после выполнения
        task = self.scheduled_tasks.get(task_id)
        if task and task.get("trigger_type") == "once":
            task["enabled"] = False
            # Асинхронно обновляем в базе данных
            asyncio.create_task(self._update_task_in_db(task_id, task))
    
    async def _get_users_with_notifications(self) -> List[Dict[str, Any]]:
        """
        Получает список пользователей с включенными уведомлениями
        
        Returns:
            List[Dict[str, Any]]: Список пользователей
        """
        try:
            response = requests.get(
                f"{self.api_base_url}/db/collections/users/items",
                params={"filter": json.dumps({"notifications_enabled": True})}
            )
            
            if response.status_code == 200:
                users = response.json()
                logger.info(f"Получено {len(users)} пользователей с уведомлениями")
                return users
            else:
                logger.error(f"Ошибка при получении пользователей с уведомлениями: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Ошибка при получении пользователей с уведомлениями: {e}")
            return []
    
    async def _execute_action(self, task: Dict[str, Any]):
        """
        Выполняет действие, указанное в задаче
        
        Args:
            task: Конфигурация задачи
        """
        action_type = task.get("action_type")
        action_config = task.get("action_config", {})
        
        try:
            if action_type == "run_agent":
                # Передаем action_config напрямую в _run_agent
                await self._run_agent(action_config)
            elif action_type == "send_notification":
                await self._send_notification(action_config)
            elif action_type == "api_call":
                await self._api_call(action_config)
            else:
                logger.error(f"Неизвестный тип действия: {action_type}")
        except Exception as e:
            logger.error(f"Ошибка при выполнении действия {action_type}: {e}")
    
    async def _run_agent(self, config: Dict[str, Any]):
        """
        Запускает агента с указанной конфигурацией
        
        Args:
            config: Конфигурация для запуска агента
        """
        try:
            # Получаем параметры из конфигурации
            agent_id = config.get("agent_id")
            user_id = config.get("user_id")
            chat_id = config.get("chat_id")
            
            if not agent_id or not user_id:
                logger.error("Не указаны обязательные параметры agent_id или user_id")
                return
            
            # Если chat_id не указан, используем user_id
            if not chat_id:
                chat_id = user_id
            
            # Запускаем агента через API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/agent-actions/{agent_id}/execute",
                    json={
                        "context": {
                            "user_id": user_id,
                            "chat_id": chat_id,
                            **config.get("context", {})
                        }
                    }
                )
            
            logger.info(f"[DEBUG _run_agent] response.text={response.text}")
            
            if response.status_code == 200:
                logger.info(f"Агент {agent_id} успешно запущен для пользователя {user_id}")
            else:
                logger.error(f"Ошибка при запуске агента: {response.status_code}")
                logger.error(f"Ответ сервера: {response.text}")
                
                # Уведомление об ошибке также должно использовать httpx
                async with httpx.AsyncClient() as client:
                    telegram_response = await client.post(
                        f"{self.api_base_url}/integration/telegram/send",
                        json={
                            "chat_id": chat_id,
                            "text": f"Scheduled agent {agent_id} could not be started properly. See logs."
                        }
                    )
                logger.info(f"[DEBUG _run_agent] telegram_response.status_code={telegram_response.status_code}")
                logger.info(f"[DEBUG _run_agent] telegram_response.text={telegram_response.text}")
                
                if telegram_response.status_code == 200:
                    logger.info(f"Отправлено сообщение пользователю {user_id} через Telegram")
                else:
                    logger.error(f"Ошибка при отправке сообщения через Telegram: {telegram_response.status_code}")
                    logger.error(f"Ответ Telegram: {telegram_response.text}")
                    
        except Exception as e:
            logger.error(f"Ошибка при запуске агента: {e}", exc_info=True)
    
    async def _send_notification(self, config: Dict[str, Any]):
        """
        Отправляет уведомление через Telegram
        
        Args:
            config: Конфигурация для отправки уведомления
        """
        try:
            user_id = config.get("user_id")
            chat_id = config.get("chat_id")
            text = config.get("text")
            
            if not user_id or not text:
                logger.error("Не указаны обязательные параметры user_id или text")
                return
            
            # Если chat_id не указан, пытаемся получить его из профиля пользователя
            if not chat_id:
                profile = await self.user_profile_manager.get_profile(user_id)
                chat_id = profile.get("chat_id", user_id)
            
            # Отправляем сообщение через Telegram
            response = requests.post(
                f"{self.api_base_url}/integration/telegram/send",
                json={
                    "chat_id": chat_id,
                    "text": text
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Отправлено уведомление пользователю {user_id}")
            else:
                logger.error(f"Ошибка при отправке уведомления: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления: {e}")
    
    async def _api_call(self, config: Dict[str, Any]):
        """
        Выполняет произвольный API-вызов
        
        Args:
            config: Конфигурация для API-вызова
        """
        try:
            method = config.get("method", "GET")
            url = config.get("url")
            headers = config.get("headers", {})
            data = config.get("data", {})
            
            if not url:
                logger.error("Не указан обязательный параметр url")
                return
            
            # Выполняем запрос
            response = requests.request(method, url, headers=headers, json=data)
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"API-вызов выполнен успешно: {url}")
            else:
                logger.error(f"Ошибка при выполнении API-вызова: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Ошибка при выполнении API-вызова: {e}")
    
    async def _validate_task_config(self, task_config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Валидирует конфигурацию задачи
        
        Args:
            task_config: Конфигурация задачи
            
        Returns:
            Tuple[bool, Optional[str]]: (True, None) если конфигурация валидна,
                                      (False, str) если есть ошибки
        """
        # Проверка обязательных полей
        required_fields = ["user_id", "trigger_type", "trigger_config", "action_type", "action_config"]
        for field in required_fields:
            if field not in task_config:
                return False, f"Отсутствует обязательное поле: {field}"
        
        # Проверка типа триггера
        trigger_type = task_config.get("trigger_type")
        trigger_config = task_config.get("trigger_config", {})
        
        if trigger_type == "once":
            if "datetime" not in trigger_config:
                return False, "Для once триггера требуется указать дату и время (datetime)"
            
            # Проверка формата datetime
            datetime_str = trigger_config.get("datetime")
            if datetime_str != "now":
                try:
                    # Парсим datetime с учетом timezone
                    self._parse_datetime(datetime_str)
                except ValueError as e:
                    return False, str(e)
            
        elif trigger_type == "interval":
            if "interval_minutes" not in trigger_config:
                return False, "Для interval триггера требуется указать интервал в минутах (interval_minutes)"
            
            # Проверка интервала
            interval_minutes = trigger_config.get("interval_minutes")
            try:
                interval_int = int(interval_minutes)
                if interval_int <= 0:
                    return False, f"Интервал должен быть положительным числом: {interval_minutes}"
            except Exception:
                return False, f"Неверный формат интервала: {interval_minutes}"
            
            # Проверка start_time, если указано
            start_time = trigger_config.get("start_time")
            if start_time and start_time != "now":
                try:
                    # Парсим datetime с учетом timezone
                    self._parse_datetime(start_time)
                except ValueError as e:
                    return False, str(e)
        
        # Проверка типа действия
        action_type = task_config.get("action_type")
        if action_type not in ["run_agent", "send_notification", "api_call"]:
            return False, f"Неподдерживаемый тип действия: {action_type}"
        
        # Проверка конфигурации действия
        action_config = task_config.get("action_config", {})
        if not action_config:
            return False, "Отсутствует конфигурация действия"
        
        return True, None

    async def add_task(self, task_config: Dict[str, Any]) -> str:
        """
        Добавить новую задачу в планировщик
        
        Args:
            task_config: Конфигурация задачи, включающая:
                - id: уникальный идентификатор задачи (опционально)
                - name: название задачи (опционально)
                - user_id: ID пользователя
                - trigger_type: тип триггера (daily, weekly, monthly, once, interval)
                - trigger_config: конфигурация триггера (время, день недели и т.д.)
                - action_type: тип действия (run_agent, send_notification, api_call)
                - action_config: конфигурация действия (agent_id, payload и т.д.)
                - enabled: включена ли задача (по умолчанию True)
                - created_at: время создания (опционально)
                
        Returns:
            str: ID добавленной задачи
            
        Raises:
            ValueError: Если конфигурация задачи недействительна
        """
        # Генерация ID, если не указан
        task_id = task_config.get("id", str(uuid.uuid4()))
        
        # Добавляем время создания с timezone, если не указано
        if "created_at" not in task_config:
            task_config["created_at"] = datetime.now(timezone.utc).isoformat()
        
        # Устанавливаем enabled в True, если не указано
        if "enabled" not in task_config:
            task_config["enabled"] = True
        
        # Обрабатываем datetime в trigger_config
        if "trigger_config" in task_config:
            trigger_config = task_config["trigger_config"]
            if "datetime" in trigger_config and trigger_config["datetime"] != "now":
                try:
                    # Парсим datetime с учетом timezone
                    dt = self._parse_datetime(trigger_config["datetime"])
                    # Сохраняем в ISO формате с timezone
                    trigger_config["datetime"] = dt.isoformat()
                except ValueError as e:
                    raise ValueError(f"Неверный формат datetime в trigger_config: {e}")
        
        # Валидация конфигурации задачи
        is_valid, error_message = await self._validate_task_config(task_config)
        if not is_valid:
            error_msg = f"Недействительная конфигурация задачи: {error_message}"
            logger.error(f"{error_msg} (ID: {task_id})")
            raise ValueError(error_msg)
        
        # Сохранение задачи в памяти
        self.scheduled_tasks[task_id] = task_config
        
        # Сохранение в базу данных
        await self._save_task_to_db(task_id, task_config)
        
        logger.info(f"Добавлена задача {task_id} для пользователя {task_config.get('user_id')}")
        return task_id
    
    async def remove_task(self, task_id: str) -> bool:
        """
        Удалить задачу из планировщика
        
        Args:
            task_id: ID задачи
            
        Returns:
            bool: True если задача успешно удалена, иначе False
        """
        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]
            await self._remove_task_from_db(task_id)
            logger.info(f"Удалена задача {task_id}")
            return True
        
        logger.warning(f"Задача {task_id} не найдена")
        return False
    
    async def update_task(self, task_id: str, task_config: Dict[str, Any]) -> bool:
        """
        Обновить существующую задачу
        
        Args:
            task_id: ID задачи
            task_config: Новая конфигурация задачи
            
        Returns:
            bool: True если задача успешно обновлена, иначе False
        """
        if task_id not in self.scheduled_tasks:
            logger.warning(f"Задача {task_id} не найдена")
            return False
        
        # Обновляем задачу в памяти
        self.scheduled_tasks[task_id].update(task_config)
        
        # Обновляем в базе данных
        await self._update_task_in_db(task_id, self.scheduled_tasks[task_id])
        
        logger.info(f"Обновлена задача {task_id}")
        return True
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о задаче
        
        Args:
            task_id: ID задачи
            
        Returns:
            Dict[str, Any]: Конфигурация задачи или None, если задача не найдена
        """
        return self.scheduled_tasks.get(task_id)
    
    async def get_tasks_by_user(self, user_id: Union[str, int]) -> List[Dict[str, Any]]:
        """
        Получить все задачи пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            List[Dict[str, Any]]: Список задач пользователя
        """
        user_tasks = []
        for task_id, task in self.scheduled_tasks.items():
            if str(task.get("user_id")) == str(user_id):
                task_copy = task.copy()
                task_copy["id"] = task_id
                user_tasks.append(task_copy)
        
        return user_tasks
    
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Получить все задачи
        
        Returns:
            List[Dict[str, Any]]: Список всех задач
        """
        all_tasks = []
        for task_id, task in self.scheduled_tasks.items():
            task_copy = task.copy()
            task_copy["id"] = task_id
            all_tasks.append(task_copy)
        
        return all_tasks
    
    async def _load_tasks_from_db(self):
        """
        Загружает задачи из базы данных
        """
        try:
            # Используем прямое подключение к MongoDB
            collection = self.db[self.collection_name]
            
            # Проверяем, существует ли коллекция
            if self.collection_name not in await self.db.list_collection_names():
                logger.info(f"Коллекция {self.collection_name} не существует, создаем...")
                await self.db.create_collection(self.collection_name)
                logger.info(f"Коллекция {self.collection_name} создана")
                return
            
            # Получаем все задачи из коллекции
            cursor = collection.find({})
            tasks = await cursor.to_list(length=100)
            
            # Очищаем текущие задачи и загружаем из базы
            self.scheduled_tasks = {}
            
            for task in tasks:
                # Извлекаем ID задачи
                task_id = task.pop("_id", None) or task.pop("id", None)
                if task_id:
                    # Преобразуем ObjectId в строку, если необходимо
                    if hasattr(task_id, "__str__"):
                        task_id = str(task_id)
                    
                    # Обрабатываем datetime в trigger_config
                    if "trigger_config" in task:
                        trigger_config = task["trigger_config"]
                        if "datetime" in trigger_config and trigger_config["datetime"] != "now":
                            try:
                                # Парсим datetime с учетом timezone
                                dt = self._parse_datetime(trigger_config["datetime"])
                                # Сохраняем в ISO формате с timezone
                                trigger_config["datetime"] = dt.isoformat()
                            except ValueError as e:
                                logger.error(f"Ошибка при обработке datetime в задаче {task_id}: {e}")
                                continue
                    
                    self.scheduled_tasks[task_id] = task
            
            logger.info(f"Загружено {len(self.scheduled_tasks)} задач из базы данных")
        except Exception as e:
            logger.error(f"Ошибка при загрузке задач из базы данных: {e}")
    
    def _serialize_datetime(self, obj):
        """Сериализует datetime объекты для MongoDB"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    async def _save_task_to_db(self, task_id: str, task_config: Dict[str, Any]):
        """
        Сохраняет задачу в базу данных
        """
        try:
            collection = self.db[self.collection_name]
            task_data = task_config.copy()
            task_data["id"] = task_id
            
            # Сериализуем все datetime объекты
            serialized_data = json.loads(
                json.dumps(task_data, default=self._serialize_datetime)
            )
            
            # Централизовано: всегда ensure_mongo_id
            result = await collection.insert_one(ensure_mongo_id(serialized_data))
            if result.inserted_id:
                logger.info(f"Задача {task_id} сохранена в базе данных")
            else:
                logger.error("Ошибка при сохранении задачи в базе данных")
        except Exception as e:
            logger.error(f"Ошибка при сохранении задачи в базе данных: {e}")
    
    async def _update_task_in_db(self, task_id: str, task_config: Dict[str, Any]):
        """
        Обновляет задачу в базе данных
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                collection = self.db[self.collection_name]
                
                # Сериализуем все datetime объекты
                serialized_data = json.loads(
                    json.dumps(task_config, default=self._serialize_datetime)
                )
                
                # Ищем задачу по ID
                existing_task = await collection.find_one({"id": task_id})
                
                if existing_task:
                    # Если обновляется только часть полей, мержим их с существующими
                    if any(key.startswith("trigger_config.") or key.startswith("action_config.") for key in serialized_data.keys()):
                        # Это частичное обновление внутренних полей
                        update_ops = {"$set": serialized_data}
                    else:
                        # Для полного обновления секций создаем обновление с учетом существующих данных
                        merged_data = {}
                        
                        # Проходим по всем ключам в обновлении
                        for key, value in serialized_data.items():
                            if key in ["trigger_config", "action_config"] and isinstance(value, dict) and key in existing_task:
                                # Для конфигурационных объектов мержим с существующими
                                merged_value = existing_task[key].copy()
                                merged_value.update(value)
                                merged_data[key] = merged_value
                            else:
                                # Для других полей просто заменяем
                                merged_data[key] = value
                        
                        # Формируем операцию обновления
                        update_ops = {"$set": merged_data}
                    
                    # Обновляем задачу в базе данных
                    result = await collection.update_one(
                        {"id": task_id},
                        update_ops
                    )
                    
                    if result.modified_count > 0:
                        logger.info(f"Задача {task_id} обновлена в базе данных")
                    else:
                        logger.info(f"Задача {task_id} не изменилась в базе данных (возможно, новые данные идентичны существующим)")
                    
                    return
                else:
                    # Если задача не найдена, создаем ее
                    logger.warning(f"Задача {task_id} не найдена в базе данных, создаем новую")
                    
                    # Проверяем наличие минимально необходимых полей для создания задачи
                    if "trigger_type" not in serialized_data and "action_type" not in serialized_data:
                        logger.error(f"Невозможно создать новую задачу {task_id}: недостаточно данных")
                        return
                    
                    # Создаем новую задачу
                    new_task = {
                        "id": task_id,
                        "created_at": datetime.now().isoformat(),
                        "enabled": True
                    }
                    
                    # Добавляем все поля из переданной конфигурации
                    new_task.update(serialized_data)
                    
                    await self._save_task_to_db(task_id, new_task)
                    return
                    
            except Exception as e:
                retry_count += 1
                logger.error(f"Ошибка при обновлении задачи {task_id} в базе данных (попытка {retry_count}/{max_retries}): {str(e)}")
                
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    logger.info(f"Повторная попытка обновления задачи {task_id} через {wait_time} секунд...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Не удалось обновить задачу {task_id} после {max_retries} попыток")
                    
                    error_info = {
                        "timestamp": datetime.now().isoformat(),
                        "task_id": task_id,
                        "operation": "update",
                        "error": str(e),
                        "data": json.dumps(task_config, default=self._serialize_datetime)
                    }
                    
                    try:
                        await self.db["scheduler_errors"].insert_one(error_info)
                    except Exception as e2:
                        logger.error(f"Не удалось сохранить информацию об ошибке: {str(e2)}")
    
    async def _remove_task_from_db(self, task_id: str):
        """
        Удаляет задачу из базы данных
        
        Args:
            task_id: ID задачи
        """
        try:
            # Используем прямое подключение к MongoDB
            collection = self.db[self.collection_name]
            
            # Удаляем задачу из базы данных
            result = await collection.delete_one({"id": task_id})
            
            if result.deleted_count > 0:
                logger.info(f"Задача {task_id} удалена из базы данных")
            else:
                logger.warning(f"Задача {task_id} не найдена в базе данных")
        except Exception as e:
            logger.error(f"Ошибка при удалении задачи из базы данных: {e}")
    
    async def send_test_notification(self, user_id: int, notification_type: str) -> bool:
        """
        Отправляет тестовое уведомление указанного типа
        
        Args:
            user_id: ID пользователя
            notification_type: Тип уведомления (morning, evening, weekly)
            
        Returns:
            bool: True если уведомление отправлено успешно, иначе False
        """
        try:
            # Получаем профиль пользователя
            profile = await self.user_profile_manager.get_profile(user_id)
            chat_id = profile.get("chat_id", user_id)
            
            # Определяем агента и текст в зависимости от типа уведомления
            if notification_type == "morning":
                agent_id = "lifehacker"
                message_text = "Доброе утро! Вот полезный совет по нейросетям на сегодня:"
            elif notification_type == "evening":
                agent_id = "coach"
                message_text = "Добрый вечер! Давайте проанализируем ваш прогресс за сегодня и подумаем, что можно улучшить:"
            elif notification_type == "weekly":
                agent_id = "digest"
                message_text = "Вот самые интересные новости о нейросетях за прошедшую неделю:"
            else:
                logger.error(f"Неизвестный тип уведомления: {notification_type}")
                return False
            
            # Создаем и выполняем задачу для запуска агента
            task_config = {
                "user_id": user_id,
                "trigger_type": "once",
                "trigger_config": {
                    "datetime": datetime.now().isoformat(),
                    "margin_seconds": 300
                },
                "action_type": "run_agent",
                "action_config": {
                    "agent_id": agent_id,
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "notification_type": notification_type,
                    "message_text": message_text
                },
                "enabled": True
            }
            
            # Выполняем действие
            await self._execute_action(task_config)
            
            logger.info(f"Отправлено тестовое уведомление типа {notification_type} пользователю {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при отправке тестового уведомления: {e}")
            return False

    # Методы для миграции старых уведомлений
    async def migrate_old_notifications(self):
        """Мигрирует старые уведомления в новый формат задач"""
        try:
            # Получаем всех пользователей с включенными уведомлениями
            users = await self._get_users_with_notifications()
            
            for user in users:
                user_id = user.get("user_id")
                
                # Создаем задачи для утренних уведомлений
                if user.get("notifications_enabled") and user.get("notification_frequency") in ["daily", "all"]:
                    daily_time = user.get("daily_notification_time", "09:00")
                    
                    morning_task = {
                        "name": f"Утреннее уведомление для пользователя {user_id}",
                        "user_id": user_id,
                        "trigger_type": "daily",
                        "trigger_config": {
                            "time": daily_time,
                            "margin_minutes": 5
                        },
                        "action_type": "run_agent",
                        "action_config": {
                            "agent_id": "lifehacker",
                            "user_id": user_id,
                            "notification_type": "morning",
                            "message_text": "Доброе утро! Вот полезный совет по нейросетям на сегодня:"
                        },
                        "enabled": True
                    }
                    
                    await self.add_task(morning_task)
                    
                    # Создаем задачи для вечерних уведомлений
                    evening_time = user.get("evening_notification_time", "20:00")
                    
                    evening_task = {
                        "name": f"Вечернее уведомление для пользователя {user_id}",
                        "user_id": user_id,
                        "trigger_type": "daily",
                        "trigger_config": {
                            "time": evening_time,
                            "margin_minutes": 5
                        },
                        "action_type": "run_agent",
                        "action_config": {
                            "agent_id": "coach",
                            "user_id": user_id,
                            "notification_type": "evening",
                            "message_text": "Добрый вечер! Давайте проанализируем ваш прогресс за сегодня и подумаем, что можно улучшить:"
                        },
                        "enabled": True
                    }
                    
                    await self.add_task(evening_task)
                
                # Создаем задачи для еженедельных уведомлений
                if user.get("notifications_enabled") and user.get("notification_frequency") in ["weekly", "all"]:
                    weekly_day = user.get("weekly_notification_day", "monday").lower()
                    weekly_time = user.get("weekly_notification_time", "10:00")
                    
                    weekly_task = {
                        "name": f"Еженедельное уведомление для пользователя {user_id}",
                        "user_id": user_id,
                        "trigger_type": "weekly",
                        "trigger_config": {
                            "day": weekly_day,
                            "time": weekly_time,
                            "margin_minutes": 5
                        },
                        "action_type": "run_agent",
                        "action_config": {
                            "agent_id": "digest",
                            "user_id": user_id,
                            "notification_type": "weekly",
                            "message_text": "Вот самые интересные новости о нейросетях за прошедшую неделю:"
                        },
                        "enabled": True
                    }
                    
                    await self.add_task(weekly_task)
            
            logger.info(f"Миграция уведомлений завершена для {len(users)} пользователей")
            return True
        except Exception as e:
            logger.error(f"Ошибка при миграции уведомлений: {e}")
            return False

    async def fix_now_datetime_in_tasks(self):
        """
        Обновляет все задачи в базе данных, заменяя значение 'now' в триггере типа 'once' 
        на текущее время в формате ISO с timezone
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Используем прямое подключение к MongoDB
                collection = self.db[self.collection_name]
                
                # Получаем все задачи с триггером типа 'once' и значением datetime = 'now'
                cursor = collection.find({
                    "trigger_type": "once",
                    "trigger_config.datetime": "now"
                })
                
                tasks = await cursor.to_list(length=100)
                
                if not tasks:
                    logger.info("Задачи с datetime = 'now' не найдены")
                    return
                
                logger.info(f"Найдено {len(tasks)} задач с datetime = 'now', начинаем обновление...")
                
                # Получаем текущее время в формате ISO с timezone
                current_time = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
                
                # Счетчики для статистики
                updated_count = 0
                error_count = 0
                
                for task in tasks:
                    task_id = task.get("id")
                    task_name = task.get("name", "Без имени")
                    
                    if not task_id:
                        logger.warning(f"Пропускаем задачу без ID: {task_name}")
                        continue
                    
                    try:
                        # Проверяем корректность структуры задачи
                        if "trigger_config" not in task:
                            logger.warning(f"Задача {task_id} не содержит trigger_config, пропускаем")
                            continue
                        
                        # Обновляем значение datetime на текущее время
                        update_result = await collection.update_one(
                            {"id": task_id},
                            {"$set": {"trigger_config.datetime": current_time}}
                        )
                        
                        if update_result.modified_count > 0:
                            logger.info(f"Задача {task_id} ({task_name}): значение 'now' заменено на {current_time}")
                            
                            # Обновляем также в локальном кэше задач, если задача там есть
                            if task_id in self.scheduled_tasks:
                                if "trigger_config" in self.scheduled_tasks[task_id]:
                                    self.scheduled_tasks[task_id]["trigger_config"]["datetime"] = current_time
                                    logger.info(f"Задача {task_id} также обновлена в локальном кэше")
                            
                            updated_count += 1
                        else:
                            logger.warning(f"Задача {task_id} не обновлена. Возможно, была изменена в другом процессе.")
                    
                    except Exception as task_error:
                        error_count += 1
                        logger.error(f"Ошибка при обновлении задачи {task_id}: {str(task_error)}")
                
                # Итоговая статистика
                logger.info(f"Обновление завершено: успешно - {updated_count}, с ошибками - {error_count}")
                
                # Если обновлены все задачи, выходим из цикла
                return
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Ошибка при обновлении задач (попытка {retry_count}/{max_retries}): {str(e)}")
                
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    logger.info(f"Повторная попытка обновления через {wait_time} секунд...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Не удалось обновить задачи после {max_retries} попыток") 