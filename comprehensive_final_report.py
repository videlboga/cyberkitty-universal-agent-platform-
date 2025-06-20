#!/usr/bin/env python3
"""
📊 ФИНАЛЬНЫЙ ОТЧЁТ COMPREHENSIVE ТЕСТИРОВАНИЯ KITTYCORE 3.0
"""

import json
import glob
from pathlib import Path

def load_results():
    """📂 Загрузка результатов всех частей тестирования"""
    results = {
        'part1': None,
        'part2': None, 
        'part3': None
    }
    
    # Ищем файлы результатов
    part1_files = glob.glob("comprehensive_part1_results_*.json")
    part2_files = glob.glob("comprehensive_part2_results_*.json")
    part3_files = glob.glob("comprehensive_part3_results_*.json")
    
    if part1_files:
        with open(part1_files[-1], 'r', encoding='utf-8') as f:
            results['part1'] = json.load(f)
            print(f"✅ Загружен {part1_files[-1]}")
    
    if part2_files:
        with open(part2_files[-1], 'r', encoding='utf-8') as f:
            results['part2'] = json.load(f)
            print(f"✅ Загружен {part2_files[-1]}")
    
    if part3_files:
        with open(part3_files[-1], 'r', encoding='utf-8') as f:
            results['part3'] = json.load(f)
            print(f"✅ Загружен {part3_files[-1]}")
    
    return results

