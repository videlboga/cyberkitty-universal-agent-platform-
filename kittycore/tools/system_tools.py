"""
🔧 SystemTools - Системные инструменты для KittyCore 3.0

Реальные инструменты для системных операций:
- Управление файлами и директориями
- Выполнение системных команд 
- Получение информации о системе
- Работа с процессами
"""

import os
import subprocess
import shutil
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base_tool import Tool, ToolResult

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class FileManager(Tool):
    """Управление файлами и директориями"""
    
    def __init__(self):
        super().__init__(
            name="file_manager",
            description="Управление файлами и директориями"
        )
    
    def execute(self, operation: str, path: str = None, content: str = None, 
               destination: str = None, **kwargs) -> ToolResult:
        """Выполнить файловую операцию"""
        try:
            if operation == "create_file":
                return self._create_file(path, content or "")
            elif operation == "read_file":
                return self._read_file(path)
            elif operation == "delete_file":
                return self._delete_file(path)
            elif operation == "copy_file":
                return self._copy_file(path, destination)
            elif operation == "move_file":
                return self._move_file(path, destination)
            elif operation == "create_directory":
                return self._create_directory(path)
            elif operation == "list_directory":
                return self._list_directory(path or ".")
            elif operation == "get_file_info":
                return self._get_file_info(path)
            else:
                return ToolResult(
                    success=False,
                    error=f"Неизвестная операция: {operation}"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка файловой операции: {str(e)}"
            )
    
    def _create_file(self, path: str, content: str) -> ToolResult:
        """Создать файл"""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return ToolResult(
            success=True,
            data={
                "operation": "create_file",
                "path": str(file_path.absolute()),
                "size": len(content),
                "encoding": "utf-8"
            }
        )
    
    def _read_file(self, path: str) -> ToolResult:
        """Прочитать файл"""
        file_path = Path(path)
        
        if not file_path.exists():
            return ToolResult(
                success=False,
                error=f"Файл не найден: {path}"
            )
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return ToolResult(
            success=True,
            data={
                "operation": "read_file",
                "path": str(file_path.absolute()),
                "content": content,
                "size": len(content),
                "lines": len(content.split('\n'))
            }
        )
    
    def _delete_file(self, path: str) -> ToolResult:
        """Удалить файл"""
        file_path = Path(path)
        
        if not file_path.exists():
            return ToolResult(
                success=False,
                error=f"Файл не найден: {path}"
            )
        
        file_path.unlink()
        
        return ToolResult(
            success=True,
            data={
                "operation": "delete_file",
                "path": str(file_path.absolute()),
                "deleted": True
            }
        )
    
    def _copy_file(self, source: str, destination: str) -> ToolResult:
        """Копировать файл"""
        source_path = Path(source)
        dest_path = Path(destination)
        
        if not source_path.exists():
            return ToolResult(
                success=False,
                error=f"Исходный файл не найден: {source}"
            )
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, dest_path)
        
        return ToolResult(
            success=True,
            data={
                "operation": "copy_file",
                "source": str(source_path.absolute()),
                "destination": str(dest_path.absolute()),
                "size": dest_path.stat().st_size
            }
        )
    
    def _move_file(self, source: str, destination: str) -> ToolResult:
        """Переместить файл"""
        source_path = Path(source)
        dest_path = Path(destination)
        
        if not source_path.exists():
            return ToolResult(
                success=False,
                error=f"Исходный файл не найден: {source}"
            )
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), str(dest_path))
        
        return ToolResult(
            success=True,
            data={
                "operation": "move_file",
                "source": str(source_path.absolute()),
                "destination": str(dest_path.absolute())
            }
        )
    
    def _create_directory(self, path: str) -> ToolResult:
        """Создать директорию"""
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        return ToolResult(
            success=True,
            data={
                "operation": "create_directory",
                "path": str(dir_path.absolute()),
                "created": True
            }
        )
    
    def _list_directory(self, path: str) -> ToolResult:
        """Список содержимого директории"""
        dir_path = Path(path)
        
        if not dir_path.exists():
            return ToolResult(
                success=False,
                error=f"Директория не найдена: {path}"
            )
        
        if not dir_path.is_dir():
            return ToolResult(
                success=False,
                error=f"Путь не является директорией: {path}"
            )
        
        items = []
        for item in dir_path.iterdir():
            try:
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "path": str(item.absolute()),
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else None,
                    "modified": stat.st_mtime
                })
            except (OSError, PermissionError):
                items.append({
                    "name": item.name,
                    "path": str(item.absolute()),
                    "type": "unknown",
                    "error": "Permission denied"
                })
        
        return ToolResult(
            success=True,
            data={
                "operation": "list_directory",
                "path": str(dir_path.absolute()),
                "items": items,
                "total_items": len(items),
                "files": len([i for i in items if i.get("type") == "file"]),
                "directories": len([i for i in items if i.get("type") == "directory"])
            }
        )
    
    def _get_file_info(self, path: str) -> ToolResult:
        """Получить информацию о файле"""
        file_path = Path(path)
        
        if not file_path.exists():
            return ToolResult(
                success=False,
                error=f"Файл не найден: {path}"
            )
        
        stat = file_path.stat()
        
        return ToolResult(
            success=True,
            data={
                "operation": "get_file_info",
                "path": str(file_path.absolute()),
                "name": file_path.name,
                "type": "directory" if file_path.is_dir() else "file",
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "permissions": oct(stat.st_mode)[-3:],
                "owner_readable": os.access(file_path, os.R_OK),
                "owner_writable": os.access(file_path, os.W_OK),
                "owner_executable": os.access(file_path, os.X_OK)
            }
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "create_file", "read_file", "delete_file", 
                        "copy_file", "move_file", "create_directory",
                        "list_directory", "get_file_info"
                    ],
                    "description": "Файловая операция"
                },
                "path": {
                    "type": "string",
                    "description": "Путь к файлу или директории"
                },
                "content": {
                    "type": "string",
                    "description": "Содержимое файла (для create_file)"
                },
                "destination": {
                    "type": "string",
                    "description": "Путь назначения (для copy_file, move_file)"
                }
            },
            "required": ["operation"]
        }


