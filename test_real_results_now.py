#!/usr/bin/env python3
"""РЕАЛЬНЫЙ тест с настоящими результатами - НИКАКИХ ОТЧЁТОВ!"""

import asyncio
import os
import sys
import time

# Добавляем путь к модулям KittyCore
sys.path.append('/home/cyberkitty/Project/kittycore')

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig


def setup_aggressive_llm():
    """Агрессивные настройки для получения НАСТОЯЩИХ результатов"""
    
    # Пробуем разные стратегии
    strategies = [
        # Стратегия 1: Очень быстрая модель с коротким таймаутом
        {
            "model": "google/gemini-2.5-flash-lite-preview-06-17",  # Самая быстрая
            "timeout": "15",
            "max_tokens": "1000",
            "temperature": "0"
        },
        # Стратегия 2: Бесплатная модель
        {
            "model": "deepseek/deepseek-r1-0528:free",
            "timeout": "20", 
            "max_tokens": "1500",
            "temperature": "0.1"
        },
        # Стратегия 3: Очень маленькие запросы
        {
            "model": "google/gemini-2.5-flash",
            "timeout": "10",
            "max_tokens": "500", 
            "temperature": "0"
        }
    ]
    
    # Выбираем первую стратегию
    strategy = strategies[0]
    
    os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY", "")
    os.environ["LLM_MODEL"] = strategy["model"]
    os.environ["TIMEOUT"] = strategy["timeout"]
    os.environ["MAX_TOKENS"] = strategy["max_tokens"]
    os.environ["TEMPERATURE"] = strategy["temperature"]
    
    print("⚡ АГРЕССИВНЫЕ НАСТРОЙКИ LLM:")
    print(f"   Модель: {strategy['model']}")
    print(f"   Таймаут: {strategy['timeout']}с (очень короткий)")
    print(f"   Токены: {strategy['max_tokens']} (минимум)")
    print(f"   Температура: {strategy['temperature']} (детерминированность)")


async def test_real_results():
    """Тест для получения НАСТОЯЩИХ результатов"""
    
    print("\n" + "="*70)
    print("🎯 ТЕСТ НАСТОЯЩИХ РЕЗУЛЬТАТОВ - НИКАКИХ ОТЧЁТОВ!")
    print("="*70)
    
    setup_aggressive_llm()
    
    # ПРОСТЕЙШАЯ задача для максимального успеха
    task = "Создай файл hello.py с print('Hello World')"
    vault_path = "vault_real_world"
    
    print(f"\n📋 ЗАДАЧА: {task}")
    print(f"📂 VAULT: {vault_path}")
    
    # Отключаем все лишнее для скорости
    config = UnifiedConfig(
        vault_path=vault_path,
        max_agents=1,  # Минимум агентов
        timeout=60,    # Короткий общий таймаут
        enable_human_intervention=False,  # Без человека
        enable_smart_validation=False,    # Без валидации пока
        enable_metrics=False,             # Без метрик
        enable_vector_memory=False,       # Без векторной памяти
        enable_amem_memory=False,         # Без A-MEM пока
        enable_shared_chat=False,         # Без чата
        enable_tool_adaptation=False      # Без адаптации
    )
    
    orchestrator = UnifiedOrchestrator(config=config)
    
    start_time = time.time()
    
    try:
        print("\n🚀 ЗАПУСК С МИНИМАЛЬНЫМИ НАСТРОЙКАМИ...")
        
        # Главный тест
        result = await orchestrator.solve_task(task)
        
        execution_time = time.time() - start_time
        print(f"\n⏱️ ВРЕМЯ: {execution_time:.2f}с")
        
        # Проверяем РЕАЛЬНЫЕ файлы
        import glob
        all_files = glob.glob(f"{vault_path}/**/*", recursive=True)
        real_files = [f for f in all_files if os.path.isfile(f)]
        
        print(f"\n📁 СОЗДАНО ФАЙЛОВ: {len(real_files)}")
        
        # Ищем hello.py
        hello_files = [f for f in real_files if 'hello.py' in f]
        
        if hello_files:
            print(f"✅ НАШЛИ hello.py: {hello_files[0]}")
            
            # ЧИТАЕМ СОДЕРЖИМОЕ
            with open(hello_files[0], 'r') as f:
                content = f.read()
                print(f"📄 СОДЕРЖИМОЕ hello.py:")
                print("="*50)
                print(content)
                print("="*50)
                
                if "print" in content and "Hello" in content:
                    print("🎉 НАСТОЯЩИЙ КОД! НЕ ОТЧЁТ!")
                    return {'success': True, 'real_content': True}
                else:
                    print("😞 Это не настоящий код...")
                    return {'success': False, 'real_content': False}
        else:
            print("❌ hello.py НЕ НАЙДЕН")
            
            # Покажем что создалось
            print("\n📂 СОЗДАННЫЕ ФАЙЛЫ:")
            for f in real_files[:10]:
                print(f"   📄 {f}")
            
            return {'success': False, 'files_created': len(real_files)}
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"\n💥 ОШИБКА: {e}")
        print(f"⏱️ ВРЕМЯ ДО ОШИБКИ: {execution_time:.2f}с")
        
        return {'success': False, 'error': str(e)}


async def main():
    """Главная функция"""
    
    print("🐱 KittyCore 3.0 - РЕАЛЬНЫЕ РЕЗУЛЬТАТЫ ИЛИ СМЕРТЬ!")
    print("=" * 70)
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ НУЖЕН OPENROUTER_API_KEY")
        return
    
    result = await test_real_results()
    
    print("\n" + "="*70)
    print("🏆 ФИНАЛЬНЫЙ ВЕРДИКТ:")
    print("="*70)
    
    if result.get('success') and result.get('real_content'):
        print("🎉 ПОБЕДА! Система создала НАСТОЯЩИЙ КОД!")
        print("   KittyCore 3.0 работает как надо!")
    elif result.get('success'):
        print("⚠️ Система работает, но результат сомнительный")
    else:
        print("💀 Система пока создаёт только отчёты о работе...")
        print("   Ты прав - это просто генератор отчётов 😞")


if __name__ == "__main__":
    asyncio.run(main()) 