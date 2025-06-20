#!/usr/bin/env python3
"""
🧠 АДАПТИВНЫЙ LLM-БЕНЧМАРК - ЧАСТЬ 1: КОНЦЕПЦИЯ
Революционная система оценки агентов с неизвестными заранее метриками

КЛЮЧЕВЫЕ ПРИНЦИПЫ:
1. 🎯 АДАПТИВНАЯ СЛОЖНОСТЬ - задачи усложняются в зависимости от способностей агента
2. 🔍 СКРЫТЫЕ МЕТРИКИ - критерии успеха не известны заранее
3. 🌐 МУЛЬТИМОДАЛЬНАЯ ОЦЕНКА - текст, код, логика, творчество, этика
4. 🌍 РЕАЛЬНЫЕ СЦЕНАРИИ - задачи из реального мира, а не академические
5. 🔄 ДИНАМИЧЕСКАЯ АДАПТАЦИЯ - бенчмарк учится и эволюционирует
"""

import random
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class TaskComplexity(Enum):
    """Уровни сложности задач - от простых до невозможных"""
    TRIVIAL = 1      # Простые задачи (успех 90%+)
    BASIC = 2        # Базовые задачи (успех 70-90%)
    INTERMEDIATE = 3 # Средние задачи (успех 50-70%)
    ADVANCED = 4     # Сложные задачи (успех 30-50%)
    EXPERT = 5       # Экспертные задачи (успех 10-30%)
    IMPOSSIBLE = 6   # "Невозможные" задачи (успех <10%)

class TaskDomain(Enum):
    """Домены задач - разные типы интеллекта"""
    REASONING = "reasoning"           # Логическое мышление
    CREATIVITY = "creativity"         # Творческие задачи
    ETHICS = "ethics"                # Этические дилеммы
    CODING = "coding"                # Программирование
    COMMUNICATION = "communication"   # Коммуникация
    PROBLEM_SOLVING = "problem_solving" # Решение проблем
    ADAPTATION = "adaptation"         # Адаптация к новому

@dataclass
class AdaptiveTask:
    """Адаптивная задача с скрытыми целями"""
    id: str
    domain: TaskDomain
    complexity: TaskComplexity
    description: str
    context: Dict[str, Any]
    hidden_objectives: List[str]  # Скрытые цели оценки
    time_limit: Optional[int] = None
    requires_llm: bool = True

