#!/usr/bin/env python3
"""
📊 Анализ динамики оценок в итеративном улучшении
"""

import re
import subprocess
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class ScoreChange:
    """Изменение оценки"""
    step: str
    initial_score: float
    final_score: float
    change: float
    attempts: int
    success: bool

def extract_scores_from_logs() -> List[ScoreChange]:
    """Извлекает изменения оценок из логов"""
    
    # Запускаем тест и получаем логи
    result = subprocess.run(
        ["python", "test_iterative_improvement.py"],
        capture_output=True,
        text=True
    )
    
    # Логи могут быть в stdout или stderr
    logs = result.stdout + result.stderr
    
    # Паттерны для поиска оценок
    validation_pattern = r"🔍 Валидация:.*?\(оценка: ([\d.]+)/1\.0\)"
    improvement_pattern = r"🔄 Попытка улучшения #(\d+) \(текущая оценка: ([\d.]+)\)"
    final_pattern = r"(📈 Улучшение|📉 Ухудшение): ([\d.]+) \(([+-][\d.]+)\)"
    
    # Находим все оценки
    validations = re.findall(validation_pattern, logs)
    improvements = re.findall(improvement_pattern, logs)
    finals = re.findall(final_pattern, logs)
    
    print("🔍 НАЙДЕННЫЕ ОЦЕНКИ:")
    print(f"Валидации: {len(validations)}")
    print(f"Попытки улучшения: {len(improvements)}")
    print(f"Финальные результаты: {len(finals)}")
    
    # Группируем по задачам
    changes = []
    
    # Простой анализ - берём каждую валидацию как начало цикла улучшения
    for i, validation_score in enumerate(validations):
        initial_score = float(validation_score)
        
        # Ищем соответствующие попытки улучшения
        task_improvements = []
        for attempt, current_score in improvements:
            if abs(float(current_score) - initial_score) < 0.1:  # Примерное совпадение
                task_improvements.append((int(attempt), float(current_score)))
        
        # Ищем финальный результат
        final_score = initial_score
        change = 0.0
        success = False
        
        if i < len(finals):
            final_type, final_val, change_val = finals[i]
            final_score = float(final_val)
            change = float(change_val)
            success = "Улучшение" in final_type
        
        changes.append(ScoreChange(
            step=f"Задача {i+1}",
            initial_score=initial_score,
            final_score=final_score,
            change=change,
            attempts=len(task_improvements),
            success=success
        ))
    
    return changes

def analyze_improvement_patterns(changes: List[ScoreChange]) -> Dict[str, any]:
    """Анализирует паттерны улучшения"""
    
    total_tasks = len(changes)
    successful_improvements = sum(1 for c in changes if c.success and c.change > 0)
    total_improvement = sum(c.change for c in changes if c.change > 0)
    total_degradation = sum(abs(c.change) for c in changes if c.change < 0)
    
    avg_initial_score = sum(c.initial_score for c in changes) / total_tasks if total_tasks > 0 else 0
    avg_final_score = sum(c.final_score for c in changes) / total_tasks if total_tasks > 0 else 0
    
    return {
        "total_tasks": total_tasks,
        "successful_improvements": successful_improvements,
        "success_rate": successful_improvements / total_tasks if total_tasks > 0 else 0,
        "total_improvement": total_improvement,
        "total_degradation": total_degradation,
        "net_improvement": total_improvement - total_degradation,
        "avg_initial_score": avg_initial_score,
        "avg_final_score": avg_final_score,
        "avg_improvement": avg_final_score - avg_initial_score
    }

def print_detailed_analysis():
    """Выводит детальный анализ"""
    
    print("📊 АНАЛИЗ ДИНАМИКИ ОЦЕНОК В ИТЕРАТИВНОМ УЛУЧШЕНИИ")
    print("=" * 60)
    
    changes = extract_scores_from_logs()
    
    if not changes:
        print("❌ Не удалось извлечь данные об оценках")
        return
    
    # Детальная таблица изменений
    print("\n📋 ДЕТАЛЬНАЯ ТАБЛИЦА ИЗМЕНЕНИЙ:")
    print("-" * 60)
    print(f"{'Задача':<12} {'Начальная':<10} {'Финальная':<10} {'Изменение':<12} {'Попытки':<8} {'Успех':<6}")
    print("-" * 60)
    
    for change in changes:
        success_icon = "✅" if change.success else "❌"
        change_str = f"{change.change:+.1f}" if change.change != 0 else "0.0"
        
        print(f"{change.step:<12} {change.initial_score:<10.1f} {change.final_score:<10.1f} "
              f"{change_str:<12} {change.attempts:<8} {success_icon:<6}")
    
    # Статистический анализ
    stats = analyze_improvement_patterns(changes)
    
    print(f"\n📈 СТАТИСТИЧЕСКИЙ АНАЛИЗ:")
    print("-" * 40)
    print(f"Всего задач: {stats['total_tasks']}")
    print(f"Успешных улучшений: {stats['successful_improvements']}")
    print(f"Процент успеха: {stats['success_rate']:.1%}")
    print(f"Общее улучшение: +{stats['total_improvement']:.1f}")
    print(f"Общее ухудшение: -{stats['total_degradation']:.1f}")
    print(f"Чистое улучшение: {stats['net_improvement']:+.1f}")
    print(f"Средняя начальная оценка: {stats['avg_initial_score']:.1f}")
    print(f"Средняя финальная оценка: {stats['avg_final_score']:.1f}")
    print(f"Среднее улучшение: {stats['avg_improvement']:+.1f}")
    
    # Выводы
    print(f"\n🎯 ВЫВОДЫ:")
    print("-" * 30)
    
    if stats['success_rate'] > 0.5:
        print("✅ Система итеративного улучшения работает эффективно")
    else:
        print("⚠️ Система требует доработки")
    
    if stats['avg_improvement'] > 0:
        print(f"✅ В среднем оценки улучшаются на {stats['avg_improvement']:.1f}")
    else:
        print(f"❌ В среднем оценки ухудшаются на {abs(stats['avg_improvement']):.1f}")
    
    if stats['net_improvement'] > 0:
        print(f"✅ Общий эффект положительный: +{stats['net_improvement']:.1f}")
    else:
        print(f"❌ Общий эффект отрицательный: {stats['net_improvement']:.1f}")

if __name__ == "__main__":
    print_detailed_analysis() 