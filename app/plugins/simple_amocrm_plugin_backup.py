"""
Simple AmoCRM Plugin - Упрощённый плагин для интеграции с AmoCRM

Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
- Основные операции: поиск, создание, обновление контактов и сделок
- Работа с кастомными полями
- Добавление заметок
- Минимум зависимостей
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger
import httpx

from app.core.base_plugin import BasePlugin


class SimpleAmoCRMPlugin(BasePlugin):
    """Простой плагин для работы с AmoCRM"""
    
    def __init__(self):
        super().__init__("simple_amocrm")
        
        # Настройки AmoCRM (будут загружены из БД)
        self.base_url = None
        self.access_token = None
        self.headers = {}
        
        # Карта полей (будет загружена из БД)
        self.fields_map = {}
        
        logger.info("SimpleAmoCRMPlugin инициализирован")
    
    async def _do_initialize(self):
        """Инициализация плагина"""
        # Загружаем настройки из БД
        await self._load_settings_from_db()
        
        # Загружаем карту полей из БД
        await self._load_fields_from_db()
        
        # Настраиваем HTTP заголовки если есть токен
        if self.access_token:
            self.headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            logger.info("✅ SimpleAmoCRMPlugin готов к работе")
        else:
            logger.warning("⚠️ SimpleAmoCRMPlugin работает в ограниченном режиме - настройки не найдены в БД")
            logger.info("💡 Для настройки используйте: POST /admin/plugins/amocrm/settings")
    
    async def _load_settings_from_db(self):
        """Загружает настройки AmoCRM из MongoDB"""
        try:
            logger.info(f"🔍 Проверка доступности MongoDB: engine={self.engine is not None}")
            if self.engine:
                logger.info(f"🔍 Плагины в движке: {list(self.engine.plugins.keys()) if hasattr(self.engine, 'plugins') else 'нет атрибута plugins'}")
            
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                logger.warning("MongoDB плагин недоступен для загрузки настроек AmoCRM")
                return
                
            mongo_plugin = self.engine.plugins['mongo']
            
            # Загружаем настройки AmoCRM (ищем по правильному имени плагина)
            logger.info("🔍 Ищем настройки с именем: simple_amocrm")
            settings_result = await mongo_plugin._find_one("plugin_settings", {"plugin_name": "simple_amocrm"})
            logger.info(f"🔍 Результат поиска настроек при инициализации: {settings_result}")
            
            if settings_result and settings_result.get("success") and settings_result.get("document"):
                settings = settings_result["document"]
                new_base_url = settings.get("base_url")
                new_access_token = settings.get("access_token")
                
                logger.info(f"🔍 Найденные настройки при инициализации: base_url={new_base_url}, token_length={len(new_access_token) if new_access_token else 0}")
                
                self.base_url = new_base_url
                self.access_token = new_access_token
                logger.info(f"✅ Настройки AmoCRM загружены из БД: {self.base_url}")
            else:
                logger.info("⚠️ Настройки AmoCRM не найдены в БД")
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки настроек AmoCRM из БД: {e}")
    
    async def _load_fields_from_db(self):
        """Загружает карту полей AmoCRM из MongoDB"""
        try:
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                logger.warning("MongoDB плагин недоступен для загрузки полей AmoCRM")
                await self._load_fields_from_file()  # Fallback к файлу
                return
                
            mongo_plugin = self.engine.plugins['mongo']
            
            # Загружаем карту полей
            fields_result = await mongo_plugin._find_one("plugin_settings", {"plugin_name": "amocrm_fields"})
            
            if fields_result and fields_result.get("success") and fields_result.get("document"):
                self.fields_map = fields_result["document"].get("fields_map", {})
                logger.info(f"✅ Карта полей AmoCRM загружена из БД: {len(self.fields_map)} полей")
            else:
                logger.info("⚠️ Карта полей AmoCRM не найдена в БД, загружаем из файла")
                await self._load_fields_from_file()
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки полей AmoCRM из БД: {e}")
            await self._load_fields_from_file()  # Fallback к файлу
    
    async def _load_fields_from_file(self):
        """УДАЛЕНО: больше не используем файлы конфигурации"""
        # Используем пустую карту полей если нет в БД
        self.fields_map = {}
        logger.info("⚠️ Карта полей AmoCRM пуста - настройте через API или БД")
    
    # === МЕТОДЫ ДЛЯ НАСТРОЙКИ ЧЕРЕЗ API ===
    
    async def save_settings_to_db(self, base_url: str, access_token: str) -> Dict[str, Any]:
        """Сохраняет настройки AmoCRM в MongoDB (для использования через API)"""
        try:
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                return {"success": False, "error": "MongoDB недоступен"}
                
            mongo_plugin = self.engine.plugins['mongo']
            
            settings_doc = {
                "plugin_name": "amocrm",
                "base_url": base_url,
                "access_token": access_token,
                "updated_at": datetime.now().isoformat()
            }
            
            # Используем upsert для обновления или создания
            result = await mongo_plugin._update_one(
                "plugin_settings", 
                {"plugin_name": "amocrm"}, 
                {"$set": settings_doc},
                upsert=True
            )
            
            if result.get("success"):
                # Обновляем настройки в плагине
                self.base_url = base_url
                self.access_token = access_token
                self.headers = {
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                }
                
                logger.info("✅ Настройки AmoCRM сохранены в БД и применены")
                return {"success": True, "message": "Настройки сохранены"}
            else:
                error_msg = result.get('error', 'неизвестная ошибка')
                logger.warning(f"⚠️ Не удалось сохранить настройки AmoCRM в БД: {error_msg}")
                return {"success": False, "error": error_msg}
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения настроек AmoCRM в БД: {e}")
            return {"success": False, "error": str(e)}
    
    async def save_fields_to_db(self, fields_map: Dict[str, Any]) -> Dict[str, Any]:
        """Сохраняет карту полей AmoCRM в MongoDB (для использования через API)"""
        try:
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                return {"success": False, "error": "MongoDB недоступен"}
                
            mongo_plugin = self.engine.plugins['mongo']
            
            fields_doc = {
                "plugin_name": "amocrm_fields",
                "fields_map": fields_map,
                "updated_at": datetime.now().isoformat()
            }
            
            # Используем upsert для обновления или создания
            result = await mongo_plugin._update_one(
                "plugin_settings", 
                {"plugin_name": "amocrm_fields"}, 
                {"$set": fields_doc},
                upsert=True
            )
            
            if result.get("success"):
                # Обновляем карту полей в плагине
                self.fields_map = fields_map
                
                logger.info(f"✅ Карта полей AmoCRM сохранена в БД: {len(fields_map)} полей")
                return {"success": True, "message": f"Карта полей сохранена ({len(fields_map)} полей)"}
            else:
                error_msg = result.get('error', 'неизвестная ошибка')
                logger.warning(f"⚠️ Не удалось сохранить карту полей AmoCRM в БД: {error_msg}")
                return {"success": False, "error": error_msg}
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения полей AmoCRM в БД: {e}")
            return {"success": False, "error": str(e)}
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Возвращает текущие настройки плагина"""
        return {
            "base_url": self.base_url,
            "access_token": "***" if self.access_token else None,
            "access_token_set": bool(self.access_token),
            "fields_count": len(self.fields_map),
            "configured": bool(self.base_url and self.access_token)
        }
    
    def register_handlers(self) -> Dict[str, Any]:
        """Регистрация обработчиков шагов"""
        return {
            # === КОНТАКТЫ ===
            "amocrm_find_contact": self._handle_find_contact,
            "amocrm_create_contact": self._handle_create_contact,
            "amocrm_update_contact": self._handle_update_contact,
            "amocrm_delete_contact": self._handle_delete_contact,
            "amocrm_get_contact": self._handle_get_contact,
            "amocrm_list_contacts": self._handle_list_contacts,
            
            # === СДЕЛКИ ===
            "amocrm_find_lead": self._handle_find_lead,
            "amocrm_create_lead": self._handle_create_lead,
            "amocrm_update_lead": self._handle_update_lead,
            "amocrm_delete_lead": self._handle_delete_lead,
            "amocrm_get_lead": self._handle_get_lead,
            "amocrm_list_leads": self._handle_list_leads,
            
            # === СОБЫТИЯ И ЗАМЕТКИ ===
            "amocrm_add_note": self._handle_add_note,
            
            # === УНИВЕРСАЛЬНЫЕ ОПЕРАЦИИ ===
            "amocrm_search": self._handle_search,
            "amocrm_get_account": self._handle_get_account,
        }
    
    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===
    
    @staticmethod
    def _get_enum_id(field: Dict[str, Any], value: Any = None, code: str = "WORK") -> Optional[int]:
        """Получает ID enum значения для поля"""
        enums = field.get("enums", [])
        
        # Поиск по значению
        if value:
            for enum in enums:
                if str(enum.get("value", "")).lower() == str(value).lower():
                    return enum["id"]
        
        # Поиск по коду
        for enum in enums:
            enum_value = enum.get("value", "").upper()
            enum_code = enum.get("enum_code", "").upper()
            if enum_value == code.upper() or enum_code == code.upper():
                return enum["id"]
        
        # Возвращаем первый доступный
        if enums:
            return enums[0]["id"]
            
        return None
    
    def _prepare_custom_fields(self, data: Dict[str, Any]) -> list:
        """Подготавливает кастомные поля для AmoCRM API"""
        custom_fields = []
        
        for field_name, value in data.items():
            field = self.fields_map.get(field_name)
            if not field:
                continue
                
            field_type = field.get("type")
            field_id = field["id"]
            
            if field_type in ["multitext", "text"]:
                # Текстовые поля
                custom_fields.append({
                    "field_id": field_id,
                    "values": [{"value": str(value)}]
                })
                
            elif field_type == "numeric":
                # Числовые поля
                custom_fields.append({
                    "field_id": field_id,
                    "values": [{"value": value}]
                })
                
            elif field_type == "select":
                # Селект (одиночный выбор)
                enum_id = self._get_enum_id(field, value=value)
                if enum_id:
                    custom_fields.append({
                        "field_id": field_id,
                        "values": [{"enum_id": enum_id}]
                    })
                    
            elif field_type == "multiselect":
                # Мультиселект
                if isinstance(value, list):
                    enum_ids = [self._get_enum_id(field, value=v) for v in value]
                    custom_fields.append({
                        "field_id": field_id,
                        "values": [{"enum_id": eid} for eid in enum_ids if eid]
                    })
                    
            elif field_type == "multiphonemail":
                # Телефон/Email с типом
                enum_id = self._get_enum_id(field)
                custom_fields.append({
                    "field_id": field_id,
                    "values": [{"value": str(value), "enum_id": enum_id}]
                })
                
            else:
                # Fallback для остальных типов
                custom_fields.append({
                    "field_id": field_id,
                    "values": [{"value": str(value)}]
                })
                
        return custom_fields
    
    async def _ensure_fresh_settings(self):
        """
        Динамически загружает актуальные настройки из БД перед каждым запросом.
        Это обеспечивает работу с актуальными кредами без перезапуска контейнера.
        """
        try:
            logger.info("🔄 Начинаем динамическую загрузку настроек AmoCRM")
            
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                logger.warning("MongoDB плагин недоступен для загрузки настроек AmoCRM")
                return
                
            mongo_plugin = self.engine.plugins['mongo']
            logger.info("🔍 MongoDB плагин найден, ищем настройки simple_amocrm")
            
            # Загружаем настройки AmoCRM (ищем по правильному имени плагина)
            settings_result = await mongo_plugin._find_one("plugin_settings", {"plugin_name": "simple_amocrm"})
            logger.info(f"🔍 Результат поиска настроек: {settings_result}")
            
            if settings_result and settings_result.get("success") and settings_result.get("document"):
                settings = settings_result["document"]
                new_base_url = settings.get("base_url")
                new_access_token = settings.get("access_token")
                
                logger.info(f"🔍 Найденные настройки: base_url={new_base_url}, token_length={len(new_access_token) if new_access_token else 0}")
                logger.info(f"🔍 Текущие настройки: base_url={self.base_url}, token_length={len(self.access_token) if self.access_token else 0}")
                
                # Обновляем настройки если они изменились
                if new_base_url != self.base_url or new_access_token != self.access_token:
                    logger.info(f"🔄 Обновляем настройки: {self.base_url} -> {new_base_url}")
                    self.base_url = new_base_url
                    self.access_token = new_access_token
                    self.headers = {
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json'
                    } if self.access_token else {}
                    logger.info(f"✅ Настройки AmoCRM обновлены: {self.base_url}")
                else:
                    logger.info("ℹ️ Настройки не изменились, обновление не требуется")
            else:
                logger.warning("⚠️ Настройки simple_amocrm не найдены в БД")
                    
        except Exception as e:
            logger.error(f"❌ Ошибка динамической загрузки настроек AmoCRM: {e}")

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполняет HTTP запрос к AmoCRM API"""
        
        # Динамически загружаем актуальные настройки из БД
        await self._ensure_fresh_settings()
        
        if not self.base_url or not self.access_token:
            return {
                "success": False,
                "error": "AmoCRM не настроен (отсутствуют AMO_BASE_URL или AMO_ACCESS_TOKEN)"
            }
        
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"🔗 AmoCRM {method} запрос: {url}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    timeout=30.0,
                    **kwargs
                )
                
                # Парсим ответ
                try:
                    data = response.json()
                except:
                    data = response.text
                
                result = {
                    "success": response.status_code < 400,
                    "status_code": response.status_code,
                    "data": data
                }
                
                if response.status_code >= 400:
                    result["error"] = f"AmoCRM API ошибка {response.status_code}"
                    logger.error(f"❌ AmoCRM ошибка {response.status_code}: {url}")
                else:
                    logger.info(f"✅ AmoCRM {method} успешно: {url}")
                
                return result
                
        except Exception as e:
            logger.error(f"❌ Ошибка запроса к AmoCRM: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": 0
            }
    
    def _resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Подстановка переменных из контекста"""
        if isinstance(value, str) and "{" in value and "}" in value:
            try:
                return value.format(**context)
            except (KeyError, ValueError) as e:
                logger.warning(f"Не удалось разрешить '{value}': {e}")
                return value
        return value
    
    # === ОБРАБОТЧИКИ ШАГОВ ===
    
    async def _handle_find_contact(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Поиск контакта в AmoCRM"""
        params = step_data.get("params", {})
        
        try:
            # Параметры поиска
            query = self._resolve_value(params.get("query", ""), context)
            telegram_id = self._resolve_value(params.get("telegram_id", ""), context)
            phone = self._resolve_value(params.get("phone", ""), context)
            email = self._resolve_value(params.get("email", ""), context)
            
            # Переменная для результата
            output_var = params.get("output_var", "contact")
            
            # Поиск по Telegram ID (через кастомное поле)
            if telegram_id:
                result = await self._find_contact_by_telegram_id(telegram_id)
            # Поиск по телефону
            elif phone:
                result = await self._find_contact_by_phone(phone)
            # Поиск по email
            elif email:
                result = await self._find_contact_by_email(email)
            # Общий поиск по запросу
            elif query:
                result = await self._search_contacts(query)
            else:
                result = {"success": False, "error": "Не указаны параметры поиска"}
            
            # Сохраняем результат
            context[output_var] = result
            
            if result.get("success"):
                logger.info(f"✅ Контакт найден: {result.get('contact', {}).get('id')}")
            else:
                logger.warning(f"⚠️ Контакт не найден: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска контакта: {e}")
            context["__step_error__"] = f"AmoCRM поиск контакта: {str(e)}"

    async def _handle_get_contact(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение контакта по ID"""
        params = step_data.get("params", {})
        
        try:
            contact_id = self._resolve_value(params.get("contact_id", ""), context)
            output_var = params.get("output_var", "contact")
            with_fields = params.get("with", [])  # Дополнительные поля для загрузки
            
            if not contact_id:
                context[output_var] = {"success": False, "error": "Не указан contact_id"}
                return
            
            # Формируем параметры запроса
            query_params = {}
            if with_fields:
                query_params["with"] = ",".join(with_fields)
            
            endpoint = f"/api/v4/contacts/{contact_id}"
            result = await self._make_request("GET", endpoint, params=query_params)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "contact": result["data"]
                }
                logger.info(f"✅ Контакт получен: {contact_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения контакта {contact_id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения контакта: {e}")
            context["__step_error__"] = f"AmoCRM получение контакта: {str(e)}"

    async def _handle_list_contacts(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка контактов"""
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "contacts")
            limit = params.get("limit", 250)
            page = params.get("page", 1)
            with_fields = params.get("with", [])
            filter_params = params.get("filter", {})
            order = params.get("order", {})
            
            # Формируем параметры запроса
            query_params = {
                "limit": limit,
                "page": page
            }
            
            if with_fields:
                query_params["with"] = ",".join(with_fields)
            
            # Добавляем фильтры
            for key, value in filter_params.items():
                resolved_value = self._resolve_value(value, context)
                query_params[f"filter[{key}]"] = resolved_value
            
            # Добавляем сортировку
            for key, value in order.items():
                query_params[f"order[{key}]"] = value
            
            endpoint = "/api/v4/contacts"
            result = await self._make_request("GET", endpoint, params=query_params)
            
            if result["success"]:
                contacts = result["data"].get("_embedded", {}).get("contacts", [])
                context[output_var] = {
                    "success": True,
                    "contacts": contacts,
                    "count": len(contacts),
                    "page_info": result["data"].get("_page", {})
                }
                logger.info(f"✅ Получен список контактов: {len(contacts)} шт.")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка контактов: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка контактов: {e}")
            context["__step_error__"] = f"AmoCRM список контактов: {str(e)}"

    async def _handle_delete_contact(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Удаление контакта"""
        params = step_data.get("params", {})
        
        try:
            contact_id = self._resolve_value(params.get("contact_id", ""), context)
            output_var = params.get("output_var", "delete_result")
            
            if not contact_id:
                context[output_var] = {"success": False, "error": "Не указан contact_id"}
                return
            
            endpoint = f"/api/v4/contacts/{contact_id}"
            result = await self._make_request("DELETE", endpoint)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "deleted": True,
                    "contact_id": contact_id
                }
                logger.info(f"✅ Контакт удален: {contact_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка удаления контакта {contact_id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка удаления контакта: {e}")
            context["__step_error__"] = f"AmoCRM удаление контакта: {str(e)}"
    
    # === ОБРАБОТЧИКИ СДЕЛОК ===
    
    async def _handle_find_lead(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Поиск сделки в AmoCRM"""
        params = step_data.get("params", {})
        
        try:
            # Параметры поиска
            query = self._resolve_value(params.get("query", ""), context)
            lead_id = self._resolve_value(params.get("lead_id", ""), context)
            
            # Переменная для результата
            output_var = params.get("output_var", "lead")
            
            # Поиск по ID
            if lead_id:
                result = await self._get_lead_by_id(lead_id)
            # Общий поиск
            elif query:
                result = await self._search_leads(query)
            else:
                result = {"success": False, "error": "Не указаны параметры поиска"}
            
            # Сохраняем результат
            context[output_var] = result
            
            if result.get("success"):
                logger.info(f"✅ Сделка найдена: {result.get('lead', {}).get('id')}")
            else:
                logger.warning(f"⚠️ Сделка не найдена: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска сделки: {e}")
            context["__step_error__"] = f"AmoCRM поиск сделки: {str(e)}"
    
    async def _handle_create_lead(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание сделки в AmoCRM"""
        params = step_data.get("params", {})
        
        try:
            # Основные поля
            name = self._resolve_value(params.get("name", ""), context)
            price = self._resolve_value(params.get("price", 0), context)
            contact_id = self._resolve_value(params.get("contact_id", ""), context)
            pipeline_id = self._resolve_value(params.get("pipeline_id", ""), context)
            status_id = self._resolve_value(params.get("status_id", ""), context)
            
            # Кастомные поля
            custom_fields_data = params.get("custom_fields", {})
            for key, value in custom_fields_data.items():
                custom_fields_data[key] = self._resolve_value(value, context)
            
            # Переменная для результата
            output_var = params.get("output_var", "created_lead")
            
            # Создаем сделку
            result = await self._create_lead(
                name=name,
                price=price,
                contact_id=contact_id,
                pipeline_id=pipeline_id,
                status_id=status_id,
                custom_fields=custom_fields_data
            )
            
            # Сохраняем результат
            context[output_var] = result
            
            if result.get("success"):
                logger.info(f"✅ Сделка создана: {result.get('lead', {}).get('id')}")
            else:
                logger.error(f"❌ Ошибка создания сделки: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания сделки: {e}")
            context["__step_error__"] = f"AmoCRM создание сделки: {str(e)}"
    
    async def _handle_add_note(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Добавление заметки к сущности в AmoCRM"""
        params = step_data.get("params", {})
        
        try:
            # Параметры заметки
            entity_type = params.get("entity_type", "leads")  # leads, contacts, companies
            entity_id = self._resolve_value(params.get("entity_id", ""), context)
            note_text = self._resolve_value(params.get("note_text", ""), context)
            note_type = params.get("note_type", "common")  # common, call_in, call_out, etc.
            
            # Переменная для результата
            output_var = params.get("output_var", "note_result")
            
            # Добавляем заметку
            result = await self._add_note_to_entity(entity_type, entity_id, note_text, note_type)
            
            # Сохраняем результат
            context[output_var] = result
            
            if result.get("success"):
                logger.info(f"✅ Заметка добавлена к {entity_type}:{entity_id}")
            else:
                logger.error(f"❌ Ошибка добавления заметки: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка добавления заметки: {e}")
            context["__step_error__"] = f"AmoCRM добавление заметки: {str(e)}"
    
    async def _handle_search(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Универсальный поиск в AmoCRM"""
        params = step_data.get("params", {})
        
        try:
            # Параметры поиска
            query = self._resolve_value(params.get("query", ""), context)
            entity_type = params.get("entity_type", "contacts")  # contacts, leads, companies
            limit = params.get("limit", 50)
            
            # Переменная для результата
            output_var = params.get("output_var", "search_results")
            
            # Выполняем поиск
            if entity_type == "contacts":
                result = await self._search_contacts(query)
            elif entity_type == "leads":
                result = await self._search_leads(query)
            elif entity_type == "companies":
                result = await self._search_companies(query)
            else:
                result = {"success": False, "error": f"Неподдерживаемый тип сущности: {entity_type}"}
            
            # Ограничиваем количество результатов
            if result.get("success") and "contacts" in result:
                result["contacts"] = result["contacts"][:limit]
            elif result.get("success") and "leads" in result:
                result["leads"] = result["leads"][:limit]
            elif result.get("success") and "companies" in result:
                result["companies"] = result["companies"][:limit]
            
            # Сохраняем результат
            context[output_var] = result
            
            if result.get("success"):
                count = result.get("count", 0)
                logger.info(f"✅ Поиск выполнен: найдено {count} результатов")
            else:
                logger.warning(f"⚠️ Поиск не дал результатов: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")
            context["__step_error__"] = f"AmoCRM поиск: {str(e)}"
    
    # === МЕТОДЫ РАБОТЫ СО СДЕЛКАМИ ===
    
    async def _get_lead_by_id(self, lead_id: int) -> Dict[str, Any]:
        """Получение сделки по ID"""
        endpoint = f"/api/v4/leads/{lead_id}"
        
        result = await self._make_request("GET", endpoint)
        
        if result["success"]:
            return {
                "success": True,
                "lead": result["data"],
                "found": True
            }
        
        return {"success": False, "error": result.get("error", "Сделка не найдена")}
    
    async def _search_leads(self, query: str) -> Dict[str, Any]:
        """Поиск сделок"""
        endpoint = f"/api/v4/leads"
        params = {"query": query}
        
        result = await self._make_request("GET", endpoint, params=params)
        
        if result["success"]:
            leads = result["data"].get("_embedded", {}).get("leads", [])
            return {
                "success": True,
                "leads": leads,
                "count": len(leads)
            }
        
        return {"success": False, "error": result.get("error", "Ошибка поиска сделок")}
    
    async def _create_lead(self, name: str, price: int = 0, contact_id: int = None,
                          pipeline_id: int = None, status_id: int = None,
                          custom_fields: Dict[str, Any] = None) -> Dict[str, Any]:
        """Создание новой сделки"""
        lead_data = {"name": name}
        
        if price:
            lead_data["price"] = price
        if pipeline_id:
            lead_data["pipeline_id"] = pipeline_id
        if status_id:
            lead_data["status_id"] = status_id
        
        # Привязка к контакту
        if contact_id:
            lead_data["_embedded"] = {
                "contacts": [{"id": contact_id}]
            }
        
        # Кастомные поля
        if custom_fields:
            lead_data["custom_fields_values"] = self._prepare_custom_fields(custom_fields)
        
        endpoint = "/api/v4/leads"
        payload = [lead_data]
        
        result = await self._make_request("POST", endpoint, json=payload)
        
        if result["success"] and result["data"].get("_embedded", {}).get("leads"):
            lead = result["data"]["_embedded"]["leads"][0]
            return {
                "success": True,
                "lead": lead,
                "lead_id": lead["id"]
            }
        
        return {"success": False, "error": result.get("error", "Ошибка создания сделки")}
    
    async def _search_companies(self, query: str) -> Dict[str, Any]:
        """Поиск компаний"""
        endpoint = f"/api/v4/companies"
        params = {"query": query}
        
        result = await self._make_request("GET", endpoint, params=params)
        
        if result["success"]:
            companies = result["data"].get("_embedded", {}).get("companies", [])
            return {
                "success": True,
                "companies": companies,
                "count": len(companies)
            }
        
        return {"success": False, "error": result.get("error", "Ошибка поиска компаний")}
    
    async def _add_note_to_entity(self, entity_type: str, entity_id: int, 
                                 note_text: str, note_type: str = "common") -> Dict[str, Any]:
        """Добавление заметки к сущности"""
        note_data = {
            "entity_id": entity_id,
            "note_type": note_type,
            "params": {
                "text": note_text
            }
        }
        
        endpoint = f"/api/v4/{entity_type}/notes"
        payload = [note_data]
        
        result = await self._make_request("POST", endpoint, json=payload)
        
        if result["success"]:
            return {
                "success": True,
                "note_added": True,
                "entity_id": entity_id
            }
        
        return {"success": False, "error": result.get("error", "Ошибка добавления заметки")}
    
    # === HEALTHCHECK ===
    
    async def healthcheck(self) -> bool:
        """Проверка работоспособности AmoCRM плагина"""
        try:
            if not self.base_url or not self.access_token:
                logger.warning("❌ AmoCRM healthcheck: отсутствуют настройки")
                return False
            
            # Проверяем доступность API через получение информации об аккаунте
            result = await self._make_request("GET", "/api/v4/account")
            
            if result["success"]:
                account_name = result["data"].get("name", "Unknown")
                logger.info(f"✅ AmoCRM healthcheck: OK (аккаунт: {account_name})")
                return True
            else:
                logger.error(f"❌ AmoCRM healthcheck: API недоступен - {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ AmoCRM healthcheck: ошибка - {e}")
            return False

    async def _handle_create_contact(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание контакта в AmoCRM"""
        params = step_data.get("params", {})
        
        try:
            # Основные поля
            name = self._resolve_value(params.get("name", ""), context)
            first_name = self._resolve_value(params.get("first_name", ""), context)
            last_name = self._resolve_value(params.get("last_name", ""), context)
            
            # Кастомные поля
            custom_fields_data = params.get("custom_fields", {})
            for key, value in custom_fields_data.items():
                custom_fields_data[key] = self._resolve_value(value, context)
            
            # Переменная для результата
            output_var = params.get("output_var", "created_contact")
            
            # Создаем контакт
            result = await self._create_contact(
                name=name,
                first_name=first_name,
                last_name=last_name,
                custom_fields=custom_fields_data
            )
            
            # Сохраняем результат
            context[output_var] = result
            
            if result.get("success"):
                logger.info(f"✅ Контакт создан: {result.get('contact', {}).get('id')}")
            else:
                logger.error(f"❌ Ошибка создания контакта: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания контакта: {e}")
            context["__step_error__"] = f"AmoCRM создание контакта: {str(e)}"

    async def _handle_update_contact(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Обновление контакта в AmoCRM"""
        params = step_data.get("params", {})
        
        try:
            # ID контакта
            contact_id = self._resolve_value(params.get("contact_id", ""), context)
            
            # Поля для обновления
            update_data = params.get("update_data", {})
            for key, value in update_data.items():
                update_data[key] = self._resolve_value(value, context)
            
            # Переменная для результата
            output_var = params.get("output_var", "updated_contact")
            
            # Обновляем контакт
            result = await self._update_contact(contact_id, update_data)
            
            # Сохраняем результат
            context[output_var] = result
            
            if result.get("success"):
                logger.info(f"✅ Контакт обновлен: {contact_id}")
            else:
                logger.error(f"❌ Ошибка обновления контакта: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления контакта: {e}")
            context["__step_error__"] = f"AmoCRM обновление контакта: {str(e)}"
    
    # === МЕТОДЫ РАБОТЫ С КОНТАКТАМИ ===
    
    async def _find_contact_by_telegram_id(self, telegram_id: str) -> Dict[str, Any]:
        """Поиск контакта по Telegram ID"""
        # Ищем через кастомное поле telegram_id
        endpoint = f"/api/v4/contacts"
        params = {"query": telegram_id}
        
        result = await self._make_request("GET", endpoint, params=params)
        
        if result["success"] and result["data"].get("_embedded", {}).get("contacts"):
            contacts = result["data"]["_embedded"]["contacts"]
            
            # Ищем точное совпадение по telegram_id в кастомных полях
            for contact in contacts:
                custom_fields = contact.get("custom_fields_values", [])
                for field in custom_fields:
                    if field.get("field_name") == "telegram_id":
                        values = field.get("values", [])
                        for value in values:
                            if str(value.get("value")) == str(telegram_id):
                                return {
                                    "success": True,
                                    "contact": contact,
                                    "found": True
                                }
            
            return {"success": True, "contact": None, "found": False}
        
        return {"success": False, "error": result.get("error", "Контакт не найден")}
    
    async def _find_contact_by_phone(self, phone: str) -> Dict[str, Any]:
        """Поиск контакта по телефону"""
        endpoint = f"/api/v4/contacts"
        params = {"query": phone}
        
        result = await self._make_request("GET", endpoint, params=params)
        
        if result["success"] and result["data"].get("_embedded", {}).get("contacts"):
            contacts = result["data"]["_embedded"]["contacts"]
            return {
                "success": True,
                "contact": contacts[0] if contacts else None,
                "found": len(contacts) > 0
            }
        
        return {"success": False, "error": result.get("error", "Контакт не найден")}
    
    async def _find_contact_by_email(self, email: str) -> Dict[str, Any]:
        """Поиск контакта по email"""
        endpoint = f"/api/v4/contacts"
        params = {"query": email}
        
        result = await self._make_request("GET", endpoint, params=params)
        
        if result["success"] and result["data"].get("_embedded", {}).get("contacts"):
            contacts = result["data"]["_embedded"]["contacts"]
            return {
                "success": True,
                "contact": contacts[0] if contacts else None,
                "found": len(contacts) > 0
            }
        
        return {"success": False, "error": result.get("error", "Контакт не найден")}
    
    async def _search_contacts(self, query: str) -> Dict[str, Any]:
        """Общий поиск контактов"""
        endpoint = f"/api/v4/contacts"
        params = {"query": query}
        
        result = await self._make_request("GET", endpoint, params=params)
        
        if result["success"]:
            contacts = result["data"].get("_embedded", {}).get("contacts", [])
            return {
                "success": True,
                "contacts": contacts,
                "count": len(contacts)
            }
        
        return {"success": False, "error": result.get("error", "Ошибка поиска")}
    
    async def _create_contact(self, name: str = "", first_name: str = "", last_name: str = "", 
                            custom_fields: Dict[str, Any] = None) -> Dict[str, Any]:
        """Создание нового контакта"""
        contact_data = {}
        
        # Имя контакта
        if name:
            contact_data["name"] = name
        elif first_name or last_name:
            contact_data["name"] = f"{first_name} {last_name}".strip()
        
        if first_name:
            contact_data["first_name"] = first_name
        if last_name:
            contact_data["last_name"] = last_name
        
        # Кастомные поля
        if custom_fields:
            contact_data["custom_fields_values"] = self._prepare_custom_fields(custom_fields)
        
        endpoint = "/api/v4/contacts"
        payload = [contact_data]
        
        result = await self._make_request("POST", endpoint, json=payload)
        
        if result["success"] and result["data"].get("_embedded", {}).get("contacts"):
            contact = result["data"]["_embedded"]["contacts"][0]
            return {
                "success": True,
                "contact": contact,
                "contact_id": contact["id"]
            }
        
        return {"success": False, "error": result.get("error", "Ошибка создания контакта")}
    
    async def _update_contact(self, contact_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление существующего контакта"""
        contact_data = {"id": contact_id}
        
        # Основные поля
        for field in ["name", "first_name", "last_name"]:
            if field in update_data:
                contact_data[field] = update_data[field]
        
        # Кастомные поля
        custom_fields = {k: v for k, v in update_data.items() 
                        if k not in ["name", "first_name", "last_name"]}
        if custom_fields:
            contact_data["custom_fields_values"] = self._prepare_custom_fields(custom_fields)
        
        endpoint = "/api/v4/contacts"
        payload = [contact_data]
        
        result = await self._make_request("PATCH", endpoint, json=payload)
        
        if result["success"]:
            return {
                "success": True,
                "contact_id": contact_id,
                "updated": True
            }
        
        return {"success": False, "error": result.get("error", "Ошибка обновления контакта")}
    
    # === ОБРАБОТЧИКИ СДЕЛОК (РАСШИРЕННЫЕ) ===
    
    async def _handle_update_lead(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Обновление сделки в AmoCRM"""
        params = step_data.get("params", {})
        
        try:
            lead_id = self._resolve_value(params.get("lead_id", ""), context)
            update_data = params.get("update_data", {})
            output_var = params.get("output_var", "updated_lead")
            
            # Разрешаем переменные в данных для обновления
            for key, value in update_data.items():
                update_data[key] = self._resolve_value(value, context)
            
            if not lead_id:
                context[output_var] = {"success": False, "error": "Не указан lead_id"}
                return
            
            result = await self._update_lead_data(lead_id, update_data)
            context[output_var] = result
            
            if result.get("success"):
                logger.info(f"✅ Сделка обновлена: {lead_id}")
            else:
                logger.error(f"❌ Ошибка обновления сделки: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления сделки: {e}")
            context["__step_error__"] = f"AmoCRM обновление сделки: {str(e)}"

    async def _handle_delete_lead(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Удаление сделки"""
        params = step_data.get("params", {})
        
        try:
            lead_id = self._resolve_value(params.get("lead_id", ""), context)
            output_var = params.get("output_var", "delete_result")
            
            if not lead_id:
                context[output_var] = {"success": False, "error": "Не указан lead_id"}
                return
            
            endpoint = f"/api/v4/leads/{lead_id}"
            result = await self._make_request("DELETE", endpoint)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "deleted": True,
                    "lead_id": lead_id
                }
                logger.info(f"✅ Сделка удалена: {lead_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка удаления сделки {lead_id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка удаления сделки: {e}")
            context["__step_error__"] = f"AmoCRM удаление сделки: {str(e)}"

    async def _handle_get_lead(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение сделки по ID"""
        params = step_data.get("params", {})
        
        try:
            lead_id = self._resolve_value(params.get("lead_id", ""), context)
            output_var = params.get("output_var", "lead")
            with_fields = params.get("with", [])
            
            if not lead_id:
                context[output_var] = {"success": False, "error": "Не указан lead_id"}
                return
            
            query_params = {}
            if with_fields:
                query_params["with"] = ",".join(with_fields)
            
            endpoint = f"/api/v4/leads/{lead_id}"
            result = await self._make_request("GET", endpoint, params=query_params)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "lead": result["data"]
                }
                logger.info(f"✅ Сделка получена: {lead_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения сделки {lead_id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения сделки: {e}")
            context["__step_error__"] = f"AmoCRM получение сделки: {str(e)}"

    async def _handle_list_leads(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка сделок"""
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "leads")
            limit = params.get("limit", 250)
            page = params.get("page", 1)
            with_fields = params.get("with", [])
            filter_params = params.get("filter", {})
            order = params.get("order", {})
            
            query_params = {
                "limit": limit,
                "page": page
            }
            
            if with_fields:
                query_params["with"] = ",".join(with_fields)
            
            # Добавляем фильтры
            for key, value in filter_params.items():
                resolved_value = self._resolve_value(value, context)
                query_params[f"filter[{key}]"] = resolved_value
            
            # Добавляем сортировку
            for key, value in order.items():
                query_params[f"order[{key}]"] = value
            
            endpoint = "/api/v4/leads"
            result = await self._make_request("GET", endpoint, params=query_params)
            
            if result["success"]:
                leads = result["data"].get("_embedded", {}).get("leads", [])
                context[output_var] = {
                    "success": True,
                    "leads": leads,
                    "count": len(leads),
                    "page_info": result["data"].get("_page", {})
                }
                logger.info(f"✅ Получен список сделок: {len(leads)} шт.")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка сделок: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка сделок: {e}")
            context["__step_error__"] = f"AmoCRM список сделок: {str(e)}"

    async def _update_lead_data(self, lead_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление существующей сделки"""
        lead_data = {"id": lead_id}
        
        # Основные поля
        for field in ["name", "price", "pipeline_id", "status_id", "responsible_user_id"]:
            if field in update_data:
                lead_data[field] = update_data[field]
        
        # Кастомные поля
        custom_fields = {k: v for k, v in update_data.items() 
                        if k not in ["name", "price", "pipeline_id", "status_id", "responsible_user_id"]}
        if custom_fields:
            lead_data["custom_fields_values"] = self._prepare_custom_fields(custom_fields)
        
        endpoint = "/api/v4/leads"
        payload = [lead_data]
        
        result = await self._make_request("PATCH", endpoint, json=payload)
        
        if result["success"]:
            return {
                "success": True,
                "lead_id": lead_id,
                "updated": True
            }
        
        return {"success": False, "error": result.get("error", "Ошибка обновления сделки")}

    # === УНИВЕРСАЛЬНЫЕ ОБРАБОТЧИКИ ===
    
    async def _handle_get_account(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение информации об аккаунте AmoCRM"""
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "account")
            with_fields = params.get("with", [])
            
            query_params = {}
            if with_fields:
                query_params["with"] = ",".join(with_fields)
            
            endpoint = "/api/v4/account"
            result = await self._make_request("GET", endpoint, params=query_params)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "account": result["data"]
                }
                account_name = result["data"].get("name", "Unknown")
                logger.info(f"✅ Информация об аккаунте получена: {account_name}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения информации об аккаунте: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации об аккаунте: {e}")
            context["__step_error__"] = f"AmoCRM информация об аккаунте: {str(e)}" 