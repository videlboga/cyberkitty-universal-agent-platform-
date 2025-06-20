"""
🔍 Enhanced Web Search Tool - Продвинутый поиск в интернете

Улучшенный инструмент поиска с поддержкой:
- DuckDuckGo API
- Fallback поисковые системы
- Асинхронные запросы
- Ранжирование результатов
"""

import time
from typing import Dict, Any, List
from urllib.parse import quote

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from .base_tool import Tool, ToolResult
from .web_common import SearchResult, asdict


class EnhancedWebSearchTool(Tool):
    """Улучшенный поиск в интернете с несколькими источниками"""
    
    def __init__(self):
        super().__init__(
            name="enhanced_web_search",
            description="Продвинутый поиск информации в интернете через множественные источники"
        )
        self.duckduckgo_url = "https://api.duckduckgo.com/"
        self.session = None
        
        # Проверка зависимостей
        if not AIOHTTP_AVAILABLE:
            print("⚠️ aiohttp не установлен - асинхронные запросы недоступны")
    
    async def _ensure_session(self):
        """Обеспечивает наличие aiohttp сессии"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=15)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def _close_session(self):
        """Закрытие сессии"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def execute(self, query: str, limit: int = 10, sources: List[str] = None) -> ToolResult:
        """Выполнить улучшенный поиск"""
        try:
            await self._ensure_session()
            
            if sources is None:
                sources = ["duckduckgo", "fallback"]
            
            all_results = []
            
            # Поиск через DuckDuckGo
            if "duckduckgo" in sources:
                ddg_results = await self._search_duckduckgo(query, limit)
                all_results.extend(ddg_results)
            
            # Fallback поиск
            if "fallback" in sources and len(all_results) < limit:
                fallback_results = self._search_fallback(query, limit - len(all_results))
                all_results.extend(fallback_results)
            
            # Сортируем по релевантности
            all_results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "results": [asdict(result) for result in all_results[:limit]],
                    "total_found": len(all_results),
                    "sources_used": sources,
                    "search_time": time.time()
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка поиска: {str(e)}"
            )
        finally:
            # Не закрываем сессию здесь, чтобы переиспользовать
            pass
    
    async def _search_duckduckgo(self, query: str, limit: int) -> List[SearchResult]:
        """Поиск через DuckDuckGo API"""
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            async with self.session.get(self.duckduckgo_url, params=params) as response:
                if response.status != 200:
                    return []
                
                # DuckDuckGo возвращает JSON с неправильным Content-Type
                text = await response.text()
                import json
                data = json.loads(text)
                results = []
                
                # Instant Answer
                if data.get('Answer'):
                    results.append(SearchResult(
                        title=f"Instant Answer: {query}",
                        url=data.get('AnswerURL', ''),
                        snippet=data['Answer'],
                        source="DuckDuckGo Instant",
                        relevance_score=0.9,
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
                    ))
                
                # Abstract
                if data.get('Abstract'):
                    results.append(SearchResult(
                        title=data.get('Heading', query),
                        url=data.get('AbstractURL', ''),
                        snippet=data['Abstract'],
                        source="DuckDuckGo Abstract",
                        relevance_score=0.8,
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
                    ))
                
                # Related Topics
                for i, topic in enumerate(data.get('RelatedTopics', [])[:limit-len(results)]):
                    if isinstance(topic, dict) and topic.get('Text'):
                        title = topic.get('FirstURL', '').split('/')[-1].replace('_', ' ')
                        results.append(SearchResult(
                            title=title or f"Related: {query}",
                            url=topic.get('FirstURL', ''),
                            snippet=topic['Text'],
                            source="DuckDuckGo Related",
                            relevance_score=0.7 - (i * 0.1),  # Снижаем релевантность
                            timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
                        ))
                
                return results[:limit]
                
        except Exception as e:
            return []
    
    def _search_fallback(self, query: str, limit: int) -> List[SearchResult]:
        """Fallback поисковые результаты"""
        results = []
        
        # Создаём полезные ссылки на основе запроса
        search_engines = [
            ("Google", f"https://www.google.com/search?q={quote(query)}"),
            ("Bing", f"https://www.bing.com/search?q={quote(query)}"),
            ("Yandex", f"https://yandex.ru/search/?text={quote(query)}"),
            ("Wikipedia", f"https://en.wikipedia.org/wiki/Special:Search?search={quote(query)}")
        ]
        
        for i, (engine, url) in enumerate(search_engines[:limit]):
            results.append(SearchResult(
                title=f"Поиск '{query}' в {engine}",
                url=url,
                snippet=f"Выполните поиск запроса '{query}' в поисковой системе {engine}",
                source=f"Fallback {engine}",
                relevance_score=0.3 - (i * 0.05),
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
            ))
        
        return results

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
                    "default": 10,
                    "minimum": 1,
                    "maximum": 20
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["duckduckgo", "fallback"]},
                    "description": "Источники поиска для использования",
                    "default": ["duckduckgo", "fallback"]
                }
            },
            "required": ["query"]
        }

    # Обязательные методы базового класса
    async def execute_action(self, action: str, **kwargs) -> ToolResult:
        """Выполнение действия (алиас для execute)"""
        return await self.execute(**kwargs)


# Фабричная функция
def create_enhanced_web_search_tool() -> EnhancedWebSearchTool:
    """Создание инструмента Enhanced Web Search"""
    return EnhancedWebSearchTool() 