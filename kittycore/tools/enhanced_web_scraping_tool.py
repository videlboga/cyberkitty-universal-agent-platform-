"""
Продвинутый инструмент веб-скрапинга для KittyCore 3.0
Поддерживает парсинг HTML, извлечение метаданных, фильтрацию контента
"""

import asyncio
import time
import re
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    BeautifulSoup = None  # Fallback для типов

from .base_tool import Tool, ToolResult
from .web_common import ScrapingResult, is_valid_url, clean_text, create_headers, WebSession


@dataclass
class ScrapingConfig:
    """Конфигурация для скрапинга"""
    extract_links: bool = True
    extract_images: bool = True
    extract_metadata: bool = True
    filter_text: bool = True
    max_content_length: int = 50000
    timeout: int = 30
    follow_redirects: bool = True


class EnhancedWebScrapingTool(Tool):
    """
    Продвинутый инструмент веб-скрапинга
    
    Возможности:
    - Парсинг HTML с BeautifulSoup
    - Извлечение текста, ссылок, изображений
    - Метаданные страницы (title, description, keywords)
    - Фильтрация и очистка контента
    - Поддержка множественных URL
    - Асинхронная обработка
    """
    
    def __init__(self):
        super().__init__(
            name="enhanced_web_scraping",
            description="Продвинутый веб-скрапинг с извлечением структурированных данных"
        )
        self.session = WebSession()
        
        # Проверка зависимостей
        if not AIOHTTP_AVAILABLE:
            print("⚠️ aiohttp не установлен - асинхронные запросы недоступны")
        if not BS4_AVAILABLE:
            print("⚠️ BeautifulSoup4 не установлен - парсинг HTML ограничен")
    
    def get_schema(self) -> Dict[str, Any]:
        """Схема параметров инструмента"""
        return {
            "type": "object",
            "properties": {
                "urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Список URL для скрапинга"
                },
                "extract_links": {
                    "type": "boolean",
                    "default": True,
                    "description": "Извлекать ссылки"
                },
                "extract_images": {
                    "type": "boolean", 
                    "default": True,
                    "description": "Извлекать изображения"
                },
                "extract_metadata": {
                    "type": "boolean",
                    "default": True,
                    "description": "Извлекать метаданные"
                },
                "filter_text": {
                    "type": "boolean",
                    "default": True,
                    "description": "Фильтровать и очищать текст"
                },
                "max_content_length": {
                    "type": "integer",
                    "default": 50000,
                    "description": "Максимальная длина контента"
                }
            },
            "required": ["urls"]
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Выполнение веб-скрапинга"""
        try:
            # Парсим параметры
            urls = kwargs.get("urls", [])
            if isinstance(urls, str):
                urls = [urls]
            
            config = ScrapingConfig(
                extract_links=kwargs.get("extract_links", True),
                extract_images=kwargs.get("extract_images", True),
                extract_metadata=kwargs.get("extract_metadata", True),
                filter_text=kwargs.get("filter_text", True),
                max_content_length=kwargs.get("max_content_length", 50000)
            )
            
            # Валидация URL
            valid_urls = []
            for url in urls:
                if is_valid_url(url):
                    valid_urls.append(url)
                else:
                    print(f"⚠️ Невалидный URL пропущен: {url}")
            
            if not valid_urls:
                return ToolResult(
                    success=False,
                    error="Нет валидных URL для скрапинга",
                    data={"results": []}
                )
            
            # Асинхронный скрапинг
            results = await self._scrape_multiple_urls(valid_urls, config)
            
            return ToolResult(
                success=True,
                data={
                    "total_urls": len(valid_urls),
                    "successful_scrapes": len([r for r in results if r.success]),
                    "results": [self._format_result(r) for r in results]
                }
            )
            
        except Exception as e:
            print(f"❌ Ошибка веб-скрапинга: {e}")
            return ToolResult(
                success=False,
                error=f"Ошибка скрапинга: {str(e)}",
                data={"results": []}
            )
    
    async def _scrape_multiple_urls(self, urls: List[str], config: ScrapingConfig) -> List[ScrapingResult]:
        """Асинхронный скрапинг множественных URL"""
        tasks = []
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=config.timeout),
            headers=create_headers()
        ) as session:
            for url in urls:
                task = self._scrape_single_url(session, url, config)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Обработка результатов и исключений
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ScrapingResult(
                    url=urls[i],
                    success=False,
                    data={},
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _scrape_single_url(self, session: aiohttp.ClientSession, url: str, config: ScrapingConfig) -> ScrapingResult:
        """Скрапинг одного URL"""
        start_time = time.time()
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return ScrapingResult(
                        url=url,
                        success=False,
                        data={},
                        error=f"HTTP {response.status}: {response.reason}"
                    )
                
                # Получаем контент
                content = await response.text()
                response_time = time.time() - start_time
                
                # Ограничиваем размер контента
                if len(content) > config.max_content_length:
                    content = content[:config.max_content_length]
                
                # Парсим HTML
                soup = BeautifulSoup(content, 'html.parser')
                
                # Собираем все данные в структуру data
                scraped_data = {
                    "response_time": response_time,
                    "content_length": len(content),
                    "raw_html": content[:1000] if len(content) > 1000 else content,  # Первые 1000 символов
                }
                
                # Извлекаем текст
                if config.filter_text:
                    scraped_data["text"] = self._extract_clean_text(soup)
                else:
                    scraped_data["text"] = soup.get_text()
                
                # Извлекаем метаданные
                if config.extract_metadata:
                    scraped_data["page_metadata"] = self._extract_metadata(soup)
                
                # Извлекаем ссылки
                if config.extract_links:
                    scraped_data["links"] = self._extract_links(soup, url)
                
                # Извлекаем изображения
                if config.extract_images:
                    scraped_data["images"] = self._extract_images(soup, url)
                
                # Создаем правильный результат
                return ScrapingResult(
                    url=url,
                    success=True,
                    data=scraped_data,
                    error=None
                )
                
        except Exception as e:
            return ScrapingResult(
                url=url,
                success=False,
                data={},
                error=str(e)
            )
    
    def _extract_clean_text(self, soup) -> str:
        """Извлечение и очистка текста"""
        # Удаляем скрипты и стили
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Извлекаем основной контент
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content|main|article'))
        
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
        
        return clean_text(text)
    
    def _extract_metadata(self, soup) -> Dict[str, str]:
        """Извлечение метаданных страницы"""
        metadata = {}
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            metadata['description'] = desc_tag.get('content', '').strip()
        
        # Meta keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag:
            metadata['keywords'] = keywords_tag.get('content', '').strip()
        
        # Open Graph
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title:
            metadata['og:title'] = og_title.get('content', '').strip()
        
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc:
            metadata['og:description'] = og_desc.get('content', '').strip()
        
        return metadata
    
    def _extract_links(self, soup, base_url: str) -> List[Dict[str, str]]:
        """Извлечение ссылок"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            text = clean_text(link.get_text()).strip()
            
            # Абсолютный URL
            full_url = urljoin(base_url, href)
            
            if full_url and text:
                links.append({
                    'url': full_url,
                    'text': text[:200],  # Ограничиваем длину
                    'title': link.get('title', '').strip()
                })
        
        return links[:50]  # Максимум 50 ссылок
    
    def _extract_images(self, soup, base_url: str) -> List[Dict[str, str]]:
        """Извлечение изображений"""
        images = []
        
        for img in soup.find_all('img', src=True):
            src = img['src'].strip()
            alt = img.get('alt', '').strip()
            
            # Абсолютный URL
            full_url = urljoin(base_url, src)
            
            if full_url:
                images.append({
                    'url': full_url,
                    'alt': alt[:200],  # Ограничиваем длину
                    'title': img.get('title', '').strip()
                })
        
        return images[:20]  # Максимум 20 изображений
    
    def _format_result(self, result: ScrapingResult) -> Dict[str, Any]:
        """Форматирование результата для вывода"""
        formatted = {
            "url": result.url,
            "success": result.success
        }
        
        if not result.success:
            formatted["error"] = result.error
            return formatted
        
        # Извлекаем данные из структуры data
        data = result.data
        
        if "response_time" in data:
            formatted["response_time"] = f"{data['response_time']:.2f}s"
        
        if "content_length" in data:
            formatted["content_length"] = data["content_length"]
        
        if "text" in data and data["text"]:
            text = data["text"]
            formatted["text_preview"] = text[:500] + "..." if len(text) > 500 else text
            formatted["text_length"] = len(text)
        
        if "page_metadata" in data and data["page_metadata"]:
            formatted["metadata"] = data["page_metadata"]
        
        if "links" in data and data["links"]:
            formatted["links_count"] = len(data["links"])
            formatted["links_preview"] = data["links"][:5]  # Первые 5 ссылок
        
        if "images" in data and data["images"]:
            formatted["images_count"] = len(data["images"])
            formatted["images_preview"] = data["images"][:3]  # Первые 3 изображения
        
        return formatted


def create_enhanced_web_scraping_tool() -> EnhancedWebScrapingTool:
    """Фабричная функция для создания инструмента"""
    return EnhancedWebScrapingTool() 