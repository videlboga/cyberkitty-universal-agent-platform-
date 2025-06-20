#!/usr/bin/env python3
"""
🔄 Тест итеративного улучшения агентов

Проверяет что система может улучшать агентов через фидбек
вместо простого исправления результатов
"""

import asyncio
import os
from pathlib import Path

from kittycore.core.obsidian_orchestrator import ObsidianOrchestrator


async def test_iterative_improvement():
    """Тестирует итеративное улучшение агентов"""
    
    print("🔄 ТЕСТ ИТЕРАТИВНОГО УЛУЧШЕНИЯ АГЕНТОВ")
    print("=" * 50)
    
    # Создаём оркестратор
    vault_path = "./test_vault_iterative"
    orchestrator = ObsidianOrchestrator(vault_path)
    
    # Задача которая обычно создаёт отчёт вместо результата
    task = "Создай файл с расчётом площади кота по формуле A = π * r²"
    
    print(f"📋 Задача: {task}")
    print()
    
    try:
        # Решаем задачу
        result = await orchestrator.solve_task(task)
        
        print("📊 РЕЗУЛЬТАТЫ:")
        print(f"✅ Статус: {result.get('status', 'unknown')}")
        print(f"📁 Файлов создано: {len(result.get('files_created', []))}")
        
        # Проверяем файлы
        files_created = result.get('files_created', [])
        for file_path in files_created:
            if os.path.exists(file_path):
                print(f"📄 Файл: {file_path}")
                
                # Читаем содержимое
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"📝 Размер: {len(content)} символов")
                
                # Проверяем что это НЕ отчёт
                report_indicators = [
                    "отчёт", "анализ", "рекомендации", "выводы",
                    "заключение", "исследование", "обзор"
                ]
                
                is_report = any(indicator in content.lower() for indicator in report_indicators)
                
                # Проверяем что это реальный контент
                content_indicators = [
                    "π", "3.14", "math", "площадь", "формула", "=", "*"
                ]
                
                has_real_content = any(indicator in content.lower() for indicator in content_indicators)
                
                if is_report:
                    print("❌ ПРОБЛЕМА: Файл содержит отчёт вместо контента!")
                elif has_real_content:
                    print("✅ УСПЕХ: Файл содержит реальный контент!")
                else:
                    print("⚠️ НЕОПРЕДЕЛЁННО: Сложно определить тип контента")
                
                # Показываем первые 200 символов
                print(f"📖 Превью: {content[:200]}...")
                print()
        
        # Проверяем информацию об улучшениях
        execution_result = result.get('execution_result', {})
        step_results = execution_result.get('step_results', {})
        
        improvements_found = False
        for step_id, step_result in step_results.items():
            if step_result.get('iteratively_improved', False):
                improvements_found = True
                attempts = step_result.get('improvement_attempts', 0)
                original_score = step_result.get('original_validation', {}).get('score', 0)
                final_validation = step_result.get('validation', {})
                final_score = final_validation.get('score', 0)
                
                print(f"🔄 ИТЕРАТИВНОЕ УЛУЧШЕНИЕ (шаг {step_id}):")
                print(f"   📈 Попыток улучшения: {attempts}")
                print(f"   📊 Оценка: {original_score:.1f} → {final_score:.1f}")
                print(f"   ✅ Улучшение: {final_score - original_score:+.1f}")
                print()
        
        if not improvements_found:
            print("ℹ️ Итеративные улучшения не потребовались (результат сразу хороший)")
        
        print("🎯 ИТОГИ ТЕСТА:")
        if result.get('status') == 'completed' and files_created:
            print("✅ Тест ПРОЙДЕН: Система создала файлы и завершила задачу")
        else:
            print("❌ Тест ПРОВАЛЕН: Система не создала ожидаемые результаты")
        
    except Exception as e:
        print(f"❌ ОШИБКА ТЕСТА: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Очистка
        import shutil
        if os.path.exists(vault_path):
            shutil.rmtree(vault_path)
            print(f"🧹 Очищен тестовый vault: {vault_path}")


if __name__ == "__main__":
    asyncio.run(test_iterative_improvement()) 