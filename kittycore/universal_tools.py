#!/usr/bin/env python3

"""
Universal Tools for KittyCore
Inspired by CrewAI, AutoGen, and LangChain best practices
"""

import subprocess
import requests
import json
import os
import sys
from typing import Any, Dict, List, Optional, Union
import tempfile
import io

from .tools.unified_tool_result import ToolResult

try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class PythonExecutionTool:
    """Execute Python code safely in isolated environment"""
    
    def __init__(self, use_docker: bool = False):
        self.use_docker = use_docker
        self.name = "Python"
        self.description = "Execute Python code and return results"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute"
                    },
                    "libraries": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Required libraries (will be installed if missing)"
                    }
                },
                "required": ["code"]
            }
        }
    
    def execute(self, code: str, libraries: List[str] = None) -> ToolResult:
        """Execute Python code"""
        try:
            return self._execute_local(code, libraries or [])
        except Exception as e:
            return ToolResult(success=False, error=str(e))
    
    def _execute_local(self, code: str, libraries: List[str] = None) -> ToolResult:
        """Execute code locally with safety measures"""
        # Install required libraries
        if libraries:
            for lib in libraries:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", lib], 
                                        capture_output=True, text=True)
                except subprocess.CalledProcessError:
                    pass  # Continue if installation fails
        
        # Capture output
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # Create safe execution environment
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'abs': abs,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'zip': zip,
                },
                'json': json,
                'requests': requests,
            }
            
            # Add pandas and numpy if available
            if PANDAS_AVAILABLE:
                safe_globals['pandas'] = pd
                safe_globals['numpy'] = np
                safe_globals['matplotlib'] = plt
            
            # Execute code
            exec(code, safe_globals)
            
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            if stderr_output:
                return ToolResult(success=False, error=stderr_output)
            
            return ToolResult(
                success=True, 
                data=stdout_output if stdout_output else "Code executed successfully",
                metadata={"execution_type": "local"}
            )
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


# PandasTool удален - используйте kittycore.tools.data_tools.PandasTool


