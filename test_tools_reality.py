#!/usr/bin/env python3
"""
🚀 РЕАЛЬНОЕ ТЕСТИРОВАНИЕ ИНСТРУМЕНТОВ KITTYCORE 3.0

РЕВОЛЮЦИОННЫЕ ПРИНЦИПЫ:
❌ НЕТ МОКОВ - только реальная работа
❌ НЕТ ФИКТИВНЫХ ОТВЕТОВ  
❌ НЕТ "len(text) > 20" валидации
✅ РЕАЛЬНЫЕ API вызовы
✅ РЕАЛЬНАЯ проверка результатов
✅ РЕАЛЬНАЯ работа с файлами/сетью
"""

import asyncio
import time
import json
import os
import tempfile
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class RealTestResult:
    """Результат реального теста инструмента"""
    tool_name: str
    success: bool
    execution_time: float
    real_output: Optional[str] = None
    error_message: Optional[str] = None
    data_size: int = 0
    api_calls_made: int = 0
    files_created: int = 0

class ToolRealityTester:
    """Тестировщик реальности инструментов"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="kittycore_reality_"))
        self.results: List[RealTestResult] = []
        
    async def test_enhanced_web_search(self) -> RealTestResult:
        """РЕАЛЬНЫЙ тест веб-поиска"""
        print("🔍 Тестирую РЕАЛЬНЫЙ веб-поиск...")
        start_time = time.time()
        
        try:
            from kittycore.tools import DEFAULT_TOOLS
            tool = DEFAULT_TOOLS.get_tool("enhanced_web_search")
            
            if not tool:
                return RealTestResult("enhanced_web_search", False, 0, error_message="Tool not found")
            
            # РЕАЛЬНЫЙ поиск Python
            result = await tool.execute(query="Python programming language", max_results=3)
            execution_time = time.time() - start_time
            
            # РЕАЛЬНАЯ валидация
            success = (
                result.success and 
                result.data and
                len(str(result.data)) > 100 and  # Реальный контент
                ("python" in str(result.data).lower() or "programming" in str(result.data).lower())
            )
            
            return RealTestResult(
                "enhanced_web_search", 
                success, 
                execution_time,
                real_output=str(result.data)[:200] if result.data else None,
                data_size=len(str(result.data)) if result.data else 0,
                api_calls_made=1
            )
            
        except Exception as e:
            return RealTestResult("enhanced_web_search", False, time.time() - start_time, error_message=str(e))
    
    async def test_enhanced_web_scraping(self) -> RealTestResult:
        """РЕАЛЬНЫЙ тест веб-скрапинга"""
        print("🕷️ Тестирую РЕАЛЬНЫЙ веб-скрапинг...")
        start_time = time.time()
        
        try:
            from kittycore.tools import DEFAULT_TOOLS
            tool = DEFAULT_TOOLS.get_tool("enhanced_web_scraping")
            
            if not tool:
                return RealTestResult("enhanced_web_scraping", False, 0, error_message="Tool not found")
            
            # РЕАЛЬНЫЙ скрапинг httpbin (надёжный тестовый сайт)
            result = await tool.execute(url="https://httpbin.org/html")
            execution_time = time.time() - start_time
            
            # РЕАЛЬНАЯ валидация HTML
            success = (
                result.success and 
                result.data and
                "<html>" in str(result.data).lower() and
                len(str(result.data)) > 50
            )
            
            return RealTestResult(
                "enhanced_web_scraping", 
                success, 
                execution_time,
                real_output=str(result.data)[:200] if result.data else None,
                data_size=len(str(result.data)) if result.data else 0,
                api_calls_made=1
            )
            
        except Exception as e:
            return RealTestResult("enhanced_web_scraping", False, time.time() - start_time, error_message=str(e))
    
    async def test_api_request(self) -> RealTestResult:
        """РЕАЛЬНЫЙ тест API запросов"""
        print("🌐 Тестирую РЕАЛЬНЫЕ API запросы...")
        start_time = time.time()
        
        try:
            from kittycore.tools import DEFAULT_TOOLS
            tool = DEFAULT_TOOLS.get_tool("api_request")
            
            if not tool:
                return RealTestResult("api_request", False, 0, error_message="Tool not found")
            
            # РЕАЛЬНЫЙ API запрос к httpbin
            result = await tool.execute(
                url="https://httpbin.org/json",
                method="GET"
            )
            execution_time = time.time() - start_time
            
            # РЕАЛЬНАЯ валидация JSON
            success = False
            if result.success and result.data:
                try:
                    if isinstance(result.data, dict):
                        success = True
                    elif isinstance(result.data, str):
                        json.loads(result.data)
                        success = True
                except:
                    pass
            
            return RealTestResult(
                "api_request", 
                success, 
                execution_time,
                real_output=str(result.data)[:200] if result.data else None,
                data_size=len(str(result.data)) if result.data else 0,
                api_calls_made=1
            )
            
        except Exception as e:
            return RealTestResult("api_request", False, time.time() - start_time, error_message=str(e))
    
    async def test_code_execution(self) -> RealTestResult:
        """РЕАЛЬНЫЙ тест выполнения кода"""
        print("💻 Тестирую РЕАЛЬНОЕ выполнение кода...")
        start_time = time.time()
        
        try:
            from kittycore.tools import DEFAULT_TOOLS
            tool = DEFAULT_TOOLS.get_tool("code_execution")
            
            if not tool:
                return RealTestResult("code_execution", False, 0, error_message="Tool not found")
            
            # РЕАЛЬНОЕ выполнение Python
            test_code = """
