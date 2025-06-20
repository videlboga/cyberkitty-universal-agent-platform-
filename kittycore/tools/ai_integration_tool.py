"""
AIIntegrationTool для KittyCore 3.0 - Расширенная интеграция с AI провайдерами

Фокус на OpenRouter с возможностями:
- Получение всех доступных моделей
- Умная ротация при недоступности
- Подсчёт токенов и стоимости
- Работа через VPN туннель (WireGuard)
"""

import os
import json
import time
import subprocess
import requests
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from .base_tool import Tool
from .unified_tool_result import ToolResult

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Информация о модели OpenRouter"""
    id: str
    name: str
    description: str
    pricing: Dict[str, float]  # prompt_price, completion_price
    context_length: int
    top_provider: str
    per_request_limits: Optional[Dict] = None
    architecture: Optional[str] = None
    
    @property
    def prompt_price_per_1k(self) -> float:
        """Цена за 1K токенов prompt"""
        price = self.pricing.get('prompt', 0)
        return float(price) if isinstance(price, (int, float, str)) else 0.0
    
    @property
    def completion_price_per_1k(self) -> float:
        """Цена за 1K токенов completion"""
        price = self.pricing.get('completion', 0)
        return float(price) if isinstance(price, (int, float, str)) else 0.0


@dataclass
class UsageStats:
    """Статистика использования"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    model_used: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'cost_usd': self.cost_usd,
            'model_used': self.model_used,
            'timestamp': self.timestamp.isoformat()
        }


