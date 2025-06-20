"""
🚀 SuperSystemTool - Объединение всех системных инструментов KittyCore 3.0

Революционный инструмент, объединяющий лучшие возможности:
- SystemTool (1946 строк): полная системная информация + файлы + мониторинг
- SystemMonitoringTool (823 строки): продвинутый мониторинг + network
- system_tools.py (594 строки): FileManager + SystemTools
- enhanced_system_tools.py (460 строк): безопасные операции

ИТОГО: 3823 строки → 2500 строк SuperSystemTool
Экономия: 1323 строки (35% оптимизация)
"""

import os
import subprocess
import shutil
import platform
import time
import threading
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Union
from loguru import logger

from .base_tool import Tool, ToolResult

# ========================================
# 📊 DATACLASSES - ОБЪЕДИНЁННЫЕ СТРУКТУРЫ
# ========================================

@dataclass
class SystemInfo:
    """Полная информация о системе (лучшее из всех инструментов)"""
    platform: str
    platform_release: str  
    platform_version: str
    architecture: str
    hostname: str
    username: str
    processor: str
    python_version: str
    cpu_count: int
    memory_total_gb: float
    disk_total_gb: float
    uptime_hours: float
    boot_time: str
    load_average: List[float]

@dataclass
class ResourceUsage:
    """Использование ресурсов (объединение SystemTool + SystemMonitoringTool)"""
    cpu_percent: float
    cpu_per_core: List[float]
    memory_percent: float
    memory_available_gb: float
    memory_used_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_io: Dict[str, int]
    top_processes: List[Dict[str, Any]]
    load_average: List[float]

@dataclass
class ProcessInfo:
    """Информация о процессе (лучшая версия)"""
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    create_time: float
    cmdline: List[str]
    username: str
    num_threads: int
    parent_pid: int

@dataclass
class FileInfo:
    """Информация о файле (безопасная версия)"""
    path: str
    size: int
    modified_time: str
    is_directory: bool
    permissions: str
    owner: str
    extension: str
    is_safe: bool
    encoding: Optional[str] = None

# ========================================
# 🚀 SUPERSYSTEMTOOL - ОБЪЕДИНЁННЫЙ ИНСТРУМЕНТ
# ========================================

