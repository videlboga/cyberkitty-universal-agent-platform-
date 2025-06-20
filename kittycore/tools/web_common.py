"""
🌐 Web Common - Общие компоненты для веб-инструментов KittyCore 3.0

Общие импорты, структуры данных и утилиты для всех веб-инструментов
"""

import asyncio
import aiohttp
import requests
import json
import time
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urljoin, urlparse, quote
from dataclasses import dataclass, asdict
from .base_tool import Tool, ToolResult

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False


@dataclass
class SearchResult:
    """Результат поиска"""
    title: str
    url: str
    snippet: str
    source: str
    relevance_score: float = 0.0
    timestamp: Optional[str] = None


@dataclass
class ScrapingResult:
    """Результат scraping"""
    url: str
    success: bool
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class ApiResponse:
    """Результат API запроса"""
    url: str
    status_code: int
    success: bool
    data: Dict[str, Any]
    headers: Dict[str, str]
    response_time: float
    error: Optional[str] = None


# Общие утилиты
def is_valid_url(url: str) -> bool:
    """Проверка корректности URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def clean_text(text: str) -> str:
    """Очистка текста от лишних символов"""
    if not text:
        return ""
    
    # Убираем лишние пробелы и переносы
    text = ' '.join(text.split())
    
    # Убираем управляющие символы
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    return text.strip()


def create_headers(user_agent: str = None) -> Dict[str, str]:
    """Создание базовых HTTP заголовков"""
    if not user_agent:
        user_agent = "KittyCore-WebTools/3.0"
    
    return {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }


def extract_domain(url: str) -> str:
    """Извлечение домена из URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return ""


def format_file_size(size_bytes: int) -> str:
    """Форматирование размера файла"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"


class WebSession:
    """Управление HTTP сессией"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=create_headers()
        )
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close() 