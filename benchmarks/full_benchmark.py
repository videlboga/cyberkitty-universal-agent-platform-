#!/usr/bin/env python3
"""
🎧 ПОЛНЫЙ БЕНЧМАРК АГЕНТОВ ПОДДЕРЖКИ
Сравнение базового агента и настоящего LLM агента
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import json
from typing import Dict, Any
from support_agent_part1_knowledge import *
from support_agent_part2_agent import SupportAgent
from support_agent_part3_benchmark import SupportBenchmark

# Импортируем настоящий LLM провайдер
try:
    from kittycore.llm import get_llm_provider
    REAL_LLM_AVAILABLE = True
except ImportError:
    print("⚠️ LLM провайдер не найден")
    REAL_LLM_AVAILABLE = False

class AdvancedLLMSupportAgent:
    """Продвинутый LLM-агент поддержки для бенчмарка"""
    
    def __init__(self, name: str = "LLM Агент Поддержки"):
        self.name = name
        self.knowledge_base = KnowledgeBase()
        self.customer_db = CustomerDatabase()
        
        if REAL_LLM_AVAILABLE:
            self.llm = get_llm_provider("meta-llama/llama-3.2-3b-instruct:free")
            print("✅ LLM агент использует настоящий провайдер")
        else:
            self.llm = None
            print("❌ LLM провайдер недоступен")
    
    def handle_ticket(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Обработка тикета с помощью LLM"""
        
        if not self.llm:
            return self._fallback_handling(ticket)
        
        # Подготавливаем контекст для LLM
        customer_info = f"""
ИНФОРМАЦИЯ О КЛИЕНТЕ:
- Имя: {ticket.customer.name}
- Тарифный план: {ticket.customer.plan}
- Оборудование: {', '.join(ticket.customer.equipment)}
- История обращений: {len(ticket.customer.history)} раз
- Рейтинг удовлетворённости: {ticket.customer.satisfaction_score}/5.0
- Предыдущие проблемы: {'; '.join(ticket.customer.history[-3:]) if ticket.customer.history else 'Нет'}
"""
        
        # Доступные решения
        solutions_info = "ДОСТУПНЫЕ РЕШЕНИЯ:\n"
        for entry in self.knowledge_base.entries:
            solutions_info += f"• {entry.title} (успех: {entry.success_rate*100:.0f}%)\n"
        
        prompt = f"""Ты - эксперт по технической поддержке интернет-провайдера "КиберКот".

{customer_info}

{solutions_info}

ПРОБЛЕМА КЛИЕНТА: "{ticket.problem_description}"
ПРИОРИТЕТ: {ticket.priority.value}

Проанализируй ситуацию и реши что делать. Ответь СТРОГО в JSON формате:
{{
    "action": "resolve|escalate",
    "solution_title": "название решения из базы знаний или null",
    "reasoning": "краткое объяснение решения",
    "customer_satisfaction": 1-5,
    "resolution_confidence": 0.0-1.0
}}

ПРАВИЛА РЕШЕНИЙ:
- Если есть подходящее решение в базе знаний - используй его (action: "resolve")
- Если клиент злой или проблема повторяется часто - эскалируй (action: "escalate")
- Если проблема технически сложная или нет подходящего решения - эскалируй
- Для массовых аварий ("у соседей тоже") - всегда эскалируй
- Учитывай рейтинг клиента: низкий рейтинг = больше внимания"""

        try:
            response = self.llm.complete(prompt)
            analysis = json.loads(response.strip())
            
            # Валидация ответа
            required_fields = ["action", "reasoning", "customer_satisfaction", "resolution_confidence"]
            if not all(field in analysis for field in required_fields):
                raise ValueError("Неполный ответ от LLM")
            
            # Формируем результат
            if analysis["action"] == "resolve" and analysis.get("solution_title"):
                status = "resolved"
                # Ищем решение в базе знаний
                solutions = self.knowledge_base.search(analysis["solution_title"])
                resolution_time = 15  # Стандартное время решения
            else:
                status = "escalated"
                resolution_time = 5  # Быстрая эскалация
            
            return {
                "status": status,
                "solution": analysis.get("solution_title", "Эскалация"),
                "resolution_time": resolution_time,
                "customer_satisfaction": analysis["customer_satisfaction"],
                "reasoning": analysis["reasoning"],
                "confidence": analysis["resolution_confidence"]
            }
            
        except Exception as e:
            print(f"❌ Ошибка LLM: {e}")
            return self._fallback_handling(ticket)
    
    def _fallback_handling(self, ticket: SupportTicket) -> Dict[str, Any]:
        """Запасная обработка без LLM"""
        print("🔄 Используется запасная обработка")
        
        # Простая логика
        problem = ticket.problem_description.lower()
        
        if any(word in problem for word in ["опять", "третий раз", "злой"]):
            return {
                "status": "escalated",
                "solution": "Эскалация для проблемного клиента",
                "resolution_time": 5,
                "customer_satisfaction": 2,
                "reasoning": "Запасная эскалация",
                "confidence": 0.5
            }
        else:
            return {
                "status": "resolved",
                "solution": "Стандартное решение",
                "resolution_time": 10,
                "customer_satisfaction": 3,
                "reasoning": "Запасное решение",
                "confidence": 0.6
            }

