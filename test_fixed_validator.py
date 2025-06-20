#!/usr/bin/env python3
"""
🔍 ТЕСТ ИСПРАВЛЕННОГО ВАЛИДАТОРА

Проверяем что новый валидатор правильно штрафует за подделки
"""

import asyncio
import os
from pathlib import Path

# Импортируем исправленный валидатор
import sys
sys.path.append("kittycore/core")
from unified_orchestrator_fixed import FixedUnifiedOrchestrator

async def test_fixed_validator():
    print("🔍 ТЕСТ ИСПРАВЛЕННОГО ВАЛИДАТОРА")
    print("="*50)
    
    task = "Проведи анализ рынка приложений маркета битрикс 24"
    
    # Создаём исправленный оркестратор
    orchestrator = FixedUnifiedOrchestrator()
    
    # Файлы из нашего теста
    test_files = [
        "outputs/report.md",           # ПОДДЕЛКА
        "outputs/complexity.md",       # ПОДДЕЛКА  
        "outputs/top10_bitrix24_apps.json",  # ХОРОШИЙ
        "outputs/bitrix24_market_analysis.md"  # ХОРОШИЙ
    ]
    
    print(f"📁 Тестируем файлы: {len(test_files)}")
    for f in test_files:
        exists = "✅" if os.path.exists(f) else "❌"
        print(f"   {exists} {f}")
    
    # Запускаем валидацию
    expected_outcome = {"type": "analysis"}
    
    print(f"\n🔍 ЗАПУСК ВАЛИДАЦИИ...")
    
    try:
        result = await orchestrator._validate_file_contents(test_files, task, expected_outcome)
        
        print(f"\n📊 РЕЗУЛЬТАТЫ ВАЛИДАЦИИ:")
        print(f"   📈 Бонус: {result['score_bonus']:.3f}")
        print(f"   📁 Всего файлов: {result['total_files_count']}")
        print(f"   🚨 Подделок: {result['fake_files_count']}")
        print(f"   📊 Процент подделок: {result['fake_ratio']*100:.1f}%")
        
        print(f"\n✅ ДЕТАЛИ:")
        for detail in result['details']:
            print(f"   {detail}")
            
        print(f"\n❌ ПРОБЛЕМЫ:")
        for issue in result['issues']:
            print(f"   {issue}")
        
        # Проверяем что валидатор теперь даёт низкую оценку
        base_score = 0.7
        final_score = base_score + result['score_bonus']
        
        print(f"\n🎯 ФИНАЛЬНЫЙ СЧЁТ:")
        print(f"   🔹 Базовый: {base_score}")
        print(f"   🔹 Бонус: {result['score_bonus']:.3f}")
        print(f"   🔹 Итого: {final_score:.3f}")
        
        if final_score < 0.7:
            print(f"   ✅ ОТЛИЧНО! Валидатор теперь правильно штрафует: {final_score:.3f} < 0.7")
        else:
            print(f"   ❌ ПРОБЛЕМА! Валидатор всё ещё даёт высокую оценку: {final_score:.3f} >= 0.7")
            
        print(f"\n🔄 СРАВНЕНИЕ:")
        print(f"   📊 ДО ИСПРАВЛЕНИЯ: 0.85 (ЛОЖНЫЙ УСПЕХ)")
        print(f"   📊 ПОСЛЕ ИСПРАВЛЕНИЯ: {final_score:.2f} ({'ПРОВАЛ' if final_score < 0.7 else 'УСПЕХ'})")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_fixed_validator()) 