"""
🌐 Web Client Tool - Простой веб-клиент для проверок

Инструмент для быстрых проверок веб-ресурсов:
- Проверка статуса сайтов
- Ping проверки
- Время отклика
- Базовая диагностика
"""

import time
import subprocess
import platform
from typing import Dict, Any, List

from .web_common import (
    Tool, ToolResult, requests, urlparse,
    is_valid_url, extract_domain, format_file_size
)


class WebClientTool(Tool):
    """Простой веб-клиент для быстрых проверок"""
    
    def __init__(self):
        super().__init__(
            name="web_client",
            description="Простая проверка доступности веб-ресурсов"
        )
    
    def execute(self, url: str, check_type: str = "status", timeout: int = 10) -> ToolResult:
        """Проверить веб-ресурс"""
        try:
            # Валидация URL
            if not is_valid_url(url):
                return ToolResult(
                    success=False,
                    error=f"Некорректный URL: {url}"
                )
            
            if check_type == "status":
                return self._check_status(url, timeout)
            elif check_type == "ping":
                return self._ping_url(url)
            elif check_type == "full":
                return self._full_check(url, timeout)
            else:
                return ToolResult(
                    success=False,
                    error=f"Неизвестный тип проверки: {check_type}. Доступные: status, ping, full"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка проверки: {str(e)}"
            )
    
    def _check_status(self, url: str, timeout: int = 10) -> ToolResult:
        """Проверить статус сайта"""
        start_time = time.time()
        
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            response_time = time.time() - start_time
            
            # Дополнительная информация
            content_length = response.headers.get('content-length', 0)
            if content_length:
                try:
                    content_length = int(content_length)
                except:
                    content_length = 0
            
            return ToolResult(
                success=True,
                data={
                    "check_type": "status",
                    "url": url,
                    "domain": extract_domain(url),
                    "status_code": response.status_code,
                    "status_text": response.reason,
                    "available": 200 <= response.status_code < 400,
                    "response_time_seconds": round(response_time, 3),
                    "response_time_ms": round(response_time * 1000, 1),
                    "headers": dict(response.headers),
                    "final_url": response.url,
                    "redirected": str(response.url) != url,
                    "content_length": content_length,
                    "content_length_formatted": format_file_size(content_length) if content_length else "Unknown",
                    "server": response.headers.get('server', 'Unknown'),
                    "content_type": response.headers.get('content-type', 'Unknown'),
                    "encoding": response.headers.get('content-encoding', None),
                    "cache_control": response.headers.get('cache-control', None),
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            return ToolResult(
                success=True,  # Успех в плане выполнения проверки
                data={
                    "check_type": "status", 
                    "url": url,
                    "domain": extract_domain(url),
                    "available": False,
                    "error": f"Таймаут ({timeout}с)",
                    "response_time_seconds": round(response_time, 3),
                    "timeout_limit": timeout,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
        except requests.exceptions.ConnectionError as e:
            response_time = time.time() - start_time
            return ToolResult(
                success=True,
                data={
                    "check_type": "status",
                    "url": url,
                    "domain": extract_domain(url),
                    "available": False,
                    "error": f"Ошибка подключения: {str(e)[:100]}",
                    "response_time_seconds": round(response_time, 3),
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
        except Exception as e:
            response_time = time.time() - start_time
            return ToolResult(
                success=True,
                data={
                    "check_type": "status",
                    "url": url,
                    "domain": extract_domain(url),
                    "available": False,
                    "error": str(e)[:100],
                    "response_time_seconds": round(response_time, 3),
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
    
    def _ping_url(self, url: str) -> ToolResult:
        """Быстрая проверка доступности через ping"""
        try:
            domain = extract_domain(url) or url
            
            # Убираем протокол и порт если есть
            if '://' in domain:
                domain = domain.split('://')[1]
            if ':' in domain:
                domain = domain.split(':')[0]
            
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', domain]
            
            start_time = time.time()
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            ping_time = time.time() - start_time
            
            return ToolResult(
                success=True,
                data={
                    "check_type": "ping",
                    "url": url,
                    "domain": domain,
                    "ping_success": result.returncode == 0,
                    "ping_time_seconds": round(ping_time, 3),
                    "return_code": result.returncode,
                    "output": result.stdout[:300] if result.stdout else "",
                    "error": result.stderr[:300] if result.stderr else "",
                    "command": ' '.join(command),
                    "platform": platform.system(),
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=True,
                data={
                    "check_type": "ping",
                    "url": url,
                    "domain": domain,
                    "ping_success": False,
                    "error": "Ping timeout (10s)",
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка ping: {str(e)}"
            )
    
    def _full_check(self, url: str, timeout: int = 10) -> ToolResult:
        """Полная проверка: статус + ping"""
        try:
            # Проверка статуса
            status_result = self._check_status(url, timeout)
            
            # Проверка ping
            ping_result = self._ping_url(url)
            
            # Объединяем результаты
            combined_data = {
                "check_type": "full",
                "url": url,
                "domain": extract_domain(url),
                "status_check": status_result.data if status_result.success else {"error": status_result.error},
                "ping_check": ping_result.data if ping_result.success else {"error": ping_result.error},
                "overall_available": False,
                "summary": [],
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Анализ результатов
            status_ok = (status_result.success and 
                        status_result.data.get('available', False))
            ping_ok = (ping_result.success and 
                      ping_result.data.get('ping_success', False))
            
            combined_data["overall_available"] = status_ok or ping_ok
            
            if status_ok:
                combined_data["summary"].append("✅ HTTP статус: OK")
            else:
                combined_data["summary"].append("❌ HTTP статус: Недоступен")
            
            if ping_ok:
                combined_data["summary"].append("✅ Ping: OK")
            else:
                combined_data["summary"].append("❌ Ping: Неудачен")
            
            return ToolResult(
                success=True,
                data=combined_data
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка полной проверки: {str(e)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL для проверки",
                    "format": "uri"
                },
                "check_type": {
                    "type": "string",
                    "enum": ["status", "ping", "full"],
                    "description": "Тип проверки (status - HTTP статус, ping - проверка доступности, full - обе)",
                    "default": "status"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Таймаут для HTTP запроса в секундах",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 60
                }
            },
            "required": ["url"]
        }

    def get_available_actions(self) -> List[str]:
        """Доступные действия инструмента"""
        return [
            "status",  # Проверка HTTP статуса
            "ping",    # Ping проверка
            "full"     # Полная проверка
        ]

    def execute_action(self, action: str, **kwargs) -> ToolResult:
        """Выполнение действия по имени"""
        kwargs['check_type'] = action
        return self.execute(**kwargs)


# Фабричная функция
def create_web_client_tool() -> WebClientTool:
    """Создание инструмента Web Client"""
    return WebClientTool() 