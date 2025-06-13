#!/usr/bin/env python3
"""
🔥 Тест сложных задач для Enhanced OrchestratorAgent

Проверяем систему на реальных сложных задачах БЕЗ подсказок
"""

import asyncio
import time
from pathlib import Path
from integrate_to_orchestrator import EnhancedOrchestratorAgent
from kittycore.core.orchestrator import OrchestratorConfig

async def test_complex_tasks():
    """Тест сложных задач без подсказок"""
    print("🔥 === ТЕСТ СЛОЖНЫХ ЗАДАЧ БЕЗ ПОДСКАЗОК ===")
    print("Система должна сама понять что делать и создать реальный контент")
    print("=" * 80)
    
    # Создаём Enhanced Orchestrator
    config = OrchestratorConfig(orchestrator_id="complex_test_orchestrator")
    orchestrator = EnhancedOrchestratorAgent(config)
    
    # Сложные задачи БЕЗ подсказок
    complex_tasks = [
        "Калькулятор для расчёта ипотеки с досрочным погашением",
        "Система управления библиотекой книг",
        "Генератор QR-кодов с настройками",
        "Конвертер валют с актуальными курсами",
        "Планировщик задач с уведомлениями"
    ]
    
    results = []
    start_time = time.time()
    
    for i, task in enumerate(complex_tasks, 1):
        print(f"\n🎯 СЛОЖНАЯ ЗАДАЧА {i}/5:")
        print(f"📋 {task}")
        print("-" * 60)
        
        task_start = time.time()
        
        try:
            result = await orchestrator.execute_task_with_content_validation(task)
            task_time = time.time() - task_start
            
            if result["status"] == "completed" and "enhanced_result" in result:
                print(f"✅ УСПЕХ за {task_time:.1f}с")
                print(f"📁 Файл: {result['content_file']}")
                print(f"🎯 Валидация: {result['validation']['score']:.2f}")
                
                # Проверяем содержимое файла
                try:
                    with open(result['content_file'], 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    print(f"📏 Размер: {len(content)} символов")
                    print(f"💎 Превью: {content[:100]}...")
                    
                    # Проверяем что это НЕ отчёт
                    is_report = any(pattern in content for pattern in ["Задача:", "Результат работы", "агентом"])
                    print(f"✅ Реальный контент: {'Нет' if is_report else 'Да'}")
                    
                    results.append({
                        "task": task,
                        "success": True,
                        "time": task_time,
                        "file": result['content_file'],
                        "size": len(content),
                        "is_real_content": not is_report,
                        "validation_score": result['validation']['score']
                    })
                    
                except Exception as e:
                    print(f"⚠️ Ошибка чтения файла: {e}")
                    results.append({
                        "task": task,
                        "success": False,
                        "error": f"Файл не читается: {e}",
                        "time": task_time
                    })
            else:
                print(f"❌ НЕУДАЧА за {task_time:.1f}с")
                if "error" in result:
                    print(f"🚫 Ошибка: {result['error']}")
                
                results.append({
                    "task": task,
                    "success": False,
                    "error": result.get('error', 'Неизвестная ошибка'),
                    "time": task_time
                })
                
        except Exception as e:
            task_time = time.time() - task_start
            print(f"💥 КРИТИЧЕСКАЯ ОШИБКА за {task_time:.1f}с: {e}")
            results.append({
                "task": task,
                "success": False,
                "error": f"Критическая ошибка: {e}",
                "time": task_time
            })
    
    total_time = time.time() - start_time
    
    # Анализ результатов
    print("\n" + "=" * 80)
    print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ СЛОЖНЫХ ЗАДАЧ")
    print("=" * 80)
    
    successful_tasks = [r for r in results if r.get("success", False)]
    real_content_tasks = [r for r in successful_tasks if r.get("is_real_content", False)]
    
    print(f"⏱️ Общее время: {total_time:.1f}с")
    print(f"✅ Успешных задач: {len(successful_tasks)}/{len(complex_tasks)}")
    print(f"💎 Реальный контент: {len(real_content_tasks)}/{len(successful_tasks)}")
    
    if successful_tasks:
        avg_time = sum(r["time"] for r in successful_tasks) / len(successful_tasks)
        avg_size = sum(r.get("size", 0) for r in successful_tasks) / len(successful_tasks)
        avg_validation = sum(r.get("validation_score", 0) for r in successful_tasks) / len(successful_tasks)
        
        print(f"⏱️ Среднее время: {avg_time:.1f}с")
        print(f"📏 Средний размер: {avg_size:.0f} символов")
        print(f"🎯 Средняя валидация: {avg_validation:.2f}")
    
    print("\n📋 ДЕТАЛИ ПО ЗАДАЧАМ:")
    for i, result in enumerate(results, 1):
        status = "✅" if result.get("success") else "❌"
        task_name = result["task"][:40] + "..." if len(result["task"]) > 40 else result["task"]
        
        print(f"{status} {i}. {task_name}")
        if result.get("success"):
            print(f"    📁 {result.get('file', 'Нет файла')}")
            print(f"    ⏱️ {result['time']:.1f}с, 📏 {result.get('size', 0)} символов")
        else:
            print(f"    🚫 {result.get('error', 'Неизвестная ошибка')}")
    
    # Оценка готовности к продакшену
    success_rate = len(successful_tasks) / len(complex_tasks)
    real_content_rate = len(real_content_tasks) / len(successful_tasks) if successful_tasks else 0
    
    print(f"\n🎯 ОЦЕНКА ГОТОВНОСТИ К ПРОДАКШЕНУ:")
    print(f"📈 Успешность: {success_rate:.1%}")
    print(f"💎 Качество контента: {real_content_rate:.1%}")
    
    if success_rate >= 0.8 and real_content_rate >= 0.9:
        print("🚀 СИСТЕМА ГОТОВА К ПРОДАКШЕНУ!")
        print("✅ Высокая успешность выполнения сложных задач")
        print("✅ Создаёт реальный контент вместо отчётов")
        print("✅ Можно пушить в продакшен")
        return True
    elif success_rate >= 0.6:
        print("⚠️ СИСТЕМА ЧАСТИЧНО ГОТОВА")
        print("🔧 Требуется доработка для повышения надёжности")
        return False
    else:
        print("❌ СИСТЕМА НЕ ГОТОВА")
        print("🛠️ Требуется серьёзная доработка")
        return False

async def check_created_files():
    """Проверяем созданные файлы"""
    print("\n📁 === ПРОВЕРКА СОЗДАННЫХ ФАЙЛОВ ===")
    
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        print("❌ Папка outputs не найдена")
        return
    
    files = list(outputs_dir.glob("*"))
    print(f"📊 Найдено файлов: {len(files)}")
    
    for file_path in files:
        if file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"\n📄 {file_path.name}:")
                print(f"   📏 Размер: {len(content)} символов")
                print(f"   💎 Превью: {content[:80]}...")
                
                # Проверяем тип контента
                is_report = any(pattern in content for pattern in ["Задача:", "Результат работы"])
                content_type = "Отчёт" if is_report else "Реальный контент"
                print(f"   🎯 Тип: {content_type}")
                
            except Exception as e:
                print(f"\n📄 {file_path.name}: Ошибка чтения - {e}")

async def main():
    """Главная функция тестирования"""
    print("🔥 ТЕСТ СЛОЖНЫХ ЗАДАЧ ДЛЯ ENHANCED ORCHESTRATOR")
    print("Проверяем готовность системы к продакшену")
    print("=" * 80)
    
    # Тестируем сложные задачи
    is_ready = await test_complex_tasks()
    
    # Проверяем созданные файлы
    await check_created_files()
    
    print("\n" + "=" * 80)
    if is_ready:
        print("🎉 ФИНАЛЬНЫЙ ВЕРДИКТ: СИСТЕМА ГОТОВА К ПРОДАКШЕНУ!")
        print("🚀 Можно пушить и использовать в реальных проектах")
    else:
        print("⚠️ ФИНАЛЬНЫЙ ВЕРДИКТ: ТРЕБУЕТСЯ ДОРАБОТКА")
        print("🔧 Нужно улучшить систему перед продакшеном")

if __name__ == "__main__":
    asyncio.run(main()) 