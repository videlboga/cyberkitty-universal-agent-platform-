"""
Тесты для AIIntegrationTool - расширенной интеграции с AI провайдерами
"""

import pytest
import os
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta

from kittycore.tools.ai_integration_tool import (
    AIIntegrationTool, OpenRouterClient, ModelInfo, 
    UsageStats, ModelRotationManager, WireGuardManager
)


@pytest.fixture
def mock_api_key():
    """Фикстура с мок API ключом"""
    return "test_api_key_12345"


@pytest.fixture 
def ai_tool():
    """Фикстура для AIIntegrationTool с мокнутыми сетевыми запросами"""
    with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test_key'}), \
         patch('requests.Session.get') as mock_get, \
         patch('requests.Session.post') as mock_post, \
         patch('subprocess.run') as mock_subprocess:
        
        # Мокаем успешный ответ для get_models
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "anthropic/claude-3-sonnet",
                    "name": "Claude 3 Sonnet", 
                    "description": "Claude 3 Sonnet by Anthropic",
                    "pricing": {"prompt": 0.003, "completion": 0.015},
                    "context_length": 200000,
                    "top_provider": {"name": "Anthropic"},
                    "architecture": {"tokenizer": "claude"}
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Мокаем subprocess для WireGuard
        mock_subprocess.return_value = Mock(returncode=1, stderr="No VPN")
        
        tool = AIIntegrationTool(wireguard_config="/fake/path/config.conf")
        return tool


@pytest.fixture
def mock_model_info():
    """Фикстура с тестовой информацией о модели"""
    return ModelInfo(
        id="test/model",
        name="Test Model", 
        description="A test model",
        pricing={"prompt": 0.001, "completion": 0.002},
        context_length=4096,
        top_provider="TestProvider"
    )


@pytest.fixture
def mock_models_response():
    """Фикстура с мок ответом от API моделей"""
    return {
        "data": [
            {
                "id": "anthropic/claude-3-sonnet",
                "name": "Claude 3 Sonnet",
                "description": "Claude 3 Sonnet by Anthropic",
                "pricing": {"prompt": 0.003, "completion": 0.015},
                "context_length": 200000,
                "top_provider": {"name": "Anthropic"},
                "architecture": {"tokenizer": "claude"},
                "per_request_limits": {"max_tokens": 4096}
            },
            {
                "id": "openai/gpt-4o-mini",
                "name": "GPT-4o Mini",
                "description": "GPT-4o Mini by OpenAI",
                "pricing": {"prompt": 0.00015, "completion": 0.0006},
                "context_length": 128000,
                "top_provider": {"name": "OpenAI"},
                "architecture": {"tokenizer": "gpt"},
                "per_request_limits": {"max_tokens": 4096}
            }
        ]
    }


class TestModelInfo:
    """Тесты для класса ModelInfo"""
    
    def test_model_info_creation(self, mock_model_info):
        """Тест создания ModelInfo"""
        assert mock_model_info.id == "test/model"
        assert mock_model_info.name == "Test Model"
        assert mock_model_info.context_length == 4096
    
    def test_price_properties(self, mock_model_info):
        """Тест свойств цены"""
        assert mock_model_info.prompt_price_per_1k == 1.0
        assert mock_model_info.completion_price_per_1k == 2.0


class TestUsageStats:
    """Тесты для класса UsageStats"""
    
    def test_usage_stats_creation(self):
        """Тест создания UsageStats"""
        stats = UsageStats(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            cost_usd=0.005,
            model_used="test/model",
            timestamp=datetime.now()
        )
        
        assert stats.prompt_tokens == 100
        assert stats.completion_tokens == 50
        assert stats.total_tokens == 150
    
    def test_to_dict(self):
        """Тест преобразования в словарь"""
        timestamp = datetime.now()
        stats = UsageStats(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            cost_usd=0.005,
            model_used="test/model",
            timestamp=timestamp
        )
        
        data = stats.to_dict()
        assert data['prompt_tokens'] == 100
        assert data['total_tokens'] == 150
        assert data['model_used'] == "test/model"


