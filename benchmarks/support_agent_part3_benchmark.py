#!/usr/bin/env python3
"""
🎧 БЕНЧМАРК АГЕНТА ПОДДЕРЖКИ - ЧАСТЬ 3: СИСТЕМА ОЦЕНКИ
Реалистичная оценка качества работы агентов поддержки
"""

import time
import random
from typing import List, Dict, Any
from support_agent_part1_knowledge import *
from support_agent_part2_agent import SupportAgent

class SupportBenchmark:
    """Бенчмарк для оценки агентов поддержки"""
    
    def __init__(self):
        self.test_scenarios = self._create_test_scenarios()
    
    def _create_test_scenarios(self) -> List[Dict[str, Any]]:
        """Создание тестовых сценариев"""
        return [
            # Простые случаи
            {
                "customer_id": "cust_001",
                "problem": "Нет интернета дома",
                "priority": TicketPriority.MEDIUM,
                "expected_resolution": True,
                "difficulty": "easy"
            },
            {
                "customer_id": "cust_002", 
                "problem": "Медленно загружаются сайты",
                "priority": TicketPriority.LOW,
                "expected_resolution": True,
                "difficulty": "easy"
            },
            
            # Средние случаи
            {
                "customer_id": "cust_001",
                "problem": "Как поменять пароль wifi?",
                "priority": TicketPriority.LOW,
                "expected_resolution": True,
                "difficulty": "medium"
            },
            {
                "customer_id": "cust_002",
                "problem": "Роутер не включается совсем",
                "priority": TicketPriority.HIGH,
                "expected_resolution": False,  # Требует эскалации
                "difficulty": "medium"
            },
            
            # Сложные случаи
            {
                "customer_id": "cust_003",  # Проблемный клиент
                "problem": "Опять интернет не работает! Уже третий раз!",
                "priority": TicketPriority.HIGH,
                "expected_resolution": False,  # Сложный клиент
                "difficulty": "hard"
            },
            {
                "customer_id": "cust_001",
                "problem": "У всех соседей тоже нет интернета",
                "priority": TicketPriority.URGENT,
                "expected_resolution": False,  # Массовая авария
                "difficulty": "hard"
            }
        ]
    
    def evaluate_agent(self, agent: SupportAgent) -> Dict[str, Any]:
        """Оценка агента по всем сценариям"""
        print(f"\n🎯 ОЦЕНКА АГЕНТА: {agent.name}")
        print("=" * 50)
        
        results = []
        total_time = 0
        total_satisfaction = 0
        resolved_count = 0
        escalated_count = 0
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            print(f"\n📋 Сценарий {i}/{len(self.test_scenarios)} ({scenario['difficulty'].upper()})")
            
            # Создаём тикет
            customer = agent.customer_db.get_customer(scenario["customer_id"])
            ticket = SupportTicket(
                id=f"BENCH_{i:03d}",
                customer=customer,
                problem_description=scenario["problem"],
                priority=scenario["priority"],
                status=TicketStatus.NEW,
                created_at=time.time(),
                agent_actions=[]
            )
            
            # Обрабатываем тикет
            start_time = time.time()
            result = agent.handle_ticket(ticket)
            end_time = time.time()
            
            # Анализируем результат
            scenario_result = {
                "scenario": i,
                "difficulty": scenario["difficulty"],
                "expected": scenario["expected_resolution"],
                "actual_status": result["status"],
                "processing_time": end_time - start_time,
                "customer_satisfaction": result.get("customer_satisfaction", 0),
                "correct_prediction": (result["status"] == "resolved") == scenario["expected_resolution"]
            }
            
            results.append(scenario_result)
            
            # Статистика
            total_time += scenario_result["processing_time"]
            if result["status"] == "resolved":
                resolved_count += 1
                total_satisfaction += scenario_result["customer_satisfaction"]
            else:
                escalated_count += 1
            
            print(f"✅ Ожидание: {'Решить' if scenario['expected_resolution'] else 'Эскалировать'}")
            print(f"📊 Результат: {result['status']} ({'✅' if scenario_result['correct_prediction'] else '❌'})")
        
        # Итоговые метрики
        avg_time = total_time / len(self.test_scenarios)
        resolution_rate = resolved_count / len(self.test_scenarios)
        escalation_rate = escalated_count / len(self.test_scenarios)
        avg_satisfaction = total_satisfaction / max(resolved_count, 1)
        
        accuracy = sum(1 for r in results if r["correct_prediction"]) / len(results)
        
        # Оценка по сложности
        easy_results = [r for r in results if r["difficulty"] == "easy"]
        medium_results = [r for r in results if r["difficulty"] == "medium"]  
        hard_results = [r for r in results if r["difficulty"] == "hard"]
        
        easy_accuracy = sum(1 for r in easy_results if r["correct_prediction"]) / len(easy_results) if easy_results else 0
        medium_accuracy = sum(1 for r in medium_results if r["correct_prediction"]) / len(medium_results) if medium_results else 0
        hard_accuracy = sum(1 for r in hard_results if r["correct_prediction"]) / len(hard_results) if hard_results else 0
        
        # Итоговый балл (0-100)
        final_score = (
            accuracy * 40 +           # Точность решений (40%)
            (avg_satisfaction/5) * 30 + # Удовлетворённость клиентов (30%)
            (1 - avg_time/10) * 20 +  # Скорость работы (20%)
            (easy_accuracy * 0.3 + medium_accuracy * 0.4 + hard_accuracy * 0.3) * 10  # Работа со сложностью (10%)
        )
        
        return {
            "agent_name": agent.name,
            "total_scenarios": len(self.test_scenarios),
            "resolved_tickets": resolved_count,
            "escalated_tickets": escalated_count,
            "resolution_rate": resolution_rate,
            "escalation_rate": escalation_rate,
            "avg_processing_time": avg_time,
            "avg_customer_satisfaction": avg_satisfaction,
            "accuracy": accuracy,
            "easy_accuracy": easy_accuracy,
            "medium_accuracy": medium_accuracy,
            "hard_accuracy": hard_accuracy,
            "final_score": final_score,
            "detailed_results": results
        }
    
    def print_evaluation_report(self, evaluation: Dict[str, Any]):
        """Печать отчёта об оценке"""
        print(f"\n📊 ИТОГОВЫЙ ОТЧЁТ: {evaluation['agent_name']}")
        print("=" * 60)
        
        print(f"🎯 Итоговый балл: {evaluation['final_score']:.1f}/100")
        print()
        
        print("📈 ОСНОВНЫЕ МЕТРИКИ:")
        print(f"  • Решено тикетов: {evaluation['resolved_tickets']}/{evaluation['total_scenarios']} ({evaluation['resolution_rate']*100:.1f}%)")
        print(f"  • Эскалировано: {evaluation['escalated_tickets']}/{evaluation['total_scenarios']} ({evaluation['escalation_rate']*100:.1f}%)")
        print(f"  • Точность решений: {evaluation['accuracy']*100:.1f}%")
        print(f"  • Среднее время: {evaluation['avg_processing_time']:.2f} сек")
        print(f"  • Удовлетворённость: {evaluation['avg_customer_satisfaction']:.1f}/5.0")
        print()
        
        print("🎚️ РАБОТА ПО СЛОЖНОСТИ:")
        print(f"  • Простые задачи: {evaluation['easy_accuracy']*100:.1f}%")
        print(f"  • Средние задачи: {evaluation['medium_accuracy']*100:.1f}%") 
        print(f"  • Сложные задачи: {evaluation['hard_accuracy']*100:.1f}%")
        
        # Оценка качества
        if evaluation['final_score'] >= 80:
            grade = "🏆 ОТЛИЧНО"
        elif evaluation['final_score'] >= 60:
            grade = "👍 ХОРОШО"
        elif evaluation['final_score'] >= 40:
            grade = "⚠️ УДОВЛЕТВОРИТЕЛЬНО"
        else:
            grade = "❌ НЕУДОВЛЕТВОРИТЕЛЬНО"
        
        print(f"\n🏅 ИТОГОВАЯ ОЦЕНКА: {grade}")

# Тест бенчмарка
if __name__ == "__main__":
    print("🎯 ТЕСТ БЕНЧМАРКА АГЕНТА ПОДДЕРЖКИ")
    
    # Создаём агента и бенчмарк
    agent = SupportAgent("Тестовый Агент")
    benchmark = SupportBenchmark()
    
    # Оцениваем агента
    evaluation = benchmark.evaluate_agent(agent)
    
    # Печатаем отчёт
    benchmark.print_evaluation_report(evaluation)
    
    print(f"\n✅ Бенчмарк завершён!") 