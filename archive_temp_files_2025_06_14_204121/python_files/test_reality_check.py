#!/usr/bin/env python3
"""
🔍 ПРОВЕРКА РЕАЛЬНОСТИ - Что на самом деле делает ObsidianOrchestrator?

НЕ ВЕРИМ СТАТИСТИКЕ - ПРОВЕРЯЕМ ФАКТЫ:
❓ Создаются ли реальные файлы?
❓ Содержат ли они то что просили?
❓ Работает ли код который создали агенты?
❓ Или это опять отчёты о работе?
"""

import asyncio
import shutil
from pathlib import Path
from kittycore.core.obsidian_orchestrator import create_obsidian_orchestrator

async def reality_check_factorial():
    """Проверка реальности: создание факториала"""
    print("🔍 ПРОВЕРКА РЕАЛЬНОСТИ: Факториал")
    print("=" * 50)
    
    vault_path = "./reality_test_vault"
    if Path(vault_path).exists():
        shutil.rmtree(vault_path)
    
    orchestrator = create_obsidian_orchestrator(vault_path)
    
    # Задача: создать факториал
    task = "Создай файл factorial.py с функцией для вычисления факториала числа"
    print(f"📋 Задача: {task}")
    
    result = await orchestrator.solve_task(task, user_id="reality_test")
    
    print(f"\n📊 Статистика говорит:")
    print(f"   Статус: {result['status']}")
    print(f"   Агентов: {result['agents_created']}")
    print(f"   Шагов: {result['steps_completed']}")
    
    print(f"\n🔍 А ЧТО НА САМОМ ДЕЛЕ?")
    
    # Проверка 1: Создался ли файл factorial.py?
    factorial_files = list(Path(".").glob("**/factorial.py"))
    print(f"📁 Файлы factorial.py найдены: {len(factorial_files)}")
    for file in factorial_files:
        print(f"   - {file}")
    
    # Проверка 2: Что в папке outputs?
    outputs_path = Path("outputs")
    if outputs_path.exists():
        output_files = list(outputs_path.glob("*.py"))
        print(f"📁 Python файлы в outputs/: {len(output_files)}")
        for file in output_files:
            print(f"   - {file}")
            if file.name == "factorial.py":
                content = file.read_text()
                print(f"   📄 Содержимое factorial.py:")
                print(f"   {content[:200]}...")
    else:
        print("📁 Папка outputs/ не существует")
    
    # Проверка 3: Что в vault?
    vault_files = list(Path(vault_path).rglob("*.py"))
    print(f"📁 Python файлы в vault: {len(vault_files)}")
    for file in vault_files:
        print(f"   - {file}")
    
    # Проверка 4: Что в результатах агентов?
    task_id = result['task_id']
    agent_results = result.get('obsidian_results', {}).get('agent_results', [])
    print(f"🤖 Результаты агентов ({len(agent_results)}):")
    
    real_code_found = False
    for i, agent_result in enumerate(agent_results):
        content = agent_result.get('content', '')
        print(f"   Агент {i+1}: {len(content)} символов")
        
        # Проверяем есть ли в результате РЕАЛЬНЫЙ код
        if 'def factorial' in content or 'factorial(' in content:
            real_code_found = True
            print(f"   ✅ НАЙДЕН РЕАЛЬНЫЙ КОД факториала!")
            print(f"   📄 Фрагмент: {content[:150]}...")
        else:
            print(f"   ⚠️ Возможно отчёт: {content[:100]}...")
    
    # Проверка 5: Можно ли запустить созданный код?
    working_code = False
    for factorial_file in factorial_files:
        try:
            # Читаем файл
            code = factorial_file.read_text()
            
            # Проверяем есть ли функция factorial
            if 'def factorial' in code:
                # Пытаемся выполнить код
                exec_globals = {}
                exec(code, exec_globals)
                
                if 'factorial' in exec_globals:
                    # Тестируем функцию
                    factorial_func = exec_globals['factorial']
                    test_result = factorial_func(5)
                    expected = 120  # 5! = 120
                    
                    if test_result == expected:
                        working_code = True
                        print(f"   ✅ КОД РАБОТАЕТ! factorial(5) = {test_result}")
                    else:
                        print(f"   ❌ Код не работает: factorial(5) = {test_result}, ожидалось 120")
                else:
                    print(f"   ❌ Функция factorial не найдена в коде")
            else:
                print(f"   ❌ Определение функции не найдено")
                
        except Exception as e:
            print(f"   ❌ Ошибка выполнения кода: {e}")
    
    # ИТОГ
    print(f"\n🎯 ИТОГ ПРОВЕРКИ РЕАЛЬНОСТИ:")
    print(f"   📁 Файлы созданы: {len(factorial_files) > 0}")
    print(f"   🤖 Реальный код в результатах: {real_code_found}")
    print(f"   ⚡ Код работает: {working_code}")
    
    reality_score = sum([
        len(factorial_files) > 0,
        real_code_found,
        working_code
    ]) / 3 * 100
    
    print(f"   🎯 ПОКАЗАТЕЛЬ РЕАЛЬНОСТИ: {reality_score:.1f}%")
    
    if reality_score < 50:
        print(f"   🔥 ДИАГНОЗ: ИЛЛЮЗИЯ РАБОТЫ!")
    elif reality_score < 80:
        print(f"   ⚠️ ДИАГНОЗ: ЧАСТИЧНАЯ РАБОТА")
    else:
        print(f"   ✅ ДИАГНОЗ: РЕАЛЬНАЯ РАБОТА")
    
    return reality_score

