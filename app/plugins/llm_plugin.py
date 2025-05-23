import os
import json
import httpx
from typing import Dict, Any, List, Optional, Union
from loguru import logger
from app.plugins.plugin_base import PluginBase
from app.integrations.openrouter import openrouter_chat
from app.core.utils import _resolve_value_from_context

# Вспомогательная функция для рекурсивного разрешения плейсхолдеров
def _resolve_placeholders_in_structure_recursive(item: Any, context: Dict[str, Any]) -> Any:
    if isinstance(item, dict):
        return {k: _resolve_placeholders_in_structure_recursive(v, context) for k, v in item.items()}
    elif isinstance(item, list):
        return [_resolve_placeholders_in_structure_recursive(elem, context) for elem in item]
    elif isinstance(item, str):
        return _resolve_value_from_context(item, context)
    else:
        return item

class LLMPlugin(PluginBase):
    """
    Плагин для интеграции с языковыми моделями через OpenRouter.
    
    Позволяет выполнять запросы к различным LLM через единый интерфейс.
    Поддерживает:
    - Обработку пользовательских запросов
    - Системные промпты
    - Кастомизацию параметров модели
    - Запросы к различным моделям (OpenAI, DeepSeek, Claude и др.)
    - История сообщений (memory)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация плагина
        
        Args:
            config: Конфигурация плагина (API ключи, URL и др.)
        """
        super().__init__()
        self.api_key = (config.get('api_key') if config else None) or os.getenv("OPENROUTER_API_KEY", "")
        self.api_url = (config.get('api_url') if config else None) or os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.default_model = (config.get('default_model') if config else None) or "deepseek/deepseek-chat-v3-0324"
        
        # Проверка наличия API ключа при инициализации
        if not self.api_key:
            logger.warning("LLMPlugin: OPENROUTER_API_KEY не найден. Запросы к OpenRouter будут невозможны.")
        else:
            logger.info(f"LLMPlugin инициализирован с API ключом: {self.api_key[:5]}...{self.api_key[-5:] if len(self.api_key) > 10 else ''}")
        logger.info(f"LLMPlugin: Модель по умолчанию: {self.default_model}")
    
    async def query(self, 
                   prompt: Optional[str] = None, 
                   model: Optional[str] = None, 
                   system_prompt: Optional[str] = None,
                   messages: Optional[List[Dict[str, str]]] = None,
                   temperature: float = 0.7,
                   max_tokens: int = 500,
                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Отправка запроса к LLM-модели
        
        Args:
            prompt: Текст запроса
            model: Модель для запроса (например, "openai/gpt-3.5-turbo")
            system_prompt: Системный промпт (для GPT и подобных моделей)
            messages: История сообщений (для контекста)
            temperature: Температура генерации (0-1)
            max_tokens: Максимальное количество токенов в ответе
            context: Дополнительный контекст для запроса
            
        Returns:
            Dict: Ответ от модели
        """
        if not self.api_key:
            logger.error("LLMPlugin.query: Отсутствует OPENROUTER_API_KEY. Невозможно выполнить запрос.")
            return {"status": "error", "message": "API key for OpenRouter is missing."}

        actual_model = model or self.default_model
        if not actual_model:
            logger.error("LLMPlugin.query: Модель не указана и default_model не установлен.")
            return {"status": "error", "message": "LLM model not specified."}
            
        logger.info(f"LLMPlugin.query: Запрос к модели \'{actual_model}\'.")
        
        request_payload = {
            "model": actual_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if messages:
            request_payload["messages"] = messages
            if prompt:
                 logger.warning("LLMPlugin.query: Переданы и \'messages\', и \'prompt\'. \'prompt\' будет проигнорирован.")
        elif prompt:
            payload_messages = []
            if system_prompt:
                payload_messages.append({"role": "system", "content": system_prompt})
            payload_messages.append({"role": "user", "content": prompt})
            request_payload["messages"] = payload_messages
        else:
            logger.error("LLMPlugin.query: Необходимо предоставить либо \'messages\', либо \'prompt\'.")
            return {"status": "error", "message": "Either \'messages\' or \'prompt\' must be provided."}

        try:
            logger.debug(f"LLMPlugin.query: Payload для OpenRouter: {json.dumps(request_payload, ensure_ascii=False)}")
            
            # ===== ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ ПЕРЕД ВЫЗОВОМ OPENROUTER_CHAT =====
            logger.info(f"[LLMPlugin.query - PRE-CALL DEBUG] Готовлюсь вызвать openrouter_chat. API Key: {self.api_key[:5]}...{self.api_key[-5:] if len(self.api_key) > 10 else ''}")
            logger.info(f"[LLMPlugin.query - PRE-CALL DEBUG] Actual Model: {actual_model}")
            logger.info(f"[LLMPlugin.query - PRE-CALL DEBUG] Full Request Payload to be sent to openrouter_chat:")
            logger.info(json.dumps(request_payload, indent=2, ensure_ascii=False))
            # ===== КОНЕЦ ДЕТАЛЬНОГО ЛОГИРОВАНИЯ =====

            api_response = await openrouter_chat(
                prompt=None,
                model=actual_model, 
                messages=request_payload["messages"],
                temperature=temperature,
                max_tokens=max_tokens
            )

            if "error" in api_response:
                logger.error(f"LLMPlugin.query: Ошибка от openrouter_chat: {api_response['error']}")
                return {"status": "error", "message": str(api_response["error"]), "details": api_response}
            
            response_content_sample = ""
            if api_response.get("choices") and isinstance(api_response["choices"], list) and len(api_response["choices"]) > 0:
                first_choice = api_response["choices"][0]
                if isinstance(first_choice, dict) and first_choice.get("message") and isinstance(first_choice["message"], dict):
                    response_content_sample = str(first_choice["message"].get("content", ""))[:100]
            
            logger.info(f"LLMPlugin.query: Успешный ответ от модели \'{actual_model}\'. Пример ответа: \'{response_content_sample}...\'")
            
            return {"status": "ok", "response": api_response} 

        except httpx.HTTPStatusError as e:
            error_body = e.response.text
            logger.error(f"LLMPlugin.query: HTTPStatusError при запросе к OpenRouter: {e}. Response: {error_body}")
            return {"status": "error", "message": f"OpenRouter API request failed with status {e.response.status_code}", "details": error_body}
        except Exception as e:
            logger.opt(exception=True).error(f"LLMPlugin.query: Неожиданная ошибка при запросе к OpenRouter: {e}")
            return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}
    
    async def on_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка события для плагина
        
        Args:
            event: Данные события с параметрами запроса
            
        Returns:
            Dict: Результат обработки
        """
        prompt = event.get("prompt", "")
        if not prompt:
            return {"status": "error", "error": "No prompt provided"}
        
        # Извлекаем параметры запроса
        model = event.get("model")
        system_prompt = event.get("system_prompt")
        messages = event.get("messages")
        temperature = event.get("temperature", 0.7)
        max_tokens = event.get("max_tokens", 500)
        context = event.get("context")
        
        # Выполняем запрос
        return await self.query(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            context=context
        )
    
    async def handle_llm_query(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Обработчик шага типа llm_query - отправка запроса к LLM
        
        Args:
            step_data: Данные шага (prompt, model, system_prompt и т.д.)
            context: Контекст сценария
            
        Returns:
            Результат LLM запроса (обычно словарь) или None в случае ошибки конфигурации шага.
        """
        params = step_data.get("params", {})
        scenario_id = context.get("__current_scenario_id__", "unknown_scenario")
        step_id = step_data.get("id", "unknown_llm_step")
        logger.info(f"[LLMPlugin.handle_llm_query SCENARIO_ID:{scenario_id} STEP_ID:{step_id}] Processing step.")
        logger.debug(f"Step_data.params: {json.dumps(params, ensure_ascii=False, default=str)}")
        logger.debug(f"Context before resolving: {json.dumps(context, ensure_ascii=False, default=str)}")

        resolved_params = _resolve_placeholders_in_structure_recursive(params, context)
        logger.debug(f"Resolved step_data.params: {json.dumps(resolved_params, ensure_ascii=False, default=str)}")
        
        prompt_from_params = resolved_params.get("prompt")
        messages_from_params = resolved_params.get("messages")
        
        model = resolved_params.get("model")
        if not model:
            model_from_context = context.get("llm_model")
            if model_from_context:
                model = model_from_context
                logger.info(f"Модель взята из контекста: {model}")

        system_prompt = resolved_params.get("system_prompt")
        temperature = resolved_params.get("temperature", 0.7)
        max_tokens = resolved_params.get("max_tokens", 500)
        output_var = params.get("output_var", "llm_result")

        if not messages_from_params and not prompt_from_params:
            logger.error(f"[LLMPlugin.handle_llm_query SCENARIO_ID:{scenario_id} STEP_ID:{step_id}] Ошибка: В параметрах шага llm_query должны быть указаны 'messages' или 'prompt'.")
            context["__step_error__"] = f"LLMPlugin: Шаг {step_id} не содержит 'messages' или 'prompt'."
            return None

        api_result_envelope = await self.query(
            prompt=prompt_from_params,
            model=model,
            system_prompt=system_prompt,
            messages=messages_from_params,
            temperature=temperature,
            max_tokens=max_tokens,
            context=context
        )
        
        if api_result_envelope.get("status") == "ok":
            logger.info(f"[LLMPlugin.handle_llm_query SCENARIO_ID:{scenario_id} STEP_ID:{step_id}] Запрос к LLM успешно обработан плагином.")
            return api_result_envelope.get("response")
        else:
            error_msg = api_result_envelope.get("message", "Неизвестная ошибка от LLMPlugin.query")
            logger.error(f"[LLMPlugin.handle_llm_query SCENARIO_ID:{scenario_id} STEP_ID:{step_id}] Ошибка при выполнении LLM запроса: {error_msg}")
            context["__step_error__"] = f"LLMPlugin: {error_msg}"
            return None

    def register_step_handlers(self, step_handlers: Dict[str, Any]):
        """
        Регистрация обработчиков шагов в step_handlers
        
        Args:
            step_handlers: Словарь обработчиков шагов сценария
        """
        step_handlers["llm_query"] = self.handle_llm_query
        logger.info("LLMPlugin: Зарегистрирован обработчик шага llm_query.")
    
    def healthcheck(self) -> bool:
        """
        Проверка работоспособности плагина
        
        Returns:
            bool: True, если плагин работоспособен
        """
        is_healthy = bool(self.api_key)
        logger.info(f"LLMPlugin healthcheck: {'OK' if is_healthy else 'FAIL (API key missing)'}")
        return is_healthy

    def get_default_config(self) -> Dict[str, Any]:
        return {
            "api_key": "YOUR_OPENROUTER_API_KEY",
            "api_url": "https://openrouter.ai/api/v1/chat/completions",
            "default_model": "deepseek/deepseek-chat-v3-0324"
        }

    def get_config_description(self) -> Dict[str, str]:
        return {
            "api_key": "API ключ для OpenRouter.ai.",
            "api_url": "URL для OpenRouter API (по умолчанию: https://openrouter.ai/api/v1/chat/completions).",
            "default_model": "Модель по умолчанию для использования, если не указана в шаге сценария."
        } 