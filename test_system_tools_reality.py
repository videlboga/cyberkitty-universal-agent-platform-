#!/usr/bin/env python3
"""
🚀 РЕАЛЬНОЕ ТЕСТИРОВАНИЕ СИСТЕМНЫХ ИНСТРУМЕНТОВ - ЧАСТЬ 2

РЕВОЛЮЦИОННЫЕ ПРИНЦИПЫ:
❌ НЕТ МОКОВ - только реальная работа
❌ НЕТ f"{tool}: успешно протестирован"
❌ НЕТ len(text) > 20 валидации
✅ РЕАЛЬНЫЕ файловые операции
✅ РЕАЛЬНАЯ проверка результатов
✅ РЕАЛЬНАЯ работа с системой
"""

import asyncio
import time
import tempfile
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
    files_created: int = 0
    system_operations: int = 0

class SystemToolsRealityTester:
    """Тестировщик реальности системных инструментов"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="kittycore_system_reality_"))
        self.results: List[RealTestResult] = []
        
    async def test_super_system_tool(self) -> RealTestResult:
        """РЕАЛЬНЫЙ тест системного инструмента"""
        print("🚀 Тестирую super_system_tool...")
        start_time = time.time()
        
        try:
            from kittycore.tools import DEFAULT_TOOLS
            tool = DEFAULT_TOOLS.get_tool("super_system_tool")
            
            if not tool:
                return RealTestResult("super_system_tool", False, 0, error_message="Tool not found")
            
            # РЕАЛЬНАЯ операция - создание файла
            test_file = self.temp_dir / "system_test.txt"
            test_content = "KittyCore 3.0 System Reality Test"
            
            result = tool.execute(
                action="safe_file_write",
                path=str(test_file),
                content=test_content
            )
            execution_time = time.time() - start_time
            
            # СТРОГАЯ валидация - файл реально создан?
            success = False
            files_created = 0
            real_output = "No file created"
            
            if result and hasattr(result, 'success') and result.success:
                if test_file.exists():
                    actual_content = test_file.read_text().strip()
                    if actual_content == test_content:
                        success = True
                        files_created = 1
                        real_output = f"File created: {actual_content}"
                    else:
                        real_output = f"File content mismatch: {actual_content}"
                else:
                    real_output = "File not found on filesystem"
            
            return RealTestResult(
                "super_system_tool", 
                success, 
                execution_time,
                real_output=real_output,
                files_created=files_created,
                system_operations=1
            )
            
        except Exception as e:
            return RealTestResult("super_system_tool", False, time.time() - start_time, error_message=str(e)[:100])

    async def test_code_execution(self) -> RealTestResult:
        """РЕАЛЬНЫЙ тест выполнения кода"""
        print("💻 Тестирую code_execution...")
        start_time = time.time()
        
        try:
            from kittycore.tools import DEFAULT_TOOLS
            tool = DEFAULT_TOOLS.get_tool("code_execution")
            
            if not tool:
                return RealTestResult("code_execution", False, 0, error_message="Tool not found")
            
            # РЕАЛЬНОЕ выполнение Python с математикой
            test_code = """
import math
result = math.sqrt(16) + math.pi
print(f"Результат: {result:.2f}")
print("Тест выполнен успешно!")
"""
            
            result = tool.execute(
                action="execute_python",
                code=test_code
            )
            execution_time = time.time() - start_time
            
            # СТРОГАЯ валидация результата
            success = False
            real_output = "No output"
            
            if result and hasattr(result, 'success') and result.success:
                if hasattr(result, 'data') and result.data:
                    output_str = str(result.data)
                    real_output = output_str[:100]
                    
                    # Проверяем РЕАЛЬНОЕ выполнение
                    success = (
                        "Результат: 7.14" in output_str and  # sqrt(16) + pi ≈ 7.14
                        "Тест выполнен успешно!" in output_str and
                        not ("успешно протестирован" in output_str.lower())
                    )
            
            return RealTestResult(
                "code_execution", 
                success, 
                execution_time,
                real_output=real_output,
                system_operations=1
            )
            
        except Exception as e:
            return RealTestResult("code_execution", False, time.time() - start_time, error_message=str(e)[:100])

    async def run_tests(self):
        """Запуск тестов"""
        print("🚀" + "="*60)
        print("🚀 KITTYCORE 3.0 - РЕАЛЬНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ")  
        print("🚀" + "="*60)
        print("❌ НЕТ МОКОВ | ✅ ТОЛЬКО РЕАЛЬНЫЕ ОПЕРАЦИИ")
        print()
        
        # Тест 1: SuperSystemTool
        result1 = await self.test_super_system_tool()
        self.results.append(result1)
        
        status1 = "✅" if result1.success else "❌"
        print(f"1/2 super_system_tool    {status1} {result1.execution_time:.1f}с")
        
        if result1.error_message:
            print(f"    ⚠️ {result1.error_message}")
        elif result1.success:
            print(f"    📁 {result1.files_created} файлов создано")
        else:
            print(f"    ❌ {result1.real_output}")
        
        # Тест 2: CodeExecution
        result2 = await self.test_code_execution()
        self.results.append(result2)
        
        status2 = "✅" if result2.success else "❌"
        print(f"2/2 code_execution       {status2} {result2.execution_time:.1f}с")
        
        if result2.error_message:
            print(f"    ⚠️ {result2.error_message}")
        elif result2.success:
            print(f"    💻 Код выполнен успешно")
        else:
            print(f"    ❌ {result2.real_output}")
            
        # Итоги
        successful = sum(1 for r in self.results if r.success)
        success_rate = successful / len(self.results)
        
        print(f"\n🚀" + "="*60)
        print(f"🚀 ИТОГИ СИСТЕМНЫХ ИНСТРУМЕНТОВ")
        print(f"🚀" + "="*60)
        print(f"   ✅ Успешных: {successful}/{len(self.results)} ({success_rate:.1%})")
        print(f"   📁 Файлов создано: {sum(r.files_created for r in self.results)}")
        print(f"   🔧 Операций: {sum(r.system_operations for r in self.results)}")
        
        if success_rate >= 0.8:
            print(f"\n🏆 СИСТЕМНЫЕ ИНСТРУМЕНТЫ: ОТЛИЧНАЯ РЕАЛЬНОСТЬ!")
        elif success_rate >= 0.6:
            print(f"\n👍 СИСТЕМНЫЕ ИНСТРУМЕНТЫ: ХОРОШАЯ РЕАЛЬНОСТЬ")
        else:
            print(f"\n⚠️ СИСТЕМНЫЕ ИНСТРУМЕНТЫ: НУЖНЫ ИСПРАВЛЕНИЯ")

async def main():
    tester = SystemToolsRealityTester()
    
    try:
        await tester.run_tests()
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