async def reality_check_website():
    """Проверка реальности: создание веб-сайта"""
    print("\n🔍 ПРОВЕРКА РЕАЛЬНОСТИ: Веб-сайт")
    print("=" * 50)
    
    vault_path = "./reality_test_vault"
    orchestrator = create_obsidian_orchestrator(vault_path)
    
    # Задача: создать простой сайт
    task = "Создай простой HTML сайт с формой регистрации"
    print(f"📋 Задача: {task}")
    
    result = await orchestrator.solve_task(task, user_id="reality_web_test")
    
    print(f"\n📊 Статистика говорит:")
    print(f"   Статус: {result['status']}")
    print(f"   Агентов: {result['agents_created']}")
    print(f"   Шагов: {result['steps_completed']}")
    
    print(f"\n🔍 А ЧТО НА САМОМ ДЕЛЕ?")
    
    # Ищем HTML файлы
    html_files = list(Path(".").glob("**/*.html"))
    print(f"📁 HTML файлы найдены: {len(html_files)}")
    
    working_html = False
    real_form_found = False
    
    for html_file in html_files:
        print(f"   - {html_file}")
        content = html_file.read_text()
        
        # Проверяем есть ли реальная форма
        if '<form' in content and 'input' in content:
            real_form_found = True
            print(f"   ✅ НАЙДЕНА РЕАЛЬНАЯ ФОРМА!")
            
            # Проверяем структуру HTML
            if '<!DOCTYPE html>' in content and '<html>' in content:
                working_html = True
                print(f"   ✅ КОРРЕКТНЫЙ HTML!")
            else:
                print(f"   ⚠️ HTML может быть неполным")
        else:
            print(f"   ❌ Форма не найдена или неполная")
            print(f"   📄 Содержимое: {content[:200]}...")
    
    # ИТОГ
    print(f"\n🎯 ИТОГ ПРОВЕРКИ ВЕБА:")
    print(f"   📁 HTML файлы: {len(html_files) > 0}")
    print(f"   📝 Реальная форма: {real_form_found}")
    print(f"   ✅ Корректный HTML: {working_html}")
    
    web_reality_score = sum([
        len(html_files) > 0,
        real_form_found,
        working_html
    ]) / 3 * 100
    
    print(f"   🎯 ПОКАЗАТЕЛЬ РЕАЛЬНОСТИ ВЕБА: {web_reality_score:.1f}%")
    
    return web_reality_score