class SuperSystemTool(Tool):
    """
    🚀 SuperSystemTool - Мощнейший системный инструмент KittyCore 3.0
    
    Объединяет ВСЕ возможности системных инструментов:
    - 🖥️ Системная информация (CPU, память, диски, сеть)
    - 📂 Управление процессами (список, информация, завершение)
    - 📁 Файловые операции (безопасные + расширенные)
    - 🛡️ Безопасность (валидация, проверки)
    - 📊 Мониторинг (реального времени + метрики)
    - ⚡ Команды (выполнение + сервисы)
    """
    
    def __init__(self):
        super().__init__(
            name="super_system_tool",
            description="Мощнейший системный инструмент - объединение всех системных возможностей"
        )
        
        # Кеширование для производительности
        self._cache = {}
        self._cache_timeout = 5.0
        
        # Мониторинг
        self._monitoring_active = False
        self._monitoring_thread = None
        self._monitoring_data = []
        self._max_monitoring_records = 1000
        
        # Безопасность файлов
        self.allowed_extensions = {
            '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml',
            '.xml', '.csv', '.log', '.sh', '.bat', '.ps1', '.cfg', '.conf', '.ini'
        }
        self.max_file_size_mb = 100
        self.max_output_size = 50000
        
        # Безопасные директории
        self.safe_directories = {'/tmp', '/var/tmp', os.path.expanduser('~')}
        
        logger.info("🚀 SuperSystemTool инициализирован - объединение всех системных возможностей")

    def get_schema(self) -> Dict[str, Any]:
        """Схема инструмента с ВСЕМИ действиями"""
        return {
            "name": self.name,
            "description": self.description,
            "actions": {
                # 🖥️ СИСТЕМНАЯ ИНФОРМАЦИЯ
                "get_system_info": {"description": "Полная информация о системе"},
                "get_resource_usage": {"description": "Текущее использование ресурсов"},
                "get_cpu_info": {"description": "Детальная информация о CPU"},
                "get_memory_info": {"description": "Информация о памяти"},
                "get_disk_info": {"description": "Информация о дисках", "parameters": {"path": "str"}},
                "get_network_info": {"description": "Информация о сетевых интерфейсах"},
                "health_check": {"description": "Проверка состояния системы"},
                
                # 📂 ПРОЦЕССЫ
                "get_processes": {"description": "Список процессов", "parameters": {"limit": "int", "process_name": "str"}},
                "get_process_info": {"description": "Информация о процессе", "parameters": {"pid": "int"}},
                "kill_process": {"description": "Завершить процесс", "parameters": {"pid": "int", "force": "bool"}},
                "run_command": {"description": "Выполнить команду", "parameters": {"command": "str", "timeout": "int"}},
                "check_service_status": {"description": "Статус сервиса", "parameters": {"service_name": "str"}},
                
                # 📁 ФАЙЛОВЫЕ ОПЕРАЦИИ (БЕЗОПАСНЫЕ)
                "safe_file_create": {"description": "Безопасное создание файла", "parameters": {"path": "str", "content": "str", "encoding": "str"}},
                "safe_file_read": {"description": "Безопасное чтение файла", "parameters": {"path": "str", "encoding": "str", "max_size": "int"}},
                "safe_file_write": {"description": "Безопасная запись файла", "parameters": {"path": "str", "content": "str", "encoding": "str"}},
                "safe_file_delete": {"description": "Безопасное удаление файла", "parameters": {"path": "str", "force": "bool"}},
                "safe_file_list": {"description": "Безопасный список файлов", "parameters": {"path": "str", "recursive": "bool"}},
                
                # 📁 РАСШИРЕННЫЕ ФАЙЛОВЫЕ ОПЕРАЦИИ
                "file_info": {"description": "Детальная информация о файле", "parameters": {"path": "str"}},
                "file_exists": {"description": "Проверка существования файла", "parameters": {"path": "str"}},
                "copy_file": {"description": "Копирование файла", "parameters": {"path": "str", "destination": "str"}},
                "move_file": {"description": "Перемещение файла", "parameters": {"path": "str", "destination": "str"}},
                "create_directory": {"description": "Создание директории", "parameters": {"path": "str"}},
                "delete_directory": {"description": "Удаление директории", "parameters": {"path": "str", "force": "bool"}},
                
                # 🛡️ БЕЗОПАСНОСТЬ И ВАЛИДАЦИЯ  
                "validate_file_path": {"description": "Валидация пути файла", "parameters": {"path": "str"}},
                "check_file_safety": {"description": "Проверка безопасности файла", "parameters": {"path": "str"}},
                "scan_directory_safety": {"description": "Сканирование безопасности директории", "parameters": {"path": "str", "recursive": "bool"}},
                
                # 📊 МОНИТОРИНГ
                "start_monitoring": {"description": "Запуск мониторинга", "parameters": {"interval": "float", "max_records": "int"}},
                "stop_monitoring": {"description": "Остановка мониторинга"},
                "get_monitoring_data": {"description": "Получение данных мониторинга"},
                "get_system_metrics": {"description": "Ключевые метрики системы"},
                "check_system_health": {"description": "Проверка здоровья системы"}
            }
        }

    def execute(self, action: str, **kwargs) -> ToolResult:
        """🚀 Главный метод выполнения - обрабатывает ВСЕ действия"""
        try:
            # 🖥️ СИСТЕМНАЯ ИНФОРМАЦИЯ
            if action == "get_system_info":
                return self._get_system_info()
            elif action == "get_resource_usage":
                return self._get_resource_usage()
            elif action == "get_cpu_info":
                return self._get_cpu_info()
            elif action == "get_memory_info":
                return self._get_memory_info()
            elif action == "get_disk_info":
                return self._get_disk_info(**kwargs)
            elif action == "get_network_info":
                return self._get_network_info()
            elif action == "health_check":
                return self._health_check()
                
            # 📂 ПРОЦЕССЫ
            elif action == "get_processes":
                return self._get_processes(**kwargs)
            elif action == "get_process_info":
                return self._get_process_info(**kwargs)
            elif action == "kill_process":
                return self._kill_process(**kwargs)
            elif action == "run_command":
                return self._run_command(**kwargs)
            elif action == "check_service_status":
                return self._check_service_status(**kwargs)
                
            # 📁 БЕЗОПАСНЫЕ ФАЙЛОВЫЕ ОПЕРАЦИИ
            elif action == "safe_file_create":
                return self._safe_file_create(**kwargs)
            elif action == "safe_file_read":
                return self._safe_file_read(**kwargs)
            elif action == "safe_file_write":
                return self._safe_file_write(**kwargs)
            elif action == "safe_file_delete":
                return self._safe_file_delete(**kwargs)
            elif action == "safe_file_list":
                return self._safe_file_list(**kwargs)
                
            # 📁 РАСШИРЕННЫЕ ФАЙЛОВЫЕ ОПЕРАЦИИ
            elif action == "file_info":
                return self._get_file_info(**kwargs)
            elif action == "file_exists":
                return self._file_exists(**kwargs)
            elif action == "copy_file":
                return self._copy_file(**kwargs)
            elif action == "move_file":
                return self._move_file(**kwargs)
            elif action == "create_directory":
                return self._create_directory(**kwargs)
            elif action == "delete_directory":
                return self._delete_directory(**kwargs)
                
            # 🛡️ БЕЗОПАСНОСТЬ
            elif action == "validate_file_path":
                return self._validate_file_path(**kwargs)
            elif action == "check_file_safety":
                return self._check_file_safety(**kwargs)
            elif action == "scan_directory_safety":
                return self._scan_directory_safety(**kwargs)
                
            # 📊 МОНИТОРИНГ
            elif action == "start_monitoring":
                return self._start_monitoring(**kwargs)
            elif action == "stop_monitoring":
                return self._stop_monitoring()
            elif action == "get_monitoring_data":
                return self._get_monitoring_data()
            elif action == "get_system_metrics":
                return self._get_system_metrics()
            elif action == "check_system_health":
                return self._check_system_health()
            else:
                return ToolResult(
                    success=False,
                    error=f"Неизвестное действие: {action}. Доступно {len(self.get_schema()['actions'])} действий"
                )
                
        except Exception as e:
            logger.error(f"❌ Ошибка SuperSystemTool {action}: {e}")
            return ToolResult(
                success=False,
                error=f"Ошибка выполнения {action}: {str(e)}"
            )

    # ========================================
    # 🖥️ СИСТЕМНАЯ ИНФОРМАЦИЯ (ЛУЧШИЕ МЕТОДЫ)
    # ========================================
    
    def _get_cached_or_compute(self, key: str, compute_func, ttl: float = None) -> Any:
        """Умное кеширование для производительности"""
        now = time.time()
        ttl = ttl or self._cache_timeout
        
        if key in self._cache:
            data, timestamp = self._cache[key]
            if now - timestamp < ttl:
                return data
        
        # Вычисляем новые данные
        data = compute_func()
        self._cache[key] = (data, now)
        return data

    def _get_system_info(self) -> ToolResult:
        """🖥️ Полная информация о системе (лучшая версия)"""
        try:
            def compute_system_info():
                boot_time = psutil.boot_time()
                uptime_seconds = time.time() - boot_time
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Load average (только для Unix)
                try:
                    load_avg = list(os.getloadavg())
                except (OSError, AttributeError):
                    load_avg = [0.0, 0.0, 0.0]
                
                return SystemInfo(
                    platform=platform.system(),
                    platform_release=platform.release(),
                    platform_version=platform.version(),
                    architecture=platform.machine(),
                    hostname=platform.node(),
                    username=os.getenv('USER', os.getenv('USERNAME', 'unknown')),
                    processor=platform.processor() or "Unknown",
                    python_version=platform.python_version(),
                    cpu_count=psutil.cpu_count(),
                    memory_total_gb=round(memory.total / (1024**3), 2),
                    disk_total_gb=round(disk.total / (1024**3), 2),
                    uptime_hours=round(uptime_seconds / 3600, 2),
                    boot_time=datetime.fromtimestamp(boot_time).isoformat(),
                    load_average=load_avg
                )
            
            system_info = self._get_cached_or_compute("system_info", compute_system_info, ttl=60.0)
            
            return ToolResult(
                success=True,
                data={
                    "system_info": asdict(system_info),
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения информации о системе: {str(e)}"
            )

    def _get_resource_usage(self) -> ToolResult:
        """📊 Текущее использование ресурсов (расширенная версия)"""
        try:
            def compute_resource_usage():
                # CPU информация
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
                
                # Память
                memory = psutil.virtual_memory()
                
                # Диск
                disk = psutil.disk_usage('/')
                
                # Сеть
                net_io = psutil.net_io_counters()
                network_io = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                    "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2)
                }
                
                # Load average
                try:
                    load_avg = list(os.getloadavg())
                except (OSError, AttributeError):
                    load_avg = [0.0, 0.0, 0.0]
                
                # Топ процессов по CPU
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        pinfo = proc.info
                        if pinfo['cpu_percent'] and pinfo['cpu_percent'] > 0:
                            processes.append({
                                'pid': pinfo['pid'],
                                'name': pinfo['name'],
                                'cpu_percent': pinfo['cpu_percent'],
                                'memory_percent': round(pinfo['memory_percent'], 2)
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Сортируем по CPU
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
                
                return ResourceUsage(
                    cpu_percent=cpu_percent,
                    cpu_per_core=cpu_per_core,
                    memory_percent=memory.percent,
                    memory_available_gb=round(memory.available / (1024**3), 2),
                    memory_used_gb=round(memory.used / (1024**3), 2),
                    disk_usage_percent=round(disk.used / disk.total * 100, 2),
                    disk_free_gb=round(disk.free / (1024**3), 2),
                    network_io=network_io,
                    top_processes=processes[:10],
                    load_average=load_avg
                )
            
            resource_usage = self._get_cached_or_compute("resource_usage", compute_resource_usage, ttl=2.0)
            
            return ToolResult(
                success=True,
                data={
                    "resource_usage": asdict(resource_usage),
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения использования ресурсов: {str(e)}"
            )

    def _get_cpu_info(self) -> ToolResult:
        """🖥️ Детальная информация о CPU"""
        try:
            def compute_cpu_info():
                cpu_freq = psutil.cpu_freq()
                cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
                
                # Load average
                try:
                    load_avg = list(os.getloadavg())
                except (OSError, AttributeError):
                    load_avg = [0.0, 0.0, 0.0]
                
                return {
                    "physical_cores": psutil.cpu_count(logical=False),
                    "logical_cores": psutil.cpu_count(logical=True),
                    "max_frequency": round(cpu_freq.max, 2) if cpu_freq else 0,
                    "min_frequency": round(cpu_freq.min, 2) if cpu_freq else 0,
                    "current_frequency": round(cpu_freq.current, 2) if cpu_freq else 0,
                    "usage_percent": round(psutil.cpu_percent(interval=1), 2),
                    "usage_per_core": [round(p, 2) for p in cpu_percent],
                    "load_average": load_avg
                }
            
            cpu_info = self._get_cached_or_compute("cpu_info", compute_cpu_info, ttl=10.0)
            
            return ToolResult(
                success=True,
                data={
                    "cpu_info": cpu_info,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения информации о CPU: {str(e)}"
            )

    def _get_memory_info(self) -> ToolResult:
        """💾 Информация о памяти"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_info = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "percent": memory.percent,
                "swap_total_gb": round(swap.total / (1024**3), 2),
                "swap_used_gb": round(swap.used / (1024**3), 2),
                "swap_free_gb": round(swap.free / (1024**3), 2),
                "swap_percent": swap.percent
            }
            
            return ToolResult(
                success=True,
                data={
                    "memory_info": memory_info,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения информации о памяти: {str(e)}"
            )

    def _get_disk_info(self, path: str = "/") -> ToolResult:
        """💿 Информация о дисках"""
        try:
            disk_usage = psutil.disk_usage(path)
            disk_partitions = psutil.disk_partitions()
            
            disk_info = {
                "path": path,
                "total_gb": round(disk_usage.total / (1024**3), 2),
                "used_gb": round(disk_usage.used / (1024**3), 2),
                "free_gb": round(disk_usage.free / (1024**3), 2),
                "percent": round(disk_usage.used / disk_usage.total * 100, 2),
                "partitions": []
            }
            
            for partition in disk_partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    disk_info["partitions"].append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": round(partition_usage.total / (1024**3), 2),
                        "used_gb": round(partition_usage.used / (1024**3), 2),
                        "free_gb": round(partition_usage.free / (1024**3), 2),
                        "percent": round(partition_usage.used / partition_usage.total * 100, 2)
                    })
                except (PermissionError, OSError):
                    continue
            
            return ToolResult(
                success=True,
                data={
                    "disk_info": disk_info,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения информации о дисках: {str(e)}"
            )

    def _get_network_info(self) -> ToolResult:
        """🌐 Информация о сетевых интерфейсах"""
        try:
            net_interfaces = psutil.net_if_addrs()
            net_stats = psutil.net_if_stats()
            net_io = psutil.net_io_counters(pernic=True)
            
            interfaces = []
            
            for interface, addrs in net_interfaces.items():
                interface_info = {
                    "interface": interface,
                    "addresses": [],
                    "is_up": False,
                    "speed": 0,
                    "bytes_sent": 0,
                    "bytes_recv": 0,
                    "packets_sent": 0,
                    "packets_recv": 0
                }
                
                # Адреса
                for addr in addrs:
                    interface_info["addresses"].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    })
                
                # Статистика интерфейса
                if interface in net_stats:
                    stats = net_stats[interface]
                    interface_info["is_up"] = stats.isup
                    interface_info["speed"] = stats.speed
                
                # IO статистика
                if interface in net_io:
                    io = net_io[interface]
                    interface_info.update({
                        "bytes_sent": io.bytes_sent,
                        "bytes_recv": io.bytes_recv,
                        "packets_sent": io.packets_sent,
                        "packets_recv": io.packets_recv,
                        "bytes_sent_mb": round(io.bytes_sent / (1024**2), 2),
                        "bytes_recv_mb": round(io.bytes_recv / (1024**2), 2)
                    })
                
                interfaces.append(interface_info)
            
            return ToolResult(
                success=True,
                data={
                    "network_info": {
                        "interfaces": interfaces,
                        "total_interfaces": len(interfaces),
                        "active_interfaces": len([i for i in interfaces if i["is_up"]])
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения информации о сети: {str(e)}"
            )

    # ========================================
    # 📂 УПРАВЛЕНИЕ ПРОЦЕССАМИ
    # ========================================

    def _get_processes(self, process_name: Optional[str] = None, limit: int = 20) -> ToolResult:
        """📂 Список процессов"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'memory_info', 'create_time', 'cmdline', 'username', 'num_threads', 'ppid']):
                try:
                    pinfo = proc.info
                    
                    # Фильтр по имени
                    if process_name and process_name.lower() not in pinfo['name'].lower():
                        continue
                    
                    process_data = {
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'status': pinfo['status'],
                        'cpu_percent': pinfo['cpu_percent'] or 0,
                        'memory_percent': round(pinfo['memory_percent'] or 0, 2),
                        'memory_mb': round((pinfo['memory_info'].rss if pinfo['memory_info'] else 0) / (1024**2), 2),
                        'create_time': pinfo['create_time'],
                        'cmdline': ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else '',
                        'username': pinfo['username'] or 'unknown',
                        'num_threads': pinfo['num_threads'] or 0,
                        'parent_pid': pinfo['ppid'] or 0
                    }
                    
                    processes.append(process_data)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Сортировка по CPU
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            # Ограничение
            if limit > 0:
                processes = processes[:limit]
            
            return ToolResult(
                success=True,
                data={
                    "processes": processes,
                    "total_processes": len(processes),
                    "filter": process_name,
                    "limit": limit,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения списка процессов: {str(e)}"
            )

    def _get_process_info(self, pid: int) -> ToolResult:
        """📂 Детальная информация о процессе"""
        try:
            proc = psutil.Process(pid)
            
            # Собираем полную информацию
            process_info = {
                'pid': proc.pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(),
                'memory_percent': round(proc.memory_percent(), 2),
                'memory_info': {
                    'rss_mb': round(proc.memory_info().rss / (1024**2), 2),
                    'vms_mb': round(proc.memory_info().vms / (1024**2), 2)
                },
                'create_time': proc.create_time(),
                'create_time_formatted': datetime.fromtimestamp(proc.create_time()).isoformat(),
                'cmdline': proc.cmdline(),
                'cwd': proc.cwd() if hasattr(proc, 'cwd') else None,
                'username': proc.username(),
                'num_threads': proc.num_threads(),
                'parent_pid': proc.ppid(),
                'children': [child.pid for child in proc.children()],
                'connections': []
            }
            
            # Сетевые соединения (опционально)
            try:
                connections = proc.connections()
                for conn in connections[:10]:  # Ограничиваем до 10
                    process_info['connections'].append({
                        'fd': conn.fd,
                        'family': str(conn.family),
                        'type': str(conn.type),
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        'status': conn.status
                    })
            except (psutil.AccessDenied, AttributeError):
                pass
            
            return ToolResult(
                success=True,
                data={
                    "process_info": process_info,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except psutil.NoSuchProcess:
            return ToolResult(
                success=False,
                error=f"Процесс с PID {pid} не найден"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения информации о процессе {pid}: {str(e)}"
            )

    def _kill_process(self, pid: int, force: bool = False) -> ToolResult:
        """⚡ Завершение процесса"""
        try:
            proc = psutil.Process(pid)
            process_name = proc.name()
            
            if force:
                proc.kill()  # SIGKILL
                method = "KILL"
            else:
                proc.terminate()  # SIGTERM
                method = "TERMINATE"
            
            # Ожидаем завершения
            try:
                proc.wait(timeout=5)
                status = "completed"
            except psutil.TimeoutExpired:
                status = "timeout"
            
            return ToolResult(
                success=True,
                data={
                    "pid": pid,
                    "process_name": process_name,
                    "method": method,
                    "status": status,
                    "message": f"Процесс {process_name} (PID: {pid}) завершён методом {method}",
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except psutil.NoSuchProcess:
            return ToolResult(
                success=False,
                error=f"Процесс с PID {pid} не найден"
            )
        except psutil.AccessDenied:
            return ToolResult(
                success=False,
                error=f"Недостаточно прав для завершения процесса {pid}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка завершения процесса {pid}: {str(e)}"
            )

    def _run_command(self, command: str, timeout: int = 30) -> ToolResult:
        """⚡ Выполнение команды"""
        try:
            start_time = time.time()
            
            # Выполняем команду
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = round(time.time() - start_time, 2)
            
            return ToolResult(
                success=True,
                data={
                    "command": command,
                    "return_code": result.returncode,
                    "stdout": result.stdout[:self.max_output_size] if result.stdout else "",
                    "stderr": result.stderr[:self.max_output_size] if result.stderr else "",
                    "execution_time_seconds": execution_time,
                    "timeout": timeout,
                    "success": result.returncode == 0,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error=f"Команда превысила timeout {timeout} секунд"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка выполнения команды: {str(e)}"
            )

    def _check_service_status(self, service_name: str) -> ToolResult:
        """⚡ Проверка статуса сервиса"""
        try:
            # Пробуем systemctl для systemd
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', service_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                status = result.stdout.strip()
                is_active = result.returncode == 0
                
                # Дополнительная информация
                info_result = subprocess.run(
                    ['systemctl', 'status', service_name, '--no-pager', '-l'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                return ToolResult(
                    success=True,
                    data={
                        "service_name": service_name,
                        "status": status,
                        "is_active": is_active,
                        "detailed_status": info_result.stdout[:self.max_output_size],
                        "method": "systemctl",
                        "timestamp": datetime.now().isoformat(),
                        "source": "SuperSystemTool"
                    }
                )
                
            except (FileNotFoundError, subprocess.TimeoutExpired):
                # Fallback - поиск процесса по имени
                found_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'status']):
                    try:
                        if service_name.lower() in proc.info['name'].lower():
                            found_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'status': proc.info['status']
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                return ToolResult(
                    success=True,
                    data={
                        "service_name": service_name,
                        "status": "active" if found_processes else "inactive",
                        "is_active": bool(found_processes),
                        "processes": found_processes,
                        "method": "process_search",
                        "timestamp": datetime.now().isoformat(),
                        "source": "SuperSystemTool"
                    }
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка проверки статуса сервиса {service_name}: {str(e)}"
            )

    # ========================================
    # 📁 БЕЗОПАСНЫЕ ФАЙЛОВЫЕ ОПЕРАЦИИ
    # ========================================

    def _is_safe_extension(self, file_path: str) -> bool:
        """🛡️ Проверка безопасного расширения файла"""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.allowed_extensions

    def _is_safe_path(self, path: str) -> tuple[bool, str]:
        """🛡️ Проверка безопасности пути"""
        try:
            abs_path = Path(path).resolve()
            
            # Проверка на опасные пути
            dangerous_paths = {'/etc', '/bin', '/sbin', '/usr/bin', '/usr/sbin', '/boot', '/proc', '/sys'}
            
            for dangerous in dangerous_paths:
                if str(abs_path).startswith(dangerous):
                    return False, f"Путь {path} находится в опасной директории {dangerous}"
            
            return True, "Путь безопасен"
            
        except Exception as e:
            return False, f"Ошибка проверки пути: {str(e)}"

    def _safe_file_create(self, path: str, content: str = "", encoding: str = "utf-8") -> ToolResult:
        """📁 Безопасное создание файла"""
        try:
            # Проверки безопасности
            if not path:
                return ToolResult(success=False, error="Путь к файлу обязателен")
            
            is_safe, safety_msg = self._is_safe_path(path)
            if not is_safe:
                return ToolResult(success=False, error=f"Небезопасный путь: {safety_msg}")
            
            if not self._is_safe_extension(path):
                return ToolResult(success=False, error=f"Небезопасное расширение файла: {Path(path).suffix}")
            
            # Проверка размера контента
            if len(content.encode(encoding)) > self.max_file_size_mb * 1024 * 1024:
                return ToolResult(success=False, error=f"Контент слишком большой (лимит: {self.max_file_size_mb}MB)")
            
            # Создание файла
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.info(f"📁 Создан безопасный файл: {path} ({len(content)} символов)")
            
            return ToolResult(
                success=True,
                data={
                    "operation": "safe_file_create",
                    "path": str(file_path.absolute()),
                    "size_bytes": len(content.encode(encoding)),
                    "size_chars": len(content),
                    "encoding": encoding,
                    "is_safe": True,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания файла {path}: {e}")
            return ToolResult(success=False, error=f"Ошибка создания файла: {str(e)}")

    def _safe_file_read(self, path: str, encoding: str = "utf-8", max_size: int = None) -> ToolResult:
        """📖 Безопасное чтение файла"""
        try:
            if not path:
                return ToolResult(success=False, error="Путь к файлу обязателен")
            
            file_path = Path(path)
            
            # Проверки существования
            if not file_path.exists():
                return ToolResult(success=False, error=f"Файл не существует: {path}")
            
            if not file_path.is_file():
                return ToolResult(success=False, error=f"Путь не является файлом: {path}")
            
            # Проверки безопасности
            is_safe, safety_msg = self._is_safe_path(path)
            if not is_safe:
                return ToolResult(success=False, error=f"Небезопасный путь: {safety_msg}")
            
            if not self._is_safe_extension(path):
                return ToolResult(success=False, error=f"Небезопасное расширение файла: {file_path.suffix}")
            
            # Проверка размера файла
            file_size = file_path.stat().st_size
            max_file_size = max_size or (self.max_file_size_mb * 1024 * 1024)
            
            if file_size > max_file_size:
                return ToolResult(
                    success=False,
                    error=f"Файл слишком большой: {file_size} байт (лимит: {max_file_size})"
                )
            
            # Чтение файла
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Ограничение вывода
            truncated = False
            if len(content) > self.max_output_size:
                content = content[:self.max_output_size] + "\n... (контент обрезан)"
                truncated = True
            
            logger.info(f"📖 Прочитан безопасный файл: {path} ({file_size} байт)")
            
            return ToolResult(
                success=True,
                data={
                    "operation": "safe_file_read",
                    "path": str(file_path.absolute()),
                    "content": content,
                    "size_bytes": file_size,
                    "size_chars": len(content),
                    "encoding": encoding,
                    "truncated": truncated,
                    "is_safe": True,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка чтения файла {path}: {e}")
            return ToolResult(success=False, error=f"Ошибка чтения файла: {str(e)}")

    def _safe_file_write(self, path: str, content: str, encoding: str = "utf-8") -> ToolResult:
        """✏️ Безопасная запись файла"""
        try:
            # Используем safe_file_create для записи (она включает все проверки)
            return self._safe_file_create(path, content, encoding)
            
        except Exception as e:
            logger.error(f"❌ Ошибка записи файла {path}: {e}")
            return ToolResult(success=False, error=f"Ошибка записи файла: {str(e)}")

    def _safe_file_delete(self, path: str, force: bool = False) -> ToolResult:
        """🗑️ Безопасное удаление файла"""
        try:
            if not path:
                return ToolResult(success=False, error="Путь к файлу обязателен")
            
            file_path = Path(path)
            
            # Проверки существования
            if not file_path.exists():
                return ToolResult(success=False, error=f"Файл не существует: {path}")
            
            if not file_path.is_file():
                return ToolResult(success=False, error=f"Путь не является файлом: {path}")
            
            # Проверки безопасности (если не force)
            if not force:
                is_safe, safety_msg = self._is_safe_path(path)
                if not is_safe:
                    return ToolResult(success=False, error=f"Небезопасный путь: {safety_msg}")
                
                if not self._is_safe_extension(path):
                    return ToolResult(success=False, error=f"Небезопасное расширение файла: {file_path.suffix}")
            
            # Получаем информацию перед удалением
            file_size = file_path.stat().st_size
            
            # Удаление
            file_path.unlink()
            
            logger.info(f"🗑️ Удален безопасный файл: {path} ({file_size} байт)")
            
            return ToolResult(
                success=True,
                data={
                    "operation": "safe_file_delete",
                    "path": str(file_path.absolute()),
                    "size_bytes": file_size,
                    "force": force,
                    "deleted": True,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка удаления файла {path}: {e}")
            return ToolResult(success=False, error=f"Ошибка удаления файла: {str(e)}")

    def _safe_file_list(self, path: str = ".", recursive: bool = False) -> ToolResult:
        """📋 Безопасный список файлов"""
        try:
            dir_path = Path(path)
            
            # Проверки существования
            if not dir_path.exists():
                return ToolResult(success=False, error=f"Директория не существует: {path}")
            
            if not dir_path.is_dir():
                return ToolResult(success=False, error=f"Путь не является директорией: {path}")
            
            # Проверки безопасности
            is_safe, safety_msg = self._is_safe_path(path)
            if not is_safe:
                return ToolResult(success=False, error=f"Небезопасный путь: {safety_msg}")
            
            items = []
            
            try:
                if recursive:
                    files = dir_path.rglob("*")
                else:
                    files = dir_path.iterdir()
                
                for item in files:
                    try:
                        stat_info = item.stat()
                        item_info = {
                            "name": item.name,
                            "path": str(item.absolute()),
                            "type": "file" if item.is_file() else "directory",
                            "size_bytes": stat_info.st_size if item.is_file() else None,
                            "size_mb": round(stat_info.st_size / (1024**2), 2) if item.is_file() else None,
                            "modified_time": stat_info.st_mtime,
                            "modified_formatted": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                            "extension": item.suffix if item.is_file() else None,
                            "is_safe": self._is_safe_extension(str(item)) if item.is_file() else True
                        }
                        items.append(item_info)
                        
                    except (PermissionError, OSError):
                        # Пропускаем недоступные файлы
                        continue
                
            except PermissionError:
                return ToolResult(success=False, error=f"Недостаточно прав для чтения директории: {path}")
            
            # Сортировка: сначала директории, потом файлы
            items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
            
            logger.info(f"📋 Получен список: {len(items)} элементов в {path}")
            
            return ToolResult(
                success=True,
                data={
                    "operation": "safe_file_list",
                    "path": str(dir_path.absolute()),
                    "items": items,
                    "total_items": len(items),
                    "files_count": len([i for i in items if i["type"] == "file"]),
                    "directories_count": len([i for i in items if i["type"] == "directory"]),
                    "safe_files_count": len([i for i in items if i["type"] == "file" and i["is_safe"]]),
                    "recursive": recursive,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка файлов {path}: {e}")
            return ToolResult(success=False, error=f"Ошибка получения списка файлов: {str(e)}")

    # ========================================
    # 📁 РАСШИРЕННЫЕ ФАЙЛОВЫЕ ОПЕРАЦИИ
    # ========================================

    def _get_file_info(self, path: str) -> ToolResult:
        """📄 Детальная информация о файле"""
        try:
            if not path:
                return ToolResult(success=False, error="Путь к файлу обязателен")
            
            file_path = Path(path)
            
            if not file_path.exists():
                return ToolResult(success=False, error=f"Файл не существует: {path}")
            
            stat_info = file_path.stat()
            is_file = file_path.is_file()
            is_dir = file_path.is_dir()
            
            # Базовая информация
            file_info = {
                "path": str(file_path.absolute()),
                "name": file_path.name,
                "parent": str(file_path.parent),
                "is_file": is_file,
                "is_directory": is_dir,
                "is_symlink": file_path.is_symlink(),
                "exists": True,
                "size_bytes": stat_info.st_size,
                "size_mb": round(stat_info.st_size / (1024**2), 4),
                "modified_time": stat_info.st_mtime,
                "modified_formatted": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "created_time": stat_info.st_ctime,
                "created_formatted": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "accessed_time": stat_info.st_atime,
                "accessed_formatted": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                "permissions": oct(stat_info.st_mode)[-3:],
                "owner_uid": stat_info.st_uid,
                "group_gid": stat_info.st_gid
            }
            
            # Дополнительная информация для файлов
            if is_file:
                file_info.update({
                    "extension": file_path.suffix,
                    "stem": file_path.stem,
                    "is_safe": self._is_safe_extension(path),
                    "mime_type": self._get_mime_type(file_path)
                })
            
            # Дополнительная информация для директорий
            if is_dir:
                try:
                    contents = list(file_path.iterdir())
                    file_info.update({
                        "contents_count": len(contents),
                        "files_count": len([f for f in contents if f.is_file()]),
                        "directories_count": len([f for f in contents if f.is_dir()])
                    })
                except PermissionError:
                    file_info.update({
                        "contents_count": "Permission denied",
                        "files_count": "Permission denied",
                        "directories_count": "Permission denied"
                    })
            
            return ToolResult(
                success=True,
                data={
                    "file_info": file_info,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения информации о файле {path}: {str(e)}"
            )

    def _get_mime_type(self, file_path: Path) -> str:
        """🔍 Определение MIME типа файла"""
        try:
            import mimetypes
            mime_type, _ = mimetypes.guess_type(str(file_path))
            return mime_type or "unknown"
        except Exception:
            return "unknown"

    def _file_exists(self, path: str) -> ToolResult:
        """✅ Проверка существования файла"""
        try:
            if not path:
                return ToolResult(success=False, error="Путь к файлу обязателен")
            
            file_path = Path(path)
            exists = file_path.exists()
            
            result_data = {
                "path": str(file_path.absolute()),
                "exists": exists,
                "is_file": file_path.is_file() if exists else False,
                "is_directory": file_path.is_dir() if exists else False,
                "is_symlink": file_path.is_symlink() if exists else False,
                "timestamp": datetime.now().isoformat(),
                "source": "SuperSystemTool"
            }
            
            return ToolResult(success=True, data=result_data)
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка проверки существования файла {path}: {str(e)}"
            )

    def _copy_file(self, path: str, destination: str) -> ToolResult:
        """📋 Копирование файла"""
        try:
            if not path or not destination:
                return ToolResult(success=False, error="Путь источника и назначения обязательны")
            
            source_path = Path(path)
            dest_path = Path(destination)
            
            # Проверки источника
            if not source_path.exists():
                return ToolResult(success=False, error=f"Исходный файл не найден: {path}")
            
            if not source_path.is_file():
                return ToolResult(success=False, error=f"Источник не является файлом: {path}")
            
            # Проверки безопасности
            is_safe_src, safety_msg_src = self._is_safe_path(path)
            if not is_safe_src:
                return ToolResult(success=False, error=f"Небезопасный путь источника: {safety_msg_src}")
            
            is_safe_dst, safety_msg_dst = self._is_safe_path(destination)
            if not is_safe_dst:
                return ToolResult(success=False, error=f"Небезопасный путь назначения: {safety_msg_dst}")
            
            # Создаем директории назначения
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Получаем размер исходного файла
            source_size = source_path.stat().st_size
            
            # Копирование
            shutil.copy2(source_path, dest_path)
            
            # Проверяем успешность копирования
            if dest_path.exists():
                dest_size = dest_path.stat().st_size
                success = (source_size == dest_size)
            else:
                success = False
                dest_size = 0
            
            logger.info(f"📋 Скопирован файл: {path} → {destination} ({source_size} байт)")
            
            return ToolResult(
                success=success,
                data={
                    "operation": "copy_file",
                    "source": str(source_path.absolute()),
                    "destination": str(dest_path.absolute()),
                    "source_size_bytes": source_size,
                    "destination_size_bytes": dest_size,
                    "size_match": source_size == dest_size,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка копирования файла {path}: {e}")
            return ToolResult(success=False, error=f"Ошибка копирования файла: {str(e)}")

    def _move_file(self, path: str, destination: str) -> ToolResult:
        """🚚 Перемещение файла"""
        try:
            if not path or not destination:
                return ToolResult(success=False, error="Путь источника и назначения обязательны")
            
            source_path = Path(path)
            dest_path = Path(destination)
            
            # Проверки источника
            if not source_path.exists():
                return ToolResult(success=False, error=f"Исходный файл не найден: {path}")
            
            if not source_path.is_file():
                return ToolResult(success=False, error=f"Источник не является файлом: {path}")
            
            # Проверки безопасности
            is_safe_src, safety_msg_src = self._is_safe_path(path)
            if not is_safe_src:
                return ToolResult(success=False, error=f"Небезопасный путь источника: {safety_msg_src}")
            
            is_safe_dst, safety_msg_dst = self._is_safe_path(destination)
            if not is_safe_dst:
                return ToolResult(success=False, error=f"Небезопасный путь назначения: {safety_msg_dst}")
            
            # Получаем размер исходного файла
            source_size = source_path.stat().st_size
            
            # Создаем директории назначения
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Перемещение
            shutil.move(str(source_path), str(dest_path))
            
            # Проверяем успешность перемещения
            moved_successfully = dest_path.exists() and not source_path.exists()
            
            logger.info(f"🚚 Перемещен файл: {path} → {destination} ({source_size} байт)")
            
            return ToolResult(
                success=moved_successfully,
                data={
                    "operation": "move_file",
                    "source": str(Path(path).absolute()),
                    "destination": str(dest_path.absolute()),
                    "size_bytes": source_size,
                    "moved_successfully": moved_successfully,
                    "source_exists": source_path.exists(),
                    "destination_exists": dest_path.exists(),
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка перемещения файла {path}: {e}")
            return ToolResult(success=False, error=f"Ошибка перемещения файла: {str(e)}")

    def _create_directory(self, path: str) -> ToolResult:
        """📁 Создание директории"""
        try:
            if not path:
                return ToolResult(success=False, error="Путь к директории обязателен")
            
            dir_path = Path(path)
            
            # Проверки безопасности
            is_safe, safety_msg = self._is_safe_path(path)
            if not is_safe:
                return ToolResult(success=False, error=f"Небезопасный путь: {safety_msg}")
            
            # Создание директории
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Проверяем успешность создания
            success = dir_path.exists() and dir_path.is_dir()
            
            logger.info(f"📁 Создана директория: {path}")
            
            return ToolResult(
                success=success,
                data={
                    "operation": "create_directory",
                    "path": str(dir_path.absolute()),
                    "created": success,
                    "already_existed": dir_path.exists(),
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания директории {path}: {e}")
            return ToolResult(success=False, error=f"Ошибка создания директории: {str(e)}")

    def _delete_directory(self, path: str, force: bool = False) -> ToolResult:
        """🗑️ Удаление директории"""
        try:
            if not path:
                return ToolResult(success=False, error="Путь к директории обязателен")
            
            dir_path = Path(path)
            
            # Проверки существования
            if not dir_path.exists():
                return ToolResult(success=False, error=f"Директория не существует: {path}")
            
            if not dir_path.is_dir():
                return ToolResult(success=False, error=f"Путь не является директорией: {path}")
            
            # Проверки безопасности (если не force)
            if not force:
                is_safe, safety_msg = self._is_safe_path(path)
                if not is_safe:
                    return ToolResult(success=False, error=f"Небезопасный путь: {safety_msg}")
            
            # Подсчитываем содержимое перед удалением
            try:
                contents = list(dir_path.rglob("*"))
                files_count = len([f for f in contents if f.is_file()])
                dirs_count = len([f for f in contents if f.is_dir()])
                total_size = sum(f.stat().st_size for f in contents if f.is_file())
            except PermissionError:
                files_count = dirs_count = total_size = 0
            
            # Удаление
            shutil.rmtree(dir_path)
            
            # Проверяем успешность удаления
            deleted = not dir_path.exists()
            
            logger.info(f"🗑️ Удалена директория: {path} ({files_count} файлов, {dirs_count} папок)")
            
            return ToolResult(
                success=deleted,
                data={
                    "operation": "delete_directory",
                    "path": str(dir_path.absolute()),
                    "deleted": deleted,
                    "force": force,
                    "files_deleted": files_count,
                    "directories_deleted": dirs_count,
                    "total_size_bytes": total_size,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка удаления директории {path}: {e}")
            return ToolResult(success=False, error=f"Ошибка удаления директории: {str(e)}")

    # ========================================
    # 🛡️ БЕЗОПАСНОСТЬ И ВАЛИДАЦИЯ
    # ========================================

    def _validate_file_path(self, path: str) -> ToolResult:
        """🛡️ Валидация пути файла"""
        try:
            if not path:
                return ToolResult(success=False, error="Путь к файлу обязателен")
            
            file_path = Path(path)
            validation_results = {
                "path": path,
                "absolute_path": str(file_path.absolute()),
                "is_valid": True,
                "issues": [],
                "recommendations": []
            }
            
            # Проверка безопасности пути
            is_safe, safety_msg = self._is_safe_path(path)
            if not is_safe:
                validation_results["is_valid"] = False
                validation_results["issues"].append(f"Небезопасный путь: {safety_msg}")
            
            # Проверка расширения файла
            if file_path.suffix and not self._is_safe_extension(path):
                validation_results["issues"].append(f"Небезопасное расширение: {file_path.suffix}")
                validation_results["recommendations"].append(f"Используйте одно из разрешённых расширений: {', '.join(sorted(self.allowed_extensions))}")
            
            # Проверка длины пути
            if len(str(file_path.absolute())) > 255:
                validation_results["issues"].append("Путь слишком длинный (>255 символов)")
                validation_results["recommendations"].append("Сократите путь к файлу")
            
            # Проверка недопустимых символов
            invalid_chars = set(str(file_path)) & {'<', '>', ':', '"', '|', '?', '*'}
            if invalid_chars:
                validation_results["issues"].append(f"Недопустимые символы в пути: {', '.join(invalid_chars)}")
                validation_results["recommendations"].append("Удалите недопустимые символы из пути")
            
            # Проверка существования родительской директории
            if not file_path.parent.exists():
                validation_results["recommendations"].append("Родительская директория не существует и будет создана")
            
            # Финальная валидация
            if validation_results["issues"]:
                validation_results["is_valid"] = False
            
            return ToolResult(
                success=True,
                data={
                    "validation": validation_results,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка валидации пути {path}: {str(e)}"
            )

    def _check_file_safety(self, path: str) -> ToolResult:
        """🛡️ Проверка безопасности файла"""
        try:
            if not path:
                return ToolResult(success=False, error="Путь к файлу обязателен")
            
            file_path = Path(path)
            safety_results = {
                "path": path,
                "is_safe": True,
                "safety_score": 100,  # из 100
                "issues": [],
                "warnings": [],
                "recommendations": []
            }
            
            # Проверка существования файла
            if file_path.exists():
                if file_path.is_file():
                    # Проверка размера файла
                    file_size = file_path.stat().st_size
                    if file_size > self.max_file_size_mb * 1024 * 1024:
                        safety_results["issues"].append(f"Файл слишком большой: {file_size} байт")
                        safety_results["safety_score"] -= 30
                    elif file_size > self.max_file_size_mb * 1024 * 1024 * 0.5:
                        safety_results["warnings"].append(f"Файл довольно большой: {round(file_size/(1024**2), 2)} MB")
                        safety_results["safety_score"] -= 10
                    
                    # Проверка расширения
                    if not self._is_safe_extension(path):
                        safety_results["issues"].append(f"Небезопасное расширение: {file_path.suffix}")
                        safety_results["safety_score"] -= 40
                    
                    # Проверка MIME типа
                    mime_type = self._get_mime_type(file_path)
                    if mime_type.startswith('application/') and mime_type not in ['application/json', 'application/xml']:
                        safety_results["warnings"].append(f"Потенциально небезопасный MIME тип: {mime_type}")
                        safety_results["safety_score"] -= 15
                    
                else:
                    safety_results["warnings"].append("Путь является директорией, а не файлом")
            else:
                safety_results["warnings"].append("Файл не существует")
            
            # Проверка пути
            is_safe_path, path_msg = self._is_safe_path(path)
            if not is_safe_path:
                safety_results["issues"].append(f"Небезопасный путь: {path_msg}")
                safety_results["safety_score"] -= 50
            
            # Рекомендации
            if safety_results["issues"]:
                safety_results["is_safe"] = False
                safety_results["recommendations"].append("Исправьте все обнаруженные проблемы безопасности")
            
            if safety_results["warnings"]:
                safety_results["recommendations"].append("Обратите внимание на предупреждения")
            
            if safety_results["safety_score"] < 70:
                safety_results["is_safe"] = False
                safety_results["recommendations"].append("Рейтинг безопасности слишком низкий")
            
            return ToolResult(
                success=True,
                data={
                    "safety_check": safety_results,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка проверки безопасности файла {path}: {str(e)}"
            )

    def _scan_directory_safety(self, path: str, recursive: bool = False) -> ToolResult:
        """🔍 Сканирование безопасности директории"""
        try:
            if not path:
                return ToolResult(success=False, error="Путь к директории обязателен")
            
            dir_path = Path(path)
            
            if not dir_path.exists():
                return ToolResult(success=False, error=f"Директория не существует: {path}")
            
            if not dir_path.is_dir():
                return ToolResult(success=False, error=f"Путь не является директорией: {path}")
            
            scan_results = {
                "path": path,
                "scanned_files": 0,
                "safe_files": 0,
                "unsafe_files": 0,
                "large_files": 0,
                "unknown_extensions": 0,
                "total_size_bytes": 0,
                "largest_file": None,
                "unsafe_file_list": [],
                "large_file_list": [],
                "unknown_extension_list": [],
                "safety_percentage": 0
            }
            
            try:
                if recursive:
                    files = [f for f in dir_path.rglob("*") if f.is_file()]
                else:
                    files = [f for f in dir_path.iterdir() if f.is_file()]
                
                scan_results["scanned_files"] = len(files)
                
                largest_size = 0
                
                for file_path in files:
                    try:
                        file_size = file_path.stat().st_size
                        scan_results["total_size_bytes"] += file_size
                        
                        # Отслеживаем самый большой файл
                        if file_size > largest_size:
                            largest_size = file_size
                            scan_results["largest_file"] = {
                                "path": str(file_path),
                                "size_bytes": file_size,
                                "size_mb": round(file_size / (1024**2), 2)
                            }
                        
                        # Проверка безопасности расширения
                        if self._is_safe_extension(str(file_path)):
                            scan_results["safe_files"] += 1
                        else:
                            scan_results["unsafe_files"] += 1
                            if file_path.suffix:
                                scan_results["unsafe_file_list"].append({
                                    "path": str(file_path),
                                    "extension": file_path.suffix,
                                    "size_mb": round(file_size / (1024**2), 2)
                                })
                            else:
                                scan_results["unknown_extensions"] += 1
                                scan_results["unknown_extension_list"].append({
                                    "path": str(file_path),
                                    "size_mb": round(file_size / (1024**2), 2)
                                })
                        
                        # Проверка размера
                        if file_size > self.max_file_size_mb * 1024 * 1024 * 0.5:  # 50% от лимита
                            scan_results["large_files"] += 1
                            scan_results["large_file_list"].append({
                                "path": str(file_path),
                                "size_mb": round(file_size / (1024**2), 2),
                                "extension": file_path.suffix
                            })
                        
                    except (PermissionError, OSError):
                        continue
                
                # Вычисляем процент безопасности
                if scan_results["scanned_files"] > 0:
                    scan_results["safety_percentage"] = round(
                        (scan_results["safe_files"] / scan_results["scanned_files"]) * 100, 1
                    )
                
                # Ограничиваем списки для вывода
                scan_results["unsafe_file_list"] = scan_results["unsafe_file_list"][:20]
                scan_results["large_file_list"] = scan_results["large_file_list"][:20]
                scan_results["unknown_extension_list"] = scan_results["unknown_extension_list"][:20]
                
            except PermissionError:
                return ToolResult(success=False, error=f"Недостаточно прав для сканирования директории: {path}")
            
            logger.info(f"🔍 Просканирована директория: {path} ({scan_results['scanned_files']} файлов, {scan_results['safety_percentage']}% безопасных)")
            
            return ToolResult(
                success=True,
                data={
                    "safety_scan": scan_results,
                    "recursive": recursive,
                    "total_size_mb": round(scan_results["total_size_bytes"] / (1024**2), 2),
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка сканирования безопасности {path}: {e}")
            return ToolResult(success=False, error=f"Ошибка сканирования безопасности: {str(e)}")

    # ========================================
    # 📊 МОНИТОРИНГ И HEALTH CHECK
    # ========================================

    def _health_check(self) -> ToolResult:
        """🩺 Проверка здоровья системы"""
        try:
            health_results = {
                "overall_health": "healthy",
                "health_score": 100,  # из 100
                "cpu_status": "good",
                "memory_status": "good", 
                "disk_status": "good",
                "system_status": "good",
                "warnings": [],
                "critical_issues": [],
                "recommendations": []
            }
            
            # Проверка CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                health_results["cpu_status"] = "critical"
                health_results["critical_issues"].append(f"Критическая загрузка CPU: {cpu_percent}%")
                health_results["health_score"] -= 30
            elif cpu_percent > 70:
                health_results["cpu_status"] = "warning"
                health_results["warnings"].append(f"Высокая загрузка CPU: {cpu_percent}%")
                health_results["health_score"] -= 15
            
            # Проверка памяти
            memory = psutil.virtual_memory()
            if memory.percent > 95:
                health_results["memory_status"] = "critical"
                health_results["critical_issues"].append(f"Критическое использование памяти: {memory.percent}%")
                health_results["health_score"] -= 30
            elif memory.percent > 80:
                health_results["memory_status"] = "warning"
                health_results["warnings"].append(f"Высокое использование памяти: {memory.percent}%")
                health_results["health_score"] -= 15
            
            # Проверка дисков
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 95:
                health_results["disk_status"] = "critical"
                health_results["critical_issues"].append(f"Критическое заполнение диска: {disk_percent:.1f}%")
                health_results["health_score"] -= 25
            elif disk_percent > 85:
                health_results["disk_status"] = "warning"
                health_results["warnings"].append(f"Высокое заполнение диска: {disk_percent:.1f}%")
                health_results["health_score"] -= 10
            
            # Проверка системы
            try:
                load_avg = os.getloadavg()[0]  # 1-минутная нагрузка
                cpu_count = psutil.cpu_count()
                if load_avg > cpu_count * 2:
                    health_results["system_status"] = "critical"
                    health_results["critical_issues"].append(f"Критическая системная нагрузка: {load_avg:.2f}")
                    health_results["health_score"] -= 20
                elif load_avg > cpu_count:
                    health_results["system_status"] = "warning"
                    health_results["warnings"].append(f"Высокая системная нагрузка: {load_avg:.2f}")
                    health_results["health_score"] -= 10
            except (OSError, AttributeError):
                pass  # Windows не поддерживает load average
            
            # Определяем общее состояние
            if health_results["critical_issues"]:
                health_results["overall_health"] = "critical"
                health_results["recommendations"].append("🚨 Немедленно устраните критические проблемы")
            elif health_results["warnings"]:
                health_results["overall_health"] = "warning"
                health_results["recommendations"].append("⚠️ Обратите внимание на предупреждения")
            else:
                health_results["overall_health"] = "healthy"
                health_results["recommendations"].append("✅ Система работает нормально")
            
            # Дополнительные рекомендации
            if health_results["health_score"] < 70:
                health_results["recommendations"].append("💡 Рассмотрите оптимизацию системы")
            
            return ToolResult(
                success=True,
                data={
                    "health_check": health_results,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка проверки здоровья системы: {str(e)}"
            )

    def _start_monitoring(self, interval: float = 1.0, max_records: int = None) -> ToolResult:
        """📊 Запуск мониторинга системы"""
        try:
            if self._monitoring_active:
                return ToolResult(
                    success=False,
                    error="Мониторинг уже активен. Сначала остановите текущий мониторинг."
                )
            
            # Настройки мониторинга
            self._monitoring_active = True
            self._monitoring_data.clear()
            if max_records:
                self._max_monitoring_records = max_records
            
            def monitoring_loop():
                """Цикл мониторинга"""
                while self._monitoring_active:
                    try:
                        # Собираем метрики
                        cpu_percent = psutil.cpu_percent(interval=0.1)
                        memory = psutil.virtual_memory()
                        disk = psutil.disk_usage('/')
                        net_io = psutil.net_io_counters()
                        
                        # Создаем запись
                        record = {
                            "timestamp": datetime.now().isoformat(),
                            "cpu_percent": cpu_percent,
                            "memory_percent": memory.percent,
                            "memory_available_gb": round(memory.available / (1024**3), 2),
                            "disk_percent": round((disk.used / disk.total) * 100, 2),
                            "disk_free_gb": round(disk.free / (1024**3), 2),
                            "network_bytes_sent": net_io.bytes_sent,
                            "network_bytes_recv": net_io.bytes_recv
                        }
                        
                        # Добавляем запись
                        self._monitoring_data.append(record)
                        
                        # Ограничиваем количество записей
                        if len(self._monitoring_data) > self._max_monitoring_records:
                            self._monitoring_data.pop(0)
                        
                        time.sleep(interval)
                        
                    except Exception as e:
                        logger.error(f"❌ Ошибка в цикле мониторинга: {e}")
                        time.sleep(5)  # Пауза при ошибке
            
            # Запускаем мониторинг в отдельном потоке
            self._monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
            self._monitoring_thread.start()
            
            logger.info(f"📊 Запущен мониторинг системы (интервал: {interval}с, лимит записей: {self._max_monitoring_records})")
            
            return ToolResult(
                success=True,
                data={
                    "operation": "start_monitoring",
                    "interval_seconds": interval,
                    "max_records": self._max_monitoring_records,
                    "monitoring_active": self._monitoring_active,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            self._monitoring_active = False
            logger.error(f"❌ Ошибка запуска мониторинга: {e}")
            return ToolResult(success=False, error=f"Ошибка запуска мониторинга: {str(e)}")

    def _stop_monitoring(self) -> ToolResult:
        """⏹️ Остановка мониторинга системы"""
        try:
            if not self._monitoring_active:
                return ToolResult(
                    success=False,
                    error="Мониторинг не активен"
                )
            
            # Останавливаем мониторинг
            self._monitoring_active = False
            
            # Ждём завершения потока
            if self._monitoring_thread and self._monitoring_thread.is_alive():
                self._monitoring_thread.join(timeout=5)
            
            records_count = len(self._monitoring_data)
            
            logger.info(f"⏹️ Остановлен мониторинг системы ({records_count} записей собрано)")
            
            return ToolResult(
                success=True,
                data={
                    "operation": "stop_monitoring",
                    "monitoring_active": self._monitoring_active,
                    "records_collected": records_count,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки мониторинга: {e}")
            return ToolResult(success=False, error=f"Ошибка остановки мониторинга: {str(e)}")

    def _get_monitoring_data(self) -> ToolResult:
        """📈 Получение данных мониторинга"""
        try:
            records_count = len(self._monitoring_data)
            
            if records_count == 0:
                return ToolResult(
                    success=True,
                    data={
                        "monitoring_data": [],
                        "records_count": 0,
                        "monitoring_active": self._monitoring_active,
                        "message": "Нет данных мониторинга",
                        "timestamp": datetime.now().isoformat(),
                        "source": "SuperSystemTool"
                    }
                )
            
            # Статистика по данным
            if records_count > 0:
                cpu_values = [r["cpu_percent"] for r in self._monitoring_data]
                memory_values = [r["memory_percent"] for r in self._monitoring_data]
                
                statistics = {
                    "cpu_avg": round(sum(cpu_values) / len(cpu_values), 2),
                    "cpu_max": max(cpu_values),
                    "cpu_min": min(cpu_values),
                    "memory_avg": round(sum(memory_values) / len(memory_values), 2),
                    "memory_max": max(memory_values),
                    "memory_min": min(memory_values),
                    "timespan_minutes": round((records_count * 1.0) / 60, 2)  # Примерно
                }
            else:
                statistics = {}
            
            return ToolResult(
                success=True,
                data={
                    "monitoring_data": self._monitoring_data[-100:],  # Последние 100 записей
                    "records_count": records_count,
                    "monitoring_active": self._monitoring_active,
                    "statistics": statistics,
                    "total_records_available": records_count,
                    "showing_last_records": min(100, records_count),
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения данных мониторинга: {str(e)}"
            )

    def _get_system_metrics(self) -> ToolResult:
        """📊 Ключевые метрики системы"""
        try:
            # Собираем актуальные метрики
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net_io = psutil.net_io_counters()
            boot_time = psutil.boot_time()
            
            # Процессы
            processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent']))
            active_processes = len([p for p in processes if p.info['cpu_percent'] and p.info['cpu_percent'] > 0])
            
            # Load average
            try:
                load_avg = list(os.getloadavg())
            except (OSError, AttributeError):
                load_avg = [0.0, 0.0, 0.0]
            
            metrics = {
                "system": {
                    "uptime_hours": round((time.time() - boot_time) / 3600, 2),
                    "load_average": load_avg,
                    "active_processes": active_processes,
                    "total_processes": len(processes)
                },
                "cpu": {
                    "usage_percent": cpu_percent,
                    "cores": psutil.cpu_count(),
                    "frequency_mhz": round(psutil.cpu_freq().current, 0) if psutil.cpu_freq() else 0
                },
                "memory": {
                    "usage_percent": memory.percent,
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2)
                },
                "disk": {
                    "usage_percent": round((disk.used / disk.total) * 100, 2),
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2)
                },
                "network": {
                    "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                    "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                }
            }
            
            return ToolResult(
                success=True,
                data={
                    "system_metrics": metrics,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка получения системных метрик: {str(e)}"
            )

    def _check_system_health(self) -> ToolResult:
        """🩺 Расширенная проверка здоровья системы"""
        try:
            # Используем базовый health_check и добавляем дополнительные проверки
            base_health = self._health_check()
            
            if not base_health.success:
                return base_health
            
            health_data = base_health.data["health_check"]
            
            # Дополнительные проверки
            additional_checks = {
                "network_connectivity": "unknown",
                "disk_io_performance": "unknown", 
                "system_services": "unknown",
                "file_system_health": "unknown"
            }
            
            # Проверка сетевого подключения (простая)
            try:
                import socket
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                additional_checks["network_connectivity"] = "good"
            except:
                additional_checks["network_connectivity"] = "warning"
                health_data["warnings"].append("Проблемы с сетевым подключением")
                health_data["health_score"] -= 5
            
            # Проверка производительности диска
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io and hasattr(disk_io, 'read_time') and hasattr(disk_io, 'write_time'):
                    total_io_time = disk_io.read_time + disk_io.write_time
                    if total_io_time > 0:  # Есть активность
                        additional_checks["disk_io_performance"] = "good"
                    else:
                        additional_checks["disk_io_performance"] = "warning"
                else:
                    additional_checks["disk_io_performance"] = "unknown"
            except:
                additional_checks["disk_io_performance"] = "unknown"
            
            # Проверка файловой системы (базовая)
            try:
                test_file = Path("/tmp/supersystem_health_check.tmp")
                test_file.touch()
                test_file.unlink()
                additional_checks["file_system_health"] = "good"
            except:
                additional_checks["file_system_health"] = "warning"
                health_data["warnings"].append("Проблемы с файловой системой")
                health_data["health_score"] -= 10
            
            # Обновляем данные
            health_data["additional_checks"] = additional_checks
            
            return ToolResult(
                success=True,
                data={
                    "extended_health_check": health_data,
                    "timestamp": datetime.now().isoformat(),
                    "source": "SuperSystemTool"
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Ошибка расширенной проверки здоровья: {str(e)}"
            )


# ========================================
# 🏭 ФАБРИЧНЫЕ ФУНКЦИИ
# ========================================

def create_super_system_tool() -> SuperSystemTool:
    """🚀 Создание SuperSystemTool"""
    return SuperSystemTool()

def create_lightweight_super_system_tool() -> SuperSystemTool:
    """⚡ Создание облегчённой версии SuperSystemTool"""
    tool = SuperSystemTool()
    tool._cache_timeout = 10.0  # Более длинный кеш
    tool.max_file_size_mb = 50   # Меньший лимит файлов
    tool.max_output_size = 25000  # Меньший вывод
    return tool