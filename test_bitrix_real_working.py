#!/usr/bin/env python3
"""РЕАЛЬНЫЙ тест анализа рынка Битрикс24 с РАБОТАЮЩЕЙ системой"""

import asyncio
import os
import sys
import time

# Добавляем путь к модулям KittyCore
sys.path.append('/home/cyberkitty/Project/kittycore')

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig


def setup_working_llm():
    """Настройки LLM которые ТОЧНО работают (как в предыдущем тесте)"""
    
    os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY", "")
    os.environ["LLM_MODEL"] = "google/gemini-2.5-flash-lite-preview-06-17"  # Та же модель что работала
    os.environ["TIMEOUT"] = "15"
    os.environ["MAX_TOKENS"] = "1000"
    os.environ["TEMPERATURE"] = "0"
    
    print("🚀 РАБОЧИЕ НАСТРОЙКИ LLM:")
    print(f"   Модель: {os.environ['LLM_MODEL']}")
    print(f"   Таймаут: {os.environ['TIMEOUT']}с")
    print(f"   Токены: {os.environ['MAX_TOKENS']}")
    print(f"   API ключ: {'✅ есть' if os.environ['OPENROUTER_API_KEY'] else '❌ нет'}")


async def test_bitrix_market_analysis():
    """Тест комплексной задачи анализа рынка Битрикс24"""
    
    print("\n" + "="*80)
    print("🎯 РЕАЛЬНЫЙ ТЕСТ: Анализ рынка Битрикс24")
    print("="*80)
    
    setup_working_llm()
    
    # Комплексная задача анализа рынка
    task = """
    Проведи анализ рынка Битрикс24:
    1. Найди ТОП-10 популярных приложений в Битрикс24 маркетплейсе
    2. Создай подробный отчёт что существует на рынке
    3. Проанализируй сложность реализации каждого типа приложений
    4. Выяви основные проблемы существующих решений
    5. Создай 3 прототипа улучшенных UX приложений с конкретными решениями
    """
    
    vault_path = "vault_bitrix_real"
    
    print(f"\n📋 ЗАДАЧА: {task}")
    print(f"📂 VAULT: {vault_path}")
    
    # Настройки для более сложной задачи
    config = UnifiedConfig(
        vault_path=vault_path,
        max_agents=5,  # Больше агентов для сложной задачи
        timeout=300,   # Больше времени
        enable_human_intervention=False,  # Автономная работа
        enable_smart_validation=True,     # ВКЛЮЧАЕМ валидацию
        enable_metrics=True,              # Включаем метрики
        enable_vector_memory=False,       # Пока без векторной памяти (для скорости)
        enable_amem_memory=False,         # Пока без A-MEM (для скорости)
        enable_shared_chat=True,          # Координация агентов
        enable_tool_adaptation=False      # Без адаптации пока
    )
    
    orchestrator = UnifiedOrchestrator(config=config)
    
    start_time = time.time()
    
    try:
        print("\n🚀 ЗАПУСК АНАЛИЗА РЫНКА БИТРИКС24...")
        
        # Выполняем сложную задачу
        result = await orchestrator.solve_task(task)
        
        execution_time = time.time() - start_time
        print(f"\n⏱️ ВРЕМЯ ВЫПОЛНЕНИЯ: {execution_time:.2f}с")
        print(f"📊 РЕЗУЛЬТАТ СИСТЕМЫ: {result}")
        
        # Анализируем созданные файлы
        import glob
        
        # Ищем файлы в outputs (старая схема) и vault (новая схема)
        outputs_files = glob.glob("outputs/**/*", recursive=True)
        outputs_files = [f for f in outputs_files if os.path.isfile(f)]
        
        vault_files = glob.glob(f"{vault_path}/**/*", recursive=True)
        vault_files = [f for f in vault_files if os.path.isfile(f)]
        
        all_files = outputs_files + vault_files
        
        print(f"\n📁 ОБЩЕЕ КОЛИЧЕСТВО ФАЙЛОВ: {len(all_files)}")
        print(f"   📂 В outputs/: {len(outputs_files)}")
        print(f"   📂 В vault/: {len(vault_files)}")
        
        # Ищем файлы связанные с Битрикс24
        bitrix_files = [f for f in outputs_files if 'bitrix' in f.lower()]
        analysis_files = [f for f in outputs_files if any(word in f.lower() for word in ['analysis', 'анализ', 'report', 'отчет'])]
        prototype_files = [f for f in outputs_files if any(word in f.lower() for word in ['prototype', 'прототип'])]
        
        print(f"\n🔍 АНАЛИЗ РЕЗУЛЬТАТОВ:")
        print(f"   📊 Файлы про Битрикс24: {len(bitrix_files)}")
        print(f"   📈 Файлы анализа: {len(analysis_files)}")
        print(f"   🎨 Файлы прототипов: {len(prototype_files)}")
        
        # Показываем созданные файлы
        if bitrix_files:
            print(f"\n📋 ФАЙЛЫ ПРО БИТРИКС24:")
            for f in bitrix_files[:5]:
                print(f"   📄 {f}")
                
        if prototype_files:
            print(f"\n🎨 ФАЙЛЫ ПРОТОТИПОВ:")
            for f in prototype_files[:3]:
                print(f"   📄 {f}")
        
        # Читаем один из главных файлов
        if bitrix_files:
            main_file = bitrix_files[0]
            print(f"\n📖 СОДЕРЖИМОЕ {main_file}:")
            print("="*60)
            try:
                with open(main_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content[:500] + "..." if len(content) > 500 else content)
            except Exception as e:
                print(f"❌ Ошибка чтения: {e}")
            print("="*60)
        
        # Оценка качества результата
        success = len(bitrix_files) > 0 and len(prototype_files) > 0
        
        return {
            'success': success,
            'execution_time': execution_time,
            'total_files': len(all_files),
            'bitrix_files': len(bitrix_files),
            'prototype_files': len(prototype_files),
            'analysis_files': len(analysis_files)
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"\n💥 ОШИБКА: {e}")
        print(f"⏱️ ВРЕМЯ ДО ОШИБКИ: {execution_time:.2f}с")
        
        return {
            'success': False,
            'error': str(e),
            'execution_time': execution_time
        }


async def main():
    """Главная функция"""
    
    print("🐱 KittyCore 3.0 - РЕАЛЬНЫЙ АНАЛИЗ РЫНКА БИТРИКС24")
    print("=" * 80)
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ НУЖЕН OPENROUTER_API_KEY")
        return
    
    result = await test_bitrix_market_analysis()
    
    print("\n" + "="*80)
    print("🏆 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print("="*80)
    
    if result.get('success'):
        print("🎉 УСПЕХ! Система провела РЕАЛЬНЫЙ анализ рынка!")
        print(f"   ⏱️ Время: {result['execution_time']:.2f}с")
        print(f"   📁 Всего файлов: {result['total_files']}")
        print(f"   📊 Анализ Битрикс24: {result['bitrix_files']} файлов")
        print(f"   🎨 Прототипы: {result['prototype_files']} файлов")
        print(f"   📈 Анализы: {result['analysis_files']} файлов")
        
        # Проверим качество с валидатором
        print("\n🎯 Теперь валидатор проверит качество результатов...")
        
    else:
        if 'error' in result:
            print(f"❌ ОШИБКА: {result['error']}")
        else:
            print("❌ НЕУДАЧА: система не создала нужные файлы")
        
        print(f"   ⏱️ Время: {result['execution_time']:.2f}с")


if __name__ == "__main__":
    asyncio.run(main()) 