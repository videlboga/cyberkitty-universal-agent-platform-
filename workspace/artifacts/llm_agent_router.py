#!/usr/bin/env python3
"""
🚀 УМНЫЙ МАРШРУТИЗАТОР АГЕНТОВ С LLM
Интеграция быстрой LLM-классификации в систему агентов
"""

import asyncio
import aiohttp
import time
import os
from enum import Enum
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Agent(Enum):
    NOVA = "nova"           # Анализ данных
    SHERLOCK = "sherlock"   # Поиск информации
    ARTEMIS = "artemis"     # Контент, дизайн
    ADA = "ada"             # Программирование
    CIPHER = "cipher"       # Безопасность
    WARREN = "warren"       # Финансы
    VIRAL = "viral"         # Маркетинг

class LLMAgentRouter:
    """🧠 Умный маршрутизатор агентов"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
        self.llm_available = bool(self.api_key)
        
        print(f"🧠 LLM Router: {'✅ готов' if self.llm_available else '❌ только эвристика'}")
    
    async def route(self, task: str) -> Dict[str, Any]:
        """Маршрутизация задачи"""
        
        # Сначала пробуем LLM (если доступен)
        if self.llm_available:
            try:
                return await self._llm_classify(task)
            except Exception as e:
                print(f"⚠️ LLM ошибка: {e}, fallback на эвристику")
        
        # Fallback на эвристику
        return self._heuristic_classify(task)
    
    async def _llm_classify(self, task: str) -> Dict[str, Any]:
        """Классификация через LLM"""
        
        start_time = time.time()
        
        prompt = f"""Ты классификатор агентов. Выбери ОДНОГО агента:

nova - анализ данных, статистика
sherlock - поиск информации, исследования
artemis - контент, тексты, дизайн
ada - программирование, код
cipher - безопасность, тесты
warren - финансы, деньги
viral - маркетинг, реклама

ЗАДАЧА: {task}

ОТВЕТ: только имя агента"""
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 10,
                "temperature": 0.1
            }
            
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers, json=payload, timeout=10
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    agent_name = self._extract_agent(content)
                    
                    return {
                        "agent": Agent(agent_name),
                        "method": "llm",
                        "confidence": 0.92,
                        "response": content.strip(),
                        "time_ms": round((time.time() - start_time) * 1000)
                    }
                else:
                    raise Exception(f"HTTP {response.status}")
    
    def _heuristic_classify(self, task: str) -> Dict[str, Any]:
        """Эвристическая классификация"""
        
        task_lower = task.lower()
        
        rules = [
            (["анализ", "данные"], Agent.NOVA),
            (["найди", "поиск"], Agent.SHERLOCK),
            (["создай", "дизайн"], Agent.ARTEMIS),
            (["код", "программ"], Agent.ADA),
            (["тест", "безопасность"], Agent.CIPHER),
            (["бюджет", "финанс"], Agent.WARREN),
            (["реклам", "маркетинг"], Agent.VIRAL)
        ]
        
        for keywords, agent in rules:
            if any(word in task_lower for word in keywords):
                return {
                    "agent": agent,
                    "method": "heuristic",
                    "confidence": 0.75,
                    "response": f"Эвристика выбрала {agent.value}",
                    "time_ms": 1
                }
        
        return {
            "agent": Agent.SHERLOCK,
            "method": "heuristic", 
            "confidence": 0.6,
            "response": "По умолчанию",
            "time_ms": 1
        }
    
    def _extract_agent(self, response: str) -> str:
        """Извлечение агента из ответа"""
        response_lower = response.lower()
        agents = ["nova", "sherlock", "artemis", "ada", "cipher", "warren", "viral"]
        
        for agent in agents:
            if agent in response_lower:
                return agent
        return "sherlock"

# Демо
async def demo():
    """Демонстрация работы маршрутизатора"""
    
    print("🚀 ДЕМО LLM МАРШРУТИЗАТОРА АГЕНТОВ")
    print("=" * 50)
    
    router = LLMAgentRouter()
    
    tasks = [
        "Проанализируй продажи за квартал",
        "Создай логотип для компании",
        "Найди информацию о конкурентах",
        "Напиши код для API",
        "Запусти рекламную кампанию",
        "Рассчитай бюджет проекта"
    ]
    
    results = []
    
    for i, task in enumerate(tasks, 1):
        print(f"\n🎯 ЗАДАЧА {i}: '{task}'")
        
        result = await router.route(task)
        results.append(result)
        
        print(f"   🤖 Агент: {result['agent'].value}")
        print(f"   🔧 Метод: {result['method']}")
        print(f"   🎯 Уверенность: {result['confidence']:.1%}")
        print(f"   ⚡ Время: {result['time_ms']}мс")
        print(f"   💬 Ответ: {result['response']}")
    
    # Статистика
    llm_count = sum(1 for r in results if r['method'] == 'llm')
    avg_time = sum(r['time_ms'] for r in results) / len(results)
    
    print(f"\n📊 СТАТИСТИКА:")
    print(f"   📈 LLM использован: {llm_count}/{len(results)} раз")
    print(f"   ⚡ Среднее время: {round(avg_time)}мс")

if __name__ == "__main__":
    asyncio.run(demo()) 