"""
Тесты для NetworkTool KittyCore 3.0
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from kittycore.tools.network_tool import (
    NetworkTool,
    HttpResponse,
    DnsRecord,
    HostCheck,
    NetworkConnection
)


class TestNetworkTool:
    """Тесты для NetworkTool"""
    
    @pytest.fixture
    def network_tool(self):
        """Фикстура для сетевого инструмента"""
        return NetworkTool()
    
    @pytest.mark.asyncio
    async def test_tool_initialization(self, network_tool):
        """Тест инициализации инструмента"""
        assert network_tool.name == "network_tool"
        assert "комплексный инструмент" in network_tool.description.lower()
        assert network_tool._session is None
        assert network_tool._dns_cache == {}
    
    def test_available_actions(self, network_tool):
        """Тест списка доступных действий"""
        actions = network_tool.get_available_actions()
        
        expected_actions = [
            "http_request", "get_request", "post_request",
            "resolve_dns", "ping_host", "scan_port", "scan_ports_range"
        ]
        
        for action in expected_actions:
            assert action in actions
    
    @pytest.mark.asyncio
    async def test_ensure_session(self, network_tool):
        """Тест создания HTTP сессии"""
        await network_tool._ensure_session()
        assert network_tool._session is not None
        assert not network_tool._session.closed
        
        # Закрываем для очистки
        await network_tool._close_session()
    
    @pytest.mark.asyncio
    async def test_http_request_simple(self, network_tool):
        """Тест HTTP запроса (проверка доступности действия)"""
        # Проверяем что http_request доступен
        actions = network_tool.get_available_actions()
        assert "http_request" in actions
        
        # Проверяем схему
        schema = network_tool.get_schema()
        assert "url" in schema["properties"]
        assert "method" in schema["properties"]
    
    @pytest.mark.asyncio 
    async def test_get_request(self, network_tool):
        """Тест GET запроса через алиас"""
        with patch.object(network_tool, 'http_request') as mock_http:
            from kittycore.tools.base_tool import ToolResult
            mock_http.return_value = ToolResult(success=True, data={"method": "GET"})
            
            result = await network_tool.get_request("https://example.com")
            
            assert result.success is True
            mock_http.assert_called_once_with("https://example.com", method="GET")
    
    @pytest.mark.asyncio
    async def test_post_request(self, network_tool):
        """Тест POST запроса с данными"""
        with patch.object(network_tool, 'http_request') as mock_http:
            from kittycore.tools.base_tool import ToolResult
            mock_http.return_value = ToolResult(success=True, data={"method": "POST"})
            
            test_data = {"key": "value"}
            result = await network_tool.post_request("https://example.com", data=test_data)
            
            assert result.success is True
            mock_http.assert_called_once_with("https://example.com", method="POST", data=test_data)
    
    @pytest.mark.asyncio
    async def test_resolve_dns_mock(self, network_tool):
        """Тест DNS резолвинга с мокированным ответом"""
        with patch('dns.resolver.Resolver') as mock_resolver_class:
            mock_resolver = mock_resolver_class.return_value
            mock_resolver.nameservers = ["8.8.8.8"]
            
            # Создаём мок ответа DNS
            mock_answer = MagicMock()
            mock_answer.__str__ = lambda x: "93.184.216.34"
            
            mock_answers = MagicMock()
            mock_answers.__iter__ = lambda x: iter([mock_answer])
            mock_answers.rrset.ttl = 300
            
            mock_resolver.resolve.return_value = mock_answers
            
            result = await network_tool.resolve_dns("example.com", "A")
            
            assert result.success is True
            assert result.data["hostname"] == "example.com"
            assert result.data["record_type"] == "A"
            assert len(result.data["records"]) == 1
            assert result.data["records"][0]["value"] == "93.184.216.34"
    
    @pytest.mark.asyncio
    async def test_dns_caching(self, network_tool):
        """Тест кеширования DNS запросов"""
        with patch('dns.resolver.Resolver') as mock_resolver_class:
            mock_resolver = mock_resolver_class.return_value
            mock_resolver.nameservers = ["8.8.8.8"]
            
            mock_answer = MagicMock()
            mock_answer.__str__ = lambda x: "1.2.3.4"
            
            mock_answers = MagicMock()
            mock_answers.__iter__ = lambda x: iter([mock_answer])
            mock_answers.rrset.ttl = 300
            
            mock_resolver.resolve.return_value = mock_answers
            
            # Первый запрос
            result1 = await network_tool.resolve_dns("test.com", "A")
            assert result1.success is True
            
            # Второй запрос должен использовать кеш
            result2 = await network_tool.resolve_dns("test.com", "A")
            assert result2.success is True
            
            # Проверяем что DNS resolver вызывался только один раз
            assert mock_resolver.resolve.call_count == 1
    
    @pytest.mark.asyncio
    async def test_get_dns_records(self, network_tool):
        """Тест получения всех DNS записей"""
        with patch.object(network_tool, 'resolve_dns') as mock_resolve:
            from kittycore.tools.base_tool import ToolResult
            
            # Настраиваем успешные ответы для разных типов записей
            def resolve_side_effect(hostname, record_type):
                if record_type == "A":
                    return ToolResult(success=True, data={"records": [{"value": "1.2.3.4"}]})
                elif record_type == "MX":
                    return ToolResult(success=True, data={"records": [{"value": "mail.example.com", "priority": 10}]})
                else:
                    return ToolResult(success=False, data={})
            
            mock_resolve.side_effect = resolve_side_effect
            
            result = await network_tool.get_dns_records("example.com")
            
            assert result.success is True
            assert "A" in result.data["records"]
            assert "MX" in result.data["records"]
            assert result.data["total_types"] == 2
    
    @pytest.mark.asyncio
    async def test_ping_host_mock(self, network_tool):
        """Тест ping хоста с мокированным subprocess"""
        mock_ping_output = """
