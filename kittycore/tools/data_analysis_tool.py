"""
DataAnalysisTool для KittyCore 3.0 - Инструмент анализа данных

Возможности:
- Анализ CSV/Excel файлов
- Статистический анализ
- Генерация отчётов
- Визуализация данных
- Машинное обучение (базовые модели)
"""

import pandas as pd
import numpy as np
import json
import csv
import asyncio
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging

from .base_tool import Tool
from .unified_tool_result import ToolResult

# Настройка логирования
logger = logging.getLogger(__name__)

class DataAnalysisTool(Tool):
    """
    Инструмент для анализа данных
    
    Основные возможности:
    - Загрузка и обработка данных (CSV, Excel, JSON)
    - Статистический анализ
    - Очистка данных
    - Генерация отчётов
    """
    
    def __init__(self):
        super().__init__(
            name="data_analysis_tool",
            description="Инструмент для анализа данных: загрузка, обработка, статистика, отчёты"
        )
        
        # Поддерживаемые форматы файлов
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.json', '.tsv']
        
        # Кеш для загруженных данных
        self._data_cache = {}
        
        logger.info("DataAnalysisTool инициализирован")
    
    def get_schema(self) -> Dict[str, Any]:
        """Получить JSON Schema для параметров инструмента"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Действие для выполнения",
                    "enum": [
                        "load_data", "list_datasets", "analyze_basic",
                        "clean_data", "generate_report", "export_data"
                    ]
                },
                "file_path": {
                    "type": "string",
                    "description": "Путь к файлу данных (для load_data)"
                },
                "dataset_name": {
                    "type": "string", 
                    "description": "Имя датасета"
                },
                "operations": {
                    "type": "array",
                    "description": "Список операций очистки (для clean_data)",
                    "items": {"type": "string"}
                },
                "report_type": {
                    "type": "string",
                    "description": "Тип отчёта (для generate_report)",
                    "enum": ["basic", "comprehensive", "executive"]
                },
                "output_path": {
                    "type": "string",
                    "description": "Путь для экспорта (для export_data)"
                },
                "file_format": {
                    "type": "string",
                    "description": "Формат файла для экспорта",
                    "enum": ["csv", "excel", "json"]
                }
            },
            "required": ["action"]
        }
    
    def execute(self, action: str, **kwargs) -> ToolResult:
        """
        Выполнение действий с данными
        
        Args:
            action: Тип действия
            **kwargs: Параметры действия
            
        Returns:
            Результат выполнения
        """
        try:
            # Выполняем async методы правильно
            if action == "load_data":
                result = self._execute_async_method(self._load_data, **kwargs)
            elif action == "list_datasets":
                result = self._execute_async_method(self._get_datasets_list)
            elif action == "analyze_basic":
                result = self._execute_async_method(self._analyze_basic, **kwargs)
            elif action == "clean_data":
                result = self._execute_async_method(self._clean_data, **kwargs)
            elif action == "generate_report":
                result = self._execute_async_method(self._generate_report, **kwargs)
            elif action == "export_data":
                result = self._execute_async_method(self._export_data, **kwargs)
            else:
                return ToolResult(
                    success=False,
                    error=f'Неизвестное действие: {action}',
                    data={
                        'available_actions': [
                            'load_data', 'list_datasets', 'analyze_basic', 
                            'clean_data', 'generate_report', 'export_data'
                        ]
                    }
                )
            
            # Конвертируем результат в ToolResult
            if isinstance(result, dict):
                if result.get('success', True):
                    return ToolResult(success=True, data=result)
                else:
                    return ToolResult(success=False, error=result.get('error', 'Unknown error'))
            else:
                return ToolResult(success=True, data={'result': result})
                
        except Exception as e:
            logger.error(f"Ошибка в DataAnalysisTool.execute: {e}")
            return ToolResult(
                success=False,
                error=str(e)
            )
    
    def _execute_async_method(self, method, **kwargs):
        """Безопасное выполнение async методов"""
        try:
            # Фильтруем параметры для метода
            import inspect
            method_signature = inspect.signature(method)
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in method_signature.parameters}
            
            # Проверяем есть ли запущенный event loop
            loop = asyncio.get_running_loop()
            # Если да - выполняем в отдельном потоке
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, method(**filtered_kwargs))
                return future.result(timeout=30)  # 30 сек таймаут
        except RuntimeError:
            # Нет запущенного loop - можем использовать asyncio.run
            method_signature = inspect.signature(method)
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in method_signature.parameters}
            return asyncio.run(method(**filtered_kwargs)) 
    
    async def _load_data(self, file_path: str, dataset_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Загрузка данных из файла
        
        Args:
            file_path: Путь к файлу
            dataset_name: Имя датасета (опционально)
            
        Returns:
            Результат загрузки
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {
                    'success': False,
                    'error': f'Файл не найден: {file_path}'
                }
            
            # Определение имени датасета
            if not dataset_name:
                dataset_name = file_path.stem
            
            # Загрузка в зависимости от формата
            file_ext = file_path.suffix.lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext == '.tsv':
                df = pd.read_csv(file_path, sep='\t')
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif file_ext == '.json':
                df = pd.read_json(file_path)
            else:
                return {
                    'success': False,
                    'error': f'Неподдерживаемый формат: {file_ext}',
                    'supported_formats': self.supported_formats
                }
            
            # Сохранение в кеш
            self._data_cache[dataset_name] = df
            
            # Информация о загруженных данных
            info = {
                'dataset_name': dataset_name,
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.astype(str).to_dict(),
                'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB",
                'missing_values': df.isnull().sum().to_dict(),
                'head': df.head().to_dict('records')
            }
            
            logger.info(f"Загружен датасет '{dataset_name}': {df.shape}")
            
            return {
                'success': True,
                'message': f'Данные успешно загружены: {df.shape[0]} строк, {df.shape[1]} столбцов',
                'data_info': info
            }
            
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            return {
                'success': False,
                'error': f'Ошибка загрузки: {str(e)}'
            }
    
    async def _get_datasets_list(self) -> Dict[str, Any]:
        """Получение списка загруженных датасетов"""
        try:
            datasets_info = {}
            
            for name, df in self._data_cache.items():
                datasets_info[name] = {
                    'shape': df.shape,
                    'columns': len(df.columns),
                    'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
                }
            
            return {
                'success': True,
                'datasets': datasets_info,
                'total_datasets': len(self._data_cache)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 
    
    async def _analyze_basic(self, dataset_name: str) -> Dict[str, Any]:
        """
        Базовый статистический анализ данных
        
        Args:
            dataset_name: Имя датасета
            
        Returns:
            Результат анализа
        """
        try:
            if dataset_name not in self._data_cache:
                return {
                    'success': False,
                    'error': f'Датасет "{dataset_name}" не найден',
                    'available_datasets': list(self._data_cache.keys())
                }
            
            df = self._data_cache[dataset_name]
            
            # Базовая информация
            basic_info = {
                'shape': df.shape,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
            }
            
            # Типы данных
            dtypes_info = {
                'column_types': df.dtypes.astype(str).to_dict(),
                'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
                'text_columns': df.select_dtypes(include=['object']).columns.tolist(),
                'datetime_columns': df.select_dtypes(include=['datetime64']).columns.tolist()
            }
            
            # Пропущенные значения
            missing_info = {
                'missing_counts': df.isnull().sum().to_dict(),
                'missing_percentages': (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
                'total_missing': df.isnull().sum().sum(),
                'complete_rows': len(df.dropna())
            }
            
            # Описательная статистика для числовых столбцов
            numeric_stats = {}
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) > 0:
                stats_df = df[numeric_cols].describe()
                numeric_stats = stats_df.to_dict()
                
                # Дополнительная статистика
                for col in numeric_cols:
                    if col in numeric_stats:
                        numeric_stats[col]['median'] = df[col].median()
                        numeric_stats[col]['mode'] = df[col].mode().iloc[0] if len(df[col].mode()) > 0 else None
                        numeric_stats[col]['skewness'] = df[col].skew()
                        numeric_stats[col]['kurtosis'] = df[col].kurtosis()
            
            # Анализ категориальных данных
            categorical_stats = {}
            text_cols = df.select_dtypes(include=['object']).columns
            
            for col in text_cols:
                if col not in categorical_stats:
                    categorical_stats[col] = {}
                
                categorical_stats[col] = {
                    'unique_values': df[col].nunique(),
                    'most_frequent': df[col].mode().iloc[0] if len(df[col].mode()) > 0 else None,
                    'value_counts': df[col].value_counts().head(10).to_dict()
                }
            
            result = {
                'success': True,
                'dataset_name': dataset_name,
                'basic_info': basic_info,
                'data_types': dtypes_info,
                'missing_values': missing_info,
                'numeric_statistics': numeric_stats,
                'categorical_statistics': categorical_stats,
                'summary': {
                    'data_quality': 'Good' if missing_info['total_missing'] < len(df) * 0.1 else 'Needs cleaning',
                    'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            logger.info(f"Проведён базовый анализ датасета '{dataset_name}'")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка анализа данных: {e}")
            return {
                'success': False,
                'error': f'Ошибка анализа: {str(e)}'
            } 
    
    async def _clean_data(self, dataset_name: str, operations: List[str] = None) -> Dict[str, Any]:
        """
        Очистка и предобработка данных
        
        Args:
            dataset_name: Имя датасета
            operations: Список операций очистки
            
        Returns:
            Результат очистки
        """
        try:
            if dataset_name not in self._data_cache:
                return {
                    'success': False,
                    'error': f'Датасет "{dataset_name}" не найден'
                }
            
            df = self._data_cache[dataset_name].copy()
            original_shape = df.shape
            
            # Операции по умолчанию
            if operations is None:
                operations = ['remove_duplicates', 'handle_missing', 'fix_types']
            
            applied_operations = []
            
            # Удаление дубликатов
            if 'remove_duplicates' in operations:
                duplicates_before = df.duplicated().sum()
                df = df.drop_duplicates()
                applied_operations.append({
                    'operation': 'remove_duplicates',
                    'removed_rows': duplicates_before,
                    'status': 'success'
                })
            
            # Обработка пропущенных значений
            if 'handle_missing' in operations:
                missing_before = df.isnull().sum().sum()
                
                # Для числовых столбцов - заполнение медианой
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    if df[col].isnull().sum() > 0:
                        df[col].fillna(df[col].median(), inplace=True)
                
                # Для категориальных - заполнение модой
                categorical_cols = df.select_dtypes(include=['object']).columns
                for col in categorical_cols:
                    if df[col].isnull().sum() > 0:
                        mode_value = df[col].mode()
                        if len(mode_value) > 0:
                            df[col].fillna(mode_value.iloc[0], inplace=True)
                        else:
                            df[col].fillna('Unknown', inplace=True)
                
                missing_after = df.isnull().sum().sum()
                applied_operations.append({
                    'operation': 'handle_missing',
                    'filled_values': missing_before - missing_after,
                    'status': 'success'
                })
            
            # Исправление типов данных
            if 'fix_types' in operations:
                type_fixes = []
                
                # Попытка конвертации строк в числа
                for col in df.select_dtypes(include=['object']).columns:
                    try:
                        # Проверка, можно ли конвертировать в число
                        numeric_test = pd.to_numeric(df[col], errors='coerce')
                        if numeric_test.notna().sum() / len(df) > 0.8:  # Если 80%+ значений числовые
                            df[col] = numeric_test
                            type_fixes.append(f'{col}: object -> numeric')
                    except:
                        continue
                
                applied_operations.append({
                    'operation': 'fix_types',
                    'fixes_applied': type_fixes,
                    'status': 'success'
                })
            
            # Удаление пустых строк и столбцов
            if 'remove_empty' in operations:
                empty_rows_before = len(df)
                df = df.dropna(how='all')  # Удаление полностью пустых строк
                empty_cols_before = len(df.columns)
                df = df.dropna(axis=1, how='all')  # Удаление полностью пустых столбцов
                
                applied_operations.append({
                    'operation': 'remove_empty',
                    'removed_rows': empty_rows_before - len(df),
                    'removed_columns': empty_cols_before - len(df.columns),
                    'status': 'success'
                })
            
            # Сохранение очищенного датасета
            cleaned_name = f"{dataset_name}_cleaned"
            self._data_cache[cleaned_name] = df
            
            result = {
                'success': True,
                'original_dataset': dataset_name,
                'cleaned_dataset': cleaned_name,
                'original_shape': original_shape,
                'cleaned_shape': df.shape,
                'rows_removed': original_shape[0] - df.shape[0],
                'columns_removed': original_shape[1] - df.shape[1],
                'applied_operations': applied_operations,
                'data_quality_improvement': {
                    'missing_values_before': original_shape[0] * original_shape[1] - self._data_cache[dataset_name].count().sum(),
                    'missing_values_after': df.shape[0] * df.shape[1] - df.count().sum(),
                    'duplicates_removed': any(op['operation'] == 'remove_duplicates' for op in applied_operations)
                }
            }
            
            logger.info(f"Очищен датасет '{dataset_name}' -> '{cleaned_name}': {original_shape} -> {df.shape}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка очистки данных: {e}")
            return {
                'success': False,
                'error': f'Ошибка очистки: {str(e)}'
            }
    
    async def _generate_report(self, dataset_name: str, report_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        Генерация детального отчёта по данным
        
        Args:
            dataset_name: Имя датасета
            report_type: Тип отчёта ('basic', 'comprehensive', 'executive')
            
        Returns:
            Детальный отчёт
        """
        try:
            if dataset_name not in self._data_cache:
                return {
                    'success': False,
                    'error': f'Датасет "{dataset_name}" не найден'
                }
            
            df = self._data_cache[dataset_name]
            
            # Базовые метрики
            basic_metrics = {
                'dataset_overview': {
                    'name': dataset_name,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'memory_usage_kb': round(df.memory_usage(deep=True).sum() / 1024, 2),
                    'completeness': round((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100, 2)
                }
            }
            
            if report_type in ['comprehensive', 'executive']:
                # Анализ качества данных
                data_quality = {
                    'missing_values': {
                        'total_missing': int(df.isnull().sum().sum()),
                        'missing_percentage': round(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100, 2),
                        'columns_with_missing': df.columns[df.isnull().any()].tolist(),
                        'complete_rows': int(len(df.dropna()))
                    },
                    'duplicates': {
                        'duplicate_rows': int(df.duplicated().sum()),
                        'duplicate_percentage': round(df.duplicated().sum() / len(df) * 100, 2)
                    }
                }
                
                # Анализ типов данных
                data_types = {
                    'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
                    'text_columns': df.select_dtypes(include=['object']).columns.tolist(),
                    'datetime_columns': df.select_dtypes(include=['datetime64']).columns.tolist(),
                    'column_types': df.dtypes.astype(str).to_dict()
                }
                
                basic_metrics.update({
                    'data_quality': data_quality,
                    'data_types': data_types
                })
            
            if report_type == 'comprehensive':
                # Детальная статистика для числовых колонок
                numeric_analysis = {}
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                
                for col in numeric_cols:
                    numeric_analysis[col] = {
                        'mean': float(df[col].mean()),
                        'median': float(df[col].median()),
                        'std': float(df[col].std()),
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'q25': float(df[col].quantile(0.25)),
                        'q75': float(df[col].quantile(0.75)),
                        'skewness': float(df[col].skew()),
                        'kurtosis': float(df[col].kurtosis())
                    }
                
                # Анализ категориальных данных
                categorical_analysis = {}
                text_cols = df.select_dtypes(include=['object']).columns
                
                for col in text_cols:
                    value_counts = df[col].value_counts()
                    categorical_analysis[col] = {
                        'unique_values': int(df[col].nunique()),
                        'most_frequent': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                        'most_frequent_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                        'top_5_values': value_counts.head(5).to_dict()
                    }
                
                basic_metrics.update({
                    'numeric_analysis': numeric_analysis,
                    'categorical_analysis': categorical_analysis
                })
            
            # Рекомендации по улучшению данных
            recommendations = []
            
            missing_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
            if missing_pct > 5:
                recommendations.append("Рассмотрите обработку пропущенных значений (>5% от общего объёма)")
            
            if df.duplicated().sum() > 0:
                recommendations.append(f"Обнаружено {df.duplicated().sum()} дублированных строк - рекомендуется удаление")
            
            # Проверка на потенциальные числовые колонки в текстовом формате
            for col in df.select_dtypes(include=['object']).columns:
                try:
                    numeric_conversion = pd.to_numeric(df[col], errors='coerce')
                    if numeric_conversion.notna().sum() / len(df) > 0.8:
                        recommendations.append(f"Колонка '{col}' содержит числовые данные - рекомендуется изменить тип")
                except:
                    continue
            
            # Итоговый отчёт
            report = {
                'report_info': {
                    'dataset_name': dataset_name,
                    'report_type': report_type,
                    'generated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'tool_version': '1.0'
                },
                'analysis_results': basic_metrics,
                'recommendations': recommendations,
                'summary': {
                    'data_quality_score': max(0, 100 - missing_pct - (df.duplicated().sum() / len(df) * 100)),
                    'ready_for_analysis': missing_pct < 10 and df.duplicated().sum() / len(df) < 0.05
                }
            }
            
            logger.info(f"Сгенерирован {report_type} отчёт для датасета '{dataset_name}'")
            
            return {
                'success': True,
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации отчёта: {e}")
            return {
                'success': False,
                'error': f'Ошибка генерации отчёта: {str(e)}'
            }
    
    async def _export_data(self, dataset_name: str, output_path: str, file_format: str = 'csv') -> Dict[str, Any]:
        """
        Экспорт данных в файл
        
        Args:
            dataset_name: Имя датасета
            output_path: Путь для сохранения
            file_format: Формат файла ('csv', 'excel', 'json')
            
        Returns:
            Результат экспорта
        """
        try:
            if dataset_name not in self._data_cache:
                return {
                    'success': False,
                    'error': f'Датасет "{dataset_name}" не найден'
                }
            
            df = self._data_cache[dataset_name]
            output_path = Path(output_path)
            
            # Создание директории если не существует
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if file_format.lower() == 'csv':
                df.to_csv(output_path, index=False)
            elif file_format.lower() == 'excel':
                df.to_excel(output_path, index=False)
            elif file_format.lower() == 'json':
                df.to_json(output_path, orient='records', indent=2)
            else:
                return {
                    'success': False,
                    'error': f'Неподдерживаемый формат: {file_format}',
                    'supported_formats': ['csv', 'excel', 'json']
                }
            
            logger.info(f"Датасет '{dataset_name}' экспортирован в {output_path}")
            
            return {
                'success': True,
                'message': f'Данные успешно экспортированы',
                'output_path': str(output_path),
                'file_size_kb': round(output_path.stat().st_size / 1024, 2),
                'rows_exported': len(df),
                'columns_exported': len(df.columns)
            }
            
        except Exception as e:
            logger.error(f"Ошибка экспорта данных: {e}")
            return {
                'success': False,
                'error': f'Ошибка экспорта: {str(e)}'
            } 