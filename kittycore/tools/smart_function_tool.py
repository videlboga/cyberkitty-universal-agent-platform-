"""
🧠 SmartFunctionTool - Революционный инструмент для работы с Python функциями

Автоматическое создание, выполнение и анализ Python функций с динамическим парсингом.
"""

import ast
import inspect
import time
import sys
import traceback
from typing import Optional, Dict, Any, List, Union, Callable
from dataclasses import dataclass
from loguru import logger

from kittycore.tools.base_tool import Tool, ToolResult


@dataclass
class FunctionMetadata:
    """Метаданные Python функции"""
    name: str
    signature: str
    parameters: List[Dict[str, Any]]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    source_code: Optional[str] = None
    complexity: int = 0
    is_async: bool = False


@dataclass
class ExecutionResult:
    """Результат выполнения функции"""
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    output: Optional[str] = None
    function_name: str = ""


class SmartFunctionTool(Tool):
    """Умный инструмент для работы с Python функциями"""
    
    def __init__(self):
        super().__init__(
            name="smart_function_tool", 
            description="Создание, выполнение и анализ Python функций с автопарсингом"
        )
        
        # Регистр функций
        self.functions: Dict[str, Callable] = {}
        self.metadata: Dict[str, FunctionMetadata] = {}
        
        # Глобальный namespace для выполнения
        self.global_namespace = {
            '__builtins__': __builtins__,
            'math': None,  # Будет импортирован при необходимости
            'datetime': None,
            'json': None,
            'random': None,
            'os': None,
            're': None
        }
        
        logger.info("🧠 SmartFunctionTool инициализирован")
    
    def get_available_actions(self) -> List[str]:
        """Получение списка доступных действий"""
        return [
            "create_function",
            "execute_function", 
            "analyze_function",
            "list_functions",
            "get_function_info",
            "delete_function",
            "import_module",
            "validate_code"
        ]
    
    async def create_function(self, 
                            function_code: str,
                            function_name: Optional[str] = None,
                            auto_import: bool = True) -> ToolResult:
        """
        Создание Python функции из кода
        
        Args:
            function_code: Код функции
            function_name: Имя функции (если None - автоопределение)
            auto_import: Автоматический импорт модулей
        """
        try:
            # Валидация синтаксиса
            validation_result = await self.validate_code(function_code)
            if not validation_result.success:
                return validation_result
            
            # Автоматический импорт модулей
            if auto_import:
                await self._auto_import_modules(function_code)
            
            # Парсинг AST для получения информации о функции
            tree = ast.parse(function_code)
            
            # Поиск определения функции
            function_def = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_def = node
                    break
            
            if not function_def:
                return ToolResult(
                    success=False,
                    error="Код не содержит определения функции"
                )
            
            # Определяем имя функции
            actual_name = function_name or function_def.name
            
            # Выполняем код в глобальном namespace
            exec(function_code, self.global_namespace)
            
            # Получаем созданную функцию
            created_function = self.global_namespace.get(function_def.name)
            if not created_function:
                return ToolResult(
                    success=False,
                    error=f"Функция {function_def.name} не была создана"
                )
            
            # Анализируем функцию
            metadata = self._analyze_function_ast(function_def, function_code)
            
            # Регистрируем функцию
            self.functions[actual_name] = created_function
            self.metadata[actual_name] = metadata
            
            logger.info(f"🎯 Функция {actual_name} создана и зарегистрирована")
            
            return ToolResult(
                success=True,
                data={
                    "function_name": actual_name,
                    "metadata": metadata.__dict__,
                    "registered": True
                }
            )
            
        except SyntaxError as e:
            return ToolResult(
                success=False,
                error=f"Синтаксическая ошибка: {e}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка создания функции: {e}"
            )
    
    def _analyze_function_ast(self, func_node: ast.FunctionDef, source_code: str) -> FunctionMetadata:
        """Анализ функции через AST"""
        
        # Получаем параметры
        parameters = []
        for arg in func_node.args.args:
            param_info = {
                "name": arg.arg,
                "type": None,
                "default": None,
                "required": True
            }
            
            # Аннотация типа
            if arg.annotation:
                param_info["type"] = ast.unparse(arg.annotation)
            
            parameters.append(param_info)
        
        # Обрабатываем значения по умолчанию
        defaults = func_node.args.defaults
        if defaults:
            # Значения по умолчанию идут с конца
            offset = len(parameters) - len(defaults)
            for i, default in enumerate(defaults):
                parameters[offset + i]["default"] = ast.unparse(default)
                parameters[offset + i]["required"] = False
        
        # Получаем тип возвращаемого значения
        return_type = None
        if func_node.returns:
            return_type = ast.unparse(func_node.returns)
        
        # Получаем docstring
        docstring = None
        if (func_node.body and 
            isinstance(func_node.body[0], ast.Expr) and 
            isinstance(func_node.body[0].value, ast.Constant) and 
            isinstance(func_node.body[0].value.value, str)):
            docstring = func_node.body[0].value.value
        
        # Вычисляем сложность (количество узлов)
        complexity = len(list(ast.walk(func_node)))
        
        # Проверяем асинхронность
        is_async = isinstance(func_node, ast.AsyncFunctionDef)
        
        # Создаем сигнатуру
        signature = f"{func_node.name}({', '.join([p['name'] for p in parameters])})"
        if return_type:
            signature += f" -> {return_type}"
        
        return FunctionMetadata(
            name=func_node.name,
            signature=signature,
            parameters=parameters,
            return_type=return_type,
            docstring=docstring,
            source_code=source_code,
            complexity=complexity,
            is_async=is_async
        )
    
    async def validate_code(self, code: str) -> ToolResult:
        """Валидация Python кода"""
        try:
            # Проверка синтаксиса
            ast.parse(code)
            
            # Проверка на опасные операции
            dangerous_patterns = [
                '__import__', 'eval', 'exec', 'open', 'file',
                'subprocess', 'os.system', 'os.popen'
            ]
            
            warnings = []
            for pattern in dangerous_patterns:
                if pattern in code:
                    warnings.append(f"Обнаружена потенциально опасная операция: {pattern}")
            
            return ToolResult(
                success=True,
                data={
                    "valid": True,
                    "warnings": warnings,
                    "ast_nodes": len(list(ast.walk(ast.parse(code))))
                }
            )
            
        except SyntaxError as e:
            return ToolResult(
                success=False,
                error=f"Синтаксическая ошибка: {e}",
                data={
                    "valid": False,
                    "line": e.lineno,
                    "column": e.offset
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка валидации: {e}"
            )
    
    async def execute_function(self,
                             function_name: str,
                             args: Optional[List[Any]] = None,
                             kwargs: Optional[Dict[str, Any]] = None,
                             timeout: float = 30.0) -> ToolResult:
        """
        Выполнение зарегистрированной функции
        
        Args:
            function_name: Имя функции
            args: Позиционные аргументы
            kwargs: Именованные аргументы
            timeout: Таймаут выполнения в секундах
        """
        try:
            if function_name not in self.functions:
                return ToolResult(
                    success=False,
                    error=f"Функция {function_name} не найдена"
                )
            
            func = self.functions[function_name]
            args = args or []
            kwargs = kwargs or {}
            
            # Валидация аргументов
            validation_result = self._validate_function_args(function_name, args, kwargs)
            if not validation_result.success:
                return validation_result
            
            # Выполнение с измерением времени
            start_time = time.time()
            
            try:
                # Проверяем асинхронность
                if self.metadata[function_name].is_async:
                    import asyncio
                    result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                else:
                    result = func(*args, **kwargs)
                
                execution_time = time.time() - start_time
                
                return ToolResult(
                    success=True,
                    data={
                        "function_name": function_name,
                        "result": result,
                        "execution_time": max(round(execution_time, 6), 0.000001),  # Минимум 1 микросекунда
                        "args_count": len(args),
                        "kwargs_count": len(kwargs)
                    }
                )
                
            except Exception as func_error:
                execution_time = time.time() - start_time
                
                return ToolResult(
                    success=False,
                    error=f"Ошибка выполнения функции: {func_error}",
                    data={
                        "function_name": function_name,
                        "execution_time": round(execution_time, 4),
                        "traceback": traceback.format_exc()
                    }
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка при попытке выполнения: {e}"
            )
    
    def _validate_function_args(self, function_name: str, args: List[Any], kwargs: Dict[str, Any]) -> ToolResult:
        """Валидация аргументов функции"""
        try:
            metadata = self.metadata[function_name]
            
            # Проверяем количество позиционных аргументов
            required_params = [p for p in metadata.parameters if p["required"]]
            optional_params = [p for p in metadata.parameters if not p["required"]]
            
            total_provided = len(args) + len(kwargs)
            min_required = len(required_params)
            max_allowed = len(metadata.parameters)
            
            if total_provided < min_required:
                return ToolResult(
                    success=False,
                    error=f"Недостаточно аргументов: нужно минимум {min_required}, передано {total_provided}"
                )
            
            if total_provided > max_allowed:
                return ToolResult(
                    success=False,
                    error=f"Слишком много аргументов: максимум {max_allowed}, передано {total_provided}"
                )
            
            # Проверяем конфликты имен
            param_names = [p["name"] for p in metadata.parameters]
            for i, arg in enumerate(args):
                if i < len(param_names) and param_names[i] in kwargs:
                    return ToolResult(
                        success=False,
                        error=f"Конфликт аргументов: {param_names[i]} передан и позиционно и по имени"
                    )
            
            return ToolResult(success=True, data={"validation": "passed"})
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка валидации аргументов: {e}"
            )
    
    async def _auto_import_modules(self, code: str):
        """Автоматический импорт модулей на основе анализа кода"""
        try:
            # Стандартные модули для автоимпорта
            common_modules = {
                'math': ['math', 'sqrt', 'sin', 'cos', 'pi', 'e'],
                'datetime': ['datetime', 'date', 'time', 'timedelta'],
                'json': ['json', 'loads', 'dumps'],
                'random': ['random', 'randint', 'choice', 'shuffle'],
                'os': ['os', 'path', 'listdir', 'getcwd'],
                're': ['re', 'match', 'search', 'findall', 'sub']
            }
            
            for module_name, keywords in common_modules.items():
                if any(keyword in code for keyword in keywords):
                    if self.global_namespace.get(module_name) is None:
                        try:
                            imported_module = __import__(module_name)
                            self.global_namespace[module_name] = imported_module
                            logger.info(f"📦 Автоимпорт модуля: {module_name}")
                        except ImportError:
                            logger.warning(f"⚠️ Не удалось импортировать модуль: {module_name}")
                            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка автоимпорта: {e}")
    
    async def import_module(self, module_name: str, alias: Optional[str] = None) -> ToolResult:
        """Импорт модуля в глобальный namespace"""
        try:
            imported_module = __import__(module_name)
            
            # Для составных имен модулей (например, os.path)
            if '.' in module_name:
                for part in module_name.split('.')[1:]:
                    imported_module = getattr(imported_module, part)
            
            name_in_namespace = alias or module_name.split('.')[-1]
            self.global_namespace[name_in_namespace] = imported_module
            
            logger.info(f"📦 Модуль {module_name} импортирован как {name_in_namespace}")
            
            return ToolResult(
                success=True,
                data={
                    "module": module_name,
                    "alias": name_in_namespace,
                    "type": str(type(imported_module))
                }
            )
            
        except ImportError as e:
            return ToolResult(
                success=False,
                error=f"Ошибка импорта модуля {module_name}: {e}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка при импорте: {e}"
            )
    
    async def list_functions(self) -> ToolResult:
        """Получение списка всех зарегистрированных функций"""
        try:
            functions_info = []
            
            for name, metadata in self.metadata.items():
                functions_info.append({
                    "name": name,
                    "signature": metadata.signature,
                    "parameters_count": len(metadata.parameters),
                    "complexity": metadata.complexity,
                    "is_async": metadata.is_async,
                    "has_docstring": bool(metadata.docstring)
                })
            
            return ToolResult(
                success=True,
                data={
                    "functions": functions_info,
                    "total_count": len(functions_info),
                    "namespace_size": len(self.global_namespace)
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения списка функций: {e}"
            )
    
    async def get_function_info(self, function_name: str) -> ToolResult:
        """Получение подробной информации о функции"""
        try:
            if function_name not in self.metadata:
                return ToolResult(
                    success=False,
                    error=f"Функция {function_name} не найдена"
                )
            
            metadata = self.metadata[function_name]
            
            return ToolResult(
                success=True,
                data={
                    "metadata": metadata.__dict__,
                    "is_registered": function_name in self.functions,
                    "source_available": bool(metadata.source_code)
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения информации о функции: {e}"
            )
    
    async def analyze_function(self, function_name: str) -> ToolResult:
        """Анализ функции с дополнительными метриками"""
        try:
            if function_name not in self.functions:
                return ToolResult(
                    success=False,
                    error=f"Функция {function_name} не найдена"
                )
            
            func = self.functions[function_name]
            metadata = self.metadata[function_name]
            
            # Дополнительный анализ через inspect
            try:
                signature = inspect.signature(func)
                source = inspect.getsource(func)
                lines_count = len(source.split('\n'))
            except Exception:
                signature = None
                source = metadata.source_code
                lines_count = len(source.split('\n')) if source else 0
            
            analysis = {
                "basic_info": metadata.__dict__,
                "inspect_signature": str(signature) if signature else None,
                "lines_of_code": lines_count,
                "callable": callable(func),
                "memory_size": sys.getsizeof(func),
                "is_builtin": inspect.isbuiltin(func),
                "is_method": inspect.ismethod(func)
            }
            
            return ToolResult(
                success=True,
                data=analysis
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка анализа функции: {e}"
            )
    
    async def delete_function(self, function_name: str) -> ToolResult:
        """Удаление функции из регистра"""
        try:
            if function_name not in self.functions:
                return ToolResult(
                    success=False,
                    error=f"Функция {function_name} не найдена"
                )
            
            # Удаляем из регистра
            del self.functions[function_name]
            del self.metadata[function_name]
            
            # Удаляем из глобального namespace если есть
            if function_name in self.global_namespace:
                del self.global_namespace[function_name]
            
            logger.info(f"🗑️ Функция {function_name} удалена")
            
            return ToolResult(
                success=True,
                data={
                    "deleted_function": function_name,
                    "remaining_functions": len(self.functions)
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка удаления функции: {e}"
            )
    
    # Обязательные абстрактные методы Tool
    async def execute(self, **kwargs) -> ToolResult:
        """Основной метод выполнения - алиас для execute_action"""
        action = kwargs.pop('action', 'list_functions')  # По умолчанию показать функции
        return await self.execute_action(action, **kwargs)
    
    def get_schema(self) -> Dict[str, Any]:
        """Получение схемы инструмента для LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "actions": {
                "create_function": {
                    "description": "Создание Python функции из кода",
                    "parameters": {
                        "function_code": {"type": "string", "required": True, "description": "Код функции"},
                        "function_name": {"type": "string", "required": False, "description": "Имя функции (автоопределение)"},
                        "auto_import": {"type": "boolean", "required": False, "default": True, "description": "Автоимпорт модулей"}
                    }
                },
                "execute_function": {
                    "description": "Выполнение зарегистрированной функции",
                    "parameters": {
                        "function_name": {"type": "string", "required": True, "description": "Имя функции"},
                        "args": {"type": "array", "required": False, "description": "Позиционные аргументы"},
                        "kwargs": {"type": "object", "required": False, "description": "Именованные аргументы"},
                        "timeout": {"type": "number", "required": False, "default": 30.0, "description": "Таймаут в секундах"}
                    }
                },
                "validate_code": {
                    "description": "Валидация Python кода",
                    "parameters": {
                        "code": {"type": "string", "required": True, "description": "Код для валидации"}
                    }
                },
                "list_functions": {
                    "description": "Получение списка всех функций",
                    "parameters": {}
                },
                "get_function_info": {
                    "description": "Получение информации о функции",
                    "parameters": {
                        "function_name": {"type": "string", "required": True, "description": "Имя функции"}
                    }
                },
                "analyze_function": {
                    "description": "Анализ функции с метриками",
                    "parameters": {
                        "function_name": {"type": "string", "required": True, "description": "Имя функции"}
                    }
                },
                "delete_function": {
                    "description": "Удаление функции",
                    "parameters": {
                        "function_name": {"type": "string", "required": True, "description": "Имя функции"}
                    }
                },
                "import_module": {
                    "description": "Импорт модуля в namespace",
                    "parameters": {
                        "module_name": {"type": "string", "required": True, "description": "Имя модуля"},
                        "alias": {"type": "string", "required": False, "description": "Алиас модуля"}
                    }
                }
            },
            "examples": [
                {
                    "description": "Создание математической функции",
                    "action": "create_function",
                    "parameters": {
                        "function_code": "def factorial(n):\\n    if n <= 1:\\n        return 1\\n    return n * factorial(n-1)"
                    }
                },
                {
                    "description": "Выполнение функции",
                    "action": "execute_function",
                    "parameters": {
                        "function_name": "factorial",
                        "args": [5]
                    }
                }
            ]
        }
    
    # Основной метод Tool
    async def execute_action(self, action: str, **kwargs) -> ToolResult:
        """Выполнение действия инструмента"""
        
        action_map = {
            "create_function": self.create_function,
            "execute_function": self.execute_function,
            "analyze_function": self.analyze_function,
            "list_functions": self.list_functions,
            "get_function_info": self.get_function_info,
            "delete_function": self.delete_function,
            "import_module": self.import_module,
            "validate_code": self.validate_code
        }
        
        if action not in action_map:
            return ToolResult(
                success=False,
                error=f"Неизвестное действие: {action}. Доступные: {list(action_map.keys())}"
            )
        
        try:
            method = action_map[action]
            
            # Проверяем является ли метод асинхронным
            if inspect.iscoroutinefunction(method):
                return await method(**kwargs)
            else:
                return method(**kwargs)
                
        except TypeError as e:
            return ToolResult(
                success=False,
                error=f"Неверные параметры для действия {action}: {e}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка выполнения действия {action}: {e}"
            )


# Фабричные функции
def create_smart_function_tool() -> SmartFunctionTool:
    """Создание инструмента для работы с функциями"""
    return SmartFunctionTool()


def create_math_function_tool() -> SmartFunctionTool:
    """Создание инструмента с предзагруженными математическими функциями"""
    tool = SmartFunctionTool()
    
    # Предзагружаем math модуль
    import math
    tool.global_namespace['math'] = math
    
    return tool