"""
🛠️ BaseTool - Базовые классы для инструментов KittyCore 3.0

Содержит только базовые классы и интерфейсы:
- Tool (абстрактный базовый класс)
- BaseTool (расширенный базовый класс для новых инструментов)
- ToolResult (стандартный результат)
- ToolManager (менеджер инструментов)

ПРАВИЛО: Готовые инструменты должны быть в отдельных файлах!
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

from .unified_tool_result import ToolResult

logger = logging.getLogger(__name__)


class Tool(ABC):
    """
    Абстрактный базовый класс для всех инструментов KittyCore 3.0
    
    Обеспечивает:
    - Единый интерфейс execute()
    - Стандартизированные схемы
    - Логирование и валидацию
    - Статистику использования
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.created_at = datetime.now()
        self.execution_count = 0
        self.last_execution = None
        
        logger.info(f"🛠️ Инструмент {name} инициализирован")
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Выполнить инструмент с заданными параметрами
        
        Args:
            **kwargs: Параметры для выполнения
            
        Returns:
            ToolResult: Результат выполнения
        """
        pass
    
    @abstractmethod 
    def get_schema(self) -> Dict[str, Any]:
        """
        Получить JSON Schema для валидации параметров
        
        Returns:
            Dict: JSON Schema
        """
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Валидация параметров по схеме"""
        try:
            # Базовая валидация - можно расширить с jsonschema
            schema = self.get_schema()
            required = schema.get("required", [])
            
            for field in required:
                if field not in params:
                    logger.error(f"Отсутствует обязательный параметр: {field}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации параметров: {e}")
            return False
    
    def _execute_with_logging(self, **kwargs) -> ToolResult:
        """Выполнение с логированием и статистикой"""
        start_time = datetime.now()
        
        try:
            # Валидация параметров
            if not self.validate_params(kwargs):
                return ToolResult(
                    success=False,
                    error="Ошибка валидации параметров"
                )
            
            # Выполнение
            result = self.execute(**kwargs)
            
            # Обновляем статистику
            self.execution_count += 1
            self.last_execution = datetime.now()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ {self.name} выполнен за {execution_time:.2f}с")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения {self.name}: {e}")
            return ToolResult(success=False, error=str(e))
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику использования инструмента"""
        return {
            "name": self.name,
            "description": self.description,
            "execution_count": self.execution_count,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "created_at": self.created_at.isoformat()
        }


class BaseTool(Tool):
    """
    Расширенный базовый класс для новых инструментов KittyCore 3.0
    
    Добавляет:
    - Стандартные действия (actions)
    - Улучшенное логирование
    - Поддержка асинхронности
    - Метрики производительности
    """
    
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.actions = {}
        self.metrics = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "average_execution_time": 0.0
        }
    
    def get_available_actions(self) -> List[str]:
        """Получить список доступных действий"""
        return list(self.actions.keys()) if hasattr(self, 'actions') else []
    
    def execute(self, action: str = None, **kwargs) -> ToolResult:
        """
        Выполнить действие инструмента
        
        Args:
            action: Название действия
            **kwargs: Параметры действия
        """
        start_time = datetime.now()
        
        try:
            if not action:
                return ToolResult(
                    success=False,
                    error="Не указано действие",
                    data={"available_actions": self.get_available_actions()}
                )
            
            # Выполняем действие
            result = self._execute_action(action, **kwargs)
            
            # Обновляем метрики
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(True, execution_time)
            
            return result
            
        except Exception as e:
            self._update_metrics(False, (datetime.now() - start_time).total_seconds())
            logger.error(f"❌ Ошибка выполнения действия {action}: {e}")
            return ToolResult(success=False, error=str(e))
    
    def _execute_action(self, action: str, **kwargs) -> ToolResult:
        """Выполнить конкретное действие - переопределяется в наследниках"""
        return ToolResult(
            success=False,
            error=f"Действие {action} не реализовано"
        )
    
    def _update_metrics(self, success: bool, execution_time: float):
        """Обновить метрики производительности"""
        self.metrics["total_actions"] += 1
        
        if success:
            self.metrics["successful_actions"] += 1
        else:
            self.metrics["failed_actions"] += 1
        
        # Обновляем среднее время выполнения
        total = self.metrics["total_actions"]
        current_avg = self.metrics["average_execution_time"]
        self.metrics["average_execution_time"] = ((current_avg * (total - 1)) + execution_time) / total
    
    def get_schema(self) -> Dict[str, Any]:
        """Стандартная схема для BaseTool"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Действие для выполнения",
                    "enum": self.get_available_actions()
                }
            },
            "required": ["action"]
        }


class FunctionTool(Tool):
    """Обёртка для превращения функции в инструмент"""
    
    def __init__(self, name: str, description: str, func: Callable, schema: Dict[str, Any]):
        super().__init__(name, description)
        self.func = func
        self.schema = schema
    
    def execute(self, **kwargs) -> ToolResult:
        """Выполнить обёрнутую функцию"""
        try:
            result = self.func(**kwargs)
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def get_schema(self) -> Dict[str, Any]:
        """Получить схему обёрнутой функции"""
        return self.schema


class ToolManager:
    """Менеджер для управления инструментами"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.categories: Dict[str, List[str]] = {}
        
        logger.info("🔧 ToolManager инициализирован")
    
    def register(self, tool: Tool, category: str = "general") -> None:
        """Зарегистрировать инструмент"""
        self.tools[tool.name] = tool
        
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(tool.name)
        
        logger.info(f"📝 Инструмент {tool.name} зарегистрирован в категории {category}")
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Получить инструмент по имени"""
        return self.tools.get(name)
    
    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """Выполнить инструмент по имени"""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Инструмент {name} не найден",
                data={"available_tools": list(self.tools.keys())}
            )
        
        return tool._execute_with_logging(**kwargs)
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получить список инструментов"""
        if category:
            tool_names = self.categories.get(category, [])
            return [self.tools[name].get_stats() for name in tool_names]
        
        return [tool.get_stats() for tool in self.tools.values()]
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Получить инструменты по категории"""
        tool_names = self.categories.get(category, [])
        return [self.tools[name] for name in tool_names]
    
    def get_schema_for_all(self) -> Dict[str, Any]:
        """Получить схемы для всех инструментов"""
        return {
            name: tool.get_schema() 
            for name, tool in self.tools.items()
        }


# Утилиты для создания инструментов

def create_function_tool(
    name: str, 
    description: str, 
    func: Callable,
    schema: Dict[str, Any]
) -> Tool:
    """Создать инструмент из функции"""
    return FunctionTool(name, description, func, schema)


def create_simple_tool(name: str, description: str, func: Callable) -> Tool:
    """Создать простой инструмент из функции с автоматической схемой"""
    
    # Простая схема для функции
    import inspect
    sig = inspect.signature(func)
    
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        properties[param_name] = {
            "type": "string",  # Упрощенно все параметры как строки
            "description": f"Параметр {param_name}"
        }
        
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    
    schema = {
        "type": "object", 
        "properties": properties,
        "required": required
    }
    
    return create_function_tool(name, description, func, schema) 