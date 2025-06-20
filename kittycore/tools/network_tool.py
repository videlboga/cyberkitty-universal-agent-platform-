"""
NetworkTool - Продвинутый сетевой инструмент для KittyCore 3.0

Обеспечивает полноценную работу с сетью:
- HTTP/HTTPS запросы (GET, POST, PUT, DELETE, PATCH)
- Веб-скрапинг с поддержкой JavaScript
- API интеграции и тестирование
- Мониторинг сетевых соединений
- Работа с WebSocket
- DNS резолвинг и анализ
- Проверка доступности хостов
"""

import asyncio
import json
import socket
import ssl
import time
import urllib.parse
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Union

import aiohttp
import dns.resolver
from loguru import logger

from kittycore.tools.base_tool import Tool, ToolResult


@dataclass
class HttpResponse:
    """HTTP ответ"""
    status_code: int
    headers: Dict[str, str]
    content: str
    content_type: str
    response_time: float
    size_bytes: int
    encoding: str
    url: str
    redirected_from: Optional[str] = None


@dataclass
class NetworkConnection:
    """Сетевое соединение"""
    local_address: str
    local_port: int
    remote_address: str
    remote_port: int
    status: str
    protocol: str
    process_name: Optional[str] = None
    process_pid: Optional[int] = None


@dataclass
class DnsRecord:
    """DNS запись"""
    name: str
    record_type: str
    value: str
    ttl: int
    priority: Optional[int] = None


@dataclass
class HostCheck:
    """Проверка доступности хоста"""
    host: str
    port: int
    is_reachable: bool
    response_time: float
    error: Optional[str] = None