def run_full_benchmark():
    """Запуск полного бенчмарка"""
    print("🎯 ПОЛНЫЙ БЕНЧМАРК АГЕНТОВ ПОДДЕРЖКИ")
    print("=" * 60)
    
    benchmark = SupportBenchmark()
    
    # Тестируем базового агента
    print("\n🤖 ТЕСТИРОВАНИЕ БАЗОВОГО АГЕНТА")
    basic_agent = SupportAgent("Базовый Агент")
    basic_evaluation = benchmark.evaluate_agent(basic_agent)
    benchmark.print_evaluation_report(basic_evaluation)
    
    # Тестируем LLM агента
    if REAL_LLM_AVAILABLE:
        print("\n🧠 ТЕСТИРОВАНИЕ LLM АГЕНТА С НАСТОЯЩИМ LLM")
        llm_agent = AdvancedLLMSupportAgent("LLM Агент")
        llm_evaluation = benchmark.evaluate_agent(llm_agent)
        benchmark.print_evaluation_report(llm_evaluation)
        
        # Сравнение результатов
        print("\n📊 СРАВНЕНИЕ АГЕНТОВ")
        print("=" * 60)
        
        print(f"🏆 ИТОГОВЫЕ БАЛЛЫ:")
        print(f"  Базовый агент: {basic_evaluation['final_score']:.1f}/100")
        print(f"  LLM агент:     {llm_evaluation['final_score']:.1f}/100")
        
        improvement = llm_evaluation['final_score'] - basic_evaluation['final_score']
        print(f"  Улучшение:     {improvement:+.1f} баллов")
        
        print(f"\n📈 ДЕТАЛЬНОЕ СРАВНЕНИЕ:")
        print(f"  Точность решений:")
        print(f"    Базовый: {basic_evaluation['accuracy']*100:.1f}%")
        print(f"    LLM:     {llm_evaluation['accuracy']*100:.1f}%")
        
        print(f"  Удовлетворённость клиентов:")
        print(f"    Базовый: {basic_evaluation['avg_customer_satisfaction']:.1f}/5.0")
        print(f"    LLM:     {llm_evaluation['avg_customer_satisfaction']:.1f}/5.0")
        
        print(f"  Сложные задачи:")
        print(f"    Базовый: {basic_evaluation['hard_accuracy']*100:.1f}%")
        print(f"    LLM:     {llm_evaluation['hard_accuracy']*100:.1f}%")
        
        # Итоговый вердикт
        if improvement > 10:
            verdict = "🚀 LLM АГЕНТ ЗНАЧИТЕЛЬНО ПРЕВОСХОДИТ БАЗОВЫЙ!"
        elif improvement > 0:
            verdict = "✅ LLM агент лучше базового"
        elif improvement == 0:
            verdict = "⚖️ Агенты показывают одинаковые результаты"
        else:
            verdict = "❌ Базовый агент лучше LLM агента"
        
        print(f"\n{verdict}")
        
    else:
        print("\n⚠️ LLM провайдер недоступен, тестируем только базового агента")
    
    print(f"\n✅ Полный бенчмарк завершён!")

if __name__ == "__main__":
    run_full_benchmark() 