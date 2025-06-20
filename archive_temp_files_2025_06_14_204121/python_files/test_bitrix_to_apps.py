#!/usr/bin/env python3
"""
Тест: От анализа рынка Битрикс24 к РАБОЧИМ ПРИЛОЖЕНИЯМ
Цель: создать реальные приложения на основе найденных проблем UX
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'kittycore'))

from kittycore.core.obsidian_orchestrator import solve_with_obsidian_orchestrator

async def test_bitrix_to_working_apps():
    """Тест создания рабочих приложений на основе анализа Битрикс24"""
    
    print("🚀 ТЕСТ: От анализа Битрикс24 к РАБОЧИМ ПРИЛОЖЕНИЯМ")
    print("=" * 70)
    
    # Задачи для создания рабочих приложений
    tasks = [
        {
            "name": "CRM Dashboard",
            "task": "Создать простое веб-приложение CRM дашборд с HTML/CSS/JS для решения проблем AmoCRM интеграции. Должно быть готово к запуску в браузере с демо-данными клиентов.",
            "expected_files": ["crm_dashboard.html", "crm_styles.css", "crm_script.js"]
        },
        {
            "name": "1C Connector UI",
            "task": "Создать современный интерфейс для 1C коннектора с упрощённой настройкой. HTML страница с формой настройки синхронизации, современный дизайн, готовая к использованию.",
            "expected_files": ["1c_connector.html", "connector_config.js"]
        },
        {
            "name": "Telegram Bot Rich Interface",
            "task": "Создать веб-интерфейс для управления Telegram ботом с rich-контентом. Панель администратора с возможностью создания карточек, кнопок, медиа. Готовое приложение.",
            "expected_files": ["telegram_bot_admin.html", "bot_interface.js", "rich_content.css"]
        }
    ]
    
    results = []
    
    for i, task_info in enumerate(tasks, 1):
        print(f"\n🎯 ЗАДАЧА {i}/3: {task_info['name']}")
        print("-" * 50)
        print(f"📋 Описание: {task_info['task'][:100]}...")
        
        try:
            print("🚀 Запускаем создание приложения...")
            result = await solve_with_obsidian_orchestrator(task_info['task'])
            
            # Проверяем результат
            if result.get("status") != "completed":
                error_msg = result.get("error", "Неизвестная ошибка")
                print(f"❌ Ошибка: {error_msg}")
                results.append({
                    "task": task_info['name'],
                    "success": False,
                    "error": error_msg,
                    "files_created": [],
                    "validation_results": []
                })
                continue
            
            # Извлекаем результаты валидации
            validation_results = []
            execution_results = result.get("execution", {})
            step_results = execution_results.get("step_results", {})
            
            for step_id, step_result in step_results.items():
                if "validation" in step_result:
                    validation = step_result["validation"]
                    validation_results.append({
                        "step": step_id,
                        "is_valid": validation.get("is_valid", False),
                        "score": validation.get("score", 0.0),
                        "verdict": validation.get("verdict", "Нет вердикта"),
                        "expected_result": validation.get("expected_result", ""),
                        "issues": validation.get("issues", [])
                    })
                    
                    print(f"🔍 Валидация шага {step_id}:")
                    print(f"  📊 Валидность: {'✅' if validation.get('is_valid') else '❌'}")
                    print(f"  🎯 Оценка: {validation.get('score', 0):.1f}/1.0")
                    print(f"  💬 Вердикт: {validation.get('verdict', 'Нет вердикта')}")
                    if validation.get("expected_result"):
                        print(f"  🎨 Ожидался: {validation.get('expected_result')[:100]}...")
                    if validation.get("issues"):
                        print(f"  ❌ Проблемы: {', '.join(validation.get('issues', []))}")
            
            # Проверяем созданные файлы из результата
            all_created_files = result.get("obsidian_results", {}).get("created_files", [])
            
            # Также проверяем файлы в директории
            recent_files = []
            for ext in ['.html', '.js', '.css']:
                files = [f for f in os.listdir('.') if f.endswith(ext) and os.path.getmtime(f) > (asyncio.get_event_loop().time() - 300)]
                recent_files.extend(files)
            
            created_files = []
            missing_files = []
            
            # Проверяем ожидаемые файлы
            for expected_file in task_info['expected_files']:
                if os.path.exists(expected_file):
                    size = os.path.getsize(expected_file)
                    created_files.append(f"{expected_file} ({size} байт)")
                    print(f"✅ Создан: {expected_file} ({size} байт)")
                else:
                    missing_files.append(expected_file)
                    print(f"❌ Отсутствует: {expected_file}")
            
            # Добавляем недавно созданные файлы
            for file in recent_files:
                if file not in [f.split(' ')[0] for f in created_files]:
                    size = os.path.getsize(file)
                    created_files.append(f"{file} ({size} байт)")
                    print(f"📄 Найден: {file} ({size} байт)")
            
            # Определяем успех на основе валидации
            valid_results = [v for v in validation_results if v["is_valid"]]
            success = len(valid_results) > 0 or len(created_files) > 0
            
            results.append({
                "task": task_info['name'],
                "success": success,
                "files_created": created_files,
                "missing_files": missing_files,
                "validation_results": validation_results,
                "valid_steps": len(valid_results),
                "total_steps": len(validation_results),
                "result": result
            })
            
            if success:
                print(f"✅ Задача '{task_info['name']}' выполнена успешно!")
            else:
                print(f"❌ Задача '{task_info['name']}' провалена - нет файлов")
                
        except Exception as e:
            print(f"💥 Ошибка выполнения: {e}")
            results.append({
                "task": task_info['name'],
                "success": False,
                "error": str(e),
                "files_created": []
            })
    
    # Итоговая статистика
    print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 70)
    
    successful_tasks = [r for r in results if r['success']]
    total_files = sum(len(r['files_created']) for r in results)
    
    print(f"✅ Успешных задач: {len(successful_tasks)}/3")
    print(f"📁 Всего файлов создано: {total_files}")
    print(f"🎯 Процент успеха: {len(successful_tasks)/3*100:.1f}%")
    
    # Детальный отчёт
    for result in results:
        print(f"\n📋 {result['task']}:")
        if result['success']:
            print(f"  ✅ Статус: УСПЕХ")
            print(f"  📁 Файлы: {', '.join(result['files_created'])}")
        else:
            print(f"  ❌ Статус: ПРОВАЛ")
            if 'error' in result:
                print(f"  💥 Ошибка: {result['error'][:100]}...")
            if result.get('missing_files'):
                print(f"  📄 Отсутствуют: {', '.join(result['missing_files'])}")
    
    # Тестируем созданные приложения
    await test_created_applications()
    
    return len(successful_tasks) >= 2  # Успех если 2+ задач выполнены

async def test_created_applications():
    """Тестируем созданные приложения на работоспособность"""
    
    print("\n🧪 ТЕСТИРОВАНИЕ СОЗДАННЫХ ПРИЛОЖЕНИЙ:")
    print("-" * 50)
    
    # Ищем все HTML файлы
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    if not html_files:
        print("❌ HTML приложения не найдены")
        return
    
    for html_file in html_files:
        print(f"\n🔍 Тестируем: {html_file}")
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверки работоспособности
            checks = {
                "HTML структура": "<!DOCTYPE html>" in content and "<html" in content,
                "CSS стили": "<style>" in content or ".css" in content,
                "JavaScript": "<script>" in content or ".js" in content,
                "Интерактивность": "onclick" in content or "addEventListener" in content or "function" in content,
                "Форма/UI": "<form>" in content or "<button>" in content or "<input>" in content,
                "Контент": len(content) > 1000  # Минимум 1KB контента
            }
            
            passed_checks = sum(checks.values())
            total_checks = len(checks)
            
            print(f"  📊 Проверок пройдено: {passed_checks}/{total_checks}")
            
            for check_name, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"    {status} {check_name}")
            
            if passed_checks >= 4:
                print(f"  🎉 {html_file} - РАБОЧЕЕ ПРИЛОЖЕНИЕ!")
            elif passed_checks >= 2:
                print(f"  ⚠️ {html_file} - частично рабочее")
            else:
                print(f"  ❌ {html_file} - не рабочее")
                
        except Exception as e:
            print(f"  💥 Ошибка тестирования: {e}")

if __name__ == "__main__":
    print("🚀 ЗАПУСК ТЕСТА: БИТРИКС24 → РАБОЧИЕ ПРИЛОЖЕНИЯ")
    print("=" * 70)
    
    success = asyncio.run(test_bitrix_to_working_apps())
    
    if success:
        print("\n🎉 ТЕСТ ПРОЙДЕН! Рабочие приложения созданы!")
        print("🌐 Откройте HTML файлы в браузере для проверки")
    else:
        print("\n💥 ТЕСТ ПРОВАЛЕН! Нужно улучшить систему")
        
    print("\n🔗 Для запуска приложений:")
    print("   chromium *.html  # Открыть все HTML файлы")
    print("   python -m http.server 8000  # Локальный сервер") 