#!/usr/bin/env python3
"""
🔄 РЕАКТИВНЫЙ БЕНЧМАРК ДЛЯ ПРОЦЕССНЫХ ЗАДАЧ
Концепция: Адаптивный Кулинарный Помощник

ИДЕЯ:
Агент готовит блюда и получает мгновенную обратную связь от "дегустаторов".
На основе реакций агент адаптирует рецепты в реальном времени.

ПРЕИМУЩЕСТВА:
- Быстрые циклы обратной связи (секунды)
- Измеримые результаты (оценки вкуса)
- Реалистичная задача (как агент поддержки)
- Простая для понимания логика
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum
import random
import asyncio

class TasteReaction(Enum):
    """Реакции дегустаторов"""
    LOVE = "😍"      # 5 баллов
    LIKE = "😋"      # 4 балла  
    OK = "😐"        # 3 балла
    DISLIKE = "😕"   # 2 балла
    HATE = "🤢"      # 1 балл

@dataclass
class Recipe:
    """Рецепт блюда"""
    name: str
    ingredients: Dict[str, float]  # ингредиент -> количество
    cooking_time: int  # минуты
    temperature: int   # градусы
    technique: str     # способ приготовления

@dataclass
class TasterFeedback:
    """Обратная связь от дегустатора"""
    taster_id: str
    reaction: TasteReaction
    score: int  # 1-5
    comment: str
    timestamp: float

@dataclass
class CookingAttempt:
    """Попытка приготовления"""
    attempt_id: str
    recipe: Recipe
    feedbacks: List[TasterFeedback]
    avg_score: float
    success: bool  # >= 4.0 средний балл

class VirtualTaster:
    """Виртуальный дегустатор с предпочтениями"""
    
    def __init__(self, taster_id: str, preferences: Dict[str, float]):
        self.taster_id = taster_id
        self.preferences = preferences  # ингредиент -> предпочтение (-1 до 1)
        self.mood_factor = random.uniform(0.8, 1.2)  # случайность
    
    def taste_dish(self, recipe: Recipe) -> TasterFeedback:
        """Дегустирует блюдо и даёт обратную связь"""
        
        # Базовая оценка на основе предпочтений
        score = 3.0  # нейтральная база
        
        # Анализируем ингредиенты
        for ingredient, amount in recipe.ingredients.items():
            if ingredient in self.preferences:
                preference = self.preferences[ingredient]
                # Влияние предпочтения и количества
                impact = preference * min(amount / 100, 1.0)  # нормализуем количество
                score += impact
        
        # Влияние техники приготовления
        technique_bonus = {
            "жарка": 0.5,
            "варка": 0.2, 
            "запекание": 0.8,
            "тушение": 0.6,
            "гриль": 0.7
        }.get(recipe.technique, 0.0)
        
        score += technique_bonus
        
        # Применяем настроение
        score *= self.mood_factor
        
        # Ограничиваем диапазон 1-5
        score = max(1.0, min(5.0, score))
        
        # Определяем реакцию
        if score >= 4.5:
            reaction = TasteReaction.LOVE
            comment = "Восхитительно! Идеальный баланс!"
        elif score >= 3.5:
            reaction = TasteReaction.LIKE
            comment = "Вкусно, но можно улучшить"
        elif score >= 2.5:
            reaction = TasteReaction.OK
            comment = "Нормально, ничего особенного"
        elif score >= 1.5:
            reaction = TasteReaction.DISLIKE
            comment = "Не очень, что-то не так"
        else:
            reaction = TasteReaction.HATE
            comment = "Ужасно! Нужно всё переделать"
        
        return TasterFeedback(
            taster_id=self.taster_id,
            reaction=reaction,
            score=int(round(score)),
            comment=comment,
            timestamp=asyncio.get_event_loop().time()
        )

# Примеры дегустаторов с разными предпочтениями
SAMPLE_TASTERS = [
    VirtualTaster("Мария_сладкоежка", {
        "сахар": 0.8, "мёд": 0.9, "шоколад": 1.0,
        "соль": -0.5, "перец": -0.3, "лук": -0.2
    }),
    
    VirtualTaster("Иван_мясоед", {
        "говядина": 1.0, "свинина": 0.8, "курица": 0.6,
        "овощи": -0.3, "салат": -0.5, "тофу": -0.8
    }),
    
    VirtualTaster("Анна_вегетарианка", {
        "овощи": 1.0, "зелень": 0.9, "орехи": 0.8,
        "мясо": -1.0, "рыба": -0.7, "сыр": 0.3
    }),
    
    VirtualTaster("Пётр_гурман", {
        "трюфели": 1.0, "икра": 0.9, "вино": 0.8,
        "фастфуд": -0.8, "консервы": -0.6, "полуфабрикаты": -0.9
    })
]

print("🔄 КОНЦЕПЦИЯ РЕАКТИВНОГО БЕНЧМАРКА ГОТОВА!")
print("📋 Основные компоненты:")
print("   - Recipe: структура рецепта")
print("   - VirtualTaster: дегустаторы с предпочтениями") 
print("   - TasterFeedback: мгновенная обратная связь")
print("   - CookingAttempt: попытка с результатами")
print("\n🎯 Готов к созданию адаптивного агента!") 