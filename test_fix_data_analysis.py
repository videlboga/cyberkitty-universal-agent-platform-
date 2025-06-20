#!/usr/bin/env python3
"""
📊 ОТЛАДКА: data_analysis_tool
"""

import time
import json
import tempfile
import os
import csv

try:
    from kittycore.tools.data_analysis_tool import DataAnalysisTool
    IMPORT_OK = True
    print("✅ Импорт data_analysis_tool успешен")
except ImportError as e:
    print(f"❌ ИМПОРТ ОШИБКА: {e}")
    IMPORT_OK = False

def test_dataset_list():
    """Тест получения списка датасетов"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📋 Тестирую список датасетов...")
    tool = DataAnalysisTool()
    
    # ВАЖНО: DataAnalysisTool СИНХРОННЫЙ через _execute_async_method
    result = tool.execute("list_datasets")
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            if isinstance(data, dict):
                datasets = data.get('datasets', [])
                print(f"📋 Датасетов в кеше: {len(datasets)}")
    
    return result

def test_load_csv_data():
    """Тест загрузки CSV данных"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📄 Тестирую загрузку CSV данных...")
    tool = DataAnalysisTool()
    
    # Создаем временный CSV файл с тестовыми данными
    test_data = [
        ['name', 'age', 'salary', 'department'],
        ['Андрей', 28, 50000, 'IT'],
        ['Мария', 32, 60000, 'Marketing'],
        ['Петр', 25, 45000, 'IT'],
        ['Анна', 30, 55000, 'Sales'],
        ['Иван', 35, 70000, 'IT']
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        temp_path = f.name
        writer = csv.writer(f)
        writer.writerows(test_data)
    
    try:
        result = tool.execute("load_data", file_path=temp_path, dataset_name="test_employees")
        
        print(f"📊 Результат: {type(result)}")
        if hasattr(result, 'success'):
            print(f"✅ Success: {result.success}")
            if result.success and hasattr(result, 'data'):
                data = result.data
                if isinstance(data, dict):
                    rows = data.get('rows', 0)
                    columns = data.get('columns', 0)
                    print(f"📄 CSV загружен: {rows} строк, {columns} столбцов")
        
        return result
        
    finally:
        # Удаляем временный файл
        try:
            os.unlink(temp_path)
        except:
            pass

def test_basic_analysis():
    """Тест базового анализа данных"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📈 Тестирую базовый анализ...")
    tool = DataAnalysisTool()
    
    # Сначала загружаем данные
    test_data = [
        ['product', 'price', 'quantity', 'category'],
        ['Laptop', 1000, 50, 'Electronics'],
        ['Mouse', 25, 200, 'Electronics'],
        ['Chair', 150, 100, 'Furniture'],
        ['Desk', 300, 75, 'Furniture'],
        ['Phone', 800, 120, 'Electronics']
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        temp_path = f.name
        writer = csv.writer(f)
        writer.writerows(test_data)
    
    try:
        # Загружаем данные
        load_result = tool.execute("load_data", file_path=temp_path, dataset_name="test_products")
        
        if hasattr(load_result, 'success') and load_result.success:
            # Анализируем
            result = tool.execute("analyze_basic", dataset_name="test_products")
            
            print(f"📊 Результат: {type(result)}")
            if hasattr(result, 'success'):
                print(f"✅ Success: {result.success}")
                if result.success and hasattr(result, 'data'):
                    data = result.data
                    if isinstance(data, dict):
                        statistics = data.get('statistics', {})
                        print(f"📈 Статистика: {list(statistics.keys()) if isinstance(statistics, dict) else 'не dict'}")
            
            return result
        else:
            print("❌ Не удалось загрузить данные для анализа")
            return load_result
        
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

def test_report_generation():
    """Тест генерации отчёта"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📝 Тестирую генерацию отчёта...")
    tool = DataAnalysisTool()
    
    # Загружаем тестовые данные
    test_data = [
        ['region', 'sales', 'profit'],
        ['North', 10000, 2000],
        ['South', 15000, 3000],
        ['East', 12000, 2400],
        ['West', 8000, 1600]
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        temp_path = f.name
        writer = csv.writer(f)
        writer.writerows(test_data)
    
    try:
        # Загружаем данные
        load_result = tool.execute("load_data", file_path=temp_path, dataset_name="test_sales")
        
        if hasattr(load_result, 'success') and load_result.success:
            # Генерируем отчёт
            result = tool.execute("generate_report", dataset_name="test_sales", report_type="basic")
            
            print(f"📊 Результат: {type(result)}")
            if hasattr(result, 'success'):
                print(f"✅ Success: {result.success}")
                if result.success and hasattr(result, 'data'):
                    data = result.data
                    if isinstance(data, dict):
                        report = data.get('report', '')
                        print(f"📝 Отчёт сгенерирован: {len(report)} символов")
            
            return result
        else:
            print("❌ Не удалось загрузить данные для отчёта")
            return load_result
        
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

def is_result_honest(result, test_name):
    """Проверка честности результата"""
    if not result:
        print(f"❌ {test_name}: Пустой результат")
        return False
    
    # Проверяем базовую структуру ToolResult
    if not hasattr(result, 'success'):
        print(f"❌ {test_name}: Результат не ToolResult")
        return False
    
    success = result.success
    if not success:
        print(f"❌ {test_name}: success=False")
        if hasattr(result, 'error'):
            print(f"   Ошибка: {result.error}")
        return False
    
    # Конвертируем в строку для анализа
    data_str = str(result.data) if hasattr(result, 'data') else str(result)
    data_size = len(data_str)
    
    # Проверка на фейковые паттерны
    fake_patterns = [
        "data_analysis: успешно",
        "демо анализ",
        "заглушка данных"
    ]
    
    for pattern in fake_patterns:
        if pattern.lower() in data_str.lower():
            print(f"❌ {test_name}: Найден фейковый паттерн: {pattern}")
            return False
    
    # Проверка на реальные признаки анализа данных
    data_indicators = [
        "data", "rows", "columns", "statistics", "analysis", "report", 
        "dataset", "csv", "mean", "median", "count", "загружен", "сгенерирован"
    ]
    
    has_data_analysis = any(indicator.lower() in data_str.lower() for indicator in data_indicators)
    
    if not has_data_analysis:
        print(f"❌ {test_name}: Нет признаков реального анализа данных")
        return False
    
    if data_size < 30:
        print(f"❌ {test_name}: Слишком маленький результат ({data_size} байт)")
        return False
    
    print(f"✅ {test_name}: ЧЕСТНЫЙ результат ({data_size} байт)")
    return True

def main():
    print("📊 ОТЛАДКА: data_analysis_tool")
    
    if not IMPORT_OK:
        return
    
    results = {}
    
    # Тесты (все синхронные через execute)
    tests = [
        ("dataset_list", test_dataset_list),
        ("load_csv_data", test_load_csv_data),
        ("basic_analysis", test_basic_analysis),
        ("report_generation", test_report_generation)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*30}")
        print(f"ТЕСТ: {test_name}")
        try:
            result = test_func()
            results[test_name] = is_result_honest(result, test_name)
        except Exception as e:
            print(f"❌ ТЕСТ ОШИБКА: {e}")
            results[test_name] = False
    
    # Итоги
    print(f"\n{'='*50}")
    print("📊 ИТОГИ:")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Всего тестов: {total_tests}")
    print(f"Прошло тестов: {passed_tests}")
    print(f"Процент успеха: {success_rate:.1f}%")
    
    for test_name, success in results.items():
        status = "✅ ПРОШЕЛ" if success else "❌ ПРОВАЛЕН"
        print(f"  {test_name}: {status}")
    
    print(f"\n📊 Статус: {'✅ РАБОТАЕТ' if success_rate >= 75 else '❌ НЕ РАБОТАЕТ'}")

if __name__ == "__main__":
    main() 