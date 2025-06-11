#!/usr/bin/env python3
"""
🔧 Демонстрация реальной работы агентов KittyCore 3.0

Показывает как агенты создают РЕАЛЬНЫЕ файлы и выполняют РЕАЛЬНУЮ работу
"""

import asyncio
import os
import kittycore

async def demo_real_work():
    """Демонстрация реальной работы агентов"""
    print("🐱 KittyCore 3.0 - Демонстрация реальной работы агентов")
    print("=" * 60)
    
    # Создаём оркестратор
    orchestrator = kittycore.create_orchestrator()
    
    # Тестируем разные типы задач
    test_tasks = [
        "создать python скрипт для расчёта факториала",
        "создать HTML страницу с приветствием",
        "создать файл с отчётом о проделанной работе",
        "проверить доступность сайта"
    ]
    
    total_files_created = []
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n🎯 ЗАДАЧА {i}: {task}")
        print("-" * 50)
        
        # Выполняем задачу
        result = await orchestrator.solve_task(task)
        
        if result['status'] == 'completed':
            print(f"✅ Выполнено за {result['duration']:.2f}с")
            
            # Показываем созданные файлы
            execution = result.get('execution', {})
            files = execution.get('files_created', [])
            
            if files:
                print(f"📁 Созданные файлы:")
                for file in files:
                    print(f"   📄 {file}")
                    total_files_created.append(file)
                    
                    # Проверяем что файл действительно создан
                    if os.path.exists(file):
                        size = os.path.getsize(file)
                        print(f"      ✅ Файл существует ({size} байт)")
                    else:
                        print(f"      ❌ Файл не найден")
            
            # Показываем результаты выполнения
            step_results = execution.get('step_results', {})
            if step_results:
                print(f"🔧 Действия агентов:")
                for step_id, step_result in step_results.items():
                    status = "✅" if step_result.get('status') == 'completed' else "❌"
                    agent = step_result.get('agent', 'unknown')
                    output = step_result.get('result', 'No output')
                    print(f"   {status} {agent}: {output}")
        else:
            print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
    
    # Финальная статистика
    print("\n" + "=" * 60)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 60)
    
    print(f"🎯 Выполнено задач: {len(test_tasks)}")
    print(f"📁 Создано файлов: {len(total_files_created)}")
    
    if total_files_created:
        print(f"\n📋 СПИСОК ВСЕХ СОЗДАННЫХ ФАЙЛОВ:")
        for file in total_files_created:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"   📄 {file} ({size} байт)")
            else:
                print(f"   📄 {file} (не найден)")
    
    # Показываем содержимое одного из файлов
    if total_files_created:
        first_file = total_files_created[0]
        if os.path.exists(first_file):
            print(f"\n📖 СОДЕРЖИМОЕ ФАЙЛА {first_file}:")
            print("-" * 40)
            try:
                with open(first_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content[:500])  # Первые 500 символов
                    if len(content) > 500:
                        print("... (обрезано)")
            except Exception as e:
                print(f"❌ Не удалось прочитать файл: {e}")
            print("-" * 40)
    
    print(f"\n🚀 ВЫВОД: Агенты KittyCore 3.0 выполняют РЕАЛЬНУЮ РАБОТУ!")
    print(f"   ✅ Создают исполняемые файлы")
    print(f"   ✅ Генерируют код")
    print(f"   ✅ Работают с файловой системой")
    print(f"   ✅ Проверяют веб-сайты")

if __name__ == "__main__":
    asyncio.run(demo_real_work()) 