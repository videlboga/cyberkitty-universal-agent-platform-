#!/usr/bin/env python3
"""
🔍 ОТЛАДКА ВАЛИДАТОРА - ПОЧЕМУ НЕ РАБОТАЕТ

Проверяем работу детектора поддельных отчётов на наших файлах
"""

import os
from pathlib import Path

def detect_fake_reports(content: str, file_path: str, task: str) -> dict:
    """Копия детектора из UnifiedOrchestrator"""
    
    # Паттерны отчётов-подделок
    fake_patterns = [
        'Результат выполнения задачи',
        'Задача обработана', 
        'Генерировано KittyCore',
        'Создан файл с результатом',
        'Отчёт о выполнении',
        'Анализ задачи',
        'Время создания:',
        '<div class="header">',
        '<div class="content">',
        '<div class="footer">',
        'Генерировано KittyCore 3.0 🐱',
        'TODO: Реализовать логику',
        'Задача успешно обработана',
        'с использованием LLM-интеллекта',
        'интеллектуальным агентом',
        'Контент для:',
        'Описание: Создан файл',
        'Выполнено интеллектуальным агентом',
        # Новые паттерны
        'первое приложение',
        'второе приложение', 
        'третье приложение'
    ]
    
    # Проверяем наличие паттернов подделок
    fake_indicators_found = []
    for pattern in fake_patterns:
        if pattern in content:
            fake_indicators_found.append(pattern)
    
    # Если найдено много индикаторов подделки
    if len(fake_indicators_found) >= 2:
        return {
            'is_fake': True,
            'reason': f'обнаружены паттерны отчёта: {", ".join(fake_indicators_found[:2])}'
        }
    
    return {'is_fake': False, 'reason': 'содержимое выглядит аутентично'}

def check_content_by_extension(file_path: str, content: str, file_ext: str, task: str) -> dict:
    """Копия проверки содержимого из UnifiedOrchestrator"""
    
    if file_ext == '.md':
        # Для MD файлов - проверяем что это не HTML в .md
        if '<html>' in content.lower() or '<!doctype' in content.lower():
            return {'is_valid': False, 'bonus': 0, 'reason': 'HTML код в MD файле'}
        else:
            return {'is_valid': True, 'bonus': 0.05, 'reason': 'текстовое содержимое'}
    
    elif file_ext == '.json':
        # Для JSON файлов
        try:
            import json
            json.loads(content)
            return {'is_valid': True, 'bonus': 0.1, 'reason': 'валидный JSON'}
        except:
            return {'is_valid': False, 'bonus': 0, 'reason': 'не является валидным JSON'}
    
    else:
        # Для других расширений - базовая проверка
        return {'is_valid': True, 'bonus': 0.02, 'reason': 'файл создан'}

def debug_validator():
    print("🔍 ОТЛАДКА ВАЛИДАТОРА")
    print("="*50)
    
    task = "Проведи анализ рынка приложений маркета битрикс 24"
    
    # Проверяем файлы из нашего теста
    test_files = [
        "outputs/report.md",
        "outputs/complexity.md", 
        "outputs/top10_bitrix24_apps.json",
        "outputs/bitrix24_market_analysis.md"
    ]
    
    total_score = 0
    total_files = 0
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"❌ {file_path} - файл не найден")
            continue
            
        print(f"\n📄 {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Показываем первые 100 символов
            print(f"   📝 Контент: {content[:100]}...")
            
            # Проверяем расширение
            file_ext = os.path.splitext(file_path)[1].lower()
            content_check = check_content_by_extension(file_path, content, file_ext, task)
            
            print(f"   ✅ Проверка расширения: {content_check}")
            
            # Проверяем на подделки
            fake_check = detect_fake_reports(content, file_path, task)
            print(f"   🔍 Детектор подделок: {fake_check}")
            
            # Считаем общий бонус
            if content_check['is_valid'] and not fake_check['is_fake']:
                score = content_check['bonus']
                total_score += score
                print(f"   📊 Бонус: +{score}")
            else:
                print(f"   ❌ Проблемы найдены!")
                
            total_files += 1
            
        except Exception as e:
            print(f"   ❌ Ошибка чтения: {e}")
    
    print(f"\n🏆 ИТОГ:")
    print(f"   📊 Общий бонус: {total_score:.3f}")
    print(f"   📁 Файлов проверено: {total_files}")
    print(f"   📈 Средний бонус: {total_score/total_files if total_files > 0 else 0:.3f}")
    
    # Проверим почему валидатор считает что всё ОК
    base_score = 0.7  # Базовая оценка
    final_score = min(base_score + total_score, 1.0)
    print(f"   🎯 Финальный счёт: {base_score} + {total_score} = {final_score}")
    
    if final_score >= 0.7:
        print(f"   ✅ ПРОБЛЕМА НАЙДЕНА: валидатор считает {final_score:.2f} >= 0.7 = УСПЕХ!")
    else:
        print(f"   ❌ Валидатор считает {final_score:.2f} < 0.7 = ПРОВАЛ")

if __name__ == "__main__":
    debug_validator() 