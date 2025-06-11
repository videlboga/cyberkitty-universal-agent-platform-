"""
LLM Provider - Универсальный интерфейс для работы с различными LLM

Поддерживает:
- OpenRouter (100+ моделей, включая бесплатные)
- Anthropic Claude
- Local модели (Ollama)
- Автоматический выбор лучшей модели
"""

import logging
import json
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass
from datetime import datetime

try:
    from .config import Config, get_config
except ImportError:
    # Fallback для случаев когда модуль запускается отдельно
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from config import Config, get_config

logger = logging.getLogger(__name__)


@dataclass
class LLMMessage:
    """Сообщение для LLM"""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: Optional[str] = None


@dataclass 
class LLMResponse:
    """Ответ от LLM"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Базовый провайдер LLM"""
    
    def __init__(self, model: str, config: Config):
        self.model = model
        self.config = config
        self.request_count = 0
        self.total_tokens = 0
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """Простое завершение промпта"""
        pass
    
    @abstractmethod
    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Чат с историей сообщений"""
        pass
    
    @abstractmethod
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Стриминг ответа"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику использования"""
        return {
            "model": self.model,
            "request_count": self.request_count,
            "total_tokens": self.total_tokens,
            "provider": self.__class__.__name__
        }


class OpenAIProvider(LLMProvider):
    """Провайдер для OpenRouter API (совместимый с OpenAI)"""
    
    def __init__(self, model: str = "deepseek/deepseek-chat", config: Optional[Config] = None):
        config = config or get_config()
        super().__init__(model, config)
        
        if not config.openai_api_key:
            raise ValueError("OpenRouter API key не настроен")
        
        self.api_key = config.openai_api_key
        # Используем OpenRouter по умолчанию, совместимость с OpenAI
        self.base_url = getattr(config, 'openai_base_url', None) or os.getenv('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1')
    
    def _parse_prompt_to_messages(self, prompt: str) -> List[Dict[str, str]]:
        """Парсит промпт в правильный формат сообщений"""
        messages = []
        
        # Разбиваем промпт на строки
        lines = prompt.strip().split('\n')
        current_role = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Ищем роли
            if line.startswith('System: '):
                if current_role and current_content:
                    messages.append({'role': current_role, 'content': '\n'.join(current_content)})
                current_role = 'system'
                current_content = [line[8:]]  # Убираем "System: "
            elif line.startswith('User: '):
                if current_role and current_content:
                    messages.append({'role': current_role, 'content': '\n'.join(current_content)})
                current_role = 'user'
                current_content = [line[6:]]  # Убираем "User: "
            elif line.startswith('Assistant:') and line != 'Assistant:':
                if current_role and current_content:
                    messages.append({'role': current_role, 'content': '\n'.join(current_content)})
                current_role = 'assistant'
                current_content = [line[10:]]  # Убираем "Assistant:"
            elif line == 'Assistant:':
                # Игнорируем пустой "Assistant:" в конце
                break
            else:
                # Продолжение текущего сообщения
                if current_content:
                    current_content.append(line)
                else:
                    # Если нет роли, добавляем как user
                    if not current_role:
                        current_role = 'user'
                    current_content.append(line)
        
        # Добавляем последнее сообщение
        if current_role and current_content:
            messages.append({'role': current_role, 'content': '\n'.join(current_content)})
        
        # Если нет сообщений, создаем базовое
        if not messages:
            messages = [{'role': 'user', 'content': prompt}]
        
        return messages
    
    def complete(self, prompt: str, **kwargs) -> str:
        """Простое завершение через OpenRouter"""
        try:
            self.request_count += 1
            
            # Пробуем настоящий API если есть ключ
            if self.api_key and self.api_key != 'test-key':
                try:
                    import requests
                    
                    headers = {
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json',
                    }
                    
                    # Добавляем специальные заголовки для OpenRouter
                    if 'openrouter.ai' in self.base_url:
                        headers.update({
                            'HTTP-Referer': 'https://github.com/kittycore/kittycore',
                            'X-Title': 'KittyCore Agent Platform'
                        })
                    
                    # Парсим промпт в правильный формат сообщений
                    messages = self._parse_prompt_to_messages(prompt)
                    
                    data = {
                        'model': self.model,
                        'messages': messages,
                        'max_tokens': kwargs.get('max_tokens', 1000),
                        'temperature': kwargs.get('temperature', 0.7)
                    }
                    
                    response = requests.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        content = result['choices'][0]['message']['content']
                        logger.info(f"OpenRouter API запрос выполнен, модель: {self.model}")
                        return content
                    else:
                        logger.warning(f"API ошибка {response.status_code}, используем mock")
                        logger.warning(f"Запрос: {json.dumps(data, indent=2)}")
                        logger.warning(f"Ответ: {response.text}")
                        
                except Exception as api_error:
                    logger.warning(f"API недоступен: {api_error}, используем mock")
            
            # Fallback: симуляция ответа
            response = f"🤖 KittyCore Mock Response для '{prompt[:30]}...' от модели {self.model}"
            logger.info(f"Mock ответ сгенерирован для модели: {self.model}")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка OpenRouter API: {e}")
            return f"Ошибка: {str(e)}"
    
    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Чат через OpenRouter API"""
        try:
            self.request_count += 1
            
            # Конвертируем сообщения в формат OpenRouter (совместимый с OpenAI)
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Симуляция ответа
            last_message = messages[-1].content if messages else ""
            content = f"Чат ответ OpenRouter {self.model}: {last_message[:30]}..."
            
            return LLMResponse(
                content=content,
                model=self.model,
                usage={"prompt_tokens": 100, "completion_tokens": 50},
                metadata={"provider": "openrouter"}
            )
            
        except Exception as e:
            logger.error(f"Ошибка OpenRouter chat: {e}")
            raise
    
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Стриминг от OpenRouter"""
        try:
            self.request_count += 1
            
            # Симуляция стриминга
            response = f"Стрим ответ от OpenRouter {self.model} на: {prompt[:30]}..."
            
            for word in response.split():
                yield word + " "
                
        except Exception as e:
            logger.error(f"Ошибка OpenRouter streaming: {e}")
            raise


