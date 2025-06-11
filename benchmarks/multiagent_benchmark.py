#!/usr/bin/env python3
"""
🤝 MULTI-AGENT COLLABORATION BENCHMARK для KittyCore 3.0
Тестирует коллективную работу агентов, memory sharing и координацию
"""

import asyncio
import sys
import os
import time
import json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from kittycore.core.orchestrator import OrchestratorAgent

class MultiAgentBenchmark:
    """Бенчмарк коллективной работы агентов"""
    
    def __init__(self):
        self.results = []
        
    async def run_benchmark(self):
        """Запуск бенчмарка коллективной работы"""
        print("🤝 MULTI-AGENT COLLABORATION BENCHMARK")
        print("=" * 50)
        
        # Задачи требующие координации нескольких агентов
        collaboration_tasks = [
            {
                'name': 'Проект интернет-магазина',
                'description': 'Создайте полный проект интернет-магазина: техническая архитектура, дизайн UI/UX, маркетинговый план и бизнес-модель. Каждый аспект должен дополнять другой.',
                'required_agents': ['technical', 'design', 'marketing', 'business'],
                'complexity': 'very_high'
            },
            {
                'name': 'Запуск нового продукта',
                'description': 'Подготовьте запуск нового SaaS продукта: исследование рынка, MVP план, ценообразование и стратегия выхода на рынок.',
                'required_agents': ['research', 'product', 'pricing', 'marketing'],
                'complexity': 'high'
            },
            {
                'name': 'Анализ конкурентной среды',
                'description': 'Проведите полный анализ конкурентов в сфере EdTech: продуктовые фичи, ценообразование, маркетинг и SWOT-анализ.',
                'required_agents': ['analyst', 'market_research', 'product_comparison'],
                'complexity': 'medium'
            }
        ]
        
        total_score = 0
        
        for i, task in enumerate(collaboration_tasks, 1):
            print(f"\n🎯 Коллективная задача {i}/{len(collaboration_tasks)}: {task['name']}")
            print(f"Описание: {task['description']}")
            print(f"Требуется агентов: {len(task['required_agents'])}")
            
            result = await self.execute_collaboration_task(task)
            self.results.append(result)
            total_score += result['score']
            
            # Проверяем координацию агентов
            coordination_score = self.evaluate_agent_coordination(result)
            memory_sharing_score = self.evaluate_memory_sharing(result)
            
            print(f"Результат задачи: {result['score']:.1f}/1.0")
            print(f"Координация агентов: {coordination_score:.1f}/1.0")
            print(f"Обмен памятью: {memory_sharing_score:.1f}/1.0")
            
        # Результаты
        success_rate = total_score / len(collaboration_tasks) * 100
        print(f"\n🏆 РЕЗУЛЬТАТЫ КОЛЛЕКТИВНОЙ РАБОТЫ")
        print("=" * 50)
        print(f"Общий счёт: {total_score:.1f}/{len(collaboration_tasks)} ({success_rate:.1f}%)")
        
        await self.save_results()
        
        return {
            'score': total_score,
            'total': len(collaboration_tasks),
            'success_rate': success_rate
        }
    
    async def execute_collaboration_task(self, task):
        """Выполнение коллективной задачи"""
        start_time = time.time()
        
        try:
            orchestrator = OrchestratorAgent()
            
            # Подчёркиваем необходимость коллективной работы
            enhanced_description = f"""
            {task['description']}
            
            ВАЖНО: Эта задача требует создания команды из {len(task['required_agents'])} специализированных агентов.
            Каждый агент должен работать в своей области: {', '.join(task['required_agents'])}.
            Агенты должны обмениваться информацией и координировать свои действия.
            """
            
            result = await orchestrator.solve_task(enhanced_description)
            
            execution_time = time.time() - start_time
            score = self.evaluate_result(result)
            
            # Очищаем результат от несериализуемых объектов
            clean_result = self._clean_result_for_json(result)
            
            return {
                'task': task['name'],
                'complexity': task['complexity'],
                'score': score,
                'time': execution_time,
                'result': clean_result,
                'agents_created': result.get('agents_created', 0),
                'files_created': len(result.get('created_files', []))
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
    
    def evaluate_result(self, result):
        """Оценка результата коллективной задачи"""
        score = 0.0
        
        # Базовое выполнение
        if result.get('status') == 'completed':
            score += 0.3
        
        # Количество созданных агентов
        agents_created = result.get('agents_created', 0)
        if agents_created >= 3:
            score += 0.3
        elif agents_created >= 2:
            score += 0.2
        elif agents_created >= 1:
            score += 0.1
        
        # Качество решения
        solution = result.get('solution', '')
        if len(solution) > 200:
            score += 0.2
        
        # Созданные артефакты
        if result.get('created_files'):
            score += 0.2
        
        return min(score, 1.0)
    
    def evaluate_agent_coordination(self, result):
        """Оценка координации между агентами"""
        score = 0.0
        
        # Проверяем rich_reporting для отслеживания взаимодействий
        if 'rich_reporting' in result:
            score += 0.3
        
        # Количество созданных агентов
        agents_created = result.get('agents_created', 0)
        if agents_created >= 3:
            score += 0.4
        elif agents_created >= 2:
            score += 0.2
        
        # Наличие планирования и координации в решении
        solution = str(result.get('solution', '')).lower()
        coordination_keywords = ['координация', 'взаимодействие', 'команда', 'совместно', 'коллектив']
        if any(keyword in solution for keyword in coordination_keywords):
            score += 0.3
        
        return min(score, 1.0)
    
    def evaluate_memory_sharing(self, result):
        """Оценка обмена памятью между агентами"""
        score = 0.0
        
        # Если есть rich reporting - есть отслеживание памяти
        if 'rich_reporting' in result:
            rich_data = result['rich_reporting']
            if 'execution_id' in rich_data:
                score += 0.4
        
        # Проверяем качество и связность решения
        solution = result.get('solution', '')
        if len(solution) > 300:  # Более детальное решение
            score += 0.3
        
        # Упоминание обмена информацией
        if 'информац' in solution.lower() or 'данны' in solution.lower():
            score += 0.3
        
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
        filename = f'workspace/benchmark_results/multiagent_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Результаты сохранены: {filename}")

async def main():
    """Запуск бенчмарка"""
    benchmark = MultiAgentBenchmark()
    results = await benchmark.run_benchmark()
    
    if results['success_rate'] >= 80:
        print("🏆 ОТЛИЧНАЯ коллективная работа!")
    elif results['success_rate'] >= 60:
        print("👍 ХОРОШАЯ координация агентов!")
    else:
        print("⚠️ НУЖНО УЛУЧШАТЬ сотрудничество!")

if __name__ == "__main__":
    asyncio.run(main()) 