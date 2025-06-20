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
from .web_tools import ApiRequestTool, WebClient
from .enhanced_web_scraping_tool import EnhancedWebScrapingTool  # 🔍 Продвинутый веб-скрапинг
from .enhanced_web_search_tool import EnhancedWebSearchTool  # 🔍 Продвинутый веб-поиск
from .super_system_tool import SuperSystemTool  # 🚀 ЕДИНСТВЕННЫЙ системный инструмент
from .document_tool_unified import DocumentTool  # 📄 Модульный документооборот
from .computer_use_tool import ComputerUseTool  # 🖱️ GUI автоматизация
from .ai_integration_tool import AIIntegrationTool  # 🧠 AI провайдеры (OpenRouter, VPN)
from .security_tool import SecurityTool  # 🛡️ Безопасность и анализ уязвимостей
from .image_generation_tool import ImageGenerationTool  # 🎨 Генерация изображений (FLUX, Imagen)
from .smart_function_tool import SmartFunctionTool  # 🧠 Умные Python функции
from .data_analysis_tool import DataAnalysisTool  # 📊 Полный анализ данных (Pandas)
from .network_tool import NetworkTool  # 🌐 Сетевые операции
from .media_tool import MediaTool  # 🎬 Обработка медиа
from .database_tool import DatabaseTool  # 🗄️ Работа с базами данных
from .vector_search_tool import VectorSearchTool  # 🔍 Семантический поиск
from .obsidian_tools import ObsidianAwareCodeGenerator, ObsidianAwareFileManager  # 📝 Obsidian интеграция
from .communication_tools import EmailTool, TelegramTool

# === РАСШИРЕННЫЕ ИНСТРУМЕНТЫ ===
from .code_execution_tools import CodeExecutionTool

# === МЕНЕДЖЕР ИНСТРУМЕНТОВ ===
def get_default_tool_manager() -> ToolManager:
    """Получить настроенный менеджер инструментов"""
    manager = ToolManager()
    
    # Веб-инструменты
    manager.register(EnhancedWebSearchTool(), "web")
    manager.register(EnhancedWebScrapingTool(), "web") 
    manager.register(ApiRequestTool(), "web")
    manager.register(WebClient(), "web")
    
    # Инструменты для кода - только продвинутые
    manager.register(CodeExecutionTool(), "code")
    
    # 🚀 ЕДИНСТВЕННЫЙ системный инструмент - SuperSystemTool
    manager.register(SuperSystemTool(), "system")
    
    # 📄 Документооборот - модульный DocumentTool
    manager.register(DocumentTool(), "documents")
    
    # 🖱️ GUI автоматизация - ComputerUseTool
    manager.register(ComputerUseTool(), "gui")
    
    # 🧠 AI интеграция - AIIntegrationTool 
    manager.register(AIIntegrationTool(), "ai")
    
    # 🛡️ Безопасность - SecurityTool
    manager.register(SecurityTool(), "security")
    
    # 🎨 Генерация изображений - ImageGenerationTool
    manager.register(ImageGenerationTool(), "media")
    
    # 🧠 Умные функции - SmartFunctionTool
    manager.register(SmartFunctionTool(), "code")
    
    # 📊 Анализ данных - DataAnalysisTool (полный)
    manager.register(DataAnalysisTool(), "data")
    
    # 🌐 Сетевые операции - NetworkTool
    manager.register(NetworkTool(), "network")
    
    # 🎬 Медиа обработка - MediaTool
    manager.register(MediaTool(), "media")
    
    # 🗄️ Базы данных - DatabaseTool
    manager.register(DatabaseTool(), "database")
    
    # 🔍 Семантический поиск - VectorSearchTool
    manager.register(VectorSearchTool(), "search")
    
    # 📝 Obsidian интеграция (пока отключена - требует obsidian_db и agent_id)
    # manager.register(ObsidianAwareCodeGenerator(), "obsidian")
    # manager.register(ObsidianAwareFileManager(), "obsidian")
    
    # (CodeExecutionTool уже зарегистрирован выше)
    
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
    "EnhancedWebSearchTool", "EnhancedWebScrapingTool", "ApiRequestTool", "WebClient",
    
    # Инструменты для кода
    "CodeExecutionTool",
    
    # 🚀 СИСТЕМНЫЙ ИНСТРУМЕНТ (единственный)
    "SuperSystemTool",
    
    # 📄 ДОКУМЕНТООБОРОТ (модульный)
    "DocumentTool",
    
    # 🖱️ GUI АВТОМАТИЗАЦИЯ
    "ComputerUseTool",
    
    # 🧠 AI ИНТЕГРАЦИЯ
    "AIIntegrationTool",
    
    # 🛡️ БЕЗОПАСНОСТЬ
    "SecurityTool",
    
    # 🎨 ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ
    "ImageGenerationTool",
    
    # 🧠 УМНЫЕ ФУНКЦИИ
    "SmartFunctionTool",
    
    # 📊 АНАЛИЗ ДАННЫХ
    "DataAnalysisTool",
    
    # 🌐 СЕТЕВЫЕ ОПЕРАЦИИ
    "NetworkTool",
    
    # 🎬 МЕДИА ОБРАБОТКА  
    "MediaTool",
    
    # 🗄️ БАЗЫ ДАННЫХ
    "DatabaseTool",
    
    # 🔍 СЕМАНТИЧЕСКИЙ ПОИСК
    "VectorSearchTool",
    
    # 📝 OBSIDIAN ИНТЕГРАЦИЯ
    "ObsidianAwareCodeGenerator", "ObsidianAwareFileManager",
    
    # Коммуникация
    "EmailTool", "TelegramTool",
    
    # Быстрый доступ
    "DEFAULT_TOOLS", "get_tool", "execute_tool", "get_default_tool_manager"
]

# === КАТЕГОРИИ ИНСТРУМЕНТОВ ===
TOOL_CATEGORIES = {
    "web": "Веб-инструменты - поиск, браузер, API запросы",
    "code": "Инструменты для кода - выполнение Python/Shell, генерация, умные функции", 
    "system": "🚀 SuperSystemTool - файлы, мониторинг, процессы, безопасность",
    "documents": "📄 DocumentTool - модульная обработка PDF, DOCX, TXT, CSV, JSON, XML",
    "gui": "🖱️ ComputerUseTool - GUI автоматизация, скриншоты, клики (Manjaro i3)",
    "ai": "🧠 AIIntegrationTool - OpenRouter, модели, токены, стоимость, VPN",
    "security": "🛡️ SecurityTool - анализ уязвимостей, пароли, хеши, безопасность",
    "media": "🎨🎬 Генерация изображений (FLUX, Imagen) + обработка медиа",
    "data": "📊 DataAnalysisTool - полный анализ данных + математические вычисления",
    "network": "🌐 NetworkTool - сетевые операции, мониторинг, диагностика",
    "database": "🗄️ DatabaseTool - работа с базами данных (SQL, NoSQL)",
    "search": "🔍 VectorSearchTool - семантический поиск, RAG, эмбеддинги",
    "obsidian": "📝 ObsidianAware - интеграция с Obsidian vault",
    "communication": "📧 Коммуникация - email, telegram, уведомления"
} 