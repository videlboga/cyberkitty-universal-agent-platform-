#!/usr/bin/env python3
"""
🚀 ИСПРАВЛЕННЫЙ ТЕСТ БИТРИКС24
Без fallback планов, только реальный LLM
"""

import asyncio
import sys
import os
sys.path.append('.')

from kittycore.core.orchestrator import solve_with_orchestrator

async def test_fixed_bitrix():
    """Тест исправленной системы"""
    
    print("🚀 ИСПРАВЛЕННЫЙ ТЕСТ БИТРИКС24")
    print("=" * 60)
    print("✅ Убран fallback к hardcoded планам")
    print("✅ Улучшен LLM промпт для планирования")
    print("✅ Добавлен web_search в REAL_TOOLS")
    print("=" * 60)
    
    # Простая задача для проверки
    task = """
    Создать анализ рынка приложений Битрикс24 и 3 прототипа с улучшенным UX.
    
    ТРЕБОВАНИЯ:
    1. Найти реальную информацию о Битрикс24 маркетплейсе
    2. Создать 3 HTML прототипа с улучшенным UX
    3. Файлы должны содержать реальный контент, а не планы
    """
    
    print(f"📋 ЗАДАЧА: {task}")
    print(f"\n🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:")
    print(f"  1. web_search для поиска информации о Битрикс24")
    print(f"  2. Создание реальных HTML файлов с прототипами")
    print(f"  3. Никаких шаблонных планов!")
    
    try:
        print(f"\n🚀 ЗАПУСК ИСПРАВЛЕННОЙ СИСТЕМЫ...")
        result = await solve_with_orchestrator(task)
        
        print(f"\n📊 РЕЗУЛЬТАТ:")
        print(f"✅ Успех: {result.get('success', False)}")
        print(f"📝 Сообщение: {result.get('message', 'Нет сообщения')}")
        
        # Проверяем созданные файлы
        print(f"\n📁 ПРОВЕРКА ФАЙЛОВ:")
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(('.html', '.md', '.txt')) and 'битрикс' in file.lower():
                    filepath = os.path.join(root, file)
                    size = os.path.getsize(filepath)
                    print(f"  📄 {filepath} ({size} байт)")
                    
                    # Читаем первые 200 символов для проверки содержимого
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read(200)
                            print(f"    🔍 Содержимое: {content[:100]}...")
                    except:
                        print(f"    ❌ Ошибка чтения файла")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False

async def main():
    print("🔧 ТЕСТ ИСПРАВЛЕННОЙ СИСТЕМЫ KITTYCORE 3.0")
    print("Проверяем работу без hardcoded fallback планов")
    print("=" * 70)
    
    success = await test_fixed_bitrix()
    
    print(f"\n📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    if success:
        print(f"🎉 СИСТЕМА РАБОТАЕТ! Создаёт реальный контент через LLM")
    else:
        print(f"❌ СИСТЕМА НЕ РАБОТАЕТ. Нужны дополнительные исправления")

if __name__ == "__main__":
    asyncio.run(main()) 