PING example.com (93.184.216.34): 56 data bytes
64 bytes from 93.184.216.34: icmp_seq=0 time=20.1 ms
64 bytes from 93.184.216.34: icmp_seq=1 time=18.5 ms
--- example.com ping statistics ---
4 packets transmitted, 4 received, 0% packet loss
"""
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = mock_ping_output
            mock_result.stderr = ""
            
            mock_run.return_value = mock_result
            
            result = await network_tool.ping_host("example.com", count=4)
            
            assert result.success is True
            assert result.data["host"] == "example.com"
            assert result.data["ping_successful"] is True
            assert "statistics" in result.data
    
    @pytest.mark.asyncio
    async def test_scan_port_open(self, network_tool):
        """Тест сканирования открытого порта"""
        with patch('socket.socket') as mock_socket_class:
            mock_socket = mock_socket_class.return_value
            mock_socket.connect_ex.return_value = 0  # Порт открыт
            
            with patch('socket.getservbyport', return_value="http"):
                result = await network_tool.scan_port("example.com", 80)
                
                assert result.success is True
                assert result.data["port"] == 80
                assert result.data["is_reachable"] is True
                assert result.data["status"] == "open"
                assert result.data["service_name"] == "http"
    
    @pytest.mark.asyncio
    async def test_scan_port_closed(self, network_tool):
        """Тест сканирования закрытого порта"""
        with patch('socket.socket') as mock_socket_class:
            mock_socket = mock_socket_class.return_value
            mock_socket.connect_ex.return_value = 1  # Порт закрыт
            
            result = await network_tool.scan_port("example.com", 12345)
            
            assert result.success is True
            assert result.data["port"] == 12345
            assert result.data["is_reachable"] is False
            assert result.data["status"] == "closed"
    
    @pytest.mark.asyncio
    async def test_scan_ports_range(self, network_tool):
        """Тест сканирования диапазона портов"""
        with patch.object(network_tool, 'scan_port') as mock_scan:
            from kittycore.tools.base_tool import ToolResult
            
            # Настраиваем мок: порт 80 открыт, остальные закрыты
            def scan_side_effect(host, port, timeout):
                if port == 80:
                    return ToolResult(success=True, data={
                        "port": port,
                        "is_reachable": True,
                        "response_time": 0.1,
                        "service_name": "http"
                    })
                else:
                    return ToolResult(success=True, data={
                        "port": port,
                        "is_reachable": False,
                        "response_time": 1.0
                    })
            
            mock_scan.side_effect = scan_side_effect
            
            result = await network_tool.scan_ports_range("example.com", 79, 81)
            
            assert result.success is True
            assert result.data["host"] == "example.com"
            assert result.data["open_count"] == 1
            assert result.data["total_scanned"] == 3
            assert len(result.data["open_ports"]) == 1
            assert result.data["open_ports"][0]["port"] == 80
    
    @pytest.mark.asyncio
    async def test_execute_method(self, network_tool):
        """Тест метода execute с различными действиями"""
        # Тест http_request
        with patch.object(network_tool, 'http_request') as mock_http:
            from kittycore.tools.base_tool import ToolResult
            mock_http.return_value = ToolResult(success=True, data={})
            
            result = await network_tool.execute("http_request", url="https://example.com")
            assert result.success is True
            mock_http.assert_called_once()
        
        # Тест неизвестного действия
        result = await network_tool.execute("unknown_action")
        assert result.success is False
        assert "неизвестное действие" in result.error.lower()
    
    def test_get_schema(self, network_tool):
        """Тест схемы инструмента"""
        schema = network_tool.get_schema()
        
        assert schema["type"] == "object"
        assert "action" in schema["properties"]
        assert "action" in schema["required"]
        
        # Проверяем основные свойства
        properties = schema["properties"]
        assert "url" in properties
        assert "hostname" in properties
        assert "host" in properties
        assert "port" in properties
        assert "timeout" in properties
        
        # Проверяем enum для действий
        actions_enum = properties["action"]["enum"]
        assert "http_request" in actions_enum
        assert "resolve_dns" in actions_enum
        assert "ping_host" in actions_enum
        assert "scan_port" in actions_enum


class TestDataClasses:
    """Тесты для dataclass структур"""
    
    def test_http_response_creation(self):
        """Тест создания HttpResponse"""
        response = HttpResponse(
            status_code=200,
            headers={"content-type": "text/html"},
            content="<html>test</html>",
            content_type="text/html",
            response_time=0.5,
            size_bytes=18,
            encoding="utf-8",
            url="https://example.com"
        )
        
        assert response.status_code == 200
        assert response.content_type == "text/html"
        assert response.response_time == 0.5
        assert response.redirected_from is None
    
    def test_dns_record_creation(self):
        """Тест создания DnsRecord"""
        record = DnsRecord(
            name="example.com",
            record_type="A",
            value="93.184.216.34",
            ttl=300,
            priority=10
        )
        
        assert record.name == "example.com"
        assert record.record_type == "A"
        assert record.value == "93.184.216.34"
        assert record.ttl == 300
        assert record.priority == 10
    
    def test_host_check_creation(self):
        """Тест создания HostCheck"""
        check = HostCheck(
            host="example.com",
            port=80,
            is_reachable=True,
            response_time=0.1,
            error=None
        )
        
        assert check.host == "example.com"
        assert check.port == 80
        assert check.is_reachable is True
        assert check.response_time == 0.1
        assert check.error is None
    
    def test_network_connection_creation(self):
        """Тест создания NetworkConnection"""
        connection = NetworkConnection(
            local_address="127.0.0.1",
            local_port=12345,
            remote_address="93.184.216.34",
            remote_port=80,
            status="ESTABLISHED",
            protocol="TCP",
            process_name="chrome",
            process_pid=1234
        )
        
        assert connection.local_address == "127.0.0.1"
        assert connection.remote_port == 80
        assert connection.status == "ESTABLISHED"
        assert connection.protocol == "TCP"
        assert connection.process_name == "chrome"


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"]) 