def generate_comprehensive_report(results):
    """📊 Генерация comprehensive отчёта"""
    
    # Собираем статистику
    total_tools = 0
    successful_tools = 0
    honest_tools = set()
    dishonest_tools = set()
    all_results = []
    total_time = 0
    
    for part_name, part_data in results.items():
        if part_data:
            total_tools += len(part_data['results'])
            successful_tools += len([r for r in part_data['results'] if r['success']])
            honest_tools.update(part_data['honest_tools'])
            dishonest_tools.update(part_data['dishonest_tools'])
            all_results.extend(part_data['results'])
            total_time += part_data['total_time']
    
    # Детальная статистика по частям
    part_stats = {}
    for part_name, part_data in results.items():
        if part_data:
            part_stats[part_name] = {
                'total': len(part_data['results']),
                'successful': len([r for r in part_data['results'] if r['success']]),
                'honest': len(part_data['honest_tools']),
                'time': part_data['total_time']
            }
    
    # Формируем отчёт
    report = f"""
🎯 COMPREHENSIVE ТЕСТИРОВАНИЕ KITTYCORE 3.0 - ФИНАЛЬНЫЙ ОТЧЁТ
{'='*80}

📋 ОБЩАЯ СТАТИСТИКА:
--------------------
🔧 Всего протестировано инструментов: {total_tools}
✅ Успешно запущено: {successful_tools} ({(successful_tools/total_tools*100):.1f}%)
🛡️ Честно работают: {len(honest_tools)} ({(len(honest_tools)/total_tools*100):.1f}%)
❌ Проблемные: {len(dishonest_tools)} ({(len(dishonest_tools)/total_tools*100):.1f}%)
⏱️ Общее время тестирования: {total_time:.1f}с

📊 СТАТИСТИКА ПО ЧАСТЯМ:
------------------------"""
    
    for part_name, stats in part_stats.items():
        if stats:
            success_rate = (stats['successful']/stats['total']*100) if stats['total'] > 0 else 0
            honesty_rate = (stats['honest']/stats['total']*100) if stats['total'] > 0 else 0
            part_title = {
                'part1': 'ЧАСТЬ 1 (БАЗОВЫЕ)',
                'part2': 'ЧАСТЬ 2 (ВЕБ)', 
                'part3': 'ЧАСТЬ 3 (ОСТАЛЬНЫЕ)'
            }.get(part_name, part_name.upper())
            
            report += f"""
{part_title}:
  🔧 Инструментов: {stats['total']}
  ✅ Успешно: {stats['successful']} ({success_rate:.1f}%)
  🛡️ Честно: {stats['honest']} ({honesty_rate:.1f}%)
  ⏱️ Время: {stats['time']:.1f}с"""
    
    report += f"""

🛡️ ЧЕСТНЫЕ ИНСТРУМЕНТЫ ({len(honest_tools)}):
{'-'*50}
{', '.join(sorted(honest_tools)) if honest_tools else 'НЕТ'}

❌ ПРОБЛЕМНЫЕ ИНСТРУМЕНТЫ ({len(dishonest_tools)}):
{'-'*50}
{', '.join(sorted(dishonest_tools)) if dishonest_tools else 'НЕТ'}

📈 ДЕТАЛЬНАЯ СТАТИСТИКА:
------------------------"""
    
    # Группируем по категориям
    categories = {
        'Базовые инструменты': ['media_tool', 'super_system_tool', 'network_tool'],
        'Веб-инструменты': ['enhanced_web_search', 'api_request', 'enhanced_web_scraping'],
        'Остальные инструменты': ['code_execution', 'security_tool', 'email_tool', 'data_analysis']
    }
    
    for category, tools in categories.items():
        honest_in_category = [t for t in tools if t in honest_tools]
        dishonest_in_category = [t for t in tools if t in dishonest_tools]
        
        report += f"""
{category}:
  ✅ Честные: {len(honest_in_category)}/{len(tools)} - {', '.join(honest_in_category) if honest_in_category else 'НЕТ'}
  ❌ Проблемные: {len(dishonest_in_category)}/{len(tools)} - {', '.join(dishonest_in_category) if dishonest_in_category else 'НЕТ'}"""
    
    # Рекомендации
    honesty_percentage = (len(honest_tools)/total_tools*100) if total_tools > 0 else 0
    
    report += f"""

🎯 ОЦЕНКА И РЕКОМЕНДАЦИИ:
-------------------------"""
    
    if honesty_percentage >= 70:
        report += f"""
🎉 ОТЛИЧНО! {honesty_percentage:.1f}% инструментов работают честно!
✨ KittyCore 3.0 показывает высокое качество инструментов
🚀 Система готова к продакшену с минимальными доработками"""
    elif honesty_percentage >= 50:
        report += f"""
👍 ХОРОШО! {honesty_percentage:.1f}% инструментов работают честно
🔧 Есть потенциал для улучшения проблемных инструментов
📈 Система на правильном пути развития"""
    else:
        report += f"""
⚠️ ТРЕБУЕТСЯ ДОРАБОТКА! Только {honesty_percentage:.1f}% инструментов честные
🛠️ Необходимо исправить проблемные инструменты
🔍 Рекомендуется детальный анализ каждого инструмента"""
    
    report += f"""

🔧 ПРИОРИТЕТЫ ИСПРАВЛЕНИЯ:
--------------------------
1. Исправить async/sync проблемы (network_tool, security_tool)
2. Добавить недостающие модули (code_execution_tool, email_tool)
3. Улучшить параметры веб-инструментов (enhanced_web_search)
4. Протестировать data_analysis_tool с правильными параметрами

💡 ПРИНЦИП ПОДТВЕРЖДЁН:
-----------------------
"Честное тестирование выявляет реальные проблемы!"
Система честности работает - фиктивные результаты обнаружены и отклонены.

🎯 ИТОГ: KittyCore 3.0 имеет {len(honest_tools)} из {total_tools} честно работающих инструментов!
"""
    
    return report

def main():
    """Главная функция генерации финального отчёта"""
    print("📊 ГЕНЕРАЦИЯ ФИНАЛЬНОГО ОТЧЁТА COMPREHENSIVE ТЕСТИРОВАНИЯ")
    print("=" * 70)
    
    # Загружаем результаты
    results = load_results()
    
    # Генерируем отчёт
    report = generate_comprehensive_report(results)
    
    # Выводим отчёт
    print(report)
    
    # Сохраняем отчёт
    report_file = "COMPREHENSIVE_FINAL_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 Финальный отчёт сохранён в {report_file}")
    
    # Сохраняем также JSON со всеми данными
    json_file = "comprehensive_final_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Данные сохранены в {json_file}")

if __name__ == "__main__":
    main() 