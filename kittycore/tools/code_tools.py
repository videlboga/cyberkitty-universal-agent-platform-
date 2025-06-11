"""
💻 CodeTools - Инструменты для работы с кодом в KittyCore 3.0

Реальные инструменты для разработки:
- Безопасное выполнение Python кода
- Генерация кода по шаблонам
- Проверка синтаксиса
- Простые тесты
"""

import subprocess
import sys
import io
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base_tool import Tool, ToolResult


class PythonExecutionTool(Tool):
    """Безопасное выполнение Python кода"""
    
    def __init__(self):
        super().__init__(
            name="python_execution",
            description="Безопасное выполнение Python кода с ограничениями"
        )
        self.safe_builtins = {
            'print': print,
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
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
            'round': round,
            'type': type,
        }
    
    def execute(self, code: str, timeout: int = 10, capture_output: bool = True) -> ToolResult:
        """Выполнить Python код"""
        try:
            if capture_output:
                return self._execute_with_capture(code, timeout)
            else:
                return self._execute_direct(code, timeout)
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка выполнения: {str(e)}"
            )
    
    def _execute_with_capture(self, code: str, timeout: int) -> ToolResult:
        """Выполнить с захватом вывода"""
        # Захватываем stdout и stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # Создаем безопасное окружение
            safe_globals = {
                '__builtins__': self.safe_builtins,
                '__name__': '__main__'
            }
            
            # Выполняем код
            exec(code, safe_globals)
            
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            if stderr_output:
                return ToolResult(
                    success=False,
                    error=stderr_output,
                    data={"stdout": stdout_output}
                )
            
            return ToolResult(
                success=True,
                data={
                    "output": stdout_output,
                    "execution_method": "captured"
                }
            )
            
        except Exception as e:
            stderr_output = stderr_capture.getvalue()
            return ToolResult(
                success=False,
                error=str(e),
                data={"stderr": stderr_output}
            )
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def _execute_direct(self, code: str, timeout: int) -> ToolResult:
        """Прямое выполнение без захвата"""
        try:
            safe_globals = {
                '__builtins__': self.safe_builtins,
                '__name__': '__main__'
            }
            
            exec(code, safe_globals)
            
            return ToolResult(
                success=True,
                data={
                    "message": "Код выполнен успешно",
                    "execution_method": "direct"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python код для выполнения"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Таймаут выполнения в секундах",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 60
                },
                "capture_output": {
                    "type": "boolean",
                    "description": "Захватывать ли вывод",
                    "default": True
                }
            },
            "required": ["code"]
        }


