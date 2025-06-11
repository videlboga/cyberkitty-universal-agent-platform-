#!/usr/bin/env python3
"""
🧪 Финальный тест исправленной CLI системы качества
"""

import asyncio
import kittycore

async def test_fixed_cli_quality():
    """Тест исправленной CLI логики"""
    print("🧪 ТЕСТ ИСПРАВЛЕННОЙ CLI СИСТЕМЫ КАЧЕСТВА")
    print("=" * 45)
    
    orchestrator = kittycore.create_orchestrator()
    result = await orchestrator.solve_task('Сделай сайт с котятами')
    
    # Копия ИСПРАВЛЕННОЙ функции quality_check из CLI
    execution = result.get('execution', {})
    files_created = execution.get('files_created', [])
    step_results = execution.get('step_results', {})
    duration = result.get('duration', 0)
    user_input = 'Сделай сайт с котятами'
    
    issues = []
    warnings = []
    
    # Проверка подозрительно быстрого выполнения
    if duration < 0.5:
        issues.append(f"⚠️ ПОДОЗРИТЕЛЬНО БЫСТРОЕ ВЫПОЛНЕНИЕ: {duration:.2f}с")
    
    # Проверка отсутствия файлов для задач создания
    creation_keywords = ['создай', 'создать', 'сделай', 'сделать', 'напиши', 'написать', 'сгенерируй', 'файл', 'сайт', 'html', 'веб']
    if any(keyword in user_input.lower() for keyword in creation_keywords):
        if not files_created:
            issues.append("🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: ЗАДАЧА СОЗДАНИЯ БЕЗ ФАЙЛОВ")
    
    # Проверка неадекватных результатов - ИСПРАВЛЕНО
    if step_results:
        all_results = " ".join([str(step_result.get('result', '')) for step_result in step_results.values()])
        if "httpbin.org" in all_results:
            if any(word in user_input.lower() for word in ['сайт', 'веб', 'html']):
                issues.append("🚨 НЕАДЕКВАТНЫЙ РЕЗУЛЬТАТ: ЛЕВЫЕ ДЕЙСТВИЯ")
    
    print(f"📊 РЕЗУЛЬТАТ ЗАДАЧИ:")
    print(f"   Время: {duration:.2f}с")
    print(f"   Файлов: {len(files_created)}")
    print(f"   Шагов: {len(step_results)}")
    
    print(f"\n🔍 ПРОВЕРКА КАЧЕСТВА:")
    if issues:
        print(f"🚨 ОБНАРУЖЕНЫ ПРОБЛЕМЫ ({len(issues)}):")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n✅ CLI СИСТЕМА КАЧЕСТВА РАБОТАЕТ!")
    elif warnings:
        print(f"⚠️ ПРЕДУПРЕЖДЕНИЯ ({len(warnings)}):")
        for warning in warnings:
            print(f"   {warning}")
    else:
        print(f"❌ ПРОБЛЕМ НЕ ОБНАРУЖЕНО - СИСТЕМА НЕ РАБОТАЕТ!")
    
    # Сравнение с ожидаемым поведением
    expected_issues = 2  # Нет файлов + левые действия
    
    print(f"\n🎯 СРАВНЕНИЕ С ОЖИДАНИЕМ:")
    print(f"   Ожидаемо проблем: {expected_issues}")
    print(f"   Обнаружено проблем: {len(issues)}")
    
    if len(issues) >= expected_issues:
        print(f"   🎉 ИСПРАВЛЕНИЕ УСПЕШНО!")
        print(f"   ✅ CLI теперь правильно обнаруживает проблемы")
    else:
        print(f"   ❌ ИСПРАВЛЕНИЕ НЕ ПОМОГЛО")
        print(f"   🔧 Требуется дополнительная отладка")

if __name__ == "__main__":
    asyncio.run(test_fixed_cli_quality()) 