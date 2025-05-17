import os
import json
import uuid
from typing import Dict, Any, List, Optional, Union
from loguru import logger
from datetime import datetime, time, timedelta
import asyncio
import requests
import pytz
from app.utils.dialog_state import DialogStateManager
from app.utils.user_profile import UserProfileManager
from motor.motor_asyncio import AsyncIOMotorClient

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/scheduler.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

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
    
    def __init__(self, api_base_url: str = None, mongo_uri: str = None):
        """
        Инициализация сервиса планировщика
        
        Args:
            api_base_url: Базовый URL API для работы с коллекциями и агентами
            mongo_uri: URI для подключения к MongoDB
        """
        self.api_base_url = api_base_url or "http://app:8000"
        self.mongo_uri = mongo_uri or "mongodb://mongo:27017"
        self.mongo_client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.mongo_client.agent_platform
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
        """Основной цикл планировщика для проверки и выполнения задач"""
        while self.scheduler_running:
            try:
                # Получаем текущее время
                now = datetime.now()
                
                # Проверяем все задачи
                for task_id, task in list(self.scheduled_tasks.items()):
                    # Пропускаем отключенные задачи
                    if not task.get("enabled", True):
                        continue
                    
                    # Проверяем, должна ли задача выполниться сейчас
                    if await self._should_trigger(task, now):
                        # Проверяем, не выполнялась ли задача недавно
                        if not self._was_recently_executed(task_id, task, now):
                            # Выполняем действие
                            await self._execute_action(task)
                            # Отмечаем выполнение
                            self._mark_executed(task_id, now)
                
                # Ждем перед следующей проверкой (60 секунд)
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Ошибка в цикле планировщика: {e}")
                await asyncio.sleep(60)  # Ждем 1 минуту перед повторной попыткой
    
    async def _should_trigger(self, task: Dict[str, Any], now: datetime) -> bool:
        """
        Проверяет, должен ли сработать триггер для задачи
        
        Args:
            task: Конфигурация задачи
            now: Текущее время
            
        Returns:
            bool: True если триггер должен сработать, иначе False
        """
        trigger_type = task.get("trigger_type")
        config = task.get("trigger_config", {})
        
        if trigger_type == "daily":
            # Ежедневный триггер
            time_str = config.get("time", "09:00")
            target_time = self._parse_time(time_str)
            margin_minutes = config.get("margin_minutes", 5)
            
            return self._is_time_match(now.time(), target_time, margin_minutes)
            
        elif trigger_type == "weekly":
            # Еженедельный триггер
            day = config.get("day", "monday").lower()
            time_str = config.get("time", "10:00")
            target_time = self._parse_time(time_str)
            margin_minutes = config.get("margin_minutes", 5)
            
            current_day = now.strftime("%A").lower()
            return current_day == day and self._is_time_match(now.time(), target_time, margin_minutes)
            
        elif trigger_type == "monthly":
            # Ежемесячный триггер
            day = config.get("day", 1)
            time_str = config.get("time", "10:00")
            target_time = self._parse_time(time_str)
            margin_minutes = config.get("margin_minutes", 5)
            
            return now.day == day and self._is_time_match(now.time(), target_time, margin_minutes)
            
        elif trigger_type == "once":
            # Одноразовый триггер
            datetime_str = config.get("datetime")
            if not datetime_str:
                return False
                
            try:
                # Обработка специального значения "now"
                if datetime_str == "now":
                    # Если значение "now", задача должна выполниться немедленно
                    # Заменим значение на текущее время в базе данных
                    task_id = task.get("id")
                    if task_id:
                        asyncio.create_task(self._update_task_in_db(task_id, {
                            "trigger_config": {
                                "datetime": now.isoformat(),
                                "margin_seconds": config.get("margin_seconds", 300)
                            }
                        }))
                    return True
                
                target_datetime = datetime.fromisoformat(datetime_str)
                diff_seconds = (now - target_datetime).total_seconds()
                margin_seconds = config.get("margin_seconds", 300)  # 5 минут по умолчанию
                
                # Триггер срабатывает, если текущее время находится в пределах допустимой погрешности
                # от целевого времени (и не слишком далеко в прошлом)
                return 0 <= diff_seconds <= margin_seconds
            except Exception as e:
                logger.error(f"Ошибка при обработке триггера once: {e}")
                return False
            
        elif trigger_type == "interval":
            # Триггер с интервалом
            interval_minutes = config.get("interval_minutes", 60)  # 60 минут по умолчанию
            start_time = config.get("start_time")
            
            # Если указано время начала, проверяем, прошло ли оно
            if start_time:
                try:
                    start_datetime = datetime.fromisoformat(start_time)
                    if now < start_datetime:
                        return False
                except Exception as e:
                    logger.error(f"Ошибка при обработке start_time: {e}")
            
            # Проверяем, прошло ли достаточно времени с последнего выполнения
            last_execution = self._get_last_execution_time(task.get("id"))
            if last_execution:
                elapsed_minutes = (now - last_execution).total_seconds() / 60
                return elapsed_minutes >= interval_minutes
            
            # Если задача еще не выполнялась, выполняем ее сейчас
            return True
            
        # Неизвестный тип триггера
        logger.warning(f"Неизвестный тип триггера: {trigger_type}")
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
        Проверяет, выполнялась ли задача недавно
        
        Args:
            task_id: ID задачи
            task: Конфигурация задачи
            now: Текущее время
            
        Returns:
            bool: True если задача недавно выполнялась, иначе False
        """
        trigger_type = task.get("trigger_type")
        
        # Получаем время последнего выполнения
        last_execution = self._get_last_execution_time(task_id)
        if not last_execution:
            return False
        
        # Проверка в зависимости от типа триггера
        if trigger_type == "daily":
            # Проверяем, выполнялась ли задача сегодня
            return last_execution.date() == now.date()
            
        elif trigger_type == "weekly":
            # Проверяем, выполнялась ли задача на этой неделе
            # (считаем неделю с понедельника)
            start_of_week = now.date() - timedelta(days=now.weekday())
            return last_execution.date() >= start_of_week
            
        elif trigger_type == "monthly":
            # Проверяем, выполнялась ли задача в этом месяце
            return last_execution.year == now.year and last_execution.month == now.month
            
        elif trigger_type == "once":
            # Для одноразового триггера: если выполнялась хоть раз, больше не выполняем
            return True
            
        elif trigger_type == "interval":
            # Для интервального триггера проверка выполняется в _should_trigger
            return False
        
        return False
    
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
            execution_time: Время выполнения
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
        Запускает агента с указанными параметрами
        
        Args:
            config: Конфигурация для запуска агента
        """
        try:
            agent_id = config.get("agent_id")
            user_id = config.get("user_id")
            chat_id = config.get("chat_id")
            
            if not agent_id or not user_id:
                logger.error("Не указаны обязательные параметры agent_id или user_id")
                return
            
            # Если chat_id не указан, пытаемся получить его из профиля пользователя
            if not chat_id:
                profile = await self.user_profile_manager.get_profile(user_id)
                chat_id = profile.get("chat_id", user_id)
            
            # Отправляем сообщение через Telegram
            message_text = config.get("message_text", f"Уведомление от агента {agent_id}")
            notification_type = config.get("notification_type", "general")
            
            # Вызываем API для запуска агента
            response = requests.post(
                f"{self.api_base_url}/agent-actions/{agent_id}/execute",
                json={
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "notification_type": notification_type,
                    "message": message_text
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Агент {agent_id} успешно запущен для пользователя {user_id}")
            else:
                logger.error(f"Ошибка при запуске агента: {response.status_code}")
                
                # Если не удалось запустить агента, отправляем хотя бы сообщение
                telegram_response = requests.post(
                    f"{self.api_base_url}/integration/telegram/send",
                    json={
                        "chat_id": chat_id,
                        "text": message_text
                    }
                )
                
                if telegram_response.status_code == 200:
                    logger.info(f"Отправлено сообщение пользователю {user_id} через Telegram")
                else:
                    logger.error(f"Ошибка при отправке сообщения через Telegram: {telegram_response.status_code}")
                    
        except Exception as e:
            logger.error(f"Ошибка при запуске агента: {e}")
    
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
        """
        # Генерация ID, если не указан
        task_id = task_config.get("id", str(uuid.uuid4()))
        
        # Добавляем время создания, если не указано
        if "created_at" not in task_config:
            task_config["created_at"] = datetime.now().isoformat()
        
        # Устанавливаем enabled в True, если не указано
        if "enabled" not in task_config:
            task_config["enabled"] = True
        
        # Валидация обязательных полей
        required_fields = ["user_id", "trigger_type", "trigger_config", "action_type", "action_config"]
        for field in required_fields:
            if field not in task_config:
                raise ValueError(f"Отсутствует обязательное поле: {field}")
        
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
        """Загружает задачи из базы данных"""
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
                    self.scheduled_tasks[task_id] = task
            
            logger.info(f"Загружено {len(self.scheduled_tasks)} задач из базы данных")
        except Exception as e:
            logger.error(f"Ошибка при загрузке задач из базы данных: {e}")
    
    async def _save_task_to_db(self, task_id: str, task_config: Dict[str, Any]):
        """
        Сохраняет задачу в базу данных
        
        Args:
            task_id: ID задачи
            task_config: Конфигурация задачи
        """
        try:
            # Используем прямое подключение к MongoDB
            collection = self.db[self.collection_name]
            
            # Создаем копию конфигурации, чтобы не изменять оригинал
            task_data = task_config.copy()
            
            # Добавляем ID задачи в данные
            task_data["id"] = task_id
            
            # Сохраняем задачу в базу данных
            result = await collection.insert_one(task_data)
            
            if result.inserted_id:
                logger.info(f"Задача {task_id} сохранена в базе данных")
            else:
                logger.error("Ошибка при сохранении задачи в базе данных")
        except Exception as e:
            logger.error(f"Ошибка при сохранении задачи в базе данных: {e}")
    
    async def _update_task_in_db(self, task_id: str, task_config: Dict[str, Any]):
        """
        Обновляет задачу в базе данных
        
        Args:
            task_id: ID задачи
            task_config: Новая конфигурация задачи
        """
        try:
            # Используем прямое подключение к MongoDB
            collection = self.db[self.collection_name]
            
            # Ищем задачу по ID
            existing_task = await collection.find_one({"id": task_id})
            
            if existing_task:
                # Обновляем задачу в базе данных
                result = await collection.update_one(
                    {"id": task_id},
                    {"$set": task_config}
                )
                
                if result.modified_count > 0:
                    logger.info(f"Задача {task_id} обновлена в базе данных")
                else:
                    logger.warning(f"Задача {task_id} не изменилась в базе данных")
            else:
                # Если задача не найдена, создаем ее
                await self._save_task_to_db(task_id, task_config)
        except Exception as e:
            logger.error(f"Ошибка при обновлении задачи в базе данных: {e}")
    
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
        на текущее время в формате ISO.
        """
        try:
            # Используем прямое подключение к MongoDB
            collection = self.db[self.collection_name]
            
            # Получаем все задачи с триггером типа 'once' и значением datetime = 'now'
            cursor = collection.find({
                "trigger_type": "once",
                "trigger_config.datetime": "now"
            })
            
            tasks = await cursor.to_list(length=100)
            current_time = datetime.now().isoformat()
            
            for task in tasks:
                task_id = task.get("id")
                if task_id:
                    # Обновляем значение datetime на текущее время
                    await collection.update_one(
                        {"id": task_id},
                        {"$set": {"trigger_config.datetime": current_time}}
                    )
                    logger.info(f"Задача {task_id}: значение 'now' заменено на {current_time}")
            
            logger.info(f"Обновлено {len(tasks)} задач с значением 'now'")
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении задач с значением 'now': {e}") 