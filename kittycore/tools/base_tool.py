"""
Tools - Система инструментов для AI агентов

Простая, но мощная система инструментов с:
- Единым интерфейсом для всех инструментов
- Автоматической валидацией параметров
- JSON Schema для описания
- Встроенным логированием и ошибками
"""

import json
import logging
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Результат выполнения инструмента"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class Tool(ABC):
    """
    Базовый класс для всех инструментов
    
    Принципы:
    - Единый интерфейс execute()
    - JSON Schema для валидации
    - Автоматическое логирование
    - Обработка ошибок
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.created_at = datetime.now()
        self.execution_count = 0
        self.last_execution = None
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Выполнить инструмент
        
        Args:
            **kwargs: Параметры для выполнения
            
        Returns:
            ToolResult с результатом выполнения
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Получить JSON Schema для параметров инструмента
        
        Returns:
            JSON Schema для валидации параметров
        """
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Валидировать параметры по схеме"""
        try:
            # Простая валидация - в production нужна jsonschema
            schema = self.get_schema()
            required = schema.get("required", [])
            
            for param in required:
                if param not in params:
                    raise ValueError(f"Отсутствует обязательный параметр: {param}")
            
            return True
        except Exception as e:
            logger.error(f"Ошибка валидации параметров {self.name}: {e}")
            return False
    
    def _execute_with_logging(self, **kwargs) -> ToolResult:
        """Выполнить с логированием и подсчетом"""
        start_time = datetime.now()
        
        try:
            # Валидируем параметры
            if not self.validate_params(kwargs):
                return ToolResult(
                    success=False,
                    error="Ошибка валидации параметров"
                )
            
            # Выполняем
            logger.info(f"Выполняем инструмент: {self.name}")
            result = self.execute(**kwargs)
            
            # Обновляем статистику
            self.execution_count += 1
            self.last_execution = datetime.now()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            logger.info(f"Инструмент {self.name} выполнен за {execution_time:.2f}с")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка выполнения {self.name}: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику использования инструмента"""
        return {
            "name": self.name,
            "description": self.description,
            "execution_count": self.execution_count,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "created_at": self.created_at.isoformat()
        }


