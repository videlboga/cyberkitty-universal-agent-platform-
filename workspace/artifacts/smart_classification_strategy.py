#!/usr/bin/env python3
"""
🧠 УМНАЯ СТРАТЕГИЯ КЛАССИФИКАЦИИ АГЕНТОВ
Адаптивный выбор провайдера в зависимости от нагрузки и требований
"""

from enum import Enum
from typing import Dict, List
import asyncio
from dataclasses import dataclass
import time

class ClassificationMode(Enum):
    """Режимы классификации"""
    DEVELOPMENT = "development"  # Ollama локально
    PRODUCTION = "production"    # Groq быстро и дешево  
    HIGH_ACCURACY = "accuracy"   # GPT-4o-mini для критичных случаев
    OFFLINE = "offline"          # Только эвристика

@dataclass
class SystemLoad:
    """Текущая нагрузка системы"""
    requests_per_minute: int
    avg_response_time_ms: float
    error_rate_percent: float
    queue_length: int

class SmartClassificationStrategy:
    """
    🧠 Умная стратегия выбора провайдера классификации
    
    ПРИНЦИПЫ:
    1. Разработка = Ollama (бесплатно, приватно)
    2. Продакшен = Groq (быстро, дешево)
    3. Критичные задачи = GPT-4o-mini (точно)
    4. Оффлайн/проблемы = эвристика (надежно)
    """
    
    def __init__(self):
        self.current_mode = ClassificationMode.PRODUCTION
        self.fallback_enabled = True
        
        # Статистика использования
        self.stats = {
            "total_requests": 0,
            "provider_usage": {},
            "accuracy_scores": {},
            "cost_tracking": 0.0
        }
        
        # Адаптивные пороги
        self.thresholds = {
            "high_load_rpm": 100,     # При >100 req/min переходим на быстрые модели
            "error_rate_limit": 5.0,  # При >5% ошибок включаем fallback
            "response_time_limit": 1000  # При >1сек переходим на более быстрые
        }
    
    async def classify_with_strategy(self, task: str, priority: str = "normal") -> Dict:
        """
        Классификация с умной стратегией выбора провайдера
        
        Args:
            task: Задача для классификации
            priority: normal|high|critical
        """
        
        # Анализируем текущую нагрузку
        system_load = await self._get_system_load()
        
        # Выбираем оптимальный провайдер
        chosen_provider = self._choose_provider(priority, system_load)
        
        # Выполняем классификацию
        result = await self._execute_classification(task, chosen_provider)
        
        # Обновляем статистику
        self._update_stats(chosen_provider, result)
        
        # Адаптируем стратегию на будущее
        await self._adapt_strategy(result, system_load)
        
        return {
            **result,
            "strategy": {
                "chosen_provider": chosen_provider,
                "reason": self._get_choice_reason(priority, system_load),
                "system_load": system_load.__dict__,
                "total_cost_today": round(self.stats["cost_tracking"], 4)
            }
        }
    
    def _choose_provider(self, priority: str, load: SystemLoad) -> str:
        """Выбор оптимального провайдера"""
        
        # Критичная задача = максимальная точность
        if priority == "critical":
            return "openai"
        
        # Высокая нагрузка = самый быстрый
        if load.requests_per_minute > self.thresholds["high_load_rpm"]:
            return "groq"
        
        # Высокая частота ошибок = fallback
        if load.error_rate_percent > self.thresholds["error_rate_limit"]:
            return "heuristic"
        
        # Режим разработки = локальные модели
        if self.current_mode == ClassificationMode.DEVELOPMENT:
            return "ollama"
        
        # Режим оффлайн = эвристика
        if self.current_mode == ClassificationMode.OFFLINE:
            return "heuristic"
        
        # По умолчанию - баланс скорости и стоимости
        return "groq"
    
    def _get_choice_reason(self, priority: str, load: SystemLoad) -> str:
        """Объяснение выбора провайдера"""
        
        if priority == "critical":
            return "Критичная задача требует максимальной точности"
        
        if load.requests_per_minute > self.thresholds["high_load_rpm"]:
            return f"Высокая нагрузка ({load.requests_per_minute} req/min), нужна скорость"
        
        if load.error_rate_percent > self.thresholds["error_rate_limit"]:
            return f"Высокая частота ошибок ({load.error_rate_percent}%), используем fallback"
        
        if self.current_mode == ClassificationMode.DEVELOPMENT:
            return "Режим разработки - используем локальные модели"
        
        return "Оптимальный баланс скорости и стоимости"
    
    async def _get_system_load(self) -> SystemLoad:
        """Получение текущей нагрузки системы"""
        
        # В реальности: мониторинг из метрик системы
        # Здесь упрощенная версия
        
        return SystemLoad(
            requests_per_minute=50,  # Средняя нагрузка
            avg_response_time_ms=250.0,
            error_rate_percent=1.5,
            queue_length=0
        )
    
    async def _execute_classification(self, task: str, provider: str) -> Dict:
        """Выполнение классификации через выбранный провайдер"""
        
        start_time = time.time()
        
        try:
            if provider == "heuristic":
                return {
                    "agent": self._heuristic_classify(task),
                    "provider": "heuristic",
                    "response_time_ms": 1,
                    "cost": 0.0,
                    "confidence": 0.7
                }
            
            # Здесь был бы вызов FastAgentClassifier
            # Упрощенная симуляция
            
            response_time = (time.time() - start_time) * 1000
            
            # Симуляция разных провайдеров
            provider_simulation = {
                "groq": {"time": 200, "cost": 0.000003, "accuracy": 0.92},
                "ollama": {"time": 300, "cost": 0.0, "accuracy": 0.88},
                "openai": {"time": 800, "cost": 0.00004, "accuracy": 0.96},
                "together": {"time": 250, "cost": 0.000005, "accuracy": 0.90}
            }
            
            sim = provider_simulation.get(provider, provider_simulation["groq"])
            
            return {
                "agent": self._smart_classify(task, provider),
                "provider": provider,
                "response_time_ms": sim["time"],
                "cost": sim["cost"],
                "confidence": sim["accuracy"]
            }
            
        except Exception as e:
            # Fallback на эвристику
            return {
                "agent": self._heuristic_classify(task),
                "provider": "heuristic_fallback",
                "response_time_ms": 1,
                "cost": 0.0,
                "confidence": 0.7,
                "error": str(e)
            }
    
    def _smart_classify(self, task: str, provider: str) -> str:
        """Умная классификация с учетом провайдера"""
        
        task_lower = task.lower()
        
        # LLM-провайдеры понимают контекст лучше
        if provider in ["groq", "openai", "together"]:
            # Более точная классификация через контекст
            if "анализ" in task_lower and ("продаж" in task_lower or "данных" in task_lower):
                return "nova"
            elif "создай" in task_lower and ("лого" in task_lower or "дизайн" in task_lower):
                return "artemis"
            elif "найди" in task_lower and ("баг" in task_lower or "ошиб" in task_lower):
                return "cipher"
            elif "запусти" in task_lower and ("реклам" in task_lower or "кампан" in task_lower):
                return "viral"
            elif "изучи" in task_lower and ("конкурент" in task_lower or "рынок" in task_lower):
                return "sherlock"
        
        # Fallback на простую эвристику
        return self._heuristic_classify(task)
    
    def _heuristic_classify(self, task: str) -> str:
        """Эвристическая классификация как fallback"""
        
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["анализ", "данные", "статистика"]):
            return "nova"
        elif any(word in task_lower for word in ["создай", "дизайн", "контент"]):
            return "artemis"
        elif any(word in task_lower for word in ["код", "программ", "разработ"]):
            return "ada"
        elif any(word in task_lower for word in ["безопасность", "тест", "баг"]):
            return "cipher"
        elif any(word in task_lower for word in ["деньги", "финанс", "стоимость"]):
            return "warren"
        elif any(word in task_lower for word in ["реклам", "маркетинг", "продвиж"]):
            return "viral"
        else:
            return "sherlock"
    
    def _update_stats(self, provider: str, result: Dict):
        """Обновление статистики использования"""
        
        self.stats["total_requests"] += 1
        
        if provider not in self.stats["provider_usage"]:
            self.stats["provider_usage"][provider] = 0
        self.stats["provider_usage"][provider] += 1
        
        if "cost" in result:
            self.stats["cost_tracking"] += result["cost"]
    
    async def _adapt_strategy(self, result: Dict, load: SystemLoad):
        """Адаптация стратегии на основе результатов"""
        
        # Если слишком медленно - понижаем требования к точности
        if result.get("response_time_ms", 0) > self.thresholds["response_time_limit"]:
            if self.current_mode == ClassificationMode.HIGH_ACCURACY:
                self.current_mode = ClassificationMode.PRODUCTION
                print("⚡ Переключение на быстрые модели из-за медленного ответа")
        
        # Если слишком много ошибок - включаем fallback
        if load.error_rate_percent > self.thresholds["error_rate_limit"]:
            self.fallback_enabled = True
            print("🛡️ Включен fallback режим из-за ошибок")
    
    def get_strategy_stats(self) -> Dict:
        """Статистика работы стратегии"""
        
        total_requests = self.stats["total_requests"]
        if total_requests == 0:
            return {"message": "Статистика пуста"}
        
        provider_percentages = {}
        for provider, count in self.stats["provider_usage"].items():
            provider_percentages[provider] = round((count / total_requests) * 100, 1)
        
        return {
            "total_requests": total_requests,
            "total_cost": round(self.stats["cost_tracking"], 6),
            "avg_cost_per_request": round(self.stats["cost_tracking"] / total_requests, 6),
            "provider_distribution": provider_percentages,
            "current_mode": self.current_mode.value,
            "fallback_enabled": self.fallback_enabled,
            "cost_projection_month": round(self.stats["cost_tracking"] / total_requests * 30 * 1000, 2)  # При 1000 req/день
        }

