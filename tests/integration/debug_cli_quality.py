#!/usr/bin/env python3
"""
🐛 Отладка проблем с системой качества в CLI
"""

import asyncio
import kittycore

def cli_quality_check(result, user_input):
    """Копия функции quality_check из CLI для отладки"""
    print(f"\n🔍 ОТЛАДКА CLI QUALITY_CHECK:")
    print(f"   Входные данные:")
    print(f"   - user_input: '{user_input}'")
    print(f"   - duration: {result.get('duration', 0)}")
    print(f"   - files_created: {result.get('execution', {}).get('files_created', [])}")
    print(f"   - step_results: {result.get('execution', {}).get('step_results', {})}")
    
    issues = []
    warnings = []
    
    duration = result.get('duration', 0)
    execution = result.get('execution', {})
    files_created = execution.get('files_created', [])
    step_results = execution.get('step_results', {})
    
    # Проверка подозрительно быстрого выполнения
    if duration < 0.5:
        issues.append(f"⚠️ ПОДОЗРИТЕЛЬНО БЫСТРОЕ ВЫПОЛНЕНИЕ: {duration:.2f}с")
        print(f"   ✓ Обнаружена проблема: быстрое выполнение {duration:.2f}с")
    
    # Проверка отсутствия файлов для задач создания
    creation_keywords = ['создай', 'создать', 'сделай', 'сделать', 'напиши', 'написать', 'сгенерируй', 'файл', 'сайт', 'html', 'веб']
    creation_detected = any(keyword in user_input.lower() for keyword in creation_keywords)
    print(f"   - Задача создания обнаружена: {creation_detected}")
    print(f"   - Файлы созданы: {len(files_created)} штук")
    
    if creation_detected:
        if not files_created:
            issues.append("🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: ЗАДАЧА СОЗДАНИЯ БЕЗ ФАЙЛОВ")
            print(f"   ✓ Обнаружена проблема: нет файлов для задачи создания")
    
    # Проверка неадекватных результатов - ИСПРАВЛЕННАЯ ВЕРСИЯ
    if step_results:
        all_results = " ".join([str(step_result.get('result', '')) for step_result in step_results.values()])
        print(f"   - Все результаты: '{all_results}'")
        print(f"   - httpbin.org найден: {'httpbin.org' in all_results}")
        
        if "httpbin.org" in all_results:
            if any(word in user_input.lower() for word in ['сайт', 'веб', 'html']):
                issues.append("🚨 НЕАДЕКВАТНЫЙ РЕЗУЛЬТАТ: ЛЕВЫЕ ДЕЙСТВИЯ")
                print(f"   ✓ Обнаружена проблема: левые действия (httpbin.org вместо создания сайта)")
    
    print(f"   Итого проблем: {len(issues)}, предупреждений: {len(warnings)}")
    return issues, warnings

async def debug_cli_quality():
    """Отладка системы качества CLI"""
    print("🐛 ОТЛАДКА СИСТЕМЫ КАЧЕСТВА CLI")
    print("=" * 40)
    
    orchestrator = kittycore.create_orchestrator()
    
    # Тест с проблемным запросом
    user_input = "Сделай сайт с котятами"
    print(f"\n🌐 Тестируем: '{user_input}'")
    
    result = await orchestrator.solve_task(user_input)
    
    print(f"\n📊 ПОЛУЧЕННЫЙ РЕЗУЛЬТАТ:")
    print(f"   - Статус: {result['status']}")
    print(f"   - Длительность: {result.get('duration', 0):.2f}с")
    print(f"   - Сложность: {result['complexity_analysis']['complexity']}")
    print(f"   - Команда: {result['team']['team_size']} агентов")
    
    execution = result.get('execution', {})
    files = execution.get('files_created', [])
    steps = execution.get('step_results', {})
    
    print(f"   - Файлов создано: {len(files)}")
    print(f"   - Шагов выполнено: {len(steps)}")
    
    if steps:
        print(f"   - Детали шагов:")
        for step_id, step_result in steps.items():
            result_text = step_result.get('result', 'Нет результата')
            print(f"     • {step_id}: {result_text}")
    
    # Запускаем CLI версию проверки качества
    issues, warnings = cli_quality_check(result, user_input)
    
    print(f"\n🎯 РЕЗУЛЬТАТ ПРОВЕРКИ:")
    if issues:
        print(f"🚨 ПРОБЛЕМЫ ОБНАРУЖЕНЫ ({len(issues)}):")
        for issue in issues:
            print(f"   {issue}")
    elif warnings:
        print(f"⚠️ ПРЕДУПРЕЖДЕНИЯ ({len(warnings)}):")
        for warning in warnings:
            print(f"   {warning}")
    else:
        print(f"✅ ПРОБЛЕМ НЕ ОБНАРУЖЕНО")
    
    # Объяснение почему CLI может не работать
    print(f"\n🔧 АНАЛИЗ ПРОБЛЕМЫ CLI:")
    if result['complexity_analysis']['complexity'] == 'simple':
        print(f"   ⚠️ Сложность 'simple' - создаётся только 1 задача")
        print(f"   ⚠️ При simple задачах декомпозиция может быть неполной")
    
    if len(result['subtasks']) == 1:
        print(f"   ⚠️ Создана только 1 подзадача вместо детальной декомпозиции")
        print(f"   ⚠️ Агент может не понимать что именно нужно создать")

if __name__ == "__main__":
    asyncio.run(debug_cli_quality()) 