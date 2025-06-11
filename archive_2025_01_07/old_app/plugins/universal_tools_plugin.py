"""
Universal Tools Plugin для KittyCore
Интеграция всех существующих инструментов:
- FileSystemTool
- PythonExecutionTool  
- WebScrapingTool
- ShellExecutionTool

Обеспечивает полное взаимодействие с реальным миром:
- Работа с файловой системой
- Выполнение кода (Python, Shell)
- Web scraping и загрузка
- Безопасное выполнение в sandbox
"""

import asyncio
import subprocess
import tempfile
import shutil
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import logging
from loguru import logger

from app.core.base_plugin import BasePlugin

try:
    # Импортируем существующие инструменты
    from kittycore.universal_tools import (
        PythonExecutionTool, 
        WebScrapingTool,
        ToolResult
    )
    from browser_tools.browser_tools import FileSystemTool
    UNIVERSAL_TOOLS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Universal tools недоступны: {e}")
    UNIVERSAL_TOOLS_AVAILABLE = False
    # Создаем заглушки
    class ToolResult:
        def __init__(self, success: bool, result: str = "", error: str = "", **kwargs):
            self.success = success
            self.result = result
            self.error = error


class UniversalToolsPlugin(BasePlugin):
    """
    Universal Tools Plugin - полная интеграция с реальным миром
    """
    
    def __init__(self):
        super().__init__()
        self.name = "universal_tools"
        self.version = "1.0.0"
        self.description = "Универсальные инструменты для взаимодействия с реальным миром"
        
        # Инициализация инструментов
        if UNIVERSAL_TOOLS_AVAILABLE:
            self.filesystem_tool = FileSystemTool()
            self.python_tool = PythonExecutionTool()
            self.web_tool = WebScrapingTool()
        
        # Настройки по умолчанию
        self.default_settings = {
            "enable_filesystem": True,
            "enable_python_exec": True,
            "enable_web_scraping": True,
            "enable_shell_exec": False,  # По умолчанию отключен из соображений безопасности
            "sandbox_enabled": True,
            "max_file_size_mb": 10,
            "allowed_file_extensions": [".txt", ".json", ".csv", ".md", ".py", ".js", ".html", ".css"],
            "blocked_domains": ["localhost", "127.0.0.1", "internal"],
            "python_timeout": 30,
            "shell_timeout": 15,
            "max_output_size": 10000
        }

    async def initialize(self) -> bool:
        """Инициализация плагина"""
        try:
            if not UNIVERSAL_TOOLS_AVAILABLE:
                logger.error("Universal tools недоступны - плагин не может работать")
                return False
                
            await self._ensure_fresh_settings()
            
            logger.info(f"🛠️ Universal Tools Plugin v{self.version} инициализирован")
            logger.info(f"   📁 Файловая система: {'✅' if self.settings.get('enable_filesystem') else '❌'}")
            logger.info(f"   🐍 Python выполнение: {'✅' if self.settings.get('enable_python_exec') else '❌'}")
            logger.info(f"   🌐 Web scraping: {'✅' if self.settings.get('enable_web_scraping') else '❌'}")
            logger.info(f"   💻 Shell команды: {'✅' if self.settings.get('enable_shell_exec') else '❌'}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Universal Tools Plugin: {e}")
            return False

    # =====================================================
    # ФАЙЛОВАЯ СИСТЕМА
    # =====================================================
    
    async def file_create(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Создание файла"""
        try:
            if not self.settings.get("enable_filesystem", True):
                return {"success": False, "error": "Файловые операции отключены"}
                
            path = context.get("path", "")
            content = context.get("content", "")
            
            if not path:
                return {"success": False, "error": "Путь к файлу обязателен"}
            
            # Проверка расширения файла
            if not self._is_allowed_file_extension(path):
                return {"success": False, "error": f"Расширение файла не разрешено: {Path(path).suffix}"}
            
            # Проверка размера контента
            if len(content.encode('utf-8')) > self.settings.get("max_file_size_mb", 10) * 1024 * 1024:
                return {"success": False, "error": "Файл слишком большой"}
            
            logger.info(f"📝 Создаю файл: {path}")
            
            result = self.filesystem_tool.execute(
                action="create",
                path=path,
                content=content
            )
            
            if result.success:
                logger.success(f"✅ Файл создан: {path}")
                return {
                    "success": True,
                    "path": path,
                    "message": result.data.get("message", "Файл создан"),
                    "size": len(content.encode('utf-8'))
                }
            else:
                return {"success": False, "error": result.error}
                
        except Exception as e:
            logger.error(f"Ошибка создания файла: {e}")
            return {"success": False, "error": str(e)}

    async def file_read(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Чтение файла"""
        try:
            if not self.settings.get("enable_filesystem", True):
                return {"success": False, "error": "Файловые операции отключены"}
                
            path = context.get("path", "")
            
            if not path:
                return {"success": False, "error": "Путь к файлу обязателен"}
            
            logger.info(f"📖 Читаю файл: {path}")
            
            result = self.filesystem_tool.execute(action="read", path=path)
            
            if result.success:
                content = result.data.get("content", "")
                
                # Ограничиваем размер вывода
                max_output = self.settings.get("max_output_size", 10000)
                if len(content) > max_output:
                    content = content[:max_output] + "\n... (контент обрезан)"
                
                logger.success(f"✅ Файл прочитан: {path} ({len(content)} символов)")
                return {
                    "success": True,
                    "path": path,
                    "content": content,
                    "size": len(content)
                }
            else:
                return {"success": False, "error": result.error}
                
        except Exception as e:
            logger.error(f"Ошибка чтения файла: {e}")
            return {"success": False, "error": str(e)}

    async def file_write(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Запись в файл"""
        try:
            if not self.settings.get("enable_filesystem", True):
                return {"success": False, "error": "Файловые операции отключены"}
                
            path = context.get("path", "")
            content = context.get("content", "")
            
            if not path:
                return {"success": False, "error": "Путь к файлу обязателен"}
            
            # Проверки безопасности
            if not self._is_allowed_file_extension(path):
                return {"success": False, "error": f"Расширение файла не разрешено: {Path(path).suffix}"}
            
            if len(content.encode('utf-8')) > self.settings.get("max_file_size_mb", 10) * 1024 * 1024:
                return {"success": False, "error": "Контент слишком большой"}
            
            logger.info(f"✏️ Записываю в файл: {path}")
            
            result = self.filesystem_tool.execute(
                action="write",
                path=path,
                content=content
            )
            
            if result.success:
                logger.success(f"✅ Файл записан: {path}")
                return {
                    "success": True,
                    "path": path,
                    "message": result.data.get("message", "Файл записан"),
                    "size": len(content.encode('utf-8'))
                }
            else:
                return {"success": False, "error": result.error}
                
        except Exception as e:
            logger.error(f"Ошибка записи файла: {e}")
            return {"success": False, "error": str(e)}

    async def file_delete(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Удаление файла"""
        try:
            if not self.settings.get("enable_filesystem", True):
                return {"success": False, "error": "Файловые операции отключены"}
                
            path = context.get("path", "")
            
            if not path:
                return {"success": False, "error": "Путь к файлу обязателен"}
            
            logger.info(f"🗑️ Удаляю файл: {path}")
            
            result = self.filesystem_tool.execute(action="delete", path=path)
            
            if result.success:
                logger.success(f"✅ Файл удален: {path}")
                return {
                    "success": True,
                    "path": path,
                    "message": result.data.get("message", "Файл удален")
                }
            else:
                return {"success": False, "error": result.error}
                
        except Exception as e:
            logger.error(f"Ошибка удаления файла: {e}")
            return {"success": False, "error": str(e)}

    async def file_list(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Список файлов в директории"""
        try:
            if not self.settings.get("enable_filesystem", True):
                return {"success": False, "error": "Файловые операции отключены"}
                
            path = context.get("path", ".")
            
            logger.info(f"📋 Список файлов: {path}")
            
            result = self.filesystem_tool.execute(action="list", path=path)
            
            if result.success:
                items = result.data.get("items", [])
                logger.success(f"✅ Найдено {len(items)} элементов в {path}")
                return {
                    "success": True,
                    "path": path,
                    "items": items,
                    "count": len(items)
                }
            else:
                return {"success": False, "error": result.error}
                
        except Exception as e:
            logger.error(f"Ошибка получения списка файлов: {e}")
            return {"success": False, "error": str(e)}

    # =====================================================
    # ВЫПОЛНЕНИЕ PYTHON КОДА
    # =====================================================
    
    async def python_execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение Python кода"""
        try:
            if not self.settings.get("enable_python_exec", True):
                return {"success": False, "error": "Выполнение Python кода отключено"}
                
            code = context.get("code", "")
            libraries = context.get("libraries", [])
            timeout = context.get("timeout", self.settings.get("python_timeout", 30))
            
            if not code:
                return {"success": False, "error": "Код для выполнения обязателен"}
            
            # Проверки безопасности
            if self._has_dangerous_python_code(code):
                return {"success": False, "error": "Код содержит потенциально опасные операции"}
            
            logger.info(f"🐍 Выполняю Python код ({len(code)} символов)")
            if libraries:
                logger.info(f"   📦 Библиотеки: {', '.join(libraries)}")
            
            # Выполняем с таймаутом
            result = await asyncio.wait_for(
                self._execute_python_async(code, libraries),
                timeout=timeout
            )
            
            if result.success:
                output = result.result
                
                # Ограничиваем размер вывода
                max_output = self.settings.get("max_output_size", 10000)
                if len(output) > max_output:
                    output = output[:max_output] + "\n... (вывод обрезан)"
                
                logger.success(f"✅ Python код выполнен успешно ({len(output)} символов вывода)")
                return {
                    "success": True,
                    "output": output,
                    "code": code,
                    "libraries": libraries
                }
            else:
                return {"success": False, "error": result.error}
                
        except asyncio.TimeoutError:
            logger.error("Python код превысил лимит времени выполнения")
            return {"success": False, "error": "Превышен лимит времени выполнения"}
        except Exception as e:
            logger.error(f"Ошибка выполнения Python кода: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_python_async(self, code: str, libraries: List[str]) -> ToolResult:
        """Асинхронное выполнение Python кода"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.python_tool.execute, 
            code, 
            libraries
        )

    # =====================================================
    # SHELL КОМАНДЫ
    # =====================================================
    
    async def shell_execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение shell команд"""
        try:
            if not self.settings.get("enable_shell_exec", False):
                return {"success": False, "error": "Выполнение shell команд отключено"}
                
            command = context.get("command", "")
            timeout = context.get("timeout", self.settings.get("shell_timeout", 15))
            working_dir = context.get("working_dir", ".")
            
            if not command:
                return {"success": False, "error": "Команда для выполнения обязательна"}
            
            # Проверки безопасности
            if self._has_dangerous_shell_command(command):
                return {"success": False, "error": "Команда содержит потенциально опасные операции"}
            
            logger.info(f"💻 Выполняю shell команду: {command}")
            
            # Выполняем команду с ограничениями
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                stdout_text = stdout.decode('utf-8', errors='replace')
                stderr_text = stderr.decode('utf-8', errors='replace')
                
                # Ограничиваем размер вывода
                max_output = self.settings.get("max_output_size", 10000)
                if len(stdout_text) > max_output:
                    stdout_text = stdout_text[:max_output] + "\n... (вывод обрезан)"
                if len(stderr_text) > max_output:
                    stderr_text = stderr_text[:max_output] + "\n... (ошибки обрезаны)"
                
                success = process.returncode == 0
                
                if success:
                    logger.success(f"✅ Shell команда выполнена успешно")
                else:
                    logger.warning(f"⚠️ Shell команда завершилась с кодом {process.returncode}")
                
                return {
                    "success": success,
                    "command": command,
                    "exit_code": process.returncode,
                    "stdout": stdout_text,
                    "stderr": stderr_text,
                    "working_dir": working_dir
                }
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                logger.error("Shell команда превысила лимит времени")
                return {"success": False, "error": "Превышен лимит времени выполнения"}
                
        except Exception as e:
            logger.error(f"Ошибка выполнения shell команды: {e}")
            return {"success": False, "error": str(e)}

    # =====================================================
    # WEB SCRAPING
    # =====================================================
    
    async def web_scrape(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Web scraping и получение контента"""
        try:
            if not self.settings.get("enable_web_scraping", True):
                return {"success": False, "error": "Web scraping отключен"}
                
            url = context.get("url", "")
            method = context.get("method", "text")
            selector = context.get("selector", None)
            
            if not url:
                return {"success": False, "error": "URL обязателен"}
            
            # Проверка блокированных доменов
            if self._is_blocked_domain(url):
                return {"success": False, "error": "Домен заблокирован"}
            
            logger.info(f"🌐 Web scraping: {url}")
            if selector:
                logger.info(f"   🎯 Селектор: {selector}")
            
            # Выполняем scraping
            result = await asyncio.wait_for(
                self._web_scrape_async(url, method, selector),
                timeout=30
            )
            
            if result.success:
                content = result.result
                
                # Ограничиваем размер вывода
                max_output = self.settings.get("max_output_size", 10000)
                if isinstance(content, str) and len(content) > max_output:
                    content = content[:max_output] + "\n... (контент обрезан)"
                
                logger.success(f"✅ Web scraping завершен успешно")
                return {
                    "success": True,
                    "url": url,
                    "method": method,
                    "content": content,
                    "metadata": result.metadata if hasattr(result, 'metadata') else {}
                }
            else:
                return {"success": False, "error": result.error}
                
        except asyncio.TimeoutError:
            logger.error("Web scraping превысил лимит времени")
            return {"success": False, "error": "Превышен лимит времени"}
        except Exception as e:
            logger.error(f"Ошибка web scraping: {e}")
            return {"success": False, "error": str(e)}

    async def _web_scrape_async(self, url: str, method: str, selector: str) -> ToolResult:
        """Асинхронный web scraping"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.web_tool.execute,
            url,
            method,
            selector
        )

    async def web_download(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Загрузка файлов из интернета"""
        try:
            if not self.settings.get("enable_web_scraping", True):
                return {"success": False, "error": "Web операции отключены"}
                
            url = context.get("url", "")
            filename = context.get("filename", "")
            
            if not url:
                return {"success": False, "error": "URL обязателен"}
            
            if not filename:
                # Генерируем имя из URL
                filename = Path(url).name or "downloaded_file"
            
            # Проверки безопасности
            if self._is_blocked_domain(url):
                return {"success": False, "error": "Домен заблокирован"}
            
            if not self._is_allowed_file_extension(filename):
                return {"success": False, "error": f"Расширение файла не разрешено: {Path(filename).suffix}"}
            
            logger.info(f"⬇️ Загружаю файл: {url} -> {filename}")
            
            # Загружаем файл
            import requests
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: requests.get(url, timeout=30)
                ),
                timeout=60
            )
            
            response.raise_for_status()
            
            # Проверяем размер
            content_length = len(response.content)
            max_size = self.settings.get("max_file_size_mb", 10) * 1024 * 1024
            
            if content_length > max_size:
                return {"success": False, "error": "Файл слишком большой"}
            
            # Сохраняем файл
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            logger.success(f"✅ Файл загружен: {filename} ({content_length} байт)")
            
            return {
                "success": True,
                "url": url,
                "filename": filename,
                "size": content_length,
                "content_type": response.headers.get('content-type', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Ошибка загрузки файла: {e}")
            return {"success": False, "error": str(e)}

    # =====================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ БЕЗОПАСНОСТИ
    # =====================================================
    
    def _is_allowed_file_extension(self, path: str) -> bool:
        """Проверка разрешенного расширения файла"""
        allowed_extensions = self.settings.get("allowed_file_extensions", [])
        if not allowed_extensions:
            return True
        
        extension = Path(path).suffix.lower()
        return extension in allowed_extensions
    
    def _is_blocked_domain(self, url: str) -> bool:
        """Проверка заблокированных доменов"""
        blocked_domains = self.settings.get("blocked_domains", [])
        if not blocked_domains:
            return False
        
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        
        for blocked in blocked_domains:
            if blocked.lower() in domain:
                return True
        
        return False
    
    def _has_dangerous_python_code(self, code: str) -> bool:
        """Проверка опасного Python кода"""
        dangerous_patterns = [
            'import os',
            'import sys', 
            'import subprocess',
            'exec(',
            'eval(',
            '__import__',
            'open(',
            'file(',
            'input(',
            'raw_input(',
            'compile(',
            'reload(',
            'delattr(',
            'setattr(',
            'getattr(',
            'hasattr(',
            'globals(',
            'locals(',
            'vars(',
            'dir(',
            'help(',
            'exit(',
            'quit(',
            'license(',
            'copyright(',
            'credits(',
            'reload(',
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                logger.warning(f"🚨 Обнаружен потенциально опасный паттерн: {pattern}")
                return True
        
        return False
    
    def _has_dangerous_shell_command(self, command: str) -> bool:
        """Проверка опасных shell команд"""
        dangerous_patterns = [
            'rm -rf',
            'sudo',
            'su ',
            'passwd',
            'userdel',
            'useradd',
            'usermod',
            'chmod 777',
            'chown',
            'mkfs',
            'fdisk',
            'mount',
            'umount',
            'iptables',
            'systemctl',
            'service',
            'kill -9',
            'killall',
            'pkill',
            'shutdown',
            'reboot',
            'halt',
            'dd if=',
            'wget',
            'curl',
            'nc ',
            'netcat',
            'ssh',
            'scp',
            'rsync',
            'tar -xf',
            'unzip',
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                logger.warning(f"🚨 Обнаружена потенциально опасная команда: {pattern}")
                return True
        
        return False

    # =====================================================
    # СИСТЕМНЫЕ МЕТОДЫ
    # =====================================================
    
    async def get_system_info(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Получение информации о системе"""
        try:
            import platform
            import psutil
            
            system_info = {
                "platform": platform.platform(),
                "system": platform.system(),
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(),
                "uptime": psutil.boot_time()
            }
            
            logger.info("📊 Получена информация о системе")
            return {"success": True, "system_info": system_info}
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о системе: {e}")
            return {"success": False, "error": str(e)}

    async def healthcheck(self) -> bool:
        """Проверка здоровья плагина"""
        try:
            # Проверяем доступность инструментов
            if not UNIVERSAL_TOOLS_AVAILABLE:
                logger.error("Universal tools недоступны")
                return False
            
            # Проверяем настройки
            await self._ensure_fresh_settings()
            
            # Тестируем базовые операции
            if self.settings.get("enable_filesystem"):
                test_file = "test_universal_tools.tmp"
                try:
                    result = self.filesystem_tool.execute(
                        action="create",
                        path=test_file,
                        content="test"
                    )
                    if result.success:
                        self.filesystem_tool.execute(action="delete", path=test_file)
                except Exception:
                    logger.warning("Файловая система недоступна")
                    return False
            
            logger.info("✅ Universal Tools Plugin работает корректно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка healthcheck Universal Tools: {e}")
            return False

    # =====================================================
    # РЕГИСТРАЦИЯ HANDLERS
    # =====================================================
    
    def register_handlers(self) -> Dict[str, Callable]:
        """Регистрация всех handlers плагина"""
        return {
            # Файловая система
            "file_create": self.file_create,
            "file_read": self.file_read,
            "file_write": self.file_write,
            "file_delete": self.file_delete,
            "file_list": self.file_list,
            
            # Python выполнение
            "python_execute": self.python_execute,
            "code_execute": self.python_execute,  # Алиас
            
            # Shell команды
            "shell_execute": self.shell_execute,
            "command_execute": self.shell_execute,  # Алиас
            
            # Web операции
            "web_scrape": self.web_scrape,
            "web_download": self.web_download,
            "download_file": self.web_download,  # Алиас
            
            # Системная информация
            "get_system_info": self.get_system_info,
            "system_info": self.get_system_info,  # Алиас
        } 