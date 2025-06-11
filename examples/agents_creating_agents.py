#!/usr/bin/env python3
"""
Пример работы системы "Agents Building Agents"

Демонстрирует как MasterAgent создаёт специализированных агентов
для решения задач браузерных расширений.
"""

import logging
import sys
import os

# Добавляем путь к модулю kittycore
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kittycore.master_agent import create_master_agent
from kittycore.agent_factory import agent_factory

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_browser_extension_task():
    """
    Демонстрация создания агентов для разработки браузерного расширения
    """
    
    print("🚀 === ДЕМО: АГЕНТЫ СОЗДАЮТ АГЕНТОВ ===\n")
    
    # Создаём мастер-агента
    print("1. 🧠 Создаю мастер-агента...")
    master = create_master_agent()
    print(f"   ✅ Мастер-агент создан: {master.created_at}")
    
    # Задача для разработки браузерного расширения
    task = """
Создай браузерное расширение для Chrome, которое:

1. Отслеживает время, проведённое на различных веб-сайтах
2. Показывает статистику в popup окне
3. Позволяет блокировать отвлекающие сайты
4. Имеет простой и понятный интерфейс

Расширение должно работать на Manifest V3 и следовать лучшим практикам безопасности.
"""
    
    print(f"2. 📋 Задача:\n{task}\n")
    
    # Контекст пользователя
    user_context = {
        "experience_level": "intermediate",
        "target_browser": "chrome",
        "preferences": {
            "ui_style": "modern",
            "color_scheme": "dark"
        }
    }
    
    print("3. 🎯 Запускаю решение задачи через мастер-агента...")
    
    try:
        # Решаем задачу через мастер-агента (синхронный вызов)
        result = master.solve_task(task, user_context)
        
        print("\n4. 📊 РЕЗУЛЬТАТ РАБОТЫ:")
        print("=" * 50)
        
        if result["success"]:
            print("✅ Задача выполнена успешно!")
            print(f"\n📝 Финальный отчёт:\n{result['final_report']}")
            
            print(f"\n🤖 Создано агентов: {len(result.get('agent_results', []))}")
            
            for i, agent_result in enumerate(result.get('agent_results', []), 1):
                print(f"\n🔸 Агент {i}:")
                print(f"   Роль: {agent_result['agent'][:80]}...")
                if agent_result['success']:
                    print(f"   ✅ Результат: {agent_result['result'][:200]}...")
                else:
                    print(f"   ❌ Ошибка: {agent_result['error']}")
        
        else:
            print(f"❌ Ошибка выполнения: {result['error']}")
            
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        logger.exception("Ошибка при выполнении задачи")
    
    # Показываем информацию о созданных агентах
    print("\n5. 🏗️ ИНФОРМАЦИЯ О СОЗДАННЫХ АГЕНТАХ:")
    print("=" * 50)
    
    agents_info = master.get_managed_agents_info()
    print(f"Всего создано агентов: {agents_info['total_agents']}")
    
    for agent_id, info in agents_info['agents'].items():
        print(f"\n🤖 {agent_id}:")
        print(f"   Промпт: {info['prompt']}")
        print(f"   Инструменты: {info['tools']}")
        print(f"   Создан: {info['created_at']}")
    
    # Показываем историю задач
    history = master.get_task_history()
    print(f"\n📚 История задач: {len(history)} записей")
    
    return result


def demo_agent_factory():
    """
    Демонстрация работы AgentFactory напрямую
    """
    
    print("\n🏭 === ДЕМО: ФАБРИКА АГЕНТОВ ===\n")
    
    # Создаём агента для анализа кода
    print("1. 🔍 Создаю агента-аналитика...")
    analyst = agent_factory.create_browser_dev_agent(
        "Analyze the existing tg-stat-helper extension code and suggest improvements"
    )
    print(f"   ✅ Агент создан: {analyst.created_at}")
    
    # Создаём команду агентов
    print("\n2. 👥 Создаю команду агентов для проекта...")
    team = agent_factory.create_collaborative_team(
        "Develop a comprehensive browser extension for productivity tracking"
    )
    print(f"   ✅ Команда создана: {len(team)} агентов")
    
    for i, agent in enumerate(team, 1):
        print(f"   🤖 Агент {i}: {agent.prompt[:100]}...")
    
    # Информация о фабрике
    print("\n3. 📊 Статистика фабрики:")
    created_agents = agent_factory.list_created_agents()
    print(f"   Всего создано: {len(created_agents)} агентов")
    
    for agent_id in created_agents:
        info = agent_factory.get_agent_info(agent_id)
        print(f"   🔸 {agent_id}: {info.get('created_at', 'unknown')}")


def demo_simple_task():
    """
    Простая демонстрация на маленькой задаче
    """
    
    print("\n🎯 === ДЕМО: ПРОСТАЯ ЗАДАЧА ===\n")
    
    master = create_master_agent()
    
    simple_task = "Создай простой manifest.json для браузерного расширения с popup"
    
    print(f"Задача: {simple_task}")
    
    result = master.solve_task(simple_task)
    
    print(f"\nРезультат: {result['success']}")
    if result['success']:
        print(f"Отчёт: {result['final_report'][:300]}...")


def main():
    """Главная функция демонстрации"""
    
    print("🎪 KittyCore 2.0 - Система 'Агенты создают агентов'\n")
    
    try:
        # 1. Демо полной задачи браузерного расширения
        demo_browser_extension_task()
        
        # 2. Демо фабрики агентов
        demo_agent_factory()
        
        # 3. Демо простой задачи
        demo_simple_task()
        
        print("\n🎉 Все демонстрации завершены!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Демонстрация прервана пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        logger.exception("Ошибка в главной функции")


if __name__ == "__main__":
    # Запускаем демонстрацию
    main() 