class CodeGenerator(Tool):
    """Генерация кода по шаблонам"""
    
    def __init__(self):
        super().__init__(
            name="code_generator",
            description="Генерация кода по готовым шаблонам"
        )
        self.templates = {
            "python_script": self._python_script_template,
            "html_page": self._html_page_template,
            "json_config": self._json_config_template,
            "bash_script": self._bash_script_template,
            "python_function": self._python_function_template
        }
    
    def execute(self, template_type: str, filename: str = None, **kwargs) -> ToolResult:
        """Генерировать код по шаблону"""
        try:
            if template_type not in self.templates:
                return ToolResult(
                    success=False,
                    error=f"Неизвестный шаблон: {template_type}. Доступные: {list(self.templates.keys())}"
                )
            
            # Генерируем код
            generator = self.templates[template_type]
            code = generator(**kwargs)
            
            result_data = {
                "template_type": template_type,
                "code": code,
                "length": len(code)
            }
            
            # Сохраняем в файл если указано
            if filename:
                try:
                    Path(filename).parent.mkdir(parents=True, exist_ok=True)
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(code)
                    
                    # Делаем исполняемым если это скрипт
                    if template_type in ["python_script", "bash_script"]:
                        os.chmod(filename, 0o755)
                    
                    result_data["saved_to"] = filename
                    result_data["executable"] = template_type in ["python_script", "bash_script"]
                    
                except Exception as e:
                    return ToolResult(
                        success=False,
                        error=f"Ошибка сохранения файла: {str(e)}",
                        data=result_data
                    )
            
            return ToolResult(
                success=True,
                data=result_data
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка генерации: {str(e)}"
            )
    
    def _python_script_template(self, name: str = "script", description: str = "Python script", **kwargs) -> str:
        return f'''#!/usr/bin/env python3
"""
{name} - {description}

Генерировано KittyCore 3.0
"""

import sys
import os


def main():
    """Основная функция"""
    print("🚀 Запущен: {name}")
    print("📝 Описание: {description}")
    
    # TODO: Добавить логику здесь
    
    print("✅ Выполнение завершено!")


if __name__ == "__main__":
    main()
'''
    
    def _html_page_template(self, title: str = "Страница", content: str = "Содержимое", **kwargs) -> str:
        return f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid #eee;
            margin-bottom: 30px;
        }}
        .content {{
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px 0;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
    </div>
    
    <div class="content">
        {content}
    </div>
    
    <div class="footer">
        Генерировано KittyCore 3.0 🐱
    </div>
</body>
</html>'''

    def _json_config_template(self, name: str = "config", **kwargs) -> str:
        import json
        config = {
            "name": name,
            "version": "1.0.0",
            "description": "Конфигурация создана KittyCore 3.0",
            "created_by": "KittyCore",
            "settings": kwargs
        }
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    def _bash_script_template(self, name: str = "script", description: str = "Bash script", **kwargs) -> str:
        return f'''#!/bin/bash

# {name} - {description}
# Генерировано KittyCore 3.0

set -e  # Остановка при ошибке

echo "🚀 Запущен: {name}"
echo "📝 Описание: {description}"

# TODO: Добавить команды здесь

echo "✅ Выполнение завершено!"
'''

    def _python_function_template(self, name: str = "my_function", description: str = "Функция", **kwargs) -> str:
        return f'''def {name}():
    """
    {description}
    
    Returns:
        str: Результат выполнения функции
    """
    # TODO: Реализовать логику
    return "Функция {name} выполнена успешно"


# Пример использования
if __name__ == "__main__":
    result = {name}()
    print(result)
'''
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "template_type": {
                    "type": "string",
                    "enum": list(self.templates.keys()),
                    "description": "Тип шаблона для генерации"
                },
                "filename": {
                    "type": "string", 
                    "description": "Имя файла для сохранения (опционально)"
                },
                "name": {
                    "type": "string",
                    "description": "Название создаваемого элемента",
                    "default": "generated"
                },
                "description": {
                    "type": "string",
                    "description": "Описание создаваемого элемента",
                    "default": "Создано KittyCore 3.0"
                },
                "title": {
                    "type": "string",
                    "description": "Заголовок (для HTML)",
                    "default": "Страница"
                },
                "content": {
                    "type": "string",
                    "description": "Содержимое (для HTML)",
                    "default": "Содержимое страницы"
                }
            },
            "required": ["template_type"]
        }


class CodeValidator(Tool):
    """Проверка синтаксиса кода"""
    
    def __init__(self):
        super().__init__(
            name="code_validator",
            description="Проверка синтаксиса Python кода"
        )
    
    def execute(self, code: str, language: str = "python") -> ToolResult:
        """Проверить синтаксис кода"""
        try:
            if language.lower() == "python":
                return self._validate_python(code)
            else:
                return ToolResult(
                    success=False,
                    error=f"Поддерживается только Python, получен: {language}"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка валидации: {str(e)}"
            )
    
    def _validate_python(self, code: str) -> ToolResult:
        """Проверить Python синтаксис"""
        try:
            # Компилируем код для проверки синтаксиса
            compile(code, '<string>', 'exec')
            
            # Дополнительные проверки
            lines = code.split('\n')
            issues = []
            
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Проверка на потенциальные проблемы
                if 'eval(' in line_stripped:
                    issues.append(f"Строка {i}: Использование eval() небезопасно")
                
                if 'exec(' in line_stripped:
                    issues.append(f"Строка {i}: Использование exec() небезопасно")
                
                if 'import os' in line_stripped and 'system' in code:
                    issues.append(f"Строка {i}: Потенциально опасный вызов системы")
            
            return ToolResult(
                success=True,
                data={
                    "valid": True,
                    "language": "python",
                    "lines_count": len(lines),
                    "issues": issues,
                    "safe": len(issues) == 0
                }
            )
            
        except SyntaxError as e:
            return ToolResult(
                success=True,  # Валидация выполнена, но код невалиден
                data={
                    "valid": False,
                    "error_type": "SyntaxError",
                    "error_message": str(e),
                    "line_number": e.lineno,
                    "column": e.offset
                }
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Код для проверки"
                },
                "language": {
                    "type": "string",
                    "enum": ["python"],
                    "description": "Язык программирования",
                    "default": "python"
                }
            },
            "required": ["code"]
        } 