class WebScrapingTool:
    """Tool for web scraping and content extraction"""
    
    def __init__(self):
        self.name = "WebScraper"
        self.description = "Scrape web content and extract information"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to scrape"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["text", "html", "json"],
                        "description": "Extraction method"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for specific elements"
                    }
                },
                "required": ["url"]
            }
        }
    
    def execute(self, url: str, method: str = "text", selector: str = None) -> ToolResult:
        """Scrape web content"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            if method == "text":
                content = response.text
            elif method == "html":
                content = response.text
            elif method == "json":
                content = response.json()
            else:
                content = response.text
            
            return ToolResult(
                success=True,
                data=content,
                metadata={
                    "url": url,
                    "status_code": response.status_code,
                    "content_length": len(str(content))
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, error=f"Web scraping failed: {str(e)}")


# ApiRequestTool удален - используйте kittycore.tools.web_tools.ApiRequestTool


class MathCalculationTool:
    """Tool for mathematical calculations"""
    
    def __init__(self):
        self.name = "Calculator"
        self.description = "Perform mathematical calculations and operations"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["evaluate", "statistics", "linear_algebra"],
                        "description": "Type of mathematical operation"
                    },
                    "data": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Numerical data for statistics"
                    }
                },
                "required": ["operation"]
            }
        }
    
    def execute(self, operation: str, expression: str = None, data: List[float] = None) -> ToolResult:
        """Execute mathematical operation"""
        try:
            if operation == "evaluate" and expression:
                # Safe evaluation of mathematical expressions
                import math
                allowed_names = {
                    "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
                    "pow": pow, "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
                    "tan": math.tan, "log": math.log, "exp": math.exp, "pi": math.pi,
                    "e": math.e
                }
                
                result = eval(expression, {"__builtins__": {}}, allowed_names)
                return ToolResult(success=True, data=result)
                
            elif operation == "statistics" and data:
                if not PANDAS_AVAILABLE:
                    # Basic statistics without numpy
                    stats = {
                        "mean": sum(data) / len(data),
                        "min": min(data),
                        "max": max(data),
                        "sum": sum(data),
                        "count": len(data)
                    }
                else:
                    stats = {
                        "mean": np.mean(data),
                        "median": np.median(data),
                        "std": np.std(data),
                        "min": np.min(data),
                        "max": np.max(data),
                        "sum": np.sum(data),
                        "count": len(data)
                    }
                return ToolResult(success=True, data=stats)
                
            elif operation == "linear_algebra" and data:
                if not PANDAS_AVAILABLE:
                    return ToolResult(success=False, error="NumPy required for linear algebra operations")
                
                # Convert to numpy array and provide basic operations
                arr = np.array(data)
                result = {
                    "shape": arr.shape,
                    "norm": np.linalg.norm(arr),
                    "transpose": arr.T.tolist() if arr.ndim > 1 else arr.tolist()
                }
                return ToolResult(success=True, data=result)
                
            else:
                return ToolResult(success=False, error="Invalid operation or missing parameters")
                
        except Exception as e:
            return ToolResult(success=False, error=f"Math calculation failed: {str(e)}")


# Collection of all universal tools
# ВНИМАНИЕ: PandasTool и ApiRequestTool перенесены в специализированные модули
# Используйте kittycore.tools.data_tools.PandasTool и kittycore.tools.web_tools.ApiRequestTool
UNIVERSAL_TOOLS = {
    "Python": PythonExecutionTool(),
    "WebScraper": WebScrapingTool(),
    "Calculator": MathCalculationTool(),
    "Telegram": None,  # Will be initialized on demand
    # Aliases for common names
    "Matplotlib": PythonExecutionTool(),  # Matplotlib можно использовать через Python
    "NumPy": PythonExecutionTool(),  # NumPy доступен через Python
    "Seaborn": PythonExecutionTool(),  # Seaborn доступен через Python
    "Plotly": PythonExecutionTool(),  # Plotly доступен через Python
    # Jupyter and notebook environments
    "Jupyter Notebook": PythonExecutionTool(),  # Jupyter можно эмулировать через Python
    "Jupyter Notebook (optional)": PythonExecutionTool(),
    "Jupyter": PythonExecutionTool(),
    "notebook": PythonExecutionTool(),
    # Statistical tools
    "SciPy": PythonExecutionTool(),  # SciPy доступен через Python
    "StatsModels": PythonExecutionTool(),  # StatsModels через Python
    "statistics": MathCalculationTool(),
    # Document formats
    "Markdown": PythonExecutionTool(),  # Markdown можно генерировать через Python
    "PowerPoint": PythonExecutionTool(),  # PowerPoint можно создавать через Python
    "PowerPoint (optional)": PythonExecutionTool(),
    # Составные инструменты (заглавные)
    "Python (Pandas, NumPy, Matplotlib)": PythonExecutionTool(),
    "Python (requests, BeautifulSoup)": WebScrapingTool(),
    "Python (Matplotlib, Seaborn)": PythonExecutionTool(),
    "Python (Pandas, NumPy)": PandasTool(),
    "Python (Pandas)": PandasTool(),  # Только Pandas
    "Python (Pandas, Matplotlib, Seaborn)": PythonExecutionTool(),  # Полный data science стек
    # Составные инструменты (строчные - для совместимости)
    "Python (pandas)": PandasTool(),  # строчная версия
    "Python (numpy)": PythonExecutionTool(),
    "Python (matplotlib)": PythonExecutionTool(),
    "Python (seaborn)": PythonExecutionTool(),
    "Python (pandas, numpy)": PandasTool(),
    "Python (pandas, numpy, matplotlib)": PythonExecutionTool(),
    "Python (matplotlib, seaborn)": PythonExecutionTool(),  # строчная версия
    "Python (pandas, matplotlib, seaborn)": PythonExecutionTool(),
    # Составные инструменты с косыми чертами (/)
    "Python (Pandas/Matplotlib)": PythonExecutionTool(),
    "Python (Matplotlib/Seaborn)": PythonExecutionTool(),
    "Python (Pandas/Matplotlib/Seaborn)": PythonExecutionTool(),
    "Python (Pandas, Matplotlib/Seaborn)": PythonExecutionTool(),
    "Python (pandas/matplotlib)": PythonExecutionTool(),
    "Python (matplotlib/seaborn)": PythonExecutionTool(),
    "Python (pandas/matplotlib/seaborn)": PythonExecutionTool(),
    "Python (pandas, matplotlib/seaborn)": PythonExecutionTool(),
    # Редакторы и IDE
    "Text Editor": PythonExecutionTool(),
    "IDE": PythonExecutionTool(),
    "Text Editor/IDE": PythonExecutionTool(),
    "Text Editor (VS Code, PyCharm)": PythonExecutionTool(),
    "VS Code": PythonExecutionTool(),
    "PyCharm": PythonExecutionTool(),
    "editor": PythonExecutionTool(),
    # Таблицы и офисные приложения
    "Google Sheets": PandasTool(),
    "Excel/Google Sheets": PandasTool(),
    "Sheets": PandasTool(),
    # Другие инструменты
    "SQL": PythonExecutionTool(),  # SQL можно выполнять через Python
    "R": PythonExecutionTool(),  # R можно эмулировать через Python
    "Tableau": PythonExecutionTool(),  # Visualizations через Python
}


def get_tool_by_name(name: str):
    """Get tool instance by name"""
    tool = UNIVERSAL_TOOLS.get(name)
    
    # Initialize TelegramTool on demand
    if name == "Telegram" and tool is None:
        try:
            from .telegram_tools import TelegramTool
            tool = TelegramTool()
            UNIVERSAL_TOOLS["Telegram"] = tool
        except ImportError:
            # Telegram dependencies not available
            return None
    
    return tool


def get_all_tools():
    """Get all available universal tools"""
    return UNIVERSAL_TOOLS


def get_tool_schemas():
    """Get schemas for all tools"""
    return {name: tool.get_schema() for name, tool in UNIVERSAL_TOOLS.items()}


if __name__ == "__main__":
    # Test the tools
    print("🔧 Testing Universal Tools...")
    
    # Test Python execution
    python_tool = PythonExecutionTool()
    result = python_tool.execute("print('Hello from Python tool!')")
    print(f"Python tool: {result.success} - {result.result}")
    
    # Test math calculation
    math_tool = MathCalculationTool()
    result = math_tool.execute("evaluate", expression="2 + 2 * 3")
    print(f"Math tool: {result.success} - {result.result}")
    
    # Test API request
    api_tool = ApiRequestTool()
    result = api_tool.execute("https://httpbin.org/get", method="GET")
    print(f"API tool: {result.success} - Status: {result.metadata.get('status_code') if result.success else 'Failed'}")
    
    print("✅ Universal tools test completed!") 