async def deep_vault_inspection(vault_path: str):
    """Глубокая инспекция содержимого vault"""
    print(f"\n🔬 ГЛУБОКАЯ ИНСПЕКЦИЯ VAULT: {vault_path}")
    print("=" * 50)
    
    if not Path(vault_path).exists():
        print("❌ Vault не существует!")
        return
    
    # Анализ заметок агентов
    agent_notes = list(Path(vault_path).glob("agents/*result*.md"))
    print(f"📝 Заметки результатов агентов: {len(agent_notes)}")
    
    empty_results = 0
    report_results = 0
    code_results = 0
    
    for note in agent_notes[:3]:  # Первые 3 заметки
        content = note.read_text()
        lines = content.split('\n')
        content_lines = [line for line in lines if not line.startswith('---') and not line.startswith('#') and line.strip()]
        
        print(f"\n📄 {note.name}:")
        print(f"   Всего строк: {len(lines)}")
        print(f"   Строк контента: {len(content_lines)}")
        
        if len(content_lines) == 0:
            empty_results += 1
            print(f"   ❌ ПУСТОЙ РЕЗУЛЬТАТ")
        elif any(word in content.lower() for word in ['отчёт', 'анализ', 'выполнено', 'завершено']):
            report_results += 1
            print(f"   ⚠️ ПОХОЖЕ НА ОТЧЁТ")
        elif any(word in content for word in ['def ', 'function', '<html>', 'import', 'class ']):
            code_results += 1
            print(f"   ✅ СОДЕРЖИТ КОД")
        else:
            print(f"   ❓ НЕОПРЕДЕЛЁННЫЙ КОНТЕНТ")
        
        # Показываем первые строки контента
        if content_lines:
            print(f"   📄 Первые строки:")
            for line in content_lines[:3]:
                print(f"      {line[:80]}...")
    
    print(f"\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ АГЕНТОВ:")
    print(f"   Пустые: {empty_results}")
    print(f"   Отчёты: {report_results}")
    print(f"   Код: {code_results}")

async def main():
    """Главная функция проверки реальности"""
    print("🔥 ПРОВЕРКА РЕАЛЬНОСТИ OBSIDIANORCHESTRATOR")
    print("=" * 60)
    print("🎯 НЕ ВЕРИМ СТАТИСТИКЕ - ПРОВЕРЯЕМ ФАКТЫ!")
    print("=" * 60)
    
    # Тест 1: Факториал
    factorial_score = await reality_check_factorial()
    
    # Тест 2: Веб-сайт
    web_score = await reality_check_website()
    
    # Глубокая инспекция
    await deep_vault_inspection("./reality_test_vault")
    
    # ОБЩИЙ ИТОГ
    overall_score = (factorial_score + web_score) / 2
    
    print(f"\n" + "=" * 60)
    print(f"🎯 ОБЩИЙ ПОКАЗАТЕЛЬ РЕАЛЬНОСТИ: {overall_score:.1f}%")
    print(f"=" * 60)
    
    if overall_score < 30:
        print("🔥 ДИАГНОЗ: ПОЛНАЯ ИЛЛЮЗИЯ РАБОТЫ!")
        print("   Система создаёт отчёты о работе, но НЕ РАБОТАЕТ")
    elif overall_score < 60:
        print("⚠️ ДИАГНОЗ: ЧАСТИЧНАЯ ИЛЛЮЗИЯ")
        print("   Система что-то делает, но не то что просили")
    elif overall_score < 80:
        print("🔧 ДИАГНОЗ: РАБОТАЕТ НО ПЛОХО")
        print("   Система создаёт результаты, но они неполные")
    else:
        print("✅ ДИАГНОЗ: РЕАЛЬНО РАБОТАЕТ!")
        print("   Система создаёт то что просили и оно работает")

if __name__ == "__main__":
    asyncio.run(main()) 