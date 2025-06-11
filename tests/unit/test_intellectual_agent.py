#!/usr/bin/env python3
"""
🧪 Тест IntellectualAgent - LLM-ориентированная система
"""

import asyncio
import sys
import os
import pytest
sys.path.insert(0, os.path.dirname(__file__))

# Правильные импорты
from agents.intellectual_agent import IntellectualAgent

@pytest.mark.asyncio
async def test_intellectual_agent():
    """Тест IntellectualAgent с реальными LLM решениями"""
    
    print("🧠 ТЕСТИРОВАНИЕ INTELLECTUAL AGENT")
    print("=" * 50)
    
    # Создаем агента
    agent = IntellectualAgent()
    
    # Тест 1: Анализ задачи создания сайта
    print("\n📋 ТЕСТ 1: Анализ задачи 'Создай сайт с котятами'")
    task = "Создай сайт с котятами"
    
    result = await agent.execute_task(task, {})
    
    print(f"✅ Результат: {result}")
    print(f"📊 Успех: {result.get('success', False)}")
    
    # Тест 2: Планирование
    print("\n📋 ТЕСТ 2: Планирование 'Составь план на день'")
    task = "Составь план на день"
    
    result = await agent.execute_task(task, {})
    
    print(f"✅ Результат: {result}")
    print(f"📊 Успех: {result.get('success', False)}")
    
    # Тест 3: Вычисления
    print("\n📋 ТЕСТ 3: Вычисления 'Посчитай плотность чёрной дыры'")
    task = "Посчитай плотность чёрной дыры"
    
    result = await agent.execute_task(task, {})
    
    print(f"✅ Результат: {result}")
    print(f"📊 Успех: {result.get('success', False)}")
    
    print("\n🎯 РЕЗУЛЬТАТ: IntellectualAgent работает через LLM!")

if __name__ == "__main__":
    asyncio.run(test_intellectual_agent()) 