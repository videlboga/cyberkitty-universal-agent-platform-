"""
AmoCRM Plugin Extensions - Расширенные методы для полного покрытия API

Этот файл содержит дополнительные обработчики для AmoCRM плагина,
которые покрывают все методы официального API.
"""

from typing import Dict, Any
from loguru import logger


class AmoCRMExtensions:
    """Расширения для AmoCRM плагина"""
    
    # === ОБРАБОТЧИКИ СДЕЛОК ===
    
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
            
            result = await self._update_lead(lead_id, update_data)
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

    # === ОБРАБОТЧИКИ КОМПАНИЙ ===
    
    async def _handle_create_company(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Создание компании в AmoCRM"""
        params = step_data.get("params", {})
        
        try:
            name = self._resolve_value(params.get("name", ""), context)
            custom_fields_data = params.get("custom_fields", {})
            output_var = params.get("output_var", "created_company")
            
            # Разрешаем переменные в кастомных полях
            for key, value in custom_fields_data.items():
                custom_fields_data[key] = self._resolve_value(value, context)
            
            if not name:
                context[output_var] = {"success": False, "error": "Не указано название компании"}
                return
            
            result = await self._create_company(name, custom_fields_data)
            context[output_var] = result
            
            if result.get("success"):
                logger.info(f"✅ Компания создана: {result.get('company', {}).get('id')}")
            else:
                logger.error(f"❌ Ошибка создания компании: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка создания компании: {e}")
            context["__step_error__"] = f"AmoCRM создание компании: {str(e)}"

    async def _handle_update_company(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Обновление компании"""
        params = step_data.get("params", {})
        
        try:
            company_id = self._resolve_value(params.get("company_id", ""), context)
            update_data = params.get("update_data", {})
            output_var = params.get("output_var", "updated_company")
            
            # Разрешаем переменные
            for key, value in update_data.items():
                update_data[key] = self._resolve_value(value, context)
            
            if not company_id:
                context[output_var] = {"success": False, "error": "Не указан company_id"}
                return
            
            result = await self._update_company(company_id, update_data)
            context[output_var] = result
            
            if result.get("success"):
                logger.info(f"✅ Компания обновлена: {company_id}")
            else:
                logger.error(f"❌ Ошибка обновления компании: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления компании: {e}")
            context["__step_error__"] = f"AmoCRM обновление компании: {str(e)}"

    async def _handle_delete_company(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Удаление компании"""
        params = step_data.get("params", {})
        
        try:
            company_id = self._resolve_value(params.get("company_id", ""), context)
            output_var = params.get("output_var", "delete_result")
            
            if not company_id:
                context[output_var] = {"success": False, "error": "Не указан company_id"}
                return
            
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
                logger.error(f"❌ Ошибка удаления компании {company_id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка удаления компании: {e}")
            context["__step_error__"] = f"AmoCRM удаление компании: {str(e)}"

    async def _handle_get_company(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение компании по ID"""
        params = step_data.get("params", {})
        
        try:
            company_id = self._resolve_value(params.get("company_id", ""), context)
            output_var = params.get("output_var", "company")
            with_fields = params.get("with", [])
            
            if not company_id:
                context[output_var] = {"success": False, "error": "Не указан company_id"}
                return
            
            query_params = {}
            if with_fields:
                query_params["with"] = ",".join(with_fields)
            
            endpoint = f"/api/v4/companies/{company_id}"
            result = await self._make_request("GET", endpoint, params=query_params)
            
            if result["success"]:
                context[output_var] = {
                    "success": True,
                    "company": result["data"]
                }
                logger.info(f"✅ Компания получена: {company_id}")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения компании {company_id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения компании: {e}")
            context["__step_error__"] = f"AmoCRM получение компании: {str(e)}"

    async def _handle_list_companies(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Получение списка компаний"""
        params = step_data.get("params", {})
        
        try:
            output_var = params.get("output_var", "companies")
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
            
            endpoint = "/api/v4/companies"
            result = await self._make_request("GET", endpoint, params=query_params)
            
            if result["success"]:
                companies = result["data"].get("_embedded", {}).get("companies", [])
                context[output_var] = {
                    "success": True,
                    "companies": companies,
                    "count": len(companies),
                    "page_info": result["data"].get("_page", {})
                }
                logger.info(f"✅ Получен список компаний: {len(companies)} шт.")
            else:
                context[output_var] = result
                logger.error(f"❌ Ошибка получения списка компаний: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка компаний: {e}")
            context["__step_error__"] = f"AmoCRM список компаний: {str(e)}"

    async def _handle_find_company(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Поиск компании"""
        params = step_data.get("params", {})
        
        try:
            query = self._resolve_value(params.get("query", ""), context)
            output_var = params.get("output_var", "company_search")
            
            if not query:
                context[output_var] = {"success": False, "error": "Не указан поисковый запрос"}
                return
            
            result = await self._search_companies(query)
            context[output_var] = result
            
            if result.get("success"):
                count = result.get("count", 0)
                logger.info(f"✅ Поиск компаний выполнен: найдено {count} результатов")
            else:
                logger.warning(f"⚠️ Поиск компаний не дал результатов: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска компаний: {e}")
            context["__step_error__"] = f"AmoCRM поиск компаний: {str(e)}"

    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===
    
    async def _update_lead(self, lead_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
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

    async def _create_company(self, name: str, custom_fields: Dict[str, Any] = None) -> Dict[str, Any]:
        """Создание новой компании"""
        company_data = {"name": name}
        
        # Кастомные поля
        if custom_fields:
            company_data["custom_fields_values"] = self._prepare_custom_fields(custom_fields)
        
        endpoint = "/api/v4/companies"
        payload = [company_data]
        
        result = await self._make_request("POST", endpoint, json=payload)
        
        if result["success"] and result["data"].get("_embedded", {}).get("companies"):
            company = result["data"]["_embedded"]["companies"][0]
            return {
                "success": True,
                "company": company,
                "company_id": company["id"]
            }
        
        return {"success": False, "error": result.get("error", "Ошибка создания компании")}

    async def _update_company(self, company_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление существующей компании"""
        company_data = {"id": company_id}
        
        # Основные поля
        for field in ["name", "responsible_user_id"]:
            if field in update_data:
                company_data[field] = update_data[field]
        
        # Кастомные поля
        custom_fields = {k: v for k, v in update_data.items() 
                        if k not in ["name", "responsible_user_id"]}
        if custom_fields:
            company_data["custom_fields_values"] = self._prepare_custom_fields(custom_fields)
        
        endpoint = "/api/v4/companies"
        payload = [company_data]
        
        result = await self._make_request("PATCH", endpoint, json=payload)
        
        if result["success"]:
            return {
                "success": True,
                "company_id": company_id,
                "updated": True
            }
        
        return {"success": False, "error": result.get("error", "Ошибка обновления компании")} 