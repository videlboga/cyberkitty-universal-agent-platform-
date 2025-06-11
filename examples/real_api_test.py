#!/usr/bin/env python3
"""
🌐 Тест саморазвивающегося агента с реальным API

Этот тест использует реальные запросы к OpenRouter через VPN
для демонстрации настоящего улучшения производительности.
"""

import os
import sys
import time
import requests
sys.path.append('/app')

from kittycore import Agent
from kittycore.self_improvement import create_self_improving_agent

def check_vpn_connection():
    """Проверка VPN подключения"""
    try:
        # Проверяем внешний IP
        response = requests.get('https://httpbin.org/ip', timeout=10)
        ip_info = response.json()
        print(f"🌐 Внешний IP: {ip_info['origin']}")
        
        # Проверяем доступность OpenRouter
        response = requests.get('https://openrouter.ai', timeout=10)
        if response.status_code == 200:
            print("✅ OpenRouter доступен")
            return True
        else:
            print(f"❌ OpenRouter недоступен: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def test_real_improvement():
    """Тест реального улучшения с API"""
    
    print("🧠 Тест саморазвивающегося агента с реальным API")
    print("=" * 60)
    
    # Проверка VPN
    if not check_vpn_connection():
        print("❌ VPN не работает, используем моки")
        model = "mock"
    else:
        print("✅ VPN активен, используем реальный API")
        model = "deepseek/deepseek-chat"
    
    # Проверка API ключа
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key and model != "mock":
        print("❌ Нет API ключа, используем моки")
        model = "mock"
    else:
        print(f"🔑 API ключ: {'*' * (len(api_key) - 8) + api_key[-8:]}")
        
        # Настройка переменных окружения для OpenRouter
        os.environ['OPENAI_API_KEY'] = api_key
        os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'
    
    # Создание агента
    base_agent = Agent(
        prompt="""
        Ты эксперт-аналитик данных. Твоя задача:
        1. Анализировать предоставленные данные
        2. Находить закономерности и инсайты
        3. Давать практические рекомендации
        4. Улучшать качество своих ответов со временем
        
        Отвечай структурированно, с конкретными выводами.
        """,
        model=model
    )
    
    # Обёртка в саморазвивающегося агента
    smart_agent = create_self_improving_agent("real_api_agent", base_agent)
    
    # Тестовые задачи разной сложности
    tasks = [
        {
            "task": "Проанализируй тренд: продажи января 100, февраля 120, марта 95",
            "complexity": "simple",
            "expected_keywords": ["тренд", "снижение", "волатильность"]
        },
        {
            "task": "Какие факторы могут влиять на конверсию в e-commerce?",
            "complexity": "medium", 
            "expected_keywords": ["ux", "цена", "доставка", "отзывы"]
        },
        {
            "task": "Создай SQL запрос для поиска клиентов с LTV > 1000 и последней покупкой в 2024",
            "complexity": "medium",
            "expected_keywords": ["SELECT", "WHERE", "LTV", "2024"]
        },
        {
            "task": "Как построить модель прогнозирования оттока клиентов?",
            "complexity": "hard",
            "expected_keywords": ["машинное обучение", "признаки", "модель", "валидация"]
        },
        {
            "task": "Оптимизируй рекламный бюджет: Facebook 30% CTR 2%, Google 50% CTR 3%, Email 20% CTR 8%",
            "complexity": "hard",
            "expected_keywords": ["email", "эффективность", "перераспределение", "ROI"]
        }
    ]
    
    print(f"📋 Выполнение {len(tasks)} задач с нарастающей сложностью...")
    print()
    
    results = []
    
    for i, task_info in enumerate(tasks, 1):
        task = task_info["task"]
        complexity = task_info["complexity"]
        expected_keywords = task_info["expected_keywords"]
        
        print(f"🔄 Задача {i}/{len(tasks)} ({complexity}): {task[:50]}...")
        
        start_time = time.time()
        
        try:
            # Выполнение с самооценкой
            result = smart_agent.run_with_self_improvement(
                task,
                context={
                    'task_number': i,
                    'complexity': complexity,
                    'expected_keywords': expected_keywords
                }
            )
            
            execution_time = time.time() - start_time
            
            # Оценка качества ответа
            result_text = str(result).lower()
            keyword_score = sum(1 for kw in expected_keywords if kw.lower() in result_text) / len(expected_keywords)
            
            results.append({
                'task_number': i,
                'complexity': complexity,
                'execution_time': execution_time,
                'keyword_score': keyword_score,
                'result_length': len(str(result)),
                'result_preview': str(result)[:100] + "..."
            })
            
            print(f"✅ Выполнено за {execution_time:.2f}с")
            print(f"📊 Качество: {keyword_score:.1%} (ключевые слова)")
            print(f"📄 Ответ: {str(result)[:150]}...")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            results.append({
                'task_number': i,
                'complexity': complexity,
                'execution_time': 0,
                'keyword_score': 0,
                'result_length': 0,
                'error': str(e)
            })
        
        print()
        time.sleep(1)  # Пауза между запросами
    
    # Анализ результатов
    print("=" * 60)
    print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ")
    print("=" * 60)
    
    # Отчёт агента
    report = smart_agent.get_self_improvement_report()
    
    print(f"🆔 ID агента: {report['agent_id']}")
    print(f"📈 Выполнено задач: {report['task_count']}")
    print(f"🛠️ Создано инструментов: {report['created_tools']}")
    print(f"🔧 Применено оптимизаций: {report['optimizations_applied']}")
    print()
    
    # Анализ прогресса
    successful_results = [r for r in results if 'error' not in r]
    
    if len(successful_results) >= 3:
        first_three = successful_results[:3]
        last_three = successful_results[-3:]
        
        avg_time_start = sum(r['execution_time'] for r in first_three) / len(first_three)
        avg_time_end = sum(r['execution_time'] for r in last_three) / len(last_three)
        
        avg_quality_start = sum(r['keyword_score'] for r in first_three) / len(first_three)
        avg_quality_end = sum(r['keyword_score'] for r in last_three) / len(last_three)
        
        time_improvement = (avg_time_start - avg_time_end) / avg_time_start if avg_time_start > 0 else 0
        quality_improvement = (avg_quality_end - avg_quality_start) / avg_quality_start if avg_quality_start > 0 else 0
        
        print("📈 ПРОГРЕСС ОБУЧЕНИЯ:")
        print(f"⏱️  Время выполнения: {time_improvement:.1%} {'улучшение' if time_improvement > 0 else 'ухудшение'}")
        print(f"🎯 Качество ответов: {quality_improvement:.1%} {'улучшение' if quality_improvement > 0 else 'ухудшение'}")
        print()
        
        if time_improvement > 0.1 or quality_improvement > 0.1:
            print("✅ АГЕНТ ПОКАЗАЛ ЗНАЧИТЕЛЬНОЕ УЛУЧШЕНИЕ!")
        elif time_improvement > 0 or quality_improvement > 0:
            print("📈 Агент показал умеренное улучшение")
        else:
            print("➡️ Производительность стабильна")
    
    # Детальные метрики
    print("\n📊 ДЕТАЛЬНЫЕ МЕТРИКИ:")
    performance = report['performance_summary']
    
    for metric_name, data in performance.items():
        trend_emoji = {
            'improving': '📈',
            'stable': '➡️',
            'declining': '📉'
        }.get(data['trend'], '❓')
        
        print(f"{trend_emoji} {metric_name}:")
        print(f"   Начальное: {data['baseline']:.3f}")
        print(f"   Текущее: {data['current']:.3f}")
        print(f"   Изменение: {data['improvement_rate']:.1%}")
        print()
    
    print("🚀 Тест завершён!")
    
    return results, report

if __name__ == "__main__":
    test_real_improvement() 