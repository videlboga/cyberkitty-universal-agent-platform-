"""
SystemTools - Системные инструменты для агентов KittyCore

Предоставляет базовые системные операции:
- Математические вычисления
- Анализ данных
- Системная информация
- Конвертация данных
"""

import os
import sys
import json
import math
import statistics
from typing import Dict, List, Any, Union
from datetime import datetime
from .base_tool import BaseTool


class SystemTools(BaseTool):
    """Системные инструменты для агентов"""
    
    def __init__(self):
        super().__init__()
        self.name = "system_tools"
        self.description = "Системные операции: вычисления, анализ данных, конвертация"
    
    async def use(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Использование системного инструмента
        
        Args:
            action: Тип операции (calculate, analyze_data, system_info, convert)
            **kwargs: Параметры операции
        """
        try:
            if action == "calculate":
                return await self._calculate(kwargs)
            elif action == "analyze_data":
                return await self._analyze_data(kwargs)
            elif action == "system_info":
                return await self._system_info(kwargs)
            elif action == "convert":
                return await self._convert(kwargs)
            elif action == "list_files":
                return await self._list_files(kwargs)
            elif action == "file_stats":
                return await self._file_stats(kwargs)
            else:
                return {
                    'success': False,
                    'error': f'Неизвестное действие: {action}',
                    'available_actions': ['calculate', 'analyze_data', 'system_info', 'convert', 'list_files', 'file_stats']
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка выполнения {action}: {str(e)}'
            }
    
    async def _calculate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Математические вычисления"""
        expression = params.get('expression', '')
        numbers = params.get('numbers', [])
        operation = params.get('operation', '')
        
        if expression:
            # Безопасные вычисления выражений
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "len": len, "pow": pow,
                "math": math, "statistics": statistics
            }
            try:
                # Простая проверка безопасности
                if any(keyword in expression for keyword in ['import', 'exec', 'eval', '__']):
                    raise ValueError("Небезопасное выражение")
                
                result = eval(expression, {"__builtins__": {}}, allowed_names)
                return {
                    'success': True,
                    'result': result,
                    'expression': expression
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Ошибка вычисления: {str(e)}'
                }
        
        elif numbers and operation:
            # Операции над списком чисел
            try:
                if operation == 'sum':
                    result = sum(numbers)
                elif operation == 'avg' or operation == 'mean':
                    result = statistics.mean(numbers)
                elif operation == 'median':
                    result = statistics.median(numbers)
                elif operation == 'min':
                    result = min(numbers)
                elif operation == 'max':
                    result = max(numbers)
                elif operation == 'std':
                    result = statistics.stdev(numbers) if len(numbers) > 1 else 0
                else:
                    return {
                        'success': False,
                        'error': f'Неизвестная операция: {operation}',
                        'available_operations': ['sum', 'avg', 'median', 'min', 'max', 'std']
                    }
                
                return {
                    'success': True,
                    'result': result,
                    'operation': operation,
                    'numbers_count': len(numbers)
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Ошибка операции {operation}: {str(e)}'
                }
        
        return {
            'success': False,
            'error': 'Укажите expression (для вычисления выражения) или numbers+operation (для операций над списком)'
        }
    
    async def _analyze_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ данных"""
        data = params.get('data', [])
        analysis_type = params.get('type', 'basic')
        
        if not data:
            return {
                'success': False,
                'error': 'Не переданы данные для анализа'
            }
        
        try:
            if analysis_type == 'basic':
                # Базовая статистика
                if isinstance(data[0], (int, float)):
                    # Числовые данные
                    return {
                        'success': True,
                        'type': 'numeric',
                        'count': len(data),
                        'sum': sum(data),
                        'mean': statistics.mean(data),
                        'median': statistics.median(data),
                        'min': min(data),
                        'max': max(data),
                        'std': statistics.stdev(data) if len(data) > 1 else 0
                    }
                else:
                    # Текстовые/категориальные данные
                    from collections import Counter
                    counts = Counter(data)
                    return {
                        'success': True,
                        'type': 'categorical',
                        'count': len(data),
                        'unique': len(counts),
                        'most_common': counts.most_common(5),
                        'distribution': dict(counts)
                    }
            
            elif analysis_type == 'distribution':
                # Анализ распределения
                if isinstance(data[0], (int, float)):
                    # Разбиваем на интервалы
                    min_val, max_val = min(data), max(data)
                    bins = 10
                    step = (max_val - min_val) / bins
                    distribution = {}
                    
                    for i in range(bins):
                        start = min_val + i * step
                        end = min_val + (i + 1) * step
                        count = sum(1 for x in data if start <= x < end)
                        distribution[f"{start:.1f}-{end:.1f}"] = count
                    
                    return {
                        'success': True,
                        'type': 'distribution',
                        'bins': bins,
                        'distribution': distribution
                    }
                
            return {
                'success': False,
                'error': f'Неподдерживаемый тип анализа: {analysis_type}',
                'available_types': ['basic', 'distribution']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка анализа данных: {str(e)}'
            }
    
    async def _system_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Системная информация"""
        info_type = params.get('type', 'basic')
        
        try:
            if info_type == 'basic':
                return {
                    'success': True,
                    'platform': sys.platform,
                    'python_version': sys.version,
                    'cwd': os.getcwd(),
                    'timestamp': datetime.now().isoformat()
                }
            
            elif info_type == 'environment':
                return {
                    'success': True,
                    'env_vars': dict(os.environ),
                    'path': os.environ.get('PATH', '').split(os.pathsep)
                }
            
            elif info_type == 'files':
                directory = params.get('directory', '.')
                try:
                    files = os.listdir(directory)
                    return {
                        'success': True,
                        'directory': directory,
                        'files': files,
                        'count': len(files)
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Ошибка чтения директории {directory}: {str(e)}'
                    }
            
            return {
                'success': False,
                'error': f'Неподдерживаемый тип информации: {info_type}',
                'available_types': ['basic', 'environment', 'files']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения системной информации: {str(e)}'
            }
    
    async def _convert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Конвертация данных"""
        data = params.get('data')
        from_format = params.get('from', '')
        to_format = params.get('to', '')
        
        try:
            if from_format == 'json' and to_format == 'dict':
                result = json.loads(data) if isinstance(data, str) else data
                return {
                    'success': True,
                    'result': result,
                    'conversion': f'{from_format} -> {to_format}'
                }
            
            elif from_format == 'dict' and to_format == 'json':
                result = json.dumps(data, ensure_ascii=False, indent=2)
                return {
                    'success': True,
                    'result': result,
                    'conversion': f'{from_format} -> {to_format}'
                }
            
            elif from_format == 'list' and to_format == 'csv':
                if isinstance(data, list) and data:
                    if isinstance(data[0], dict):
                        # Список словарей в CSV
                        import csv
                        import io
                        output = io.StringIO()
                        writer = csv.DictWriter(output, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
                        result = output.getvalue()
                    else:
                        # Простой список в CSV
                        result = ','.join(map(str, data))
                    
                    return {
                        'success': True,
                        'result': result,
                        'conversion': f'{from_format} -> {to_format}'
                    }
            
            return {
                'success': False,
                'error': f'Неподдерживаемая конвертация: {from_format} -> {to_format}',
                'available_conversions': [
                    'json -> dict',
                    'dict -> json', 
                    'list -> csv'
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка конвертации: {str(e)}'
            }
    
    async def _list_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Список файлов в директории"""
        directory = params.get('directory', '.')
        pattern = params.get('pattern', '*')
        
        try:
            import glob
            if pattern != '*':
                path_pattern = os.path.join(directory, pattern)
                files = glob.glob(path_pattern)
            else:
                files = [os.path.join(directory, f) for f in os.listdir(directory)]
            
            files_info = []
            for file_path in files:
                if os.path.isfile(file_path):
                    stat_info = os.stat(file_path)
                    files_info.append({
                        'name': os.path.basename(file_path),
                        'path': file_path,
                        'size': stat_info.st_size,
                        'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                    })
            
            return {
                'success': True,
                'directory': directory,
                'pattern': pattern,
                'files': files_info,
                'count': len(files_info)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения списка файлов: {str(e)}'
            }
    
    async def _file_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Статистика файла"""
        file_path = params.get('file_path', '')
        
        if not file_path:
            return {
                'success': False,
                'error': 'Не указан путь к файлу'
            }
        
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'Файл не существует: {file_path}'
                }
            
            stat_info = os.stat(file_path)
            
            result = {
                'success': True,
                'file_path': file_path,
                'size': stat_info.st_size,
                'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'is_file': os.path.isfile(file_path),
                'is_directory': os.path.isdir(file_path)
            }
            
            # Если это текстовый файл, добавляем статистику содержимого
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        result.update({
                            'lines': len(content.splitlines()),
                            'chars': len(content),
                            'words': len(content.split()),
                            'encoding': 'utf-8'
                        })
                except UnicodeDecodeError:
                    result['encoding'] = 'binary'
                except Exception:
                    pass
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения статистики файла: {str(e)}'
            } 