class TestOpenRouterClient:
    """Тесты для класса OpenRouterClient"""
    
    def test_client_initialization(self):
        """Тест инициализации клиента"""
        client = OpenRouterClient("test_key")
        
        assert client.api_key == "test_key"
        assert client.base_url == "https://openrouter.ai/api/v1"
        assert "Authorization" in client.session.headers
    
    def test_check_model_availability(self):
        """Тест проверки доступности модели"""
        client = OpenRouterClient("test_key")
        
        # Мокаем метод get_models
        mock_models = {"test/model": Mock()}
        client.get_models = Mock(return_value=mock_models)
        
        assert client.check_model_availability("test/model") is True
        assert client.check_model_availability("nonexistent/model") is False
    
    def test_calculate_cost(self, mock_model_info):
        """Тест расчёта стоимости"""
        client = OpenRouterClient("test_key")
        
        # Мокаем get_models
        client.get_models = Mock(return_value={"test/model": mock_model_info})
        
        cost = client.calculate_cost("test/model", 1000, 500)
        
        # Ожидаемая стоимость: (1000/1000 * 0.001) + (500/1000 * 0.002) = 0.002
        assert cost == 0.002


class TestModelRotationManager:
    """Тесты для класса ModelRotationManager"""
    
    def test_rotation_manager_initialization(self, mock_api_key):
        """Тест инициализации менеджера ротации"""
        client = OpenRouterClient(mock_api_key)
        manager = ModelRotationManager(client)
        
        assert manager.client == client
        assert len(manager.model_categories) > 0
        assert 'balanced' in manager.model_categories
        assert 'fast' in manager.model_categories
    
    def test_get_available_models(self, mock_api_key):
        """Тест получения доступных моделей"""
        client = OpenRouterClient(mock_api_key)
        manager = ModelRotationManager(client)
        
        # Мокаем клиент
        mock_models = {
            "anthropic/claude-3-sonnet": Mock(),
            "openai/gpt-4o-mini": Mock(),
            "google/gemini-flash-1.5": Mock()
        }
        client.get_models = Mock(return_value=mock_models)
        
        available = manager.get_available_models('balanced')
        
        # Должны получить модели из категории balanced, которые существуют
        assert len(available) > 0
        assert any(model in available for model in ["anthropic/claude-3-sonnet", "openai/gpt-4o-mini"])
    
    def test_mark_model_failed(self, mock_api_key):
        """Тест отметки модели как недоступной"""
        client = OpenRouterClient(mock_api_key)
        manager = ModelRotationManager(client)
        
        model_id = "test/model"
        manager.mark_model_failed(model_id)
        
        assert model_id in manager.failed_models
        assert manager._is_model_failed(model_id) is True
    
    def test_model_retry_after_delay(self, mock_api_key):
        """Тест повторной попытки модели после задержки"""
        client = OpenRouterClient(mock_api_key)
        manager = ModelRotationManager(client)
        manager.retry_delay = timedelta(seconds=1)  # Короткий delay для теста
        
        model_id = "test/model"
        manager.mark_model_failed(model_id)
        
        # Сразу модель недоступна
        assert manager._is_model_failed(model_id) is True
        
        # Симулируем прошедшее время
        manager.failed_models[model_id] = datetime.now() - timedelta(seconds=2)
        
        # Теперь модель должна стать доступной
        assert manager._is_model_failed(model_id) is False
        assert model_id not in manager.failed_models


