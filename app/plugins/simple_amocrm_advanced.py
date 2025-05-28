"""
Simple AmoCRM Advanced Plugin - Модуль для продвинутых операций

Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
- Только продвинутые операции AmoCRM
- Вебхуки, виджеты, звонки, каталоги
- Наследует настройки от базового плагина
- Минимум кода и зависимостей
"""

from typing import Dict, Any
from loguru import logger

from app.core.base_plugin import BasePlugin


class SimpleAmoCRMAdvancedPlugin(BasePlugin):
    """Простой плагин для продвинутых операций AmoCRM"""
    
    def __init__(self):
        super().__init__("simple_amocrm_advanced")
        
        # Ссылка на базовый плагин для использования его методов
        self.base_plugin = None
        
        logger.info("SimpleAmoCRMAdvancedPlugin инициализирован")
    
    async def _do_initialize(self):
        """Инициализация плагина"""
        # Получаем ссылку на базовый AmoCRM плагин
        if self.engine and hasattr(self.engine, 'plugins'):
            self.base_plugin = self.engine.plugins.get('simple_amocrm')
            
        if self.base_plugin:
            logger.info("✅ SimpleAmoCRMAdvancedPlugin готов к работе")
        else:
            logger.warning("⚠️ Базовый AmoCRM плагин не найден")
    
    def register_handlers(self) -> Dict[str, Any]:
        """Регистрация обработчиков для продвинутых операций"""
        return {
            # === ВЕБХУКИ ===
            "amocrm_list_webhooks": self._handle_list_webhooks,
            "amocrm_create_webhook": self._handle_create_webhook,
            "amocrm_update_webhook": self._handle_update_webhook,
            "amocrm_delete_webhook": self._handle_delete_webhook,
            
            # === ВИДЖЕТЫ ===
            "amocrm_list_widgets": self._handle_list_widgets,
            "amocrm_install_widget": self._handle_install_widget,
            "amocrm_uninstall_widget": self._handle_uninstall_widget,
            
            # === ЗВОНКИ ===
            "amocrm_create_call": self._handle_create_call,
            "amocrm_list_calls": self._handle_list_calls,
            
            # === КАТАЛОГИ ===
            "amocrm_list_catalogs": self._handle_list_catalogs,
            "amocrm_create_catalog": self._handle_create_catalog,
            "amocrm_list_catalog_elements": self._handle_list_catalog_elements,
            "amocrm_create_catalog_element": self._handle_create_catalog_element,
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
    
    # === ОБРАБОТЧИКИ ВЕБХУКОВ ===
    
    async def _handle_list_webhooks(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка вебхуков"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "webhooks")
            
            # Получение списка вебхуков
            endpoint = "/api/v4/webhooks"
            result = await self._make_request("GET", endpoint)
            
            if result["success"]:
                webhooks = result["data"].get("_embedded", {}).get("webhooks", [])
                context[output_var] = {
                    "success": True,
                    "webhooks": webhooks,
                    "count": len(webhooks)
                }
                logger.info(f"✅ Список вебхуков получен: {len(webhooks)} записей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка вебхуков: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка вебхуков: {e}")
            context["__step_error__"] = f"AmoCRM список вебхуков: {str(e)}"

    async def _handle_create_webhook(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание вебхука"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            destination = self._resolve_value(params.get("destination", ""), context)
            events = self._resolve_value(params.get("events", []), context)
            output_var = params.get("output_var", "created_webhook")
            
            if not destination or not events:
                context[output_var] = {"success": False, "error": "Не указаны destination или events"}
                return
            
            # Формируем данные вебхука
            webhook_data = {
                "destination": destination,
                "events": events
            }
            
            if "settings" in params:
                webhook_data["settings"] = self._resolve_value(params["settings"], context)
            
            # Создаем вебхук
            endpoint = "/api/v4/webhooks"
            result = await self._make_request("POST", endpoint, json=[webhook_data])
            
            if result["success"]:
                webhooks = result["data"].get("_embedded", {}).get("webhooks", [])
                if webhooks:
                    webhook = webhooks[0]
                    context[output_var] = {
                        "success": True,
                        "webhook": webhook,
                        "webhook_id": webhook["id"]
                    }
                    logger.info(f"✅ Вебхук создан: {webhook['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Вебхук не создан"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка создания вебхука: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания вебхука: {e}")
            context["__step_error__"] = f"AmoCRM создание вебхука: {str(e)}"

    async def _handle_update_webhook(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Обновление вебхука"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            webhook_id = self._resolve_value(params.get("webhook_id", ""), context)
            output_var = params.get("output_var", "updated_webhook")
            
            if not webhook_id:
                context[output_var] = {"success": False, "error": "Не указан webhook_id"}
                return
            
            # Формируем данные для обновления
            webhook_data = {"id": webhook_id}
            
            if "destination" in params:
                webhook_data["destination"] = self._resolve_value(params["destination"], context)
            
            if "events" in params:
                webhook_data["events"] = self._resolve_value(params["events"], context)
            
            if "settings" in params:
                webhook_data["settings"] = self._resolve_value(params["settings"], context)
            
            # Обновляем вебхук
            endpoint = "/api/v4/webhooks"
            result = await self._make_request("PATCH", endpoint, json=[webhook_data])
            
            if result["success"]:
                webhooks = result["data"].get("_embedded", {}).get("webhooks", [])
                if webhooks:
                    webhook = webhooks[0]
                    context[output_var] = {
                        "success": True,
                        "webhook": webhook,
                        "webhook_id": webhook["id"]
                    }
                    logger.info(f"✅ Вебхук обновлен: {webhook['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Вебхук не обновлен"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка обновления вебхука: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления вебхука: {e}")
            context["__step_error__"] = f"AmoCRM обновление вебхука: {str(e)}"

    async def _handle_delete_webhook(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Удаление вебхука"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            webhook_id = self._resolve_value(params.get("webhook_id", ""), context)
            output_var = params.get("output_var", "delete_result")
            
            if not webhook_id:
                context[output_var] = {"success": False, "error": "Не указан webhook_id"}
                return
            
            # Удаляем вебхук
            endpoint = f"/api/v4/webhooks/{webhook_id}"
            result = await self._make_request("DELETE", endpoint)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "deleted": True,
                    "webhook_id": webhook_id
                }
                logger.info(f"✅ Вебхук удален: {webhook_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка удаления вебхука: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка удаления вебхука: {e}")
            context["__step_error__"] = f"AmoCRM удаление вебхука: {str(e)}"

    # === ОБРАБОТЧИКИ ВИДЖЕТОВ ===

    async def _handle_list_widgets(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка виджетов"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "widgets")
            
            # Получение списка виджетов
            endpoint = "/api/v4/widgets"
            result = await self._make_request("GET", endpoint)
            
            if result["success"]:
                widgets = result["data"].get("_embedded", {}).get("widgets", [])
                context[output_var] = {
                    "success": True,
                    "widgets": widgets,
                    "count": len(widgets)
                }
                logger.info(f"✅ Список виджетов получен: {len(widgets)} записей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка виджетов: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка виджетов: {e}")
            context["__step_error__"] = f"AmoCRM список виджетов: {str(e)}"

    async def _handle_install_widget(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Установка виджета"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            code = self._resolve_value(params.get("code", ""), context)
            output_var = params.get("output_var", "installed_widget")
            
            if not code:
                context[output_var] = {"success": False, "error": "Не указан код виджета"}
                return
            
            # Формируем данные виджета
            widget_data = {"code": code}
            
            if "settings" in params:
                widget_data["settings"] = self._resolve_value(params["settings"], context)
            
            # Устанавливаем виджет
            endpoint = "/api/v4/widgets"
            result = await self._make_request("POST", endpoint, json=[widget_data])
            
            if result["success"]:
                widgets = result["data"].get("_embedded", {}).get("widgets", [])
                if widgets:
                    widget = widgets[0]
                    context[output_var] = {
                        "success": True,
                        "widget": widget,
                        "widget_id": widget["id"]
                    }
                    logger.info(f"✅ Виджет установлен: {widget['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Виджет не установлен"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка установки виджета: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка установки виджета: {e}")
            context["__step_error__"] = f"AmoCRM установка виджета: {str(e)}"

    async def _handle_uninstall_widget(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Удаление виджета"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            widget_code = self._resolve_value(params.get("widget_code", ""), context)
            output_var = params.get("output_var", "uninstall_result")
            
            if not widget_code:
                context[output_var] = {"success": False, "error": "Не указан код виджета"}
                return
            
            # Удаляем виджет
            endpoint = f"/api/v4/widgets/{widget_code}"
            result = await self._make_request("DELETE", endpoint)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "uninstalled": True,
                    "widget_code": widget_code
                }
                logger.info(f"✅ Виджет удален: {widget_code}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка удаления виджета: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка удаления виджета: {e}")
            context["__step_error__"] = f"AmoCRM удаление виджета: {str(e)}"

    # === ОБРАБОТЧИКИ ЗВОНКОВ ===

    async def _handle_create_call(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание звонка"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            phone = self._resolve_value(params.get("phone", ""), context)
            direction = self._resolve_value(params.get("direction", "outbound"), context)  # inbound, outbound
            output_var = params.get("output_var", "created_call")
            
            if not phone:
                context[output_var] = {"success": False, "error": "Не указан номер телефона"}
                return
            
            # Формируем данные звонка
            call_data = {
                "phone": phone,
                "direction": direction
            }
            
            if "duration" in params:
                call_data["duration"] = int(self._resolve_value(params["duration"], context))
            
            if "call_status" in params:
                call_data["call_status"] = int(self._resolve_value(params["call_status"], context))
            
            if "responsible_user_id" in params:
                call_data["responsible_user_id"] = int(self._resolve_value(params["responsible_user_id"], context))
            
            if "entity_id" in params:
                call_data["entity_id"] = int(self._resolve_value(params["entity_id"], context))
            
            if "entity_type" in params:
                call_data["entity_type"] = self._resolve_value(params["entity_type"], context)
            
            # Создаем звонок
            endpoint = "/api/v4/calls"
            result = await self._make_request("POST", endpoint, json=[call_data])
            
            if result["success"]:
                calls = result["data"].get("_embedded", {}).get("calls", [])
                if calls:
                    call = calls[0]
                    context[output_var] = {
                        "success": True,
                        "call": call,
                        "call_id": call["id"]
                    }
                    logger.info(f"✅ Звонок создан: {call['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Звонок не создан"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка создания звонка: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания звонка: {e}")
            context["__step_error__"] = f"AmoCRM создание звонка: {str(e)}"

    async def _handle_list_calls(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка звонков"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "calls")
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
            
            # Получение списка звонков
            endpoint = f"/api/v4/calls"
            result = await self._make_request("GET", endpoint, params=request_params)
            
            if result["success"]:
                calls = result["data"].get("_embedded", {}).get("calls", [])
                context[output_var] = {
                    "success": True,
                    "calls": calls,
                    "count": len(calls),
                    "page": page,
                    "limit": limit
                }
                logger.info(f"✅ Список звонков получен: {len(calls)} записей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка звонков: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка звонков: {e}")
            context["__step_error__"] = f"AmoCRM список звонков: {str(e)}"

    # === ОБРАБОТЧИКИ КАТАЛОГОВ ===

    async def _handle_list_catalogs(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка каталогов"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "catalogs")
            
            # Получение списка каталогов
            endpoint = "/api/v4/catalogs"
            result = await self._make_request("GET", endpoint)
            
            if result["success"]:
                catalogs = result["data"].get("_embedded", {}).get("catalogs", [])
                context[output_var] = {
                    "success": True,
                    "catalogs": catalogs,
                    "count": len(catalogs)
                }
                logger.info(f"✅ Список каталогов получен: {len(catalogs)} записей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка каталогов: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка каталогов: {e}")
            context["__step_error__"] = f"AmoCRM список каталогов: {str(e)}"

    async def _handle_create_catalog(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание каталога"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            name = self._resolve_value(params.get("name", ""), context)
            output_var = params.get("output_var", "created_catalog")
            
            if not name:
                context[output_var] = {"success": False, "error": "Не указано название каталога"}
                return
            
            # Формируем данные каталога
            catalog_data = {"name": name}
            
            if "type" in params:
                catalog_data["type"] = self._resolve_value(params["type"], context)
            
            # Создаем каталог
            endpoint = "/api/v4/catalogs"
            result = await self._make_request("POST", endpoint, json=[catalog_data])
            
            if result["success"]:
                catalogs = result["data"].get("_embedded", {}).get("catalogs", [])
                if catalogs:
                    catalog = catalogs[0]
                    context[output_var] = {
                        "success": True,
                        "catalog": catalog,
                        "catalog_id": catalog["id"]
                    }
                    logger.info(f"✅ Каталог создан: {catalog['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Каталог не создан"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка создания каталога: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания каталога: {e}")
            context["__step_error__"] = f"AmoCRM создание каталога: {str(e)}"

    async def _handle_list_catalog_elements(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение элементов каталога"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            catalog_id = self._resolve_value(params.get("catalog_id", ""), context)
            output_var = params.get("output_var", "catalog_elements")
            limit = params.get("limit", 250)
            page = params.get("page", 1)
            
            if not catalog_id:
                context[output_var] = {"success": False, "error": "Не указан catalog_id"}
                return
            
            # Параметры запроса
            request_params = {
                "limit": limit,
                "page": page
            }
            
            # Получение элементов каталога
            endpoint = f"/api/v4/catalogs/{catalog_id}/elements"
            result = await self._make_request("GET", endpoint, params=request_params)
            
            if result["success"]:
                elements = result["data"].get("_embedded", {}).get("elements", [])
                context[output_var] = {
                    "success": True,
                    "elements": elements,
                    "count": len(elements),
                    "catalog_id": catalog_id,
                    "page": page,
                    "limit": limit
                }
                logger.info(f"✅ Элементы каталога получены: {len(elements)} записей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения элементов каталога: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения элементов каталога: {e}")
            context["__step_error__"] = f"AmoCRM элементы каталога: {str(e)}"

    async def _handle_create_catalog_element(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание элемента каталога"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            catalog_id = self._resolve_value(params.get("catalog_id", ""), context)
            name = self._resolve_value(params.get("name", ""), context)
            output_var = params.get("output_var", "created_element")
            
            if not catalog_id or not name:
                context[output_var] = {"success": False, "error": "Не указаны catalog_id или name"}
                return
            
            # Формируем данные элемента
            element_data = {"name": name}
            
            if "custom_fields_values" in params:
                element_data["custom_fields_values"] = self._resolve_value(params["custom_fields_values"], context)
            
            # Создаем элемент каталога
            endpoint = f"/api/v4/catalogs/{catalog_id}/elements"
            result = await self._make_request("POST", endpoint, json=[element_data])
            
            if result["success"]:
                elements = result["data"].get("_embedded", {}).get("elements", [])
                if elements:
                    element = elements[0]
                    context[output_var] = {
                        "success": True,
                        "element": element,
                        "element_id": element["id"]
                    }
                    logger.info(f"✅ Элемент каталога создан: {element['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Элемент каталога не создан"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка создания элемента каталога: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания элемента каталога: {e}")
            context["__step_error__"] = f"AmoCRM создание элемента каталога: {str(e)}"

    async def healthcheck(self) -> bool:
        """Проверка работоспособности продвинутого модуля"""
        try:
            if not self.base_plugin:
                logger.warning("❌ Advanced healthcheck: базовый плагин недоступен")
                return False
            
            # Проверяем базовый плагин
            base_health = await self.base_plugin.healthcheck()
            
            if base_health:
                logger.info("✅ Advanced healthcheck: OK")
                return True
            else:
                logger.error("❌ Advanced healthcheck: базовый плагин не работает")
                return False
                
        except Exception as e:
            logger.error(f"❌ Advanced healthcheck: ошибка - {e}")
            return False 