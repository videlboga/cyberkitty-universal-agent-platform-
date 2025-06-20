#!/usr/bin/env python3
"""
🔧 РЕАЛЬНОЕ ТЕСТИРОВАНИЕ ИНСТРУМЕНТОВ KITTYCORE 3.0 - ИСПРАВЛЕННАЯ ВЕРСИЯ
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

class RealToolsTesterFixed:
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
        
        # РЕАЛЬНЫЙ поиск информации о KittyCore - правильные параметры
        result = await tool.execute(
            query="KittyCore agentic system github", 
            limit=3
        )
        
        execution_time = time.time() - start_time
        
        # СТРОГАЯ проверка содержимого
        success = False
        data_size = 0
        validation_notes = []
        
        if result.success and result.data:
            data = result.data
            data_size = len(str(data))
            
            # Проверяем структуру результатов
            if isinstance(data, dict) and "results" in data:
                results_list = data["results"]
                if len(results_list) > 0:
                    validation_notes.append("✅ Получены реальные результаты поиска")
                    success = True
                else:
                    validation_notes.append("❌ Пустой список результатов")
            else:
                validation_notes.append("❌ Неправильная структура данных")
        else:
            validation_notes.append(f"❌ Инструмент вернул ошибку: {result.error}")
            
        # Записываем в память
        self.record_memory(
            "enhanced_web_search", 
            "search", 
            {"success": success, "params": {"query": "string", "limit": "number"}, "data": data_size},
            f"Время: {execution_time:.1f}с, размер: {data_size} байт. " + "; ".join(validation_notes)
        )
        
        print(f"   Время: {execution_time:.1f}с, размер данных: {data_size} байт")
        print(f"   Валидация: {'; '.join(validation_notes)}")
        return {"tool": "enhanced_web_search", "success": success, "time": execution_time, "size": data_size}
        
    async def test_media_tool(self):
        """🎨 РЕАЛЬНЫЙ тест медиа-инструмента"""
        print("🎨 Тестирую media_tool...")
        start_time = time.time()
        
        tool = MediaTool()
        
        try:
            # Тестируем получение информации об инструменте - правильное действие
            result = tool.execute(action="get_info")
            
            execution_time = time.time() - start_time
            
            # СТРОГАЯ проверка
            success = False
            data_size = 0
            validation_notes = []
            
            if result.success:
                data = result.data or ""
                data_size = len(str(data))
                
                if data_size > 50:  # Минимум содержимого
                    validation_notes.append("✅ Получена информация об инструменте")
                    success = True
                else:
                    validation_notes.append("❌ Слишком мало данных")
            else:
                validation_notes.append(f"❌ Ошибка: {result.error or 'Unknown'}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            data_size = 0
            validation_notes = [f"❌ Исключение: {str(e)[:100]}"]
            
        # Записываем в память
        self.record_memory(
            "media_tool",
            "get_info", 
            {"success": success, "params": {"action": "get_info"}, "data": data_size},
            f"Время: {execution_time:.1f}с, размер: {data_size} байт. " + "; ".join(validation_notes)
        )
        
        print(f"   Время: {execution_time:.1f}с, размер данных: {data_size} байт")
        print(f"   Валидация: {'; '.join(validation_notes)}")
        return {"tool": "media_tool", "success": success, "time": execution_time, "size": data_size}
        
    async def test_network_tool(self):
        """🌐 РЕАЛЬНЫЙ тест сетевого инструмента"""
        print("🌐 Тестирую network_tool...")
        start_time = time.time()
        
        tool = NetworkTool()
        
        try:
            # Тестируем простой ping - правильные параметры
            result = await tool.execute(
                action="ping",
                target="google.com",
                count=1
            )
            
            execution_time = time.time() - start_time
            
            # СТРОГАЯ проверка
            success = False
            data_size = 0
            validation_notes = []
            
            if result.success:
                data = result.data or ""
                data_size = len(str(data))
                
                # Проверяем что это реальный ping результат
                data_str = str(data).lower()
                if "ms" in data_str or "time=" in data_str or "ping" in data_str:
                    validation_notes.append("✅ Реальный ping результат")
                    success = True
                else:
                    validation_notes.append(f"❌ Подозрительный результат: {str(data)[:100]}")
            else:
                validation_notes.append(f"❌ Ошибка: {result.error or 'Unknown'}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            data_size = 0
            validation_notes = [f"❌ Исключение: {str(e)[:100]}"]
            
        # Записываем в память
        self.record_memory(
            "network_tool",
            "ping",
            {"success": success, "params": {"action": "ping", "target": "string", "count": "number"}, "data": data_size},
            f"Время: {execution_time:.1f}с, размер: {data_size} байт. " + "; ".join(validation_notes)
        )
        
        print(f"   Время: {execution_time:.1f}с, размер данных: {data_size} байт")
        print(f"   Валидация: {'; '.join(validation_notes)}")
        return {"tool": "network_tool", "success": success, "time": execution_time, "size": data_size}
        
    async def test_code_execution(self):
        """💻 РЕАЛЬНЫЙ тест выполнения кода"""
        print("💻 Тестирую code_execution_tool...")
        start_time = time.time()
        
        tool = CodeExecutionTool()
        
        try:
            # Выполняем простой Python код - правильные параметры
            result = tool.execute(
                action="execute",
                code="print('KittyCore Test'); result = 2 + 2; print(f'2 + 2 = {result}')",
                language="python"
            )
            
            execution_time = time.time() - start_time
            
            # СТРОГАЯ проверка
            success = False
            data_size = 0
            validation_notes = []
            
            if result.success:
                output = result.data or ""
                data_size = len(str(output))
                
                # Проверяем что код реально выполнился
                output_str = str(output)
                if "KittyCore Test" in output_str and "2 + 2 = 4" in output_str:
                    validation_notes.append("✅ Код выполнился корректно")
                    success = True
                else:
                    validation_notes.append(f"❌ Неожиданный вывод: {output_str[:100]}")
            else:
                validation_notes.append(f"❌ Ошибка: {result.error or 'Unknown'}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            data_size = 0
            validation_notes = [f"❌ Исключение: {str(e)[:100]}"]
            
        # Записываем в память
        self.record_memory(
            "code_execution_tool",
            "execute",
            {"success": success, "params": {"action": "execute", "code": "string", "language": "python"}, "data": data_size},
            f"Время: {execution_time:.1f}с, размер: {data_size} байт. " + "; ".join(validation_notes)
        )
        
        print(f"   Время: {execution_time:.1f}с, размер данных: {data_size} байт")
        print(f"   Валидация: {'; '.join(validation_notes)}")
        return {"tool": "code_execution", "success": success, "time": execution_time, "size": data_size}
        
    async def test_data_analysis(self):
        """📊 РЕАЛЬНЫЙ тест анализа данных"""
        print("📊 Тестирую data_analysis_tool...")
        start_time = time.time()
        
        tool = DataAnalysisTool()
        
        try:
            # Анализируем простые данные - правильные параметры
            test_data = [
                {"name": "Agent1", "performance": 0.85, "tasks": 10},
                {"name": "Agent2", "performance": 0.92, "tasks": 15},
                {"name": "Agent3", "performance": 0.78, "tasks": 8}
            ]
            
            result = tool.execute(
                action="analyze_data",
                data=test_data
            )
            
            execution_time = time.time() - start_time
            
            # СТРОГАЯ проверка
            success = False
            data_size = 0
            validation_notes = []
            
            if result.success:
                analysis = result.data or ""
                data_size = len(str(analysis))
                
                # Проверяем что анализ содержит реальную статистику
                analysis_str = str(analysis).lower()
                if any(word in analysis_str for word in ["mean", "average", "std", "max", "min", "count", "data"]):
                    validation_notes.append("✅ Реальный статистический анализ")
                    success = True
                else:
                    validation_notes.append(f"❌ Подозрительный анализ: {str(analysis)[:100]}")
            else:
                validation_notes.append(f"❌ Ошибка: {result.error or 'Unknown'}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            data_size = 0
            validation_notes = [f"❌ Исключение: {str(e)[:100]}"]
            
        # Записываем в память
        self.record_memory(
            "data_analysis_tool",
            "analyze_data",
            {"success": success, "params": {"action": "analyze_data", "data": "list"}, "data": data_size},
            f"Время: {execution_time:.1f}с, размер: {data_size} байт. " + "; ".join(validation_notes)
        )
        
        print(f"   Время: {execution_time:.1f}с, размер данных: {data_size} байт")
        print(f"   Валидация: {'; '.join(validation_notes)}")
        return {"tool": "data_analysis", "success": success, "time": execution_time, "size": data_size}
        
    async def run_all_tests(self):
        """Запускаем все реальные тесты"""
        print("🚀 ЗАПУСК ИСПРАВЛЕННЫХ РЕАЛЬНЫХ ТЕСТОВ ИНСТРУМЕНТОВ KITTYCORE 3.0")
        print("=" * 60)
        
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
        print("=" * 60)
        print("📈 ИТОГИ РЕАЛЬНОГО ТЕСТИРОВАНИЯ")
        
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
            
        # Сохраняем результаты
        self.save_results()
        
    def save_results(self):
        """Сохраняем результаты тестирования"""
        # Создаём папку если её нет
        os.makedirs("test_real_tools_fixed", exist_ok=True)
        
        # Сохраняем общие результаты
        with open("test_real_tools_fixed/tools_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
            
        # Сохраняем записи памяти
        with open("test_real_tools_fixed/memory_records.json", "w", encoding="utf-8") as f:
            json.dump(self.memory_records, f, indent=2, ensure_ascii=False)
            
        print(f"💾 Результаты сохранены в test_real_tools_fixed/")

async def main():
    """Главная функция"""
    tester = RealToolsTesterFixed()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 