import math
result = math.sqrt(16) + math.pi
print(f"Результат: {result}")
"""
            
            result = await tool.execute(code=test_code, language="python")
            execution_time = time.time() - start_time
            
            # РЕАЛЬНАЯ валидация результата
            success = (
                result.success and 
                result.data and
                "Результат:" in str(result.data) and
                "7.14" in str(result.data)  # sqrt(16) + pi ≈ 7.14
            )
            
            return RealTestResult(
                "code_execution", 
                success, 
                execution_time,
                real_output=str(result.data)[:200] if result.data else None,
                data_size=len(str(result.data)) if result.data else 0
            )
            
        except Exception as e:
            return RealTestResult("code_execution", False, time.time() - start_time, error_message=str(e))
    
    async def test_super_system_tool(self) -> RealTestResult:
        """РЕАЛЬНЫЙ тест системного инструмента"""
        print("🚀 Тестирую РЕАЛЬНЫЕ системные операции...")
        start_time = time.time()
        
        try:
            from kittycore.tools import DEFAULT_TOOLS
            tool = DEFAULT_TOOLS.get_tool("super_system_tool")
            
            if not tool:
                return RealTestResult("super_system_tool", False, 0, error_message="Tool not found")
            
            # РЕАЛЬНАЯ операция - создание файла
            test_file = self.temp_dir / "system_test.txt"
            test_content = "KittyCore 3.0 Reality Test"
            
            result = await tool.execute(
                action="write_file",
                file_path=str(test_file),
                content=test_content
            )
            execution_time = time.time() - start_time
            
            # РЕАЛЬНАЯ валидация - файл создан?
            success = (
                result.success and 
                test_file.exists() and
                test_file.read_text().strip() == test_content
            )
            
            files_created = 1 if test_file.exists() else 0
            
            return RealTestResult(
                "super_system_tool", 
                success, 
                execution_time,
                real_output=f"File created: {test_file.exists()}",
                files_created=files_created
            )
            
        except Exception as e:
            return RealTestResult("super_system_tool", False, time.time() - start_time, error_message=str(e))
    
    async def test_image_generation(self) -> RealTestResult:
        """РЕАЛЬНЫЙ тест генерации изображений"""
        print("🎨 Тестирую РЕАЛЬНУЮ генерацию изображений...")
        start_time = time.time()
        
        try:
            from kittycore.tools import DEFAULT_TOOLS
            tool = DEFAULT_TOOLS.get_tool("image_generation")
            
            if not tool:
                return RealTestResult("image_generation", False, 0, error_message="Tool not found")
            
            # РЕАЛЬНАЯ генерация изображения
            result = await tool.execute(
                prompt="A simple blue circle on white background",
                width=256,
                height=256
            )
            execution_time = time.time() - start_time
            
            # РЕАЛЬНАЯ валидация изображения
            success = (
                result.success and 
                result.data and
                (isinstance(result.data, bytes) or "image" in str(result.data).lower())
            )
            
            data_size = len(result.data) if isinstance(result.data, bytes) else len(str(result.data))
            
            return RealTestResult(
                "image_generation", 
                success, 
                execution_time,
                real_output=f"Image data: {type(result.data).__name__}",
                data_size=data_size,
                api_calls_made=1
            )
            
        except Exception as e:
            return RealTestResult("image_generation", False, time.time() - start_time, error_message=str(e))

    async def run_reality_tests(self) -> Dict[str, Any]:
        """Запуск всех реальных тестов"""
        print("🚀" + "="*50)
        print("🚀 KITTYCORE 3.0 - ТЕСТИРОВАНИЕ РЕАЛЬНОСТИ")  
        print("🚀" + "="*50)
        print("❌ НЕТ МОКОВ | ✅ ТОЛЬКО РЕАЛЬНАЯ РАБОТА")
        print()
        
        # Список тестов
        tests = [
            self.test_enhanced_web_search,
            self.test_enhanced_web_scraping, 
            self.test_api_request,
            self.test_code_execution,
            self.test_super_system_tool,
            self.test_image_generation,
        ]
        
        # Выполняем тесты
        total_start = time.time()
        for i, test_func in enumerate(tests, 1):
            print(f"{i}/{len(tests)} {test_func.__name__}")
            result = await test_func()
            self.results.append(result)
            
            status = "✅" if result.success else "❌"
            time_str = f"{result.execution_time:.1f}с"
            print(f"    {status} {time_str}")
            
            if result.error_message:
                print(f"    ⚠️ {result.error_message[:50]}...")
            elif result.real_output:
                print(f"    📊 {result.real_output[:50]}...")
                
        total_time = time.time() - total_start
        
        # Статистика
        successful = sum(1 for r in self.results if r.success)
        success_rate = successful / len(self.results)
        
        print("\n🚀" + "="*50)
        print("🚀 РЕЗУЛЬТАТЫ РЕАЛЬНОСТИ")
        print("🚀" + "="*50)
        
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"   ✅ Успешных: {successful}/{len(self.results)} ({success_rate:.1%})")
        print(f"   ⏱️ Общее время: {total_time:.1f}с")
        print(f"   📈 Среднее время: {total_time/len(self.results):.1f}с")
        
        print(f"\n🔍 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        for result in self.results:
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.tool_name:20} - {result.execution_time:.1f}с")
            
            if result.data_size > 0:
                print(f"      📊 Данных: {result.data_size} байт")
            if result.api_calls_made > 0:
                print(f"      🌐 API вызовов: {result.api_calls_made}")
            if result.files_created > 0:
                print(f"      📁 Файлов создано: {result.files_created}")
        
        # Финальная оценка
        if success_rate >= 0.8:
            print(f"\n🏆 KITTYCORE 3.0: ОТЛИЧНАЯ РЕАЛЬНОСТЬ!")
        elif success_rate >= 0.6:
            print(f"\n👍 KITTYCORE 3.0: ХОРОШАЯ РЕАЛЬНОСТЬ")
        else:
            print(f"\n⚠️ KITTYCORE 3.0: НУЖНЫ ИСПРАВЛЕНИЯ")
            
        print(f"\n💡 РЕВОЛЮЦИЯ: Никаких моков - только реальная работа! 🚀")
        
        return {
            "success_rate": success_rate,
            "successful_tests": successful,
            "total_tests": len(self.results),
            "total_time": total_time,
            "results": self.results
        }

async def main():
    """Главная функция тестирования"""
    tester = ToolRealityTester()
    
    try:
        results = await tester.run_reality_tests()
        
        # Сохраняем результаты
        results_file = Path("reality_test_results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            # Преобразуем результаты в сериализуемый формат
            serializable_results = []
            for r in results["results"]:
                serializable_results.append({
                    "tool_name": r.tool_name,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "real_output": r.real_output,
                    "error_message": r.error_message,
                    "data_size": r.data_size,
                    "api_calls_made": r.api_calls_made,
                    "files_created": r.files_created
                })
            
            json.dump({
                "success_rate": results["success_rate"],
                "successful_tests": results["successful_tests"],
                "total_tests": results["total_tests"],
                "total_time": results["total_time"],
                "results": serializable_results
            }, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Результаты сохранены в {results_file}")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Очистка
        import shutil
        try:
            shutil.rmtree(tester.temp_dir)
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main()) 