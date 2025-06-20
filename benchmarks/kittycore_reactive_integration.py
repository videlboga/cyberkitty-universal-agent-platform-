#!/usr/bin/env python3
"""
🔄 ИНТЕГРАЦИЯ РЕАКТИВНОГО БЕНЧМАРКА С KITTYCORE 3.0
Адаптирует реактивный кулинарный бенчмарк для работы с агентами KittyCore
"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к KittyCore
sys.path.append(str(Path(__file__).parent.parent))

from typing import List, Dict, Any
from reactive_benchmark_concept import VirtualTaster, TasteReaction, TasterFeedback
from adaptive_cooking_agent import AdaptiveCookingAgent

class KittyCoreReactiveAgent:
    """Агент KittyCore адаптированный для реактивного бенчмарка"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.attempt_count = 0
        self.memory = {
            "successful_recipes": [],
            "failed_recipes": [],
            "ingredient_scores": {},
            "technique_scores": {},
            "taster_preferences": {}
        }
    
    async def cook_dish(self, dish_request: str, tasters: List[VirtualTaster]) -> Dict[str, Any]:
        """Готовит блюдо используя принципы KittyCore"""
        
        self.attempt_count += 1
        
        print(f"🤖 {self.agent_name} (KittyCore) готовит: {dish_request}")
        
        # 1. Анализируем задачу (имитация TaskAnalyzer)
        task_complexity = await self._analyze_task_complexity(dish_request)
        
        # 2. Создаём рецепт с учётом сложности и памяти
        recipe_data = await self._create_smart_recipe(dish_request, task_complexity)
        
        print(f"   Сложность задачи: {task_complexity}")
        print(f"   Ингредиенты: {recipe_data['ingredients']}")
        print(f"   Техника: {recipe_data['technique']}")
        
        # 3. Получаем обратную связь от дегустаторов
        feedbacks = []
        for taster in tasters:
            # Создаём объект рецепта для дегустатора
            from reactive_benchmark_concept import Recipe
            recipe = Recipe(
                name=recipe_data['name'],
                ingredients=recipe_data['ingredients'],
                cooking_time=recipe_data['time'],
                temperature=recipe_data['temperature'],
                technique=recipe_data['technique']
            )
            
            feedback = taster.taste_dish(recipe)
            feedbacks.append(feedback)
            print(f"   {feedback.taster_id}: {feedback.reaction.value} ({feedback.score}/5) - {feedback.comment}")
        
        # 4. Анализируем результат
        avg_score = sum(f.score for f in feedbacks) / len(feedbacks)
        success = avg_score >= 4.0
        
        # 5. Если результат плохой, применяем итеративное улучшение
        if avg_score < 3.5 and self.attempt_count <= 3:
            print(f"   🔄 Результат неудовлетворительный ({avg_score:.1f}/5.0), применяю улучшения...")
            
            # Анализируем фидбек и улучшаем рецепт
            improved_recipe = await self._improve_recipe(recipe_data, feedbacks)
            
            # Повторно тестируем улучшенный рецепт
            improved_feedbacks = []
            for taster in tasters:
                improved_recipe_obj = Recipe(
                    name=improved_recipe['name'],
                    ingredients=improved_recipe['ingredients'],
                    cooking_time=improved_recipe['time'],
                    temperature=improved_recipe['temperature'],
                    technique=improved_recipe['technique']
                )
                
                feedback = taster.taste_dish(improved_recipe_obj)
                improved_feedbacks.append(feedback)
            
            improved_avg_score = sum(f.score for f in improved_feedbacks) / len(improved_feedbacks)
            
            if improved_avg_score > avg_score:
                print(f"   ✅ Улучшение успешно! {avg_score:.1f} → {improved_avg_score:.1f}")
                recipe_data = improved_recipe
                feedbacks = improved_feedbacks
                avg_score = improved_avg_score
                success = avg_score >= 4.0
            else:
                print(f"   ⚠️ Улучшение не помогло: {improved_avg_score:.1f}")
        
        # 6. Обновляем память (имитация AgentLearningSystem)
        await self._update_memory(recipe_data, avg_score, success, feedbacks)
        
        print(f"   📊 Средняя оценка: {avg_score:.1f}/5.0 ({'✅ Успех' if success else '❌ Неудача'})")
        
        return {
            "attempt_id": f"kittycore_attempt_{self.attempt_count}",
            "recipe": recipe_data,
            "feedbacks": [
                {
                    "taster": f.taster_id,
                    "score": f.score,
                    "reaction": f.reaction.value,
                    "comment": f.comment
                }
                for f in feedbacks
            ],
            "avg_score": avg_score,
            "success": success
        }
    
    async def _analyze_task_complexity(self, dish_request: str) -> str:
        """Анализирует сложность кулинарной задачи"""
        
        complex_dishes = ["суп", "стейк", "ризотто", "суфле"]
        simple_dishes = ["салат", "бутерброд", "смузи"]
        
        dish_lower = dish_request.lower()
        
        if any(complex_dish in dish_lower for complex_dish in complex_dishes):
            return "высокая"
        elif any(simple_dish in dish_lower for simple_dish in simple_dishes):
            return "низкая"
        else:
            return "средняя"
    
    async def _create_smart_recipe(self, dish_request: str, complexity: str) -> Dict[str, Any]:
        """Создаёт умный рецепт с учётом сложности и памяти"""
        
        # Базовые рецепты
        base_recipes = {
            "паста": {
                "ingredients": {"макароны": 200, "томаты": 150, "сыр": 50, "оливковое_масло": 30},
                "technique": "варка",
                "time": 15,
                "temp": 100
            },
            "стейк": {
                "ingredients": {"говядина": 300, "соль": 5, "перец": 3, "масло": 20},
                "technique": "жарка",
                "time": 10,
                "temp": 200
            },
            "салат": {
                "ingredients": {"салат": 100, "помидоры": 80, "огурцы": 60, "оливковое_масло": 20},
                "technique": "смешивание",
                "time": 5,
                "temp": 20
            },
            "суп": {
                "ingredients": {"бульон": 500, "овощи": 200, "мясо": 150, "соль": 8},
                "technique": "варка",
                "time": 30,
                "temp": 90
            }
        }
        
        # Определяем тип блюда
        dish_type = "паста"  # по умолчанию
        for dish in base_recipes.keys():
            if dish in dish_request.lower():
                dish_type = dish
                break
        
        base = base_recipes[dish_type]
        ingredients = base["ingredients"].copy()
        
        # Адаптируем на основе сложности
        if complexity == "высокая":
            # Добавляем сложные ингредиенты
            if dish_type == "стейк":
                ingredients["трюфели"] = 10
                ingredients["вино"] = 50
            elif dish_type == "суп":
                ingredients["специи"] = 15
                ingredients["зелень"] = 30
        elif complexity == "низкая":
            # Упрощаем рецепт
            ingredients = {k: v for k, v in ingredients.items() if v > 50}  # только основные ингредиенты
        
        # Применяем накопленную память
        if self.memory["ingredient_scores"]:
            for ingredient, amount in list(ingredients.items()):
                if ingredient in self.memory["ingredient_scores"]:
                    score = self.memory["ingredient_scores"][ingredient]
                    if score > 3.5:  # хороший ингредиент
                        ingredients[ingredient] = amount * 1.3
                    elif score < 2.5:  # плохой ингредиент
                        ingredients[ingredient] = amount * 0.7
        
        # Выбираем лучшую технику из памяти
        technique = base["technique"]
        if self.memory["technique_scores"]:
            best_technique = max(self.memory["technique_scores"].items(), key=lambda x: x[1])
            if best_technique[1] > 3.5:
                technique = best_technique[0]
        
        return {
            "name": f"{dish_request}_{self.attempt_count}",
            "ingredients": ingredients,
            "technique": technique,
            "time": base["time"],
            "temperature": base["temp"]
        }
    
    async def _improve_recipe(self, recipe_data: Dict, feedbacks: List[TasterFeedback]) -> Dict[str, Any]:
        """Улучшает рецепт на основе обратной связи"""
        
        improved_recipe = recipe_data.copy()
        improved_recipe["name"] = f"{recipe_data['name']}_improved"
        
        # Анализируем фидбек
        avg_score = sum(f.score for f in feedbacks) / len(feedbacks)
        low_scores = [f for f in feedbacks if f.score <= 2]
        
        # Если много низких оценок, меняем технику
        if len(low_scores) >= 2:
            technique_alternatives = {
                "варка": "тушение",
                "жарка": "запекание",
                "запекание": "гриль",
                "тушение": "варка",
                "смешивание": "смешивание"  # остаётся тем же
            }
            
            current_technique = improved_recipe["technique"]
            if current_technique in technique_alternatives:
                improved_recipe["technique"] = technique_alternatives[current_technique]
                print(f"     🔄 Меняю технику: {current_technique} → {improved_recipe['technique']}")
        
        # Если оценки очень низкие, добавляем "улучшающие" ингредиенты
        if avg_score < 2.5:
            improvement_ingredients = {
                "специи": 10,
                "зелень": 20,
                "лимон": 15
            }
            
            for ingredient, amount in improvement_ingredients.items():
                if ingredient not in improved_recipe["ingredients"]:
                    improved_recipe["ingredients"][ingredient] = amount
                    print(f"     ➕ Добавляю {ingredient}: {amount}")
        
        # Корректируем количества на основе предпочтений дегустаторов
        for feedback in feedbacks:
            if feedback.score <= 2:
                # Уменьшаем количество ингредиентов для недовольных дегустаторов
                for ingredient in list(improved_recipe["ingredients"].keys()):
                    if "мясо" in ingredient.lower() and "вегетарианка" in feedback.taster_id:
                        improved_recipe["ingredients"][ingredient] *= 0.5
                        print(f"     📉 Уменьшаю {ingredient} для {feedback.taster_id}")
                    elif "сахар" in ingredient.lower() and "гурман" in feedback.taster_id:
                        improved_recipe["ingredients"][ingredient] *= 0.8
                        print(f"     📉 Уменьшаю {ingredient} для {feedback.taster_id}")
        
        return improved_recipe
    
    async def _update_memory(self, recipe_data: Dict, avg_score: float, success: bool, feedbacks: List):
        """Обновляет память агента"""
        
        # Обновляем списки рецептов
        if success:
            self.memory["successful_recipes"].append(recipe_data)
            self.memory["successful_recipes"] = self.memory["successful_recipes"][-5:]
        else:
            self.memory["failed_recipes"].append(recipe_data)
            self.memory["failed_recipes"] = self.memory["failed_recipes"][-5:]
        
        # Обновляем оценки ингредиентов
        for ingredient in recipe_data["ingredients"]:
            if ingredient not in self.memory["ingredient_scores"]:
                self.memory["ingredient_scores"][ingredient] = avg_score
            else:
                current = self.memory["ingredient_scores"][ingredient]
                self.memory["ingredient_scores"][ingredient] = (current + avg_score) / 2
        
        # Обновляем оценки техник
        technique = recipe_data["technique"]
        if technique not in self.memory["technique_scores"]:
            self.memory["technique_scores"][technique] = avg_score
        else:
            current = self.memory["technique_scores"][technique]
            self.memory["technique_scores"][technique] = (current + avg_score) / 2
        
        # Анализируем предпочтения дегустаторов
        for feedback in feedbacks:
            taster_id = feedback.taster_id
            if taster_id not in self.memory["taster_preferences"]:
                self.memory["taster_preferences"][taster_id] = {}
            
            for ingredient in recipe_data["ingredients"]:
                if ingredient not in self.memory["taster_preferences"][taster_id]:
                    self.memory["taster_preferences"][taster_id][ingredient] = feedback.score
                else:
                    current = self.memory["taster_preferences"][taster_id][ingredient]
                    self.memory["taster_preferences"][taster_id][ingredient] = (current + feedback.score) / 2
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Возвращает статистику обучения"""
        
        return {
            "total_attempts": self.attempt_count,
            "successful_recipes": len(self.memory["successful_recipes"]),
            "failed_recipes": len(self.memory["failed_recipes"]),
            "known_ingredients": len(self.memory["ingredient_scores"]),
            "known_techniques": len(self.memory["technique_scores"]),
            "known_tasters": len(self.memory.get("taster_preferences", {})),
            "best_ingredients": sorted(
                self.memory["ingredient_scores"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3],
            "best_techniques": sorted(
                self.memory["technique_scores"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
        }

async def run_kittycore_reactive_benchmark():
    """Запускает реактивный бенчмарк с агентом KittyCore"""
    
    print("🤖 РЕАКТИВНЫЙ БЕНЧМАРК С KITTYCORE 3.0")
    print("=" * 50)
    
    # Импортируем компоненты бенчмарка
    from reactive_benchmark_concept import SAMPLE_TASTERS
    from reactive_cooking_benchmark import ReactiveCookingBenchmark
    
    # Создаём KittyCore агента
    kittycore_agent = KittyCoreReactiveAgent("KittyCore_Chef")
    
    # Адаптируем бенчмарк для KittyCore
    class KittyCoreReactiveBenchmark(ReactiveCookingBenchmark):
        def __init__(self):
            super().__init__()
            # Упрощаем сценарии для демонстрации
            self.test_scenarios = [
                "Приготовь пасту",
                "Сделай стейк",
                "Приготовь салат",
                "Приготовь пасту"  # повторяем для проверки обучения
            ]
    
    # Запускаем бенчмарк
    benchmark = KittyCoreReactiveBenchmark()
    results = await benchmark.run_benchmark(kittycore_agent)
    
    print(f"\n🎉 KITTYCORE РЕАКТИВНЫЙ БЕНЧМАРК ЗАВЕРШЁН!")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_kittycore_reactive_benchmark()) 