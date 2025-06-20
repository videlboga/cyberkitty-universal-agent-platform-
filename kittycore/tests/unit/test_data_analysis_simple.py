"""
Тесты для DataAnalysisSimpleTool
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
from pathlib import Path

from kittycore.tools.data_analysis_simple import DataAnalysisSimpleTool


@pytest.fixture
def data_tool():
    """Фикстура для DataAnalysisSimpleTool"""
    return DataAnalysisSimpleTool()


@pytest.fixture
def sample_csv():
    """Фикстура с тестовым CSV файлом"""
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'salary': [50000, 60000, 70000, 55000, 65000],
        'department': ['IT', 'HR', 'IT', 'Finance', 'IT']
    }
    df = pd.DataFrame(data)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        yield f.name
    
    # Очистка
    Path(f.name).unlink(missing_ok=True)


class TestDataAnalysisSimpleTool:
    """Тесты для DataAnalysisSimpleTool"""
    
    def test_initialization(self, data_tool):
        """Тест инициализации"""
        assert data_tool.name == "data_analysis_simple"
        assert "анализа данных" in data_tool.description
        assert '.csv' in data_tool.supported_formats
        assert '.json' in data_tool.supported_formats
    
    def test_get_schema(self, data_tool):
        """Тест получения схемы"""
        schema = data_tool.get_schema()
        
        assert schema['type'] == 'object'
        assert 'action' in schema['properties']
        assert 'required' in schema
        assert 'action' in schema['required']
    
    def test_load_csv_data(self, data_tool, sample_csv):
        """Тест загрузки CSV данных"""
        result = data_tool.execute(action="load_data", file_path=sample_csv)
        
        assert result.success is True
        assert 'dataset_name' in result.data
        assert 'shape' in result.data
        assert result.data['shape'] == (5, 5)  # 5 строк, 5 столбцов
        assert len(result.data['columns']) == 5
    
    def test_load_nonexistent_file(self, data_tool):
        """Тест загрузки несуществующего файла"""
        result = data_tool.execute(action="load_data", file_path="nonexistent.csv")
        
        assert result.success is False
        assert 'не найден' in result.error
    
    def test_load_unsupported_format(self, data_tool):
        """Тест загрузки неподдерживаемого формата"""
        with tempfile.NamedTemporaryFile(suffix='.txt') as f:
            f.write(b"test data")
            f.flush()
            
            result = data_tool.execute(action="load_data", file_path=f.name)
            
            assert result.success is False
            assert 'Неподдерживаемый формат' in result.error
            assert 'supported_formats' in result.data
    
    def test_analyze_basic(self, data_tool, sample_csv):
        """Тест базового анализа"""
        # Сначала загружаем данные
        load_result = data_tool.execute(action="load_data", file_path=sample_csv)
        dataset_name = load_result.data['dataset_name']
        
        # Затем анализируем
        result = data_tool.execute(action="analyze_basic", dataset_name=dataset_name)
        
        assert result.success is True
        assert 'dataset_info' in result.data
        assert 'missing_values' in result.data
        assert 'data_types' in result.data
        assert 'numeric_statistics' in result.data
        
        # Проверяем базовую информацию
        dataset_info = result.data['dataset_info']
        assert dataset_info['rows'] == 5
        assert dataset_info['columns'] == 5
        
        # Проверяем статистику
        numeric_stats = result.data['numeric_statistics']
        assert 'age' in numeric_stats
        assert 'salary' in numeric_stats
        assert numeric_stats['age']['mean'] == 30.0  # (25+30+35+28+32)/5
    
    def test_analyze_nonexistent_dataset(self, data_tool):
        """Тест анализа несуществующего датасета"""
        result = data_tool.execute(action="analyze_basic", dataset_name="nonexistent")
        
        assert result.success is False
        assert 'не найден' in result.error
        assert 'available_datasets' in result.data
    
    def test_list_datasets(self, data_tool, sample_csv):
        """Тест получения списка датасетов"""
        # Загружаем данные
        data_tool.execute(action="load_data", file_path=sample_csv)
        
        # Получаем список
        result = data_tool.execute(action="list_datasets")
        
        assert result.success is True
        assert 'datasets' in result.data
        assert 'total_datasets' in result.data
        assert result.data['total_datasets'] > 0
    
    def test_invalid_action(self, data_tool):
        """Тест вызова несуществующего действия"""
        result = data_tool.execute(action="unknown_action")
        
        assert result.success is False
        assert 'Неизвестное действие' in result.error
        assert 'available_actions' in result.data
        
        # Проверяем что все доступные действия присутствуют
        available = result.data['available_actions']
        assert 'load_data' in available
        assert 'analyze_basic' in available
        assert 'list_datasets' in available
    
    def test_full_workflow(self, data_tool, sample_csv):
        """Тест полного рабочего процесса"""
        # 1. Загружаем данные
        load_result = data_tool.execute(action="load_data", file_path=sample_csv)
        assert load_result.success is True
        dataset_name = load_result.data['dataset_name']
        
        # 2. Получаем список датасетов
        list_result = data_tool.execute(action="list_datasets")
        assert list_result.success is True
        assert dataset_name in list_result.data['datasets']
        
        # 3. Анализируем данные
        analyze_result = data_tool.execute(action="analyze_basic", dataset_name=dataset_name)
        assert analyze_result.success is True
        
        # Проверяем что анализ содержит все необходимые части
        analysis = analyze_result.data
        assert 'dataset_info' in analysis
        assert 'missing_values' in analysis
        assert 'data_types' in analysis
        assert 'numeric_statistics' in analysis
        
        # Проверяем что числовые колонки правильно определены
        data_types = analysis['data_types']
        assert 'age' in data_types['numeric_columns']
        assert 'salary' in data_types['numeric_columns']
        assert 'name' in data_types['text_columns']
        assert 'department' in data_types['text_columns'] 