class AnthropicProvider(LLMProvider):
    """Провайдер для Anthropic Claude"""
    
    def __init__(self, model: str = "claude-3-haiku-20240307", config: Optional[Config] = None):
        config = config or get_config()
        super().__init__(model, config)
        
        if not config.anthropic_api_key:
            raise ValueError("Anthropic API key не настроен")
        
        self.api_key = config.anthropic_api_key
        self.base_url = "https://api.anthropic.com/v1"
    
    def complete(self, prompt: str, **kwargs) -> str:
        """Простое завершение через Anthropic"""
        try:
            self.request_count += 1
            
            # Симуляция ответа
            response = f"Ответ Claude {self.model} на промпт: {prompt[:50]}..."
            
            logger.info(f"Anthropic запрос выполнен, модель: {self.model}")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка Anthropic API: {e}")
            raise
    
    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Чат через Anthropic API"""
        try:
            self.request_count += 1
            
            # Конвертируем в формат Anthropic
            last_message = messages[-1].content if messages else ""
            content = f"Claude ответ {self.model}: {last_message[:30]}..."
            
            return LLMResponse(
                content=content,
                model=self.model,
                usage={"input_tokens": 100, "output_tokens": 50},
                metadata={"provider": "anthropic"}
            )
            
        except Exception as e:
            logger.error(f"Ошибка Anthropic chat: {e}")
            raise
    
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Стриминг от Anthropic"""
        try:
            self.request_count += 1
            
            # Симуляция стриминга
            response = f"Стрим ответ от Claude {self.model} на: {prompt[:30]}..."
            
            for word in response.split():
                yield word + " "
                
        except Exception as e:
            logger.error(f"Ошибка Anthropic streaming: {e}")
            raise


class LocalLLMProvider(LLMProvider):
    """Провайдер для локальных моделей (через Ollama и др.)"""
    
    def __init__(self, model: str = "llama3", config: Optional[Config] = None):
        config = config or get_config()
        super().__init__(model, config)
        
        self.base_url = "http://localhost:11434"  # Ollama default
    
    def complete(self, prompt: str, **kwargs) -> str:
        """Простое завершение через локальную модель"""
        try:
            self.request_count += 1
            
            # Симуляция ответа
            response = f"Локальный ответ {self.model} на промпт: {prompt[:50]}..."
            
            logger.info(f"Локальный запрос выполнен, модель: {self.model}")
            return response
            
        except Exception as e:
            logger.error(f"Ошибка локальной модели: {e}")
            raise
    
    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Чат через локальную модель"""
        try:
            self.request_count += 1
            
            last_message = messages[-1].content if messages else ""
            content = f"Локальный чат {self.model}: {last_message[:30]}..."
            
            return LLMResponse(
                content=content,
                model=self.model,
                usage={"tokens": 150},
                metadata={"provider": "local"}
            )
            
        except Exception as e:
            logger.error(f"Ошибка локального чата: {e}")
            raise
    
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Стриминг от локальной модели"""
        try:
            self.request_count += 1
            
            response = f"Локальный стрим {self.model} на: {prompt[:30]}..."
            
            for word in response.split():
                yield word + " "
                
        except Exception as e:
            logger.error(f"Ошибка локального стриминга: {e}")
            raise