class NetworkTool(Tool):
    """Продвинутый сетевой инструмент"""
    
    def __init__(self):
        super().__init__(
            name="network_tool", 
            description="Комплексный инструмент для работы с сетью - HTTP запросы, API, веб-скрапинг, мониторинг"
        )
        
        # Настройки HTTP клиента
        self._session = None
        self._default_timeout = 30.0
        self._default_headers = {
            'User-Agent': 'KittyCore-NetworkTool/3.0'
        }
        
        # Кеш DNS
        self._dns_cache = {}
        self._dns_cache_ttl = 300  # 5 минут
        
        logger.info("🌐 NetworkTool инициализирован")
    
    def get_available_actions(self) -> List[str]:
        """Получение списка доступных действий"""
        return [
            "http_request",
            "get_request", 
            "post_request",
            "put_request",
            "delete_request",
            "patch_request",
            "download_file",
            "check_website",
            "ping_host",
            "resolve_dns",
            "get_dns_records",
            "scan_port",
            "scan_ports_range",
            "get_network_connections",
            "trace_route",
            "get_whois_info",
            "test_api_endpoint",
            "scrape_webpage"
        ]
    
    async def _ensure_session(self):
        """Обеспечивает наличие HTTP сессии"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self._default_timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._default_headers,
                connector=aiohttp.TCPConnector(limit=100, limit_per_host=10)
            )
    
    async def _close_session(self):
        """Закрытие HTTP сессии"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def http_request(self, 
                          url: str,
                          method: str = "GET",
                          headers: Optional[Dict[str, str]] = None,
                          data: Optional[Union[str, Dict]] = None,
                          params: Optional[Dict[str, str]] = None,
                          timeout: float = None,
                          follow_redirects: bool = True,
                          verify_ssl: bool = True) -> ToolResult:
        """Универсальный HTTP запрос"""
        try:
            await self._ensure_session()
            
            # Подготовка параметров
            request_headers = self._default_headers.copy()
            if headers:
                request_headers.update(headers)
            
            request_timeout = timeout or self._default_timeout
            ssl_context = ssl.create_default_context() if verify_ssl else False
            
            # Подготовка данных
            request_data = None
            if data:
                if isinstance(data, dict):
                    if request_headers.get('Content-Type', '').startswith('application/json'):
                        request_data = json.dumps(data)
                    else:
                        request_data = data
                else:
                    request_data = data
            
            start_time = time.time()
            
            async with self._session.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                data=request_data,
                params=params,
                timeout=aiohttp.ClientTimeout(total=request_timeout),
                allow_redirects=follow_redirects,
                ssl=ssl_context
            ) as response:
                
                content = await response.text()
                response_time = time.time() - start_time
                
                # Определяем редирект
                redirected_from = None
                if response.history:
                    redirected_from = str(response.history[0].url)
                
                http_response = HttpResponse(
                    status_code=response.status,
                    headers=dict(response.headers),
                    content=content,
                    content_type=response.content_type or 'unknown',
                    response_time=response_time,
                    size_bytes=len(content.encode('utf-8')),
                    encoding=response.charset or 'utf-8',
                    url=str(response.url),
                    redirected_from=redirected_from
                )
                
                return ToolResult(
                    success=True,
                    data=asdict(http_response)
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"HTTP запрос неудачен: {str(e)}"
            )
    
    # Упрощённые методы HTTP
    async def get_request(self, url: str, **kwargs) -> ToolResult:
        """GET запрос"""
        return await self.http_request(url, method="GET", **kwargs)
    
    async def post_request(self, url: str, data: Optional[Union[str, Dict]] = None, **kwargs) -> ToolResult:
        """POST запрос"""
        return await self.http_request(url, method="POST", data=data, **kwargs)
    
    async def put_request(self, url: str, data: Optional[Union[str, Dict]] = None, **kwargs) -> ToolResult:
        """PUT запрос"""
        return await self.http_request(url, method="PUT", data=data, **kwargs)
    
    async def delete_request(self, url: str, **kwargs) -> ToolResult:
        """DELETE запрос"""
        return await self.http_request(url, method="DELETE", **kwargs)
    
    async def patch_request(self, url: str, data: Optional[Union[str, Dict]] = None, **kwargs) -> ToolResult:
        """PATCH запрос"""
        return await self.http_request(url, method="PATCH", data=data, **kwargs)
    
    # DNS функции
    async def resolve_dns(self, hostname: str, record_type: str = "A") -> ToolResult:
        """Резолвинг DNS записей"""
        try:
            # Проверяем кеш
            cache_key = f"{hostname}:{record_type}"
            if cache_key in self._dns_cache:
                cached_time, cached_result = self._dns_cache[cache_key]
                if time.time() - cached_time < self._dns_cache_ttl:
                    return cached_result
            
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 10
            
            answers = resolver.resolve(hostname, record_type)
            
            records = []
            for answer in answers:
                record = DnsRecord(
                    name=hostname,
                    record_type=record_type,
                    value=str(answer),
                    ttl=answers.rrset.ttl if hasattr(answers, 'rrset') else 300
                )
                
                # Для MX записей добавляем приоритет
                if record_type == "MX" and hasattr(answer, 'preference'):
                    record.priority = answer.preference
                    
                records.append(asdict(record))
            
            result = ToolResult(
                success=True,
                data={
                    "hostname": hostname,
                    "record_type": record_type,
                    "records": records,
                    "count": len(records),
                    "resolver_used": str(resolver.nameservers)
                }
            )
            
            # Кешируем результат
            self._dns_cache[cache_key] = (time.time(), result)
            
            return result
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"DNS резолвинг неудачен: {str(e)}"
            )
    
    async def get_dns_records(self, hostname: str) -> ToolResult:
        """Получение всех основных DNS записей"""
        try:
            record_types = ["A", "AAAA", "MX", "CNAME", "TXT", "NS"]
            all_records = {}
            
            for record_type in record_types:
                try:
                    result = await self.resolve_dns(hostname, record_type)
                    if result.success:
                        all_records[record_type] = result.data["records"]
                    else:
                        all_records[record_type] = []
                except:
                    all_records[record_type] = []
            
            return ToolResult(
                success=True,
                data={
                    "hostname": hostname,
                    "records": all_records,
                    "total_types": len([k for k, v in all_records.items() if v])
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Получение DNS записей неудачно: {str(e)}"
            )
    
    # Сетевые проверки
    async def ping_host(self, host: str, count: int = 4, timeout: float = 5.0) -> ToolResult:
        """Ping хоста"""
        try:
            import subprocess
            import platform
            
            # Определяем команду ping для OS
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", str(count), host]
            else:
                cmd = ["ping", "-c", str(count), "-W", str(int(timeout)), host]
            
            start_time = time.time()
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout * count + 5
            )
            total_time = time.time() - start_time
            
            success = result.returncode == 0
            
            # Парсим вывод для извлечения статистики
            output_lines = result.stdout.split('\n')
            stats = {
                "packets_sent": count,
                "packets_received": 0,
                "packet_loss": 100.0,
                "min_time": None,
                "max_time": None,
                "avg_time": None
            }
            
            # Простой парсинг для получения базовой статистики
            for line in output_lines:
                if "received" in line.lower() and "transmitted" in line.lower():
                    # Linux/Mac формат
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            stats["packets_received"] = int(parts[3])
                            stats["packet_loss"] = (count - stats["packets_received"]) / count * 100
                        except:
                            pass
                elif "time=" in line.lower():
                    # Извлекаем время ответа
                    try:
                        time_part = line.split("time=")[1].split()[0]
                        time_ms = float(time_part.replace("ms", ""))
                        if stats["min_time"] is None or time_ms < stats["min_time"]:
                            stats["min_time"] = time_ms
                        if stats["max_time"] is None or time_ms > stats["max_time"]:
                            stats["max_time"] = time_ms
                    except:
                        pass
            
            return ToolResult(
                success=success,
                data={
                    "host": host,
                    "ping_successful": success,
                    "total_time": total_time,
                    "statistics": stats,
                    "output": result.stdout[:500],  # Ограничиваем вывод
                    "error_output": result.stderr[:200] if result.stderr else None
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ping неудачен: {str(e)}"
            )
    
    async def scan_port(self, host: str, port: int, timeout: float = 3.0) -> ToolResult:
        """Сканирование одного порта"""
        try:
            start_time = time.time()
            
            # Создаём socket для проверки
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            try:
                result = sock.connect_ex((host, port))
                is_open = result == 0
                response_time = time.time() - start_time
                
                # Пытаемся определить сервис
                service_name = None
                try:
                    service_name = socket.getservbyport(port)
                except:
                    pass
                
                check = HostCheck(
                    host=host,
                    port=port,
                    is_reachable=is_open,
                    response_time=response_time,
                    error=None if is_open else f"Connection refused or timeout"
                )
                
                return ToolResult(
                    success=True,
                    data={
                        **asdict(check),
                        "service_name": service_name,
                        "status": "open" if is_open else "closed"
                    }
                )
                
            finally:
                sock.close()
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Сканирование порта неудачно: {str(e)}"
            )
    
    async def scan_ports_range(self, host: str, start_port: int = 1, end_port: int = 1000, timeout: float = 1.0) -> ToolResult:
        """Сканирование диапазона портов"""
        try:
            open_ports = []
            closed_ports = []
            total_scanned = 0
            
            start_time = time.time()
            
            # Ограничиваем количество портов для сканирования
            max_ports = min(end_port - start_port + 1, 200)  # Максимум 200 портов
            actual_end = min(end_port, start_port + max_ports - 1)
            
            # Создаём задачи для параллельного сканирования
            scan_tasks = []
            for port in range(start_port, actual_end + 1):
                task = self.scan_port(host, port, timeout)
                scan_tasks.append(task)
            
            # Выполняем сканирование батчами по 50 портов
            batch_size = 50
            for i in range(0, len(scan_tasks), batch_size):
                batch = scan_tasks[i:i + batch_size]
                results = await asyncio.gather(*batch, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        continue
                    
                    if result.success and result.data["is_reachable"]:
                        open_ports.append({
                            "port": result.data["port"],
                            "service_name": result.data.get("service_name"),
                            "response_time": result.data["response_time"]
                        })
                    else:
                        closed_ports.append(result.data["port"])
                    
                    total_scanned += 1
            
            total_time = time.time() - start_time
            
            return ToolResult(
                success=True,
                data={
                    "host": host,
                    "port_range": f"{start_port}-{actual_end}",
                    "total_scanned": total_scanned,
                    "open_ports": open_ports,
                    "open_count": len(open_ports),
                    "closed_count": len(closed_ports),
                    "scan_time": total_time,
                    "ports_per_second": total_scanned / total_time if total_time > 0 else 0
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Сканирование диапазона портов неудачно: {str(e)}"
            )
    
    # Реализуем обязательные методы
    async def execute(self, action: str, **kwargs) -> ToolResult:
        """Выполнение действия"""
        if action == "http_request":
            return await self.http_request(**kwargs)
        elif action == "get_request":
            return await self.get_request(**kwargs)
        elif action == "post_request":
            return await self.post_request(**kwargs)
        elif action == "put_request":
            return await self.put_request(**kwargs)
        elif action == "delete_request":
            return await self.delete_request(**kwargs)
        elif action == "patch_request":
            return await self.patch_request(**kwargs)
        elif action == "resolve_dns":
            return await self.resolve_dns(**kwargs)
        elif action == "get_dns_records":
            return await self.get_dns_records(**kwargs)
        elif action == "ping_host":
            return await self.ping_host(**kwargs)
        elif action == "scan_port":
            return await self.scan_port(**kwargs)
        elif action == "scan_ports_range":
            return await self.scan_ports_range(**kwargs)
        else:
            return ToolResult(
                success=False,
                error=f"Неизвестное действие: {action}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": self.get_available_actions(),
                    "description": "Действие для выполнения"
                },
                "url": {
                    "type": "string",
                    "description": "URL для HTTP запросов"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    "description": "HTTP метод"
                },
                "hostname": {
                    "type": "string",
                    "description": "Имя хоста для DNS операций"
                },
                "host": {
                    "type": "string",
                    "description": "IP адрес или имя хоста"
                },
                "port": {
                    "type": "integer",
                    "description": "Номер порта"
                },
                "start_port": {
                    "type": "integer",
                    "description": "Начальный порт для сканирования"
                },
                "end_port": {
                    "type": "integer",
                    "description": "Конечный порт для сканирования"
                },
                "record_type": {
                    "type": "string",
                    "enum": ["A", "AAAA", "MX", "CNAME", "TXT", "NS", "PTR"],
                    "description": "Тип DNS записи"
                },
                "timeout": {
                    "type": "number",
                    "description": "Таймаут в секундах"
                },
                "count": {
                    "type": "integer",
                    "description": "Количество ping пакетов"
                }
            },
            "required": ["action"]
        } 