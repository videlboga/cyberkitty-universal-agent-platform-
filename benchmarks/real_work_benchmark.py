#!/usr/bin/env python3
"""
🎯 REAL WORK BENCHMARK для KittyCore 3.0
Тестирует агентную систему на реальных рабочих задачах

Основано на исследованиях:
- SWE-bench: реальные GitHub issues
- AgentBench: разнообразные практические задачи  
- C³-Bench: многозадачность с инструментами
"""

import asyncio
import sys
import os
import time
import json
from typing import List, Dict, Any
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from kittycore.core.orchestrator import OrchestratorAgent

class RealWorkBenchmark:
    """Бенчмарк реальных рабочих задач"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        
    async def run_benchmark(self):
        """Запуск бенчмарка"""
        print("🎯 REAL WORK BENCHMARK для KittyCore 3.0")
        print("=" * 50)
        
        self.start_time = time.time()
        
        # Простые но реальные задачи
        tasks = [
            {
                'name': 'Анализ данных продаж',
                'description': 'Проанализируй данные продаж за последний месяц. Найди топ-3 товара и дай рекомендации по улучшению продаж.',
                'complexity': 'medium'
            },
            {
                'name': 'Создание технической документации',
                'description': 'Создай техническую документацию для REST API. Включи описание endpoints, примеры запросов и ответов.',
                'complexity': 'high'
            },
            {
                'name': 'План маркетинговой кампании',
                'description': 'Разработай план маркетинговой кампании для запуска нового продукта. Включи целевую аудиторию, каналы и бюджет.',
                'complexity': 'medium'
            },
            {
                'name': 'Автоматизация рабочего процесса',
                'description': 'Создай план автоматизации процесса обработки заявок клиентов. Опиши этапы и необходимые инструменты.',
                'complexity': 'high'
            },
            {
                'name': 'Анализ конкурентов',
                'description': 'Проведи анализ 3 основных конкурентов. Сравни их продукты, цены и маркетинговые стратегии.',
                'complexity': 'medium'
            }
        ]
        
        total_score = 0
        
        for i, task in enumerate(tasks, 1):
            print(f"\n📋 Задача {i}/{len(tasks)}: {task['name']}")
            print(f"Описание: {task['description']}")
            print(f"Сложность: {task['complexity']}")
            
            result = await self.execute_task(task)
            self.results.append(result)
            total_score += result['score']
            
            status = "✅ УСПЕХ" if result['score'] >= 0.7 else "❌ НЕУДАЧА"
            print(f"Результат: {status} ({result['score']:.1f}/1.0)")
        
        # Финальные результаты
        total_time = time.time() - self.start_time
        success_rate = total_score / len(tasks) * 100
        
        print(f"\n🏆 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ")
        print("=" * 50)
        print(f"Общий счёт: {total_score:.1f}/{len(tasks)} ({success_rate:.1f}%)")
        print(f"Время выполнения: {total_time:.1f} секунд")
        
        await self.save_results()
        
        return {
            'score': total_score,
            'total': len(tasks),
            'success_rate': success_rate,
            'time': total_time
        }
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение одной задачи"""
        start_time = time.time()
        
        try:
            # Создаём оркестратор для задачи
            orchestrator = OrchestratorAgent()
            
            # Выполняем задачу
            result = await orchestrator.solve_task(task['description'])
            
            execution_time = time.time() - start_time
            
            # Простая оценка результата
            score = self.evaluate_result(result)
            
            # Очищаем результат от несериализуемых объектов
            clean_result = self._clean_result_for_json(result)
            
            return {
                'task': task['name'],
                'complexity': task['complexity'],
                'score': score,
                'time': execution_time,
                'result': clean_result
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ ОШИБКА: {str(e)}")
            
            return {
                'task': task['name'],
                'complexity': task['complexity'],
                'score': 0,
                'time': execution_time,
                'error': str(e)
            }
    
    def evaluate_result(self, result: Dict[str, Any]) -> float:
        """Простая оценка результата"""
        score = 0.0
        
        # Задача выполнена
        if result.get('status') == 'completed':
            score += 0.5
        
        # Есть осмысленное решение
        if result.get('solution') and len(result['solution']) > 50:
            score += 0.3
        
        # Созданы агенты или файлы
        if result.get('agents_created') or result.get('created_files'):
            score += 0.2
        
        return min(score, 1.0)
    
    def _clean_result_for_json(self, result):
        """Очищает результат от несериализуемых объектов для JSON"""
        from datetime import datetime
        
        if isinstance(result, dict):
            cleaned = {}
            for key, value in result.items():
                if hasattr(value, '__dict__') and not isinstance(value, datetime):  # Если это объект (например Agent)
                    cleaned[key] = str(value)  # Преобразуем в строку
                elif isinstance(value, datetime):
                    cleaned[key] = value.isoformat()  # Преобразуем datetime в строку
                elif isinstance(value, (list, dict)):
                    cleaned[key] = self._clean_result_for_json(value)
                else:
                    cleaned[key] = value
            return cleaned
        elif isinstance(result, list):
            return [self._clean_result_for_json(item) for item in result]
        elif isinstance(result, datetime):
            return result.isoformat()
        else:
            return result
    
    async def save_results(self):
        """Сохранение результатов"""
        os.makedirs('workspace/benchmark_results', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'workspace/benchmark_results/real_work_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Результаты сохранены: {filename}")

async def main():
    """Запуск бенчмарка"""
    benchmark = RealWorkBenchmark()
    results = await benchmark.run_benchmark()
    
    if results['success_rate'] >= 80:
        print("🏆 ОТЛИЧНЫЙ результат!")
    elif results['success_rate'] >= 60:
        print("👍 ХОРОШИЙ результат!")
    else:
        print("⚠️ НУЖНА РАБОТА!")

if __name__ == "__main__":
    asyncio.run(main()) 