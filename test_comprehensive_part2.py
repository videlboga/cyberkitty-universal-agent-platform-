#!/usr/bin/env python3
"""
🌐 COMPREHENSIVE ТЕСТИРОВАНИЕ KITTYCORE 3.0 - ЧАСТЬ 2: ВЕБ-ИНСТРУМЕНТЫ
"""

import json
import time
import sys
import asyncio
from pathlib import Path

# Добавляем путь к KittyCore
sys.path.insert(0, str(Path(__file__).parent / 'kittycore'))

class ComprehensivePart2Tester:
    """🌐 Тестер веб-инструментов KittyCore 3.0"""
    
    def __init__(self):
        self.results = []
        self.honest_tools = set()
        self.dishonest_tools = set()
        print("🎯 Comprehensive Part 2 тестер инициализирован")
    
    def test_web_search_tool(self):
        """🔍 Тест EnhancedWebSearchTool"""
        print("   🔍 Тестирую EnhancedWebSearchTool...")
        start_time = time.time()
        
        try:
            from kittycore.tools.enhanced_web_search_tool import EnhancedWebSearchTool
            tool = EnhancedWebSearchTool()
            
            # Простой тест поиска
            result = asyncio.run(tool.execute(
                query="KittyCore агентная система",
                max_results=3
            ))
            
            execution_time = time.time() - start_time
            
            # Честная проверка
            if hasattr(result, 'data') and result.data and len(str(result.data)) > 500:
                self.honest_tools.add("enhanced_web_search")
                honesty = "✅ ЧЕСТНО"
                size = len(str(result.data))
            else:
                self.dishonest_tools.add("enhanced_web_search")
                honesty = "❌ ПОДОЗРИТЕЛЬНО"
                size = len(str(result.data)) if hasattr(result, 'data') else 0
            
            test_result = {
                'tool_name': 'enhanced_web_search',
                'action': 'search',
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
                'tool_name': 'enhanced_web_search',
                'action': 'search',
                'success': False,
                'execution_time': execution_time,
                'error': error_msg,
                'honesty': "❌ ОШИБКА"
            }
            
            self.dishonest_tools.add("enhanced_web_search")
            self.results.append(test_result)
            return test_result
    
    def test_api_request_tool(self):
        """🌐 Тест API Request через requests"""
        print("   🌐 Тестирую API Request Tool...")
        start_time = time.time()
        
        try:
            import requests
            
            # Простой тест API запроса
            response = requests.get("https://httpbin.org/get", timeout=10)
            
            execution_time = time.time() - start_time
            
            # Честная проверка
            if response.status_code == 200 and len(response.text) > 200:
                self.honest_tools.add("api_request")
                honesty = "✅ ЧЕСТНО"
                size = len(response.text)
            else:
                self.dishonest_tools.add("api_request")
                honesty = "❌ ПОДОЗРИТЕЛЬНО"
                size = 0
            
            test_result = {
                'tool_name': 'api_request',
                'action': 'get_request',
                'success': True,
                'execution_time': execution_time,
                'data_size': size,
                'status_code': response.status_code,
                'honesty': honesty
            }
            
            print(f"      ⏱️ Время: {execution_time:.2f}с")
            print(f"      📊 Размер данных: {size} байт")
            print(f"      📡 Статус: {response.status_code}")
            print(f"      {honesty}")
            
            self.results.append(test_result)
            return test_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)[:100]
            print(f"      💥 ОШИБКА: {error_msg}")
            
            test_result = {
                'tool_name': 'api_request',
                'action': 'get_request',
                'success': False,
                'execution_time': execution_time,
                'error': error_msg,
                'honesty': "❌ ОШИБКА"
            }
            
            self.dishonest_tools.add("api_request")
            self.results.append(test_result)
            return test_result
    
    def test_web_scraping_tool(self):
        """🕷️ Тест EnhancedWebScrapingTool"""
        print("   🕷️ Тестирую EnhancedWebScrapingTool...")
        start_time = time.time()
        
        try:
            from kittycore.tools.enhanced_web_scraping_tool import EnhancedWebScrapingTool
            tool = EnhancedWebScrapingTool()
            
            # Простой тест скрапинга
            result = asyncio.run(tool.execute(
                url="https://httpbin.org/html",
                action="get_text"
            ))
            
            execution_time = time.time() - start_time
            
            # Честная проверка
            if hasattr(result, 'data') and result.data and len(str(result.data)) > 100:
                self.honest_tools.add("enhanced_web_scraping")
                honesty = "✅ ЧЕСТНО"
                size = len(str(result.data))
            else:
                self.dishonest_tools.add("enhanced_web_scraping")
                honesty = "❌ ПОДОЗРИТЕЛЬНО"
                size = len(str(result.data)) if hasattr(result, 'data') else 0
            
            test_result = {
                'tool_name': 'enhanced_web_scraping',
                'action': 'get_text',
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
                'tool_name': 'enhanced_web_scraping',
                'action': 'get_text',
                'success': False,
                'execution_time': execution_time,
                'error': error_msg,
                'honesty': "❌ ОШИБКА"
            }
            
            self.dishonest_tools.add("enhanced_web_scraping")
            self.results.append(test_result)
            return test_result
    
    def test_all_web_tools(self):
        """🚀 Тестирование всех веб-инструментов"""
        print("📋 ТЕСТИРОВАНИЕ ВЕБ-ИНСТРУМЕНТОВ (ЧАСТЬ 2):")
        print("-" * 60)
        
        tools_to_test = [
            ("EnhancedWebSearchTool", self.test_web_search_tool),
            ("API Request Tool", self.test_api_request_tool),
            ("EnhancedWebScrapingTool", self.test_web_scraping_tool),
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
📊 ИТОГИ COMPREHENSIVE ТЕСТИРОВАНИЯ - ЧАСТЬ 2:
{'='*60}
🔧 Всего веб-инструментов: {total_tools}
✅ Успешно запущено: {successful_tools}
🛡️ Честно работают: {honest_count}
❌ Проблемные: {len(self.dishonest_tools)}

🛡️ ЧЕСТНЫЕ ВЕБ-ИНСТРУМЕНТЫ: {', '.join(self.honest_tools) if self.honest_tools else 'НЕТ'}
❌ ПРОБЛЕМНЫЕ ВЕБ-ИНСТРУМЕНТЫ: {', '.join(self.dishonest_tools) if self.dishonest_tools else 'НЕТ'}

📈 ПРОЦЕНТ ЧЕСТНОСТИ ВЕБ-ИНСТРУМЕНТОВ: {(honest_count/total_tools*100):.1f}%
"""
        return summary

def main():
    """Главная функция тестирования части 2"""
    print("🌐 COMPREHENSIVE ТЕСТИРОВАНИЕ KITTYCORE 3.0 - ЧАСТЬ 2")
    print("=" * 60)
    print("🚀 Тестируем веб-инструменты!")
    print()
    
    tester = ComprehensivePart2Tester()
    
    start_time = time.time()
    tester.test_all_web_tools()
    total_time = time.time() - start_time
    
    print(tester.generate_summary())
    
    # Сохраняем результаты
    timestamp = int(time.time())
    results_file = f"comprehensive_part2_results_{timestamp}.json"
    
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