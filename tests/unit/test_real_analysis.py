#!/usr/bin/env python3
"""
🧪 Тест реального анализа задачи анализа рынка
"""

import asyncio
from agents.intellectual_agent import IntellectualAgent


async def test_real_analysis():
    """Тестируем анализ на реальной задаче анализа рынка"""
    
    print("🧪 ТЕСТ РЕАЛЬНОГО АНАЛИЗА")
    print("=" * 50)
    
    agent = IntellectualAgent()
    
    task = "Проанализируй рынок веб приложений и сделай прототипы 3 перспективных"
    
    print(f"🎯 ЗАДАЧА: {task}")
    print("-" * 50)
    
    # Выполняем полный анализ и выполнение
    result = await agent.execute_task(task, {})
    
    print(f"\n📊 РЕЗУЛЬТАТ АНАЛИЗА:")
    if "plan" in result:
        plan = result["plan"]
        print(f"   🎯 Тип задачи: {plan.get('task_type', 'unknown')}")
        print(f"   📝 Ожидаемый результат: {plan.get('expected_output', 'неизвестно')}")
        print(f"   📊 Сложность: {plan.get('complexity', 'unknown')}")
        print(f"   🏷️  Область: {plan.get('domain', 'unknown')}")
    
    print(f"\n✅ Успех: {result.get('success', False)}")
    print(f"⏱️  Время: {result.get('time', 0):.2f}с")
    
    if result.get("success"):
        print("🎉 АНАЛИЗ РАБОТАЕТ! Теперь система правильно понимает задачи!")
    else:
        print("❌ Проблема в выполнении задачи")


if __name__ == "__main__":
    asyncio.run(test_real_analysis()) 