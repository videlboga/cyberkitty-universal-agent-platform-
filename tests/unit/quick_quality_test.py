#!/usr/bin/env python3
"""
🧪 Быстрый тест системы контроля качества
"""

import asyncio
import kittycore

async def test_quality_system():
    """Тест системы проверки качества"""
    print("🧪 ТЕСТ СИСТЕМЫ КОНТРОЛЯ КАЧЕСТВА")
    print("=" * 40)
    
    orchestrator = kittycore.create_orchestrator()
    
    # Тест 1: Задача создания файла (должна создать файлы)
    print("\n📝 ТЕСТ 1: Задача создания")
    print("-" * 30)
    result1 = await orchestrator.solve_task("создай файл с планом на завтра")
    
    duration1 = result1['duration']
    files1 = result1.get('execution', {}).get('files_created', [])
    
    print(f"⏱️ Время: {duration1:.2f}с")
    print(f"📁 Файлов: {len(files1)}")
    
    # Проверка качества
    if duration1 < 0.5:
        print("🚨 ПРОБЛЕМА: Подозрительно быстро!")
    if not files1 and "создай" in "создай файл":
        print("🚨 ПРОБЛЕМА: Нет файлов для задачи создания!")
    if duration1 > 1.0 and files1:
        print("✅ КАЧЕСТВО: Время реалистично, файлы созданы")
    
    # Тест 2: Аналитическая задача (не должна создавать файлы)
    print("\n🧮 ТЕСТ 2: Аналитическая задача")
    print("-" * 30)
    result2 = await orchestrator.solve_task("посчитай плотность чёрной дыры")
    
    duration2 = result2['duration']
    files2 = result2.get('execution', {}).get('files_created', [])
    
    print(f"⏱️ Время: {duration2:.2f}с")
    print(f"📁 Файлов: {len(files2)}")
    
    # Проверка качества
    if duration2 < 0.5:
        print("🚨 ПРОБЛЕМА: Подозрительно быстро для LLM анализа!")
    if duration2 > 1.0:
        print("✅ КАЧЕСТВО: Время указывает на реальный LLM анализ")
    
    # Сводка
    print("\n📊 СВОДКА КАЧЕСТВА:")
    print("-" * 30)
    print(f"Тест 1 (создание): {duration1:.2f}с, файлов: {len(files1)}")
    print(f"Тест 2 (анализ): {duration2:.2f}с, файлов: {len(files2)}")
    
    if duration1 > 1.0 and files1 and duration2 > 1.0:
        print("🎉 ВСЕ ТЕСТЫ КАЧЕСТВА ПРОШЛИ!")
        print("💪 Система использует РЕАЛЬНЫЕ компоненты!")
    else:
        print("⚠️ ОБНАРУЖЕНЫ ПРОБЛЕМЫ КАЧЕСТВА!")
        print("🔧 Требуется активация реальных компонентов!")

if __name__ == "__main__":
    asyncio.run(test_quality_system()) 