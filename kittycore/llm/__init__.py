"""
🧠 LLM Провайдеры для KittyCore 3.0

Поддерживаемые провайдеры:
- OpenRouter (бесплатные модели)
- OpenAI 
- Anthropic
- Local models
"""

import os
import json
import httpx
import asyncio
from typing import Dict, Any, Optional, Iterator
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """Конфигурация LLM"""
    provider: str = "openrouter"
    model: str = "meta-llama/llama-3.2-3b-instruct:free"  # Бесплатная модель
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 30

class LLMProvider:
    """Базовый класс для LLM провайдеров"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        
    def complete(self, prompt: str, **kwargs) -> str:
        """Получить ответ от LLM"""
        raise NotImplementedError
        
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        """Стриминг ответов"""
        raise NotImplementedError

class OpenRouterProvider(LLMProvider):
    """OpenRouter провайдер с бесплатными моделями + rate limiting"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.last_request_time = 0
        self.min_request_interval = 3.5  # Минимум 3.5 секунды между запросами (безопасно для 20/мин лимита)
        
        if not self.api_key:
            raise ValueError("❌ OPENROUTER_API_KEY не найден! Система НЕ МОЖЕТ работать без LLM!")
            
    def complete(self, prompt: str, **kwargs) -> str:
        """Отправить запрос к OpenRouter с rate limiting - БЕЗ FALLBACK"""
        if not self.api_key:
            raise ValueError("❌ КРИТИЧЕСКАЯ ОШИБКА: Нет API ключа для LLM!")
        
        # Rate limiting - ждём если нужно
        import time
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            print(f"🛡️ Rate limiting: ждём {sleep_time:.1f}с...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
            
        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.config.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.config.max_tokens)
                },
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception(f"❌ КРИТИЧЕСКАЯ ОШИБКА LLM API: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"❌ КРИТИЧЕСКАЯ ОШИБКА LLM: {e} - СИСТЕМА НЕ МОЖЕТ РАБОТАТЬ БЕЗ LLM!")

class SimpleLocalProvider(LLMProvider):
    """УДАЛЕН - НЕТ МОКОВ!"""
    
    def complete(self, prompt: str, **kwargs) -> str:
        """НЕТ ЛОКАЛЬНЫХ МОКОВ!"""
        raise Exception("❌ КРИТИЧЕСКАЯ ОШИБКА: Локальные провайдеры отключены! Нужен реальный LLM!")

def get_llm_provider(model: str = None, config: LLMConfig = None) -> LLMProvider:
    """Получить LLM провайдер - ТОЛЬКО РЕАЛЬНЫЕ LLM"""
    if config is None:
        config = LLMConfig()
        
    if model:
        config.model = model
        
    # ТОЛЬКО OpenRouter - никаких fallback
    if "openrouter" in config.provider or any(provider in config.model for provider in ["meta-llama", "google", "anthropic"]):
        return OpenRouterProvider(config)
    else:
        # Больше никаких fallback - если не OpenRouter, то ошибка
        raise Exception(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Неподдерживаемый провайдер {config.provider}! Только OpenRouter!")

# Глобальный провайдер по умолчанию
_default_provider = None

def get_default_provider() -> LLMProvider:
    """Получить провайдер по умолчанию"""
    global _default_provider
    if _default_provider is None:
        _default_provider = get_llm_provider()
    return _default_provider

def set_default_provider(provider: LLMProvider):
    """Установить провайдер по умолчанию"""
    global _default_provider
    _default_provider = provider 