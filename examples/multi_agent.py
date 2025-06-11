#!/usr/bin/env python3
"""
👥 Мульти-агентная система - KittyCore 2.0 (30 минут)

Этот пример показывает как создать команду агентов,
которые работают вместе для решения сложных задач.
"""

import asyncio
from typing import List, Dict, Any
from kittycore import Agent
from kittycore.tools import WebSearchTool, EmailTool
from kittycore.memory import SharedMemory

class AgentTeam:
    """Команда агентов для совместной работы"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.shared_memory = SharedMemory()
        self.conversation_history = []
        
    def add_agent(self, name: str, agent: Agent):
        """Добавить агента в команду"""
        self.agents[name] = agent
        agent.team_name = name
        agent.shared_memory = self.shared_memory
        
    async def discuss(self, topic: str, rounds: int = 3) -> str:
        """Провести обсуждение темы между агентами"""
        print(f"🗣️ Начинаем обсуждение: {topic}")
        print("=" * 50)
        
        current_context = f"Обсуждаем: {topic}"
        
        for round_num in range(rounds):
            print(f"\n🔄 Раунд {round_num + 1}")
            print("-" * 30)
            
            round_responses = []
            
            for agent_name, agent in self.agents.items():
                # Каждый агент высказывается по теме
                prompt = f"""
                Контекст: {current_context}
                
                Предыдущие высказывания команды:
                {chr(10).join(round_responses[-3:]) if round_responses else 'Пока никто не высказался'}
                
                Твоя задача: высказать свое мнение по теме "{topic}" 
                учитывая свою роль и предыдущие высказывания.
                Будь конструктивен и краток (2-3 предложения).
                """
                
                response = agent.run(prompt)
                round_responses.append(f"{agent_name}: {response}")
                print(f"🤖 {agent_name}: {response}")
                
                # Сохранить в общую память
                self.shared_memory.store(
                    key=f"discussion_{topic}_{round_num}_{agent_name}",
                    value=response,
                    metadata={"topic": topic, "round": round_num, "agent": agent_name}
                )
            
            # Обновить контекст для следующего раунда
            current_context += f"\n\nРаунд {round_num + 1}: " + "; ".join(round_responses[-len(self.agents):])
        
        # Синтез итогового решения
        print(f"\n🎯 Синтез решения...")
        synthesizer = self.agents.get("coordinator", list(self.agents.values())[0])
        
        final_prompt = f"""
        Тема обсуждения: {topic}
        
        Все высказывания команды:
        {chr(10).join(round_responses)}
        
        Твоя задача: создать итоговое решение/вывод на основе 
        всех высказываний. Выдели ключевые моменты и дай 
        практические рекомендации.
        """
        
        final_decision = synthesizer.run(final_prompt)
        print(f"\n✅ Итоговое решение команды:")
        print(final_decision)
        
        return final_decision

def create_customer_support_team() -> AgentTeam:
    """Создать команду для клиентской поддержки"""
    
    team = AgentTeam()
    
    # Координатор команды
    coordinator = Agent(
        prompt="""
        Ты координатор команды клиентской поддержки.
        Твоя роль: анализировать запросы, распределять задачи,
        синтезировать решения команды. Ты видишь общую картину.
        """,
        tools=[WebSearchTool()],
        name="coordinator"
    )
    
    # Технический специалист
    tech_expert = Agent(
        prompt="""
        Ты технический эксперт в команде поддержки.
        Твоя роль: решать технические проблемы, объяснять
        как работают продукты, предлагать техническое решения.
        """,
        tools=[WebSearchTool()],
        name="tech_expert"
    )
    
    # Специалист по работе с клиентами
    customer_specialist = Agent(
        prompt="""
        Ты специалист по работе с клиентами.
        Твоя роль: понимать эмоции клиентов, предлагать
        компромиссы, заботиться о клиентском опыте.
        """,
        tools=[EmailTool()],
        name="customer_specialist"
    )
    
    # Добавить всех в команду
    team.add_agent("coordinator", coordinator)
    team.add_agent("tech_expert", tech_expert)
    team.add_agent("customer_specialist", customer_specialist)
    
    return team

async def main():
    print("👥 Создание мульти-агентной системы...")
    
    # Создать команду
    support_team = create_customer_support_team()
    
    print("✅ Команда создана:")
    for name in support_team.agents.keys():
        print(f"  🤖 {name}")
    
    print("\n📝 Примеры задач для команды:")
    print("1. 'Клиент жалуется на медленную работу приложения'")
    print("2. 'Нужно выбрать новый инструмент для команды'")
    print("3. 'Клиент хочет возврат денег за продукт'")
    print("4. 'custom: <ваша задача>' - произвольная задача")
    print("5. 'выход' - завершить работу")
    
    while True:
        try:
            user_input = input("\n👤 Задача для команды: ")
            
            if user_input.lower() in ['выход', 'quit', 'exit']:
                print("👋 Команда завершает работу!")
                break
            
            if user_input.startswith('custom:'):
                topic = user_input[7:].strip()
            elif user_input == '1':
                topic = "Клиент жалуется на медленную работу приложения"
            elif user_input == '2':
                topic = "Нужно выбрать новый инструмент для команды"
            elif user_input == '3':
                topic = "Клиент хочет возврат денег за продукт"
            else:
                topic = user_input
            
            # Команда обсуждает задачу
            decision = await support_team.discuss(topic, rounds=2)
            
            # Показать статистику
            print(f"\n📊 Статистика команды:")
            total_memory = len(support_team.shared_memory.storage)
            print(f"  💾 Записей в общей памяти: {total_memory}")
            
            for name, agent in support_team.agents.items():
                stats = agent.get_conversation_stats()
                print(f"  🤖 {name}: {stats['total']} разговоров")
            
        except KeyboardInterrupt:
            print("\n👋 Команда завершает работу!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def demo_mode():
    """Демо режим для быстрого тестирования"""
    print("🎯 ДЕМО РЕЖИМ - Быстрое тестирование команды")
    
    async def demo():
        team = create_customer_support_team()
        
        # Быстрое обсуждение
        await team.discuss("Тестовая задача для демо", rounds=1)
        
        print("\n✅ Демо завершено!")
    
    asyncio.run(demo())

if __name__ == "__main__":
    print("🐱 KittyCore 2.0 - Мульти-агентная система")
    print("=" * 50)
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_mode()
    else:
        asyncio.run(main()) 