class TaskGenerator:
    """Генератор адаптивных задач"""
    
    def __init__(self):
        self.task_templates = {
            TaskDomain.REASONING: [
                {
                    "template": "🕵️ Детектив расследует дело с {num_suspects} подозреваемыми. {evidence}. Кто виновен и почему?",
                    "hidden_objectives": ["логическая цепочка", "исключение невозможного", "работа с противоречиями"],
                    "variables": {
                        "num_suspects": [3, 4, 5, 7, 10, 15],
                        "evidence": [
                            "Найдены отпечатки пальцев на орудии убийства",
                            "Свидетель видел подозрительную фигуру в 23:30",
                            "Камеры зафиксировали странное поведение одного из подозреваемых",
                            "Обнаружены противоречивые показания трёх свидетелей",
                            "Найдены улики, указывающие на двух разных людей одновременно"
                        ]
                    }
                },
                {
                    "template": "🧩 В городе происходят странные события: {events}. Найдите закономерность и предскажите следующее.",
                    "hidden_objectives": ["распознавание паттернов", "экстраполяция", "системное мышление"],
                    "variables": {
                        "events": [
                            "каждый понедельник пропадают красные машины",
                            "в полнолуние все коты мяукают одновременно в 3:33",
                            "каждое 7-е число месяца отключается интернет на 77 минут",
                            "люди в синих куртках забывают свои имена на час"
                        ]
                    }
                }
            ],
            TaskDomain.CREATIVITY: [
                {
                    "template": "✨ Создайте рассказ о {protagonist} в мире, где {world_rule}. История должна быть {style}.",
                    "hidden_objectives": ["оригинальность", "связность сюжета", "эмоциональное воздействие"],
                    "variables": {
                        "protagonist": ["роботе-поэте", "кошке-детективе", "дереве-философе", "облаке-путешественнике"],
                        "world_rule": ["гравитация работает наоборот", "эмоции материальны", "время течёт случайно"],
                        "style": ["трогательной", "загадочной", "юмористической", "философской"]
                    }
                }
            ],
            TaskDomain.ETHICS: [
                {
                    "template": "⚖️ Автономный автомобиль должен выбрать: {choice_a} или {choice_b}. Какое решение правильное?",
                    "hidden_objectives": ["этическое обоснование", "учёт всех сторон", "принципиальность"],
                    "variables": {
                        "choice_a": ["спасти одного ребёнка", "защитить пассажира", "сохранить дорогое оборудование"],
                        "choice_b": ["спасти трёх пожилых людей", "защитить пешеходов", "минимизировать ущерб"]
                    }
                }
            ]
        }
    
    def generate_task(self, domain: TaskDomain, complexity: TaskComplexity, 
                     agent_history: Optional[Dict] = None) -> AdaptiveTask:
        """Генерация адаптивной задачи"""
        
        # Адаптация сложности под историю агента
        if agent_history:
            complexity = self._adapt_complexity(complexity, agent_history, domain)
        
        # Выбор шаблона
        templates = self.task_templates.get(domain, [])
        if not templates:
            return self._create_fallback_task(domain, complexity)
        
        template = random.choice(templates)
        
        # Генерация переменных
        variables = {}
        for var_name, var_options in template["variables"].items():
            if isinstance(var_options, list):
                # Сложность влияет на выбор
                complexity_index = min(complexity.value - 1, len(var_options) - 1)
                variables[var_name] = var_options[complexity_index]
        
        # Формирование описания
        description = template["template"].format(**variables)
        
        # Время выполнения зависит от сложности
        time_limits = {
            TaskComplexity.TRIVIAL: 120,     # 2 минуты
            TaskComplexity.BASIC: 300,       # 5 минут
            TaskComplexity.INTERMEDIATE: 600, # 10 минут
            TaskComplexity.ADVANCED: 900,    # 15 минут
            TaskComplexity.EXPERT: 1800,     # 30 минут
            TaskComplexity.IMPOSSIBLE: None   # Без лимита
        }
        
        return AdaptiveTask(
            id=f"{domain.value}_{complexity.value}_{int(time.time())}",
            domain=domain,
            complexity=complexity,
            description=description,
            context={
                "variables": variables,
                "complexity_level": complexity.value,
                "generated_at": time.time()
            },
            hidden_objectives=template["hidden_objectives"],
            time_limit=time_limits[complexity]
        )
    
    def _adapt_complexity(self, base_complexity: TaskComplexity, 
                         agent_history: Dict, domain: TaskDomain) -> TaskComplexity:
        """Адаптация сложности под историю агента"""
        domain_stats = agent_history.get(domain.value, {})
        success_rate = domain_stats.get("success_rate", 0.5)
        
        # Если агент слишком хорошо справляется - усложняем
        if success_rate > 0.8:
            new_complexity = min(base_complexity.value + 1, TaskComplexity.IMPOSSIBLE.value)
            print(f"🔥 Агент слишком хорош! Усложняем {domain.value}: {base_complexity.name} → {TaskComplexity(new_complexity).name}")
        # Если слишком плохо - упрощаем
        elif success_rate < 0.3:
            new_complexity = max(base_complexity.value - 1, TaskComplexity.TRIVIAL.value)
            print(f"💡 Агент испытывает трудности. Упрощаем {domain.value}: {base_complexity.name} → {TaskComplexity(new_complexity).name}")
        else:
            new_complexity = base_complexity.value
        
        return TaskComplexity(new_complexity)
    
    def _create_fallback_task(self, domain: TaskDomain, complexity: TaskComplexity) -> AdaptiveTask:
        """Создание запасной задачи"""
        return AdaptiveTask(
            id=f"fallback_{domain.value}_{complexity.value}",
            domain=domain,
            complexity=complexity,
            description=f"Решите задачу уровня {complexity.name} в области {domain.value}",
            context={"fallback": True},
            hidden_objectives=["базовая компетентность"],
            time_limit=300
        )

# Демонстрация концепции
if __name__ == "__main__":
    print("🧠 АДАПТИВНЫЙ LLM-БЕНЧМАРК - КОНЦЕПЦИЯ")
    print("=" * 60)
    
    generator = TaskGenerator()
    
    print("\n📋 ДОМЕНЫ ЗАДАЧ:")
    for domain in TaskDomain:
        print(f"  • {domain.value}: {domain.name}")
    
    print("\n📊 УРОВНИ СЛОЖНОСТИ:")
    for complexity in TaskComplexity:
        print(f"  • {complexity.name} (уровень {complexity.value})")
    
    print("\n🎯 ПРИМЕРЫ ЗАДАЧ:")
    print("-" * 40)
    
    # Генерируем примеры задач
    test_domains = [TaskDomain.REASONING, TaskDomain.CREATIVITY, TaskDomain.ETHICS]
    test_complexities = [TaskComplexity.BASIC, TaskComplexity.ADVANCED]
    
    for domain in test_domains:
        for complexity in test_complexities:
            task = generator.generate_task(domain, complexity)
            print(f"\n🔸 {domain.value.upper()} ({complexity.name})")
            print(f"   Задача: {task.description}")
            print(f"   Скрытые цели: {', '.join(task.hidden_objectives)}")
            if task.time_limit:
                print(f"   ⏰ Лимит: {task.time_limit//60} мин")
    
    print(f"\n✅ Концепция готова! Создано {len(test_domains) * len(test_complexities)} примеров задач.")
    print("🔄 Следующий шаг: создание системы скрытых метрик...") 