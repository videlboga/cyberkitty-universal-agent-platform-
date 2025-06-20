#!/usr/bin/env python3
"""
👨‍🍳 АДАПТИВНЫЙ КУЛИНАРНЫЙ АГЕНТ
Агент, который учится готовить на основе реакций дегустаторов
"""

import asyncio
import random
from typing import List, Dict, Any
from dataclasses import dataclass
from reactive_benchmark_concept import Recipe, TasterFeedback, CookingAttempt, VirtualTaster

@dataclass
class CookingMemory:
    """Память агента о приготовлении"""
    successful_recipes: List[Recipe]
    failed_recipes: List[Recipe]
    ingredient_scores: Dict[str, float]  # ингредиент -> средняя оценка
    technique_scores: Dict[str, float]   # техника -> средняя оценка
    taster_preferences: Dict[str, Dict[str, float]]  # дегустатор -> предпочтения

class AdaptiveCookingAgent:
    """Адаптивный кулинарный агент"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.memory = CookingMemory(
            successful_recipes=[],
            failed_recipes=[],
            ingredient_scores={},
            technique_scores={},
            taster_preferences={}
        )
        self.attempt_count = 0
    
    async def cook_dish(self, dish_request: str, tasters: List[VirtualTaster]) -> CookingAttempt:
        """Готовит блюдо и получает обратную связь"""
        
        self.attempt_count += 1
        
        # 1. Создаём рецепт на основе запроса и памяти
        recipe = await self._create_recipe(dish_request)
        
        print(f"👨‍🍳 {self.agent_name} готовит: {recipe.name}")
        print(f"   Ингредиенты: {recipe.ingredients}")
        print(f"   Техника: {recipe.technique}")
        
        # 2. Получаем обратную связь от дегустаторов
        feedbacks = []
        for taster in tasters:
            feedback = taster.taste_dish(recipe)
            feedbacks.append(feedback)
            print(f"   {feedback.taster_id}: {feedback.reaction.value} ({feedback.score}/5) - {feedback.comment}")
        
        # 3. Анализируем результат
        avg_score = sum(f.score for f in feedbacks) / len(feedbacks)
        success = avg_score >= 4.0
        
        attempt = CookingAttempt(
            attempt_id=f"attempt_{self.attempt_count}",
            recipe=recipe,
            feedbacks=feedbacks,
            avg_score=avg_score,
            success=success
        )
        
        # 4. Обновляем память
        await self._update_memory(attempt)
        
        print(f"   📊 Средняя оценка: {avg_score:.1f}/5.0 ({'✅ Успех' if success else '❌ Неудача'})")
        
        return attempt
    
    async def _create_recipe(self, dish_request: str) -> Recipe:
        """Создаёт рецепт на основе запроса и накопленной памяти"""
        
        # Базовые рецепты для разных блюд
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
        
        # Адаптируем рецепт на основе памяти
        if self.memory.ingredient_scores:
            # Увеличиваем количество успешных ингредиентов
            for ingredient, amount in ingredients.items():
                if ingredient in self.memory.ingredient_scores:
                    score = self.memory.ingredient_scores[ingredient]
                    if score > 3.5:  # хороший ингредиент
                        ingredients[ingredient] = amount * 1.2
                    elif score < 2.5:  # плохой ингредиент
                        ingredients[ingredient] = amount * 0.8
        
        # Выбираем технику на основе опыта
        technique = base["technique"]
        if self.memory.technique_scores:
            best_technique = max(self.memory.technique_scores.items(), key=lambda x: x[1])
            if best_technique[1] > 3.5:
                technique = best_technique[0]
        
        return Recipe(
            name=f"{dish_request}_{self.attempt_count}",
            ingredients=ingredients,
            cooking_time=base["time"],
            temperature=base["temp"],
            technique=technique
        )
    
    async def _update_memory(self, attempt: CookingAttempt):
        """Обновляет память агента на основе результата"""
        
        recipe = attempt.recipe
        avg_score = attempt.avg_score
        
        # Обновляем списки успешных/неудачных рецептов
        if attempt.success:
            self.memory.successful_recipes.append(recipe)
            self.memory.successful_recipes = self.memory.successful_recipes[-5:]  # последние 5
        else:
            self.memory.failed_recipes.append(recipe)
            self.memory.failed_recipes = self.memory.failed_recipes[-5:]  # последние 5
        
        # Обновляем оценки ингредиентов
        for ingredient in recipe.ingredients:
            if ingredient not in self.memory.ingredient_scores:
                self.memory.ingredient_scores[ingredient] = avg_score
            else:
                # Скользящее среднее
                current = self.memory.ingredient_scores[ingredient]
                self.memory.ingredient_scores[ingredient] = (current + avg_score) / 2
        
        # Обновляем оценки техник
        technique = recipe.technique
        if technique not in self.memory.technique_scores:
            self.memory.technique_scores[technique] = avg_score
        else:
            current = self.memory.technique_scores[technique]
            self.memory.technique_scores[technique] = (current + avg_score) / 2
        
        # Анализируем предпочтения дегустаторов
        for feedback in attempt.feedbacks:
            taster_id = feedback.taster_id
            if taster_id not in self.memory.taster_preferences:
                self.memory.taster_preferences[taster_id] = {}
            
            # Записываем реакцию на ингредиенты
            for ingredient in recipe.ingredients:
                if ingredient not in self.memory.taster_preferences[taster_id]:
                    self.memory.taster_preferences[taster_id][ingredient] = feedback.score
                else:
                    current = self.memory.taster_preferences[taster_id][ingredient]
                    self.memory.taster_preferences[taster_id][ingredient] = (current + feedback.score) / 2
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Возвращает статистику обучения"""
        
        return {
            "total_attempts": self.attempt_count,
            "successful_recipes": len(self.memory.successful_recipes),
            "failed_recipes": len(self.memory.failed_recipes),
            "known_ingredients": len(self.memory.ingredient_scores),
            "known_techniques": len(self.memory.technique_scores),
            "known_tasters": len(self.memory.taster_preferences),
            "best_ingredients": sorted(
                self.memory.ingredient_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3],
            "best_techniques": sorted(
                self.memory.technique_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
        }

print("👨‍🍳 АДАПТИВНЫЙ КУЛИНАРНЫЙ АГЕНТ ГОТОВ!")
print("🧠 Возможности:")
print("   - Создаёт рецепты на основе запросов")
print("   - Адаптируется к обратной связи")
print("   - Запоминает предпочтения дегустаторов")
print("   - Улучшает рецепты со временем") 