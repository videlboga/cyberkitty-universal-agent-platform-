#!/usr/bin/env python3
"""
🚀 МАЛЕНЬКИЕ БЫСТРЫЕ LLM ДЛЯ КЛАССИФИКАЦИИ АГЕНТОВ
Простая задача = простое решение!
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SmallLLMProvider:
    """Провайдер маленьких LLM"""
    name: str
    api_url: str
    model: str
    cost_per_1k_tokens: float
    avg_response_time_ms: int
    max_tokens: int

class FastAgentClassifier:
    """
    🚀 Быстрая классификация агентов через маленькие LLM
    
    ПРИНЦИП: Классификация агентов - это простая задача классификации текста.
    Не нужны мощные модели типа GPT-4, достаточно маленьких и быстрых!
    """
    
    def __init__(self):
        self.providers = self._init_providers()
        self.current_provider = "groq"  # По умолчанию самый быстрый
        
        # Кеш для частых запросов
        self.classification_cache: Dict[str, str] = {}
        
        # Простой промпт для классификации
        self.classification_prompt = self._create_classification_prompt()
    
    def _init_providers(self) -> Dict[str, SmallLLMProvider]:
        """Инициализация провайдеров маленьких LLM"""
        
        return {
            # Groq - сверхбыстрые инференс
            "groq": SmallLLMProvider(
                name="Groq Llama-3.1-8B",
                api_url="https://api.groq.com/openai/v1/chat/completions",
                model="llama-3.1-8b-instant",
                cost_per_1k_tokens=0.0001,  # $0.0001 за 1K токенов!
                avg_response_time_ms=200,    # 200мс!
                max_tokens=8192
            ),
            
            # Ollama - локальные модели
            "ollama": SmallLLMProvider(
                name="Ollama Llama-3.2-3B",
                api_url="http://localhost:11434/api/generate",
                model="llama3.2:3b",
                cost_per_1k_tokens=0.0,     # Бесплатно!
                avg_response_time_ms=300,    # 300мс на CPU
                max_tokens=4096
            ),
            
            # Together AI - быстрые малые модели
            "together": SmallLLMProvider(
                name="Together Llama-3.2-3B",
                api_url="https://api.together.xyz/v1/chat/completions", 
                model="meta-llama/Llama-3.2-3B-Instruct-Turbo",
                cost_per_1k_tokens=0.0002,
                avg_response_time_ms=250,
                max_tokens=4096
            ),
            
            # OpenAI GPT-4o-mini (для сравнения)
            "openai": SmallLLMProvider(
                name="OpenAI GPT-4o-mini",
                api_url="https://api.openai.com/v1/chat/completions",
                model="gpt-4o-mini",
                cost_per_1k_tokens=0.00015,
                avg_response_time_ms=800,
                max_tokens=4096
            )
        }
    
    def _create_classification_prompt(self) -> str:
        """Создание простого промпта для классификации"""
        
        return """Ты классификатор агентов. Выбери ОДНОГО агента для задачи:

АГЕНТЫ:
nova - анализ данных, статистика, математика
sherlock - поиск информации, исследования
artemis - контент, тексты, дизайн  
ada - программирование, код
cipher - безопасность, тесты
warren - финансы, деньги
viral - маркетинг, реклама

ЗАДАЧА: {task}

