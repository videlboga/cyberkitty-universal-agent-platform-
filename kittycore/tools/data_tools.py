"""
📊 DataTools - Инструменты анализа данных для KittyCore 3.0

Реальные инструменты для работы с данными:
- Анализ данных с Pandas (если доступен)
- Математические вычисления
- Статистика
- Простые графики
"""

import json
import math
import statistics
from typing import Dict, Any, List, Optional, Union
from .base_tool import Tool, ToolResult

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class PandasTool(Tool):
    """Инструмент анализа данных с Pandas"""
    
    def __init__(self):
        super().__init__(
            name="pandas_tool",
            description="Анализ данных с помощью Pandas"
        )
    
    def execute(self, operation: str, data: Union[List, str] = None, **kwargs) -> ToolResult:
        """Выполнить операцию анализа данных"""
        if not PANDAS_AVAILABLE:
            return ToolResult(
                success=False,
                error="Pandas не доступен. Установите: pip install pandas"
            )
        
        try:
            if operation == "analyze_list":
                return self._analyze_list(data)
            elif operation == "load_csv":
                return self._load_csv(data, **kwargs)
            elif operation == "describe_data":
                return self._describe_data(data)
            elif operation == "create_dataframe":
                return self._create_dataframe(data, **kwargs)
            else:
                return ToolResult(
                    success=False,
                    error=f"Неизвестная операция: {operation}"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка анализа данных: {str(e)}"
            )
    
    def _analyze_list(self, data: List) -> ToolResult:
        """Анализ списка данных"""
        if not data:
            return ToolResult(
                success=False,
                error="Данные для анализа не предоставлены"
            )
        
        import pandas as pd
        
        # Создаем DataFrame
        df = pd.DataFrame(data, columns=['value'])
        
        # Основная статистика
        stats = {
            "count": len(df),
            "type": str(df['value'].dtype),
            "memory_usage": df.memory_usage(deep=True).sum()
        }
        
        # Если числовые данные
        if pd.api.types.is_numeric_dtype(df['value']):
            stats.update({
                "mean": float(df['value'].mean()),
                "median": float(df['value'].median()),
                "std": float(df['value'].std()),
                "min": float(df['value'].min()),
                "max": float(df['value'].max()),
                "sum": float(df['value'].sum())
            })
        
        # Анализ пропущенных значений
        stats["missing_values"] = int(df['value'].isnull().sum())
        stats["unique_values"] = int(df['value'].nunique())
        
        return ToolResult(
            success=True,
            data={
                "operation": "analyze_list",
                "statistics": stats,
                "sample_data": data[:5],  # Первые 5 элементов
                "dataframe_info": str(df.info())
            }
        )
    
    def _load_csv(self, filepath: str, **kwargs) -> ToolResult:
        """Загрузить CSV файл"""
        import pandas as pd
        
        try:
            df = pd.read_csv(filepath, **kwargs)
            
            return ToolResult(
                success=True,
                data={
                    "operation": "load_csv",
                    "filepath": filepath,
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.to_dict(),
                    "sample": df.head().to_dict(),
                    "memory_usage": df.memory_usage(deep=True).sum()
                }
            )
            
        except FileNotFoundError:
            return ToolResult(
                success=False,
                error=f"Файл не найден: {filepath}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка загрузки CSV: {str(e)}"
            )
    
    def _describe_data(self, data: Union[List, Dict]) -> ToolResult:
        """Описательная статистика"""
        import pandas as pd
        
        if isinstance(data, list):
            df = pd.DataFrame(data, columns=['value'])
        elif isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            return ToolResult(
                success=False,
                error="Данные должны быть списком или словарем"
            )
        
        description = df.describe(include='all').to_dict()
        
        return ToolResult(
            success=True,
            data={
                "operation": "describe_data",
                "description": description,
                "shape": df.shape,
                "dtypes": df.dtypes.to_dict()
            }
        )
    
    def _create_dataframe(self, data: Dict, **kwargs) -> ToolResult:
        """Создать DataFrame"""
        import pandas as pd
        
        try:
            df = pd.DataFrame(data)
            
            return ToolResult(
                success=True,
                data={
                    "operation": "create_dataframe",
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.to_dict(),
                    "head": df.head().to_dict(),
                    "info": str(df.info())
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка создания DataFrame: {str(e)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["analyze_list", "load_csv", "describe_data", "create_dataframe"],
                    "description": "Операция анализа данных"
                },
                "data": {
                    "description": "Данные для анализа (список, словарь или путь к файлу)"
                }
            },
            "required": ["operation"]
        }


