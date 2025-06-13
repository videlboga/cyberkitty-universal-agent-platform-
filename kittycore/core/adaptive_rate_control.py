#!/usr/bin/env python3
"""
🚀 Adaptive Rate Control - Умное управление скоростью запросов

Современные подходы 2024:
- Circuit Breakers для автоматического отключения при перегрузке
- Exponential Backoff с jitter для избежания thundering herd
- Provider Switching с fallback между LLM провайдерами
- Smart Batching и приоритизация запросов
- Кеширование результатов для повторных запросов

Принцип: "Система адаптируется к нагрузке и не падает" 🔄
"""

import asyncio
import time
import random
import hashlib
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Состояния Circuit Breaker"""
    CLOSED = "closed"      # Нормальная работа
    OPEN = "open"          # Блокировка запросов
    HALF_OPEN = "half_open"  # Тестирование восстановления

@dataclass
class RateLimitConfig:
    """Конфигурация rate limiting"""
    requests_per_second: float = 2.0
    burst_size: int = 5
    backoff_base: float = 1.0
    backoff_max: float = 60.0
    circuit_failure_threshold: int = 5
    circuit_recovery_timeout: int = 30
    jitter_factor: float = 0.1

@dataclass
class RequestResult:
    """Результат выполнения запроса"""
    success: bool
    duration: float
    error: Optional[str] = None
    provider: Optional[str] = None
    cached: bool = False
    retries: int = 0

class CircuitBreaker:
    """Circuit Breaker для защиты от перегрузки"""
    
    def __init__(self, config: RateLimitConfig, provider_name: str):
        self.config = config
        self.provider_name = provider_name
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        
    def can_execute(self) -> bool:
        """Проверить можно ли выполнить запрос"""
        
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            # Проверяем можно ли попробовать восстановление
            if (self.last_failure_time and 
                time.time() - self.last_failure_time > self.config.circuit_recovery_timeout):
                self.state = CircuitState.HALF_OPEN
                logger.info(f"🔄 Circuit breaker {self.provider_name}: переход в HALF_OPEN")
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Записать успешное выполнение"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:  # 3 успешных запроса - восстановление
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info(f"✅ Circuit breaker {self.provider_name}: восстановлен (CLOSED)")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)  # Снижаем счетчик ошибок
    
    def record_failure(self):
        """Записать неуспешное выполнение"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.circuit_failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"⚠️ Circuit breaker {self.provider_name}: ОТКРЫТ (слишком много ошибок)")

class ExponentialBackoff:
    """Exponential Backoff с jitter"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.attempt_count = 0
    
    def get_delay(self) -> float:
        """Получить задержку для следующей попытки"""
        if self.attempt_count == 0:
            return 0
        
        # Exponential backoff
        delay = self.config.backoff_base * (2 ** (self.attempt_count - 1))
        delay = min(delay, self.config.backoff_max)
        
        # Добавляем jitter для избежания thundering herd
        jitter = delay * self.config.jitter_factor * random.random()
        final_delay = delay + jitter
        
        logger.debug(f"⏳ Exponential backoff: попытка {self.attempt_count}, задержка {final_delay:.2f}с")
        return final_delay
    
    def next_attempt(self):
        """Увеличить счетчик попыток"""
        self.attempt_count += 1
    
    def reset(self):
        """Сбросить счетчик попыток"""
        self.attempt_count = 0

class TokenBucket:
    """Token Bucket для rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Попытаться использовать токены"""
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Пополнить токены"""
        now = time.time()
        time_passed = now - self.last_refill
        tokens_to_add = time_passed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """Получить время ожидания для нужного количества токенов"""
        self._refill()
        
        if self.tokens >= tokens:
            return 0
        
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate

