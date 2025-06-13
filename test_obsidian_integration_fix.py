#!/usr/bin/env python3
"""
🔧 ТЕСТ ИСПРАВЛЕННОЙ ИНТЕГРАЦИИ OBSIDIANORCHESTRATOR

Проверяем что после исправления ObsidianAware инструментов:
1. Агенты используют правильные инструменты
2. Результаты сохраняются в ObsidianDB
3. Файлы создаются И записываются в vault
4. НЕТ пустых результатов
"""

import asyncio
import shutil
from pathlib import Path
from kittycore.core.obsidian_orchestrator import create_obsidian_orchestrator

async def test_integration_fix():
    """Тест исправленной интеграции"""
    print("🔧 ТЕСТ ИСПРАВЛЕННОЙ ИНТЕГРАЦИИ OBSIDIANORCHESTRATOR")
    print("=" * 60)
    
    vault_path = "./integration_fix_vault"
    if Path(vault_path).exists():
        shutil.rmtree(vault_path)
    
    orchestrator = create_obsidian_orchestrator(vault_path)
    
    # Тест 1: Простая задача создания кода
    print("📝 ТЕСТ 1: Создание Python скрипта")
    print("-" * 40)
    
    task = "Создай файл calculator.py с функцией для сложения двух чисел"
    result = await orchestrator.solve_task(task, user_id="integration_test")
    
    print(f"📊 Результат:")
    print(f"   Статус: {result['status']}")
    print(f"   Агентов: {result['agents_created']}")
    print(f"   Task ID: {result['task_id']}")
    
    # Проверяем что создались РЕАЛЬНЫЕ файлы
    calculator_files = list(Path(".").glob("**/calculator.py"))
    print(f"📁 Найдено файлов calculator.py: {len(calculator_files)}")
    
    # Проверяем что в vault есть СОДЕРЖАТЕЛЬНЫЕ заметки агентов
    task_id = result['task_id']
    agent_results = list(Path(vault_path).glob("agents/*result*.md"))
    print(f"📝 Заметки результатов агентов: {len(agent_results)}")
    
    obsidian_has_real_content = False
    for result_file in agent_results:
        content = result_file.read_text()
        if 'def ' in content or 'calculator' in content or 'function' in content:
            obsidian_has_real_content = True
            print(f"   ✅ НАЙДЕН РЕАЛЬНЫЙ КОНТЕНТ в {result_file.name}")
            print(f"   📄 Фрагмент: {content[200:400]}...")
            break
        else:
            print(f"   ⚠️ Пустой/отчётный контент в {result_file.name}")
    
    # Проверяем артефакты (новые!)
    artifact_files = list(Path(vault_path).glob("agents/*/artifacts/*.md"))
    print(f"💎 Артефакты агентов: {len(artifact_files)}")
    
    obsidian_has_artifacts = False
    for artifact_file in artifact_files:
        content = artifact_file.read_text()
        if 'def ' in content or 'calculator' in content:
            obsidian_has_artifacts = True
            print(f"   ✅ НАЙДЕН АРТЕФАКТ с кодом в {artifact_file.name}")
            print(f"   📄 Фрагмент: {content[400:600]}...")
            break
    
    # Тест работоспособности созданного кода
    code_works = False
    if calculator_files:
        try:
            calc_file = calculator_files[0]
            code = calc_file.read_text()
            
            if 'def ' in code:
                exec_globals = {}
                exec(code, exec_globals)
                
                # Ищем функцию сложения
                for func_name, func_obj in exec_globals.items():
                    if callable(func_obj) and func_name != '__builtins__':
                        try:
                            # Пробуем вызвать с двумя аргументами
                            test_result = func_obj(5, 3)
                            if test_result == 8:
                                code_works = True
                                print(f"   ✅ ФУНКЦИЯ РАБОТАЕТ! {func_name}(5, 3) = {test_result}")
                                break
                        except:
                            continue
        except Exception as e:
            print(f"   ❌ Ошибка тестирования кода: {e}")
    
    # Подсчёт общего успеха
    test1_success = sum([
        len(calculator_files) > 0,        # Файлы созданы
        obsidian_has_real_content,        # Контент в результатах
        obsidian_has_artifacts,           # Артефакты есть
        code_works                        # Код работает
    ]) / 4 * 100
    
    print(f"\n🎯 ТЕСТ 1 РЕЗУЛЬТАТ: {test1_success:.1f}%")
    print(f"   📁 Файлы созданы: {len(calculator_files) > 0}")
    print(f"   📝 Контент в результатах: {obsidian_has_real_content}")
    print(f"   💎 Артефакты сохранены: {obsidian_has_artifacts}")
    print(f"   ⚡ Код работает: {code_works}")
    
    # Тест 2: Создание веб-страницы
    print(f"\n📝 ТЕСТ 2: Создание HTML страницы")
    print("-" * 40)
    
    task2 = "Создай красивую HTML страницу с формой обратной связи"
    result2 = await orchestrator.solve_task(task2, user_id="integration_test")
    
    print(f"📊 Результат:")
    print(f"   Статус: {result2['status']}")
    print(f"   Агентов: {result2['agents_created']}")
    
    # Проверяем HTML файлы
    html_files = list(Path("outputs").glob("*.html")) if Path("outputs").exists() else []
    print(f"📁 HTML файлы в outputs/: {len(html_files)}")
    
    real_form_found = False
    for html_file in html_files:
        content = html_file.read_text()
        if '<form' in content and 'input' in content:
            real_form_found = True
            print(f"   ✅ НАЙДЕНА РЕАЛЬНАЯ ФОРМА в {html_file.name}")
            break
    
    # Проверяем веб-артефакты в vault
    web_artifacts = list(Path(vault_path).glob("agents/*/artifacts/*webpage*.md"))
    print(f"💎 Веб-артефакты: {len(web_artifacts)}")
    
    web_artifacts_real = False
    for web_artifact in web_artifacts:
        content = web_artifact.read_text()
        if '<form' in content and 'input' in content:
            web_artifacts_real = True
            print(f"   ✅ НАЙДЕН ВЕБ-АРТЕФАКТ с формой в {web_artifact.name}")
            break
    
    test2_success = sum([
        len(html_files) > 0,
        real_form_found,
        web_artifacts_real
    ]) / 3 * 100
    
    print(f"\n🎯 ТЕСТ 2 РЕЗУЛЬТАТ: {test2_success:.1f}%")
    print(f"   📁 HTML файлы: {len(html_files) > 0}")
    print(f"   📝 Реальная форма: {real_form_found}")
    print(f"   💎 Веб-артефакты: {web_artifacts_real}")
    
    # ОБЩИЙ ИТОГ
    overall_success = (test1_success + test2_success) / 2
    
    print(f"\n" + "=" * 60)
    print(f"🎯 ОБЩИЙ РЕЗУЛЬТАТ ИНТЕГРАЦИИ: {overall_success:.1f}%")
    print(f"=" * 60)
    
    if overall_success >= 80:
        print("✅ ИНТЕГРАЦИЯ ИСПРАВЛЕНА!")
        print("   ObsidianAware инструменты работают корректно")
        print("   Результаты сохраняются в vault И файловую систему")
    elif overall_success >= 60:
        print("🔧 ИНТЕГРАЦИЯ ЧАСТИЧНО ИСПРАВЛЕНА")
        print("   Некоторые проблемы остались")
    else:
        print("❌ ИНТЕГРАЦИЯ ВСЁ ЕЩЁ СЛОМАНА")
        print("   Требуются дополнительные исправления")
    
    # Показываем статистику vault
    print(f"\n📊 СТАТИСТИКА VAULT:")
    all_notes = list(Path(vault_path).rglob("*.md"))
    print(f"   Всего заметок: {len(all_notes)}")
    
    by_folder = {}
    for note in all_notes:
        folder = str(note.parent.relative_to(vault_path))
        by_folder[folder] = by_folder.get(folder, 0) + 1
    
    for folder, count in sorted(by_folder.items()):
        print(f"   {folder}: {count} заметок")
    
    return overall_success

if __name__ == "__main__":
    asyncio.run(test_integration_fix()) 