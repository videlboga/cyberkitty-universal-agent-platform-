"""
Тесты для улучшенных веб-инструментов KittyCore 3.0
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from kittycore.tools.web_tools import (
    EnhancedWebSearchTool, 
    EnhancedWebScrapingTool,
    SearchResult
)


class TestEnhancedWebSearchTool:
    """Тесты для EnhancedWebSearchTool"""
    
    @pytest.fixture
    def search_tool(self):
        """Фикстура для инструмента поиска"""
        return EnhancedWebSearchTool()
    
    @pytest.mark.asyncio
    async def test_search_tool_initialization(self, search_tool):
        """Тест инициализации инструмента поиска"""
        assert search_tool.name == "enhanced_web_search"
        assert "продвинутый поиск" in search_tool.description.lower()
        assert search_tool.session is None
    
    @pytest.mark.asyncio
    async def test_ensure_session(self, search_tool):
        """Тест создания сессии"""
        await search_tool._ensure_session()
        assert search_tool.session is not None
        assert not search_tool.session.closed
        
        # Закрываем сессию для очистки
        await search_tool._close_session()
    
    @pytest.mark.asyncio
    async def test_search_with_duckduckgo_mock(self, search_tool):
        """Тест поиска с мокированным DuckDuckGo"""
        mock_response_data = {
            "Answer": "Тестовый ответ",
            "AnswerURL": "https://example.com",
            "Abstract": "Абстрактное описание",
            "AbstractURL": "https://example.com/abstract",
            "Heading": "Тестовый заголовок",
            "RelatedTopics": [
                {
                    "Text": "Связанная тема",
                    "FirstURL": "https://example.com/related"
                }
            ]
        }
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.status = 200
            # Исправляем async mock
            async def mock_json():
                return mock_response_data
            mock_response.json = mock_json
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            search_tool.session = mock_session.return_value.__aenter__.return_value
            
            result = await search_tool.execute("тестовый запрос", limit=5)
            
            assert result.success is True
            assert "results" in result.data
            assert "query" in result.data
            assert result.data["query"] == "тестовый запрос"
    
    @pytest.mark.asyncio
    async def test_fallback_search(self, search_tool):
        """Тест fallback поиска"""
        fallback_results = search_tool._search_fallback("Python", 3)
        
        assert len(fallback_results) <= 3
        assert all(isinstance(r, SearchResult) for r in fallback_results)
        assert all("Python" in r.title for r in fallback_results)
        assert all(r.source.startswith("Fallback") for r in fallback_results)
    
    @pytest.mark.asyncio 
    async def test_search_error_handling(self, search_tool):
        """Тест обработки ошибок поиска"""
        with patch('aiohttp.ClientSession') as mock_session:
            # Настраиваем исключение
            mock_session.side_effect = Exception("Network error")
            
            result = await search_tool.execute("тестовый запрос")
            
            assert result.success is False
            assert "ошибка поиска" in result.error.lower()
    
    def test_search_schema(self, search_tool):
        """Тест схемы инструмента поиска"""
        schema = search_tool.get_schema()
        
        assert schema["type"] == "object"
        assert "query" in schema["properties"]
        assert "limit" in schema["properties"]
        assert "sources" in schema["properties"]
        assert "query" in schema["required"]


class TestEnhancedWebScrapingTool:
    """Тесты для EnhancedWebScrapingTool"""
    
    @pytest.fixture
    def scraping_tool(self):
        """Фикстура для инструмента scraping"""
        return EnhancedWebScrapingTool()
    
    @pytest.mark.asyncio
    async def test_scraping_tool_initialization(self, scraping_tool):
        """Тест инициализации инструмента scraping"""
        assert scraping_tool.name == "enhanced_web_scraping"
        assert "продвинутое извлечение" in scraping_tool.description.lower()
        assert scraping_tool.session is None
    
    @pytest.mark.asyncio
    async def test_ensure_session(self, scraping_tool):
        """Тест создания сессии"""
        await scraping_tool._ensure_session()
        assert scraping_tool.session is not None
        assert not scraping_tool.session.closed
        
        # Закрываем для очистки
        if scraping_tool.session and not scraping_tool.session.closed:
            await scraping_tool.session.close()
    
    @pytest.mark.asyncio
    async def test_single_scrape_text_mock(self, scraping_tool):
        """Тест извлечения текста с мокированным ответом"""
        mock_html = """
        <html>
            <head><title>Тестовая страница</title></head>
            <body>
                <h1>Главный заголовок</h1>
                <p>Основной текст страницы</p>
                <script>console.log('script')</script>
            </body>
        </html>
        """
        
        # Используем прямой мок _single_scrape вместо сложного aiohttp mock
        from kittycore.tools.base_tool import ToolResult
        
        expected_result = ToolResult(
            success=True,
            data={
                "url": "https://example.com",
                "title": "Тестовая страница",
                "text": "Главный заголовок Основной текст страницы",
                "text_length": 46,
                "headings": [{"level": "h1", "text": "Главный заголовок"}],
                "method": "enhanced_beautifulsoup"
            }
        )
        
        with patch.object(scraping_tool, '_single_scrape', return_value=expected_result):
            result = await scraping_tool.execute("https://example.com", method="text")
            
            assert result.success is True
            assert "text" in result.data
            assert "title" in result.data
            assert result.data["title"] == "Тестовая страница"
    
    @pytest.mark.asyncio
    async def test_smart_extract_mock(self, scraping_tool):
        """Тест умного извлечения"""
        # Используем прямой мок _single_scrape
        from kittycore.tools.base_tool import ToolResult
        
        expected_result = ToolResult(
            success=True,
            data={
                "url": "https://example.com",
                "title": "Smart Test Page",
                "description": "Test description",
                "main_content": "Main Heading Main content text",
                "images": [{"src": "https://example.com/image.jpg", "alt": "Test image", "title": ""}],
                "headings": [{"level": "h1", "text": "Main Heading"}],
                "method": "smart_extract"
            }
        )
        
        with patch.object(scraping_tool, '_single_scrape', return_value=expected_result):
            result = await scraping_tool.execute("https://example.com", method="smart")
            
            assert result.success is True
            assert result.data["title"] == "Smart Test Page"
            assert "description" in result.data
            assert "main_content" in result.data
            assert "images" in result.data
            assert "headings" in result.data
    
    @pytest.mark.asyncio
    async def test_batch_scraping_mock(self, scraping_tool):
        """Тест batch scraping"""
        urls = ["https://example1.com", "https://example2.com"]
        
        with patch.object(scraping_tool, '_single_scrape') as mock_single:
            from kittycore.tools.base_tool import ToolResult
            
            # Настраиваем успешные результаты
            mock_single.return_value = ToolResult(
                success=True,
                data={"url": "mock", "text": "mock text", "method": "text"}
            )
            
            result = await scraping_tool.execute(
                "https://example1.com", 
                method="text",
                batch_urls=urls
            )
            
            assert result.success is True
            assert "batch_results" in result.data
            assert result.data["successful_count"] == 2
            assert result.data["failed_count"] == 0
    
    def test_is_useful_link(self, scraping_tool):
        """Тест определения полезности ссылок"""
        # Полезные ссылки
        assert scraping_tool._is_useful_link("https://example.com/page") is True
        assert scraping_tool._is_useful_link("http://test.org/article") is True
        
        # Бесполезные ссылки
        assert scraping_tool._is_useful_link("#anchor") is False
        assert scraping_tool._is_useful_link("javascript:void(0)") is False
        assert scraping_tool._is_useful_link("mailto:test@example.com") is False
        assert scraping_tool._is_useful_link("https://example.com/image.jpg") is False
        assert scraping_tool._is_useful_link("https://example.com/file.pdf") is False
    
    @pytest.mark.asyncio
    async def test_scraping_error_handling(self, scraping_tool):
        """Тест обработки ошибок scraping"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.status = 404
            mock_response.reason = "Not Found"
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            scraping_tool.session = mock_session.return_value.__aenter__.return_value
            
            result = await scraping_tool.execute("https://example.com")
            
            assert result.success is False
            # Проверяем что есть ошибка HTTP
            assert ("404" in str(result.error) or "Not Found" in str(result.error) or "HTTP" in str(result.error))
    
    def test_scraping_schema(self, scraping_tool):
        """Тест схемы инструмента scraping"""
        schema = scraping_tool.get_schema()
        
        assert schema["type"] == "object"
        assert "url" in schema["properties"]
        assert "method" in schema["properties"]
        assert "batch_urls" in schema["properties"]
        assert "extract_metadata" in schema["properties"]
        assert "url" in schema["required"]
        
        # Проверяем методы
        methods = schema["properties"]["method"]["enum"]
        assert "text" in methods
        assert "links" in methods
        assert "selector" in methods
        assert "smart" in methods


class TestSearchResult:
    """Тесты для dataclass SearchResult"""
    
    def test_search_result_creation(self):
        """Тест создания SearchResult"""
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            source="Test Source",
            relevance_score=0.8,
            timestamp="2025-01-08 12:00:00"
        )
        
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.snippet == "Test snippet"
        assert result.source == "Test Source"
        assert result.relevance_score == 0.8
        assert result.timestamp == "2025-01-08 12:00:00"
    
    def test_search_result_defaults(self):
        """Тест значений по умолчанию SearchResult"""
        result = SearchResult(
            title="Test",
            url="https://example.com",
            snippet="Test",
            source="Test"
        )
        
        assert result.relevance_score == 0.0
        assert result.timestamp is None


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"]) 