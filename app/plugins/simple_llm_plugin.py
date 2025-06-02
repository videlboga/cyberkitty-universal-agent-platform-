"""
Simple LLM Plugin - Упрощённый плагин для работы с языковыми моделями

Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
- Только основные функции: отправка запросов и получение ответов
- Минимум зависимостей
- Простая обработка ошибок
- Возврат только нужного контекста
"""

import os
import json
import httpx
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

from app.core.base_plugin import BasePlugin


class SimpleLLMPlugin(BasePlugin):
    """Простой плагин для работы с LLM через OpenRouter API"""
    
    def __init__(self):
        super().__init__("simple_llm")
        
        # Настройки LLM (будут загружены из БД)
        self.api_key = None
        self.openai_api_key = None
        self.anthropic_api_key = None
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.default_model = "meta-llama/llama-3.2-3b-instruct:free"
        
        logger.info("SimpleLLMPlugin инициализирован")
    
    async def _do_initialize(self):
        """Инициализация плагина"""
        # Загружаем настройки из БД
        await self._load_settings_from_db()
            
        if self.api_key or self.openai_api_key or self.anthropic_api_key:
            logger.info(f"✅ SimpleLLMPlugin готов к работе с моделью: {self.default_model}")
        else:
            logger.warning("⚠️ SimpleLLMPlugin работает в ограниченном режиме - API ключи не найдены в БД")
            logger.info("💡 Для настройки добавьте настройки в коллекцию settings с plugin_name: 'llm'")
    
    async def _load_settings_from_db(self):
        """Загружает настройки LLM из MongoDB"""
        try:
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                logger.warning("MongoDB плагин недоступен для загрузки настроек LLM")
                return
                
            mongo_plugin = self.engine.plugins['mongo']
            
            # Пробуем найти настройки по разным вариантам plugin_name
            settings_result = None
            
            # Сначала ищем по "llm"
            settings_result = await mongo_plugin._find_one("settings", {"plugin_name": "llm"})
            
            # Если не найдено, ищем по "simple_llm"
            if not (settings_result and settings_result.get("success") and settings_result.get("document")):
                settings_result = await mongo_plugin._find_one("settings", {"plugin_name": "simple_llm"})
            
            # Если не найдено, ищем по полю "plugin"
            if not (settings_result and settings_result.get("success") and settings_result.get("document")):
                settings_result = await mongo_plugin._find_one("settings", {"plugin": "simple_llm"})
            
            logger.info(f"🔍 ОТЛАДКА settings_result: {settings_result}")
            
            if settings_result and settings_result.get("success") and settings_result.get("document"):
                settings = settings_result["document"]
                logger.info(f"🔍 ОТЛАДКА document: {settings}")
                
                # Загружаем API ключи из разных полей
                self.api_key = (settings.get("openrouter_api_key") or 
                               settings.get("api_key") or 
                               settings.get("openai_api_key"))  # Для обратной совместимости
                               
                self.openai_api_key = settings.get("openai_api_key")
                self.anthropic_api_key = settings.get("anthropic_api_key")
                self.default_model = settings.get("default_model", self.default_model)
                
                if self.api_key:
                    logger.info("✅ Настройки LLM загружены из БД - API ключ найден")
                else:
                    logger.warning("⚠️ Настройки LLM найдены в БД, но API ключ не установлен")
            else:
                logger.info("⚠️ Настройки LLM не найдены в БД")
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки настроек LLM из БД: {e}")

    async def _ensure_fresh_settings(self):
        """Обновляет настройки из БД перед каждым запросом"""
        await self._load_settings_from_db()
    
    # === МЕТОДЫ ДЛЯ НАСТРОЙКИ ЧЕРЕЗ API ===
    
    async def save_settings_to_db(self, openrouter_api_key: str = None, openai_api_key: str = None, 
                                 anthropic_api_key: str = None, default_model: str = None) -> Dict[str, Any]:
        """Сохраняет настройки LLM в MongoDB (для использования через API)"""
        try:
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                return {"success": False, "error": "MongoDB недоступен"}
                
            mongo_plugin = self.engine.plugins['mongo']
            
            settings_doc = {
                "plugin_name": "llm",
                "plugin": "simple_llm",  # Добавляем для совместимости
                "openrouter_api_key": openrouter_api_key,
                "api_key": openrouter_api_key,  # Дублируем для совместимости  
                "openai_api_key": openai_api_key,
                "anthropic_api_key": anthropic_api_key,
                "default_model": default_model or self.default_model,
                "updated_at": datetime.now().isoformat()
            }
            
            # Используем upsert для обновления или создания в коллекции settings
            result = await mongo_plugin._update_one(
                "settings", 
                {"plugin_name": "llm"}, 
                {"$set": settings_doc},
                upsert=True
            )
            
            if result.get("success"):
                # Обновляем настройки в плагине
                if openrouter_api_key:
                    self.api_key = openrouter_api_key
                if openai_api_key:
                    self.openai_api_key = openai_api_key
                if anthropic_api_key:
                    self.anthropic_api_key = anthropic_api_key
                if default_model:
                    self.default_model = default_model
                
                logger.info("✅ Настройки LLM сохранены в БД и применены")
                return {"success": True, "message": "Настройки сохранены"}
            else:
                error_msg = result.get('error', 'неизвестная ошибка')
                logger.warning(f"⚠️ Не удалось сохранить настройки LLM в БД: {error_msg}")
                return {"success": False, "error": error_msg}
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения настроек LLM в БД: {e}")
            return {"success": False, "error": str(e)}
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Возвращает текущие настройки плагина"""
        return {
            "openrouter_api_key": "***" if self.api_key else None,
            "openai_api_key": "***" if self.openai_api_key else None,
            "anthropic_api_key": "***" if self.anthropic_api_key else None,
            "default_model": self.default_model,
            "any_key_set": bool(self.api_key or self.openai_api_key or self.anthropic_api_key),
            "configured": bool(self.api_key or self.openai_api_key or self.anthropic_api_key)
        }

    def register_handlers(self) -> Dict[str, Any]:
        """Регистрация обработчиков шагов"""
        return {
            "llm_query": self._handle_llm_query,
            "llm_chat": self._handle_llm_chat,
            "build_prompt": self._handle_build_prompt  # Универсальный конструктор промптов
        }
    
    async def _handle_llm_query(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага llm_query - простой запрос к LLM
        
        Параметры:
        - prompt: текст запроса (обязательно)
        - model: модель (опционально, по умолчанию из env)
        - system_prompt: системный промпт (опционально)
        - temperature: температура (опционально, по умолчанию 0.7)
        - max_tokens: максимум токенов (опционально, по умолчанию 500)
        - output_var: переменная для сохранения ответа (по умолчанию "llm_response")
        """
        # Загружаем свежие настройки из БД
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        # Извлекаем параметры с подстановкой из контекста
        prompt = self._resolve_value(params.get("prompt", ""), context)
        model = params.get("model", self.default_model)
        system_prompt = self._resolve_value(params.get("system_prompt", ""), context)
        temperature = params.get("temperature", 0.7)
        max_tokens = params.get("max_tokens", 500)
        output_var = params.get("output_var", "llm_response")
        
        if not prompt:
            logger.error("SimpleLLMPlugin: prompt не указан")
            context[output_var] = {"error": "Prompt не указан"}
            return context
        
        # Выполняем запрос
        response = await self._make_llm_request(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Сохраняем только нужную часть ответа в контекст
        if response.get("success"):
            context[output_var] = response["content"]
            logger.info(f"LLM ответ сохранён в {output_var}: {response['content'][:100]}...")
        else:
            context[output_var] = {"error": response.get("error", "Неизвестная ошибка")}
            logger.error(f"Ошибка LLM: {response.get('error')}")
        
        return context
    
    async def _handle_llm_chat(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага llm_chat - чат с историей сообщений
        
        Параметры:
        - messages: список сообщений [{"role": "user/assistant", "content": "..."}]
        - model: модель (опционально)
        - temperature: температура (опционально)
        - max_tokens: максимум токенов (опционально)
        - output_var: переменная для сохранения ответа (по умолчанию "llm_response")
        """
        # Загружаем свежие настройки из БД
        await self._ensure_fresh_settings()
        
        params = step_data.get("params", {})
        
        messages = params.get("messages", [])
        model = params.get("model", self.default_model)
        temperature = params.get("temperature", 0.7)
        max_tokens = params.get("max_tokens", 500)
        output_var = params.get("output_var", "llm_response")
        
        if not messages:
            logger.error("SimpleLLMPlugin: messages не указаны")
            context[output_var] = {"error": "Messages не указаны"}
            return context
        
        # Разрешаем плейсхолдеры в сообщениях
        resolved_messages = []
        for msg in messages:
            resolved_msg = {
                "role": msg.get("role", "user"),
                "content": self._resolve_value(msg.get("content", ""), context)
            }
            resolved_messages.append(resolved_msg)
        
        # Выполняем запрос
        response = await self._make_llm_request(
            messages=resolved_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Сохраняем ответ
        if response.get("success"):
            context[output_var] = response["content"]
            logger.info(f"LLM чат ответ сохранён в {output_var}")
        else:
            context[output_var] = {"error": response.get("error", "Неизвестная ошибка")}
            logger.error(f"Ошибка LLM чата: {response.get('error')}")
        
        return context
    
    async def _handle_build_prompt(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Универсальный обработчик для конструирования промптов из шаблонов и данных.
        
        Параметры:
        - template: шаблон промпта с плейсхолдерами (обязательно)
        - variables: словарь переменных для подстановки (опционально)
        - format_type: тип форматирования ("simple", "json", "list") (опционально)
        - output_var: переменная для сохранения результата (по умолчанию "built_prompt")
        
        Пример:
        {
            "type": "build_prompt",
            "params": {
                "template": "Проанализируй данные пользователя:\nИмя: {name}\nОтветы: {answers}",
                "variables": {
                    "name": "{user_profile.name}",
                    "answers": "{diagnosis_answers}"
                },
                "format_type": "simple",
                "output_var": "analysis_prompt"
            }
        }
        """
        params = step_data.get("params", {})
        
        # Извлекаем параметры
        template = params.get("template", "")
        variables = params.get("variables", {})
        format_type = params.get("format_type", "simple")
        output_var = params.get("output_var", "built_prompt")
        
        if not template:
            logger.error("build_prompt: template не указан")
            context[output_var] = {"error": "Template не указан"}
            return context
        
        try:
            # Подставляем переменные из контекста
            resolved_variables = {}
            for key, value in variables.items():
                resolved_variables[key] = self._resolve_value(value, context)
            
            # Конструируем промпт в зависимости от типа
            if format_type == "json":
                # JSON формат с правильными кавычками
                built_prompt = template.format(**{
                    k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
                    for k, v in resolved_variables.items()
                })
            elif format_type == "list":
                # Список формат
                built_prompt = template.format(**{
                    k: '\n'.join([f"- {item}" for item in v]) if isinstance(v, list) else str(v)
                    for k, v in resolved_variables.items()
                })
            else:  # simple
                # Простая подстановка строк
                built_prompt = template.format(**{
                    k: str(v) for k, v in resolved_variables.items()
                })
            
            # Сохраняем результат
            context[output_var] = {
                "success": True,
                "template": template,
                "variables": resolved_variables,
                "built_prompt": built_prompt,
                "format_type": format_type
            }
            
            logger.info(f"✅ Промпт построен успешно: {len(built_prompt)} символов")
            
        except Exception as e:
            logger.error(f"❌ Ошибка конструирования промпта: {e}")
            context[output_var] = {
                "success": False,
                "error": str(e),
                "template": template,
                "variables": variables
            }
        
        return context
    
    async def _make_llm_request(self, prompt: str = None, messages: list = None, 
                               model: str = None, system_prompt: str = None,
                               temperature: float = 0.7, max_tokens: int = 500) -> Dict[str, Any]:
        """Выполнение HTTP запроса к LLM API"""
        
        # Выбираем подходящий API ключ
        api_key = self.api_key or self.openai_api_key or self.anthropic_api_key
        
        logger.info(f"🔍 ОТЛАДКА API ключей: api_key={'***' if self.api_key else None}, openai_api_key={'***' if self.openai_api_key else None}, anthropic_api_key={'***' if self.anthropic_api_key else None}")
        logger.info(f"🔍 ОТЛАДКА выбранный api_key: {'***' + api_key[-10:] if api_key and len(api_key) > 10 else api_key}")
        
        if not api_key:
            return {"success": False, "error": "API ключ не настроен"}
        
        # Формируем сообщения
        if messages:
            request_messages = messages
        elif prompt:
            request_messages = []
            if system_prompt:
                request_messages.append({"role": "system", "content": system_prompt})
            request_messages.append({"role": "user", "content": prompt})
        else:
            return {"success": False, "error": "Не указан prompt или messages"}
        
        # Формируем payload
        payload = {
            "model": model or self.default_model,
            "messages": request_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        logger.info(f"🔍 ОТЛАДКА payload: model={payload['model']}, messages_count={len(request_messages)}")
        
        # Выполняем HTTP запрос
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://universal-agent-platform.local",
                    "X-Title": "Universal Agent Platform"
                }
                
                logger.info(f"🔍 ОТЛАДКА headers Authorization: {'Bearer ' + api_key[:20] + '***' if api_key else 'None'}")
                
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                logger.info(f"🔍 ОТЛАДКА response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Извлекаем только текст ответа
                    if data.get("choices") and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"]
                        return {"success": True, "content": content}
                    else:
                        return {"success": False, "error": "Пустой ответ от API"}
                else:
                    error_text = response.text
                    logger.error(f"LLM API ошибка {response.status_code}: {error_text}")
                    return {"success": False, "error": f"API ошибка {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Ошибка запроса к LLM: {e}")
            return {"success": False, "error": str(e)}
    
    def _resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Простая подстановка значений из контекста"""
        if isinstance(value, str) and "{" in value and "}" in value:
            try:
                return value.format(**context)
            except (KeyError, ValueError) as e:
                logger.warning(f"Не удалось разрешить '{value}': {e}")
                return value
        return value
    
    async def healthcheck(self) -> bool:
        """Проверка здоровья плагина"""
        if not self.api_key:
            return False
        
        try:
            # Простой тестовый запрос
            response = await self._make_llm_request(
                prompt="test",
                max_tokens=1
            )
            return response.get("success", False)
        except Exception:
            return False 