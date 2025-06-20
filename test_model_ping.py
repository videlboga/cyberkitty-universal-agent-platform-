#!/usr/bin/env python3
"""
🚀 ТЕСТ СКОРОСТИ МОДЕЛЕЙ - найдем самую быструю

Цель: протестировать разные модели и найти оптимальную по скорости
"""

import time
import os
from typing import Dict, List

# Настройка окружения
os.environ["MAX_TOKENS"] = "50"  # Короткие ответы для скорости
os.environ["TEMPERATURE"] = "0.1"
os.environ["TIMEOUT"] = "10"  # Короткий таймаут

# Модели для тестирования
TEST_MODELS = [
    # Быстрые модели
    "deepseek/deepseek-chat",
    "google/gemini-2.0-flash-exp",
    "google/gemini-flash-1.5",
    "anthropic/claude-3-haiku",
    "meta-llama/llama-3.1-8b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "huggingface/zephyr-7b-beta:free",
    "mistralai/mistral-7b-instruct:free",
    
    # Groq модели (очень быстрые)
    "groq/llama-3.1-8b-instant",
    "groq/gemma-7b-it",
    "groq/mixtral-8x7b-32768",
]

SIMPLE_PROMPT = "Скажи 'тест' одним словом"

def test_model_speed(model_name: str) -> Dict:
    """🏃 Тестирует скорость модели"""
    
    print(f"   🔍 Тестирую {model_name}...")
    
    try:
        from kittycore.llm import get_llm_provider
        
        start_time = time.time()
        
        # Создаем провайдер с моделью
        llm = get_llm_provider(model=model_name)
        init_time = time.time() - start_time
        
        # Тестируем запрос
        request_start = time.time()
        response = llm.complete(SIMPLE_PROMPT)
        request_time = time.time() - request_start
        
        total_time = time.time() - start_time
        
        result = {
            'model': model_name,
            'success': True,
            'init_time': round(init_time, 2),
            'request_time': round(request_time, 2),
            'total_time': round(total_time, 2),
            'response_length': len(response),
            'response': response[:50],
            'error': None
        }
        
        print(f"   ✅ {model_name}: {request_time:.2f}с (инициализация: {init_time:.2f}с)")
        return result
        
    except Exception as e:
        error_time = time.time() - start_time
        
        result = {
            'model': model_name,
            'success': False,
            'init_time': 0,
            'request_time': 999,
            'total_time': round(error_time, 2),
            'response_length': 0,
            'response': '',
            'error': str(e)
        }
        
        print(f"   ❌ {model_name}: ОШИБКА - {str(e)[:100]}")
        return result

def ping_models():
    """🚀 Тестируем все модели"""
    
    print("🚀" + "="*70)
    print("🚀 ТЕСТ СКОРОСТИ МОДЕЛЕЙ")
    print("🚀" + "="*70)
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ OPENROUTER_API_KEY не найден!")
        return
    
    results = []
    
    for model in TEST_MODELS:
        result = test_model_speed(model)
        results.append(result)
        time.sleep(1)  # Пауза между запросами
    
    # Сортируем по скорости
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    successful.sort(key=lambda x: x['request_time'])
    
    print(f"\n🏆" + "="*70)
    print(f"🏆 РЕЗУЛЬТАТЫ (сортировка по скорости)")
    print(f"🏆" + "="*70)
    
    print(f"\n✅ РАБОЧИЕ МОДЕЛИ ({len(successful)}):")
    for i, result in enumerate(successful[:10]):  # Топ 10
        speed_emoji = "🚀" if result['request_time'] < 2 else "⚡" if result['request_time'] < 5 else "🐌"
        print(f"{i+1:2d}. {speed_emoji} {result['model']:<40} {result['request_time']:>6.2f}с")
    
    if failed:
        print(f"\n❌ НЕ РАБОТАЮТ ({len(failed)}):")
        for result in failed:
            print(f"   💥 {result['model']:<40} {result['error'][:50]}")
    
    # Рекомендации
    if successful:
        fastest = successful[0]
        print(f"\n🏆 САМАЯ БЫСТРАЯ: {fastest['model']} ({fastest['request_time']:.2f}с)")
        
        # Топ 3 для разных целей
        print(f"\n🎯 РЕКОМЕНДАЦИИ:")
        print(f"   🚀 Для быстрых тестов: {successful[0]['model']}")
        if len(successful) > 1:
            print(f"   ⚡ Для валидации: {successful[1]['model']}")
        if len(successful) > 2:
            print(f"   🎯 Для точности: {successful[2]['model']}")
    
    return results

if __name__ == "__main__":
    ping_models() 