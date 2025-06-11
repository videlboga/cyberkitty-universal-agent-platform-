#!/usr/bin/env python3
"""
🧪 ТЕСТЫ HTTP ПЛАГИНА
Тестирует SimpleHTTPPlugin для внешних HTTP запросов.
Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from app.plugins.simple_http_plugin import SimpleHTTPPlugin


@pytest.fixture
def http_plugin():
    """Создает экземпляр HTTP плагина для тестов."""
    return SimpleHTTPPlugin()


@pytest.mark.asyncio
async def test_plugin_initialization(http_plugin):
    """Тест инициализации плагина."""
    assert http_plugin.name == "simple_http"
    assert http_plugin.default_timeout == 30.0
    assert "User-Agent" in http_plugin.default_headers
    
    # Тест инициализации
    await http_plugin.initialize()
    # Проверяем что плагин инициализирован (базовый класс устанавливает флаг)
    assert hasattr(http_plugin, 'name')


@pytest.mark.asyncio
async def test_register_handlers(http_plugin):
    """Тест регистрации обработчиков."""
    handlers = http_plugin.register_handlers()
    
    expected_handlers = [
        "http_get",
        "http_post", 
        "http_put",
        "http_delete",
        "http_request"
    ]
    
    for handler_name in expected_handlers:
        assert handler_name in handlers
        assert callable(handlers[handler_name])


@pytest.mark.asyncio
async def test_http_get_success(http_plugin):
    """Тест успешного GET запроса."""
    # Мокаем HTTP ответ
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "data": "test"}
    mock_response.text = "test response"
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.url = "https://httpbin.org/get"
    mock_response.reason_phrase = "OK"
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
        
        step_data = {
            "id": "test_get",
            "type": "http_get",
            "params": {
                "url": "https://httpbin.org/get",
                "output_var": "get_result"
            }
        }
        context = {}
        
        result_context = await http_plugin._handle_http_get(step_data, context)
        
        assert "get_result" in result_context
        assert result_context["get_result"]["success"] is True
        assert result_context["get_result"]["status_code"] == 200
        # Проверяем что data содержит ожидаемые данные
        data = result_context["get_result"]["data"]
        assert isinstance(data, dict)
        assert data["success"] is True


@pytest.mark.asyncio
async def test_http_post_with_json(http_plugin):
    """Тест POST запроса с JSON данными."""
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 123, "created": True}
    mock_response.text = "created response"
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.url = "https://httpbin.org/post"
    mock_response.reason_phrase = "Created"
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
        
        step_data = {
            "id": "test_post",
            "type": "http_post",
            "params": {
                "url": "https://httpbin.org/post",
                "json": {
                    "name": "Test User",
                    "email": "test@example.com"
                },
                "output_var": "post_result"
            }
        }
        context = {}
        
        result_context = await http_plugin._handle_http_post(step_data, context)
        
        assert "post_result" in result_context
        assert result_context["post_result"]["success"] is True
        assert result_context["post_result"]["status_code"] == 201


@pytest.mark.asyncio
async def test_http_request_universal(http_plugin):
    """Тест универсального HTTP запроса."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"updated": True}
    mock_response.text = "updated response"
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.url = "https://httpbin.org/put"
    mock_response.reason_phrase = "OK"
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
        
        step_data = {
            "id": "test_universal",
            "type": "http_request",
            "params": {
                "method": "PUT",
                "url": "https://httpbin.org/put",
                "json": {"status": "updated"},
                "headers": {"Authorization": "Bearer token123"},
                "output_var": "universal_result"
            }
        }
        context = {}
        
        result_context = await http_plugin._handle_http_request(step_data, context)
        
        assert "universal_result" in result_context
        assert result_context["universal_result"]["success"] is True
        assert result_context["universal_result"]["status_code"] == 200


@pytest.mark.asyncio
async def test_http_error_handling(http_plugin):
    """Тест обработки HTTP ошибок."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.json.side_effect = Exception("Not JSON")  # Имитируем ошибку парсинга JSON
    mock_response.headers = {"Content-Type": "text/plain"}
    mock_response.url = "https://httpbin.org/status/404"
    mock_response.reason_phrase = "Not Found"
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
        
        step_data = {
            "id": "test_error",
            "type": "http_get",
            "params": {
                "url": "https://httpbin.org/status/404",
                "output_var": "error_result"
            }
        }
        context = {}
        
        result_context = await http_plugin._handle_http_get(step_data, context)
        
        assert "error_result" in result_context
        assert result_context["error_result"]["success"] is False
        assert result_context["error_result"]["status_code"] == 404
        assert "error" in result_context["error_result"]


@pytest.mark.asyncio
async def test_context_variable_resolution(http_plugin):
    """Тест подстановки переменных из контекста."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"user_id": 123}
    mock_response.text = "user response"
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.url = "https://api.example.com/users/123"
    mock_response.reason_phrase = "OK"
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
        
        step_data = {
            "id": "test_variables",
            "type": "http_get",
            "params": {
                "url": "https://api.example.com/users/{user_id}",
                "output_var": "user_data"
            }
        }
        context = {"user_id": "123"}
        
        result_context = await http_plugin._handle_http_get(step_data, context)
        
        # Проверяем что переменная была подставлена
        mock_client.return_value.__aenter__.return_value.request.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.request.call_args
        assert "https://api.example.com/users/123" in str(call_args)


@pytest.mark.asyncio
async def test_missing_url_error(http_plugin):
    """Тест обработки отсутствующего URL."""
    step_data = {
        "id": "test_no_url",
        "type": "http_get",
        "params": {
            "output_var": "result"
        }
    }
    context = {}
    
    result_context = await http_plugin._handle_http_get(step_data, context)
    
    assert "result" in result_context
    assert result_context["result"]["success"] is False
    assert "URL не указан" in result_context["result"]["error"]


@pytest.mark.asyncio
async def test_network_error_handling(http_plugin):
    """Тест обработки сетевых ошибок."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.request = AsyncMock(
            side_effect=Exception("Network error")
        )
        
        step_data = {
            "id": "test_network_error",
            "type": "http_get",
            "params": {
                "url": "https://unreachable.example.com",
                "output_var": "network_result"
            }
        }
        context = {}
        
        result_context = await http_plugin._handle_http_get(step_data, context)
        
        assert "network_result" in result_context
        assert result_context["network_result"]["success"] is False
        assert "Network error" in result_context["network_result"]["error"]


@pytest.mark.asyncio
async def test_healthcheck_success(http_plugin):
    """Тест успешного healthcheck."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_response.text = "OK"
    mock_response.headers = {}
    mock_response.url = "https://httpbin.org/status/200"
    mock_response.reason_phrase = "OK"
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
        
        result = await http_plugin.healthcheck()
        assert result is True


@pytest.mark.asyncio
async def test_healthcheck_failure(http_plugin):
    """Тест неуспешного healthcheck."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.request = AsyncMock(
            side_effect=Exception("Connection failed")
        )
        
        result = await http_plugin.healthcheck()
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 