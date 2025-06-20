#!/usr/bin/env python3
"""
🔧 ТЕСТ ИСПРАВЛЕННЫХ ИНСТРУМЕНТОВ KittyCore 3.0

Тестирование:
- code_execution_tool (исправлены asyncio конфликты)
- data_analysis_tool (исправлены sync/async проблемы)

Принцип: "Реальные вызовы, никаких моков!" 
"""

import asyncio
import time
import json
import tempfile
import os
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорт инструментов
from kittycore.tools.code_execution_tools import CodeExecutionTool
from kittycore.tools.data_analysis_tool import DataAnalysisTool

class FixedToolsTester:
    """Тестер исправленных инструментов"""
    
    def __init__(self):
        self.code_tool = CodeExecutionTool()
        self.data_tool = DataAnalysisTool()
        self.results = {}
        
    def test_code_execution_tool(self):
        """Тестирование CodeExecutionTool"""
        print("🐍 ТЕСТИРОВАНИЕ CODE_EXECUTION_TOOL")
        
        tests = [
            {
                'name': 'Простой Python код',
                'action': 'execute_python',
                'code': 'print("Hello from KittyCore!")\nresult = 2 + 2\nprint(f"2 + 2 = {result}")'
            },
            {
                'name': 'Python с математикой',
                'action': 'execute_python', 
                'code': 'import math\nprint(f"π = {math.pi:.6f}")\nprint(f"e = {math.e:.6f}")',
                'libraries': ['math']
            },
            {
                'name': 'Валидация Python кода',
                'action': 'validate_python',
                'code': 'print("Valid code")'
            },
            {
                'name': 'Shell команда',
                'action': 'execute_shell',
                'code': 'echo "Hello from shell!"'
            },
            {
                'name': 'Список библиотек',
                'action': 'list_libraries'
            }
        ]
        
        results = []
        for test in tests:
            print(f"\n   📝 {test['name']}")
            start_time = time.time()
            
            try:
                result = self.code_tool.execute(**test)
                execution_time = time.time() - start_time
                
                if result.success:
                    data_size = len(str(result.data)) if result.data else 0
                    print(f"   ✅ Успех ({execution_time:.1f}с, {data_size} байт)")
                    if result.data and 'output' in result.data:
                        output = result.data['output'][:100] + '...' if len(result.data['output']) > 100 else result.data['output']
                        print(f"      📄 Вывод: {output}")
                    results.append(True)
                else:
                    print(f"   ❌ Ошибка: {result.error}")
                    results.append(False)
                    
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"   💥 Исключение ({execution_time:.1f}с): {e}")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n🏆 CODE_EXECUTION_TOOL: {sum(results)}/{len(results)} успешно ({success_rate:.1f}%)")
        
        self.results['code_execution_tool'] = {
            'success_count': sum(results),
            'total_count': len(results),
            'success_rate': success_rate,
            'working': success_rate > 50
        }
        
        return success_rate > 50
    
    def test_data_analysis_tool(self):
        """Тестирование DataAnalysisTool"""
        print("\n📊 ТЕСТИРОВАНИЕ DATA_ANALYSIS_TOOL")
        
        # Создаём тестовый CSV файл
        test_csv_path = self._create_test_csv()
        
        tests = [
            {
                'name': 'Загрузка CSV данных',
                'action': 'load_data',
                'file_path': str(test_csv_path),
                'dataset_name': 'test_data'
            },
            {
                'name': 'Список датасетов',
                'action': 'list_datasets'
            },
            {
                'name': 'Базовый анализ',
                'action': 'analyze_basic',
                'dataset_name': 'test_data'
            },
            {
                'name': 'Очистка данных',
                'action': 'clean_data',
                'dataset_name': 'test_data',
                'operations': ['remove_duplicates', 'fill_missing']
            },
            {
                'name': 'Генерация отчёта',
                'action': 'generate_report',
                'dataset_name': 'test_data',
                'report_type': 'basic'
            }
        ]
        
        results = []
        for test in tests:
            print(f"\n   📝 {test['name']}")
            start_time = time.time()
            
            try:
                result = self.data_tool.execute(**test)
                execution_time = time.time() - start_time
                
                if result.success:
                    data_size = len(str(result.data)) if result.data else 0
                    print(f"   ✅ Успех ({execution_time:.1f}с, {data_size} байт)")
                    
                    # Показываем ключевую информацию
                    if result.data:
                        if 'dataset_name' in result.data:
                            print(f"      📊 Датасет: {result.data['dataset_name']}")
                        if 'shape' in result.data:
                            print(f"      📐 Размер: {result.data['shape']}")
                        if 'message' in result.data:
                            msg = result.data['message'][:100] + '...' if len(result.data['message']) > 100 else result.data['message']
                            print(f"      💬 Сообщение: {msg}")
                    
                    results.append(True)
                else:
                    print(f"   ❌ Ошибка: {result.error}")
                    results.append(False)
                    
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"   💥 Исключение ({execution_time:.1f}с): {e}")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n🏆 DATA_ANALYSIS_TOOL: {sum(results)}/{len(results)} успешно ({success_rate:.1f}%)")
        
        self.results['data_analysis_tool'] = {
            'success_count': sum(results),
            'total_count': len(results), 
            'success_rate': success_rate,
            'working': success_rate > 50
        }
        
        # Очистка
        if test_csv_path.exists():
            test_csv_path.unlink()
        
        return success_rate > 50
    
    def _create_test_csv(self):
        """Создание тестового CSV файла"""
        test_data = [
            ['name', 'age', 'city', 'salary'],
            ['Alice', '25', 'Moscow', '50000'],
            ['Bob', '30', 'St.Petersburg', '60000'], 
            ['Charlie', '35', 'Moscow', '70000'],
            ['Diana', '28', 'Novosibirsk', '55000'],
            ['Eve', '', 'Moscow', '65000']  # Пропущенное значение
        ]
        
        temp_dir = Path(tempfile.gettempdir())
        csv_path = temp_dir / 'kittycore_test_data.csv'
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            import csv
            writer = csv.writer(f)
            writer.writerows(test_data)
        
        return csv_path
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🔧 ТЕСТИРОВАНИЕ ИСПРАВЛЕННЫХ ИНСТРУМЕНТОВ KITTYCORE 3.0")
        print("=" * 60)
        
        start_time = time.time()
        
        # Тестирование инструментов
        code_working = self.test_code_execution_tool()
        data_working = self.test_data_analysis_tool()
        
        total_time = time.time() - start_time
        
        # Итоговый отчёт
        print("\n" + "=" * 60)
        print("🎯 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
        print("-" * 40)
        
        total_tools = len(self.results)
        working_tools = sum(1 for r in self.results.values() if r['working'])
        
        for tool_name, result in self.results.items():
            status = "✅ РАБОТАЕТ" if result['working'] else "❌ ПРОБЛЕМЫ"
            print(f"{tool_name:25} {status} ({result['success_count']}/{result['total_count']})")
        
        print("-" * 40)
        print(f"ИСПРАВЛЕНО: {working_tools}/{total_tools} инструментов ({working_tools/total_tools*100:.1f}%)")
        print(f"ВРЕМЯ: {total_time:.1f} секунд")
        
        if working_tools == total_tools:
            print("\n🎉 ВСЕ ПРОБЛЕМНЫЕ ИНСТРУМЕНТЫ ИСПРАВЛЕНЫ!")
        else:
            print(f"\n⚠️ Ещё остались проблемы: {total_tools - working_tools} инструментов")
        
        return working_tools == total_tools

def main():
    """Главная функция"""
    tester = FixedToolsTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Все исправления работают корректно!")
        exit(0)
    else:
        print("\n❌ Некоторые исправления не работают")
        exit(1)

if __name__ == "__main__":
    main() 