#!/usr/bin/env python3
"""
🎧 НАСТОЯЩИЙ LLM-АГЕНТ ПОДДЕРЖКИ
Агент с реальными LLM API вызовами для анализа проблем клиентов
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import json
import asyncio
from typing import Dict, Any, Optional
from support_agent_part1_knowledge import *

# Импортируем настоящий LLM провайдер
try:
    from kittycore.llm import get_llm_provider
    REAL_LLM_AVAILABLE = True
except ImportError:
    print("⚠️ LLM провайдер не найден, используем заглушку")
    REAL_LLM_AVAILABLE = False

class RealLLMSupportAgent:
    """Настоящий LLM-агент технической поддержки"""
    
    def __init__(self, name: str = "Настоящий LLM Агент"):
        self.name = name
        self.knowledge_base = KnowledgeBase()
        self.customer_db = CustomerDatabase()
        
        if REAL_LLM_AVAILABLE:
            self.llm = get_llm_provider("meta-llama/llama-3.2-3b-instruct:free")
            print("✅ Используется настоящий LLM провайдер")
        else:
            self.llm = None
            print("❌ LLM провайдер недоступен")
    
    def analyze_problem_with_llm(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Реальный LLM-анализ проблемы клиента"""
        
        if not self.llm:
            return self._fallback_analysis(ticket)
        
        # Формируем контекст для LLM
        customer_info = f"""
КЛИЕНТ: {ticket.customer.name}
- Тарифный план: {ticket.customer.plan}
- Оборудование: {', '.join(ticket.customer.equipment)}
- История обращений: {len(ticket.customer.history)} раз
- Рейтинг удовлетворённости: {ticket.customer.satisfaction_score}/5.0
- Предыдущие проблемы: {'; '.join(ticket.customer.history[-2:]) if ticket.customer.history else 'Нет'}
"""
        
        # База знаний для контекста
        kb_info = "ДОСТУПНЫЕ РЕШЕНИЯ:\n"
        for entry in self.knowledge_base.entries:
            kb_info += f"• {entry.title} (успех: {entry.success_rate*100:.0f}%)\n"
        
        prompt = f"""Ты - эксперт по технической поддержке интернет-провайдера "КиберКот".

{customer_info}

{kb_info}

ПРОБЛЕМА КЛИЕНТА: "{ticket.problem_description}"

Проанализируй ситуацию и ответь СТРОГО в JSON формате:
{{
    "problem_category": "connectivity|performance|configuration|equipment|billing|other",
    "urgency_level": 1-5,
    "customer_mood": "calm|confused|frustrated|angry",
    "escalation_needed": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "краткое объяснение анализа"
}}

Учти:
- Если клиент пишет ЗАГЛАВНЫМИ или использует "!!!" - он злой
- Если "третий раз", "опять", "снова" - фрустрация
- Если "помогите", "не получается" - растерянность
- Если проблема повторяется у проблемного клиента (рейтинг <3) - эскалация"""

        try:
            print("🧠 Отправляю запрос к настоящему LLM...")
            response = self.llm.complete(prompt)
            
            print(f"🔍 LLM ответ: {response[:500]}...")  # Показываем первые 500 символов
            
            # Парсим JSON ответ
            analysis = json.loads(response.strip())
            
            # Валидация ответа
            required_fields = ["problem_category", "urgency_level", "customer_mood", "escalation_needed", "confidence", "reasoning"]
            if not all(field in analysis for field in required_fields):
                raise ValueError("Неполный ответ от LLM")
            
            print(f"✅ LLM анализ получен (уверенность: {analysis['confidence']:.2f})")
            return analysis
            
        except Exception as e:
            print(f"❌ Ошибка LLM анализа: {e}")
            return self._fallback_analysis(ticket)
    
    def _fallback_analysis(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Запасной анализ без LLM"""
        print("🔄 Используется запасной анализ")
        
        problem = ticket.problem_description.lower()
        
        # Простая категоризация
        if any(word in problem for word in ["нет интернета", "не работает", "отключился"]):
            category = "connectivity"
        elif any(word in problem for word in ["медленно", "тормозит", "скорость"]):
            category = "performance"
        elif any(word in problem for word in ["пароль", "настройка", "wifi"]):
            category = "configuration"
        else:
            category = "other"
        
        # Определение настроения
        if any(indicator in problem for indicator in ["!!!", "опять", "третий раз"]):
            mood = "angry"
            urgency = 5
        elif any(word in problem for word in ["помогите", "не получается"]):
            mood = "confused"
            urgency = 3
        else:
            mood = "calm"
            urgency = 2
        
        # Эскалация для проблемных клиентов
        escalation_needed = (ticket.customer.satisfaction_score < 3.0 and mood in ["angry", "frustrated"])
        
        return {
            "problem_category": category,
            "urgency_level": urgency,
            "customer_mood": mood,
            "escalation_needed": escalation_needed,
            "confidence": 0.6,  # Низкая уверенность без LLM
            "reasoning": f"Запасной анализ: {category}, клиент {mood}"
        }

# Тест настоящего LLM-агента
if __name__ == "__main__":
    def test_real_llm():
        print("🎧 ТЕСТ НАСТОЯЩЕГО LLM-АГЕНТА")
        print("=" * 50)
        
        agent = RealLLMSupportAgent()
        
        if not REAL_LLM_AVAILABLE:
            print("⚠️ LLM провайдер недоступен, тест будет использовать запасной анализ")
        
        # Тестовый случай
        customer = Customer(
            id="test_001",
            name="Тестовый Клиент",
            plan="Тест 100 Мбит/с",
            location="Тестовая улица",
            equipment=["Тестовый роутер"],
            history=["Предыдущая проблема"],
            satisfaction_score=2.5  # Проблемный клиент
        )
        
        ticket = SupportTicket(
            id="TEST_001",
            customer=customer,
            problem_description="ОПЯТЬ НЕ РАБОТАЕТ ИНТЕРНЕТ!!! Уже третий раз за неделю! Когда это кончится?!",
            priority=TicketPriority.HIGH,
            status=TicketStatus.NEW,
            created_at=time.time(),
            agent_actions=[]
        )
        
        # Анализируем проблему
        analysis = agent.analyze_problem_with_llm(ticket)
        
        print("\n📊 РЕЗУЛЬТАТ АНАЛИЗА:")
        print(f"  Категория: {analysis['problem_category']}")
        print(f"  Настроение: {analysis['customer_mood']}")
        print(f"  Срочность: {analysis['urgency_level']}/5")
        print(f"  Эскалация: {'Да' if analysis['escalation_needed'] else 'Нет'}")
        print(f"  Уверенность: {analysis['confidence']:.2f}")
        print(f"  Обоснование: {analysis['reasoning']}")
        
        print("\n✅ Тест завершён!")
    
    # Запускаем тест
    test_real_llm()