ОТВЕТ: только имя агента (например: nova)"""
    
    async def classify_agent(self, task: str) -> Dict[str, any]:
        """Быстрая классификация агента"""
        
        # Проверяем кеш
        cache_key = task.lower().strip()
        if cache_key in self.classification_cache:
            return {
                "agent": self.classification_cache[cache_key],
                "source": "cache",
                "response_time_ms": 0,
                "cost": 0.0
            }
        
        # Выбираем провайдера
        provider = self.providers[self.current_provider]
        
        # Засекаем время
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Формируем запрос
            prompt = self.classification_prompt.format(task=task)
            
            if self.current_provider == "groq":
                agent = await self._classify_groq(prompt, provider)
            elif self.current_provider == "ollama":
                agent = await self._classify_ollama(prompt, provider)
            elif self.current_provider == "together":
                agent = await self._classify_together(prompt, provider)
            elif self.current_provider == "openai":
                agent = await self._classify_openai(prompt, provider)
            else:
                agent = "sherlock"  # Fallback
            
            # Рассчитываем метрики
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            estimated_tokens = len(prompt.split()) + 1  # Промпт + ответ
            cost = (estimated_tokens / 1000) * provider.cost_per_1k_tokens
            
            # Сохраняем в кеш
            self.classification_cache[cache_key] = agent
            
            return {
                "agent": agent,
                "source": f"{provider.name}",
                "response_time_ms": round(response_time),
                "cost": round(cost, 6),
                "tokens_used": estimated_tokens
            }
            
        except Exception as e:
            # Fallback на эвристику
            return {
                "agent": self._fallback_heuristic(task),
                "source": "heuristic_fallback",
                "response_time_ms": 1,
                "cost": 0.0,
                "error": str(e)
            }
    
    async def _classify_groq(self, prompt: str, provider: SmallLLMProvider) -> str:
        """Классификация через Groq"""
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self._get_api_key('groq')}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": provider.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 10,
                "temperature": 0.1
            }
            
            async with session.post(provider.api_url, json=payload, headers=headers) as response:
                data = await response.json()
                return self._extract_agent_name(data["choices"][0]["message"]["content"])
    
    async def _classify_ollama(self, prompt: str, provider: SmallLLMProvider) -> str:
        """Классификация через Ollama (локально)"""
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": provider.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 10
                }
            }
            
            async with session.post(provider.api_url, json=payload) as response:
                data = await response.json()
                return self._extract_agent_name(data["response"])
    
    async def _classify_together(self, prompt: str, provider: SmallLLMProvider) -> str:
        """Классификация через Together AI"""
        
        # Аналогично Groq
        return await self._classify_groq(prompt, provider)
    
    async def _classify_openai(self, prompt: str, provider: SmallLLMProvider) -> str:
        """Классификация через OpenAI (для сравнения)"""
        
        # Аналогично Groq, но другой API ключ
        return await self._classify_groq(prompt, provider)
    
    def _extract_agent_name(self, response: str) -> str:
        """Извлечение имени агента из ответа"""
        
        response_lower = response.lower().strip()
        
        # Список валидных агентов
        valid_agents = ["nova", "sherlock", "artemis", "ada", "cipher", "warren", "viral"]
        
        # Ищем первое совпадение
        for agent in valid_agents:
            if agent in response_lower:
                return agent
        
        # Если не найдено - по умолчанию
        return "sherlock"
    
    def _fallback_heuristic(self, task: str) -> str:
        """Эвристика как fallback"""
        
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["анализ", "данные"]):
            return "nova"
        elif any(word in task_lower for word in ["контент", "текст"]):
            return "artemis"
        elif any(word in task_lower for word in ["код", "программ"]):
            return "ada"
        else:
            return "sherlock"
    
    def _get_api_key(self, provider: str) -> str:
        """Получение API ключа (в реальности из env)"""
        # В реальности: os.getenv(f"{provider.upper()}_API_KEY")
        return "fake_api_key_for_demo"
    
    def get_provider_stats(self) -> Dict[str, Dict]:
        """Статистика провайдеров"""
        
        stats = {}
        for name, provider in self.providers.items():
            stats[name] = {
                "cost_per_1k_tokens": provider.cost_per_1k_tokens,
                "avg_response_time_ms": provider.avg_response_time_ms,
                "cost_per_month_1000_requests": round(provider.cost_per_1k_tokens * 50 * 30, 4),  # ~50 токенов на запрос
                "suitable_for": self._get_use_cases(provider)
            }
        
        return stats
    
    def _get_use_cases(self, provider: SmallLLMProvider) -> List[str]:
        """Подходящие случаи использования"""
        
        use_cases = []
        
        if provider.cost_per_1k_tokens == 0:
            use_cases.append("Разработка и тестирование")
        
        if provider.avg_response_time_ms < 300:
            use_cases.append("Real-time приложения")
        
        if provider.cost_per_1k_tokens < 0.0005:
            use_cases.append("Высоконагруженные системы")
        
        return use_cases

# Демо быстрой классификации
async def demo_fast_classification():
    """Демонстрация быстрой классификации"""
    
    classifier = FastAgentClassifier()
    
    print("🚀 ДЕМО БЫСТРОЙ LLM-КЛАССИФИКАЦИИ")
    print("=" * 50)
    
    # Тестовые задачи
    test_tasks = [
        "Проанализируй продажи за квартал",
        "Создай логотип для стартапа", 
        "Найди баги в коде",
        "Запусти рекламную кампанию",
        "Изучи конкурентов на рынке"
    ]
    
    # Статистика провайдеров
    print("\n📊 СРАВНЕНИЕ ПРОВАЙДЕРОВ:")
    stats = classifier.get_provider_stats()
    for provider, data in stats.items():
        print(f"   {provider}:")
        print(f"      💰 ${data['cost_per_1k_tokens']:.6f} за 1K токенов")
        print(f"      ⚡ {data['avg_response_time_ms']}мс ответ")
        print(f"      📅 ${data['cost_per_month_1000_requests']}/месяц за 1000 запросов")
        print(f"      🎯 {', '.join(data['suitable_for'])}")
    
    # Тестируем классификацию
    print(f"\n🧪 ТЕСТЫ КЛАССИФИКАЦИИ:")
    
    for task in test_tasks:
        result = await classifier.classify_agent(task)
        
        print(f"\n📋 '{task}'")
        print(f"   🤖 Агент: {result['agent']}")
        print(f"   ⚡ Время: {result['response_time_ms']}мс")
        print(f"   💰 Стоимость: ${result['cost']:.6f}")
        print(f"   📡 Источник: {result['source']}")

if __name__ == "__main__":
    asyncio.run(demo_fast_classification()) 