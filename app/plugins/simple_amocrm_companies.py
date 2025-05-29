"""
Simple AmoCRM Companies Plugin - Модуль для работы с компаниями

Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
- Только операции с компаниями AmoCRM
- Наследует настройки от базового плагина
- Минимум кода и зависимостей
"""

from typing import Dict, Any
from loguru import logger

from app.core.base_plugin import BasePlugin


class SimpleAmoCRMCompaniesPlugin(BasePlugin):
    """Простой плагин для работы с компаниями AmoCRM"""
    
    def __init__(self):
        super().__init__("simple_amocrm_companies")
        
        # Ссылка на базовый плагин для использования его методов
        self.base_plugin = None
        
        logger.info("SimpleAmoCRMCompaniesPlugin инициализирован")
    
    async def _do_initialize(self):
        """Инициализация плагина"""
        # Получаем ссылку на базовый AmoCRM плагин
        if self.engine and hasattr(self.engine, 'plugins'):
            self.base_plugin = self.engine.plugins.get('simple_amocrm')
            
        if self.base_plugin:
            logger.info("✅ SimpleAmoCRMCompaniesPlugin готов к работе")
        else:
            logger.warning("⚠️ Базовый AmoCRM плагин не найден")
    
    def register_handlers(self) -> Dict[str, Any]:
        """Регистрация обработчиков для работы с компаниями"""
        return {
            # === КОМПАНИИ ===
            "amocrm_find_company": self._handle_find_company,
            "amocrm_create_company": self._handle_create_company,
            "amocrm_update_company": self._handle_update_company,
            "amocrm_delete_company": self._handle_delete_company,
            "amocrm_get_company": self._handle_get_company,
            "amocrm_list_companies": self._handle_list_companies,
            
            # === СВЯЗИ ===
            "amocrm_link_contact_to_company": self._handle_link_contact_to_company,
            "amocrm_unlink_contact_from_company": self._handle_unlink_contact_from_company,
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
    
    # === ОБРАБОТЧИКИ КОМПАНИЙ ===
    
    async def _handle_find_company(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Поиск компании в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            query = self._resolve_value(params.get("query", ""), context)
            output_var = params.get("output_var", "company")
            
            if not query:
                context[output_var] = {"success": False, "error": "Не указан query для поиска"}
                return
            
            # Поиск компании
            endpoint = f"/api/v4/companies"
            result = await self._make_request("GET", endpoint, params={"query": query})
            
            if result["success"]:
                companies = result["data"].get("_embedded", {}).get("companies", [])
                context[output_var] = {
                    "success": True,
                    "company": companies[0] if companies else None,
                    "found": len(companies) > 0,
                    "count": len(companies)
                }
                logger.info(f"✅ Поиск компании: найдено {len(companies)} результатов")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка поиска компании: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска компании: {e}")
            context["__step_error__"] = f"AmoCRM поиск компании: {str(e)}"

    async def _handle_get_company(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение компании по ID"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            company_id = self._resolve_value(params.get("company_id", ""), context)
            output_var = params.get("output_var", "company")
            with_param = params.get("with", [])  # contacts, leads, customers
            
            if not company_id:
                context[output_var] = {"success": False, "error": "Не указан company_id"}
                return
            
            # Параметры запроса
            request_params = {}
            if with_param:
                request_params["with"] = ",".join(with_param) if isinstance(with_param, list) else with_param
            
            # Получение компании
            endpoint = f"/api/v4/companies/{company_id}"
            result = await self._make_request("GET", endpoint, params=request_params)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "company": result["data"]
                }
                logger.info(f"✅ Компания получена: {company_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения компании: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения компании: {e}")
            context["__step_error__"] = f"AmoCRM получение компании: {str(e)}"

    async def _handle_list_companies(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка компаний"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "companies")
            limit = params.get("limit", 250)
            page = params.get("page", 1)
            with_param = params.get("with", [])
            filter_params = params.get("filter", {})
            
            # Параметры запроса
            request_params = {
                "limit": limit,
                "page": page
            }
            
            if with_param:
                request_params["with"] = ",".join(with_param) if isinstance(with_param, list) else with_param
            
            # Добавляем фильтры
            for key, value in filter_params.items():
                resolved_value = self._resolve_value(value, context)
                request_params[key] = resolved_value
            
            # Получение списка компаний
            endpoint = f"/api/v4/companies"
            result = await self._make_request("GET", endpoint, params=request_params)
            
            if result["success"]:
                companies = result["data"].get("_embedded", {}).get("companies", [])
                context[output_var] = {
                    "success": True,
                    "companies": companies,
                    "count": len(companies),
                    "page": page,
                    "limit": limit
                }
                logger.info(f"✅ Список компаний получен: {len(companies)} записей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка компаний: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка компаний: {e}")
            context["__step_error__"] = f"AmoCRM список компаний: {str(e)}"

    async def _handle_create_company(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание компании в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            name = self._resolve_value(params.get("name", ""), context)
            output_var = params.get("output_var", "created_company")
            
            if not name:
                context[output_var] = {"success": False, "error": "Не указано название компании"}
                return
            
            # Формируем данные компании
            company_data = {"name": name}
            
            # Дополнительные поля
            if "responsible_user_id" in params:
                company_data["responsible_user_id"] = int(self._resolve_value(params["responsible_user_id"], context))
            
            # Кастомные поля
            custom_fields = []
            
            # Телефон
            if "phone" in params:
                phone = self._resolve_value(params["phone"], context)
                if phone:
                    custom_fields.append({
                        "field_code": "PHONE",
                        "values": [{"value": phone, "enum_code": "WORK"}]
                    })
            
            # Email
            if "email" in params:
                email = self._resolve_value(params["email"], context)
                if email:
                    custom_fields.append({
                        "field_code": "EMAIL",
                        "values": [{"value": email, "enum_code": "WORK"}]
                    })
            
            # Веб-сайт
            if "website" in params:
                website = self._resolve_value(params["website"], context)
                if website:
                    custom_fields.append({
                        "field_code": "WEB",
                        "values": [{"value": website, "enum_code": "WORK"}]
                    })
            
            if custom_fields:
                company_data["custom_fields_values"] = custom_fields
            
            # Создаем компанию
            endpoint = "/api/v4/companies"
            result = await self._make_request("POST", endpoint, json=[company_data])
            
            if result["success"]:
                companies = result["data"].get("_embedded", {}).get("companies", [])
                if companies:
                    company = companies[0]
                    context[output_var] = {
                        "success": True,
                        "company": company,
                        "company_id": company["id"]
                    }
                    logger.info(f"✅ Компания создана: {company['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Компания не создана"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка создания компании: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания компании: {e}")
            context["__step_error__"] = f"AmoCRM создание компании: {str(e)}"

    async def _handle_update_company(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Обновление компании в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            company_id = self._resolve_value(params.get("company_id", ""), context)
            output_var = params.get("output_var", "updated_company")
            
            if not company_id:
                context[output_var] = {"success": False, "error": "Не указан company_id"}
                return
            
            # Формируем данные для обновления
            company_data = {"id": int(company_id)}
            
            # Обновляемые поля
            if "name" in params:
                company_data["name"] = self._resolve_value(params["name"], context)
            
            if "responsible_user_id" in params:
                company_data["responsible_user_id"] = int(self._resolve_value(params["responsible_user_id"], context))
            
            # Кастомные поля для обновления
            custom_fields = []
            
            if "phone" in params:
                phone = self._resolve_value(params["phone"], context)
                if phone:
                    custom_fields.append({
                        "field_code": "PHONE",
                        "values": [{"value": phone, "enum_code": "WORK"}]
                    })
            
            if "email" in params:
                email = self._resolve_value(params["email"], context)
                if email:
                    custom_fields.append({
                        "field_code": "EMAIL",
                        "values": [{"value": email, "enum_code": "WORK"}]
                    })
            
            if "website" in params:
                website = self._resolve_value(params["website"], context)
                if website:
                    custom_fields.append({
                        "field_code": "WEB",
                        "values": [{"value": website, "enum_code": "WORK"}]
                    })
            
            if custom_fields:
                company_data["custom_fields_values"] = custom_fields
            
            # Обновляем компанию
            endpoint = "/api/v4/companies"
            result = await self._make_request("PATCH", endpoint, json=[company_data])
            
            if result["success"]:
                companies = result["data"].get("_embedded", {}).get("companies", [])
                if companies:
                    company = companies[0]
                    context[output_var] = {
                        "success": True,
                        "company": company,
                        "company_id": company["id"]
                    }
                    logger.info(f"✅ Компания обновлена: {company['id']}")
                else:
                    context[output_var] = {"success": False, "error": "Компания не обновлена"}
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка обновления компании: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления компании: {e}")
            context["__step_error__"] = f"AmoCRM обновление компании: {str(e)}"

    async def _handle_delete_company(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Удаление компании из AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            company_id = self._resolve_value(params.get("company_id", ""), context)
            output_var = params.get("output_var", "delete_result")
            
            if not company_id:
                context[output_var] = {"success": False, "error": "Не указан company_id"}
                return
            
            # Удаляем компанию
            endpoint = f"/api/v4/companies/{company_id}"
            result = await self._make_request("DELETE", endpoint)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "deleted": True,
                    "company_id": company_id
                }
                logger.info(f"✅ Компания удалена: {company_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка удаления компании: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка удаления компании: {e}")
            context["__step_error__"] = f"AmoCRM удаление компании: {str(e)}"

    # === ОБРАБОТЧИКИ СВЯЗЕЙ ===

    async def _handle_link_contact_to_company(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Привязка контакта к компании"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            contact_id = self._resolve_value(params.get("contact_id", ""), context)
            company_id = self._resolve_value(params.get("company_id", ""), context)
            output_var = params.get("output_var", "link_result")
            
            if not contact_id or not company_id:
                context[output_var] = {"success": False, "error": "Не указаны contact_id или company_id"}
                return
            
            # Обновляем контакт, добавляя связь с компанией
            contact_data = {
                "id": int(contact_id),
                "_embedded": {
                    "companies": [{"id": int(company_id)}]
                }
            }
            
            endpoint = "/api/v4/contacts"
            result = await self._make_request("PATCH", endpoint, json=[contact_data])
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "linked": True,
                    "contact_id": contact_id,
                    "company_id": company_id
                }
                logger.info(f"✅ Контакт {contact_id} привязан к компании {company_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка привязки контакта к компании: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка привязки контакта к компании: {e}")
            context["__step_error__"] = f"AmoCRM привязка контакта: {str(e)}"

    async def _handle_unlink_contact_from_company(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Отвязка контакта от компании"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            contact_id = self._resolve_value(params.get("contact_id", ""), context)
            output_var = params.get("output_var", "unlink_result")
            
            if not contact_id:
                context[output_var] = {"success": False, "error": "Не указан contact_id"}
                return
            
            # Обновляем контакт, убирая связи с компаниями
            contact_data = {
                "id": int(contact_id),
                "_embedded": {
                    "companies": []
                }
            }
            
            endpoint = "/api/v4/contacts"
            result = await self._make_request("PATCH", endpoint, json=[contact_data])
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "unlinked": True,
                    "contact_id": contact_id
                }
                logger.info(f"✅ Контакт {contact_id} отвязан от компаний")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка отвязки контакта от компании: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка отвязки контакта от компании: {e}")
            context["__step_error__"] = f"AmoCRM отвязка контакта: {str(e)}"

    async def healthcheck(self) -> bool:
        """Проверка работоспособности модуля компаний"""
        try:
            if not self.base_plugin:
                logger.warning("❌ Companies healthcheck: базовый плагин недоступен")
                return False
            
            # Проверяем базовый плагин
            base_health = await self.base_plugin.healthcheck()
            
            if base_health:
                logger.info("✅ Companies healthcheck: OK")
                return True
            else:
                logger.error("❌ Companies healthcheck: базовый плагин не работает")
                return False
                
        except Exception as e:
            logger.error(f"❌ Companies healthcheck: ошибка - {e}")
            return False 