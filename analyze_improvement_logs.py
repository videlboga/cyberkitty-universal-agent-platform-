#!/usr/bin/env python3
"""
📊 Анализ логов итеративного улучшения
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple

def analyze_improvement_logs():
    """Анализирует логи итеративного улучшения"""
    
    print("📊 АНАЛИЗ ЛОГОВ ИТЕРАТИВНОГО УЛУЧШЕНИЯ")
    print("=" * 50)
    
    # Ищем файлы логов
    log_files = [
        "logs/improvement.log",
        "logs/orchestrator.log", 
        "logs/agents.log",
        "logs/kittycore.log"
    ]
    
    found_logs = []
    for log_file in log_files:
        if Path(log_file).exists():
            found_logs.append(log_file)
            size = Path(log_file).stat().st_size
            print(f"✅ {log_file} - {size} байт")
        else:
            print(f"❌ {log_file} - не найден")
    
    if not found_logs:
        print("\n❌ Логи не найдены. Запустите тест итеративного улучшения:")
        print("python test_iterative_improvement.py")
        return
    
    # Анализируем каждый лог
    all_scores = []
    all_improvements = []
    
    for log_file in found_logs:
        print(f"\n🔍 АНАЛИЗ {log_file}:")
        print("-" * 30)
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем оценки валидации
            validation_pattern = r"Валидация:.*?оценка: ([\d.]+)/1\.0"
            validations = re.findall(validation_pattern, content)
            
            # Ищем попытки улучшения
            improvement_pattern = r"Попытка улучшения #(\d+).*?оценка: ([\d.]+)"
            improvements = re.findall(improvement_pattern, content)
            
            # Ищем итоговые результаты
            result_pattern = r"(Улучшение|Ухудшение): ([\d.]+) \(([+-][\d.]+)\)"
            results = re.findall(result_pattern, content)
            
            print(f"📋 Найдено валидаций: {len(validations)}")
            print(f"🔄 Найдено попыток улучшения: {len(improvements)}")
            print(f"📈 Найдено результатов: {len(results)}")
            
            if validations:
                scores = [float(v) for v in validations]
                all_scores.extend(scores)
                print(f"📊 Оценки: {scores}")
                print(f"📊 Средняя оценка: {sum(scores)/len(scores):.2f}")
            
            if results:
                for result_type, final_score, change in results:
                    change_val = float(change)
                    all_improvements.append(change_val)
                    icon = "📈" if change_val > 0 else "📉"
                    print(f"{icon} {result_type}: {final_score} ({change})")
        
        except Exception as e:
            print(f"❌ Ошибка чтения {log_file}: {e}")
    
    # Общая статистика
    if all_scores or all_improvements:
        print(f"\n🎯 ОБЩАЯ СТАТИСТИКА:")
        print("-" * 30)
        
        if all_scores:
            print(f"📊 Всего оценок: {len(all_scores)}")
            print(f"📊 Средняя оценка: {sum(all_scores)/len(all_scores):.2f}")
            print(f"📊 Минимальная: {min(all_scores):.2f}")
            print(f"📊 Максимальная: {max(all_scores):.2f}")
        
        if all_improvements:
            positive = [x for x in all_improvements if x > 0]
            negative = [x for x in all_improvements if x < 0]
            
            print(f"📈 Улучшений: {len(positive)}")
            print(f"📉 Ухудшений: {len(negative)}")
            
            if positive:
                print(f"📈 Среднее улучшение: +{sum(positive)/len(positive):.2f}")
            if negative:
                print(f"📉 Среднее ухудшение: {sum(negative)/len(negative):.2f}")
            
            total_change = sum(all_improvements)
            print(f"🎯 Общий эффект: {total_change:+.2f}")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    print("-" * 20)
    
    if all_scores:
        avg_score = sum(all_scores) / len(all_scores)
        if avg_score < 0.5:
            print("⚠️ Низкие оценки - нужно улучшить качество агентов")
        elif avg_score < 0.7:
            print("🔄 Средние оценки - система работает, но есть потенциал")
        else:
            print("✅ Высокие оценки - система работает отлично")
    
    if all_improvements:
        positive_rate = len([x for x in all_improvements if x > 0]) / len(all_improvements)
        if positive_rate > 0.6:
            print("✅ Итеративное улучшение эффективно")
        else:
            print("⚠️ Итеративное улучшение требует доработки")

if __name__ == "__main__":
    analyze_improvement_logs() 