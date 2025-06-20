"""
Code Execution Tools для KittyCore 3.0
Безопасное выполнение Python и Shell кода в sandbox окружении

Возможности:
- Выполнение Python кода с проверками безопасности
- Выполнение Shell команд в ограниченном окружении
- Sandbox с таймаутами и ограничениями ресурсов
- Блокировка опасных операций
- Мониторинг выполнения
"""

import asyncio
import subprocess
import tempfile
import os
import sys
import io
import contextlib
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import logging
from loguru import logger

from .base_tool import Tool, ToolResult


class CodeExecutionTool(Tool):
    """
    Безопасное выполнение кода в sandbox окружении
    """
    
    def __init__(self):
        super().__init__(
            name="code_execution",
            description="Безопасное выполнение Python и Shell кода"
        )
        
        # Настройки безопасности
        self.python_timeout = 30
        self.shell_timeout = 15
        self.max_output_size = 10000
        self.allowed_libraries = {
            "math", "json", "re", "datetime", "time", "random", "string",
            "collections", "itertools", "functools", "operator", "decimal",
            "fractions", "statistics", "urllib.parse", "base64", "hashlib",
            "hmac", "uuid", "pathlib", "textwrap", "unicodedata"
        }
        
        # Опасные паттерны для блокировки
        self.dangerous_python_patterns = {
            'import os', 'import sys', 'import subprocess', 'exec(', 'eval(',
            '__import__', 'open(', 'file(', 'input(', 'raw_input(',
            'compile(', 'reload(', 'delattr(', 'setattr(', 'getattr(',
            'hasattr(', 'globals(', 'locals(', 'vars(', 'dir(',
            'exit(', 'quit(', '__builtins__'
        }
        
        self.dangerous_shell_patterns = {
            'rm -rf', 'sudo', 'su ', 'passwd', 'userdel', 'useradd',
            'usermod', 'chmod 777', 'chown', 'mkfs', 'fdisk',
            'mount', 'umount', 'iptables', 'systemctl', 'service',
            'kill -9', 'killall', 'pkill', 'shutdown', 'reboot',
            'halt', 'dd if=', 'wget', 'curl', 'nc ', 'netcat',
            'ssh', 'scp', 'rsync'
        }

    def get_schema(self):
        """Схема для выполнения кода"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string", 
                    "enum": [
                        "execute_python", "execute_shell", "validate_python",
                        "validate_shell", "list_libraries", "get_execution_limits"
                    ],
                    "description": "Тип выполнения кода"
                },
                "code": {
                    "type": "string",
                    "description": "Код для выполнения"
                },
                "language": {
                    "type": "string",
                    "enum": ["python", "shell", "bash"],
                    "description": "Язык выполнения"
                },
                "libraries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Список библиотек для импорта"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Таймаут выполнения в секундах"
                },
                "working_dir": {
                    "type": "string",
                    "description": "Рабочая директория"
                },
                "env_vars": {
                    "type": "object",
                    "description": "Переменные окружения"
                }
            },
            "required": ["action"]
        }

    def execute(self, action: str, **kwargs) -> ToolResult:
        """Выполнить операцию с кодом"""
        try:
            if action == "execute_python":
                # Проверяем есть ли уже запущенный event loop
                try:
                    loop = asyncio.get_running_loop()
                    # Если да - создаём задачу
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._execute_python(**kwargs))
                        return future.result(timeout=kwargs.get("timeout", self.python_timeout) + 5)
                except RuntimeError:
                    # Нет запущенного loop - можем использовать asyncio.run
                    return asyncio.run(self._execute_python(**kwargs))
            elif action == "execute_shell":
                # Аналогично для shell
                try:
                    loop = asyncio.get_running_loop()
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._execute_shell(**kwargs))
                        return future.result(timeout=kwargs.get("timeout", self.shell_timeout) + 5)
                except RuntimeError:
                    return asyncio.run(self._execute_shell(**kwargs))
            elif action == "validate_python":
                return self._validate_python_code(**kwargs)
            elif action == "validate_shell":
                return self._validate_shell_command(**kwargs)
            elif action == "list_libraries":
                return self._list_allowed_libraries(**kwargs)
            elif action == "get_execution_limits":
                return self._get_execution_limits(**kwargs)
            else:
                return ToolResult(
                    success=False,
                    error=f"Неизвестное действие: {action}"
                )
                
        except Exception as e:
            logger.error(f"Ошибка Code Execution Tool {action}: {e}")
            return ToolResult(success=False, error=str(e))

    # =====================================================
    # ВЫПОЛНЕНИЕ PYTHON КОДА
    # =====================================================
    
    async def _execute_python(self, **kwargs) -> ToolResult:
        """Безопасное выполнение Python кода"""
        try:
            code = kwargs.get("code", "")
            libraries = kwargs.get("libraries", [])
            timeout = kwargs.get("timeout", self.python_timeout)
            
            if not code:
                return ToolResult(success=False, error="Код для выполнения обязателен")
            
            # Проверка безопасности
            safety_check = self._validate_python_code(code=code, libraries=libraries)
            if not safety_check.success:
                return safety_check
            
            logger.info(f"🐍 Выполняю Python код ({len(code)} символов)")
            if libraries:
                logger.info(f"   📦 Библиотеки: {', '.join(libraries)}")
            
            # Выполняем с таймаутом
            result = await asyncio.wait_for(
                self._run_python_in_sandbox(code, libraries),
                timeout=timeout
            )
            
            return result
                
        except asyncio.TimeoutError:
            logger.error("Python код превысил лимит времени выполнения")
            return ToolResult(success=False, error=f"Превышен лимит времени ({timeout}с)")
        except Exception as e:
            logger.error(f"Ошибка выполнения Python кода: {e}")
            return ToolResult(success=False, error=str(e))

    async def _run_python_in_sandbox(self, code: str, libraries: List[str]) -> ToolResult:
        """Выполнение Python кода в sandbox"""
        try:
            # Подготавливаем окружение
            sandbox_globals = {
                "__builtins__": {
                    # Безопасные встроенные функции
                    "print": print, "len": len, "range": range, "str": str,
                    "int": int, "float": float, "bool": bool, "list": list,
                    "dict": dict, "tuple": tuple, "set": set, "abs": abs,
                    "min": min, "max": max, "sum": sum, "sorted": sorted,
                    "reversed": reversed, "enumerate": enumerate, "zip": zip,
                    "round": round, "pow": pow, "divmod": divmod,
                    "__import__": __import__  # Добавляем __import__ для импорта модулей
                }
            }
            
            # Импортируем разрешенные библиотеки
            for lib in libraries:
                if lib in self.allowed_libraries:
                    try:
                        # Используем __import__ напрямую для импорта в sandbox
                        module = __import__(lib)
                        sandbox_globals[lib] = module
                    except ImportError:
                        logger.warning(f"Библиотека {lib} недоступна")
            
            # Захватываем вывод
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            try:
                sys.stdout = stdout_capture
                sys.stderr = stderr_capture
                
                # Выполняем код в отдельном потоке для безопасности
                result = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    self._execute_python_code, 
                    code, 
                    sandbox_globals
                )
                
                stdout_content = stdout_capture.getvalue()
                stderr_content = stderr_capture.getvalue()
                
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            
            # Ограничиваем размер вывода
            if len(stdout_content) > self.max_output_size:
                stdout_content = stdout_content[:self.max_output_size] + "\n... (вывод обрезан)"
            
            if len(stderr_content) > self.max_output_size:
                stderr_content = stderr_content[:self.max_output_size] + "\n... (ошибки обрезаны)"
            
            output = stdout_content
            if stderr_content:
                output += f"\n--- STDERR ---\n{stderr_content}"
            
            logger.success(f"✅ Python код выполнен успешно ({len(output)} символов вывода)")
            
            return ToolResult(
                success=True,
                data={
                    "output": output or "Код выполнен успешно (без вывода)",
                    "stdout": stdout_content,
                    "stderr": stderr_content,
                    "libraries_used": libraries,
                    "code_length": len(code)
                }
            )
            
        except Exception as e:
            logger.error(f"Ошибка выполнения Python в sandbox: {e}")
            return ToolResult(success=False, error=str(e))

    def _execute_python_code(self, code: str, globals_dict: dict) -> Any:
        """Выполнение Python кода с ограниченными глобалами"""
        try:
            exec(code, globals_dict)
            return True
        except Exception as e:
            raise e

    # =====================================================
    # ВЫПОЛНЕНИЕ SHELL КОМАНД
    # =====================================================
    
    async def _execute_shell(self, **kwargs) -> ToolResult:
        """Безопасное выполнение shell команд"""
        try:
            code = kwargs.get("code", "")
            timeout = kwargs.get("timeout", self.shell_timeout)
            working_dir = kwargs.get("working_dir", ".")
            env_vars = kwargs.get("env_vars", {})
            
            if not code:
                return ToolResult(success=False, error="Команда для выполнения обязательна")
            
            # Проверка безопасности
            safety_check = self._validate_shell_command(code=code)
            if not safety_check.success:
                return safety_check
            
            logger.info(f"💻 Выполняю shell команду: {code}")
            
            # Подготавливаем окружение
            env = os.environ.copy()
            env.update(env_vars)
            
            # Выполняем команду
            process = await asyncio.create_subprocess_shell(
                code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
                env=env
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                stdout_text = stdout.decode('utf-8', errors='replace')
                stderr_text = stderr.decode('utf-8', errors='replace')
                
                # Ограничиваем размер вывода
                if len(stdout_text) > self.max_output_size:
                    stdout_text = stdout_text[:self.max_output_size] + "\n... (вывод обрезан)"
                if len(stderr_text) > self.max_output_size:
                    stderr_text = stderr_text[:self.max_output_size] + "\n... (ошибки обрезаны)"
                
                success = process.returncode == 0
                output = stdout_text
                if stderr_text:
                    output += f"\n--- STDERR ---\n{stderr_text}"
                
                if success:
                    logger.success(f"✅ Shell команда выполнена успешно")
                else:
                    logger.warning(f"⚠️ Shell команда завершилась с кодом {process.returncode}")
                
                return ToolResult(
                    success=success,
                    data={
                        "output": output or f"Команда выполнена (код возврата: {process.returncode})",
                        "return_code": process.returncode,
                        "stdout": stdout_text,
                        "stderr": stderr_text,
                        "command": code,
                        "working_dir": working_dir
                    }
                )
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise asyncio.TimeoutError()
                
        except asyncio.TimeoutError:
            logger.error("Shell команда превысила лимит времени выполнения")
            return ToolResult(success=False, error=f"Превышен лимит времени ({timeout}с)")
        except Exception as e:
            logger.error(f"Ошибка выполнения shell команды: {e}")
            return ToolResult(success=False, error=str(e))

    # =====================================================
    # ПРОВЕРКИ БЕЗОПАСНОСТИ
    # =====================================================
    
    def _validate_python_code(self, **kwargs) -> ToolResult:
        """Проверка безопасности Python кода"""
        code = kwargs.get("code", "")
        libraries = kwargs.get("libraries", [])
        
        if not code:
            return ToolResult(success=False, error="Код для проверки обязателен")
        
        code_lower = code.lower()
        
        # Проверка опасных паттернов
        for pattern in self.dangerous_python_patterns:
            if pattern in code_lower:
                return ToolResult(
                    success=False,
                    error=f"🚨 Обнаружен потенциально опасный паттерн: {pattern}"
                )
        
        # Проверка библиотек
        for lib in libraries:
            if lib not in self.allowed_libraries:
                return ToolResult(
                    success=False,
                    error=f"🚨 Библиотека не разрешена: {lib}"
                )
        
        return ToolResult(success=True, data={"message": "Код прошел проверку безопасности"})

    def _validate_shell_command(self, **kwargs) -> ToolResult:
        """Проверка безопасности shell команд"""
        code = kwargs.get("code", "")
        
        if not code:
            return ToolResult(success=False, error="Команда для проверки обязательна")
        
        command_lower = code.lower()
        
        # Проверка опасных паттернов
        for pattern in self.dangerous_shell_patterns:
            if pattern in command_lower:
                return ToolResult(
                    success=False,
                    error=f"🚨 Обнаружена потенциально опасная команда: {pattern}"
                )
        
        return ToolResult(success=True, data={"message": "Команда прошла проверку безопасности"})

    def _list_allowed_libraries(self, **kwargs) -> ToolResult:
        """Список разрешенных библиотек"""
        return ToolResult(
            success=True,
            data={
                "message": f"Разрешено {len(self.allowed_libraries)} библиотек",
                "allowed_libraries": sorted(list(self.allowed_libraries)),
                "count": len(self.allowed_libraries)
            }
        )

    def _get_execution_limits(self, **kwargs) -> ToolResult:
        """Получение лимитов выполнения"""
        return ToolResult(
            success=True,
            data={
                "message": "Лимиты выполнения",
                "python_timeout": self.python_timeout,
                "shell_timeout": self.shell_timeout,
                "max_output_size": self.max_output_size,
                "allowed_libraries_count": len(self.allowed_libraries),
                "dangerous_python_patterns_count": len(self.dangerous_python_patterns),
                "dangerous_shell_patterns_count": len(self.dangerous_shell_patterns)
            }
        ) 