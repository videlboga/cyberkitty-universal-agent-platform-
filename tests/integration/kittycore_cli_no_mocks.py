#!/usr/bin/env python3
"""
🐱 KittyCore 3.0 - CLI БЕЗ МОКОВ

ЧЕСТНАЯ СИСТЕМА: Запрос не прошёл = критическая ошибка!
"""

import asyncio
import sys
import os
from agents.base_agent import Agent

def check_llm_config():
    """Проверить конфигурацию LLM"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: OPENROUTER_API_KEY не найден!")
        print()
        print("🔧 ДЛЯ ЗАПУСКА НУЖНО:")
        print("   1. Получить API ключ на https://openrouter.ai")
        print("   2. export OPENROUTER_API_KEY='ваш-ключ'")
        print("   3. Или создать файл .env с ключом")
        print()
        print("💰 БЕСПЛАТНЫЕ МОДЕЛИ ДОСТУПНЫ!")
        return False
    
    print(f"✅ OPENROUTER_API_KEY найден: {api_key[:10]}...")
    return True

async def process_request(user_input: str):
    """Обработать запрос пользователя - БЕЗ МОКОВ"""
    print(f"\n🔍 Обрабатываю запрос: {user_input}")
    print("=" * 50)
    
    try:
        # Создаём ЧЕСТНОГО агента
        agent = Agent(agent_id="main_agent", name="IntellectualAgent")
        
        # Выполняем задачу
        result = await agent.execute(user_input)
        
        if result.get('success', False):
            print(f"✅ ЗАДАЧА ВЫПОЛНЕНА УСПЕШНО!")
            print(f"🧠 Использован: IntellectualAgent с РЕАЛЬНЫМ LLM")
            
            # Показываем результаты
            files_created = result.get('files_created', [])
            if files_created:
                print(f"\n📁 СОЗДАННЫЕ ФАЙЛЫ ({len(files_created)}):")
                for file in files_created:
                    print(f"   📄 {file}")
            else:
                print(f"\n📁 ФАЙЛЫ НЕ СОЗДАВАЛИСЬ")
            
            # Показываем действия
            results = result.get('results', [])
            if results:
                print(f"\n🔧 ВЫПОЛНЕННЫЕ ДЕЙСТВИЯ:")
                for i, action_result in enumerate(results, 1):
                    success_icon = "✅" if action_result.get('success') else "❌"
                    action = action_result.get('action', 'Неизвестное действие')
                    print(f"   {success_icon} {i}. {action}")
            
            # Показываем план
            plan = result.get('plan', {})
            if plan:
                print(f"\n📋 ПЛАН LLM:")
                task_type = plan.get('task_type', 'unknown')
                expected_output = plan.get('expected_output', 'неизвестно')
                complexity = plan.get('complexity', 'unknown')
                print(f"   🎯 Тип задачи: {task_type}")
                print(f"   📝 Ожидаемый результат: {expected_output}")
                print(f"   📊 Сложность: {complexity}")
        
        else:
            error = result.get('error', 'Неизвестная ошибка')
            print(f"❌ ЗАДАЧА ПРОВАЛЕНА!")
            print(f"📜 Ошибка: {error}")
            
            if "API" in error or "LLM" in error:
                print(f"\n🔧 ВОЗМОЖНЫЕ РЕШЕНИЯ:")
                print(f"   1. Проверить OPENROUTER_API_KEY")
                print(f"   2. Проверить интернет соединение")
                print(f"   3. Проверить лимиты API")
                print(f"   4. Попробовать другую модель")
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА СИСТЕМЫ!")
        print(f"📜 Детали: {e}")
        print(f"\n🚨 СИСТЕМА НЕ МОЖЕТ РАБОТАТЬ БЕЗ LLM!")
        print(f"   Никаких моков, никаких fallback - только реальные LLM!")

async def main():
    print("🐱 KittyCore 3.0 - CLI БЕЗ МОКОВ")
    print("=" * 40)
    print("ЧЕСТНАЯ СИСТЕМА: Запрос не прошёл = критическая ошибка!")
    print("🚫 НИКАКИХ МОКОВ, ТОЛЬКО РЕАЛЬНЫЕ LLM!")
    print()
    
    # Проверяем конфигурацию
    if not check_llm_config():
        return
    
    print("Введи 'exit' для выхода\n")
    
    while True:
        try:
            user_input = input("💬 Твой запрос: ").strip()
            
            if user_input.lower() in ['exit', 'выход', 'quit']:
                print("👋 До свидания!")
                break
            
            if not user_input:
                continue
                
            await process_request(user_input)
            print("\n" + "="*50)
            
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            print("🚨 СИСТЕМА ОСТАНОВЛЕНА!")
            break

if __name__ == "__main__":
    asyncio.run(main()) 