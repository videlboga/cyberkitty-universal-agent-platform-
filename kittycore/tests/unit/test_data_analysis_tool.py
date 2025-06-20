"""
Тесты для DataAnalysisTool - инструмента анализа данных
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import json
from pathlib import Path

from kittycore.tools.data_analysis_tool import DataAnalysisTool


@pytest.fixture
def data_tool():
    """Фикстура для DataAnalysisTool"""
    return DataAnalysisTool()


@pytest.fixture
def sample_data():
    """Фикстура с тестовыми данными"""
    np.random.seed(42)
    data = {
        'id': range(1, 101),
        'name': [f'Item_{i}' for i in range(1, 101)],
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'price': np.random.normal(100, 20, 100),
        'quantity': np.random.randint(1, 50, 100),
        'rating': np.random.uniform(1, 5, 100)
    }
    
    # Добавляем пропущенные значения
    df = pd.DataFrame(data)
    df.loc[df.sample(10).index, 'price'] = np.nan
    df.loc[df.sample(5).index, 'rating'] = np.nan
    
    # Добавляем дубликаты
    df = pd.concat([df, df.tail(3)], ignore_index=True)
    
    return df


@pytest.fixture
def csv_file(sample_data):
    """Фикстура с CSV файлом"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_data.to_csv(f.name, index=False)
        yield f.name
    
    # Очистка
    Path(f.name).unlink(missing_ok=True)


