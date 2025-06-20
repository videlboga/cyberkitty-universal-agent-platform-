#!/usr/bin/env python3
"""
Тест демонстрации удаления HARDCODED логики из KittyCore 3.0
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'kittycore'))

from kittycore.agents.intellectual_agent import IntellectualAgent

async def test_hardcode_removed():
    """Тест что hardcoded планы удалены"""
    
    print("🧪 ТЕСТ: Проверка удаления hardcoded логики")
    print("=" * 60)
    
    # Создаем агента
    subtask = {
        "description": "Создать Python скрипт для вычисления факториала",
        "priority": "high"
    }
    
    agent = IntellectualAgent("TestAgent", subtask)
    
    # Тестируем что _create_simple_plan теперь падает
    try:
        print("🔍 Тестируем _create_simple_plan...")
        result = agent._create_simple_plan("Создать Python скрипт для вычисления факториала", {})
        print("❌ ОШИБКА: _create_simple_plan НЕ ДОЛЖЕН работать!")
        print(f"Результат: {result}")
        return False
        
    except Exception as e:
        if "HARDCODED ПЛАНЫ УДАЛЕНЫ" in str(e):
            print("✅ ОТЛИЧНО: _create_simple_plan правильно падает!")
            print(f"Сообщение: {e}")
        else:
            print(f"❌ Неожиданная ошибка: {e}")
            return False
    
    print("\n📊 РЕЗУЛЬТАТ ТЕСТА:")
    print("✅ Hardcoded планы успешно удалены!")
    print("✅ Система теперь требует реальный LLM для планирования!")
    print("✅ Принцип 'мок ответ = лучше смерть' соблюдён!")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_hardcode_removed())
    if success:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print("\n💥 ТЕСТЫ ПРОВАЛЕНЫ!")
        sys.exit(1) 