class WebSearchTool(Tool):
    """Инструмент для поиска в интернете"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Поиск информации в интернете"
        )
    
    def execute(self, query: str, limit: int = 5) -> ToolResult:
        """Выполнить поиск в интернете"""
        try:
            # Заглушка - в production интегрировать с реальным поиском
            results = [
                {
                    "title": f"Результат поиска {i+1} для '{query}'",
                    "url": f"https://example.com/result{i+1}",
                    "snippet": f"Описание результата {i+1} для запроса '{query}'"
                }
                for i in range(min(limit, 3))
            ]
            
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "results": results,
                    "total_found": len(results)
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def get_schema(self) -> Dict[str, Any]:
        """Схема для web поиска"""
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
                    "maximum": 20
                }
            },
            "required": ["query"]
        }


class DatabaseTool(Tool):
    """Инструмент для работы с базой данных"""
    
    def __init__(self, connection_string: str = None):
        super().__init__(
            name="database",
            description="Выполнение запросов к базе данных"
        )
        self.connection_string = connection_string
    
    def execute(self, query: str, params: Optional[List] = None) -> ToolResult:
        """Выполнить SQL запрос"""
        try:
            # Заглушка - в production подключаться к реальной БД
            if query.lower().startswith("select"):
                # Имитируем SELECT
                return ToolResult(
                    success=True,
                    data={
                        "query": query,
                        "rows": [
                            {"id": 1, "name": "Тестовая запись 1"},
                            {"id": 2, "name": "Тестовая запись 2"}
                        ],
                        "row_count": 2
                    }
                )
            else:
                # Имитируем INSERT/UPDATE/DELETE
                return ToolResult(
                    success=True,
                    data={
                        "query": query,
                        "affected_rows": 1
                    }
                )
                
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def get_schema(self) -> Dict[str, Any]:
        """Схема для database запросов"""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL запрос для выполнения"
                },
                "params": {
                    "type": "array",
                    "description": "Параметры для запроса",
                    "items": {"type": "string"}
                }
            },
            "required": ["query"]
        }


class EmailTool(Tool):
    """Инструмент для отправки email"""
    
    def __init__(self, smtp_config: Optional[Dict] = None):
        super().__init__(
            name="email",
            description="Отправка email сообщений"
        )
        self.smtp_config = smtp_config or {}
    
    def execute(self, to: str, subject: str, body: str, **kwargs) -> ToolResult:
        """Отправить email"""
        try:
            # Заглушка - в production настроить SMTP
            logger.info(f"Отправляется email на {to} с темой '{subject}'")
            
            return ToolResult(
                success=True,
                data={
                    "to": to,
                    "subject": subject,
                    "body_length": len(body),
                    "sent_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def get_schema(self) -> Dict[str, Any]:
        """Схема для email"""
        return {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Email получателя",
                    "format": "email"
                },
                "subject": {
                    "type": "string",
                    "description": "Тема сообщения"
                },
                "body": {
                    "type": "string",
                    "description": "Тело сообщения"
                },
                "cc": {
                    "type": "string",
                    "description": "Копия (опционально)"
                }
            },
            "required": ["to", "subject", "body"]
        }


class FunctionTool(Tool):
    """Обертка для превращения функции в инструмент"""
    
    def __init__(self, name: str, description: str, func: Callable, schema: Dict[str, Any]):
        super().__init__(name, description)
        self.func = func
        self.schema = schema
    
    def execute(self, **kwargs) -> ToolResult:
        """Выполнить обернутую функцию"""
        try:
            result = self.func(**kwargs)
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def get_schema(self) -> Dict[str, Any]:
        """Получить схему обернутой функции"""
        return self.schema


class ToolManager:
    """Менеджер для управления инструментами"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.categories: Dict[str, List[str]] = {}
    
    def register(self, tool: Tool, category: str = "general") -> None:
        """Зарегистрировать инструмент"""
        self.tools[tool.name] = tool
        
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(tool.name)
        
        logger.info(f"Зарегистрирован инструмент: {tool.name} ({category})")
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Получить инструмент по имени"""
        return self.tools.get(name)
    
    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """Выполнить инструмент по имени"""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Инструмент '{name}' не найден"
            )
        
        return tool._execute_with_logging(**kwargs)
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получить список всех инструментов"""
        if category:
            tool_names = self.categories.get(category, [])
            return [
                self.tools[name].get_stats() 
                for name in tool_names
            ]
        
        return [tool.get_stats() for tool in self.tools.values()]

    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Получить инструменты по категории"""
        tool_names = self.categories.get(category, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def get_schema_for_all(self) -> Dict[str, Any]:
        """Получить схемы всех инструментов"""
        return {
            name: tool.get_schema()
            for name, tool in self.tools.items()
        }


# Функции для быстрого создания инструментов
def create_function_tool(
    name: str, 
    description: str, 
    func: Callable,
    schema: Dict[str, Any]
) -> Tool:
    """Создать инструмент из функции"""
    return FunctionTool(name, description, func, schema)


def create_simple_tool(name: str, description: str, func: Callable) -> Tool:
    """Создать простой инструмент без схемы"""
    simple_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }
    return FunctionTool(name, description, func, simple_schema)


# Глобальный менеджер инструментов
default_tool_manager = ToolManager()

# Регистрируем базовые инструменты
default_tool_manager.register(WebSearchTool(), "web")
default_tool_manager.register(DatabaseTool(), "data")
default_tool_manager.register(EmailTool(), "communication")

# Добавляем SystemTools
try:
    from .system_tools import SystemTools
    default_tool_manager.register(SystemTools(), "system")
    logger.info("SystemTools зарегистрирован")
except ImportError as e:
    logger.warning(f"Не удалось загрузить SystemTools: {e}") 