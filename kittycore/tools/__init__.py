"""
🛠️ KittyCore 3.0 - Централизованная система инструментов

Принципы:
- Единый интерфейс для всех инструментов
- Отсутствие моков - только реальная работа  
- Категоризация по назначению
- Консистентный API и обработка ошибок
"""

# === БАЗОВАЯ АРХИТЕКТУРА ===
from .base_tool import Tool, ToolResult, ToolManager

# === КАТЕГОРИИ ИНСТРУМЕНТОВ ===
from .web_tools import WebSearchTool, WebScrapingTool, ApiRequestTool, WebClient
from .code_tools import PythonExecutionTool, CodeGenerator
from .system_tools import FileManager, SystemTools
from .data_tools import PandasTool, MathCalculationTool
from .communication_tools import EmailTool, TelegramTool

# === РАСШИРЕННЫЕ ИНСТРУМЕНТЫ ===
from .enhanced_system_tools import EnhancedSystemTool
from .code_execution_tools import CodeExecutionTool

# === МЕНЕДЖЕР ИНСТРУМЕНТОВ ===
def get_default_tool_manager() -> ToolManager:
    """Получить настроенный менеджер инструментов"""
    manager = ToolManager()
    
    # Веб-инструменты
    manager.register(WebSearchTool(), "web")
    manager.register(WebScrapingTool(), "web") 
    manager.register(ApiRequestTool(), "web")
    manager.register(WebClient(), "web")
    
    # Инструменты для кода
    manager.register(PythonExecutionTool(), "code")
    manager.register(CodeGenerator(), "code")
    
    # Системные инструменты
    manager.register(FileManager(), "system")
    manager.register(SystemTools(), "system")
    manager.register(EnhancedSystemTool(), "system")
    
    # Продвинутые инструменты кода
    manager.register(CodeExecutionTool(), "code")
    
    # Анализ данных
    manager.register(PandasTool(), "data")
    manager.register(MathCalculationTool(), "data")
    
    # Коммуникация
    manager.register(EmailTool(), "communication")
    manager.register(TelegramTool(), "communication")
    
    return manager

# === БЫСТРЫЙ ДОСТУП ===
DEFAULT_TOOLS = get_default_tool_manager()

def get_tool(name: str) -> Tool:
    """Быстрый доступ к инструменту"""
    return DEFAULT_TOOLS.get_tool(name)

def execute_tool(name: str, **kwargs) -> ToolResult:
    """Быстрое выполнение инструмента"""
    return DEFAULT_TOOLS.execute_tool(name, **kwargs)

__version__ = "3.0.0"
__all__ = [
    # Базовые классы
    "Tool", "ToolResult", "ToolManager",
    
    # Веб-инструменты  
    "WebSearchTool", "WebScrapingTool", "ApiRequestTool", "WebClient",
    
    # Инструменты для кода
    "PythonExecutionTool", "CodeGenerator", "CodeExecutionTool",
    
    # Системные инструменты
    "FileManager", "SystemTools", "EnhancedSystemTool",
    
    # Анализ данных
    "PandasTool", "MathCalculationTool",
    
    # Коммуникация
    "EmailTool", "TelegramTool",
    
    # Быстрый доступ
    "DEFAULT_TOOLS", "get_tool", "execute_tool", "get_default_tool_manager"
]

# === КАТЕГОРИИ ИНСТРУМЕНТОВ ===
TOOL_CATEGORIES = {
    "web": "Веб-инструменты - поиск, браузер, API запросы",
    "code": "Инструменты для кода - выполнение Python/Shell, генерация, sandbox", 
    "system": "Системные - файлы с безопасностью, мониторинг, healthcheck",
    "data": "Анализ данных - статистика, графики, вычисления",
    "communication": "Коммуникация - email, telegram, уведомления"
} 