class MathCalculationTool(Tool):
    """Математические вычисления"""
    
    def __init__(self):
        super().__init__(
            name="math_calculation",
            description="Выполнение математических вычислений и статистики"
        )
    
    def execute(self, operation: str, expression: str = None, 
               data: List[float] = None, **kwargs) -> ToolResult:
        """Выполнить математическую операцию"""
        try:
            if operation == "calculate":
                return self._calculate_expression(expression)
            elif operation == "statistics":
                return self._calculate_statistics(data)
            elif operation == "basic_math":
                return self._basic_math(**kwargs)
            elif operation == "convert_units":
                return self._convert_units(**kwargs)
            else:
                return ToolResult(
                    success=False,
                    error=f"Неизвестная операция: {operation}"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка вычисления: {str(e)}"
            )
    
    def _calculate_expression(self, expression: str) -> ToolResult:
        """Вычислить математическое выражение"""
        if not expression:
            return ToolResult(
                success=False,
                error="Выражение не указано"
            )
        
        # Безопасные функции для eval
        safe_dict = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
        }
        
        try:
            result = eval(expression, safe_dict)
            
            return ToolResult(
                success=True,
                data={
                    "operation": "calculate",
                    "expression": expression,
                    "result": result,
                    "type": type(result).__name__
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка вычисления выражения: {str(e)}"
            )
    
    def _calculate_statistics(self, data: List[float]) -> ToolResult:
        """Вычислить статистику"""
        if not data:
            return ToolResult(
                success=False,
                error="Данные для статистики не предоставлены"
            )
        
        # Фильтруем числовые данные
        numeric_data = [x for x in data if isinstance(x, (int, float))]
        
        if not numeric_data:
            return ToolResult(
                success=False,
                error="Нет числовых данных для статистики"
            )
        
        stats = {
            "count": len(numeric_data),
            "sum": sum(numeric_data),
            "mean": statistics.mean(numeric_data),
            "median": statistics.median(numeric_data),
            "min": min(numeric_data),
            "max": max(numeric_data),
        }
        
        # Дополнительная статистика если достаточно данных
        if len(numeric_data) > 1:
            stats["stdev"] = statistics.stdev(numeric_data)
            stats["variance"] = statistics.variance(numeric_data)
        
        if len(numeric_data) >= 2:
            try:
                stats["mode"] = statistics.mode(numeric_data)
            except statistics.StatisticsError:
                stats["mode"] = None  # Нет единственной моды
        
        return ToolResult(
            success=True,
            data={
                "operation": "statistics",
                "statistics": stats,
                "data_sample": numeric_data[:10]  # Первые 10 элементов
            }
        )
    
    def _basic_math(self, a: float, b: float, op: str) -> ToolResult:
        """Базовые математические операции"""
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else None,
            "power": lambda x, y: x ** y,
            "modulo": lambda x, y: x % y if y != 0 else None
        }
        
        if op not in operations:
            return ToolResult(
                success=False,
                error=f"Неизвестная операция: {op}. Доступные: {list(operations.keys())}"
            )
        
        try:
            result = operations[op](a, b)
            
            if result is None:
                return ToolResult(
                    success=False,
                    error="Деление на ноль"
                )
            
            return ToolResult(
                success=True,
                data={
                    "operation": "basic_math",
                    "operands": [a, b],
                    "operator": op,
                    "result": result
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка операции: {str(e)}"
            )
    
    def _convert_units(self, value: float, from_unit: str, to_unit: str) -> ToolResult:
        """Простые конвертации единиц"""
        # Температура
        temp_conversions = {
            ("celsius", "fahrenheit"): lambda c: (c * 9/5) + 32,
            ("fahrenheit", "celsius"): lambda f: (f - 32) * 5/9,
            ("celsius", "kelvin"): lambda c: c + 273.15,
            ("kelvin", "celsius"): lambda k: k - 273.15,
        }
        
        # Длина
        length_conversions = {
            ("meter", "kilometer"): lambda m: m / 1000,
            ("kilometer", "meter"): lambda km: km * 1000,
            ("meter", "centimeter"): lambda m: m * 100,
            ("centimeter", "meter"): lambda cm: cm / 100,
        }
        
        # Вес
        weight_conversions = {
            ("kilogram", "gram"): lambda kg: kg * 1000,
            ("gram", "kilogram"): lambda g: g / 1000,
            ("kilogram", "pound"): lambda kg: kg * 2.20462,
            ("pound", "kilogram"): lambda lb: lb / 2.20462,
        }
        
        all_conversions = {**temp_conversions, **length_conversions, **weight_conversions}
        
        conversion_key = (from_unit.lower(), to_unit.lower())
        
        if conversion_key not in all_conversions:
            return ToolResult(
                success=False,
                error=f"Конвертация {from_unit} → {to_unit} не поддерживается"
            )
        
        try:
            result = all_conversions[conversion_key](value)
            
            return ToolResult(
                success=True,
                data={
                    "operation": "convert_units",
                    "value": value,
                    "from_unit": from_unit,
                    "to_unit": to_unit,
                    "result": result
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка конвертации: {str(e)}"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["calculate", "statistics", "basic_math", "convert_units"],
                    "description": "Математическая операция"
                },
                "expression": {
                    "type": "string",
                    "description": "Математическое выражение (для calculate)"
                },
                "data": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Числовые данные (для statistics)"
                },
                "a": {
                    "type": "number",
                    "description": "Первое число (для basic_math)"
                },
                "b": {
                    "type": "number", 
                    "description": "Второе число (для basic_math)"
                },
                "op": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide", "power", "modulo"],
                    "description": "Математическая операция (для basic_math)"
                },
                "value": {
                    "type": "number",
                    "description": "Значение для конвертации"
                },
                "from_unit": {
                    "type": "string",
                    "description": "Исходная единица измерения"
                },
                "to_unit": {
                    "type": "string",
                    "description": "Целевая единица измерения"
                }
            },
            "required": ["operation"]
        } 