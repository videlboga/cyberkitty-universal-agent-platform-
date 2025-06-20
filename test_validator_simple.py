#!/usr/bin/env python3
"""
🔍 ПРОСТОЙ ТЕСТ ИСПРАВЛЕННОГО ВАЛИДАТОРА

Проверяем логику штрафов без сложных импортов
"""

import os

def detect_fake_reports_simple(content: str, file_path: str, task: str) -> dict:
    """Простая копия детектора подделок"""
    fake_patterns = [
        'Задача успешно обработана',
        'с использованием LLM-интеллекта',
        'интеллектуальным агентом',
        'Результат выполнения задачи',
        'Задача обработана'
    ]
    
    fake_indicators_found = []
    for pattern in fake_patterns:
        if pattern in content:
            fake_indicators_found.append(pattern)
    
    if len(fake_indicators_found) >= 2:
        return {
            'is_fake': True,
            'reason': f'обнаружены паттерны отчёта: {", ".join(fake_indicators_found[:2])}'
        }
    
    return {'is_fake': False, 'reason': 'содержимое выглядит аутентично'}

def test_validator_logic():
    """Тестируем новую логику валидатора"""
    print("🔍 ТЕСТ ЛОГИКИ ИСПРАВЛЕННОГО ВАЛИДАТОРА")
    print("="*50)
    
    # Симулируем 4 файла из нашего теста
    files_data = [
        {
            "path": "outputs/report.md",
            "content": "# Результат работы\n\nЗадача: Проведи анализ рынка приложений маркета битрикс 24\n\nЗадача успешно обработана с использованием LLM-интеллекта",
            "ext": ".md"
        },
        {
            "path": "outputs/complexity.md", 
            "content": "# Результат работы\n\nЗадача: Проведи анализ рынка приложений маркета битрикс 24\n\nЗадача успешно обработана с использованием LLM-интеллекта",
            "ext": ".md"
        },
        {
            "path": "outputs/top10_bitrix24_apps.json",
            "content": '[{"name": "Битрикс24.CRM", "category": "Управление клиентами", "price": "990 руб/мес"}]',
            "ext": ".json"
        },
        {
            "path": "outputs/bitrix24_market_analysis.md",
            "content": "# Анализ рынка приложений маркета Битрикс24\n## Битрикс24.CRM (4.2★, 990₽/мес) - лидер сегмента управления клиентами",
            "ext": ".md"
        }
    ]
    
    task = "Проведи анализ рынка приложений маркета битрикс 24"
    
    # НОВАЯ ЛОГИКА ВАЛИДАТОРА
    score_bonus = 0.0
    fake_files_count = 0
    total_files_count = len(files_data)
    
    print(f"📁 Анализируем {total_files_count} файлов:")
    
    for file_data in files_data:
        file_path = file_data["path"] 
        content = file_data["content"]
        file_ext = file_data["ext"]
        
        print(f"\n📄 {file_path}")
        print(f"   📝 Контент: {content[:60]}...")
        
        # СНАЧАЛА проверяем на подделки - ЭТО ПРИОРИТЕТ!
        fake_check = detect_fake_reports_simple(content, file_path, task)
        
        if fake_check['is_fake']:
            fake_files_count += 1
            print(f"   🚨 ПОДДЕЛКА: {fake_check['reason']}")
            # ЖЁСТКИЙ ШТРАФ за подделку
            score_bonus -= 0.25  # Каждая подделка = -25%
            print(f"   💸 Штраф: -0.25 (итого: {score_bonus:.3f})")
            continue  # Не даём бонусы за поддельные файлы!
        
        # Если НЕ подделка - даём бонусы
        if file_ext == ".json":
            score_bonus += 0.1
            print(f"   ✅ Валидный JSON: +0.1 (итого: {score_bonus:.3f})")
        elif file_ext == ".md":
            score_bonus += 0.05
            print(f"   ✅ Текстовое содержимое: +0.05 (итого: {score_bonus:.3f})")
        
        print(f"   ✅ Содержимое аутентично")
    
    # КРИТИЧЕСКАЯ ЛОГИКА: проверяем процент подделок
    fake_ratio = fake_files_count / total_files_count
    
    print(f"\n📊 АНАЛИЗ ПОДДЕЛОК:")
    print(f"   🚨 Подделок: {fake_files_count}/{total_files_count} = {fake_ratio*100:.1f}%")
    
    if fake_ratio >= 0.5:  # 50%+ подделок = критический провал
        score_bonus = -0.5
        print(f"   🚨 КРИТИЧЕСКИЙ ПРОВАЛ: {fake_ratio*100:.1f}% подделок! Штраф: -0.5")
    elif fake_ratio >= 0.3:  # 30%+ подделок = серьёзные проблемы
        score_bonus -= 0.2
        print(f"   ⚠️ СЕРЬЁЗНЫЕ ПРОБЛЕМЫ: {fake_ratio*100:.1f}% подделок! Доп.штраф: -0.2")
    elif fake_ratio > 0:
        print(f"   ⚠️ НАЙДЕНЫ ПОДДЕЛКИ: {fake_ratio*100:.1f}%")
    
    print(f"\n🎯 ФИНАЛЬНЫЙ РЕЗУЛЬТАТ:")
    print(f"   📊 Финальный бонус: {score_bonus:.3f}")
    
    base_score = 0.7
    final_score = base_score + score_bonus
    print(f"   🔹 Базовый балл: {base_score}")
    print(f"   🔹 Итоговый балл: {final_score:.3f}")
    
    print(f"\n🔄 СРАВНЕНИЕ:")
    print(f"   📊 ДО ИСПРАВЛЕНИЯ: 0.85 (ЛОЖНЫЙ УСПЕХ)")
    print(f"   📊 ПОСЛЕ ИСПРАВЛЕНИЯ: {final_score:.2f}")
    
    if final_score < 0.7:
        print(f"   ✅ УСПЕХ! Валидатор теперь правильно ШТРАФУЕТ: {final_score:.2f} < 0.7")
        print(f"   🎯 Задача будет помечена как ПРОВАЛ и отправлена на доработку")
    else:
        print(f"   ❌ ПРОБЛЕМА! Валидатор всё ещё пропускает: {final_score:.2f} >= 0.7")

if __name__ == "__main__":
    test_validator_logic() 