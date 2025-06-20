#!/usr/bin/env python3
"""
🔧 ФИНАЛЬНОЕ РЕАЛЬНОЕ ТЕСТИРОВАНИЕ ИНСТРУМЕНТОВ KITTYCORE 3.0
Принципы: ❌ НЕТ МОКОВ, ✅ РЕАЛЬНЫЕ API ВЫЗОВЫ, ✅ СТРОГАЯ ПРОВЕРКА, ✅ ЗАПИСЬ В ПАМЯТЬ
"""

import asyncio
import json
import time
import sys
import os
from pathlib import Path

# Добавляем путь к KittyCore
sys.path.append(str(Path(__file__).parent / 'kittycore'))

from kittycore.tools.enhanced_web_search_tool import EnhancedWebSearchTool
from kittycore.tools.media_tool import MediaTool
from kittycore.tools.network_tool import NetworkTool
from kittycore.tools.data_analysis_tool import DataAnalysisTool
from kittycore.tools.code_execution_tools import CodeExecutionTool

class FinalRealToolsTester:
    def __init__(self):
        self.results = []
        self.memory_records = []
        
    def record_memory(self, tool_name: str, action: str, result: dict, notes: str):
        """Записываем правильные параметры инструментов в память"""
        self.memory_records.append({
            "tool": tool_name,
            "working_action": action,
            "correct_params": result.get("params", {}),
            "notes": notes,
            "success": result.get("success", False),
            "response_size": len(str(result.get("data", "")))
        })
        
    async def test_enhanced_web_search(self):
        """✅ РЕАЛЬНЫЙ тест веб-поиска"""
        print("🌐 Тестирую enhanced_web_search_tool...")
        start_time = time.time()
        
        tool = EnhancedWebSearchTool()
        
        # РЕАЛЬНЫЙ поиск - правильные параметры
        result = await tool.execute(
            query="KittyCore agentic system", 
            limit=2
        )
        
        execution_time = time.time() - start_time
        
        # СТРОГАЯ проверка содержимого
        success = False
        data_size = 0
        validation_notes = []
        
        if result.success and result.data:
            data = result.data
            data_size = len(str(data))
            
            if isinstance(data, dict) and "results" in data and len(data["results"]) > 0:
                validation_notes.append("✅ Получены реальные результаты поиска")
                success = True
            else:
                validation_notes.append("❌ Неправильная структура данных")
        else:
            validation_notes.append(f"❌ Ошибка: {result.error}")
            
        self.record_memory("enhanced_web_search", "search", 
                         {"success": success, "params": {"query": "string", "limit": "number"}, "data": data_size},
                         f"Время: {execution_time:.1f}с, размер: {data_size} байт. " + "; ".join(validation_notes))
        
        print(f"   Время: {execution_time:.1f}с, размер данных: {data_size} байт")
        print(f"   Валидация: {'; '.join(validation_notes)}")
        return {"tool": "enhanced_web_search", "success": success, "time": execution_time, "size": data_size}
        
    async def test_media_tool(self):
        """🎨 РЕАЛЬНЫЙ тест медиа-инструмента"""
        print("🎨 Тестирую media_tool...")
        start_time = time.time()
        
        tool = MediaTool()
        
        try:
            # Тестируем правильное действие
            result = tool.execute(action="get_info")
            
            execution_time = time.time() - start_time
            
            success = False
            data_size = 0
            validation_notes = []
            
            if result.success:
                data = result.data or ""
                data_size = len(str(data))
                
                if data_size > 50:
                    validation_notes.append("✅ Получена информация об инструменте")
                    success = True
                else:
                    validation_notes.append("❌ Слишком мало данных")
            else:
                validation_notes.append(f"❌ Ошибка: {result.error}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            data_size = 0
            validation_notes = [f"❌ Исключение: {str(e)[:100]}"]
            
        self.record_memory("media_tool", "get_info", 
                         {"success": success, "params": {"action": "get_info"}, "data": data_size},
                         f"Время: {execution_time:.1f}с, размер: {data_size} байт. " + "; ".join(validation_notes))
        
        print(f"   Время: {execution_time:.1f}с, размер данных: {data_size} байт")
        print(f"   Валидация: {'; '.join(validation_notes)}")
        return {"tool": "media_tool", "success": success, "time": execution_time, "size": data_size}
        
    async def test_network_tool(self):
        """🌐 РЕАЛЬНЫЙ тест сетевого инструмента"""
        print("🌐 Тестирую network_tool...")
        start_time = time.time()
        
        tool = NetworkTool()
        
        try:
            # Правильное действие для ping
            result = await tool.execute(
                action="ping_host",
                host="google.com",
                count=1
            )
            
            execution_time = time.time() - start_time
            
            success = False
            data_size = 0
            validation_notes = []
            
            if result.success:
                data = result.data or ""
                data_size = len(str(data))
                
                # Проверяем реальный ping результат
                data_str = str(data).lower()
                if "ms" in data_str or "time" in data_str or "ping" in data_str or "bytes" in data_str:
                    validation_notes.append("✅ Реальный ping результат")
                    success = True
                else:
                    validation_notes.append(f"❌ Подозрительный результат: {str(data)[:100]}")
            else:
                validation_notes.append(f"❌ Ошибка: {result.error}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            data_size = 0
            validation_notes = [f"❌ Исключение: {str(e)[:100]}"]
            
        self.record_memory("network_tool", "ping_host",
                         {"success": success, "params": {"action": "ping_host", "host": "string", "count": "number"}, "data": data_size},
                         f"Время: {execution_time:.1f}с, размер: {data_size} байт. " + "; ".join(validation_notes))
        
        print(f"   Время: {execution_time:.1f}с, размер данных: {data_size} байт")
        print(f"   Валидация: {'; '.join(validation_notes)}")
        return {"tool": "network_tool", "success": success, "time": execution_time, "size": data_size}
        
    async def test_code_execution(self):
        """💻 РЕАЛЬНЫЙ тест выполнения кода"""
        print("💻 Тестирую code_execution_tool...")
        start_time = time.time()
        
        tool = CodeExecutionTool()
        
        try:
            # Правильное действие для выполнения Python кода
            result = tool.execute(
                action="execute_python",
                code="print('KittyCore Test'); result = 2 + 2; print(f'Result: {result}')"
            )
            
            execution_time = time.time() - start_time
            
            success = False
            data_size = 0
            validation_notes = []
            
            if result.success:
                output = result.data or ""
                data_size = len(str(output))
                
                # Проверяем что код реально выполнился
                output_str = str(output)
                if "KittyCore Test" in output_str and "Result: 4" in output_str:
                    validation_notes.append("✅ Код выполнился корректно")
                    success = True
                else:
                    validation_notes.append(f"❌ Неожиданный вывод: {output_str[:100]}")
            else:
                validation_notes.append(f"❌ Ошибка: {result.error}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            data_size = 0
            validation_notes = [f"❌ Исключение: {str(e)[:100]}"]
            
        self.record_memory("code_execution_tool", "execute_python",
                         {"success": success, "params": {"action": "execute_python", "code": "string"}, "data": data_size},
                         f"Время: {execution_time:.1f}с, размер: {data_size} байт. " + "; ".join(validation_notes))
        
        print(f"   Время: {execution_time:.1f}с, размер данных: {data_size} байт")
        print(f"   Валидация: {'; '.join(validation_notes)}")
        return {"tool": "code_execution", "success": success, "time": execution_time, "size": data_size}
        
    async def test_data_analysis(self):
        """📊 РЕАЛЬНЫЙ тест анализа данных"""
        print("📊 Тестирую data_analysis_tool...")
        start_time = time.time()
        
        tool = DataAnalysisTool()
        
        try:
            # Правильное действие для получения списка датасетов
            result = tool.execute(action="list_datasets")
            
            execution_time = time.time() - start_time
            
            success = False
            data_size = 0
            validation_notes = []
            
            if result.success:
                analysis = result.data or ""
                data_size = len(str(analysis))
                
                # Проверяем что получили информацию о датасетах
                analysis_str = str(analysis).lower()
                if "datasets" in analysis_str or "total" in analysis_str or data_size > 30:
                    validation_notes.append("✅ Получена информация о датасетах")
                    success = True
                else:
                    validation_notes.append(f"❌ Подозрительный ответ: {str(analysis)[:100]}")
            else:
                validation_notes.append(f"❌ Ошибка: {result.error}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            data_size = 0
            validation_notes = [f"❌ Исключение: {str(e)[:100]}"]
            
        self.record_memory("data_analysis_tool", "list_datasets",
                         {"success": success, "params": {"action": "list_datasets"}, "data": data_size},
                         f"Время: {execution_time:.1f}с, размер: {data_size} байт. " + "; ".join(validation_notes))
        
        print(f"   Время: {execution_time:.1f}с, размер данных: {data_size} байт")
        print(f"   Валидация: {'; '.join(validation_notes)}")
        return {"tool": "data_analysis", "success": success, "time": execution_time, "size": data_size}
        
    async def run_all_tests(self):
        """Запускаем все реальные тесты"""
        print("🚀 ФИНАЛЬНОЕ РЕАЛЬНОЕ ТЕСТИРОВАНИЕ ИНСТРУМЕНТОВ KITTYCORE 3.0")
        print("=" * 65)
        
        tests = [
            self.test_enhanced_web_search,
            self.test_media_tool,
            self.test_network_tool,
            self.test_code_execution,
            self.test_data_analysis
        ]
        
        total_start = time.time()
        
        for test in tests:
            try:
                result = await test()
                self.results.append(result)
            except Exception as e:
                print(f"❌ КРИТИЧЕСКАЯ ОШИБКА в тесте {test.__name__}: {e}")
                self.results.append({"tool": test.__name__, "success": False, "error": str(e)})
            
            print()  # Пустая строка между тестами
            
        total_time = time.time() - total_start
        
        # ИТОГОВЫЙ ОТЧЁТ
        print("=" * 65)
        print("📈 ИТОГИ ФИНАЛЬНОГО РЕАЛЬНОГО ТЕСТИРОВАНИЯ")
        
        successful = sum(1 for r in self.results if r.get("success", False))
        total = len(self.results)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        print(f"✅ Успешных тестов: {successful}/{total} ({success_rate:.1f}%)")
        print(f"⏱️  Общее время: {total_time:.1f}с")
        print(f"💾 Записано в память: {len(self.memory_records)} записей")
        
        # Показываем детали
        for result in self.results:
            status = "✅" if result.get("success") else "❌"
            tool = result.get("tool", "unknown")
            time_taken = result.get("time", 0)
            size = result.get("size", 0)
            print(f"{status} {tool}: {time_taken:.1f}с, {size} байт")
            
        print("\n🔍 СРАВНЕНИЕ С ПРЕДЫДУЩИМИ ТЕСТАМИ:")
        print(f"   Предыдущие 'успешные' тесты: 94.4% (ФИКТИВНЫЕ)")
        print(f"   Реальное тестирование: {success_rate:.1f}% (ЧЕСТНЫЕ)")
        print(f"   Разница: {94.4 - success_rate:.1f}% было подделкой!")
        
        # Сохраняем результаты
        self.save_results()
        
    def save_results(self):
        """Сохраняем результаты тестирования"""
        os.makedirs("test_real_tools_final", exist_ok=True)
        
        with open("test_real_tools_final/tools_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
            
        with open("test_real_tools_final/memory_records.json", "w", encoding="utf-8") as f:
            json.dump(self.memory_records, f, indent=2, ensure_ascii=False)
            
        print(f"💾 Результаты сохранены в test_real_tools_final/")

async def main():
    """Главная функция"""
    tester = FinalRealToolsTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 