class TestWireGuardManager:
    """Тесты для класса WireGuardManager"""
    
    def test_wireguard_initialization(self):
        """Тест инициализации WireGuard менеджера"""
        config_path = "/fake/path/config.conf"
        manager = WireGuardManager(config_path)
        
        assert str(manager.config_path) == config_path
        assert manager.interface_name == "wg0"
        assert manager.is_connected is False
    
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def test_connect_success(self, mock_exists, mock_run):
        """Тест успешного подключения"""
        mock_exists.return_value = True
        mock_run.return_value = Mock(returncode=0)
        
        manager = WireGuardManager("/fake/config.conf")
        result = manager.connect()
        
        assert result is True
        assert manager.is_connected is True
    
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def test_connect_failure(self, mock_exists, mock_run):
        """Тест неудачного подключения"""
        mock_exists.return_value = True
        mock_run.return_value = Mock(returncode=1, stderr="Connection failed")
        
        manager = WireGuardManager("/fake/config.conf")
        result = manager.connect()
        
        assert result is False
        assert manager.is_connected is False
    
    @patch('pathlib.Path.exists')
    def test_connect_config_not_found(self, mock_exists):
        """Тест подключения с несуществующим конфигом"""
        mock_exists.return_value = False
        
        manager = WireGuardManager("/nonexistent/config.conf")
        result = manager.connect()
        
        assert result is False
        assert manager.is_connected is False


class TestAIIntegrationTool:
    """Тесты для основного класса AIIntegrationTool"""
    
    def test_initialization_without_api_key(self):
        """Тест инициализации без API ключа"""
        with patch.dict(os.environ, {}, clear=True):
            tool = AIIntegrationTool()
            
            assert tool.name == "ai_integration_tool"
            assert "OpenRouter" in tool.description
            assert tool.api_key is None
    
    def test_initialization_with_api_key(self, ai_tool):
        """Тест инициализации с API ключом"""
        assert ai_tool.api_key == "test_key"
        assert ai_tool.name == "ai_integration_tool"
        assert "OpenRouter" in ai_tool.description
        assert ai_tool.openrouter_client is not None
        assert ai_tool.rotation_manager is not None
    
    def test_get_schema(self, ai_tool):
        """Тест получения схемы"""
        schema = ai_tool.get_schema()
        
        assert schema['type'] == 'object'
        assert 'action' in schema['properties']
        assert 'action' in schema['required']
        
        # Проверяем основные действия
        actions = schema['properties']['action']['enum']
        assert 'list_models' in actions
        assert 'chat_completion' in actions
        assert 'get_model_info' in actions
        assert 'calculate_cost' in actions
    
    def test_list_models_without_client(self):
        """Тест получения моделей без клиента"""
        with patch.dict(os.environ, {}, clear=True):
            tool = AIIntegrationTool()
            result = tool.execute(action="list_models")
            
            assert result.success is False
            assert "не инициализирован" in result.error
    
    def test_get_stats(self, ai_tool):
        """Тест получения статистики"""
        ai_tool.total_requests = 5
        ai_tool.total_cost = 0.123
        
        result = ai_tool.execute(action="get_stats")
        
        assert result.success is True
        assert result.data['total_requests'] == 5
        assert result.data['total_cost_usd'] == 0.123
    
    def test_invalid_action(self, ai_tool):
        """Тест вызова несуществующего действия"""
        result = ai_tool.execute(action="unknown_action")
        
        assert result.success is False
        assert 'Неизвестное действие' in result.error
        assert 'available_actions' in result.data
    
    def test_calculate_cost_without_client(self):
        """Тест расчёта стоимости без клиента"""
        with patch.dict(os.environ, {}, clear=True):
            tool = AIIntegrationTool()
            result = tool.execute(
                action="calculate_cost",
                model="test/model",
                prompt_tokens=1000,
                completion_tokens=500
            )
            
            assert result.success is False
            assert "не инициализирован" in result.error
    
    def test_list_models_with_real_logic(self, ai_tool):
        """Тест получения моделей с реальной логикой"""
        result = ai_tool.execute(action="list_models", category="balanced")
        
        assert result.success is True
        assert 'models' in result.data
        assert 'categories' in result.data
        assert result.data['category'] == 'balanced'
        assert len(result.data['models']) > 0
    
    def test_model_rotation_logic(self, ai_tool):
        """Тест логики ротации моделей"""
        # Получаем доступные модели
        available = ai_tool.rotation_manager.get_available_models('balanced')
        assert len(available) > 0
        
        # Отмечаем модель как недоступную
        first_model = available[0]
        ai_tool.rotation_manager.mark_model_failed(first_model)
        
        # Проверяем что модель теперь недоступна
        assert ai_tool.rotation_manager._is_model_failed(first_model) is True 