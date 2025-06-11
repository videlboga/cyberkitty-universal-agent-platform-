#!/usr/bin/env python3
"""
🧪 Прямой тест системы качества без CLI
"""

import asyncio
import kittycore

def quality_check(result, user_input):
    """Автоматическая проверка качества результата"""
    issues = []
    warnings = []
    
    duration = result.get('duration', 0)
    execution = result.get('execution', {})
    files_created = execution.get('files_created', [])
    step_results = execution.get('step_results', {})
    
    # Проверка подозрительно быстрого выполнения
    if duration < 0.5:
        issues.append(f"⚠️ ПОДОЗРИТЕЛЬНО БЫСТРОЕ ВЫПОЛНЕНИЕ: {duration:.2f}с")
        issues.append("   Возможные причины: моки, кэш, отсутствие LLM")
    
    # Проверка отсутствия файлов для задач создания
    creation_keywords = ['создай', 'создать', 'сделай', 'сделать', 'напиши', 'написать', 'сгенерируй', 'файл', 'сайт', 'html', 'веб']
    if any(keyword in user_input.lower() for keyword in creation_keywords):
        if not files_created:
            issues.append("🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: ЗАДАЧА СОЗДАНИЯ БЕЗ ФАЙЛОВ")
            issues.append(f"   Запрос '{user_input}' требует создания файлов, но агент их не создал!")
            issues.append("   Возможно агент использует неправильные инструменты")
    
    # Проверка неадекватных результатов
    if step_results:
        all_results = " ".join([str(step_result.get('result', '')) for step_result in step_results.values()])
        if "httpbin.org" in all_results:
            if any(word in user_input.lower() for word in ['сайт', 'веб', 'html']):
                issues.append("🚨 НЕАДЕКВАТНЫЙ РЕЗУЛЬТАТ: ЛЕВЫЕ ДЕЙСТВИЯ")
                issues.append(f"   Запросили создание сайта, а агент проверяет httpbin.org!")
                issues.append("   Агент делает НЕ ТО что просили")
    
    return issues, warnings

async def test_quality_detection():
    """Тест обнаружения проблем качества"""
    print("🧪 ТЕСТ ОБНАРУЖЕНИЯ ПРОБЛЕМ КАЧЕСТВА")
    print("=" * 45)
    
    orchestrator = kittycore.create_orchestrator()
    
    # Тест: задача создания сайта (ожидаем проблемы)
    print("\n🌐 ТЕСТ: Создание сайта")
    print("-" * 30)
    
    user_input = "Сделай сайт с котятами"
    result = await orchestrator.solve_task(user_input)
    
    print(f"⏱️ Время выполнения: {result['duration']:.2f}с")
    
    files = result.get('execution', {}).get('files_created', [])
    print(f"📁 Файлов создано: {len(files)}")
    
    step_results = result.get('execution', {}).get('step_results', {})
    print(f"🔧 Действий выполнено: {len(step_results)}")
    
    if step_results:
        for step_id, step_result in step_results.items():
            action_result = step_result.get('result', 'Нет результата')
            print(f"   • {step_id}: {action_result}")
    
    # Проверка качества
    issues, warnings = quality_check(result, user_input)
    
    print(f"\n🔍 АНАЛИЗ КАЧЕСТВА:")
    if issues:
        print("🚨 ОБНАРУЖЕНЫ КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
        for issue in issues:
            print(f"   {issue}")
    elif warnings:
        print("⚠️ ПРЕДУПРЕЖДЕНИЯ:")
        for warning in warnings:
            print(f"   {warning}")
    else:
        print("✅ ПРОБЛЕМ НЕ ОБНАРУЖЕНО")
    
    # Проверяем что система качества РАБОТАЕТ
    if issues:
        print(f"\n🎉 СИСТЕМА КАЧЕСТВА РАБОТАЕТ!")
        print(f"   ✅ Правильно обнаружила {len(issues)} проблем")
        print(f"   🔧 Система готова к автокоррекции")
        
        print(f"\n🚀 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ:")
        print(f"   1. Настроить агентов на создание HTML/CSS файлов")
        print(f"   2. Заменить левые действия (httpbin.org) на реальное создание сайта")
        print(f"   3. Увеличить время выполнения для полноценной работы")
        print(f"   4. Подключить правильные инструменты для веб-разработки")
    else:
        print(f"\n❌ СИСТЕМА КАЧЕСТВА НЕ СРАБОТАЛА!")
        print(f"   Требуется доработка алгоритмов обнаружения")

if __name__ == "__main__":
    asyncio.run(test_quality_detection()) 