#!/usr/bin/env python3
"""
🔄 РЕАКТИВНЫЙ КУЛИНАРНЫЙ БЕНЧМАРК
Тестирует способность агента адаптироваться к обратной связи в реальном времени
"""

import asyncio
import time
from typing import List, Dict, Any
from reactive_benchmark_concept import SAMPLE_TASTERS, VirtualTaster
from adaptive_cooking_agent import AdaptiveCookingAgent

class ReactiveCookingBenchmark:
    """Бенчмарк для тестирования реактивной адаптации"""
    
    def __init__(self):
        self.tasters = SAMPLE_TASTERS
        self.test_scenarios = [
            "Приготовь пасту",
            "Сделай стейк", 
            "Приготовь салат",
            "Свари суп",
            "Приготовь пасту",  # повторяем для проверки обучения
            "Сделай стейк"      # повторяем для проверки обучения
        ]
    
    async def run_benchmark(self, agent: AdaptiveCookingAgent) -> Dict[str, Any]:
        """Запускает полный бенчмарк"""
        
        print("🔄 ЗАПУСК РЕАКТИВНОГО КУЛИНАРНОГО БЕНЧМАРКА")
        print("=" * 60)
        
        results = {
            "agent_name": agent.agent_name,
            "total_scenarios": len(self.test_scenarios),
            "attempts": [],
            "learning_progression": [],
            "final_stats": {},
            "benchmark_time": 0
        }
        
        start_time = time.time()
        
        # Выполняем все сценарии
        for i, scenario in enumerate(self.test_scenarios, 1):
            print(f"\n🎯 СЦЕНАРИЙ {i}/{len(self.test_scenarios)}: {scenario}")
            print("-" * 40)
            
            # Готовим блюдо
            attempt = await agent.cook_dish(scenario, self.tasters)
            
            # Обрабатываем результат в зависимости от типа агента
            if hasattr(attempt, 'attempt_id'):  # Обычный агент
                results["attempts"].append({
                    "scenario": scenario,
                    "attempt_id": attempt.attempt_id,
                    "avg_score": attempt.avg_score,
                    "success": attempt.success,
                    "feedbacks": [
                        {
                            "taster": f.taster_id,
                            "score": f.score,
                            "reaction": f.reaction.value,
                            "comment": f.comment
                        }
                        for f in attempt.feedbacks
                    ]
                })
            else:  # KittyCore агент возвращает словарь
                results["attempts"].append({
                    "scenario": scenario,
                    "attempt_id": attempt["attempt_id"],
                    "avg_score": attempt["avg_score"],
                    "success": attempt["success"],
                    "feedbacks": attempt["feedbacks"]
                })
            
            # Записываем прогресс обучения
            stats = agent.get_learning_stats()
            avg_score = attempt["avg_score"] if isinstance(attempt, dict) else attempt.avg_score
            results["learning_progression"].append({
                "attempt_number": i,
                "total_attempts": stats["total_attempts"],
                "successful_recipes": stats["successful_recipes"],
                "known_ingredients": stats["known_ingredients"],
                "known_techniques": stats["known_techniques"],
                "avg_score": avg_score
            })
            
            # Небольшая пауза для реалистичности
            await asyncio.sleep(0.1)
        
        end_time = time.time()
        results["benchmark_time"] = end_time - start_time
        results["final_stats"] = agent.get_learning_stats()
        
        # Анализируем результаты
        await self._analyze_results(results)
        
        return results
    
    async def _analyze_results(self, results: Dict[str, Any]):
        """Анализирует результаты бенчмарка"""
        
        print(f"\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ БЕНЧМАРКА")
        print("=" * 50)
        
        attempts = results["attempts"]
        
        # Общая статистика
        total_attempts = len(attempts)
        successful_attempts = sum(1 for a in attempts if a["success"])
        avg_score = sum(a["avg_score"] for a in attempts) / total_attempts
        
        print(f"🎯 Общая статистика:")
        print(f"   - Всего попыток: {total_attempts}")
        print(f"   - Успешных: {successful_attempts} ({successful_attempts/total_attempts*100:.1f}%)")
        print(f"   - Средняя оценка: {avg_score:.2f}/5.0")
        print(f"   - Время выполнения: {results['benchmark_time']:.2f}с")
        
        # Прогресс обучения
        progression = results["learning_progression"]
        if len(progression) >= 6:
            first_half_avg = sum(p["avg_score"] for p in progression[:3]) / 3
            second_half_avg = sum(p["avg_score"] for p in progression[3:]) / 3
        elif len(progression) >= 2:
            first_half_avg = progression[0]["avg_score"]
            second_half_avg = progression[-1]["avg_score"]
        else:
            first_half_avg = second_half_avg = progression[0]["avg_score"] if progression else 0
        improvement = second_half_avg - first_half_avg
        
        print(f"\n📈 Прогресс обучения:")
        print(f"   - Первые 3 попытки: {first_half_avg:.2f}/5.0")
        print(f"   - Последние 3 попытки: {second_half_avg:.2f}/5.0")
        print(f"   - Улучшение: {improvement:+.2f} ({'✅ Обучается' if improvement > 0 else '❌ Не обучается'})")
        
        # Анализ повторных задач
        pasta_attempts = [a for a in attempts if "паста" in a["scenario"].lower()]
        steak_attempts = [a for a in attempts if "стейк" in a["scenario"].lower()]
        
        if len(pasta_attempts) > 1:
            pasta_improvement = pasta_attempts[-1]["avg_score"] - pasta_attempts[0]["avg_score"]
            print(f"   - Улучшение пасты: {pasta_improvement:+.2f}")
        
        if len(steak_attempts) > 1:
            steak_improvement = steak_attempts[-1]["avg_score"] - steak_attempts[0]["avg_score"]
            print(f"   - Улучшение стейка: {steak_improvement:+.2f}")
        
        # Финальная статистика агента
        final_stats = results["final_stats"]
        print(f"\n🧠 Накопленные знания:")
        print(f"   - Изученных ингредиентов: {final_stats['known_ingredients']}")
        print(f"   - Изученных техник: {final_stats['known_techniques']}")
        print(f"   - Изученных дегустаторов: {final_stats['known_tasters']}")
        
        if final_stats["best_ingredients"]:
            print(f"   - Лучшие ингредиенты: {final_stats['best_ingredients'][:2]}")
        
        if final_stats["best_techniques"]:
            print(f"   - Лучшие техники: {final_stats['best_techniques'][:2]}")
        
        # Оценка реактивности
        reactivity_score = self._calculate_reactivity_score(results)
        print(f"\n🔄 Оценка реактивности: {reactivity_score:.2f}/10.0")
        
        if reactivity_score >= 8.0:
            print("🎉 ОТЛИЧНАЯ РЕАКТИВНОСТЬ! Агент быстро адаптируется!")
        elif reactivity_score >= 6.0:
            print("👍 ХОРОШАЯ РЕАКТИВНОСТЬ! Агент показывает обучение!")
        elif reactivity_score >= 4.0:
            print("⚠️ СРЕДНЯЯ РЕАКТИВНОСТЬ! Есть признаки адаптации!")
        else:
            print("❌ СЛАБАЯ РЕАКТИВНОСТЬ! Агент плохо адаптируется!")
    
    def _calculate_reactivity_score(self, results: Dict[str, Any]) -> float:
        """Вычисляет оценку реактивности агента"""
        
        progression = results["learning_progression"]
        
        # 1. Улучшение со временем (40% веса)
        if len(progression) >= 2:
            first_avg = progression[0]["avg_score"]
            second_avg = progression[-1]["avg_score"]
            improvement = max(0, second_avg - first_avg) * 2  # нормализуем к 0-2
        else:
            improvement = 0
        
        # 2. Накопление знаний (30% веса)
        final_stats = results["final_stats"]
        knowledge_score = min(2.0, (
            final_stats["known_ingredients"] * 0.1 +
            final_stats["known_techniques"] * 0.2 +
            final_stats["known_tasters"] * 0.1
        ))
        
        # 3. Успешность (20% веса)
        success_rate = sum(1 for a in results["attempts"] if a["success"]) / len(results["attempts"])
        success_score = success_rate * 2
        
        # 4. Скорость адаптации (10% веса)
        speed_score = min(2.0, 10 / results["benchmark_time"])  # быстрее = лучше
        
        total_score = (
            improvement * 4.0 +      # 40%
            knowledge_score * 3.0 +  # 30%
            success_score * 2.0 +    # 20%
            speed_score * 1.0        # 10%
        )
        
        return min(10.0, total_score)

async def main():
    """Демонстрация реактивного бенчмарка"""
    
    print("🔄 ДЕМОНСТРАЦИЯ РЕАКТИВНОГО КУЛИНАРНОГО БЕНЧМАРКА")
    print("=" * 60)
    
    # Создаём агента
    agent = AdaptiveCookingAgent("Шеф_Андрей")
    
    # Запускаем бенчмарк
    benchmark = ReactiveCookingBenchmark()
    results = await benchmark.run_benchmark(agent)
    
    print(f"\n✅ БЕНЧМАРК ЗАВЕРШЁН!")
    print(f"📊 Результаты сохранены в переменной results")

if __name__ == "__main__":
    asyncio.run(main()) 