class TestDataAnalysisTool:
    """Тесты для DataAnalysisTool"""
    
    @pytest.mark.asyncio
    async def test_initialization(self, data_tool):
        """Тест инициализации"""
        assert data_tool.name == "data_analysis_tool"
        assert "анализа данных" in data_tool.description
        assert len(data_tool.supported_formats) > 0
        assert isinstance(data_tool._data_cache, dict)
    
    @pytest.mark.asyncio
    async def test_load_csv_data(self, data_tool, csv_file):
        """Тест загрузки CSV данных"""
        result = await data_tool.execute("load_data", file_path=csv_file)
        
        assert result['success'] is True
        assert 'data_info' in result
        assert result['data_info']['shape'][0] > 0
        assert result['data_info']['shape'][1] > 0
        assert len(result['data_info']['columns']) > 0
    
    @pytest.mark.asyncio
    async def test_load_nonexistent_file(self, data_tool):
        """Тест загрузки несуществующего файла"""
        result = await data_tool.execute("load_data", file_path="nonexistent.csv")
        
        assert result['success'] is False
        assert 'не найден' in result['error']
    
    @pytest.mark.asyncio
    async def test_unsupported_format(self, data_tool):
        """Тест загрузки неподдерживаемого формата"""
        with tempfile.NamedTemporaryFile(suffix='.txt') as f:
            f.write(b"test data")
            f.flush()
            
            result = await data_tool.execute("load_data", file_path=f.name)
            
            assert result['success'] is False
            assert 'Неподдерживаемый формат' in result['error']
    
    @pytest.mark.asyncio
    async def test_list_datasets(self, data_tool, csv_file):
        """Тест получения списка датасетов"""
        # Загружаем данные
        await data_tool.execute("load_data", file_path=csv_file)
        
        # Получаем список
        result = await data_tool.execute("list_datasets")
        
        assert result['success'] is True
        assert result['total_datasets'] > 0
        assert 'datasets' in result
    
    @pytest.mark.asyncio
    async def test_basic_analysis(self, data_tool, csv_file):
        """Тест базового анализа"""
        # Загружаем данные
        load_result = await data_tool.execute("load_data", file_path=csv_file)
        dataset_name = load_result['data_info']['dataset_name']
        
        # Анализируем
        result = await data_tool.execute("analyze_basic", dataset_name=dataset_name)
        
        assert result['success'] is True
        assert 'basic_info' in result
        assert 'data_types' in result
        assert 'missing_values' in result
        assert 'numeric_statistics' in result
        assert 'categorical_statistics' in result
        
        # Проверяем базовую информацию
        basic_info = result['basic_info']
        assert basic_info['total_rows'] > 0
        assert basic_info['total_columns'] > 0
    
    @pytest.mark.asyncio
    async def test_analysis_nonexistent_dataset(self, data_tool):
        """Тест анализа несуществующего датасета"""
        result = await data_tool.execute("analyze_basic", dataset_name="nonexistent")
        
        assert result['success'] is False
        assert 'не найден' in result['error']
    
    @pytest.mark.asyncio
    async def test_data_cleaning(self, data_tool, csv_file):
        """Тест очистки данных"""
        # Загружаем данные
        load_result = await data_tool.execute("load_data", file_path=csv_file)
        dataset_name = load_result['data_info']['dataset_name']
        
        # Очищаем данные
        result = await data_tool.execute("clean_data", dataset_name=dataset_name)
        
        assert result['success'] is True
        assert 'cleaned_dataset' in result
        assert 'applied_operations' in result
        assert result['cleaned_shape'][0] <= result['original_shape'][0]  # Строк не больше
        
        # Проверяем что операции применились
        operations = [op['operation'] for op in result['applied_operations']]
        assert 'remove_duplicates' in operations
        assert 'handle_missing' in operations
    
    @pytest.mark.asyncio
    async def test_data_cleaning_with_custom_operations(self, data_tool, csv_file):
        """Тест очистки с кастомными операциями"""
        # Загружаем данные
        load_result = await data_tool.execute("load_data", file_path=csv_file)
        dataset_name = load_result['data_info']['dataset_name']
        
        # Очищаем только дубликаты
        result = await data_tool.execute(
            "clean_data", 
            dataset_name=dataset_name,
            operations=["remove_duplicates"]
        )
        
        assert result['success'] is True
        operations = [op['operation'] for op in result['applied_operations']]
        assert 'remove_duplicates' in operations
        assert 'handle_missing' not in operations
    
    @pytest.mark.asyncio
    async def test_generate_report_basic(self, data_tool, csv_file):
        """Тест генерации базового отчёта"""
        # Загружаем данные
        load_result = await data_tool.execute("load_data", file_path=csv_file)
        dataset_name = load_result['data_info']['dataset_name']
        
        # Генерируем отчёт
        result = await data_tool.execute(
            "generate_report", 
            dataset_name=dataset_name,
            report_type="basic"
        )
        
        assert result['success'] is True
        assert 'report' in result
        
        report = result['report']
        assert 'report_info' in report
        assert 'analysis_results' in report
        assert 'recommendations' in report
        assert 'summary' in report
    
    @pytest.mark.asyncio
    async def test_generate_report_comprehensive(self, data_tool, csv_file):
        """Тест генерации детального отчёта"""
        # Загружаем данные
        load_result = await data_tool.execute("load_data", file_path=csv_file)
        dataset_name = load_result['data_info']['dataset_name']
        
        # Генерируем детальный отчёт
        result = await data_tool.execute(
            "generate_report", 
            dataset_name=dataset_name,
            report_type="comprehensive"
        )
        
        assert result['success'] is True
        report = result['report']
        
        # Проверяем детальную информацию
        analysis = report['analysis_results']
        assert 'numeric_analysis' in analysis
        assert 'categorical_analysis' in analysis
        
        # Проверяем что есть рекомендации
        assert isinstance(report['recommendations'], list)
        assert 'data_quality_score' in report['summary']
    
    @pytest.mark.asyncio
    async def test_export_data_csv(self, data_tool, csv_file):
        """Тест экспорта в CSV"""
        # Загружаем данные
        load_result = await data_tool.execute("load_data", file_path=csv_file)
        dataset_name = load_result['data_info']['dataset_name']
        
        # Экспортируем
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            result = await data_tool.execute(
                "export_data",
                dataset_name=dataset_name,
                output_path=f.name,
                file_format="csv"
            )
            
            assert result['success'] is True
            assert Path(f.name).exists()
            assert result['file_size_kb'] > 0
            
            # Очистка
            Path(f.name).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_export_data_json(self, data_tool, csv_file):
        """Тест экспорта в JSON"""
        # Загружаем данные
        load_result = await data_tool.execute("load_data", file_path=csv_file)
        dataset_name = load_result['data_info']['dataset_name']
        
        # Экспортируем
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            result = await data_tool.execute(
                "export_data",
                dataset_name=dataset_name,
                output_path=f.name,
                file_format="json"
            )
            
            assert result['success'] is True
            assert Path(f.name).exists()
            
            # Проверяем что JSON валидный
            with open(f.name, 'r') as json_file:
                data = json.load(json_file)
                assert isinstance(data, list)
                assert len(data) > 0
            
            # Очистка
            Path(f.name).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_export_unsupported_format(self, data_tool, csv_file):
        """Тест экспорта в неподдерживаемый формат"""
        # Загружаем данные
        load_result = await data_tool.execute("load_data", file_path=csv_file)
        dataset_name = load_result['data_info']['dataset_name']
        
        # Экспортируем в неподдерживаемый формат
        result = await data_tool.execute(
            "export_data",
            dataset_name=dataset_name,
            output_path="test.xml",
            file_format="xml"
        )
        
        assert result['success'] is False
        assert 'Неподдерживаемый формат' in result['error']
    
    @pytest.mark.asyncio
    async def test_invalid_action(self, data_tool):
        """Тест вызова несуществующего действия"""
        result = await data_tool.execute("unknown_action")
        
        assert result['success'] is False
        assert 'Неизвестное действие' in result['error']
        assert 'available_actions' in result 