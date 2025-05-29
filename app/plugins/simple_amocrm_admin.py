"""
Simple AmoCRM Admin Plugin - Модуль для административных операций

Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
- Только административные операции AmoCRM
- Воронки, поля, пользователи, статусы
- Наследует настройки от базового плагина
- Минимум кода и зависимостей
"""

from typing import Dict, Any
from loguru import logger

from app.core.base_plugin import BasePlugin


class SimpleAmoCRMAdminPlugin(BasePlugin):
    """Простой плагин для административных операций AmoCRM"""
    
    def __init__(self):
        super().__init__("simple_amocrm_admin")
        
        # Ссылка на базовый плагин для использования его методов
        self.base_plugin = None
        
        logger.info("SimpleAmoCRMAdminPlugin инициализирован")
    
    async def _do_initialize(self):
        """Инициализация плагина"""
        # Получаем ссылку на базовый AmoCRM плагин
        if self.engine and hasattr(self.engine, 'plugins'):
            self.base_plugin = self.engine.plugins.get('simple_amocrm')
            
        if self.base_plugin:
            logger.info("✅ SimpleAmoCRMAdminPlugin готов к работе")
        else:
            logger.warning("⚠️ Базовый AmoCRM плагин не найден")
    
    def register_handlers(self) -> Dict[str, Any]:
        """Регистрация обработчиков для административных операций"""
        return {
            # === ВОРОНКИ ===
            "amocrm_list_pipelines": self._handle_list_pipelines,
            "amocrm_get_pipeline": self._handle_get_pipeline,
            "amocrm_create_pipeline": self._handle_create_pipeline,
            "amocrm_update_pipeline": self._handle_update_pipeline,
            
            # === СТАТУСЫ ===
            "amocrm_list_statuses": self._handle_list_statuses,
            "amocrm_create_status": self._handle_create_status,
            "amocrm_update_status": self._handle_update_status,
            
            # === ПОЛЬЗОВАТЕЛИ ===
            "amocrm_list_users": self._handle_list_users,
            "amocrm_get_user": self._handle_get_user,
            
            # === КАСТОМНЫЕ ПОЛЯ ===
            "amocrm_list_custom_fields": self._handle_list_custom_fields,
            "amocrm_create_custom_field": self._handle_create_custom_field,
            "amocrm_update_custom_field": self._handle_update_custom_field,
            
            # === ТЕГИ ===
            "amocrm_list_tags": self._handle_list_tags,
            "amocrm_create_tag": self._handle_create_tag,
        }
    

    async def _ensure_fresh_settings(self):
        """Динамически загружает актуальные настройки из БД"""
        try:
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                return
                
            mongo_plugin = self.engine.plugins['mongo']
            settings_result = await mongo_plugin._find_one("settings", {"plugin_name": "simple_amocrm"})
            
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
    
    # === ОБРАБОТЧИКИ ВОРОНОК ===
    
    async def _handle_list_pipelines(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка воронок"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "pipelines")
            entity_type = params.get("entity_type", "leads")  # leads, contacts, companies
            
            # Получение списка воронок
            endpoint = f"/api/v4/{entity_type}/pipelines"
            result = await self._make_request("GET", endpoint)
            
            if result["success"]:
                pipelines = result["data"].get("_embedded", {}).get("pipelines", [])
                context[output_var] = {
                    "success": True,
                    "pipelines": pipelines,
                    "count": len(pipelines),
                    "entity_type": entity_type
                }
                logger.info(f"✅ Список воронок получен: {len(pipelines)} записей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка воронок: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка воронок: {e}")
            context["__step_error__"] = f"AmoCRM список воронок: {str(e)}"

    async def _handle_get_pipeline(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение воронки по ID"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            pipeline_id = self._resolve_value(params.get("pipeline_id", ""), context)
            output_var = params.get("output_var", "pipeline")
            entity_type = params.get("entity_type", "leads")
            
            if not pipeline_id:
                context[output_var] = {"success": False, "error": "Не указан pipeline_id"}
                return
            
            # Получение воронки
            endpoint = f"/api/v4/{entity_type}/pipelines/{pipeline_id}"
            result = await self._make_request("GET", endpoint)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "pipeline": result["data"]
                }
                logger.info(f"✅ Воронка получена: {pipeline_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения воронки: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения воронки: {e}")
            context["__step_error__"] = f"AmoCRM получение воронки: {str(e)}"

    async def _handle_create_pipeline(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание воронки"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            name = self._resolve_value(params.get("name", ""), context)
            output_var = params.get("output_var", "created_pipeline")
            entity_type = params.get("entity_type", "leads")
            
            if not name:
                context[output_var] = {"success": False, "error": "Не указано название воронки"}
                return
            
            # Формируем данные воронки
            pipeline_data = {"name": name}
            
            if "sort" in params:
                pipeline_data["sort"] = int(self._resolve_value(params["sort"], context))
            
            if "is_main" in params:
                pipeline_data["is_main"] = bool(self._resolve_value(params["is_main"], context))
            
            # Создаем воронку
            endpoint = f"/api/v4/{entity_type}/pipelines"
            result = await self._make_request("POST", endpoint, json=[pipeline_data])
            
            if result["success"]:
                pipelines = result["data"].get("_embedded", {}).get("pipelines", [])
                if pipelines:
                    pipeline = pipelines[0]
                    context[output_var] = {
                        "success": True,
                        "pipeline": pipeline,
                        "pipeline_id": pipeline["id"]
                    }
                    logger.info(f"✅ Воронка создана: {pipeline['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Воронка не создана"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка создания воронки: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания воронки: {e}")
            context["__step_error__"] = f"AmoCRM создание воронки: {str(e)}"

    async def _handle_update_pipeline(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Обновление воронки"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            pipeline_id = self._resolve_value(params.get("pipeline_id", ""), context)
            output_var = params.get("output_var", "updated_pipeline")
            entity_type = params.get("entity_type", "leads")
            
            if not pipeline_id:
                context[output_var] = {"success": False, "error": "Не указан pipeline_id"}
                return
            
            # Формируем данные для обновления
            pipeline_data = {"id": int(pipeline_id)}
            
            if "name" in params:
                pipeline_data["name"] = self._resolve_value(params["name"], context)
            
            if "sort" in params:
                pipeline_data["sort"] = int(self._resolve_value(params["sort"], context))
            
            if "is_main" in params:
                pipeline_data["is_main"] = bool(self._resolve_value(params["is_main"], context))
            
            # Обновляем воронку
            endpoint = f"/api/v4/{entity_type}/pipelines"
            result = await self._make_request("PATCH", endpoint, json=[pipeline_data])
            
            if result["success"]:
                pipelines = result["data"].get("_embedded", {}).get("pipelines", [])
                if pipelines:
                    pipeline = pipelines[0]
                    context[output_var] = {
                        "success": True,
                        "pipeline": pipeline,
                        "pipeline_id": pipeline["id"]
                    }
                    logger.info(f"✅ Воронка обновлена: {pipeline['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Воронка не обновлена"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка обновления воронки: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления воронки: {e}")
            context["__step_error__"] = f"AmoCRM обновление воронки: {str(e)}"

    # === ОБРАБОТЧИКИ СТАТУСОВ ===

    async def _handle_list_statuses(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка статусов воронки"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            pipeline_id = self._resolve_value(params.get("pipeline_id", ""), context)
            output_var = params.get("output_var", "statuses")
            entity_type = params.get("entity_type", "leads")
            
            if not pipeline_id:
                context[output_var] = {"success": False, "error": "Не указан pipeline_id"}
                return
            
            # Получение списка статусов
            endpoint = f"/api/v4/{entity_type}/pipelines/{pipeline_id}/statuses"
            result = await self._make_request("GET", endpoint)
            
            if result["success"]:
                statuses = result["data"].get("_embedded", {}).get("statuses", [])
                context[output_var] = {
                    "success": True,
                    "statuses": statuses,
                    "count": len(statuses),
                    "pipeline_id": pipeline_id
                }
                logger.info(f"✅ Список статусов получен: {len(statuses)} записей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка статусов: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка статусов: {e}")
            context["__step_error__"] = f"AmoCRM список статусов: {str(e)}"

    async def _handle_create_status(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание статуса в воронке"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            pipeline_id = self._resolve_value(params.get("pipeline_id", ""), context)
            name = self._resolve_value(params.get("name", ""), context)
            output_var = params.get("output_var", "created_status")
            entity_type = params.get("entity_type", "leads")
            
            if not pipeline_id or not name:
                context[output_var] = {"success": False, "error": "Не указаны pipeline_id или name"}
                return
            
            # Формируем данные статуса
            status_data = {"name": name}
            
            if "sort" in params:
                status_data["sort"] = int(self._resolve_value(params["sort"], context))
            
            if "color" in params:
                status_data["color"] = self._resolve_value(params["color"], context)
            
            if "type" in params:
                status_data["type"] = int(self._resolve_value(params["type"], context))
            
            # Создаем статус
            endpoint = f"/api/v4/{entity_type}/pipelines/{pipeline_id}/statuses"
            result = await self._make_request("POST", endpoint, json=[status_data])
            
            if result["success"]:
                statuses = result["data"].get("_embedded", {}).get("statuses", [])
                if statuses:
                    status = statuses[0]
                    context[output_var] = {
                        "success": True,
                        "status": status,
                        "status_id": status["id"]
                    }
                    logger.info(f"✅ Статус создан: {status['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Статус не создан"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка создания статуса: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания статуса: {e}")
            context["__step_error__"] = f"AmoCRM создание статуса: {str(e)}"

    async def _handle_update_status(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Обновление статуса в воронке"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            pipeline_id = self._resolve_value(params.get("pipeline_id", ""), context)
            status_id = self._resolve_value(params.get("status_id", ""), context)
            output_var = params.get("output_var", "updated_status")
            entity_type = params.get("entity_type", "leads")
            
            if not pipeline_id or not status_id:
                context[output_var] = {"success": False, "error": "Не указаны pipeline_id или status_id"}
                return
            
            # Формируем данные для обновления
            status_data = {"id": int(status_id)}
            
            if "name" in params:
                status_data["name"] = self._resolve_value(params["name"], context)
            
            if "sort" in params:
                status_data["sort"] = int(self._resolve_value(params["sort"], context))
            
            if "color" in params:
                status_data["color"] = self._resolve_value(params["color"], context)
            
            # Обновляем статус
            endpoint = f"/api/v4/{entity_type}/pipelines/{pipeline_id}/statuses"
            result = await self._make_request("PATCH", endpoint, json=[status_data])
            
            if result["success"]:
                statuses = result["data"].get("_embedded", {}).get("statuses", [])
                if statuses:
                    status = statuses[0]
                    context[output_var] = {
                        "success": True,
                        "status": status,
                        "status_id": status["id"]
                    }
                    logger.info(f"✅ Статус обновлен: {status['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Статус не обновлен"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка обновления статуса: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления статуса: {e}")
            context["__step_error__"] = f"AmoCRM обновление статуса: {str(e)}"

    # === ОБРАБОТЧИКИ ПОЛЬЗОВАТЕЛЕЙ ===

    async def _handle_list_users(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка пользователей"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "users")
            limit = params.get("limit", 250)
            page = params.get("page", 1)
            
            # Параметры запроса
            request_params = {
                "limit": limit,
                "page": page
            }
            
            # Получение списка пользователей
            endpoint = f"/api/v4/users"
            result = await self._make_request("GET", endpoint, params=request_params)
            
            if result["success"]:
                users = result["data"].get("_embedded", {}).get("users", [])
                context[output_var] = {
                    "success": True,
                    "users": users,
                    "count": len(users),
                    "page": page,
                    "limit": limit
                }
                logger.info(f"✅ Список пользователей получен: {len(users)} записей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка пользователей: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка пользователей: {e}")
            context["__step_error__"] = f"AmoCRM список пользователей: {str(e)}"

    async def _handle_get_user(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение пользователя по ID"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            user_id = self._resolve_value(params.get("user_id", ""), context)
            output_var = params.get("output_var", "user")
            
            if not user_id:
                context[output_var] = {"success": False, "error": "Не указан user_id"}
                return
            
            # Получение пользователя
            endpoint = f"/api/v4/users/{user_id}"
            result = await self._make_request("GET", endpoint)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "user": result["data"]
                }
                logger.info(f"✅ Пользователь получен: {user_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения пользователя: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователя: {e}")
            context["__step_error__"] = f"AmoCRM получение пользователя: {str(e)}"

    # === ОБРАБОТЧИКИ КАСТОМНЫХ ПОЛЕЙ ===

    async def _handle_list_custom_fields(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка кастомных полей"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "custom_fields")
            entity_type = params.get("entity_type", "leads")  # leads, contacts, companies
            
            # Получение списка кастомных полей
            endpoint = f"/api/v4/{entity_type}/custom_fields"
            result = await self._make_request("GET", endpoint)
            
            if result["success"]:
                custom_fields = result["data"].get("_embedded", {}).get("custom_fields", [])
                context[output_var] = {
                    "success": True,
                    "custom_fields": custom_fields,
                    "count": len(custom_fields),
                    "entity_type": entity_type
                }
                logger.info(f"✅ Список кастомных полей получен: {len(custom_fields)} записей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка кастомных полей: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка кастомных полей: {e}")
            context["__step_error__"] = f"AmoCRM список кастомных полей: {str(e)}"

    async def _handle_create_custom_field(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание кастомного поля"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            name = self._resolve_value(params.get("name", ""), context)
            field_type = self._resolve_value(params.get("type", ""), context)  # text, textarea, numeric, etc.
            output_var = params.get("output_var", "created_custom_field")
            entity_type = params.get("entity_type", "leads")
            
            if not name or not field_type:
                context[output_var] = {"success": False, "error": "Не указаны name или type"}
                return
            
            # Формируем данные кастомного поля
            field_data = {
                "name": name,
                "type": field_type
            }
            
            if "sort" in params:
                field_data["sort"] = int(self._resolve_value(params["sort"], context))
            
            if "code" in params:
                field_data["code"] = self._resolve_value(params["code"], context)
            
            # Создаем кастомное поле
            endpoint = f"/api/v4/{entity_type}/custom_fields"
            result = await self._make_request("POST", endpoint, json=[field_data])
            
            if result["success"]:
                custom_fields = result["data"].get("_embedded", {}).get("custom_fields", [])
                if custom_fields:
                    custom_field = custom_fields[0]
                    context[output_var] = {
                        "success": True,
                        "custom_field": custom_field,
                        "field_id": custom_field["id"]
                    }
                    logger.info(f"✅ Кастомное поле создано: {custom_field['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Кастомное поле не создано"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка создания кастомного поля: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания кастомного поля: {e}")
            context["__step_error__"] = f"AmoCRM создание кастомного поля: {str(e)}"

    async def _handle_update_custom_field(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Обновление кастомного поля"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            field_id = self._resolve_value(params.get("field_id", ""), context)
            output_var = params.get("output_var", "updated_custom_field")
            entity_type = params.get("entity_type", "leads")
            
            if not field_id:
                context[output_var] = {"success": False, "error": "Не указан field_id"}
                return
            
            # Формируем данные для обновления
            field_data = {"id": int(field_id)}
            
            if "name" in params:
                field_data["name"] = self._resolve_value(params["name"], context)
            
            if "sort" in params:
                field_data["sort"] = int(self._resolve_value(params["sort"], context))
            
            # Обновляем кастомное поле
            endpoint = f"/api/v4/{entity_type}/custom_fields"
            result = await self._make_request("PATCH", endpoint, json=[field_data])
            
            if result["success"]:
                custom_fields = result["data"].get("_embedded", {}).get("custom_fields", [])
                if custom_fields:
                    custom_field = custom_fields[0]
                    context[output_var] = {
                        "success": True,
                        "custom_field": custom_field,
                        "field_id": custom_field["id"]
                    }
                    logger.info(f"✅ Кастомное поле обновлено: {custom_field['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Кастомное поле не обновлено"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка обновления кастомного поля: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления кастомного поля: {e}")
            context["__step_error__"] = f"AmoCRM обновление кастомного поля: {str(e)}"

    # === ОБРАБОТЧИКИ ТЕГОВ ===

    async def _handle_list_tags(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка тегов"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "tags")
            entity_type = params.get("entity_type", "leads")
            
            # Получение списка тегов
            endpoint = f"/api/v4/{entity_type}/tags"
            result = await self._make_request("GET", endpoint)
            
            if result["success"]:
                tags = result["data"].get("_embedded", {}).get("tags", [])
                context[output_var] = {
                    "success": True,
                    "tags": tags,
                    "count": len(tags),
                    "entity_type": entity_type
                }
                logger.info(f"✅ Список тегов получен: {len(tags)} записей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка тегов: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка тегов: {e}")
            context["__step_error__"] = f"AmoCRM список тегов: {str(e)}"

    async def _handle_create_tag(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание тега"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            name = self._resolve_value(params.get("name", ""), context)
            output_var = params.get("output_var", "created_tag")
            entity_type = params.get("entity_type", "leads")
            
            if not name:
                context[output_var] = {"success": False, "error": "Не указано название тега"}
                return
            
            # Формируем данные тега
            tag_data = {"name": name}
            
            if "color" in params:
                tag_data["color"] = self._resolve_value(params["color"], context)
            
            # Создаем тег
            endpoint = f"/api/v4/{entity_type}/tags"
            result = await self._make_request("POST", endpoint, json=[tag_data])
            
            if result["success"]:
                tags = result["data"].get("_embedded", {}).get("tags", [])
                if tags:
                    tag = tags[0]
                    context[output_var] = {
                        "success": True,
                        "tag": tag,
                        "tag_id": tag["id"]
                    }
                    logger.info(f"✅ Тег создан: {tag['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Тег не создан"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка создания тега: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания тега: {e}")
            context["__step_error__"] = f"AmoCRM создание тега: {str(e)}"

    async def healthcheck(self) -> bool:
        """Проверка работоспособности административного модуля"""
        try:
            if not self.base_plugin:
                logger.warning("❌ Admin healthcheck: базовый плагин недоступен")
                return False
            
            # Проверяем базовый плагин
            base_health = await self.base_plugin.healthcheck()
            
            if base_health:
                logger.info("✅ Admin healthcheck: OK")
                return True
            else:
                logger.error("❌ Admin healthcheck: базовый плагин не работает")
                return False
                
        except Exception as e:
            logger.error(f"❌ Admin healthcheck: ошибка - {e}")
            return False 