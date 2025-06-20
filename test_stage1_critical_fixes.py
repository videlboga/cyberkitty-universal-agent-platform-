#!/usr/bin/env python3
"""
🔥 ЭТАП 1: КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ
Тестирование инструментов с критическими проблемами импортов

ПЛАН ЭТАПА 1:
- code_execution_tool: исправить импорт с code_execution_tools.py
- email_tool: исправить импорт с communication_tools.py
- Оценить прогресс: +2 инструмента готовых (1-2 дня)

ПРИНЦИПЫ:
✅ РЕАЛЬНЫЕ вызовы API
❌ НЕТ моков
✅ Честная проверка размера результата
✅ Запись правильных параметров в память
"""

import time
import json
import traceback
from pathlib import Path

# ИСПРАВЛЕННЫЕ ИМПОРТЫ
try:
    from kittycore.tools.code_execution_tools import CodeExecutionTool
    IMPORT_CODE_OK = True
except ImportError as e:
    print(f"❌ ИМПОРТ code_execution_tools: {e}")
    IMPORT_CODE_OK = False

try:
    from kittycore.tools.communication_tools import EmailTool
    IMPORT_EMAIL_OK = True
except ImportError as e:
    print(f"❌ ИМПОРТ communication_tools: {e}")
    IMPORT_EMAIL_OK = False

class HonestTestResults:
    """Честная система оценки результатов"""
    
    def __init__(self):
        self.results = []
        self.memory_records = []
    
    def test_tool_honest(self, tool_name, test_func):
        """Честное тестирование инструмента"""
        print(f"\n🔧 Тестирую {tool_name}...")
        start_time = time.time()
        
        try:
            result = test_func()
            execution_time = time.time() - start_time
            
            # Честная проверка
            is_honest = self.is_result_honest(result, tool_name)
            
            test_result = {
                "tool": tool_name,
                "success": is_honest,
                "size_bytes": len(str(result)) if result else 0,
                "execution_time": round(execution_time, 2),
                "honest": is_honest,
                "result_sample": str(result)[:100] if result else "NO_DATA"
            }
            
            self.results.append(test_result)
            
            if is_honest:
                print(f"✅ {tool_name}: {test_result['size_bytes']} байт за {execution_time:.2f}с")
                self.record_working_params(tool_name, test_func.__name__)
            else:
                print(f"❌ {tool_name}: подозрительный результат")
            
            return test_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ {tool_name}: ОШИБКА - {str(e)[:100]}")
            
            test_result = {
                "tool": tool_name,
                "success": False,
                "size_bytes": 0,
                "execution_time": round(execution_time, 2),
                "honest": False,
                "error": str(e)[:200]
            }
            
            self.results.append(test_result)
            return test_result
    
    def is_result_honest(self, result, tool_name):
        """Проверка честности результата"""
        if not result:
            return False
        
        result_str = str(result)
        
        # Подозрительные паттерны
        fake_patterns = [
            f"{tool_name}: успешно протестирован",
            "тестирование завершено успешно",
            "результат сгенерирован для демонстрации",
            "примерный результат",
            "заглушка для теста"
        ]
        
        for pattern in fake_patterns:
            if pattern.lower() in result_str.lower():
                return False
        
        # Минимальный размер для честности
        return len(result_str) > 20
    
    def record_working_params(self, tool_name, action_name):
        """Записать рабочие параметры в память"""
        memory_record = {
            "tool": tool_name,
            "working_action": action_name,
            "timestamp": time.time(),
            "status": "WORKING",
            "notes": f"Honest test passed for {tool_name}"
        }
        self.memory_records.append(memory_record)

def test_code_execution_tool():
    """Тест CodeExecutionTool с РЕАЛЬНЫМ кодом"""
    if not IMPORT_CODE_OK:
        return "IMPORT_ERROR"
    
    tool = CodeExecutionTool()
    
    # РЕАЛЬНЫЙ тест - выполнение Python кода
    result = tool.execute(
        action="execute_python",
        code="result = 2 + 2\nprint(f'Результат: {result}')\nresult",
        timeout=10
    )
    
    return result

def test_email_tool():
    """Тест EmailTool с безопасными параметрами"""
    if not IMPORT_EMAIL_OK:
        return "IMPORT_ERROR"
    
    tool = EmailTool()
    
    # РЕАЛЬНЫЙ тест - получение информации о конфигурации
    result = tool.execute(
        action="get_config",
        smtp_server="smtp.gmail.com",
        port=587
    )
    
    return result

def main():
    """Главная функция тестирования этапа 1"""
    print("🔥 ЭТАП 1: КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ")
    print("=" * 50)
    
    tester = HonestTestResults()
    
    # Тестируем инструменты с исправленными импортами
    if IMPORT_CODE_OK:
        tester.test_tool_honest("code_execution_tool", test_code_execution_tool)
    else:
        print("❌ code_execution_tool: ИМПОРТ НЕ ИСПРАВЛЕН")
    
    if IMPORT_EMAIL_OK:
        tester.test_tool_honest("email_tool", test_email_tool)
    else:
        print("❌ email_tool: ИМПОРТ НЕ ИСПРАВЛЕН")
    
    # Результаты этапа 1
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ЭТАПА 1:")
    
    total_tools = len(tester.results)
    honest_tools = sum(1 for r in tester.results if r["honest"])
    success_rate = (honest_tools / total_tools * 100) if total_tools > 0 else 0
    
    print(f"Всего протестировано: {total_tools}")
    print(f"Честных инструментов: {honest_tools}")
    print(f"Процент успеха: {success_rate:.1f}%")
    
    print("\n🎯 ДЕТАЛИ:")
    for result in tester.results:
        status = "✅ ЧЕСТНЫЙ" if result["honest"] else "❌ ПРОБЛЕМА"
        print(f"{result['tool']}: {status} ({result['size_bytes']} байт)")
    
    # Сохраняем результаты
    with open("stage1_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "stage": 1,
            "description": "Critical import fixes",
            "results": tester.results,
            "memory_records": tester.memory_records,
            "summary": {
                "total_tools": total_tools,
                "honest_tools": honest_tools,
                "success_rate": success_rate,
                "imports_fixed": IMPORT_CODE_OK + IMPORT_EMAIL_OK
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в stage1_results.json")
    
    # Прогресс к цели
    current_honest = 3  # из предыдущего анализа
    new_honest = current_honest + honest_tools
    total_target = 18
    
    print(f"\n🚀 ПРОГРЕСС К ЦЕЛИ:")
    print(f"Было честных: {current_honest}/18 (16.7%)")
    print(f"Стало честных: {new_honest}/18 ({new_honest/total_target*100:.1f}%)")
    print(f"Улучшение: +{honest_tools} инструментов")
    
    if success_rate >= 50:
        print("\n🎉 ЭТАП 1 УСПЕШЕН! Переходим к ЭТАПУ 2...")
        return True
    else:
        print("\n⚠️ ЭТАП 1 ТРЕБУЕТ ДОРАБОТКИ")
        return False

if __name__ == "__main__":
    main() 