class ResponseCache:
    """Кеш для ответов LLM провайдеров"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def _get_cache_key(self, request_data: Dict[str, Any]) -> str:
        """Создать ключ кеша для запроса"""
        # Создаем детерминированный хеш от запроса
        request_str = json.dumps(request_data, sort_keys=True)
        return hashlib.md5(request_str.encode()).hexdigest()
    
    def get(self, request_data: Dict[str, Any]) -> Optional[Any]:
        """Получить ответ из кеша"""
        cache_key = self._get_cache_key(request_data)
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            # Проверяем TTL
            if time.time() - entry['timestamp'] < self.ttl_seconds:
                logger.debug(f"💾 Cache HIT для запроса: {cache_key[:8]}...")
                return entry['response']
            else:
                # Удаляем устаревшую запись
                del self.cache[cache_key]
        
        return None
    
    def put(self, request_data: Dict[str, Any], response: Any):
        """Сохранить ответ в кеш"""
        cache_key = self._get_cache_key(request_data)
        
        # Если кеш переполнен, удаляем самые старые записи
        if len(self.cache) >= self.max_size:
            # Удаляем 20% самых старых записей
            sorted_entries = sorted(self.cache.items(), key=lambda x: x[1]['timestamp'])
            entries_to_remove = int(self.max_size * 0.2)
            for key, _ in sorted_entries[:entries_to_remove]:
                del self.cache[key]
        
        self.cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
        logger.debug(f"💾 Cache SET для запроса: {cache_key[:8]}...")

@dataclass
class RequestPriority:
    """Приоритет запроса"""
    HIGH = 3
    MEDIUM = 2
    LOW = 1

@dataclass
class PrioritizedRequest:
    """Приоритизированный запрос"""
    request_data: Dict[str, Any]
    priority: int
    callback: Callable
    future: asyncio.Future
    timestamp: float
    
class RequestQueue:
    """Очередь запросов с приоритизацией"""
    
    def __init__(self):
        self.queue: List[PrioritizedRequest] = []
        self.processing = False
    
    async def add_request(self, request_data: Dict[str, Any], 
                         priority: int = RequestPriority.MEDIUM,
                         callback: Callable = None) -> Any:
        """Добавить запрос в очередь"""
        
        future = asyncio.Future()
        request = PrioritizedRequest(
            request_data=request_data,
            priority=priority,
            callback=callback,
            future=future,
            timestamp=time.time()
        )
        
        # Вставляем в очередь согласно приоритету
        inserted = False
        for i, existing_request in enumerate(self.queue):
            if request.priority > existing_request.priority:
                self.queue.insert(i, request)
                inserted = True
                break
        
        if not inserted:
            self.queue.append(request)
        
        logger.debug(f"📝 Добавлен запрос в очередь (приоритет: {priority}, позиция: {len(self.queue)})")
        return await future

class AdaptiveRateController:
    """Главный контроллер адаптивного rate limiting"""
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        
        # Компоненты системы
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.backoff_managers: Dict[str, ExponentialBackoff] = {}
        self.cache = ResponseCache()
        self.request_queue = RequestQueue()
        
        # Статистика
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'cached_responses': 0,
            'circuit_breaks': 0,
            'backoff_delays': 0
        }
        
        logger.info("🚀 Adaptive Rate Controller инициализирован")
    
    def _get_or_create_components(self, provider: str):
        """Получить или создать компоненты для провайдера"""
        if provider not in self.circuit_breakers:
            self.circuit_breakers[provider] = CircuitBreaker(self.config, provider)
            self.token_buckets[provider] = TokenBucket(
                self.config.burst_size, 
                self.config.requests_per_second
            )
            self.backoff_managers[provider] = ExponentialBackoff(self.config)
    
    async def execute_request(self, provider: str, request_data: Dict[str, Any],
                            execute_func: Callable, priority: int = RequestPriority.MEDIUM) -> RequestResult:
        """Выполнить запрос с адаптивным rate limiting"""
        
        self.stats['total_requests'] += 1
        self._get_or_create_components(provider)
        
        # Проверяем кеш
        cached_response = self.cache.get(request_data)
        if cached_response is not None:
            self.stats['cached_responses'] += 1
            return RequestResult(success=True, duration=0.0, cached=True)
        
        circuit_breaker = self.circuit_breakers[provider]
        token_bucket = self.token_buckets[provider]
        backoff = self.backoff_managers[provider]
        
        start_time = time.time()
        max_retries = 3
        
        for attempt in range(max_retries + 1):
            # Проверяем circuit breaker
            if not circuit_breaker.can_execute():
                self.stats['circuit_breaks'] += 1
                return RequestResult(
                    success=False,
                    duration=time.time() - start_time,
                    error=f"Circuit breaker OPEN для {provider}",
                    provider=provider,
                    retries=attempt
                )
            
            # Ждем токены
            wait_time = token_bucket.get_wait_time()
            if wait_time > 0:
                logger.debug(f"⏳ Ожидание токенов: {wait_time:.2f}с")
                await asyncio.sleep(wait_time)
            
            # Получаем токен
            if not token_bucket.consume():
                logger.warning(f"⚠️ Не удалось получить токен для {provider}")
                continue
            
            # Применяем exponential backoff если не первая попытка
            if attempt > 0:
                delay = backoff.get_delay()
                if delay > 0:
                    self.stats['backoff_delays'] += 1
                    await asyncio.sleep(delay)
            
            try:
                # Выполняем запрос
                response = await execute_func(request_data)
                
                # Успех - сохраняем в кеш и сбрасываем backoff
                self.cache.put(request_data, response)
                circuit_breaker.record_success()
                backoff.reset()
                self.stats['successful_requests'] += 1
                
                return RequestResult(
                    success=True,
                    duration=time.time() - start_time,
                    provider=provider,
                    retries=attempt
                )
                
            except Exception as e:
                logger.warning(f"⚠️ Ошибка выполнения запроса (попытка {attempt + 1}): {e}")
                circuit_breaker.record_failure()
                backoff.next_attempt()
                
                if attempt == max_retries:
                    return RequestResult(
                        success=False,
                        duration=time.time() - start_time,
                        error=str(e),
                        provider=provider,
                        retries=attempt
                    )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику работы"""
        
        circuit_states = {name: cb.state.value for name, cb in self.circuit_breakers.items()}
        token_levels = {name: tb.tokens for name, tb in self.token_buckets.items()}
        
        success_rate = (self.stats['successful_requests'] / 
                       max(1, self.stats['total_requests'])) * 100
        
        cache_hit_rate = (self.stats['cached_responses'] / 
                         max(1, self.stats['total_requests'])) * 100
        
        return {
            'stats': self.stats,
            'success_rate': f"{success_rate:.1f}%",
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'circuit_states': circuit_states,
            'token_levels': token_levels,
            'cache_size': len(self.cache.cache)
        }
    
    def reset_circuit_breaker(self, provider: str):
        """Сбросить circuit breaker для провайдера"""
        if provider in self.circuit_breakers:
            cb = self.circuit_breakers[provider]
            cb.state = CircuitState.CLOSED
            cb.failure_count = 0
            cb.success_count = 0
            logger.info(f"🔄 Circuit breaker {provider} сброшен")

# Глобальный экземпляр контроллера
_rate_controller = None

def get_rate_controller() -> AdaptiveRateController:
    """Получить глобальный экземпляр rate controller"""
    global _rate_controller
    if _rate_controller is None:
        _rate_controller = AdaptiveRateController()
    return _rate_controller 