"""
Тесты для SimpleAmoCRMPlugin
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import os
import json

from app.plugins.simple_amocrm_plugin import SimpleAmoCRMPlugin


@pytest.fixture
def amocrm_plugin():
    """Фикстура для создания экземпляра плагина"""
    with patch.dict(os.environ, {
        'AMO_BASE_URL': 'https://test.amocrm.ru',
        'AMO_ACCESS_TOKEN': 'test_token'
    }):
        plugin = SimpleAmoCRMPlugin()
        return plugin


@pytest.fixture
def mock_fields_map():
    """Мок карты полей"""
    return {
        "telegram_id": {
            "id": 123456,
            "name": "Telegram ID",
            "type": "text",
            "code": "TELEGRAM_ID"
        },
        "phone": {
            "id": 123458,
            "name": "Телефон",
            "type": "multiphonemail",
            "code": "PHONE",
            "enums": [
                {"id": 1, "value": "WORK", "enum_code": "WORK"},
                {"id": 2, "value": "MOBILE", "enum_code": "MOBILE"}
            ]
        },
        "source": {
            "id": 123460,
            "name": "Источник",
            "type": "select",
            "code": "SOURCE",
            "enums": [
                {"id": 1, "value": "Telegram", "enum_code": "TELEGRAM"},
                {"id": 2, "value": "Сайт", "enum_code": "WEBSITE"}
            ]
        }
    }


class TestSimpleAmoCRMPlugin:
    """Тесты для SimpleAmoCRMPlugin"""
    
    def test_plugin_initialization(self, amocrm_plugin):
        """Тест инициализации плагина"""
        assert amocrm_plugin.name == "simple_amocrm"
        assert amocrm_plugin.base_url == "https://test.amocrm.ru"
        assert amocrm_plugin.access_token == "test_token"
        assert "Authorization" in amocrm_plugin.headers
        assert amocrm_plugin.headers["Authorization"] == "Bearer test_token"
    
    def test_register_handlers(self, amocrm_plugin):
        """Тест регистрации обработчиков"""
        handlers = amocrm_plugin.register_handlers()
        
        expected_handlers = [
            "amocrm_find_contact",
            "amocrm_create_contact", 
            "amocrm_update_contact",
            "amocrm_find_lead",
            "amocrm_create_lead",
            "amocrm_add_note",
            "amocrm_search"
        ]
        
        for handler in expected_handlers:
            assert handler in handlers
            assert callable(handlers[handler])
    
    def test_get_enum_id(self, mock_fields_map):
        """Тест получения ID enum значения"""
        phone_field = mock_fields_map["phone"]
        
        # Поиск по значению
        enum_id = SimpleAmoCRMPlugin._get_enum_id(phone_field, value="WORK")
        assert enum_id == 1
        
        # Поиск по коду
        enum_id = SimpleAmoCRMPlugin._get_enum_id(phone_field, code="MOBILE")
        assert enum_id == 2
        
        # Значение по умолчанию
        enum_id = SimpleAmoCRMPlugin._get_enum_id(phone_field, code="WORK")
        assert enum_id == 1
        
        # Первое доступное
        enum_id = SimpleAmoCRMPlugin._get_enum_id(phone_field, code="UNKNOWN")
        assert enum_id == 1
    
    def test_prepare_custom_fields(self, amocrm_plugin, mock_fields_map):
        """Тест подготовки кастомных полей"""
        amocrm_plugin.fields_map = mock_fields_map
        
        data = {
            "telegram_id": "123456789",
            "phone": "+7900123456",
            "source": "Telegram"
        }
        
        custom_fields = amocrm_plugin._prepare_custom_fields(data)
        
        assert len(custom_fields) == 3
        
        # Проверяем текстовое поле
        telegram_field = next(f for f in custom_fields if f["field_id"] == 123456)
        assert telegram_field["values"][0]["value"] == "123456789"
        
        # Проверяем поле с enum
        phone_field = next(f for f in custom_fields if f["field_id"] == 123458)
        assert phone_field["values"][0]["value"] == "+7900123456"
        assert "enum_id" in phone_field["values"][0]
        
        # Проверяем select поле
        source_field = next(f for f in custom_fields if f["field_id"] == 123460)
        assert source_field["values"][0]["enum_id"] == 1
    
    def test_resolve_value(self, amocrm_plugin):
        """Тест подстановки переменных"""
        context = {"user_id": "123", "name": "Тест"}
        
        # Простое значение
        result = amocrm_plugin._resolve_value("простой текст", context)
        assert result == "простой текст"
        
        # Подстановка переменной
        result = amocrm_plugin._resolve_value("Пользователь {user_id}", context)
        assert result == "Пользователь 123"
        
        # Несколько переменных
        result = amocrm_plugin._resolve_value("ID: {user_id}, Имя: {name}", context)
        assert result == "ID: 123, Имя: Тест"
        
        # Отсутствующая переменная
        result = amocrm_plugin._resolve_value("Значение: {missing}", context)
        assert result == "Значение: {missing}"  # Остается как есть
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, amocrm_plugin):
        """Тест успешного HTTP запроса"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": "test"}
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            
            result = await amocrm_plugin._make_request("GET", "/api/v4/contacts")
            
            assert result["success"] is True
            assert result["status_code"] == 200
            assert result["data"] == {"success": True, "data": "test"}
    
    @pytest.mark.asyncio
    async def test_make_request_error(self, amocrm_plugin):
        """Тест HTTP запроса с ошибкой"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad Request"}
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)
            
            result = await amocrm_plugin._make_request("GET", "/api/v4/contacts")
            
            assert result["success"] is False
            assert result["status_code"] == 400
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_make_request_no_config(self):
        """Тест запроса без настроек"""
        with patch.dict(os.environ, {}, clear=True):
            plugin = SimpleAmoCRMPlugin()
            
            result = await plugin._make_request("GET", "/api/v4/contacts")
            
            assert result["success"] is False
            assert "не настроен" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handle_find_contact(self, amocrm_plugin):
        """Тест поиска контакта"""
        step_data = {
            "params": {
                "telegram_id": "123456789",
                "output_var": "found_contact"
            }
        }
        context = {}
        
        # Мокаем метод поиска
        mock_result = {"success": True, "contact": {"id": 12345}, "found": True}
        amocrm_plugin._find_contact_by_telegram_id = AsyncMock(return_value=mock_result)
        
        await amocrm_plugin._handle_find_contact(step_data, context)
        
        assert "found_contact" in context
        assert context["found_contact"]["success"] is True
        assert context["found_contact"]["contact"]["id"] == 12345
    
    @pytest.mark.asyncio
    async def test_handle_create_contact(self, amocrm_plugin):
        """Тест создания контакта"""
        step_data = {
            "params": {
                "name": "Тест Пользователь",
                "first_name": "Тест",
                "last_name": "Пользователь",
                "custom_fields": {
                    "telegram_id": "123456789"
                },
                "output_var": "new_contact"
            }
        }
        context = {}
        
        # Мокаем метод создания
        mock_result = {"success": True, "contact": {"id": 12345}, "contact_id": 12345}
        amocrm_plugin._create_contact = AsyncMock(return_value=mock_result)
        
        await amocrm_plugin._handle_create_contact(step_data, context)
        
        assert "new_contact" in context
        assert context["new_contact"]["success"] is True
        assert context["new_contact"]["contact_id"] == 12345
    
    @pytest.mark.asyncio
    async def test_handle_create_lead(self, amocrm_plugin):
        """Тест создания сделки"""
        step_data = {
            "params": {
                "name": "Тестовая сделка",
                "price": 50000,
                "contact_id": 12345,
                "output_var": "new_lead"
            }
        }
        context = {}
        
        # Мокаем метод создания
        mock_result = {"success": True, "lead": {"id": 67890}, "lead_id": 67890}
        amocrm_plugin._create_lead = AsyncMock(return_value=mock_result)
        
        await amocrm_plugin._handle_create_lead(step_data, context)
        
        assert "new_lead" in context
        assert context["new_lead"]["success"] is True
        assert context["new_lead"]["lead_id"] == 67890
    
    @pytest.mark.asyncio
    async def test_handle_add_note(self, amocrm_plugin):
        """Тест добавления заметки"""
        step_data = {
            "params": {
                "entity_type": "leads",
                "entity_id": 67890,
                "note_text": "Тестовая заметка",
                "output_var": "note_result"
            }
        }
        context = {}
        
        # Мокаем метод добавления заметки
        mock_result = {"success": True, "note_added": True, "entity_id": 67890}
        amocrm_plugin._add_note_to_entity = AsyncMock(return_value=mock_result)
        
        await amocrm_plugin._handle_add_note(step_data, context)
        
        assert "note_result" in context
        assert context["note_result"]["success"] is True
        assert context["note_result"]["note_added"] is True
    
    @pytest.mark.asyncio
    async def test_healthcheck_success(self, amocrm_plugin):
        """Тест успешного healthcheck"""
        mock_result = {
            "success": True,
            "data": {"name": "Test Account"}
        }
        amocrm_plugin._make_request = AsyncMock(return_value=mock_result)
        
        result = await amocrm_plugin.healthcheck()
        
        assert result is True
        amocrm_plugin._make_request.assert_called_once_with("GET", "/api/v4/account")
    
    @pytest.mark.asyncio
    async def test_healthcheck_failure(self, amocrm_plugin):
        """Тест неуспешного healthcheck"""
        mock_result = {
            "success": False,
            "error": "API недоступен"
        }
        amocrm_plugin._make_request = AsyncMock(return_value=mock_result)
        
        result = await amocrm_plugin.healthcheck()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_healthcheck_no_config(self):
        """Тест healthcheck без настроек"""
        with patch.dict(os.environ, {}, clear=True):
            plugin = SimpleAmoCRMPlugin()
            
            result = await plugin.healthcheck()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_error_handling(self, amocrm_plugin):
        """Тест обработки ошибок в шагах"""
        step_data = {
            "params": {
                "telegram_id": "123456789"
            }
        }
        context = {}
        
        # Мокаем исключение
        amocrm_plugin._find_contact_by_telegram_id = AsyncMock(side_effect=Exception("Тестовая ошибка"))
        
        await amocrm_plugin._handle_find_contact(step_data, context)
        
        assert "__step_error__" in context
        assert "Тестовая ошибка" in context["__step_error__"] 