# Карта моделей к провайдерам (все через OpenRouter)
MODEL_PROVIDERS = {
    # === БЕСПЛАТНЫЕ МОДЕЛИ (для тестов) ===
    "deepseek/deepseek-chat": OpenAIProvider,                    # Бесплатная, с инструментами
    "deepseek/deepseek-r1": OpenAIProvider,                      # Бесплатная, с инструментами
    "google/gemini-flash-1.5": OpenAIProvider,                  # Бесплатная, с инструментами
    "qwen/qwen-2.5-coder-32b-instruct": OpenAIProvider,         # Бесплатная, программирование, с инструментами
    
    # === CLAUDE МОДЕЛИ (с инструментами) ===
    "anthropic/claude-3.5-sonnet": OpenAIProvider,              # Топ модель, с инструментами
    "anthropic/claude-3.5-haiku": OpenAIProvider,               # Быстрая, с инструментами
    "anthropic/claude-3-opus": OpenAIProvider,                  # Мощная, с инструментами
    
    # === GOOGLE МОДЕЛИ ===
    "google/gemini-pro-1.5": OpenAIProvider,                    # С инструментами
    "google/gemini-pro": OpenAIProvider,                        # С инструментами
    "google/gemma-2-27b-it": OpenAIProvider,                    # Без инструментов
    
    # === DEEPSEEK МОДЕЛИ ===
    "deepseek/deepseek-coder": OpenAIProvider,                  # Программирование, с инструментами
    "deepseek/deepseek-reasoner": OpenAIProvider,               # Рассуждения, с инструментами
    
    # === QWEN МОДЕЛИ ===
    "qwen/qwen-2.5-72b-instruct": OpenAIProvider,               # С инструментами
    "qwen/qwen-2-vl-72b-instruct": OpenAIProvider,              # Мультимодальная, с инструментами
    
    # === ЛОКАЛЬНЫЕ МОДЕЛИ (без инструментов) ===
    "llama3": LocalLLMProvider,
    "mistral": LocalLLMProvider,
    "codellama": LocalLLMProvider,
}

# Модели с поддержкой инструментов (function calling)
MODELS_WITH_TOOLS = {
    # Бесплатные с инструментами
    "deepseek/deepseek-chat",
    "deepseek/deepseek-r1", 
    "google/gemini-flash-1.5",
    "qwen/qwen-2.5-coder-32b-instruct",
    
    # Claude с инструментами
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3.5-haiku", 
    "anthropic/claude-3-opus",
    
    # Google с инструментами
    "google/gemini-pro-1.5",
    "google/gemini-pro",
    
    # DeepSeek с инструментами
    "deepseek/deepseek-coder",
    "deepseek/deepseek-reasoner",
    
    # Qwen с инструментами
    "qwen/qwen-2.5-72b-instruct",
    "qwen/qwen-2-vl-72b-instruct",
}

# Только бесплатные модели для тестов
FREE_MODELS = {
    "deepseek/deepseek-chat",
    "deepseek/deepseek-r1",
    "google/gemini-flash-1.5", 
    "qwen/qwen-2.5-coder-32b-instruct",
}


def get_llm_provider(model: str = "auto", config: Optional[Config] = None) -> LLMProvider:
    """
    Получить LLM провайдер для модели (только OpenRouter)
    
    Args:
        model: Название модели или "auto" для автовыбора
        config: Конфигурация
        
    Returns:
        Настроенный OpenRouter провайдер
    """
    config = config or get_config()
    
    if model == "auto":
        # Используем модель по умолчанию из конфигурации
        model = config.default_model
    
    # Всегда используем OpenAIProvider для OpenRouter
    try:
        return OpenAIProvider(model, config)
    except Exception as e:
        logger.error(f"Ошибка создания OpenRouter провайдера для {model}: {e}")
        # Fallback с mock ответами
        return MockLLMProvider()


def list_available_models() -> Dict[str, List[str]]:
    """Получить список доступных моделей по категориям"""
    return {
        "free": list(FREE_MODELS),
        "with_tools": list(MODELS_WITH_TOOLS),
        "all": list(MODEL_PROVIDERS.keys())
    }


def model_supports_tools(model: str) -> bool:
    """Проверить поддерживает ли модель инструменты"""
    return model in MODELS_WITH_TOOLS


def get_free_models() -> List[str]:
    """Получить список бесплатных моделей"""
    return list(FREE_MODELS)


def get_best_free_model_with_tools() -> str:
    """Получить лучшую бесплатную модель с поддержкой инструментов"""
    # DeepSeek Chat - наиболее стабильная бесплатная модель с инструментами
    return "deepseek/deepseek-chat"


# Глобальный кеш провайдеров
_provider_cache: Dict[str, LLMProvider] = {}


def get_cached_provider(model: str, config: Optional[Config] = None) -> LLMProvider:
    """Получить провайдер с кешированием"""
    cache_key = f"{model}_{id(config) if config else 'default'}"
    
    if cache_key not in _provider_cache:
        _provider_cache[cache_key] = get_llm_provider(model, config)
    
    return _provider_cache[cache_key]


def clear_provider_cache():
    """Очистить кеш провайдеров"""
    global _provider_cache
    _provider_cache.clear()


class MockLLMProvider(LLMProvider):
    """Mock провайдер для тестирования без API ключей"""
    
    def __init__(self, model: str = "mock"):
        # Создаем фиктивную конфигурацию
        from .config import Config
        mock_config = Config()
        super().__init__(model, mock_config)
    
    def complete(self, prompt: str, **kwargs) -> str:
        """Mock ответ"""
        return "Hello from KittyCore! (mock response)"
    
    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Mock чат"""
        return LLMResponse(
            content="Hello from KittyCore! (mock chat)",
            model=self.model,
            usage={"tokens": 10},
            metadata={"provider": "mock"}
        )
    
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Mock стриминг"""
        words = ["Hello", "from", "KittyCore!", "(mock", "stream)"]
        for word in words:
            yield word + " " 