import os
import json
import httpx
from typing import Dict, Any, List, Optional
from loguru import logger
from app.plugins.plugin import PluginBase
from app.integrations.openrouter import openrouter_chat

# Настройка логирования
os.makedirs("logs", exist_ok=True)
logger.add("logs/llm_plugin.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

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
        super().__init__(config or {})
        self.api_key = (config.get('api_key') if config else None) or os.getenv("OPENROUTER_API_KEY", "")
        self.api_url = (config.get('api_url') if config else None) or os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.default_model = (config.get('default_model') if config else None) or "deepseek/deepseek-chat-v3-0324"
        
        logger.info(f"LLMPlugin инициализирован. Модель по умолчанию: {self.default_model}")
    
    async def query(self, 
                   prompt: str, 
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
        try:
            # Формируем сообщения для запроса
            formatted_messages = []
            
            # Добавляем системный промпт, если он есть
            if system_prompt:
                formatted_messages.append({"role": "system", "content": system_prompt})
            
            # Добавляем историю сообщений, если она есть
            if messages:
                formatted_messages.extend(messages)
            
            # Добавляем текущий запрос
            formatted_messages.append({"role": "user", "content": prompt})
            
            # Используем выбранную модель или модель по умолчанию
            selected_model = model
            if not selected_model and context and isinstance(context, dict):
                selected_model = context.get("model")
            if not selected_model:
                selected_model = self.default_model
            
            # Логируем выбранную модель
            logger.info(f"LLMPlugin: выбранная модель для запроса: {selected_model}")
            
            # Формируем параметры запроса
            params = {
                "model": selected_model,
                "messages": formatted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Логируем запрос
            logger.info(f"LLM запрос: модель={selected_model}, длина промпта={len(prompt)}")
            
            # Отправляем запрос через OpenRouter
            result = await openrouter_chat(prompt, model=selected_model, messages=formatted_messages, 
                                         temperature=temperature, max_tokens=max_tokens)
            
            # Извлекаем текстовый ответ
            response_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Формируем результат
            response = {
                "status": "ok",
                "response": response_content,
                "model": selected_model,
                "raw_response": result
            }
            
            # Логируем успешный ответ
            logger.info(f"LLM ответ: модель={selected_model}, длина ответа={len(response_content)}")
            
            return response
            
        except Exception as e:
            # Логируем ошибку
            logger.error(f"Ошибка LLM запроса: {str(e)}")
            
            # Возвращаем ошибку
            return {
                "status": "error",
                "error": str(e),
                "model": model or self.default_model
            }
    
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
    
    async def handle_llm_query(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработчик шага типа llm_query - отправка запроса к LLM
        
        Args:
            step_data: Данные шага (prompt, model, system_prompt и т.д.)
            context: Контекст сценария
            
        Returns:
            Dict: Обновленный контекст с результатом запроса
        """
        # Извлекаем параметры из данных шага
        prompt = step_data.get("prompt", "")
        
        # Подстановка переменных из контекста в промпт
        if isinstance(prompt, str) and "{" in prompt and "}" in prompt:
            for key, value in context.items():
                placeholder = "{" + key + "}"
                if placeholder in prompt:
                    prompt = prompt.replace(placeholder, str(value))
        
        # Извлекаем остальные параметры
        model = step_data.get("model")
        if not model and context and isinstance(context, dict):
            model = context.get("model")
        logger.info(f"handle_llm_query: выбранная модель: {model if model else self.default_model}")
        system_prompt = step_data.get("system_prompt")
        messages = step_data.get("messages")
        temperature = step_data.get("temperature", 0.7)
        max_tokens = step_data.get("max_tokens", 500)
        output_var = step_data.get("output_var", "llm_result")
        
        # Выполняем запрос
        result = await self.query(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            context=context
        )
        
        # Сохраняем результат в контексте
        context[output_var] = result
        
        # Если указано сохранять только текстовый ответ
        if step_data.get("save_text_only", False) and result.get("status") == "ok":
            context[output_var + "_text"] = result.get("response", "")
        
        return context
    
    def register_step_handlers(self, step_handlers: Dict[str, Any]):
        """
        Регистрация обработчиков шагов в step_handlers
        
        Args:
            step_handlers: Словарь обработчиков шагов сценария
        """
        step_handlers["llm_query"] = self.handle_llm_query
        logger.info("Зарегистрирован обработчик шага llm_query")
    
    def healthcheck(self) -> bool:
        """
        Проверка работоспособности плагина
        
        Returns:
            bool: True, если плагин работоспособен
        """
        return self.api_key != "" 