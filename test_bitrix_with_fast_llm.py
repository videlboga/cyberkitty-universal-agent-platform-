#!/usr/bin/env python3
"""Тест задачи Битрикс24 с БЫСТРОЙ LLM моделью и оптимальными настройками"""

import asyncio
import os
import sys
import time
import glob

# Добавляем путь к модулям KittyCore
sys.path.append('/home/cyberkitty/Project/kittycore')

from kittycore.core.unified_orchestrator import UnifiedOrchestrator
from kittycore.core.content_validator import ContentValidator
from kittycore.core.metrics_collector import MetricsCollector


def setup_fast_llm_config():
    """Настройка быстрой LLM модели с оптимальными параметрами"""
    
    # Используем бесплатную быструю модель DeepSeek R1
    os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY", "")
    os.environ["LLM_MODEL"] = "deepseek/deepseek-r1-0528:free"  # Бесплатная и быстрая
    os.environ["TIMEOUT"] = "30"  # Короткий таймаут
    os.environ["MAX_TOKENS"] = "4000"  # Меньше токенов = быстрее
    os.environ["TEMPERATURE"] = "0.1"  # Низкая температура = более детерминированный результат
    
    print("🚀 НАСТРОЙКА LLM:")
    print(f"   Модель: {os.environ['LLM_MODEL']}")
    print(f"   Таймаут: {os.environ['TIMEOUT']}с")
    print(f"   Макс токены: {os.environ['MAX_TOKENS']}")
    print(f"   Температура: {os.environ['TEMPERATURE']}")
    print(f"   API ключ: {'✅ установлен' if os.environ['OPENROUTER_API_KEY'] else '❌ НЕ установлен'}")


async def test_bitrix_analysis_task():
    """Тест комплексной задачи анализа Битрикс24 с быстрой LLM"""
    
    print("\n" + "="*80)
    print("🎯 ТЕСТ: Анализ рынка Битрикс24 с БЫСТРОЙ LLM")
    print("="*80)
    
    setup_fast_llm_config()
    
    # Задача для анализа
    task = """
    Проведи анализ рынка Битрикс24:
    1. Найди ТОП-10 популярных приложений 
    2. Создай отчёт что существует
    3. Оцени сложность реализации и проблемы
    4. Создай 3 прототипа улучшенных UX приложений
    """
    
    vault_path = "vault_bitrix_fast"
    
    print(f"\n📋 ЗАДАЧА: {task}")
    print(f"📂 VAULT: {vault_path}")
    
    # Создаём оркестратор
    orchestrator = UnifiedOrchestrator(vault_path=vault_path)
    
    start_time = time.time()
    
    try:
        print("\n🚀 ЗАПУСК задачи...")
        
        # Выполняем задачу
        result = await orchestrator.execute_task(task)
        
        execution_time = time.time() - start_time
        print(f"\n⏱️ ВРЕМЯ ВЫПОЛНЕНИЯ: {execution_time:.2f}с")
        
        # Оценка результата с ContentValidator
        validator = ContentValidator()
        
        # Собираем список созданных файлов
        created_files = glob.glob(f"{vault_path}/**/*", recursive=True)
        created_files = [f for f in created_files if os.path.isfile(f)]
        
        validation_result = validator.validate_task_result(task, created_files)
        quality_score = validation_result.get('percentage', 0.0) / 100.0
        
        # Собираем метрики
        metrics = MetricsCollector(vault_path)
        stats = await metrics.collect_comprehensive_metrics()
        
        print(f"\n📊 ОЦЕНКА КАЧЕСТВА: {quality_score:.2f}")
        print(f"📄 СОЗДАННЫХ ФАЙЛОВ: {stats.get('total_files', 0)}")
        print(f"📈 СТАТУС: {'✅ УСПЕХ' if quality_score >= 0.7 else '❌ ПРОВАЛ'}")
        
        # Детальная информация
        print(f"\n🔍 МЕТРИКИ СИСТЕМЫ:")
        print(f"   📁 Общих файлов: {stats.get('total_files', 0)}")
        print(f"   🤖 Агентов создано: {stats.get('agent_count', 0)}")
        print(f"   📋 Задач выполнено: {stats.get('task_count', 0)}")
        
        return {
            'success': quality_score >= 0.7,
            'quality_score': quality_score,
            'execution_time': execution_time,
            'files_created': stats.get('total_files', 0),
            'task_completed': True
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        
        print(f"\n❌ ОШИБКА: {error_msg}")
        print(f"⏱️ ВРЕМЯ ДО ОШИБКИ: {execution_time:.2f}с")
        
        return {
            'success': False,
            'error': error_msg,
            'execution_time': execution_time,
            'task_completed': False
        }


async def main():
    """Главная функция"""
    
    print("🐱 KittyCore 3.0 - Тест БЫСТРОЙ LLM с задачей Битрикс24")
    print("=" * 80)
    
    # Проверяем API ключ
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ ОШИБКА: Не установлен OPENROUTER_API_KEY")
        print("   Установите: export OPENROUTER_API_KEY=your_key")
        return
    
    result = await test_bitrix_analysis_task()
    
    print("\n" + "="*80)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print("="*80)
    
    if result['task_completed']:
        if result['success']:
            print(f"✅ УСПЕХ! Система с LLM работает отлично")
            print(f"   📈 Качество: {result['quality_score']:.2f}")
            print(f"   📄 Файлов: {result['files_created']}")
            print(f"   ⏱️ Время: {result['execution_time']:.2f}с")
        else:
            print(f"⚠️ НИЗКОЕ КАЧЕСТВО: система работает, но результат плохой")
            print(f"   📈 Качество: {result['quality_score']:.2f} (нужно ≥0.7)")
            print(f"   📄 Файлов: {result['files_created']}")
            print(f"   ⏱️ Время: {result['execution_time']:.2f}с")
    else:
        print(f"❌ ПРОВАЛ: {result['error']}")
        print(f"   ⏱️ Время до ошибки: {result['execution_time']:.2f}с")
        
        if "timeout" in result['error'].lower():
            print("\n💡 РЕКОМЕНДАЦИИ для решения таймаута:")
            print("   1. Увеличить TIMEOUT в переменных окружения")
            print("   2. Уменьшить MAX_TOKENS")
            print("   3. Попробовать другую модель")
            print("   4. Проверить интернет соединение")


if __name__ == "__main__":
    asyncio.run(main()) 