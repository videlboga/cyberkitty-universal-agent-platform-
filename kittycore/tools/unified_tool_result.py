"""
Unified ToolResult - Единый результат для всех инструментов KittyCore 3.0
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime


@dataclass
class ToolResult:
    """
    Унифицированный результат выполнения инструмента
    
    Объединяет лучшие практики из universal_tools.py и base_tool.py
    """
    success: bool
    data: Any = None  # Основные данные результата (было result в universal_tools)
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    timestamp: Optional[datetime] = field(default_factory=datetime.now)
    
    # Для обратной совместимости с universal_tools.py
    @property
    def result(self) -> Any:
        """Алиас для data для обратной совместимости"""
        return self.data
    
    @result.setter
    def result(self, value: Any):
        """Сеттер для result"""
        self.data = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata or {},
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def success_result(cls, data: Any = None, metadata: Dict[str, Any] = None, execution_time: float = None) -> "ToolResult":
        """Создать успешный результат"""
        return cls(
            success=True,
            data=data,
            metadata=metadata or {},
            execution_time=execution_time
        )
    
    @classmethod
    def error_result(cls, error: str, metadata: Dict[str, Any] = None, execution_time: float = None) -> "ToolResult":
        """Создать результат с ошибкой"""
        return cls(
            success=False,
            error=error,
            metadata=metadata or {},
            execution_time=execution_time
        ) 