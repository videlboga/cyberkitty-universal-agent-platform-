"""
Comprehensive тесты для SmartFunctionTool - Умного инструмента работы с функциями
"""

import pytest
import asyncio
from unittest.mock import AsyncMock

from kittycore.tools.smart_function_tool import SmartFunctionTool, create_smart_function_tool, create_math_function_tool


class TestSmartFunctionTool:
    """Comprehensive тесты SmartFunctionTool"""

    @pytest.fixture
    def tool(self):
        """Fixture для создания инструмента"""
        return create_smart_function_tool()

    @pytest.mark.asyncio
    async def test_tool_initialization(self, tool):
        """Тест инициализации инструмента"""
        assert tool.name == "smart_function_tool"
        assert "Создание, выполнение и анализ Python функций" in tool.description
        assert len(tool.functions) == 0
        assert len(tool.metadata) == 0
        assert '__builtins__' in tool.global_namespace

    @pytest.mark.asyncio  
    async def test_available_actions(self, tool):
        """Тест доступных действий"""
        actions = tool.get_available_actions()
        expected_actions = [
            "create_function", "execute_function", "analyze_function",
            "list_functions", "get_function_info", "delete_function", 
            "import_module", "validate_code"
        ]
        
        assert len(actions) == 8
        for action in expected_actions:
            assert action in actions

    @pytest.mark.asyncio
    async def test_validate_code_success(self, tool):
        """Тест успешной валидации кода"""
        valid_code = """
def add_numbers(a, b):
    return a + b
"""
        
        result = await tool.validate_code(valid_code)
        assert result.success is True
        assert result.data["valid"] is True
        assert "warnings" in result.data
        assert result.data["ast_nodes"] > 0

    @pytest.mark.asyncio
    async def test_validate_code_syntax_error(self, tool):
        """Тест валидации кода с синтаксической ошибкой"""
        invalid_code = """
def broken_function(
    return "missing closing paren"
"""
        
        result = await tool.validate_code(invalid_code)
        assert result.success is False
        assert result.data["valid"] is False
        assert "line" in result.data

    @pytest.mark.asyncio
    async def test_validate_code_dangerous_operations(self, tool):
        """Тест обнаружения опасных операций"""
        dangerous_code = """
def dangerous_function():
    eval("print('dangerous')")
    return "done"
"""
        
        result = await tool.validate_code(dangerous_code)
        assert result.success is True  # Синтаксически корректно
        assert len(result.data["warnings"]) > 0
        assert any("eval" in warning for warning in result.data["warnings"])

    @pytest.mark.asyncio
    async def test_create_simple_function(self, tool):
        """Тест создания простой функции"""
        function_code = '''
def multiply(x, y):
    """Умножение двух чисел"""
    return x * y
'''
        
        result = await tool.create_function(function_code)
        assert result.success is True
        assert result.data["function_name"] == "multiply"
        assert result.data["registered"] is True
        
        # Проверяем что функция добавлена
        assert "multiply" in tool.functions
        assert "multiply" in tool.metadata
        
        # Проверяем метаданные
        metadata = tool.metadata["multiply"]
        assert metadata.name == "multiply"
        assert len(metadata.parameters) == 2
        assert metadata.docstring == "Умножение двух чисел"

    @pytest.mark.asyncio
    async def test_create_function_with_type_hints(self, tool):
        """Тест создания функции с type hints"""
        function_code = '''
def calculate_area(width: float, height: float = 1.0) -> float:
    """Вычисление площади прямоугольника"""
    return width * height
'''
        
        result = await tool.create_function(function_code)
        assert result.success is True
        
        metadata = tool.metadata["calculate_area"]
        assert metadata.return_type == "float"
        assert len(metadata.parameters) == 2
        
        # Проверяем параметры
        params = metadata.parameters
        assert params[0]["name"] == "width"
        assert params[0]["type"] == "float"
        assert params[0]["required"] is True
        
        assert params[1]["name"] == "height"
        assert params[1]["type"] == "float"
        assert params[1]["required"] is False
        assert params[1]["default"] == "1.0"

    @pytest.mark.asyncio
    async def test_execute_function_success(self, tool):
        """Тест успешного выполнения функции"""
        # Создаем функцию
        function_code = '''
def power(base, exponent):
    return base ** exponent
'''
        
        await tool.create_function(function_code)
        
        # Выполняем функцию
        result = await tool.execute_function("power", args=[2, 3])
        assert result.success is True
        assert result.data["result"] == 8
        assert result.data["function_name"] == "power"
        assert result.data["execution_time"] >= 0  # Может быть очень маленьким, но >= 0

    @pytest.mark.asyncio
    async def test_execute_function_with_kwargs(self, tool):
        """Тест выполнения функции с kwargs"""
        function_code = '''
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"
'''
        
        await tool.create_function(function_code)
        
        # Тест с kwargs
        result = await tool.execute_function("greet", kwargs={"name": "Alice", "greeting": "Hi"})
        assert result.success is True
        assert result.data["result"] == "Hi, Alice!"

    @pytest.mark.asyncio
    async def test_execute_function_error(self, tool):
        """Тест обработки ошибки выполнения функции"""
        function_code = '''
def divide(a, b):
    return a / b
'''
        
        await tool.create_function(function_code)
        
        # Деление на ноль
        result = await tool.execute_function("divide", args=[10, 0])
        assert result.success is False
        assert "division by zero" in result.error
        assert "traceback" in result.data

    @pytest.mark.asyncio
    async def test_execute_nonexistent_function(self, tool):
        """Тест выполнения несуществующей функции"""
        result = await tool.execute_function("nonexistent")
        assert result.success is False
        assert "не найдена" in result.error

    @pytest.mark.asyncio
    async def test_function_args_validation(self, tool):
        """Тест валидации аргументов функции"""
        function_code = '''
def add_three(a, b, c=0):
    return a + b + c
'''
        
        await tool.create_function(function_code)
        
        # Недостаточно аргументов
        result = await tool.execute_function("add_three", args=[1])
        assert result.success is False
        assert "Недостаточно аргументов" in result.error
        
        # Слишком много аргументов
        result = await tool.execute_function("add_three", args=[1, 2, 3, 4])
        assert result.success is False
        assert "Слишком много аргументов" in result.error

    @pytest.mark.asyncio
    async def test_list_functions(self, tool):
        """Тест получения списка функций"""
        # Создаем несколько функций
        functions = [
            "def func1(): return 1",
            "def func2(x): return x * 2",
            "def func3(a, b=5): return a + b"
        ]
        
        for func_code in functions:
            await tool.create_function(func_code)
        
        result = await tool.list_functions()
        assert result.success is True
        assert result.data["total_count"] == 3
        assert len(result.data["functions"]) == 3
        
        # Проверяем информацию о функциях
        func_names = [f["name"] for f in result.data["functions"]]
        assert "func1" in func_names
        assert "func2" in func_names
        assert "func3" in func_names

    @pytest.mark.asyncio
    async def test_get_function_info(self, tool):
        """Тест получения информации о функции"""
        function_code = '''
def fibonacci(n: int) -> int:
    """Вычисление числа Фибоначчи"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
        
        await tool.create_function(function_code)
        
        result = await tool.get_function_info("fibonacci")
        assert result.success is True
        assert result.data["is_registered"] is True
        assert result.data["source_available"] is True
        
        metadata = result.data["metadata"]
        assert metadata["name"] == "fibonacci"
        assert metadata["return_type"] == "int"
        assert metadata["docstring"] == "Вычисление числа Фибоначчи"

    @pytest.mark.asyncio
    async def test_analyze_function(self, tool):
        """Тест анализа функции"""
        function_code = '''
