"""
Simple AmoCRM Tasks Plugin - Модуль для работы с задачами и событиями

Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
- Только операции с задачами и событиями AmoCRM
- Наследует настройки от базового плагина
- Минимум кода и зависимостей
"""

from typing import Dict, Any
from loguru import logger

from app.core.base_plugin import BasePlugin


class SimpleAmoCRMTasksPlugin(BasePlugin):
    """Простой плагин для работы с задачами и событиями AmoCRM"""
    
    def __init__(self):
        super().__init__("simple_amocrm_tasks")
        
        # Ссылка на базовый плагин для использования его методов
        self.base_plugin = None
        
        logger.info("SimpleAmoCRMTasksPlugin инициализирован")
    
    async def _do_initialize(self):
        """Инициализация плагина"""
        # Получаем ссылку на базовый AmoCRM плагин
        if self.engine and hasattr(self.engine, 'plugins'):
            self.base_plugin = self.engine.plugins.get('simple_amocrm')
            
        if self.base_plugin:
            logger.info("✅ SimpleAmoCRMTasksPlugin готов к работе")
        else:
            logger.warning("⚠️ Базовый AmoCRM плагин не найден")
    
    def register_handlers(self) -> Dict[str, Any]:
        """Регистрация обработчиков для работы с задачами"""
        return {
            # === ЗАДАЧИ ===
            "amocrm_create_task": self._handle_create_task,
            "amocrm_update_task": self._handle_update_task,
            "amocrm_complete_task": self._handle_complete_task,
            "amocrm_get_task": self._handle_get_task,
            "amocrm_list_tasks": self._handle_list_tasks,
            "amocrm_delete_task": self._handle_delete_task,
            
            # === СОБЫТИЯ ===
            "amocrm_create_event": self._handle_create_event,
            "amocrm_list_events": self._handle_list_events,
        }
    

    async def _ensure_fresh_settings(self):
        """Динамически загружает актуальные настройки из БД"""
        try:
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                return
                
            mongo_plugin = self.engine.plugins['mongo']
            settings_result = await mongo_plugin._find_one("plugin_settings", {"plugin_name": "simple_amocrm"})
            
            if settings_result and settings_result.get("success") and settings_result.get("document"):
                settings = settings_result["document"]
                new_base_url = settings.get("base_url")
                new_access_token = settings.get("access_token")
                
                # Обновляем настройки если они изменились
                if new_base_url != self.base_url or new_access_token != self.access_token:
                    self.base_url = new_base_url
                    self.access_token = new_access_token
                    self.headers = {
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json'
                    } if self.access_token else {}
                    logger.info(f"✅ Настройки AmoCRM обновлены: {self.base_url}")
                    
        except Exception as e:
            logger.error(f"❌ Ошибка динамической загрузки настроек AmoCRM: {e}")

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Делегирует HTTP запросы базовому плагину"""
        if not self.base_plugin:
            return {
                "success": False,
                "error": "Базовый AmoCRM плагин недоступен"
            }
        
        return await self.base_plugin._make_request(method, endpoint, **kwargs)
    
    def _resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Делегирует разрешение переменных базовому плагину"""
        if not self.base_plugin:
            return value
        
        return self.base_plugin._resolve_value(value, context)
    
    # === ОБРАБОТЧИКИ ЗАДАЧ ===
    
    async def _handle_create_task(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание задачи в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            text = self._resolve_value(params.get("text", ""), context)
            entity_type = self._resolve_value(params.get("entity_type", ""), context)  # leads, contacts, companies
            entity_id = self._resolve_value(params.get("entity_id", ""), context)
            output_var = params.get("output_var", "created_task")
            
            if not text or not entity_type or not entity_id:
                context[output_var] = {"success": False, "error": "Не указаны обязательные параметры: text, entity_type, entity_id"}
                return
            
            # Формируем данные задачи
            task_data = {
                "text": text,
                "complete_till": self._resolve_value(params.get("complete_till", ""), context),
                "entity_type": entity_type,
                "entity_id": int(entity_id)
            }
            
            # Дополнительные параметры
            if "task_type_id" in params:
                task_data["task_type_id"] = int(self._resolve_value(params["task_type_id"], context))
            
            if "responsible_user_id" in params:
                task_data["responsible_user_id"] = int(self._resolve_value(params["responsible_user_id"], context))
            
            # Создаем задачу
            endpoint = "/api/v4/tasks"
            result = await self._make_request("POST", endpoint, json=[task_data])
            
            if result["success"]:
                tasks = result["data"].get("_embedded", {}).get("tasks", [])
                if tasks:
                    task = tasks[0]
                    context[output_var] = {
                        "success": True,
                        "task": task,
                        "task_id": task["id"]
                    }
                    logger.info(f"✅ Задача создана: {task['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Задача не создана"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка создания задачи: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания задачи: {e}")
            context["__step_error__"] = f"AmoCRM создание задачи: {str(e)}"

    async def _handle_update_task(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Обновление задачи в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            task_id = self._resolve_value(params.get("task_id", ""), context)
            output_var = params.get("output_var", "updated_task")
            
            if not task_id:
                context[output_var] = {"success": False, "error": "Не указан task_id"}
                return
            
            # Формируем данные для обновления
            task_data = {"id": int(task_id)}
            
            # Обновляемые поля
            if "text" in params:
                task_data["text"] = self._resolve_value(params["text"], context)
            
            if "complete_till" in params:
                task_data["complete_till"] = self._resolve_value(params["complete_till"], context)
            
            if "responsible_user_id" in params:
                task_data["responsible_user_id"] = int(self._resolve_value(params["responsible_user_id"], context))
            
            # Обновляем задачу
            endpoint = "/api/v4/tasks"
            result = await self._make_request("PATCH", endpoint, json=[task_data])
            
            if result["success"]:
                tasks = result["data"].get("_embedded", {}).get("tasks", [])
                if tasks:
                    task = tasks[0]
                    context[output_var] = {
                        "success": True,
                        "task": task,
                        "task_id": task["id"]
                    }
                    logger.info(f"✅ Задача обновлена: {task['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Задача не обновлена"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка обновления задачи: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления задачи: {e}")
            context["__step_error__"] = f"AmoCRM обновление задачи: {str(e)}"

    async def _handle_complete_task(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Завершение задачи в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            task_id = self._resolve_value(params.get("task_id", ""), context)
            output_var = params.get("output_var", "completed_task")
            result_text = self._resolve_value(params.get("result_text", ""), context)
            
            if not task_id:
                context[output_var] = {"success": False, "error": "Не указан task_id"}
                return
            
            # Формируем данные для завершения
            task_data = {
                "id": int(task_id),
                "is_completed": True
            }
            
            if result_text:
                task_data["result"] = {"text": result_text}
            
            # Завершаем задачу
            endpoint = "/api/v4/tasks"
            result = await self._make_request("PATCH", endpoint, json=[task_data])
            
            if result["success"]:
                tasks = result["data"].get("_embedded", {}).get("tasks", [])
                if tasks:
                    task = tasks[0]
                    context[output_var] = {
                        "success": True,
                        "task": task,
                        "task_id": task["id"],
                        "completed": True
                    }
                    logger.info(f"✅ Задача завершена: {task['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Задача не завершена"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка завершения задачи: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка завершения задачи: {e}")
            context["__step_error__"] = f"AmoCRM завершение задачи: {str(e)}"

    async def _handle_get_task(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение задачи по ID"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            task_id = self._resolve_value(params.get("task_id", ""), context)
            output_var = params.get("output_var", "task")
            
            if not task_id:
                context[output_var] = {"success": False, "error": "Не указан task_id"}
                return
            
            # Получение задачи
            endpoint = f"/api/v4/tasks/{task_id}"
            result = await self._make_request("GET", endpoint)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "task": result["data"]
                }
                logger.info(f"✅ Задача получена: {task_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения задачи: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения задачи: {e}")
            context["__step_error__"] = f"AmoCRM получение задачи: {str(e)}"

    async def _handle_list_tasks(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка задач"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "tasks")
            limit = params.get("limit", 250)
            page = params.get("page", 1)
            filter_params = params.get("filter", {})
            
            # Параметры запроса
            request_params = {
                "limit": limit,
                "page": page
            }
            
            # Добавляем фильтры
            for key, value in filter_params.items():
                resolved_value = self._resolve_value(value, context)
                request_params[key] = resolved_value
            
            # Получение списка задач
            endpoint = f"/api/v4/tasks"
            result = await self._make_request("GET", endpoint, params=request_params)
            
            if result["success"]:
                tasks = result["data"].get("_embedded", {}).get("tasks", [])
                context[output_var] = {
                    "success": True,
                    "tasks": tasks,
                    "count": len(tasks),
                    "page": page,
                    "limit": limit
                }
                logger.info(f"✅ Список задач получен: {len(tasks)} записей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка задач: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка задач: {e}")
            context["__step_error__"] = f"AmoCRM список задач: {str(e)}"

    async def _handle_delete_task(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Удаление задачи из AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            task_id = self._resolve_value(params.get("task_id", ""), context)
            output_var = params.get("output_var", "delete_result")
            
            if not task_id:
                context[output_var] = {"success": False, "error": "Не указан task_id"}
                return
            
            # Удаляем задачу
            endpoint = f"/api/v4/tasks/{task_id}"
            result = await self._make_request("DELETE", endpoint)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "deleted": True,
                    "task_id": task_id
                }
                logger.info(f"✅ Задача удалена: {task_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка удаления задачи: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка удаления задачи: {e}")
            context["__step_error__"] = f"AmoCRM удаление задачи: {str(e)}"

    # === ОБРАБОТЧИКИ СОБЫТИЙ ===

    async def _handle_create_event(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание события в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            type_event = self._resolve_value(params.get("type", ""), context)  # meeting, call, etc.
            entity_type = self._resolve_value(params.get("entity_type", ""), context)
            entity_id = self._resolve_value(params.get("entity_id", ""), context)
            output_var = params.get("output_var", "created_event")
            
            if not type_event or not entity_type or not entity_id:
                context[output_var] = {"success": False, "error": "Не указаны обязательные параметры: type, entity_type, entity_id"}
                return
            
            # Формируем данные события
            event_data = {
                "type": type_event,
                "entity_type": entity_type,
                "entity_id": int(entity_id)
            }
            
            # Дополнительные параметры
            if "value_after" in params:
                event_data["value_after"] = self._resolve_value(params["value_after"], context)
            
            if "value_before" in params:
                event_data["value_before"] = self._resolve_value(params["value_before"], context)
            
            if "created_by" in params:
                event_data["created_by"] = int(self._resolve_value(params["created_by"], context))
            
            # Создаем событие
            endpoint = "/api/v4/events"
            result = await self._make_request("POST", endpoint, json=[event_data])
            
            if result["success"]:
                events = result["data"].get("_embedded", {}).get("events", [])
                if events:
                    event = events[0]
                    context[output_var] = {
                        "success": True,
                        "event": event,
                        "event_id": event["id"]
                    }
                    logger.info(f"✅ Событие создано: {event['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Событие не создано"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка создания события: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания события: {e}")
            context["__step_error__"] = f"AmoCRM создание события: {str(e)}"

    async def _handle_list_events(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка событий"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "events")
            limit = params.get("limit", 250)
            page = params.get("page", 1)
            filter_params = params.get("filter", {})
            
            # Параметры запроса
            request_params = {
                "limit": limit,
                "page": page
            }
            
            # Добавляем фильтры
            for key, value in filter_params.items():
                resolved_value = self._resolve_value(value, context)
                request_params[key] = resolved_value
            
            # Получение списка событий
            endpoint = f"/api/v4/events"
            result = await self._make_request("GET", endpoint, params=request_params)
            
            if result["success"]:
                events = result["data"].get("_embedded", {}).get("events", [])
                context[output_var] = {
                    "success": True,
                    "events": events,
                    "count": len(events),
                    "page": page,
                    "limit": limit
                }
                logger.info(f"✅ Список событий получен: {len(events)} записей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка событий: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка событий: {e}")
            context["__step_error__"] = f"AmoCRM список событий: {str(e)}"

    async def healthcheck(self) -> bool:
        """Проверка работоспособности модуля задач"""
        try:
            if not self.base_plugin:
                logger.warning("❌ Tasks healthcheck: базовый плагин недоступен")
                return False
            
            # Проверяем базовый плагин
            base_health = await self.base_plugin.healthcheck()
            
            if base_health:
                logger.info("✅ Tasks healthcheck: OK")
                return True
            else:
                logger.error("❌ Tasks healthcheck: базовый плагин не работает")
                return False
                
        except Exception as e:
            logger.error(f"❌ Tasks healthcheck: ошибка - {e}")
            return False 