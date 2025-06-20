#!/usr/bin/env python3
"""
🔧 COMPREHENSIVE ТЕСТИРОВАНИЕ KITTYCORE 3.0 - ЧАСТЬ 1: БАЗОВЫЕ ИНСТРУМЕНТЫ
"""

import json
import time
import sys
from pathlib import Path

# Добавляем путь к KittyCore
sys.path.insert(0, str(Path(__file__).parent / 'kittycore'))

class ComprehensivePart1Tester:
    """🔧 Тестер базовых инструментов KittyCore 3.0"""
    
    def __init__(self):
        self.results = []
        self.honest_tools = set()
        self.dishonest_tools = set()
        print("🎯 Comprehensive Part 1 тестер инициализирован")
    
    def test_media_tool(self):
        """🎨 Тест MediaTool"""
        print("   🎨 Тестирую MediaTool...")
        start_time = time.time()
        
        try:
            from kittycore.tools.media_tool import MediaTool
            tool = MediaTool()
            result = tool.execute(action="get_info")
            
            execution_time = time.time() - start_time
            
            # Честная проверка
            if hasattr(result, 'data') and result.data and len(str(result.data)) > 50:
                self.honest_tools.add("media_tool")
                honesty = "✅ ЧЕСТНО"
                size = len(str(result.data))
            else:
                self.dishonest_tools.add("media_tool")
                honesty = "❌ ПОДОЗРИТЕЛЬНО"
                size = 0
            
            test_result = {
                'tool_name': 'media_tool',
                'action': 'get_info',
                'success': True,
                'execution_time': execution_time,
                'data_size': size,
                'honesty': honesty
            }
            
            print(f"      ⏱️ Время: {execution_time:.2f}с")
            print(f"      📊 Размер данных: {size} байт")
            print(f"      {honesty}")
            
            self.results.append(test_result)
            return test_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)[:100]
            print(f"      💥 ОШИБКА: {error_msg}")
            
            test_result = {
                'tool_name': 'media_tool',
                'action': 'get_info',
                'success': False,
                'execution_time': execution_time,
                'error': error_msg,
                'honesty': "❌ ОШИБКА"
            }
            
            self.dishonest_tools.add("media_tool")
            self.results.append(test_result)
            return test_result
    
    def test_system_tool(self):
        """💻 Тест SuperSystemTool"""
        print("   💻 Тестирую SuperSystemTool...")
        start_time = time.time()
        
        try:
            from kittycore.tools.super_system_tool import SuperSystemTool
            tool = SuperSystemTool()
            result = tool.execute(action="run_command", command="echo 'test'")
            
            execution_time = time.time() - start_time
            
            # Честная проверка - должен быть реальный вывод команды
            if hasattr(result, 'data') and 'test' in str(result.data):
                self.honest_tools.add("super_system_tool")
                honesty = "✅ ЧЕСТНО"
                size = len(str(result.data))
            else:
                self.dishonest_tools.add("super_system_tool")
                honesty = "❌ ПОДОЗРИТЕЛЬНО"
                size = 0
            
            test_result = {
                'tool_name': 'super_system_tool',
                'action': 'run_command',
                'success': True,
                'execution_time': execution_time,
                'data_size': size,
                'honesty': honesty
            }
            
            print(f"      ⏱️ Время: {execution_time:.2f}с")
            print(f"      📊 Размер данных: {size} байт")
            print(f"      {honesty}")
            
            self.results.append(test_result)
            return test_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)[:100]
            print(f"      💥 ОШИБКА: {error_msg}")
            
            test_result = {
                'tool_name': 'super_system_tool',
                'action': 'run_command',
                'success': False,
                'execution_time': execution_time,
                'error': error_msg,
                'honesty': "❌ ОШИБКА"
            }
            
            self.dishonest_tools.add("super_system_tool")
            self.results.append(test_result)
            return test_result
    
    def test_network_tool(self):
        """🌐 Тест NetworkTool"""
        print("   🌐 Тестирую NetworkTool...")
        start_time = time.time()
        
        try:
            from kittycore.tools.network_tool import NetworkTool
            tool = NetworkTool()
            result = tool.execute(action="get_info")
            
            execution_time = time.time() - start_time
            
            # Честная проверка
            if hasattr(result, 'data') and result.data and len(str(result.data)) > 100:
                self.honest_tools.add("network_tool")
                honesty = "✅ ЧЕСТНО"
                size = len(str(result.data))
            else:
                self.dishonest_tools.add("network_tool")
                honesty = "❌ ПОДОЗРИТЕЛЬНО"
                size = 0
            
            test_result = {
                'tool_name': 'network_tool',
                'action': 'get_info',
                'success': True,
                'execution_time': execution_time,
                'data_size': size,
                'honesty': honesty
            }
            
            print(f"      ⏱️ Время: {execution_time:.2f}с")
            print(f"      📊 Размер данных: {size} байт")
            print(f"      {honesty}")
            
            self.results.append(test_result)
            return test_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)[:100]
            print(f"      💥 ОШИБКА: {error_msg}")
            
            test_result = {
                'tool_name': 'network_tool',
                'action': 'get_info',
                'success': False,
                'execution_time': execution_time,
                'error': error_msg,
                'honesty': "❌ ОШИБКА"
            }
            
            self.dishonest_tools.add("network_tool")
            self.results.append(test_result)
            return test_result
    
    def test_all_basic_tools(self):
        """🚀 Тестирование всех базовых инструментов"""
        print("📋 ТЕСТИРОВАНИЕ БАЗОВЫХ ИНСТРУМЕНТОВ (ЧАСТЬ 1):")
        print("-" * 60)
        
        tools_to_test = [
            ("MediaTool", self.test_media_tool),
            ("SuperSystemTool", self.test_system_tool),
            ("NetworkTool", self.test_network_tool),
        ]
        
        for i, (tool_name, test_func) in enumerate(tools_to_test, 1):
            print(f"🔧 {i}/{len(tools_to_test)}: {tool_name}")
            test_func()
            print()
    
    def generate_summary(self):
        """📊 Генерация итогового отчёта"""
        total_tools = len(self.results)
        successful_tools = len([r for r in self.results if r['success']])
        honest_count = len(self.honest_tools)
        
        summary = f"""
📊 ИТОГИ COMPREHENSIVE ТЕСТИРОВАНИЯ - ЧАСТЬ 1:
{'='*60}
🔧 Всего инструментов: {total_tools}
✅ Успешно запущено: {successful_tools}
🛡️ Честно работают: {honest_count}
❌ Проблемные: {len(self.dishonest_tools)}

🛡️ ЧЕСТНЫЕ ИНСТРУМЕНТЫ: {', '.join(self.honest_tools) if self.honest_tools else 'НЕТ'}
❌ ПРОБЛЕМНЫЕ ИНСТРУМЕНТЫ: {', '.join(self.dishonest_tools) if self.dishonest_tools else 'НЕТ'}

📈 ПРОЦЕНТ ЧЕСТНОСТИ: {(honest_count/total_tools*100):.1f}%
"""
        return summary

def main():
    """Главная функция тестирования части 1"""
    print("🔧 COMPREHENSIVE ТЕСТИРОВАНИЕ KITTYCORE 3.0 - ЧАСТЬ 1")
    print("=" * 60)
    print("🚀 Тестируем базовые инструменты!")
    print()
    
    tester = ComprehensivePart1Tester()
    
    start_time = time.time()
    tester.test_all_basic_tools()
    total_time = time.time() - start_time
    
    print(tester.generate_summary())
    
    # Сохраняем результаты
    timestamp = int(time.time())
    results_file = f"comprehensive_part1_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total_time': total_time,
            'results': tester.results,
            'honest_tools': list(tester.honest_tools),
            'dishonest_tools': list(tester.dishonest_tools)
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Результаты сохранены в {results_file}")
    print(f"⏱️ Время тестирования: {total_time:.1f}с")

if __name__ == "__main__":
    main() 