class OpenRouterClient:
    """Клиент для работы с OpenRouter API"""
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/cyberkitty/kittycore",
            "X-Title": "KittyCore 3.0"
        })
        
        # Кеш моделей и их состояний
        self.models_cache: Dict[str, ModelInfo] = {}
        self.models_cache_time: Optional[datetime] = None
        self.cache_duration = timedelta(hours=1)
        
        # Статистика использования
        self.usage_stats: List[UsageStats] = []
        
        logger.info("OpenRouter клиент инициализирован")
    
    def get_models(self, force_refresh: bool = False) -> Dict[str, ModelInfo]:
        """Получение списка всех доступных моделей"""
        try:
            # Проверяем кеш
            if (not force_refresh and 
                self.models_cache and 
                self.models_cache_time and 
                datetime.now() - self.models_cache_time < self.cache_duration):
                logger.debug("Используем кешированный список моделей")
                return self.models_cache
            
            # Запрос к API
            response = self.session.get(f"{self.base_url}/models")
            response.raise_for_status()
            
            models_data = response.json()
            models = {}
            
            for model_data in models_data.get('data', []):
                model_info = ModelInfo(
                    id=model_data['id'],
                    name=model_data.get('name', model_data['id']),
                    description=model_data.get('description', ''),
                    pricing=model_data.get('pricing', {}),
                    context_length=model_data.get('context_length', 0),
                    top_provider=model_data.get('top_provider', {}).get('name', 'Unknown'),
                    per_request_limits=model_data.get('per_request_limits'),
                    architecture=model_data.get('architecture', {}).get('tokenizer')
                )
                models[model_info.id] = model_info
            
            # Обновляем кеш
            self.models_cache = models
            self.models_cache_time = datetime.now()
            
            logger.info(f"Получено {len(models)} моделей от OpenRouter")
            return models
            
        except Exception as e:
            logger.error(f"Ошибка получения моделей: {e}")
            # Возвращаем кеш если есть
            return self.models_cache if self.models_cache else {}
    
    def check_model_availability(self, model_id: str) -> bool:
        """Проверка доступности модели"""
        try:
            models = self.get_models()
            return model_id in models
        except Exception as e:
            logger.error(f"Ошибка проверки доступности модели {model_id}: {e}")
            return False
    
    def calculate_cost(self, model_id: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Расчёт стоимости запроса"""
        try:
            models = self.get_models()
            if model_id not in models:
                logger.warning(f"Модель {model_id} не найдена для расчёта стоимости")
                return 0.0
            
            model = models[model_id]
            
            # Безопасное получение цен с преобразованием в float
            prompt_price = model.pricing.get('prompt', 0)
            completion_price = model.pricing.get('completion', 0)
            
            try:
                prompt_price = float(prompt_price) if prompt_price else 0.0
                completion_price = float(completion_price) if completion_price else 0.0
            except (ValueError, TypeError):
                prompt_price = 0.0
                completion_price = 0.0
            
            prompt_cost = (prompt_tokens / 1000) * prompt_price
            completion_cost = (completion_tokens / 1000) * completion_price
            
            total_cost = prompt_cost + completion_cost
            logger.debug(f"Стоимость для {model_id}: ${total_cost:.6f} ({prompt_tokens}+{completion_tokens} токенов)")
            
            return total_cost
            
        except Exception as e:
            logger.error(f"Ошибка расчёта стоимости: {e}")
            return 0.0


class WireGuardManager:
    """Менеджер WireGuard VPN соединения"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.interface_name = "wg0"  # Стандартное имя интерфейса
        self.is_connected = False
        
        logger.info(f"WireGuard менеджер инициализирован с конфигом: {config_path}")
    
    def connect(self) -> bool:
        """Подключение к VPN"""
        try:
            if not self.config_path.exists():
                logger.error(f"Конфиг WireGuard не найден: {self.config_path}")
                return False
            
            # Проверяем уже подключены ли
            if self.is_connected:
                logger.info("WireGuard уже подключен")
                return True
            
            # Подключаемся
            cmd = ["sudo", "wg-quick", "up", str(self.config_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.is_connected = True
                logger.info("WireGuard VPN подключен успешно")
                return True
            else:
                logger.error(f"Ошибка подключения WireGuard: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Таймаут подключения WireGuard")
            return False
        except Exception as e:
            logger.error(f"Ошибка подключения WireGuard: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Отключение от VPN"""
        try:
            if not self.is_connected:
                logger.info("WireGuard уже отключен")
                return True
            
            cmd = ["sudo", "wg-quick", "down", str(self.config_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.is_connected = False
                logger.info("WireGuard VPN отключен успешно")
                return True
            else:
                logger.error(f"Ошибка отключения WireGuard: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка отключения WireGuard: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса VPN соединения"""
        try:
            cmd = ["sudo", "wg", "show"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                # Парсим вывод wg show
                lines = result.stdout.strip().split('\n')
                interface = lines[0].split(':')[0] if lines else None
                
                return {
                    'connected': True,
                    'interface': interface,
                    'output': result.stdout
                }
            else:
                return {
                    'connected': False,
                    'interface': None,
                    'output': ''
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения статуса WireGuard: {e}")
            return {
                'connected': False,
                'interface': None,
                'error': str(e)
            }


class ModelRotationManager:
    """Менеджер ротации моделей при недоступности"""
    
    def __init__(self, openrouter_client: OpenRouterClient):
        self.client = openrouter_client
        self.failed_models: Dict[str, datetime] = {}
        self.retry_delay = timedelta(minutes=5)  # Повторная попытка через 5 минут
        
        # Приоритеты моделей по категориям
        self.model_categories = {
            'fast': ['google/gemini-flash-1.5', 'anthropic/claude-3-haiku', 'openai/gpt-3.5-turbo'],
            'balanced': ['anthropic/claude-3-sonnet', 'openai/gpt-4o-mini', 'google/gemini-pro-1.5'],
            'powerful': ['anthropic/claude-3-opus', 'openai/gpt-4o', 'google/gemini-pro'],
            'coding': ['anthropic/claude-3-sonnet', 'openai/gpt-4o', 'deepseek/deepseek-coder'],
            'cheap': ['google/gemini-flash-1.5', 'anthropic/claude-3-haiku', 'openai/gpt-3.5-turbo']
        }
        
        logger.info("Менеджер ротации моделей инициализирован")
    
    def get_available_models(self, category: str = 'balanced') -> List[str]:
        """Получение доступных моделей в категории"""
        try:
            all_models = self.client.get_models()
            category_models = self.model_categories.get(category, self.model_categories['balanced'])
            
            available_models = []
            for model_id in category_models:
                # Проверяем что модель существует и не в блэклисте
                if (model_id in all_models and 
                    not self._is_model_failed(model_id)):
                    available_models.append(model_id)
            
            # Если нет доступных моделей в категории, берём любые доступные
            if not available_models:
                available_models = [m for m in all_models.keys() 
                                  if not self._is_model_failed(m)][:5]  # Топ 5
            
            logger.debug(f"Доступные модели в категории '{category}': {available_models}")
            return available_models
            
        except Exception as e:
            logger.error(f"Ошибка получения доступных моделей: {e}")
            return []
    
    def mark_model_failed(self, model_id: str):
        """Отметить модель как недоступную"""
        self.failed_models[model_id] = datetime.now()
        logger.warning(f"Модель {model_id} отмечена как недоступная")
    
    def _is_model_failed(self, model_id: str) -> bool:
        """Проверка, находится ли модель в блэклисте"""
        if model_id not in self.failed_models:
            return False
        
        # Если прошло достаточно времени, убираем из блэклиста
        fail_time = self.failed_models[model_id]
        if datetime.now() - fail_time > self.retry_delay:
            del self.failed_models[model_id]
            logger.info(f"Модель {model_id} возвращена в доступные")
            return False
        
        return True
    
    def get_best_model(self, category: str = 'balanced', max_cost_per_1k: float = None) -> Optional[str]:
        """Получение лучшей доступной модели"""
        try:
            available_models = self.get_available_models(category)
            if not available_models:
                return None
            
            # Если есть ограничение по стоимости, фильтруем
            if max_cost_per_1k is not None:
                all_models = self.client.get_models()
                filtered_models = []
                
                for model_id in available_models:
                    if model_id in all_models:
                        model = all_models[model_id]
                        total_cost = model.prompt_price_per_1k + model.completion_price_per_1k
                        if total_cost <= max_cost_per_1k:
                            filtered_models.append(model_id)
                
                available_models = filtered_models
            
            # Возвращаем первую доступную модель (приоритет по порядку)
            return available_models[0] if available_models else None
            
        except Exception as e:
            logger.error(f"Ошибка выбора лучшей модели: {e}")
            return None


class AIIntegrationTool(Tool):
    """
    Расширенный инструмент интеграции с AI провайдерами
    
    Фокус на OpenRouter с возможностями:
    - Получение всех доступных моделей
    - Умная ротация при недоступности
    - Подсчёт токенов и стоимости
    - Работа через VPN туннель
    """
    
    def __init__(self, wireguard_config: str = "/home/cyberkitty/Документы/wireguard-kirish.conf"):
        super().__init__(
            name="ai_integration_tool",
            description="Расширенная интеграция с AI провайдерами через OpenRouter с VPN туннелем"
        )
        
        # Получаем API ключ из переменных окружения
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY не установлен. Используйте: export OPENROUTER_API_KEY=your_key")
        
        # Инициализируем компоненты
        self.openrouter_client = None
        self.wireguard_manager = WireGuardManager(wireguard_config)
        self.rotation_manager = None
        
        # Инициализируем клиенты если есть API ключ
        if self.api_key:
            self._initialize_clients()
        
        # Статистика использования
        self.total_requests = 0
        self.total_cost = 0.0
        self.session_stats: List[UsageStats] = []
        
        logger.info("AIIntegrationTool инициализирован")
    
    def _initialize_clients(self):
        """Инициализация клиентов API"""
        try:
            self.openrouter_client = OpenRouterClient(self.api_key)
            self.rotation_manager = ModelRotationManager(self.openrouter_client)
            logger.info("Клиенты OpenRouter инициализированы успешно")
        except Exception as e:
            logger.error(f"Ошибка инициализации клиентов: {e}")
    
    def get_schema(self) -> Dict[str, Any]:
        """JSON Schema для валидации параметров"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Действие для выполнения",
                    "enum": [
                        "list_models", "chat_completion", "get_model_info",
                        "calculate_cost", "get_stats", "connect_vpn", 
                        "disconnect_vpn", "vpn_status", "test_connection"
                    ]
                },
                "model": {
                    "type": "string",
                    "description": "ID модели для использования"
                },
                "messages": {
                    "type": "array",
                    "description": "Массив сообщений для chat completion",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string", "enum": ["user", "assistant", "system"]},
                            "content": {"type": "string"}
                        },
                        "required": ["role", "content"]
                    }
                },
                "category": {
                    "type": "string",
                    "description": "Категория модели для автовыбора",
                    "enum": ["fast", "balanced", "powerful", "coding", "cheap"],
                    "default": "balanced"
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Максимальное количество токенов в ответе",
                    "minimum": 1,
                    "maximum": 4096,
                    "default": 1024
                },
                "temperature": {
                    "type": "number",
                    "description": "Температура для генерации (0.0-2.0)",
                    "minimum": 0.0,
                    "maximum": 2.0,
                    "default": 0.7
                },
                "max_cost_per_1k": {
                    "type": "number",
                    "description": "Максимальная стоимость за 1K токенов (USD)",
                    "minimum": 0.0
                },
                "use_vpn": {
                    "type": "boolean",
                    "description": "Использовать VPN для запросов",
                    "default": False
                }
            },
            "required": ["action"]
        }
    
    def execute(self, action: str, **kwargs) -> ToolResult:
        """Выполнение действий с AI провайдерами"""
        try:
            # Проверяем VPN если требуется
            if kwargs.get('use_vpn', False):
                vpn_status = self.wireguard_manager.get_status()
                if not vpn_status.get('connected', False):
                    if not self.wireguard_manager.connect():
                        return ToolResult(
                            success=False,
                            error="Не удалось подключиться к VPN"
                        )
            
            # Выполняем действие
            if action == "list_models":
                return self._list_models(**kwargs)
            elif action == "chat_completion":
                return self._chat_completion(**kwargs)
            elif action == "get_model_info":
                return self._get_model_info(**kwargs)
            elif action == "calculate_cost":
                return self._calculate_cost(**kwargs)
            elif action == "get_stats":
                return self._get_stats()
            elif action == "connect_vpn":
                return self._connect_vpn()
            elif action == "disconnect_vpn":
                return self._disconnect_vpn()
            elif action == "vpn_status":
                return self._vpn_status()
            elif action == "test_connection":
                return self._test_connection(**kwargs)
            else:
                return ToolResult(
                    success=False,
                    error=f'Неизвестное действие: {action}',
                    data={
                        'available_actions': [
                            'list_models', 'chat_completion', 'get_model_info',
                            'calculate_cost', 'get_stats', 'connect_vpn',
                            'disconnect_vpn', 'vpn_status', 'test_connection'
                        ]
                    }
                )
                
        except Exception as e:
            logger.error(f"Ошибка в AIIntegrationTool.execute: {e}")
            return ToolResult(success=False, error=str(e))
    
    def _list_models(self, category: str = 'balanced', force_refresh: bool = False) -> ToolResult:
        """Получение списка доступных моделей"""
        try:
            if not self.openrouter_client:
                return ToolResult(
                    success=False,
                    error="OpenRouter клиент не инициализирован. Установите OPENROUTER_API_KEY"
                )
            
            models = self.openrouter_client.get_models(force_refresh=force_refresh)
            available_models = self.rotation_manager.get_available_models(category)
            
            # Формируем детальный ответ
            models_info = []
            for model_id in available_models:
                if model_id in models:
                    model = models[model_id]
                    models_info.append({
                        'id': model.id,
                        'name': model.name,
                        'description': model.description[:100] + '...' if len(model.description) > 100 else model.description,
                        'context_length': model.context_length,
                        'provider': model.top_provider,
                        'prompt_price_per_1k': model.prompt_price_per_1k,
                        'completion_price_per_1k': model.completion_price_per_1k
                    })
            
            result_data = {
                'category': category,
                'total_models': len(models),
                'available_in_category': len(available_models),
                'models': models_info,
                'categories': list(self.rotation_manager.model_categories.keys())
            }
            
            logger.info(f"Получено {len(models_info)} моделей в категории '{category}'")
            
            return ToolResult(
                success=True,
                data=result_data
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка получения моделей: {str(e)}')
    
    def _chat_completion(self, messages: List[Dict], model: str = None, 
                        category: str = 'balanced', max_tokens: int = 1024,
                        temperature: float = 0.7, max_cost_per_1k: float = None) -> ToolResult:
        """Выполнение chat completion запроса"""
        try:
            if not self.openrouter_client:
                return ToolResult(
                    success=False,
                    error="OpenRouter клиент не инициализирован"
                )
            
            # Выбор модели
            if not model:
                model = self.rotation_manager.get_best_model(category, max_cost_per_1k)
                if not model:
                    return ToolResult(
                        success=False,
                        error=f"Нет доступных моделей в категории '{category}'"
                    )
            
            start_time = time.time()
            
            # Выполняем запрос с ротацией при ошибках
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Подготавливаем запрос
                    request_data = {
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "stream": False
                    }
                    
                    # Отправляем запрос
                    response = self.openrouter_client.session.post(
                        f"{self.openrouter_client.base_url}/chat/completions",
                        json=request_data,
                        timeout=60
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    
                    # Извлекаем данные о использовании
                    usage = result.get('usage', {})
                    prompt_tokens = usage.get('prompt_tokens', 0)
                    completion_tokens = usage.get('completion_tokens', 0)
                    total_tokens = usage.get('total_tokens', prompt_tokens + completion_tokens)
                    
                    # Рассчитываем стоимость
                    cost = self.openrouter_client.calculate_cost(model, prompt_tokens, completion_tokens)
                    
                    # Сохраняем статистику
                    stats = UsageStats(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        cost_usd=cost,
                        model_used=model,
                        timestamp=datetime.now()
                    )
                    self.session_stats.append(stats)
                    self.total_requests += 1
                    self.total_cost += cost
                    
                    # Формируем результат
                    completion_data = {
                        'model_used': model,
                        'response': result.get('choices', [{}])[0].get('message', {}).get('content', ''),
                        'usage': {
                            'prompt_tokens': prompt_tokens,
                            'completion_tokens': completion_tokens,
                            'total_tokens': total_tokens
                        },
                        'cost_usd': round(cost, 6),
                        'response_time': round(time.time() - start_time, 2),
                        'attempt': attempt + 1
                    }
                    
                    logger.info(f"Запрос выполнен успешно: {model}, токены: {total_tokens}, стоимость: ${cost:.6f}")
                    
                    return ToolResult(
                        success=True,
                        data=completion_data
                    )
                    
                except requests.exceptions.RequestException as e:
                    # Отмечаем модель как проблемную и пробуем следующую
                    logger.warning(f"Ошибка с моделью {model} (попытка {attempt + 1}): {e}")
                    self.rotation_manager.mark_model_failed(model)
                    
                    if attempt < max_retries - 1:
                        # Пробуем другую модель
                        new_model = self.rotation_manager.get_best_model(category, max_cost_per_1k)
                        if new_model and new_model != model:
                            model = new_model
                            logger.info(f"Переключаемся на модель: {model}")
                            continue
                    
                    # Если это последняя попытка или нет других моделей
                    if attempt == max_retries - 1:
                        return ToolResult(
                            success=False,
                            error=f"Не удалось выполнить запрос после {max_retries} попыток: {str(e)}"
                        )
            
            return ToolResult(
                success=False,
                error="Неожиданная ошибка в цикле ротации"
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка выполнения запроса: {str(e)}')
    
    def _get_model_info(self, model: str) -> ToolResult:
        """Получение детальной информации о модели"""
        try:
            if not self.openrouter_client:
                return ToolResult(
                    success=False,
                    error="OpenRouter клиент не инициализирован"
                )
            
            models = self.openrouter_client.get_models()
            
            if model not in models:
                return ToolResult(
                    success=False,
                    error=f"Модель '{model}' не найдена"
                )
            
            model_info = models[model]
            
            # Детальная информация
            info_data = {
                'id': model_info.id,
                'name': model_info.name,
                'description': model_info.description,
                'context_length': model_info.context_length,
                'top_provider': model_info.top_provider,
                'architecture': model_info.architecture,
                'pricing': {
                    'prompt_per_1k_usd': model_info.prompt_price_per_1k,
                    'completion_per_1k_usd': model_info.completion_price_per_1k,
                    'total_per_1k_usd': model_info.prompt_price_per_1k + model_info.completion_price_per_1k
                },
                'per_request_limits': model_info.per_request_limits,
                'is_available': not self.rotation_manager._is_model_failed(model) if self.rotation_manager else True
            }
            
            # Определяем в каких категориях модель
            categories = []
            for cat, models_list in self.rotation_manager.model_categories.items():
                if model in models_list:
                    categories.append(cat)
            info_data['categories'] = categories
            
            logger.info(f"Получена информация о модели: {model}")
            
            return ToolResult(
                success=True,
                data=info_data
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка получения информации о модели: {str(e)}')
    
    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> ToolResult:
        """Расчёт стоимости запроса"""
        try:
            if not self.openrouter_client:
                return ToolResult(
                    success=False,
                    error="OpenRouter клиент не инициализирован"
                )
            
            cost = self.openrouter_client.calculate_cost(model, prompt_tokens, completion_tokens)
            
            models = self.openrouter_client.get_models()
            model_info = models.get(model)
            
            if model_info:
                cost_data = {
                    'model': model,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': prompt_tokens + completion_tokens,
                    'cost_breakdown': {
                        'prompt_cost_usd': (prompt_tokens / 1000) * float(model_info.pricing.get('prompt', 0) or 0),
                        'completion_cost_usd': (completion_tokens / 1000) * float(model_info.pricing.get('completion', 0) or 0)
                    },
                    'total_cost_usd': cost,
                    'pricing_per_1k': {
                        'prompt': model_info.prompt_price_per_1k,
                        'completion': model_info.completion_price_per_1k
                    }
                }
            else:
                cost_data = {
                    'model': model,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': prompt_tokens + completion_tokens,
                    'total_cost_usd': cost,
                    'note': 'Модель не найдена в списке доступных'
                }
            
            return ToolResult(
                success=True,
                data=cost_data
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка расчёта стоимости: {str(e)}')

    def _get_stats(self) -> ToolResult:
        """Получение статистики использования"""
        try:
            stats_data = {
                'total_requests': self.total_requests,
                'total_cost_usd': self.total_cost,
                'session_stats': [stats.to_dict() for stats in self.session_stats],
                'total_models': len(self.openrouter_client.get_models())
            }
            
            logger.info("Получена статистика использования")
            
            return ToolResult(
                success=True,
                data=stats_data
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка получения статистики: {str(e)}')

    def _connect_vpn(self) -> ToolResult:
        """Подключение к VPN"""
        try:
            if not self.wireguard_manager.connect():
                return ToolResult(
                    success=False,
                    error="Не удалось подключиться к VPN"
                )
            
            return ToolResult(
                success=True,
                data={
                    'status': self.wireguard_manager.get_status()
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка подключения к VPN: {str(e)}')

    def _disconnect_vpn(self) -> ToolResult:
        """Отключение от VPN"""
        try:
            if not self.wireguard_manager.disconnect():
                return ToolResult(
                    success=False,
                    error="Не удалось отключиться от VPN"
                )
            
            return ToolResult(
                success=True,
                data={
                    'status': self.wireguard_manager.get_status()
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка отключения от VPN: {str(e)}')

    def _vpn_status(self) -> ToolResult:
        """Получение статуса VPN соединения"""
        try:
            status = self.wireguard_manager.get_status()
            
            if status.get('connected', False):
                return ToolResult(
                    success=True,
                    data={
                        'status': status
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error="VPN не подключен"
                )
                
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка получения статуса VPN: {str(e)}')

    def _test_connection(self, **kwargs) -> ToolResult:
        """Тестирование соединения с OpenRouter"""
        try:
            if not self.openrouter_client:
                return ToolResult(
                    success=False,
                    error="OpenRouter клиент не инициализирован"
                )
            
            # Проверяем доступность модели
            model = self.rotation_manager.get_best_model()
            if not model:
                return ToolResult(
                    success=False,
                    error="Не удалось получить доступную модель"
                )
            
            # Проверяем доступность модели через OpenRouter
            if not self.openrouter_client.check_model_availability(model):
                return ToolResult(
                    success=False,
                    error="Модель не найдена в списке доступных моделей OpenRouter"
                )
            
            return ToolResult(
                success=True,
                data={
                    'model': model,
                    'status': self.openrouter_client.check_model_availability(model)
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f'Ошибка тестирования соединения: {str(e)}') 