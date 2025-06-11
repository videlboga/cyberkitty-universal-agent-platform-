"""
🌐 WebTools - Веб-инструменты для KittyCore 3.0

Реальные инструменты для работы с веб:
- Поиск в интернете через DuckDuckGo API
- Web scraping с BeautifulSoup
- HTTP API запросы
- Проверка доступности сайтов
"""

import requests
import json
import time
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
from .base_tool import Tool, ToolResult

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False


class WebSearchTool(Tool):
    """Реальный поиск в интернете через DuckDuckGo Instant Answer API"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Поиск информации в интернете через DuckDuckGo API"
        )
        self.base_url = "https://api.duckduckgo.com/"
    
    def execute(self, query: str, limit: int = 5) -> ToolResult:
        """Выполнить поиск в интернете"""
        try:
            # DuckDuckGo Instant Answer API
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            
            # Instant Answer
            if data.get('Answer'):
                results.append({
                    "title": f"Instant Answer для '{query}'",
                    "url": data.get('AnswerURL', ''),
                    "snippet": data['Answer'],
                    "type": "instant_answer"
                })
            
            # Abstract
            if data.get('Abstract'):
                results.append({
                    "title": data.get('Heading', f"Информация о '{query}'"),
                    "url": data.get('AbstractURL', ''),
                    "snippet": data['Abstract'],
                    "type": "abstract"
                })
            
            # Related Topics
            for topic in data.get('RelatedTopics', [])[:limit-len(results)]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        "title": topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                        "url": topic.get('FirstURL', ''),
                        "snippet": topic['Text'],
                        "type": "related_topic"
                    })
            
            if not results:
                # Fallback результат
                results.append({
                    "title": f"Поиск для '{query}'",
                    "url": f"https://duckduckgo.com/?q={query}",
                    "snippet": f"Выполните поиск '{query}' на DuckDuckGo",
                    "type": "search_link"
                })
            
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "results": results[:limit],
                    "total_found": len(results),
                    "source": "DuckDuckGo API"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False, 
                error=f"Ошибка поиска: {str(e)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Поисковый запрос"
                },
                "limit": {
                    "type": "integer",
                    "description": "Максимальное количество результатов",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        }


class WebScrapingTool(Tool):
    """Извлечение данных с веб-страниц"""
    
    def __init__(self):
        super().__init__(
            name="web_scraping",
            description="Извлечение текста и данных с веб-страниц"
        )
    
    def execute(self, url: str, method: str = "text", selector: str = None) -> ToolResult:
        """Извлечь данные с веб-страницы"""
        try:
            headers = {
                'User-Agent': 'KittyCore 3.0 Web Scraper (https://github.com/cyberkitty/kittycore)'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            if method == "text":
                return self._extract_text(response.text, url)
            elif method == "links":
                return self._extract_links(response.text, url)
            elif method == "selector" and selector:
                return self._extract_by_selector(response.text, selector, url)
            else:
                return ToolResult(
                    success=False,
                    error=f"Неизвестный метод: {method}"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка scraping: {str(e)}"
            )
    
    def _extract_text(self, html: str, url: str) -> ToolResult:
        """Извлечь основной текст"""
        if not BEAUTIFULSOUP_AVAILABLE:
            # Простое извлечение без BeautifulSoup
            text = html[:1000] + "..." if len(html) > 1000 else html
            return ToolResult(
                success=True,
                data={
                    "url": url,
                    "text": text,
                    "method": "raw_html",
                    "warning": "BeautifulSoup недоступен - установите: pip install beautifulsoup4"
                }
            )
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Удаляем скрипты и стили
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return ToolResult(
            success=True,
            data={
                "url": url,
                "text": text[:2000] + "..." if len(text) > 2000 else text,
                "length": len(text),
                "method": "beautifulsoup"
            }
        )
    
    def _extract_links(self, html: str, url: str) -> ToolResult:
        """Извлечь все ссылки"""
        if not BEAUTIFULSOUP_AVAILABLE:
            return ToolResult(
                success=False,
                error="Для извлечения ссылок требуется BeautifulSoup: pip install beautifulsoup4"
            )
        
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            absolute_url = urljoin(url, href)
            links.append({
                "text": a.get_text(strip=True),
                "url": absolute_url,
                "title": a.get('title', '')
            })
        
        return ToolResult(
            success=True,
            data={
                "url": url,
                "links": links[:50],  # Ограничиваем количество
                "total_links": len(links),
                "method": "beautifulsoup_links"
            }
        )
    
    def _extract_by_selector(self, html: str, selector: str, url: str) -> ToolResult:
        """Извлечь по CSS селектору"""
        if not BEAUTIFULSOUP_AVAILABLE:
            return ToolResult(
                success=False,
                error="Для CSS селекторов требуется BeautifulSoup: pip install beautifulsoup4"
            )
        
        soup = BeautifulSoup(html, 'html.parser')
        elements = soup.select(selector)
        
        results = []
        for element in elements[:20]:  # Ограничиваем количество
            results.append({
                "text": element.get_text(strip=True),
                "tag": element.name,
                "attributes": dict(element.attrs)
            })
        
        return ToolResult(
            success=True,
            data={
                "url": url,
                "selector": selector,
                "elements": results,
                "total_found": len(elements),
                "method": "css_selector"
            }
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL страницы для scraping"
                },
                "method": {
                    "type": "string",
                    "enum": ["text", "links", "selector"],
                    "description": "Метод извлечения",
                    "default": "text"
                },
                "selector": {
                    "type": "string",
                    "description": "CSS селектор (только для method=selector)"
                }
            },
            "required": ["url"]
        }


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
        try:
            # Подготавливаем заголовки
            request_headers = {
                'User-Agent': 'KittyCore 3.0 API Client',
                'Accept': 'application/json'
            }
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
            
            # Пытаемся распарсить JSON
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return ToolResult(
                success=True,
                data={
                    "url": url,
                    "method": method.upper(),
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "data": response_data,
                    "success": 200 <= response.status_code < 300,
                    "response_time": response.elapsed.total_seconds()
                }
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
                    "description": "URL для API запроса"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    "description": "HTTP метод",
                    "default": "GET"
                },
                "headers": {
                    "type": "object",
                    "description": "HTTP заголовки"
                },
                "data": {
                    "type": "object",
                    "description": "Данные для отправки (JSON)"
                },
                "params": {
                    "type": "object", 
                    "description": "URL параметры"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Таймаут в секундах",
                    "default": 30
                }
            },
            "required": ["url"]
        }


class WebClient(Tool):
    """Простой веб-клиент для быстрых проверок"""
    
    def __init__(self):
        super().__init__(
            name="web_client",
            description="Простая проверка доступности веб-ресурсов"
        )
    
    def execute(self, url: str, check_type: str = "status") -> ToolResult:
        """Проверить веб-ресурс"""
        try:
            if check_type == "status":
                return self._check_status(url)
            elif check_type == "ping":
                return self._ping_url(url)
            else:
                return ToolResult(
                    success=False,
                    error=f"Неизвестный тип проверки: {check_type}"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка проверки: {str(e)}"
            )
    
    def _check_status(self, url: str) -> ToolResult:
        """Проверить статус сайта"""
        start_time = time.time()
        
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            response_time = time.time() - start_time
            
            return ToolResult(
                success=True,
                data={
                    "url": url,
                    "status_code": response.status_code,
                    "available": 200 <= response.status_code < 400,
                    "response_time": response_time,
                    "headers": dict(response.headers),
                    "final_url": response.url
                }
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return ToolResult(
                success=True,  # Успех в плане выполнения проверки
                data={
                    "url": url,
                    "available": False,
                    "error": str(e),
                    "response_time": response_time
                }
            )
    
    def _ping_url(self, url: str) -> ToolResult:
        """Быстрая проверка доступности"""
        try:
            domain = urlparse(url).netloc or url
            
            import subprocess
            import platform
            
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', domain]
            
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            
            return ToolResult(
                success=True,
                data={
                    "url": url,
                    "domain": domain,
                    "ping_success": result.returncode == 0,
                    "output": result.stdout[:200]
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка ping: {str(e)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL для проверки"
                },
                "check_type": {
                    "type": "string",
                    "enum": ["status", "ping"],
                    "description": "Тип проверки",
                    "default": "status"
                }
            },
            "required": ["url"]
        } 