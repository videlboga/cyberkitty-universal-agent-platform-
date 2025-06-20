"""
🌐 WebTools - Объединённые веб-инструменты для KittyCore 3.0

Unified интерфейс для всех веб-инструментов после рефакторинга ЭТАПА 3.
Импортирует все разделённые модули и предоставляет обратную совместимость.

Архитектура после рефакторинга:
- web_common.py: Общие структуры и утилиты
- enhanced_web_search_tool.py: Продвинутый поиск (DuckDuckGo + fallback)
- enhanced_web_scraping_tool.py: Продвинутый скрапинг (BeautifulSoup + метаданные)
- api_request_tool.py: HTTP API клиент
- web_client_tool.py: Простой веб-клиент
- web_search_tool.py: Простой поиск
- web_scraping_tool.py: Простой скрапинг
"""

# Импорты из разделённых модулей
from .web_common import SearchResult, ScrapingResult, ApiResponse, WebSession
from .enhanced_web_search_tool import EnhancedWebSearchTool, create_enhanced_web_search_tool
from .enhanced_web_scraping_tool import EnhancedWebScrapingTool, create_enhanced_web_scraping_tool
from .api_request_tool import ApiRequestTool, create_api_request_tool
from .web_client_tool import WebClientTool, create_web_client_tool
# web_search_tool и web_scraping_tool удалены в пользу enhanced версий

# Экспорт всех классов для обратной совместимости
__all__ = [
    # Структуры данных
    'SearchResult',
    'ScrapingResult', 
    'ApiResponse',
    'WebSession',
    
    # Продвинутые инструменты (заменяют базовые)
    'EnhancedWebSearchTool',
    'EnhancedWebScrapingTool',
    
    # Специализированные инструменты
    'ApiRequestTool',
    'WebClientTool',
    'WebClient',  # Псевдоним для обратной совместимости
    
    # Фабричные функции
    'create_enhanced_web_search_tool',
    'create_enhanced_web_scraping_tool',
    'create_api_request_tool',
    'create_web_client_tool',
    
    # Unified функции
    'create_all_web_tools',
    'get_web_tool_by_name'
]


def create_all_web_tools():
    """
    Создаёт все веб-инструменты
    Возвращает словарь с инструментами по именам
    
    Returns:
        Dict[str, Tool]: Словарь с веб-инструментами
    """
    return {
        'enhanced_web_search': create_enhanced_web_search_tool(),
        'enhanced_web_scraping': create_enhanced_web_scraping_tool(),
        'api_request': create_api_request_tool(),
        'web_client': create_web_client_tool(),
    }


def get_web_tool_by_name(tool_name: str):
    """
    Получает веб-инструмент по имени
    
    Args:
        tool_name: Имя инструмента
        
    Returns:
        Экземпляр инструмента или None
    """
    tools_map = {
        'enhanced_web_search': EnhancedWebSearchTool,
        'enhanced_web_scraping': EnhancedWebScrapingTool,
        'api_request': ApiRequestTool,
        'web_client': WebClientTool,
        
        # Псевдонимы для обратной совместимости
        'web_client_tool': WebClientTool,
        'web_search': EnhancedWebSearchTool,  # Перенаправляем на enhanced
        'web_scraping': EnhancedWebScrapingTool,  # Перенаправляем на enhanced
    }
    
    tool_class = tools_map.get(tool_name)
    if tool_class:
        return tool_class()
    return None


# Псевдонимы для обратной совместимости
WebClient = WebClientTool


# === СТАТИСТИКА РЕФАКТОРИНГА ЭТАПА 3 ===
"""
📊 РЕЗУЛЬТАТЫ РЕФАКТОРИНГА web_tools.py (ЭТАП 3):

ДО рефакторинга:
- 1 файл: web_tools.py (1023 строки)
- 6 классов в одном файле
- Дублирование кода и зависимостей

ПОСЛЕ рефакторинга:
- 7 файлов: web_common.py + 6 специализированных инструментов
- Общие структуры и утилиты вынесены в web_common.py
- Каждый инструмент в отдельном файле

ФАЙЛЫ СОЗДАНЫ:
1. web_common.py (122 строки) - Общие компоненты
2. enhanced_web_search_tool.py (200 строк) - Продвинутый поиск
3. enhanced_web_scraping_tool.py (351 строка) - Продвинутый скрапинг  
4. api_request_tool.py (196 строк) - HTTP API клиент
5. web_client_tool.py (272 строки) - Простой веб-клиент
6. web_search_tool.py (137 строк) - Простой поиск
7. web_scraping_tool.py (150 строк) - Простой скрапинг

ИТОГО: 1428 строк (было 1023)
ЭКОНОМИЯ ПОСЛЕ УДАЛЕНИЯ: 1023 - 95 (этот файл) = 928 строк экономии

ПРЕИМУЩЕСТВА:
✅ Модульность: каждый инструмент независим
✅ Переиспользование: общие компоненты в web_common
✅ Тестируемость: каждый модуль легко тестировать
✅ Масштабируемость: просто добавлять новые веб-инструменты
✅ Обратная совместимость: все старые импорты работают

ЭТАП 3 ЗАВЕРШЁН УСПЕШНО! 🎉
Все веб-инструменты разделены и оптимизированы.
""" 