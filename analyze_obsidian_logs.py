#!/usr/bin/env python3
"""
📊 Анализ логов итеративного улучшения из Obsidian vault
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple

def analyze_obsidian_logs():
    """Анализирует логи итеративного улучшения из Obsidian vault"""
    
    print("📊 АНАЛИЗ ЛОГОВ ИЗ OBSIDIAN VAULT")
    print("=" * 50)
    
    # Ищем файлы логов в Obsidian vault
    vault_path = Path("./obsidian_vault")
    logs_folder = vault_path / "system" / "logs"
    
    if not logs_folder.exists():
        print(f"❌ Папка логов не найдена: {logs_folder}")
        print("Запустите тест итеративного улучшения:")
        print("python test_iterative_improvement.py")
        return
    
    log_files = [
        "🔄 Iterative Improvement Logs.md",
        "🧭 Orchestrator Logs.md", 
        "🤖 Agents Logs.md",
        "⚙️ System Logs.md",
        "❌ Error Logs.md"
    ]
    
    found_logs = []
    for log_file in log_files:
        log_path = logs_folder / log_file
        if log_path.exists():
            found_logs.append(log_path)
            size = log_path.stat().st_size
            print(f"✅ {log_file} - {size} байт")
        else:
            print(f"❌ {log_file} - не найден")
    
    if not found_logs:
        print("\n❌ Логи не найдены в Obsidian vault")
        return
    
    # Анализируем каждый лог
    all_scores = []
    all_improvements = []
    improvement_details = []
    
    for log_file in found_logs:
        print(f"\n🔍 АНАЛИЗ {log_file.name}:")
        print("-" * 40)
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем оценки валидации в markdown логах
            validation_pattern = r"Валидация:.*?оценка: ([\d.]+)/1\.0"
            validations = re.findall(validation_pattern, content)
            
            # Ищем попытки улучшения
            improvement_pattern = r"Попытка улучшения #(\d+).*?оценка: ([\d.]+)"
            improvements = re.findall(improvement_pattern, content)
            
            # Ищем итоговые результаты
            result_pattern = r"(Улучшение|Ухудшение): ([\d.]+) \(([+-][\d.]+)\)"
            results = re.findall(result_pattern, content)
            
            # Ищем детали фидбека
            feedback_pattern = r"🧠 LLM фидбек: (\d+) рекомендаций, (\d+) примеров"
            feedback_details = re.findall(feedback_pattern, content)
            
            # Ищем созданные файлы
            files_pattern = r"Создан файл: ([^\n]+)"
            created_files = re.findall(files_pattern, content)
            
            print(f"📋 Найдено валидаций: {len(validations)}")
            print(f"🔄 Найдено попыток улучшения: {len(improvements)}")
            print(f"📈 Найдено результатов: {len(results)}")
            print(f"🧠 Найдено фидбека: {len(feedback_details)}")
            print(f"📁 Создано файлов: {len(created_files)}")
            
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
                    
                    improvement_details.append({
                        "type": result_type,
                        "final_score": float(final_score),
                        "change": change_val,
                        "file": log_file.name
                    })
            
            if feedback_details:
                for recommendations, examples in feedback_details:
                    print(f"🧠 Фидбек: {recommendations} рекомендаций, {examples} примеров")
            
            if created_files:
                print(f"📁 Созданные файлы:")
                for file in created_files[:5]:  # Показываем первые 5
                    print(f"   - {file}")
                if len(created_files) > 5:
                    print(f"   ... и ещё {len(created_files) - 5}")
        
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
    
    # Детальный анализ улучшений
    if improvement_details:
        print(f"\n📈 ДЕТАЛЬНЫЙ АНАЛИЗ УЛУЧШЕНИЙ:")
        print("-" * 35)
        
        for i, detail in enumerate(improvement_details, 1):
            icon = "📈" if detail["change"] > 0 else "📉"
            print(f"{i}. {icon} {detail['type']}: {detail['final_score']:.2f} ({detail['change']:+.2f})")
            print(f"   Источник: {detail['file']}")
    
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
    
    print(f"\n🗄️ Логи сохранены в Obsidian vault: {logs_folder}")
    print("📖 Откройте Obsidian для детального просмотра логов")

if __name__ == "__main__":
    analyze_obsidian_logs() 