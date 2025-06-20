#!/usr/bin/env python3
"""Простой тест LLM без валидации - проверяем что система вообще работает"""

import asyncio
import os
import sys
import time

# Добавляем путь к модулям KittyCore
sys.path.append('/home/cyberkitty/Project/kittycore')

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig


def setup_fast_llm_config():
    """Настройка быстрой LLM модели"""
    
    # Используем бесплатную быструю модель
    os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY", "")
    os.environ["LLM_MODEL"] = "deepseek/deepseek-r1-0528:free"
    os.environ["TIMEOUT"] = "30"
    os.environ["MAX_TOKENS"] = "2000"
    os.environ["TEMPERATURE"] = "0.1"
    
    print("🚀 НАСТРОЙКА LLM:")
    print(f"   Модель: {os.environ['LLM_MODEL']}")
    print(f"   Таймаут: {os.environ['TIMEOUT']}с")
    print(f"   API ключ: {'✅ установлен' if os.environ['OPENROUTER_API_KEY'] else '❌ НЕ установлен'}")


async def test_simple_task():
    """Простой тест LLM"""
    
    print("\n" + "="*60)
    print("🎯 ПРОСТОЙ ТЕСТ LLM")
    print("="*60)
    
    setup_fast_llm_config()
    
    # Простая задача
    task = "Создай простой Python скрипт hello.py который выводит Hello World"
    vault_path = "vault_simple_llm_test"
    
    print(f"\n📋 ЗАДАЧА: {task}")
    print(f"📂 VAULT: {vault_path}")
    
    # Создаём оркестратор с конфигурацией
    config = UnifiedConfig(vault_path=vault_path)
    orchestrator = UnifiedOrchestrator(config=config)
    
    start_time = time.time()
    
    try:
        print("\n🚀 ЗАПУСК...")
        
        # Выполняем задачу через solve_task
        result = await orchestrator.solve_task(task)
        
        execution_time = time.time() - start_time
        print(f"\n⏱️ ВРЕМЯ: {execution_time:.2f}с")
        print(f"📊 РЕЗУЛЬТАТ: {result}")
        
        # Проверяем что файлы созданы
        import glob
        files = glob.glob(f"{vault_path}/**/*", recursive=True)
        files = [f for f in files if os.path.isfile(f)]
        
        print(f"\n📁 СОЗДАНО ФАЙЛОВ: {len(files)}")
        for file_path in files[:5]:
            print(f"   📄 {file_path}")
        
        if len(files) > 5:
            print(f"   ... и ещё {len(files) - 5}")
        
        return {
            'success': True,
            'execution_time': execution_time,
            'files_created': len(files),
            'completed': True
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
            'completed': False
        }


async def main():
    """Главная функция"""
    
    print("🐱 KittyCore 3.0 - ПРОСТОЙ ТЕСТ LLM")
    print("=" * 60)
    
    # Проверяем API ключ
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ ОШИБКА: Не установлен OPENROUTER_API_KEY")
        return
    
    result = await test_simple_task()
    
    print("\n" + "="*60)
    print("📊 ИТОГ:")
    print("="*60)
    
    if result['completed']:
        if result['success']:
            print(f"✅ УСПЕХ! LLM система работает!")
            print(f"   📄 Файлов: {result['files_created']}")
            print(f"   ⏱️ Время: {result['execution_time']:.2f}с")
        else:
            print(f"⚠️ СИСТЕМА РАБОТАЕТ, но есть проблемы")
    else:
        print(f"❌ LLM НЕ РАБОТАЕТ: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main()) 