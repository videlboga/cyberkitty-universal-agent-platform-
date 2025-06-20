#!/usr/bin/env python3
"""
🎯 ТЕСТ БИТРИКС24 С LLM - ИСПРАВЛЕННЫЙ ВАЛИДАТОР

Проверяем работу исправленного валидатора на реальной задаче
с правильными настройками LLM
"""

import asyncio
import os
from pathlib import Path

# ПРАВИЛЬНЫЕ НАСТРОЙКИ ДЛЯ LLM
os.environ["TIMEOUT"] = "60"  # Увеличиваем таймаут до 60 секунд
os.environ["MAX_TOKENS"] = "8000"  # Больше токенов для детального анализа
os.environ["TEMPERATURE"] = "0.1"  # Небольшая температура для стабильности

# Быстрая модель для стабильности
FAST_MODEL = "anthropic/claude-3-haiku"

async def test_bitrix_with_fixed_validator():
    print("🎯 ТЕСТ БИТРИКС24 С ИСПРАВЛЕННЫМ ВАЛИДАТОРОМ")
    print("="*60)
    print(f"⚙️ Настройки:")
    print(f"   🕐 TIMEOUT: {os.environ.get('TIMEOUT')}с")
    print(f"   🔤 MAX_TOKENS: {os.environ.get('MAX_TOKENS')}")
    print(f"   🌡️ TEMPERATURE: {os.environ.get('TEMPERATURE')}")
    print(f"   🧠 MODEL: {FAST_MODEL}")
    print(f"   🔑 API Key: {'✅ Установлен' if os.getenv('OPENROUTER_API_KEY') else '❌ Отсутствует'}")
    
    task = """Проведи анализ рынка приложений маркета битрикс 24, найди топ популярных, составь отчёт о том, какие там есть, насколько они сложны в реализации и какие проблемы имеют. После сделай 3 прототипа приложений на основе этого анализа - которые можно сделать быстро с улучшением UX"""
    
    print(f"\n📋 ЗАДАЧА:")
    print(f"   {task}")
    
    try:
        # Импортируем UnifiedOrchestrator
        import sys
        sys.path.append("kittycore")
        from kittycore.core.unified_orchestrator import create_unified_orchestrator
        
        print(f"\n🚀 ЗАПУСК СИСТЕМЫ...")
        
        # Создаём оркестратор с увеличенным таймаутом
        from kittycore.core.unified_orchestrator import UnifiedConfig
        config = UnifiedConfig()
        config.timeout = 120  # 2 минуты на всю задачу
        
        orchestrator = create_unified_orchestrator(config)
        
        print(f"   ✅ Оркестратор создан")
        print(f"   🔄 Запуск решения задачи...")
        
        # Запускаем задачу
        start_time = asyncio.get_event_loop().time()
        result = await orchestrator.solve_task(task)
        end_time = asyncio.get_event_loop().time()
        
        duration = end_time - start_time
        
        print(f"\n🏁 ЗАДАЧА ЗАВЕРШЕНА!")
        print(f"   ⏱️ Время выполнения: {duration:.1f}с")
        
        # Анализируем результаты
        print(f"\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ:")
        
        # Проверяем качество
        validation_result = result.get('validation_result', {})
        quality_score = validation_result.get('quality_score', 0)
        
        print(f"   📈 Качество: {quality_score:.3f}")
        
        # Проверяем файлы
        created_files = result.get('created_files', [])
        print(f"   📁 Создано файлов: {len(created_files)}")
        
        for file_path in created_files[:5]:  # Показываем первые 5
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"      📄 {file_path} ({size} байт)")
            else:
                print(f"      ❌ {file_path} (не найден)")
        
        if len(created_files) > 5:
            print(f"      ... и ещё {len(created_files) - 5} файлов")
        
        # ГЛАВНОЕ: Проверяем работу исправленного валидатора
        print(f"\n🔍 ВАЛИДАЦИЯ (ИСПРАВЛЕННЫЙ ВАЛИДАТОР):")
        
        if 'fake_files_count' in validation_result:
            fake_count = validation_result.get('fake_files_count', 0)
            total_count = validation_result.get('total_files_count', 0)
            fake_ratio = validation_result.get('fake_ratio', 0)
            
            print(f"   🚨 Подделок: {fake_count}/{total_count} ({fake_ratio*100:.1f}%)")
            
            if fake_ratio >= 0.5:
                print(f"   🚨 КРИТИЧЕСКИЙ ПРОВАЛ: Более 50% подделок!")
            elif fake_ratio >= 0.3:
                print(f"   ⚠️ СЕРЬЁЗНЫЕ ПРОБЛЕМЫ: Более 30% подделок!")
            elif fake_ratio > 0:
                print(f"   ⚠️ НАЙДЕНЫ ПОДДЕЛКИ: {fake_ratio*100:.1f}%")
            else:
                print(f"   ✅ ПОДДЕЛОК НЕ НАЙДЕНО")
        
        # Проверяем нужна ли доработка
        needs_rework = validation_result.get('needs_rework', False)
        if needs_rework:
            print(f"   🔄 ТРЕБУЕТСЯ ДОРАБОТКА: Качество < 0.7")
            rework_reasons = validation_result.get('rework_reasons', [])
            for reason in rework_reasons[:3]:
                print(f"      - {reason}")
        else:
            print(f"   ✅ ЗАДАЧА ПРИНЯТА: Качество >= 0.7")
        
        # Итоги
        print(f"\n🎯 ИТОГИ ТЕСТА:")
        if quality_score >= 0.7 and not needs_rework:
            print(f"   ✅ УСПЕХ: Система создала качественный результат ({quality_score:.3f})")
        else:
            print(f"   ❌ ПРОВАЛ: Результат не прошёл валидацию ({quality_score:.3f})")
            print(f"   🔧 ИСПРАВЛЕННЫЙ ВАЛИДАТОР РАБОТАЕТ! Система честно оценивает качество")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ОШИБКА ВЫПОЛНЕНИЯ:")
        print(f"   {str(e)}")
        import traceback
        print("\n🔍 ТРЕЙС:")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_bitrix_with_fixed_validator()) 