# Демо умной стратегии
async def demo_smart_strategy():
    """Демонстрация умной стратегии классификации"""
    
    strategy = SmartClassificationStrategy()
    
    print("🧠 ДЕМО УМНОЙ СТРАТЕГИИ КЛАССИФИКАЦИИ")
    print("=" * 50)
    
    # Тестовые сценарии
    test_scenarios = [
        ("Проанализируй продажи", "normal"),
        ("КРИТИЧНО: Найди уязвимость в системе", "critical"),
        ("Создай логотип", "normal"),
        ("Запусти рекламу", "high"),
        ("Изучи конкурентов", "normal")
    ]
    
    print("\n🧪 ТЕСТИРОВАНИЕ РАЗНЫХ СЦЕНАРИЕВ:")
    
    for task, priority in test_scenarios:
        result = await strategy.classify_with_strategy(task, priority)
        
        print(f"\n📋 '{task}' (приоритет: {priority})")
        print(f"   🤖 Агент: {result['agent']}")
        print(f"   📡 Провайдер: {result['provider']}")
        print(f"   ⚡ Время: {result['response_time_ms']}мс")
        print(f"   💰 Стоимость: ${result['cost']:.6f}")
        print(f"   🎯 Уверенность: {result.get('confidence', 0):.1%}")
        print(f"   💡 Причина выбора: {result['strategy']['reason']}")
    
    # Статистика стратегии
    print(f"\n📊 СТАТИСТИКА СТРАТЕГИИ:")
    stats = strategy.get_strategy_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    asyncio.run(demo_smart_strategy()) 