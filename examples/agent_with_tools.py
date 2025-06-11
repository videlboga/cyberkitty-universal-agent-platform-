#!/usr/bin/env python3
"""
🛠️ Агент с инструментами - KittyCore 2.0 (15 минут)

Этот пример показывает как создать агента с различными
инструментами для решения практических задач.
"""

import os
from kittycore import Agent
from kittycore.tools import WebSearchTool, EmailTool
from kittycore.memory import PersistentMemory

def main():
    print("🤖 Создание агента с инструментами...")
    
    # Шаг 1: Создать агента с инструментами и памятью
    smart_assistant = Agent(
        prompt="""
        Ты умный помощник со доступом к инструментам.
        
        Возможности:
        - Поиск в интернете (web_search)
        - Отправка email (email)
        - Память прошлых разговоров
        
        Используй инструменты когда нужно найти свежую информацию
        или отправить сообщение. Всегда объясняй что делаешь.
        """,
        tools=[
            WebSearchTool(max_results=5),
            EmailTool()
        ],
        memory=PersistentMemory(file_path="assistant_memory.json")
    )
    
    print("✅ Агент создан с инструментами:")
    for tool_name in smart_assistant.tools.keys():
        print(f"  🔧 {tool_name}")
    
    print("\n🧠 Агент имеет постоянную память")
    print("📝 Доступные команды:")
    print("  'поиск: <запрос>' - поиск в интернете")
    print("  'email: <адрес>: <тема>: <текст>' - отправить email")
    print("  'память' - показать что помнит агент")
    print("  'выход' - завершить работу")
    print("-" * 40)
    
    # Шаг 2: Диалог с использованием инструментов
    while True:
        try:
            user_input = input("\n👤 Вы: ")
            
            if user_input.lower() in ['выход', 'quit', 'exit']:
                print("👋 До свидания!")
                break
            
            if user_input.lower() == 'память':
                # Показать содержимое памяти
                memory_summary = smart_assistant.memory.get_summary()
                print(f"🧠 Память: {memory_summary}")
                recent = smart_assistant.memory.recall("", limit=3)
                if recent:
                    print("📚 Последние записи:")
                    for entry in recent:
                        print(f"  💭 {entry['input'][:50]}...")
                continue
            
            # Обработать запрос через агента
            print("🤔 Думаю...")
            response = smart_assistant.run(user_input)
            print(f"\n🤖 Помощник: {response}")
            
            # Показать статистику
            stats = smart_assistant.get_conversation_stats()
            print(f"📊 Разговоров: {stats['total']}, Инструментов использовано: {stats['tools_used']}")
            
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def demo_mode():
    """Демо режим для быстрого тестирования"""
    print("🎯 ДЕМО РЕЖИМ - Быстрое тестирование инструментов")
    
    agent = Agent(
        prompt="Ты тестовый помощник. Кратко тестируй инструменты.",
        tools=[WebSearchTool(), EmailTool()]
    )
    
    # Тест поиска
    print("\n🔍 Тест поиска...")
    search_result = agent.run("Найди информацию о Python 3.12")
    print(f"Результат: {search_result[:100]}...")
    
    # Показать статистику инструментов
    for tool_name, tool in agent.tools.items():
        stats = tool.get_stats()
        print(f"🔧 {tool_name}: {stats['total_calls']} вызовов")

if __name__ == "__main__":
    print("🐱 KittyCore 2.0 - Агент с инструментами")
    print("=" * 50)
    
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "demo":
        demo_mode()
    else:
        main() 