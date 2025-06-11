#!/usr/bin/env python3
"""
🚀 Простой бот за 5 минут - KittyCore 2.0

Этот пример показывает как создать простого AI агента
буквально за 5 минут без сложных настроек.
"""

# Настройка OpenRouter API (замените на свой ключ)
import os
os.environ['OPENROUTER_API_KEY'] = 'your-api-key-here'

# Импорт KittyCore - все что нужно в одной строке
from kittycore import quick_agent

def main():
    print("🤖 Создание простого бота...")
    
    # Шаг 1: Создать агента за одну строку
    bot = quick_agent("""
        Ты дружелюбный помощник по имени КиттиБот.
        Отвечай кратко и полезно на русском языке.
        Если не знаешь ответа, честно скажи об этом.
    """)
    
    print("✅ Бот создан! Начинаем диалог...\n")
    
    # Шаг 2: Простой диалог в консоли
    while True:
        try:
            user_input = input("👤 Вы: ")
            if user_input.lower() in ['выход', 'quit', 'exit']:
                print("👋 До свидания!")
                break
                
            # Шаг 3: Получить ответ от бота
            response = bot.run(user_input)
            print(f"🤖 КиттиБот: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🐱 KittyCore 2.0 - Простой бот")
    print("=" * 40)
    print("💡 Совет: Установите свой OPENROUTER_API_KEY")
    print("   export OPENROUTER_API_KEY='your-key'")
    print("=" * 40)
    
    main() 