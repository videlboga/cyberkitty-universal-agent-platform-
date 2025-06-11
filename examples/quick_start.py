#!/usr/bin/env python3
"""
KittyCore - Быстрый старт

Этот пример показывает как за 5 минут создать AI агента
"""

import sys
import os

# Добавляем путь к KittyCore
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kittycore import Agent, quick_agent
from kittycore.tools import WebSearchTool, EmailTool
from kittycore.memory import PersistentMemory


def basic_agent():
    """Самый простой агент - одна строка кода"""
    print("🚀 Простейший агент:")
    
    agent = quick_agent("You are a helpful assistant")
    response = agent.run("Привет! Как дела?")
    print(f"Ответ: {response}")
    print()


def agent_with_tools():
    """Агент с инструментами"""
    print("🔧 Агент с инструментами:")
    
    agent = Agent(
        prompt="You are a research assistant that can search the web and send emails",
        tools=[WebSearchTool(), EmailTool()]
    )
    
    response = agent.run("Найди информацию о Python и отправь краткую сводку на test@example.com")
    print(f"Ответ: {response}")
    print()


def persistent_agent():
    """Агент с постоянной памятью"""
    print("🧠 Агент с памятью:")
    
    agent = Agent(
        prompt="You are a personal assistant who remembers our conversations",
        memory=PersistentMemory("my_agent_memory.db")
    )
    
    # Первый разговор
    response1 = agent.run("Меня зовут Алексей, я программист")
    print(f"Ответ 1: {response1}")
    
    # Второй разговор - агент должен помнить имя
    response2 = agent.run("Как меня зовут?")
    print(f"Ответ 2: {response2}")
    print()


def streaming_agent():
    """Агент со стримингом ответов"""
    print("📡 Стриминг агент:")
    
    agent = Agent("You are a storyteller")
    
    print("Ответ (стрим): ", end="", flush=True)
    for chunk in agent.stream("Расскажи короткую историю про кота"):
        print(chunk, end="", flush=True)
    print("\n")


def agent_stats():
    """Статистика агента"""
    print("📊 Статистика агента:")
    
    agent = Agent("You are a helpful assistant")
    
    # Несколько запросов
    agent.run("Первый вопрос")
    agent.run("Второй вопрос")
    agent.run("Третий вопрос")
    
    # Статистика
    stats = agent.export_state()
    print(f"Состояние агента: {stats}")
    
    memory_summary = agent.get_memory_summary()
    print(f"Память: {memory_summary}")
    print()


def main():
    """Запуск всех примеров"""
    print("🐱 KittyCore - Примеры быстрого старта\n")
    print("=" * 50)
    
    try:
        basic_agent()
        agent_with_tools()
        persistent_agent()
        streaming_agent()
        agent_stats()
        
        print("✅ Все примеры выполнены успешно!")
        print("\n💡 Теперь попробуйте создать своего агента!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n🔧 Убедитесь что настроены API ключи в .env файле")


if __name__ == "__main__":
    main() 