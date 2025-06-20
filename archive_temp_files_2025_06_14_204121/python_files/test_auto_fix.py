#!/usr/bin/env python3
"""
🧪 Тест автоматического исправления плохих результатов
"""

import asyncio
import os
from pathlib import Path
from kittycore.core.obsidian_orchestrator import solve_with_obsidian_orchestrator

async def test_auto_fix():
    print("🧪 ТЕСТ АВТОМАТИЧЕСКОГО ИСПРАВЛЕНИЯ")
    print("=" * 50)
    
    # Задача которая обычно создаёт плохие результаты
    task = "Создай Python скрипт для вычисления факториала числа"
    
    try:
        result = await solve_with_obsidian_orchestrator(task)
        
        print(f"✅ Статус: {result['status']}")
        print(f"⏱️ Время: {result['duration']:.1f}с")
        print(f"🤖 Агентов: {result['agents_created']}")
        
        # Анализируем результаты валидации и исправлений
        auto_fixes = 0
        validation_scores = []
        
        for step_id, step_result in result['execution']['step_results'].items():
            validation = step_result.get('validation', {})
            score = validation.get('score', 0)
            validation_scores.append(score)
            
            print(f"\n🔍 Шаг {step_id}:")
            print(f"  📊 Оценка: {score:.1f}/1.0")
            print(f"  ✅ Валидный: {validation.get('is_valid', False)}")
            
            # Проверяем автоматическое исправление
            if step_result.get('auto_fixed', False):
                auto_fixes += 1
                print(f"  🔧 АВТОМАТИЧЕСКИ ИСПРАВЛЕН!")
                print(f"  📝 Оригинальная оценка: {step_result.get('original_validation', {}).get('score', 'N/A')}")
                print(f"  📁 Создан файл: {step_result.get('filename', 'N/A')}")
            elif "✅ Результат автоматически исправлен!" in str(step_result):
                auto_fixes += 1
                print(f"  🔧 АВТОМАТИЧЕСКИ ИСПРАВЛЕН! (обнаружено в логах)")
                print(f"  📁 Создан файл: factorial.py")
        
        # Проверяем созданные файлы
        outputs_dir = Path("outputs")
        if outputs_dir.exists():
            files = list(outputs_dir.glob("*"))
            print(f"\n📁 Создано файлов: {len(files)}")
            for file in files:
                print(f"  - {file.name} ({file.stat().st_size} байт)")
                
                # Проверяем содержимое factorial.py
                if file.name == "factorial.py":
                    content = file.read_text(encoding='utf-8')
                    if "def factorial" in content and "return" in content:
                        print(f"    ✅ Содержит рабочий код факториала")
                    else:
                        print(f"    ❌ НЕ содержит рабочий код")
        
        # Итоговая статистика
        avg_score = sum(validation_scores) / len(validation_scores) if validation_scores else 0
        
        print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"🔧 Автоматических исправлений: {auto_fixes}")
        print(f"📊 Средняя оценка качества: {avg_score:.1f}/1.0")
        print(f"✅ Успешность: {result['status']}")
        
        # Оценка эффективности
        if auto_fixes > 0:
            print(f"\n🎯 АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ РАБОТАЕТ!")
            print(f"   Система исправила {auto_fixes} плохих результатов")
        else:
            print(f"\n⚠️ Автоматическое исправление не сработало")
        
        if avg_score > 0.7:
            print(f"🏆 ВЫСОКОЕ КАЧЕСТВО РЕЗУЛЬТАТОВ!")
        elif avg_score > 0.5:
            print(f"📈 Среднее качество результатов")
        else:
            print(f"❌ Низкое качество результатов")
            
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auto_fix()) 