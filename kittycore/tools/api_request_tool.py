"""
🌐 API Request Tool - Универсальный HTTP API клиент

Инструмент для выполнения HTTP запросов к API с поддержкой:
- Все HTTP методы (GET, POST, PUT, DELETE, PATCH)
- Кастомные заголовки
- JSON данные
- URL параметры
- Таймауты
"""

import time
from typing import Dict, Any, List

from .web_common import (
    Tool, ToolResult, requests,
    create_headers, ApiResponse
)


class ApiRequestTool(Tool):
    """Универсальный инструмент для HTTP API запросов"""
    
    def __init__(self):
        super().__init__(
            name="api_request",
            description="Выполнение HTTP запросов к API"
        )
    
    def execute(self, url: str, method: str = "GET", headers: Dict = None, 
               data: Dict = None, params: Dict = None, timeout: int = 30) -> ToolResult:
        """Выполнить API запрос"""
        start_time = time.time()
        
        try:
            # Подготавливаем заголовки
            request_headers = create_headers()
            request_headers.update({
                'Accept': 'application/json'
            })
            
            if headers:
                request_headers.update(headers)
            
            # Выполняем запрос
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                json=data if data else None,
                params=params,
                timeout=timeout
            )
            
            response_time = time.time() - start_time
            
            # Пытаемся распарсить JSON
            try:
                response_data = response.json()
            except:
                response_data = {
                    "content": response.text[:1000],  # Ограничиваем размер
                    "content_type": response.headers.get('content-type', 'unknown'),
                    "is_text": True
                }
            
            # Создаем структурированный ответ
            api_response = ApiResponse(
                url=url,
                status_code=response.status_code,
                success=200 <= response.status_code < 300,
                data=response_data,
                headers=dict(response.headers),
                response_time=response_time
            )
            
            return ToolResult(
                success=True,
                data={
                    "request": {
                        "url": url,
                        "method": method.upper(),
                        "headers": request_headers,
                        "data": data,
                        "params": params,
                        "timeout": timeout
                    },
                    "response": {
                        "status_code": api_response.status_code,
                        "success": api_response.success,
                        "data": api_response.data,
                        "headers": api_response.headers,
                        "response_time": api_response.response_time,
                        "content_length": len(response.content),
                        "encoding": response.encoding
                    },
                    "metadata": {
                        "url_final": response.url,
                        "redirected": str(response.url) != url,
                        "cookies": dict(response.cookies),
                        "reason": response.reason,
                        "elapsed_seconds": response.elapsed.total_seconds()
                    }
                }
            )
            
        except requests.exceptions.Timeout:
            return ToolResult(
                success=False,
                error=f"Таймаут запроса к {url} (лимит: {timeout}с)"
            )
        except requests.exceptions.ConnectionError:
            return ToolResult(
                success=False,
                error=f"Ошибка подключения к {url}"
            )
        except requests.exceptions.RequestException as e:
            return ToolResult(
                success=False,
                error=f"Ошибка HTTP запроса: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка API запроса: {str(e)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL для API запроса",
                    "format": "uri"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                    "description": "HTTP метод",
                    "default": "GET"
                },
                "headers": {
                    "type": "object",
                    "description": "HTTP заголовки (ключ-значение)",
                    "additionalProperties": {"type": "string"}
                },
                "data": {
                    "type": "object",
                    "description": "Данные для отправки в теле запроса (JSON)"
                },
                "params": {
                    "type": "object", 
                    "description": "URL параметры запроса",
                    "additionalProperties": {"type": "string"}
                },
                "timeout": {
                    "type": "integer",
                    "description": "Таймаут запроса в секундах",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 300
                }
            },
            "required": ["url"]
        }

    def get_available_actions(self) -> List[str]:
        """Доступные действия инструмента"""
        return [
            "get",      # GET запрос
            "post",     # POST запрос  
            "put",      # PUT запрос
            "delete",   # DELETE запрос
            "patch",    # PATCH запрос
            "head",     # HEAD запрос
            "options"   # OPTIONS запрос
        ]

    def execute_action(self, action: str, **kwargs) -> ToolResult:
        """Выполнение действия по имени"""
        action = action.lower()
        
        if action in self.get_available_actions():
            kwargs['method'] = action.upper()
            return self.execute(**kwargs)
        else:
            return ToolResult(
                success=False,
                error=f"Неизвестное действие: {action}. Доступные: {', '.join(self.get_available_actions())}"
            )


# Фабричная функция
def create_api_request_tool() -> ApiRequestTool:
    """Создание инструмента API Request"""
    return ApiRequestTool() 