#!/usr/bin/env python3
"""
⚡ COMPREHENSIVE ТЕСТИРОВАНИЕ KITTYCORE 3.0 - ЧАСТЬ 3: ОСТАЛЬНЫЕ ИНСТРУМЕНТЫ
"""

import json
import time
import sys
import asyncio
from pathlib import Path

# Добавляем путь к KittyCore
sys.path.insert(0, str(Path(__file__).parent / 'kittycore'))

class ComprehensivePart3Tester:
    """⚡ Тестер остальных инструментов KittyCore 3.0"""
    
    def __init__(self):
        self.results = []
        self.honest_tools = set()
        self.dishonest_tools = set()
        print("🎯 Comprehensive Part 3 тестер инициализирован")
    
    def test_code_execution_tool(self):
        """⚡ Тест CodeExecutionTool"""
        print("   ⚡ Тестирую CodeExecutionTool...")
        start_time = time.time()
        
        try:
            from kittycore.tools.code_execution_tool import CodeExecutionTool
            tool = CodeExecutionTool()
            
            # Простой тест выполнения кода
            result = asyncio.run(tool.execute(
                code="print('Hello from KittyCore!')",
                language="python"
            ))
            
            execution_time = time.time() - start_time
            
            # Честная проверка
            if (hasattr(result, 'data') and result.data and 
                'Hello from KittyCore' in str(result.data)):
                self.honest_tools.add("code_execution")
                honesty = "✅ ЧЕСТНО"
                size = len(str(result.data))
            else:
                self.dishonest_tools.add("code_execution")
                honesty = "❌ ПОДОЗРИТЕЛЬНО"
                size = len(str(result.data)) if hasattr(result, 'data') else 0
            
            test_result = {
                'tool_name': 'code_execution',
                'action': 'python_execute',
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
                'tool_name': 'code_execution',
                'action': 'python_execute',
                'success': False,
                'execution_time': execution_time,
                'error': error_msg,
                'honesty': "❌ ОШИБКА"
            }
            
            self.dishonest_tools.add("code_execution")
            self.results.append(test_result)
            return test_result
    
    def test_security_tool(self):
        """🔒 Тест SecurityTool"""
        print("   🔒 Тестирую SecurityTool...")
        start_time = time.time()
        
        try:
            from kittycore.tools.security_tool import SecurityTool
            tool = SecurityTool()
            result = tool.execute(action="get_info")
            
            execution_time = time.time() - start_time
            
            # Честная проверка
            if hasattr(result, 'data') and result.data and len(str(result.data)) > 50:
                self.honest_tools.add("security_tool")
                honesty = "✅ ЧЕСТНО"
                size = len(str(result.data))
            else:
                self.dishonest_tools.add("security_tool")
                honesty = "❌ ПОДОЗРИТЕЛЬНО"
                size = len(str(result.data)) if hasattr(result, 'data') else 0
            
            test_result = {
                'tool_name': 'security_tool',
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
                'tool_name': 'security_tool',
                'action': 'get_info',
                'success': False,
                'execution_time': execution_time,
                'error': error_msg,
                'honesty': "❌ ОШИБКА"
            }
            
            self.dishonest_tools.add("security_tool")
            self.results.append(test_result)
            return test_result
    
    def test_email_tool(self):
        """📧 Тест EmailTool"""
        print("   📧 Тестирую EmailTool...")
        start_time = time.time()
        
        try:
            from kittycore.tools.email_tool import EmailTool
            tool = EmailTool()
            result = tool.execute(action="get_info")
            
            execution_time = time.time() - start_time
            
            # Честная проверка - EmailTool без SMTP должен давать ошибку или информацию
            if hasattr(result, 'data') and result.data:
                if 'error' in str(result.data).lower() or 'smtp' in str(result.data).lower():
                    self.honest_tools.add("email_tool")
                    honesty = "✅ ЧЕСТНО (правильная ошибка)"
                else:
                    self.dishonest_tools.add("email_tool")
                    honesty = "❌ ПОДОЗРИТЕЛЬНО (фиктивный успех)"
                size = len(str(result.data))
            else:
                self.dishonest_tools.add("email_tool")
                honesty = "❌ ПОДОЗРИТЕЛЬНО"
                size = 0
            
            test_result = {
                'tool_name': 'email_tool',
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
                'tool_name': 'email_tool',
                'action': 'get_info',
                'success': False,
                'execution_time': execution_time,
                'error': error_msg,
                'honesty': "❌ ОШИБКА"
            }
            
            self.dishonest_tools.add("email_tool")
            self.results.append(test_result)
            return test_result
    
    def test_data_analysis_tool(self):
        """📊 Тест DataAnalysisTool"""
        print("   📊 Тестирую DataAnalysisTool...")
        start_time = time.time()
        
        try:
            from kittycore.tools.data_analysis_tool import DataAnalysisTool
            tool = DataAnalysisTool()
            
            # Простой тест анализа данных
            result = asyncio.run(tool.execute(
                action="analyze_data",
                data=[1, 2, 3, 4, 5]
            ))
            
            execution_time = time.time() - start_time
            
            # Честная проверка
            if hasattr(result, 'data') and result.data and len(str(result.data)) > 50:
                self.honest_tools.add("data_analysis")
                honesty = "✅ ЧЕСТНО"
                size = len(str(result.data))
            else:
                self.dishonest_tools.add("data_analysis")
                honesty = "❌ ПОДОЗРИТЕЛЬНО"
                size = len(str(result.data)) if hasattr(result, 'data') else 0
            
            test_result = {
                'tool_name': 'data_analysis',
                'action': 'analyze_data',
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
                'tool_name': 'data_analysis',
                'action': 'analyze_data',
                'success': False,
                'execution_time': execution_time,
                'error': error_msg,
                'honesty': "❌ ОШИБКА"
            }
            
            self.dishonest_tools.add("data_analysis")
            self.results.append(test_result)
            return test_result
    
    def test_all_remaining_tools(self):
        """🚀 Тестирование всех остальных инструментов"""
        print("📋 ТЕСТИРОВАНИЕ ОСТАЛЬНЫХ ИНСТРУМЕНТОВ (ЧАСТЬ 3):")
        print("-" * 60)
        
        tools_to_test = [
            ("CodeExecutionTool", self.test_code_execution_tool),
            ("SecurityTool", self.test_security_tool),
            ("EmailTool", self.test_email_tool),
            ("DataAnalysisTool", self.test_data_analysis_tool),
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
📊 ИТОГИ COMPREHENSIVE ТЕСТИРОВАНИЯ - ЧАСТЬ 3:
{'='*60}
🔧 Всего остальных инструментов: {total_tools}
✅ Успешно запущено: {successful_tools}
🛡️ Честно работают: {honest_count}
❌ Проблемные: {len(self.dishonest_tools)}

🛡️ ЧЕСТНЫЕ ИНСТРУМЕНТЫ: {', '.join(self.honest_tools) if self.honest_tools else 'НЕТ'}
❌ ПРОБЛЕМНЫЕ ИНСТРУМЕНТЫ: {', '.join(self.dishonest_tools) if self.dishonest_tools else 'НЕТ'}

📈 ПРОЦЕНТ ЧЕСТНОСТИ: {(honest_count/total_tools*100):.1f}%
"""
        return summary

def main():
    """Главная функция тестирования части 3"""
    print("⚡ COMPREHENSIVE ТЕСТИРОВАНИЕ KITTYCORE 3.0 - ЧАСТЬ 3")
    print("=" * 60)
    print("🚀 Тестируем остальные инструменты!")
    print()
    
    tester = ComprehensivePart3Tester()
    
    start_time = time.time()
    tester.test_all_remaining_tools()
    total_time = time.time() - start_time
    
    print(tester.generate_summary())
    
    # Сохраняем результаты
    timestamp = int(time.time())
    results_file = f"comprehensive_part3_results_{timestamp}.json"
    
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