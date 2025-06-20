#!/usr/bin/env python3
"""
🚀 ТЕСТ KITTYCORE 3.0 - АНАЛИЗ РЫНКА БИТРИКС24
Реальная комплексная задача для тестирования системы обучения агентов
"""

import asyncio
import sys
sys.path.append('.')

from kittycore.core.orchestrator import solve_with_orchestrator

async def main():
    task = """
    ЗАДАЧА: Анализ рынка приложений Битрикс24 и создание 3 прототипов

    ТРЕБОВАНИЯ:
    1. Проанализировать текущий рынок приложений для Битрикс24
    2. Выявить топ-15 самых популярных категорий приложений
    3. Найти проблемы UX в существующих решениях
    4. Создать 3 прототипа простых но потенциально популярных приложений:
       - С улучшенным UX по сравнению с существующими
       - Простые в использовании
       - Решающие реальные проблемы пользователей
    
    РЕЗУЛЬТАТ: 
    - Отчёт по рынку в markdown
    - 3 детальных описания прототипов
    - HTML макеты/wireframes для каждого прототипа
    """
    
    print("🚀 ЗАПУСК KITTYCORE 3.0 ДЛЯ АНАЛИЗА БИТРИКС24")
    print("=" * 60)
    
    result = await solve_with_orchestrator(task)
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТ ВЫПОЛНЕНИЯ ЗАДАЧИ")
    print("=" * 60)
    
    print(f"✅ Успех: {result.get('success', False)}")
    print(f"🤖 Агентов создано: {result.get('agents_created', 0)}")
    print(f"📁 Файлов создано: {len(result.get('generated_files', []))}")
    print(f"⏱️ Время выполнения: {result.get('execution_time', 'N/A')}")
    
    if result.get('generated_files'):
        print("\n📄 СОЗДАННЫЕ ФАЙЛЫ:")
        for file in result.get('generated_files', []):
            print(f"  • {file}")
    
    if result.get('agent_learning'):
        print(f"\n🧠 АГЕНТЫ ОБУЧИЛИСЬ: {result.get('agent_learning', 0)} записей")
    
    if result.get('errors'):
        print(f"\n❌ ОШИБКИ: {len(result.get('errors', []))}")
        for error in result.get('errors', [])[:3]:  # Первые 3 ошибки
            print(f"  • {error}")
    
    print(f"\n🎯 ИТОГОВАЯ ОЦЕНКА: {result.get('quality_score', 'N/A')}/5.0")

if __name__ == "__main__":
    asyncio.run(main()) 