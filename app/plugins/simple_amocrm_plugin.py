"""
Simple AmoCRM Plugin - Минимальная версия

Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
- Только основные операции: поиск, создание контактов и сделок
- Минимум кода и зависимостей
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
    
    async def _load_settings_from_db(self):
        """Загружает настройки AmoCRM из MongoDB"""
        try:
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                logger.warning("MongoDB плагин недоступен для загрузки настроек AmoCRM")
                return
                
            mongo_plugin = self.engine.plugins['mongo']
            
            # Загружаем настройки AmoCRM из коллекции settings
            settings_result = await mongo_plugin._find_one("settings", {"plugin_name": "simple_amocrm"})
            
            # ОТЛАДКА: логируем результат запроса
            logger.info(f"🔍 ОТЛАДКА settings_result: {settings_result}")
            if settings_result and settings_result.get("success"):
                logger.info(f"🔍 ОТЛАДКА document: {settings_result.get('document')}")
            
            if settings_result and settings_result.get("success") and settings_result.get("document"):
                settings = settings_result["document"]
                self.base_url = settings.get("base_url")
                self.access_token = settings.get("access_token")
                logger.info(f"✅ Настройки AmoCRM загружены из БД: {self.base_url}")
            else:
                logger.info("⚠️ Настройки AmoCRM не найдены в БД")
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки настроек AmoCRM из БД: {e}")
    
    async def _load_fields_from_db(self):
        """Загружает карту полей AmoCRM из MongoDB"""
        try:
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                logger.warning("MongoDB плагин недоступен для загрузки карты полей AmoCRM")
                return
                
            mongo_plugin = self.engine.plugins['mongo']
            
            # Загружаем карту полей из коллекции settings (УПРОЩЕНО!)
            fields_result = await mongo_plugin._find_one("settings", {"plugin": "simple_amocrm_fields"})
            
            if fields_result and fields_result.get("success") and fields_result.get("document"):
                self.fields_map = fields_result["document"].get("contact_fields", {})
                logger.info(f"✅ Карта полей AmoCRM загружена из settings: {len(self.fields_map)} полей")
            else:
                logger.info("⚠️ Карта полей AmoCRM не найдена в settings")
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки карты полей AmoCRM из settings: {e}")

    def register_handlers(self) -> Dict[str, Any]:
        """Регистрация обработчиков шагов"""
        return {
            # === КОНТАКТЫ ===
            "amocrm_find_contact": self._handle_find_contact,
            "amocrm_create_contact": self._handle_create_contact,
            "amocrm_update_contact": self._handle_update_contact,
            
            # === СДЕЛКИ ===
            "amocrm_find_lead": self._handle_find_lead,
            "amocrm_create_lead": self._handle_create_lead,
            
            # === ЗАМЕТКИ ===
            "amocrm_add_note": self._handle_add_note,
            
            # === УНИВЕРСАЛЬНЫЕ ===
            "amocrm_search": self._handle_search,
            
            # === КАРТА ПОЛЕЙ ===
            "amocrm_fetch_fields": self._handle_fetch_fields,
            "amocrm_save_fields": self._handle_save_fields,
            "amocrm_get_fields": self._handle_get_fields,
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
        """Выполняет HTTP запрос к AmoCRM API"""
        
        # Динамически загружаем актуальные настройки из БД
        await self._ensure_fresh_settings()
        
        if not self.base_url or not self.access_token:
            return {
                "success": False,
                "error": "AmoCRM не настроен (отсутствуют настройки в БД)"
            }
        
        url = f"{self.base_url}{endpoint}"
        
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
    
    # === ОБРАБОТЧИКИ ===
    
    async def _handle_find_contact(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Поиск контакта в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            query = self._resolve_value(params.get("query", ""), context)
            output_var = params.get("output_var", "contact")
            
            if not query:
                context[output_var] = {"success": False, "error": "Не указан query для поиска"}
                return
            
            # Поиск контакта
            endpoint = f"/api/v4/contacts"
            result = await self._make_request("GET", endpoint, params={"query": query})
            
            if result["success"]:
                # Проверяем что data является словарем
                data = result.get("data", {})
                if isinstance(data, dict):
                    contacts = data.get("_embedded", {}).get("contacts", [])
                    context[output_var] = {
                        "success": True,
                        "contact": contacts[0] if contacts else None,
                        "found": len(contacts) > 0,
                        "count": len(contacts)
                    }
                    logger.info(f"✅ Поиск контакта: найдено {len(contacts)} результатов")
                else:
                    context[output_var] = {
                        "success": False,
                        "error": f"Неожиданный формат ответа AmoCRM: {type(data).__name__}"
                    }
                    logger.error(f"❌ Неожиданный формат ответа AmoCRM: {data}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка поиска контакта: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска контакта: {e}")
            context["__step_error__"] = f"AmoCRM поиск контакта: {str(e)}"

    async def _handle_find_lead(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Поиск сделки в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            query = self._resolve_value(params.get("query", ""), context)
            output_var = params.get("output_var", "lead")
            
            if not query:
                context[output_var] = {"success": False, "error": "Не указан query для поиска"}
                return
            
            # Поиск сделки
            endpoint = f"/api/v4/leads"
            result = await self._make_request("GET", endpoint, params={"query": query})
            
            if result["success"]:
                # Проверяем что data является словарем
                data = result.get("data", {})
                if isinstance(data, dict):
                    leads = data.get("_embedded", {}).get("leads", [])
                    context[output_var] = {
                        "success": True,
                        "lead": leads[0] if leads else None,
                        "found": len(leads) > 0,
                        "count": len(leads)
                    }
                    logger.info(f"✅ Поиск сделки: найдено {len(leads)} результатов")
                else:
                    context[output_var] = {
                        "success": False,
                        "error": f"Неожиданный формат ответа AmoCRM: {type(data).__name__}"
                    }
                    logger.error(f"❌ Неожиданный формат ответа AmoCRM: {data}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка поиска сделки: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска сделки: {e}")
            context["__step_error__"] = f"AmoCRM поиск сделки: {str(e)}"

    async def _handle_search(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Универсальный поиск в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            query = self._resolve_value(params.get("query", ""), context)
            entity_type = params.get("entity_type", "contacts")  # contacts, leads
            output_var = params.get("output_var", "search_results")
            
            if not query:
                context[output_var] = {"success": False, "error": "Не указан query для поиска"}
                return
            
            # Универсальный поиск
            endpoint = f"/api/v4/{entity_type}"
            result = await self._make_request("GET", endpoint, params={"query": query})
            
            if result["success"]:
                # Проверяем что data является словарем
                data = result.get("data", {})
                if isinstance(data, dict):
                    items = data.get("_embedded", {}).get(entity_type, [])
                    context[output_var] = {
                        "success": True,
                        "items": items,
                        "count": len(items),
                        "entity_type": entity_type
                    }
                    logger.info(f"✅ Универсальный поиск {entity_type}: найдено {len(items)} результатов")
                else:
                    context[output_var] = {
                        "success": False,
                        "error": f"Неожиданный формат ответа AmoCRM: {type(data).__name__}"
                    }
                    logger.error(f"❌ Неожиданный формат ответа AmoCRM: {data}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка универсального поиска: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка универсального поиска: {e}")
            context["__step_error__"] = f"AmoCRM универсальный поиск: {str(e)}"

    async def _handle_create_contact(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание контакта в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            name = self._resolve_value(params.get("name", ""), context)
            first_name = self._resolve_value(params.get("first_name", ""), context)
            last_name = self._resolve_value(params.get("last_name", ""), context)
            phone = self._resolve_value(params.get("phone", ""), context)
            email = self._resolve_value(params.get("email", ""), context)
            output_var = params.get("output_var", "created_contact")
            
            # Кастомные поля из параметров
            custom_fields_data = params.get("custom_fields", {})
            
            # Если custom_fields пришли как строка (из-за подстановки переменных), парсим их
            if isinstance(custom_fields_data, str):
                try:
                    import json
                    custom_fields_data = json.loads(custom_fields_data)
                except:
                    # Если не JSON, пробуем eval (осторожно!)
                    try:
                        custom_fields_data = eval(custom_fields_data)
                    except:
                        logger.warning(f"Не удалось распарсить custom_fields: {custom_fields_data}")
                        custom_fields_data = {}
            
            # Подставляем переменные в значения полей
            if isinstance(custom_fields_data, dict):
                for key, value in custom_fields_data.items():
                    custom_fields_data[key] = self._resolve_value(value, context)
            else:
                custom_fields_data = {}
            
            # Формируем данные контакта
            contact_data = {}
            
            # Имя контакта
            if name:
                contact_data["name"] = name
            elif first_name or last_name:
                contact_data["name"] = f"{first_name} {last_name}".strip()
            else:
                context[output_var] = {"success": False, "error": "Не указано имя контакта"}
                return
            
            if first_name:
                contact_data["first_name"] = first_name
            if last_name:
                contact_data["last_name"] = last_name
            
            # Подготавливаем кастомные поля
            custom_fields = []
            
            # Стандартные поля (телефон и email)
            if phone:
                custom_fields.append({
                    "field_code": "PHONE",
                    "values": [{"value": phone, "enum_code": "WORK"}]
                })
            if email:
                custom_fields.append({
                    "field_code": "EMAIL", 
                    "values": [{"value": email, "enum_code": "WORK"}]
                })
            
            # Дополнительные кастомные поля через карту полей
            if custom_fields_data and self.fields_map:
                mapped_fields = self._prepare_custom_fields(custom_fields_data)
                custom_fields.extend(mapped_fields)
            
            if custom_fields:
                contact_data["custom_fields_values"] = custom_fields
            
            # Создаем контакт
            endpoint = "/api/v4/contacts"
            result = await self._make_request("POST", endpoint, json=[contact_data])
            
            if result["success"]:
                # Проверяем что data является словарем
                data = result.get("data", {})
                if isinstance(data, dict):
                    contacts = data.get("_embedded", {}).get("contacts", [])
                    if contacts:
                        contact = contacts[0]
                        context[output_var] = {
                            "success": True,
                            "contact": contact,
                            "contact_id": contact["id"],
                            "used_fields_map": len(self.fields_map) > 0,
                            "custom_fields_count": len(custom_fields)
                        }
                        logger.info(f"✅ Контакт создан: {contact['id']} (использовано {len(custom_fields)} кастомных полей)")
                    else:
                        context[output_var] = {"success": False, "error": "Контакт не создан"}
                else:
                    context[output_var] = {
                        "success": False,
                        "error": f"Неожиданный формат ответа AmoCRM: {type(data).__name__}"
                    }
                    logger.error(f"❌ Неожиданный формат ответа AmoCRM при создании контакта: {data}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка создания контакта: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания контакта: {e}")
            context["__step_error__"] = f"AmoCRM создание контакта: {str(e)}"

    async def _handle_create_lead(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание сделки в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            name = self._resolve_value(params.get("name", ""), context)
            price = self._resolve_value(params.get("price", 0), context)
            contact_id = self._resolve_value(params.get("contact_id", ""), context)
            output_var = params.get("output_var", "created_lead")
            
            if not name:
                context[output_var] = {"success": False, "error": "Не указано название сделки"}
                return
            
            # Формируем данные сделки
            lead_data = {"name": name}
            
            if price:
                lead_data["price"] = int(price)
            
            # Привязка к контакту
            if contact_id:
                lead_data["_embedded"] = {
                    "contacts": [{"id": int(contact_id)}]
                }
            
            # Создаем сделку
            endpoint = "/api/v4/leads"
            result = await self._make_request("POST", endpoint, json=[lead_data])
            
            if result["success"]:
                # Проверяем что data является словарем
                data = result.get("data", {})
                if isinstance(data, dict):
                    leads = data.get("_embedded", {}).get("leads", [])
                    if leads:
                        lead = leads[0]
                        context[output_var] = {
                            "success": True,
                            "lead": lead,
                            "lead_id": lead["id"]
                        }
                        logger.info(f"✅ Сделка создана: {lead['id']}")
                    else:
                        context[output_var] = {"success": False, "error": "Сделка не создана"}
                else:
                    context[output_var] = {
                        "success": False,
                        "error": f"Неожиданный формат ответа AmoCRM: {type(data).__name__}"
                    }
                    logger.error(f"❌ Неожиданный формат ответа AmoCRM при создании сделки: {data}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка создания сделки: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания сделки: {e}")
            context["__step_error__"] = f"AmoCRM создание сделки: {str(e)}"

    async def _handle_update_contact(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Обновление контакта в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            contact_id = self._resolve_value(params.get("contact_id", ""), context)
            output_var = params.get("output_var", "updated_contact")
            
            if not contact_id:
                context[output_var] = {"success": False, "error": "Не указан contact_id"}
                return
            
            # Формируем данные для обновления
            contact_data = {"id": int(contact_id)}
            
            # Основные поля
            if "name" in params:
                contact_data["name"] = self._resolve_value(params["name"], context)
            
            # Кастомные поля
            custom_fields = params.get("custom_fields", {})
            used_fields_map = params.get("used_fields_map", False)
            
            if custom_fields:
                if used_fields_map and self.fields_map:
                    # Используем карту полей для преобразования
                    contact_data["custom_fields_values"] = self._prepare_custom_fields(custom_fields)
                else:
                    # Прямое указание полей
                    contact_data["custom_fields_values"] = []
                    for field_id, value in custom_fields.items():
                        if isinstance(value, dict):
                            contact_data["custom_fields_values"].append(value)
                        else:
                            contact_data["custom_fields_values"].append({
                                "field_id": int(field_id),
                                "values": [{"value": str(value)}]
                            })
            
            # Обновляем контакт
            endpoint = f"/api/v4/contacts/{contact_id}"
            result = await self._make_request("PATCH", endpoint, json=contact_data)
            
            if result["success"]:
                contact = result["data"]
                context[output_var] = {
                    "success": True,
                    "contact": contact,
                    "contact_id": contact.get("id", contact_id),
                    "updated_fields": list(custom_fields.keys()) if custom_fields else []
                }
                logger.info(f"✅ Контакт обновлен: {contact_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка обновления контакта: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления контакта: {e}")
            context["__step_error__"] = f"AmoCRM обновление контакта: {str(e)}"

    async def _handle_add_note(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Добавление заметки к сущности в AmoCRM"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            entity_type = params.get("entity_type", "leads")  # leads, contacts
            entity_id = self._resolve_value(params.get("entity_id", ""), context)
            note_text = self._resolve_value(params.get("note_text", ""), context)
            output_var = params.get("output_var", "note_result")
            
            if not entity_id or not note_text:
                context[output_var] = {"success": False, "error": "Не указаны entity_id или note_text"}
                return
            
            # Формируем данные заметки
            note_data = {
                "entity_id": int(entity_id),
                "note_type": "common",
                "params": {
                    "text": note_text
                }
            }
            
            # Добавляем заметку
            endpoint = f"/api/v4/{entity_type}/notes"
            result = await self._make_request("POST", endpoint, json=[note_data])
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "note_added": True,
                    "entity_id": entity_id,
                    "entity_type": entity_type
                }
                logger.info(f"✅ Заметка добавлена к {entity_type}:{entity_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка добавления заметки: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка добавления заметки: {e}")
            context["__step_error__"] = f"AmoCRM добавление заметки: {str(e)}"

    # === ХЕНДЛЕРЫ КАРТЫ ПОЛЕЙ ===

    async def _handle_fetch_fields(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение карты полей из AmoCRM API и сохранение в БД"""
        # Обеспечиваем актуальные настройки
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        try:
            entity_type = params.get("entity_type", "contacts")  # contacts, leads, companies
            output_var = params.get("output_var", "fields_fetched")
            
            # Получаем поля из AmoCRM
            result = await self._fetch_fields_from_amocrm(entity_type)
            
            if result["success"]:
                fields_map = result["fields_map"]
                
                # Сохраняем в БД
                save_result = await self._save_fields_to_db(fields_map, entity_type)
                
                context[output_var] = {
                    "success": True,
                    "entity_type": entity_type,
                    "fields_count": len(fields_map),
                    "fields_map": fields_map,
                    "saved_to_db": save_result.get("success", False),
                    "message": f"Получено и сохранено {len(fields_map)} полей для {entity_type}"
                }
                
                logger.info(f"✅ Карта полей {entity_type} получена и сохранена: {len(fields_map)} полей")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения карты полей: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения карты полей: {e}")
            context["__step_error__"] = f"AmoCRM получение карты полей: {str(e)}"

    async def _handle_save_fields(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Сохранение карты полей в БД"""
        params = step_data.get("params", {})
        
        try:
            fields_map = self._resolve_value(params.get("fields_map", {}), context)
            entity_type = params.get("entity_type", "contacts")
            output_var = params.get("output_var", "fields_saved")
            
            if not fields_map:
                context[output_var] = {"success": False, "error": "Не указана fields_map"}
                return
            
            # Сохраняем карту полей
            result = await self._save_fields_to_db(fields_map, entity_type)
            
            context[output_var] = result
            
            if result["success"]:
                logger.info(f"✅ Карта полей сохранена: {len(fields_map)} полей для {entity_type}")
            else:
                logger.error(f"❌ Ошибка сохранения карты полей: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения карты полей: {e}")
            context["__step_error__"] = f"AmoCRM сохранение карты полей: {str(e)}"

    async def _handle_get_fields(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение текущей карты полей из БД"""
        params = step_data.get("params", {})
        
        try:
            entity_type = params.get("entity_type", "contacts")
            output_var = params.get("output_var", "current_fields")
            
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                context[output_var] = {"success": False, "error": "MongoDB недоступен"}
                return
                
            mongo_plugin = self.engine.plugins['mongo']
            
            # Загружаем карту полей из settings (УПРОЩЕНО!)
            fields_result = await mongo_plugin._find_one("settings", {"plugin": f"simple_amocrm_fields_{entity_type}"})
            
            if fields_result and fields_result.get("success") and fields_result.get("document"):
                fields_doc = fields_result["document"]
                context[output_var] = {
                    "success": True,
                    "entity_type": entity_type,
                    "fields_map": fields_doc.get("contact_fields", {}),  # УПРОЩЕНО: contact_fields
                    "fields_count": len(fields_doc.get("contact_fields", {})),
                    "updated_at": fields_doc.get("updated_at"),
                    "message": f"Найдено {len(fields_doc.get('contact_fields', {}))} полей для {entity_type}"
                }
                logger.info(f"✅ Карта полей получена из settings: {len(fields_doc.get('contact_fields', {}))} полей для {entity_type}")
            else:
                context[output_var] = {
                    "success": False,
                    "error": f"Карта полей для {entity_type} не найдена в settings",
                    "entity_type": entity_type,
                    "fields_count": 0
                }
                logger.warning(f"⚠️ Карта полей для {entity_type} не найдена в settings")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения карты полей: {e}")
            context["__step_error__"] = f"AmoCRM получение карты полей: {str(e)}"

    def _prepare_custom_fields(self, data: Dict[str, Any]) -> list:
        """Подготавливает кастомные поля для AmoCRM API используя карту полей"""
        custom_fields = []
        
        for field_name, value in data.items():
            field = self.fields_map.get(field_name)
            if not field:
                logger.warning(f"Поле '{field_name}' не найдено в карте полей")
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
                    
            elif field_type == "multitext":
                # Email/Phone с типом
                enum_id = self._get_enum_id(field, enum_code="WORK")  # По умолчанию WORK
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

    def _get_enum_id(self, field: Dict[str, Any], value: str = None, enum_code: str = None) -> Optional[int]:
        """Получает enum_id по значению или коду"""
        enums = field.get("enums", [])
        if not enums:
            return None
            
        # Поиск по коду
        if enum_code:
            for enum in enums:
                if enum.get("enum_code") == enum_code:
                    return enum["id"]
        
        # Поиск по значению
        if value:
            for enum in enums:
                if enum.get("value") == value:
                    return enum["id"]
        
        # Возвращаем первый доступный
        return enums[0]["id"] if enums else None

    async def healthcheck(self) -> bool:
        """Проверка работоспособности AmoCRM плагина"""
        try:
            # Динамически загружаем актуальные настройки из БД
            await self._ensure_fresh_settings()
            
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

    async def _fetch_fields_from_amocrm(self, entity_type: str = "contacts") -> Dict[str, Any]:
        """Получает карту полей напрямую из AmoCRM API"""
        try:
            endpoint = f"/api/v4/{entity_type}/custom_fields"
            result = await self._make_request("GET", endpoint)
            
            if result["success"]:
                custom_fields = result["data"].get("_embedded", {}).get("custom_fields", [])
                
                # Преобразуем в удобный формат
                fields_map = {}
                for field in custom_fields:
                    # Генерируем код поля если его нет
                    field_code = field.get("code")
                    if not field_code:
                        # Создаем код из названия поля
                        field_code = field["name"].upper().replace(" ", "_").replace(".", "_")
                        # Убираем недопустимые символы
                        field_code = "".join(c for c in field_code if c.isalnum() or c == "_")
                        if not field_code:
                            field_code = f"FIELD_{field['id']}"
                    
                    fields_map[field_code] = {
                        "id": field["id"],
                        "name": field["name"],
                        "type": field["type"],
                        "code": field.get("code"),
                        "enums": field.get("enums", [])
                    }
                
                logger.info(f"✅ Получено {len(fields_map)} полей из AmoCRM для {entity_type}")
                return {"success": True, "fields_map": fields_map, "entity_type": entity_type}
            else:
                logger.error(f"❌ Ошибка получения полей из AmoCRM: {result.get('error')}")
                return {"success": False, "error": result.get("error")}
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения полей из AmoCRM: {e}")
            return {"success": False, "error": str(e)}

    async def _save_fields_to_db(self, fields_map: Dict[str, Any], entity_type: str = "contacts") -> Dict[str, Any]:
        """Сохраняет карту полей в MongoDB"""
        try:
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                return {"success": False, "error": "MongoDB недоступен"}
                
            mongo_plugin = self.engine.plugins['mongo']
            
            fields_doc = {
                "plugin": f"simple_amocrm_fields_{entity_type}",
                "plugin_name": "simple_amocrm",
                "entity_type": entity_type,
                "contact_fields": fields_map,  # УПРОЩЕНО: используем contact_fields
                "updated_at": datetime.now().isoformat()
            }
            
            # Используем upsert для обновления или создания в settings
            result = await mongo_plugin._update_one(
                "settings",  # УПРОЩЕНО: сохраняем в settings 
                {"plugin": f"simple_amocrm_fields_{entity_type}"}, 
                {"$set": fields_doc},
                upsert=True
            )
            
            if result.get("success"):
                # Обновляем карту полей в плагине если это основная карта
                if entity_type == "contacts":
                    self.fields_map = fields_map
                
                logger.info(f"✅ Карта полей AmoCRM сохранена в settings: {len(fields_map)} полей для {entity_type}")
                return {"success": True, "message": f"Карта полей сохранена ({len(fields_map)} полей для {entity_type})"}
            else:
                error_msg = result.get('error', 'неизвестная ошибка')
                logger.warning(f"⚠️ Не удалось сохранить карту полей AmoCRM в settings: {error_msg}")
                return {"success": False, "error": error_msg}
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения карты полей AmoCRM в settings: {e}")
            return {"success": False, "error": str(e)} 