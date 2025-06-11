"""
Enhanced System Tools для KittyCore 3.0
Расширенные системные инструменты с продвинутыми возможностями и безопасностью

Возможности:
- Продвинутая работа с файлами с проверками безопасности
- Системная информация (CPU, память, диск)
- Безопасные проверки расширений файлов  
- Мониторинг состояния системы
- Healthcheck операции
"""

import os
import platform
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from loguru import logger

from .base_tool import Tool, ToolResult

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil не установлен - системная информация ограничена")


class EnhancedSystemTool(Tool):
    """
    Расширенные системные инструменты с безопасностью
    """
    
    def __init__(self):
        super().__init__(
            name="enhanced_system",
            description="Расширенные системные операции: файлы, система, мониторинг"
        )
        
        # Настройки безопасности
        self.allowed_extensions = {
            ".txt", ".json", ".csv", ".md", ".py", ".js", ".html", ".css",
            ".xml", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".log"
        }
        self.blocked_extensions = {
            ".exe", ".dll", ".so", ".dylib", ".bin", ".deb", ".rpm"
        }
        self.max_file_size_mb = 10
        self.max_output_size = 10000

    def get_schema(self):
        """Схема для расширенных системных операций"""
        return {
            "type": "object", 
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        # Файловые операции с безопасностью
                        "safe_file_create", "safe_file_read", "safe_file_write",
                        "safe_file_delete", "safe_file_list", "file_info",
                        
                        # Системная информация
                        "get_system_info", "get_cpu_info", "get_memory_info", 
                        "get_disk_info", "get_process_info",
                        
                        # Мониторинг
                        "health_check", "performance_check", "disk_usage",
                        
                        # Утилиты
                        "validate_file_path", "check_file_safety"
                    ],
                    "description": "Действие для выполнения"
                },
                "path": {
                    "type": "string",
                    "description": "Путь к файлу или директории"
                },
                "content": {
                    "type": "string", 
                    "description": "Контент для записи в файл"
                },
                "encoding": {
                    "type": "string",
                    "default": "utf-8",
                    "description": "Кодировка файла"
                },
                "max_size": {
                    "type": "integer",
                    "description": "Максимальный размер файла в байтах"
                },
                "recursive": {
                    "type": "boolean",
                    "default": false,
                    "description": "Рекурсивный поиск/операция"
                }
            },
            "required": ["action"]
        }

    def execute(self, action: str, **kwargs) -> ToolResult:
        """Выполнить расширенную системную операцию"""
        try:
            # Файловые операции с безопасностью
            if action == "safe_file_create":
                return self._safe_file_create(**kwargs)
            elif action == "safe_file_read":
                return self._safe_file_read(**kwargs)
            elif action == "safe_file_write":
                return self._safe_file_write(**kwargs)
            elif action == "safe_file_delete":
                return self._safe_file_delete(**kwargs)
            elif action == "safe_file_list":
                return self._safe_file_list(**kwargs)
            elif action == "file_info":
                return self._get_file_info(**kwargs)
                
            # Системная информация
            elif action == "get_system_info":
                return self._get_system_info(**kwargs)
            elif action == "get_cpu_info":
                return self._get_cpu_info(**kwargs)
            elif action == "get_memory_info":
                return self._get_memory_info(**kwargs)
            elif action == "get_disk_info":
                return self._get_disk_info(**kwargs)
            elif action == "get_process_info":
                return self._get_process_info(**kwargs)
                
            # Мониторинг
            elif action == "health_check":
                return self._health_check(**kwargs)
            elif action == "performance_check":
                return self._performance_check(**kwargs)
            elif action == "disk_usage":
                return self._disk_usage(**kwargs)
                
            # Утилиты
            elif action == "validate_file_path":
                return self._validate_file_path(**kwargs)
            elif action == "check_file_safety":
                return self._check_file_safety(**kwargs)
            else:
                return ToolResult(
                    success=False,
                    error=f"Неизвестное действие: {action}"
                )
                
        except Exception as e:
            logger.error(f"Ошибка Enhanced System Tool {action}: {e}")
            return ToolResult(success=False, error=str(e))

    # =====================================================
    # БЕЗОПАСНЫЕ ФАЙЛОВЫЕ ОПЕРАЦИИ
    # =====================================================
    
    def _safe_file_create(self, **kwargs) -> ToolResult:
        """Безопасное создание файла"""
        try:
            path = kwargs.get("path", "")
            content = kwargs.get("content", "")
            encoding = kwargs.get("encoding", "utf-8")
            
            # Валидация
            validation = self._validate_file_operation(path, content)
            if not validation.success:
                return validation
            
            # Создаем директории если нужно
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Записываем файл
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.info(f"📝 Создан файл: {path} ({len(content)} символов)")
            
            return ToolResult(
                success=True,
                data={
                    "message": f"Файл создан: {path}",
                    "path": str(file_path.absolute()),
                    "size": len(content.encode(encoding)),
                    "encoding": encoding
                }
            )
            
        except Exception as e:
            logger.error(f"Ошибка создания файла: {e}")
            return ToolResult(success=False, error=str(e))

    def _safe_file_read(self, **kwargs) -> ToolResult:
        """Безопасное чтение файла"""
        try:
            path = kwargs.get("path", "")
            encoding = kwargs.get("encoding", "utf-8")
            max_size = kwargs.get("max_size", self.max_file_size_mb * 1024 * 1024)
            
            if not path:
                return ToolResult(success=False, error="Путь к файлу обязателен")
            
            file_path = Path(path)
            
            # Проверки безопасности
            if not file_path.exists():
                return ToolResult(success=False, error="Файл не существует")
            
            if not file_path.is_file():
                return ToolResult(success=False, error="Указанный путь не является файлом")
            
            # Проверка размера
            file_size = file_path.stat().st_size
            if file_size > max_size:
                return ToolResult(
                    success=False, 
                    error=f"Файл слишком большой: {file_size} байт (лимит: {max_size})"
                )
            
            # Проверка расширения
            if not self._is_allowed_extension(path):
                return ToolResult(
                    success=False,
                    error=f"Расширение файла не разрешено: {file_path.suffix}"
                )
            
            # Читаем файл
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Ограничиваем вывод
            if len(content) > self.max_output_size:
                content = content[:self.max_output_size] + "\n... (контент обрезан)"
            
            logger.info(f"📖 Прочитан файл: {path} ({len(content)} символов)")
            
            return ToolResult(
                success=True,
                data={
                    "content": content,
                    "path": str(file_path.absolute()),
                    "size": file_size,
                    "encoding": encoding,
                    "truncated": len(content) > self.max_output_size
                }
            )
            
        except Exception as e:
            logger.error(f"Ошибка чтения файла: {e}")
            return ToolResult(success=False, error=str(e))

    def _safe_file_list(self, **kwargs) -> ToolResult:
        """Безопасный список файлов"""
        try:
            path = kwargs.get("path", ".")
            recursive = kwargs.get("recursive", False)
            
            dir_path = Path(path)
            
            if not dir_path.exists():
                return ToolResult(success=False, error="Директория не существует")
            
            if not dir_path.is_dir():
                return ToolResult(success=False, error="Указанный путь не является директорией")
            
            items = []
            
            if recursive:
                pattern = "**/*"
                files = dir_path.rglob(pattern)
            else:
                files = dir_path.iterdir()
            
            for item in files:
                try:
                    stat = item.stat()
                    items.append({
                        "name": item.name,
                        "path": str(item.absolute()),
                        "type": "file" if item.is_file() else "directory",
                        "size": stat.st_size if item.is_file() else None,
                        "modified": stat.st_mtime,
                        "extension": item.suffix if item.is_file() else None,
                        "safe": self._is_allowed_extension(str(item)) if item.is_file() else True
                    })
                except (PermissionError, OSError):
                    # Пропускаем недоступные файлы
                    continue
            
            logger.info(f"📋 Найдено {len(items)} элементов в {path}")
            
            return ToolResult(
                success=True,
                data={
                    "message": f"Найдено {len(items)} элементов",
                    "path": str(dir_path.absolute()),
                    "items": items,
                    "count": len(items),
                    "recursive": recursive
                }
            )
            
        except Exception as e:
            logger.error(f"Ошибка получения списка файлов: {e}")
            return ToolResult(success=False, error=str(e))

    # =====================================================
    # СИСТЕМНАЯ ИНФОРМАЦИЯ
    # =====================================================
    
    def _get_system_info(self, **kwargs) -> ToolResult:
        """Получение полной информации о системе"""
        try:
            system_info = {
                "platform": {
                    "system": platform.system(),
                    "release": platform.release(), 
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "architecture": platform.architecture(),
                    "platform": platform.platform()
                },
                "python": {
                    "version": platform.python_version(),
                    "implementation": platform.python_implementation(),
                    "compiler": platform.python_compiler()
                }
            }
            
            # Добавляем информацию от psutil если доступен
            if PSUTIL_AVAILABLE:
                system_info.update({
                    "memory": {
                        "total": psutil.virtual_memory().total,
                        "available": psutil.virtual_memory().available,
                        "percent": psutil.virtual_memory().percent,
                        "used": psutil.virtual_memory().used
                    },
                    "cpu": {
                        "count": psutil.cpu_count(),
                        "count_logical": psutil.cpu_count(logical=True),
                        "percent": psutil.cpu_percent(interval=1),
                        "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                    },
                    "disk": {
                        "usage": psutil.disk_usage('/')._asdict(),
                        "partitions": [p._asdict() for p in psutil.disk_partitions()]
                    },
                    "network": {
                        "connections": len(psutil.net_connections()),
                        "io_stats": psutil.net_io_counters()._asdict()
                    },
                    "uptime": psutil.boot_time()
                })
            
            logger.info("📊 Получена системная информация")
            
            return ToolResult(
                success=True,
                data={
                    "message": "Системная информация получена",
                    **system_info
                }
            )
            
        except Exception as e:
            logger.error(f"Ошибка получения системной информации: {e}")
            return ToolResult(success=False, error=str(e))

    # =====================================================
    # УТИЛИТЫ БЕЗОПАСНОСТИ  
    # =====================================================
    
    def _validate_file_operation(self, path: str, content: str = "") -> ToolResult:
        """Валидация файловой операции"""
        if not path:
            return ToolResult(success=False, error="Путь к файлу обязателен")
        
        # Проверка расширения
        if not self._is_allowed_extension(path):
            return ToolResult(
                success=False,
                error=f"Расширение файла не разрешено: {Path(path).suffix}"
            )
        
        # Проверка размера контента
        if content and len(content.encode('utf-8')) > self.max_file_size_mb * 1024 * 1024:
            return ToolResult(
                success=False,
                error=f"Контент слишком большой (лимит: {self.max_file_size_mb}MB)"
            )
        
        return ToolResult(success=True, data={"message": "Валидация пройдена"})

    def _is_allowed_extension(self, path: str) -> bool:
        """Проверка разрешенного расширения файла"""
        file_path = Path(path)
        extension = file_path.suffix.lower()
        
        # Блокированные расширения имеют приоритет
        if extension in self.blocked_extensions:
            return False
        
        # Если нет расширения, разрешаем
        if not extension:
            return True
        
        # Проверяем разрешенные расширения
        return extension in self.allowed_extensions

    def _health_check(self, **kwargs) -> ToolResult:
        """Проверка здоровья системы"""
        try:
            checks = {
                "system_accessible": True,
                "temp_writable": False,
                "psutil_available": PSUTIL_AVAILABLE,
                "disk_space_ok": False,
                "memory_ok": False
            }
            
            # Проверка записи в temp
            try:
                temp_file = tempfile.NamedTemporaryFile(delete=True)
                temp_file.close()
                checks["temp_writable"] = True
            except Exception:
                pass
            
            # Проверки с psutil
            if PSUTIL_AVAILABLE:
                # Проверка места на диске
                disk_usage = psutil.disk_usage('/')
                disk_free_percent = (disk_usage.free / disk_usage.total) * 100
                checks["disk_space_ok"] = disk_free_percent > 10  # >10% свободно
                
                # Проверка памяти
                memory = psutil.virtual_memory()
                checks["memory_ok"] = memory.percent < 90  # <90% использовано
            
            all_checks_passed = all(checks.values())
            
            logger.info(f"🏥 Health check: {'✅ OK' if all_checks_passed else '⚠️ ISSUES'}")
            
            return ToolResult(
                success=True,
                data={
                    "message": "Health check завершен",
                    "status": "healthy" if all_checks_passed else "issues_detected",
                    "checks": checks,
                    "all_passed": all_checks_passed
                }
            )
            
        except Exception as e:
            logger.error(f"Ошибка health check: {e}")
            return ToolResult(success=False, error=str(e)) 