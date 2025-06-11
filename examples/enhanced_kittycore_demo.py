#!/usr/bin/env python3
"""
🚀 KittyCore 2.1 Enhanced Demo

Демонстрация улучшений по сравнению с конкурентами:
- Structured Outputs (как MetaGPT)
- Advanced Memory (как LangGraph) 
- Enhanced Roles (как CrewAI)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from kittycore import quick_agent, create_master_agent
from kittycore.structured_outputs import SOPTemplates, apply_sop_to_agent, StructuredOutputParser
from kittycore.advanced_memory import create_enhanced_memory_agent, CrossAgentMemory
from kittycore.enhanced_roles import (
    AgentRole, 
    RoleBasedAgentFactory, 
    PersonaLibrary,
    TeamComposition
)


def demo_structured_outputs():
    """Демо структурированных выходов (как MetaGPT)"""
    print("🎯 === DEMO: Structured Outputs (inspired by MetaGPT) ===")
    
    # Создаем агента с SOP для анализа требований
    analyst = quick_agent("Ты аналитик требований")
    analyst = apply_sop_to_agent(analyst, SOPTemplates.REQUIREMENTS_SOP)
    
    task = "Создай мобильное приложение для заказа еды с доставкой"
    print(f"📝 Задача: {task}")
    print("\n💭 Агент анализирует с использованием SOP...")
    
    result = analyst.run(task)
    print(f"📋 Структурированный результат:\n{result}")
    
    # Парсим результат в структурированный формат
    parsed = StructuredOutputParser.parse_requirements(result, "analyst")
    print(f"\n📊 Parsed data: {parsed.to_dict()}")


def demo_advanced_memory():
    """Демо продвинутой памяти (как LangGraph)"""
    print("\n🧠 === DEMO: Advanced Memory (inspired by LangGraph) ===")
    
    # Создаем агента с расширенной памятью
    assistant = quick_agent("Ты помощник программиста")
    assistant = create_enhanced_memory_agent(assistant)
    
    print("💬 Серия взаимодействий с сохранением в память...")
    
    # Серия взаимодействий
    interactions = [
        "Помоги создать Python класс для пользователя",
        "Добавь метод для проверки email",
        "Теперь добавь unit тесты для этого класса",
        "Покажи статистику нашего разговора"
    ]
    
    for i, interaction in enumerate(interactions):
        print(f"\n👤 User [{i+1}]: {interaction}")
        response = assistant.run(interaction)
        print(f"🤖 Assistant: {response[:200]}...")
    
    # Демонстрируем возможности памяти
    print(f"\n📊 Memory Stats: {assistant.get_memory_stats()}")
    
    # Time travel - возвращаемся к 2-му ходу
    print("\n⏰ Time Travel - replay from turn 2:")
    replay = assistant.replay_from_turn(2)
    for snapshot in replay:
        print(f"Turn {snapshot.conversation_turn}: {snapshot.input_message[:50]}...")


def demo_enhanced_roles():
    """Демо улучшенных ролей (как CrewAI)"""
    print("\n🎭 === DEMO: Enhanced Roles (inspired by CrewAI) ===")
    
    # Создаем команду разработки с ролями
    print("👥 Создаем команду разработки...")
    
    pm = RoleBasedAgentFactory.create_agent_with_role(
        quick_agent, 
        AgentRole.PRODUCT_MANAGER
    )
    
    architect = RoleBasedAgentFactory.create_agent_with_role(
        quick_agent, 
        AgentRole.ARCHITECT
    )
    
    developer = RoleBasedAgentFactory.create_agent_with_role(
        quick_agent, 
        AgentRole.DEVELOPER
    )
    
    print(f"✅ Команда создана:")
    print(f"  - {pm.persona.role}")
    print(f"  - {architect.persona.role}")  
    print(f"  - {developer.persona.role}")
    
    # Задача для команды
    task = "Создать API для системы управления задачами"
    
    print(f"\n📝 Задача для команды: {task}")
    print("\n🏃‍♂️ Команда работает...")
    
    # PM анализирует требования
    print("\n1️⃣ Product Manager анализирует:")
    pm_result = pm.run(f"Проанализируй требования для: {task}")
    print(f"📋 PM Result: {pm_result[:300]}...")
    
    # Architect проектирует
    print("\n2️⃣ Architect проектирует:")
    arch_result = architect.run(f"Спроектируй архитектуру на основе: {pm_result[:200]}...")
    print(f"🏗️ Architect Result: {arch_result[:300]}...")
    
    # Developer реализует
    print("\n3️⃣ Developer реализует:")
    dev_result = developer.run(f"Реализуй API на основе архитектуры: {arch_result[:200]}...")
    print(f"💻 Developer Result: {dev_result[:300]}...")


def demo_master_agent_with_enhancements():
    """Демо MasterAgent с улучшениями"""
    print("\n🎯 === DEMO: Enhanced MasterAgent (our unique feature) ===")
    
    # Создаем улучшенного мастер-агента
    master = create_master_agent()
    
    # Задача требующая создания специализированных агентов
    complex_task = """
    Создай систему для интернет-магазина с корзиной, оплатой и доставкой.
    Нужны требования, архитектура, код и тесты.
    """
    
    print(f"🎯 Сложная задача: {complex_task}")
    print("\n🔮 MasterAgent создает специализированных агентов и координирует работу...")
    
    result = master.solve_task(complex_task, {
        "use_structured_outputs": True,
        "enable_memory": True,
        "assign_roles": True
    })
    
    print(f"✅ Результат: {result[:500]}...")


def show_comparison_with_competitors():
    """Показывает сравнение с конкурентами"""
    print("\n📊 === KITTYCORE VS COMPETITORS ===")
    
    comparison = """
🏆 KittyCore 2.1 ПРЕИМУЩЕСТВА:

✅ ПРОСТОТА (наша философия):
   - quick_agent("Ты помощник") # 1 строка!
   - VS CrewAI: 10+ строк с role, goal, backstory
   - VS LangGraph: 20+ строк с nodes, edges, state
   - VS AutoGen: 15+ строк с agents, chat patterns

✅ АГЕНТЫ СОЗДАЮТ АГЕНТОВ (уникально):
   - MasterAgent динамически создает специализированных агентов
   - Конкуренты: статичные команды

✅ ЛУЧШЕЕ ИЗ ВСЕХ МИРОВ:
   - Structured Outputs (от MetaGPT) ✓
   - Advanced Memory + Time Travel (от LangGraph) ✓  
   - Role-based Teams (от CrewAI) ✓
   - Enterprise Ready (от AutoGen) ✓

✅ СПЕЦИАЛИЗАЦИЯ НА БРАУЗЕРАХ:
   - Встроенные browser extension tools
   - FileSystemTool, ManifestValidator, HumanRequest
   
🎯 ИТОГ: "Агент за 5 минут, сложность по желанию!"
    """
    
    print(comparison)


def main():
    """Главная демонстрация"""
    print("🚀 KittyCore 2.1 Enhanced Demo")
    print("=" * 50)
    
    try:
        # Демо всех улучшений
        demo_structured_outputs()
        demo_advanced_memory()
        demo_enhanced_roles()
        demo_master_agent_with_enhancements()
        show_comparison_with_competitors()
        
        print("\n🎉 Демо завершено! KittyCore готов конкурировать с лидерами!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("💡 Это нормально - мы используем Mock LLM без реального API ключа")
        print("🔧 Для полной работы добавьте реальный LLM провайдер")


if __name__ == "__main__":
    main() 