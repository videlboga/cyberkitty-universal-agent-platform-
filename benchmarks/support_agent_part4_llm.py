#!/usr/bin/env python3
"""
🎧 НАСТОЯЩИЙ LLM-АГЕНТ ПОДДЕРЖКИ
Агент с реальным пониманием проблем клиентов через LLM
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import json
from typing import Dict, Any, Optional
from support_agent_part1_knowledge import *

# Простой LLM провайдер для тестирования
class SimpleLLMProvider:
    """Упрощённый LLM провайдер"""
    
    async def analyze_problem(self, problem: str, customer_context: str) -> Dict[str, Any]:
        """Анализ проблемы (имитация LLM)"""
        problem_lower = problem.lower()
        
        # Определяем категорию
        if any(word in problem_lower for word in ["нет интернета", "не работает", "отключился"]):
            category = "connectivity"
        elif any(word in problem_lower for word in ["медленно", "тормозит", "скорость"]):
            category = "performance"
        elif any(word in problem_lower for word in ["пароль", "настройка", "wifi"]):
            category = "configuration"
        elif any(word in problem_lower for word in ["роутер", "не включается", "сломался"]):
            category = "equipment"
        else:
            category = "other"
        
        # Определяем настроение
        if any(word in problem_lower for word in ["!!!", "опять", "уже", "кончится"]):
            mood = "angry"
        elif any(word in problem_lower for word in ["помогите", "не получается", "подскажите"]):
            mood = "confused"
        elif "третий раз" in problem_lower or "снова" in problem_lower:
            mood = "frustrated"
        else:
            mood = "calm"
        
        # Определяем срочность
        urgency = 3
        if "срочно" in problem_lower or mood == "angry":
            urgency = 5
        elif "не работаю" in problem_lower or "важно" in problem_lower:
            urgency = 4
        
        return {
            "problem_category": category,
            "urgency_level": urgency,
            "customer_mood": mood,
            "escalation_needed": mood == "angry" and "третий раз" in problem_lower,
            "reasoning": f"Проблема категории {category}, клиент {mood}, срочность {urgency}/5"
        }
    
    async def generate_response(self, problem: str, mood: str, solution_steps: list = None) -> str:
        """Генерация ответа клиенту"""
        
        # Персонализация по настроению
        if mood == "angry":
            greeting = "Понимаю ваше раздражение, давайте быстро решим проблему."
        elif mood == "frustrated":
            greeting = "Извините за неудобства, поможем разобраться."
        elif mood == "confused":
            greeting = "Конечно помогу! Всё объясню пошагово."
        else:
            greeting = "Добро пожаловать! Решим вашу проблему."
        
        if solution_steps:
            steps_text = " ".join([f"{i+1}) {step}." for i, step in enumerate(solution_steps[:2])])
            return f"{greeting} {steps_text} Если не поможет - сообщите!"
        else:
            return f"{greeting} Передаю ваш вопрос техническому специалисту для детального анализа."

class LLMSupportAgent:
    """LLM-агент технической поддержки"""
    
    def __init__(self, name: str = "LLM Агент КиберКот"):
        self.name = name
        self.knowledge_base = KnowledgeBase()
        self.customer_db = CustomerDatabase()
        self.llm = SimpleLLMProvider()
    
    async def handle_ticket(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Обработка тикета с LLM-анализом"""
        print(f"\n🎧 {self.name} обрабатывает тикет #{ticket.id}")
        print(f"Клиент: {ticket.customer.name} (рейтинг: {ticket.customer.satisfaction_score}/5.0)")
        print(f"Проблема: {ticket.problem_description}")
        
        start_time = time.time()
        
        # 1. LLM-анализ проблемы
        print("🧠 Анализирую проблему через LLM...")
        customer_context = f"История: {len(ticket.customer.history)} обращений, рейтинг: {ticket.customer.satisfaction_score}"
        analysis = await self.llm.analyze_problem(ticket.problem_description, customer_context)
        
        print(f"📊 Анализ: {analysis['problem_category']} | {analysis['customer_mood']} | срочность {analysis['urgency_level']}/5")
        print(f"💭 {analysis['reasoning']}")
        
        # 2. Поиск решения в базе знаний
        solutions = self.knowledge_base.search(ticket.problem_description)
        solution = solutions[0] if solutions else None
        
        # 3. Генерация персонализированного ответа
        print("✍️ Генерирую персонализированный ответ...")
        solution_steps = solution.solution_steps if solution else None
        response_text = await self.llm.generate_response(
            ticket.problem_description, 
            analysis['customer_mood'], 
            solution_steps
        )
        
        processing_time = time.time() - start_time
        
        # 4. Принятие решения
        if analysis['escalation_needed'] or not solution:
            ticket.status = TicketStatus.ESCALATED
            result = {
                "status": "escalated",
                "reason": analysis['reasoning'],
                "response": response_text,
                "processing_time": processing_time,
                "llm_analysis": analysis
            }
            print(f"⚠️ Эскалация: {analysis['reasoning']}")
        else:
            ticket.status = TicketStatus.RESOLVED
            
            # Оценка удовлетворённости на основе настроения и скорости
            base_satisfaction = 4.0
            if analysis['customer_mood'] == 'angry':
                base_satisfaction = 2.5
            elif analysis['customer_mood'] == 'frustrated':
                base_satisfaction = 3.0
            elif analysis['customer_mood'] == 'confused':
                base_satisfaction = 4.2
            
            # Бонус за быстроту
            if processing_time < 2:
                base_satisfaction += 0.5
            
            ticket.customer_satisfaction = min(base_satisfaction, 5.0)
            
            result = {
                "status": "resolved",
                "solution_used": solution.title,
                "response": response_text,
                "processing_time": processing_time,
                "customer_satisfaction": ticket.customer_satisfaction,
                "llm_analysis": analysis
            }
            print(f"✅ Решено за {processing_time:.1f} сек, оценка: {ticket.customer_satisfaction:.1f}/5.0")
        
        print(f"💬 Ответ: {response_text}")
        return result

# Тест LLM-агента
if __name__ == "__main__":
    import asyncio
    
    async def test_llm_agent():
        print("🎧 ТЕСТ LLM-АГЕНТА ПОДДЕРЖКИ")
        print("=" * 60)
        
        agent = LLMSupportAgent()
        customers = agent.customer_db
        
        # Тестовые случаи с разным настроением
        test_cases = [
            ("cust_001", "Добрый день! У меня дома пропал интернет, подскажите что делать?"),
            ("cust_003", "ОПЯТЬ НЕ РАБОТАЕТ! Уже третий раз за месяц! Когда это кончится?!"),
            ("cust_002", "Помогите настроить пароль wifi, не получается зайти в роутер"),
            ("cust_001", "Интернет работает, но очень медленно загружаются сайты")
        ]
        
        for i, (customer_id, problem) in enumerate(test_cases, 1):
            customer = customers.get_customer(customer_id)
            
            ticket = SupportTicket(
                id=f"LLM_{i:03d}",
                customer=customer,
                problem_description=problem,
                priority=TicketPriority.MEDIUM,
                status=TicketStatus.NEW,
                created_at=time.time(),
                agent_actions=[]
            )
            
            result = await agent.handle_ticket(ticket)
            print(f"📊 Результат: {result['status']}")
            print("=" * 60)
    
    # Запускаем тест
    asyncio.run(test_llm_agent()) 