def complex_function(data):
    """Сложная функция для анализа"""
    result = []
    for item in data:
        if isinstance(item, int):
            result.append(item * 2)
        else:
            result.append(str(item))
    return result
'''
        
        await tool.create_function(function_code)
        
        result = await tool.analyze_function("complex_function")
        assert result.success is True
        
        analysis = result.data
        assert "basic_info" in analysis
        assert "lines_of_code" in analysis
        assert analysis["callable"] is True
        assert analysis["memory_size"] > 0

    @pytest.mark.asyncio
    async def test_delete_function(self, tool):
        """Тест удаления функции"""
        function_code = "def temp_function(): return 'temporary'"
        
        await tool.create_function(function_code)
        assert "temp_function" in tool.functions
        
        result = await tool.delete_function("temp_function")
        assert result.success is True
        assert result.data["deleted_function"] == "temp_function"
        assert "temp_function" not in tool.functions
        assert "temp_function" not in tool.metadata

    @pytest.mark.asyncio
    async def test_import_module(self, tool):
        """Тест импорта модуля"""
        result = await tool.import_module("datetime")
        assert result.success is True
        assert result.data["module"] == "datetime"
        assert "datetime" in tool.global_namespace

    @pytest.mark.asyncio
    async def test_import_nonexistent_module(self, tool):
        """Тест импорта несуществующего модуля"""
        result = await tool.import_module("nonexistent_module_12345")
        assert result.success is False
        assert "Ошибка импорта модуля" in result.error

    @pytest.mark.asyncio
    async def test_auto_import_math(self, tool):
        """Тест автоимпорта математических функций"""
        function_code = '''
def calculate_circle_area(radius):
    return math.pi * radius ** 2
'''
        
        result = await tool.create_function(function_code, auto_import=True)
        assert result.success is True
        assert "math" in tool.global_namespace
        
        # Проверяем что функция работает
        exec_result = await tool.execute_function("calculate_circle_area", args=[5])
        assert exec_result.success is True
        assert abs(exec_result.data["result"] - 78.54) < 0.01  # π * 5² ≈ 78.54

    @pytest.mark.asyncio
    async def test_execute_action_interface(self, tool):
        """Тест интерфейса execute_action"""
        # Тест неизвестного действия
        result = await tool.execute_action("unknown_action")
        assert result.success is False
        assert "Неизвестное действие" in result.error
        
        # Тест валидного действия
        result = await tool.execute_action("list_functions")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_factory_functions(self):
        """Тест фабричных функций"""
        # Обычный инструмент
        tool1 = create_smart_function_tool()
        assert isinstance(tool1, SmartFunctionTool)
        assert tool1.global_namespace.get('math') is None
        
        # Математический инструмент
        tool2 = create_math_function_tool()
        assert isinstance(tool2, SmartFunctionTool)
        assert tool2.global_namespace.get('math') is not None