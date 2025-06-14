#!/usr/bin/env python3
"""
🎧 БЕНЧМАРК АГЕНТА ПОДДЕРЖКИ - ЧАСТЬ 2: АГЕНТ
Базовый агент технической поддержки
"""

import time
import random
from typing import List, Dict, Any, Optional
from support_agent_part1_knowledge import *

class SupportAgent:
    """Агент технической поддержки"""
    
    def __init__(self, name: str = "Агент КиберКот"):
        self.name = name
        self.knowledge_base = KnowledgeBase()
        self.customer_db = CustomerDatabase()
        self.active_tickets = {}
        self.performance_stats = {
            "tickets_handled": 0,
            "avg_resolution_time": 0,
            "customer_satisfaction": 0,
            "escalation_rate": 0
        }
    
    def handle_ticket(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Обработка тикета поддержки"""
        print(f"\n🎧 {self.name} обрабатывает тикет #{ticket.id}")
        print(f"Клиент: {ticket.customer.name}")
        print(f"Проблема: {ticket.problem_description}")
        
        # Поиск решения в базе знаний
        solutions = self.knowledge_base.search(ticket.problem_description)
        
        if not solutions:
            return self._escalate_ticket(ticket, "Решение не найдено в базе знаний")
        
        # Выбираем лучшее решение
        best_solution = solutions[0]
        print(f"📚 Найдено решение: {best_solution.title}")
        
        # Выполняем действия
        success = self._execute_solution(ticket, best_solution)
        
        if success:
            return self._resolve_ticket(ticket, best_solution)
        else:
            return self._escalate_ticket(ticket, "Стандартное решение не помогло")
    
    def _execute_solution(self, ticket: SupportTicket, solution: KnowledgeBaseEntry) -> bool:
        """Выполнение решения"""
        print(f"🔧 Выполняю действия:")
        
        for i, step in enumerate(solution.solution_steps, 1):
            print(f"  {i}. {step}")
            time.sleep(0.1)  # Имитация работы
        
        # Имитируем успешность на основе рейтинга решения
        success_chance = solution.success_rate
        
        # Учитываем историю клиента (проблемные клиенты сложнее)
        if ticket.customer.satisfaction_score < 3.0:
            success_chance *= 0.7  # Снижаем шансы для недовольных клиентов
        
        return random.random() < success_chance
    
    def _resolve_ticket(self, ticket: SupportTicket, solution: KnowledgeBaseEntry) -> Dict[str, Any]:
        """Успешное решение тикета"""
        ticket.status = TicketStatus.RESOLVED
        ticket.resolution_time = time.time() - ticket.created_at
        
        # Оценка клиента (зависит от времени решения)
        if ticket.resolution_time < 300:  # Быстро (< 5 мин)
            satisfaction = random.uniform(4.5, 5.0)
        elif ticket.resolution_time < 900:  # Нормально (< 15 мин)
            satisfaction = random.uniform(3.5, 4.5)
        else:  # Долго
            satisfaction = random.uniform(2.0, 3.5)
        
        ticket.customer_satisfaction = satisfaction
        
        print(f"✅ Тикет решён за {ticket.resolution_time:.0f} сек")
        print(f"😊 Оценка клиента: {satisfaction:.1f}/5.0")
        
        return {
            "status": "resolved",
            "resolution_time": ticket.resolution_time,
            "customer_satisfaction": satisfaction,
            "solution_used": solution.title
        }
    
    def _escalate_ticket(self, ticket: SupportTicket, reason: str) -> Dict[str, Any]:
        """Эскалация тикета"""
        ticket.status = TicketStatus.ESCALATED
        
        print(f"⚠️ Тикет эскалирован: {reason}")
        
        return {
            "status": "escalated",
            "reason": reason,
            "escalation_time": time.time() - ticket.created_at
        }

# Тест агента
if __name__ == "__main__":
    print("🎧 ТЕСТ АГЕНТА ПОДДЕРЖКИ")
    print("=" * 40)
    
    agent = SupportAgent()
    customers = agent.customer_db
    
    # Создаём тестовые тикеты
    test_problems = [
        "У меня нет интернета, помогите!",
        "Интернет очень медленно работает",
        "Забыл пароль от wifi, как поменять?"
    ]
    
    for i, problem in enumerate(test_problems, 1):
        customer = list(customers.customers.values())[i-1]
        
        ticket = SupportTicket(
            id=f"T{i:03d}",
            customer=customer,
            problem_description=problem,
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.NEW,
            created_at=time.time(),
            agent_actions=[]
        )
        
        result = agent.handle_ticket(ticket)
        print(f"Результат: {result}")
        print("-" * 40)
    
    print("✅ Тест завершён!")