class SystemTools(Tool):
    """Системные операции и информация"""
    
    def __init__(self):
        super().__init__(
            name="system_tools",
            description="Выполнение системных команд и получение информации о системе"
        )
    
    def execute(self, operation: str, command: str = None, **kwargs) -> ToolResult:
        """Выполнить системную операцию"""
        try:
            if operation == "run_command":
                return self._run_command(command, **kwargs)
            elif operation == "get_system_info":
                return self._get_system_info()
            elif operation == "get_process_info":
                return self._get_process_info(**kwargs)
            elif operation == "get_disk_usage":
                return self._get_disk_usage(kwargs.get("path", "."))
            elif operation == "get_memory_info":
                return self._get_memory_info()
            else:
                return ToolResult(
                    success=False,
                    error=f"Неизвестная операция: {operation}"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка системной операции: {str(e)}"
            )
    
    def _run_command(self, command: str, timeout: int = 30, shell: bool = False) -> ToolResult:
        """Выполнить системную команду"""
        if not command:
            return ToolResult(
                success=False,
                error="Команда не указана"
            )
        
        # Базовые проверки безопасности
        dangerous_commands = ['rm -rf', 'del /f', 'format', 'mkfs', 'dd if=']
        if any(danger in command.lower() for danger in dangerous_commands):
            return ToolResult(
                success=False,
                error="Выполнение потенциально опасной команды заблокировано"
            )
        
        try:
            if shell:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            else:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            
            return ToolResult(
                success=True,
                data={
                    "operation": "run_command",
                    "command": command,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                }
            )
            
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error=f"Команда превысила таймаут {timeout} секунд"
            )
    
    def _get_system_info(self) -> ToolResult:
        """Получить информацию о системе"""
        try:
            info = {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                "python_version": platform.python_version(),
                "current_directory": os.getcwd(),
                "environment_variables": len(os.environ),
                "cpu_count": os.cpu_count(),
            }
            
            # Добавляем информацию из psutil если доступен
            if PSUTIL_AVAILABLE:
                import psutil
                info.update({
                    "boot_time": psutil.boot_time(),
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory": {
                        "total": psutil.virtual_memory().total,
                        "available": psutil.virtual_memory().available,
                        "percent": psutil.virtual_memory().percent
                    },
                    "disk": {
                        "total": psutil.disk_usage('/').total,
                        "used": psutil.disk_usage('/').used,
                        "free": psutil.disk_usage('/').free
                    }
                })
            else:
                info["psutil_available"] = False
            
            return ToolResult(
                success=True,
                data={
                    "operation": "get_system_info",
                    "system_info": info
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения системной информации: {str(e)}"
            )
    
    def _get_process_info(self, pid: int = None) -> ToolResult:
        """Получить информацию о процессах"""
        if not PSUTIL_AVAILABLE:
            return ToolResult(
                success=False,
                error="psutil не доступен. Установите: pip install psutil"
            )
            
        try:
            import psutil
            
            if pid:
                # Информация о конкретном процессе
                try:
                    process = psutil.Process(pid)
                    info = {
                        "pid": process.pid,
                        "name": process.name(),
                        "status": process.status(),
                        "cpu_percent": process.cpu_percent(),
                        "memory_percent": process.memory_percent(),
                        "create_time": process.create_time(),
                        "cmdline": process.cmdline()
                    }
                    
                    return ToolResult(
                        success=True,
                        data={
                            "operation": "get_process_info",
                            "process": info
                        }
                    )
                except psutil.NoSuchProcess:
                    return ToolResult(
                        success=False,
                        error=f"Процесс с PID {pid} не найден"
                    )
            else:
                # Список всех процессов (топ 10 по CPU)
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Сортируем по CPU
                processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
                
                return ToolResult(
                    success=True,
                    data={
                        "operation": "get_process_info",
                        "processes": processes[:10],
                        "total_processes": len(processes)
                    }
                )
                
        except ImportError:
            return ToolResult(
                success=False,
                error="psutil не доступен. Установите: pip install psutil"
            )
    
    def _get_disk_usage(self, path: str) -> ToolResult:
        """Получить информацию об использовании диска"""
        try:
            usage = shutil.disk_usage(path)
            
            return ToolResult(
                success=True,
                data={
                    "operation": "get_disk_usage",
                    "path": path,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent_used": (usage.used / usage.total) * 100
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения информации о диске: {str(e)}"
            )
    
    def _get_memory_info(self) -> ToolResult:
        """Получить информацию о памяти"""
        if not PSUTIL_AVAILABLE:
            return ToolResult(
                success=False,
                error="psutil не доступен. Установите: pip install psutil"
            )
            
        try:
            import psutil
            
            virtual = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return ToolResult(
                success=True,
                data={
                    "operation": "get_memory_info",
                    "virtual_memory": {
                        "total": virtual.total,
                        "available": virtual.available,
                        "used": virtual.used,
                        "percent": virtual.percent
                    },
                    "swap_memory": {
                        "total": swap.total,
                        "used": swap.used,
                        "free": swap.free,
                        "percent": swap.percent
                    }
                }
            )
            
        except ImportError:
            return ToolResult(
                success=False,
                error="psutil не доступен. Установите: pip install psutil"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": [
                        "run_command", "get_system_info", "get_process_info",
                        "get_disk_usage", "get_memory_info"
                    ],
                    "description": "Системная операция"
                },
                "command": {
                    "type": "string",
                    "description": "Команда для выполнения (для run_command)"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Таймаут выполнения команды в секундах",
                    "default": 30
                },
                "shell": {
                    "type": "boolean",
                    "description": "Выполнять через shell",
                    "default": False
                },
                "pid": {
                    "type": "integer",
                    "description": "PID процесса (для get_process_info)"
                },
                "path": {
                    "type": "string",
                    "description": "Путь для проверки диска",
                    "default": "."
                }
            },
            "required": ["operation"]
        } 