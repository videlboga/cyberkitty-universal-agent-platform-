#!/usr/bin/env python3
"""
🚀 KittyCore 3.0 - Финальная демонстрация

Показывает полную мощь саморедуплицирующейся агентной системы
"""

import asyncio
import os
import kittycore

async def final_demonstration():
    """Финальная демонстрация всех возможностей"""
    print("🐱 KittyCore 3.0 - ФИНАЛЬНАЯ ДЕМОНСТРАЦИЯ")
    print("🚀 Саморедуплицирующаяся агентная система")
    print("=" * 60)
    
    orchestrator = kittycore.create_orchestrator()
    
    # Сложная задача для демонстрации всех возможностей
    complex_task = """
    Создать полноценную веб-презентацию компании CyberKitty:
    1. HTML страница с информацией о компании
    2. Python скрипт для обработки данных
    3. Отчёт о выполненной работе
    4. Проверка работоспособности созданных компонентов
    """
    
    print(f"🎯 СЛОЖНАЯ ЗАДАЧА:")
    print(complex_task)
    print("\n🔄 ЗАПУСКАЕМ АГЕНТНУЮ СИСТЕМУ...")
    print("=" * 60)
    
    result = await orchestrator.solve_task(complex_task)
    
    if result['status'] == 'completed':
        print(f"\n✅ ЗАДАЧА ВЫПОЛНЕНА ЗА {result['duration']:.2f}с")
        print(f"📊 Сложность: {result['complexity_analysis']['complexity']}")
        print(f"👥 Команда: {result['team']['team_size']} агентов")
        
        # Показываем декомпозицию
        print(f"\n📋 ПЛАН ВЫПОЛНЕНИЯ:")
        for i, subtask in enumerate(result['subtasks'], 1):
            print(f"   {i}. {subtask['description']}")
        
        # Показываем граф workflow
        print(f"\n📈 WORKFLOW ГРАФ:")
        print(result['workflow_graph']['mermaid'])
        
        # Показываем реальные результаты
        execution = result.get('execution', {})
        files = execution.get('files_created', [])
        
        print(f"\n📁 СОЗДАННЫЕ ФАЙЛЫ ({len(files)}):")
        total_size = 0
        for file in files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                total_size += size
                print(f"   📄 {file} ({size} байт)")
            else:
                print(f"   📄 {file} (не найден)")
        
        print(f"\n💾 Общий размер: {total_size} байт")
        
        # Показываем действия агентов
        step_results = execution.get('step_results', {})
        print(f"\n🤖 ДЕЙСТВИЯ АГЕНТОВ:")
        for step_id, step_result in step_results.items():
            status = "✅" if step_result.get('status') == 'completed' else "❌"
            agent = step_result.get('agent', 'unknown')
            output = step_result.get('result', 'No output')
            print(f"   {status} {agent}: {output}")
        
        # Коллективная память
        memory_stats = result.get('collective_memory_stats', {})
        if memory_stats:
            print(f"\n🧠 КОЛЛЕКТИВНАЯ ПАМЯТЬ:")
            print(f"   📝 Записей: {memory_stats.get('total_entries', 0)}")
            print(f"   👥 Агентов: {memory_stats.get('agents', 0)}")
        
        # Самообучение
        improvement = result.get('self_improvement_report', {})
        if improvement:
            print(f"\n🚀 САМООБУЧЕНИЕ:")
            print(f"   📊 Всего задач: {improvement.get('total_tasks', 0)}")
            print(f"   ⚡ Средняя эффективность: {improvement.get('avg_efficiency', 0):.2f}")
        
        print(f"\n" + "=" * 60)
        print(f"🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
        print(f"✨ KittyCore 3.0 - самая мощная агентная система!")
        print(f"=" * 60)
        
        print(f"\n🏆 ДОСТИЖЕНИЯ:")
        print(f"   ✅ Саморедуплицирующаяся архитектура")
        print(f"   ✅ Коллективная память команды")
        print(f"   ✅ Граф-планирование процессов")
        print(f"   ✅ Система самообучения")
        print(f"   ✅ Реальное выполнение с инструментами")
        print(f"   ✅ Визуализация Mermaid диаграмм")
        print(f"   ✅ Превосходство над конкурентами")
        
        # Если есть файлы, покажем содержимое
        if files and os.path.exists(files[0]):
            print(f"\n📖 ПРИМЕР СОЗДАННОГО КОНТЕНТА:")
            print(f"    Файл: {files[0]}")
            print("-" * 40)
            try:
                with open(files[0], 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content[:300])  # Первые 300 символов
                    if len(content) > 300:
                        print("... (обрезано)")
            except Exception as e:
                print(f"❌ Не удалось прочитать: {e}")
            print("-" * 40)
        
    else:
        print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(final_demonstration()) 