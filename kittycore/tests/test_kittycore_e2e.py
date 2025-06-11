#!/usr/bin/env python3
"""
🧪 E2E тесты KittyCore 3.0 - честные боевые условия без моков
Эмулируем реальные запросы пользователей и проверяем всю систему целиком
"""

import asyncio
import os
import sys
import time
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kittycore.core.orchestrator import OrchestratorAgent
from kittycore.core.self_improvement import SelfLearningEngine

class KittyCoreE2ETester:
    """Честный E2E тестер для KittyCore 3.0"""
    
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.self_learning = SelfLearningEngine()
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Записать результат теста"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            print(f"✅ {test_name}: ПРОШЁЛ {details}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: ПРОВАЛЕН {details}")
    
    async def test_basic_task_execution(self):
        """Тест: Базовое выполнение задачи"""
        print("\n🔥 === ТЕСТ 1: БАЗОВОЕ ВЫПОЛНЕНИЕ ЗАДАЧИ ===")
        
        task = "Создай простой план на завтра для изучения Python"
        
        try:
            start_time = time.time()
            result = await self.orchestrator.execute_task(task)
            execution_time = time.time() - start_time
            
            # Проверки
            has_result = result is not None
            has_meaningful_content = len(str(result)) > 50
            reasonable_time = execution_time < 30.0
            
            success = has_result and has_meaningful_content and reasonable_time
            
            details = f"({execution_time:.1f}s, {len(str(result))} символов)"
            self.log_test_result("Базовое выполнение", success, details)
            
            if success:
                print(f"📋 Результат: {str(result)[:200]}...")
                
            return success, result, execution_time
            
        except Exception as e:
            self.log_test_result("Базовое выполнение", False, f"Exception: {str(e)}")
            return False, None, 0
    
    async def test_complex_task_decomposition(self):
        """Тест: Сложная задача с декомпозицией"""
        print("\n🔥 === ТЕСТ 2: СЛОЖНАЯ ЗАДАЧА С ДЕКОМПОЗИЦИЕЙ ===")
        
        task = "Создай полный веб-сайт с котятами: HTML, CSS и описанием трёх пород кошек с фотографиями"
        
        try:
            start_time = time.time()
            result = await self.orchestrator.execute_task(task)
            execution_time = time.time() - start_time
            
            # Проверки
            has_result = result is not None
            complex_enough = len(str(result)) > 500
            has_html = 'html' in str(result).lower() or '<' in str(result)
            reasonable_time = execution_time < 60.0
            
            success = has_result and complex_enough and has_html and reasonable_time
            
            details = f"({execution_time:.1f}s, {len(str(result))} символов, HTML: {has_html})"
            self.log_test_result("Сложная декомпозиция", success, details)
            
            if success:
                print(f"🌐 Результат содержит HTML: {has_html}")
                print(f"📊 Размер результата: {len(str(result))} символов")
                
            return success, result, execution_time
            
        except Exception as e:
            self.log_test_result("Сложная декомпозиция", False, f"Exception: {str(e)}")
            return False, None, 0
    
    async def test_agent_collaboration(self):
        """Тест: Совместная работа агентов"""
        print("\n🔥 === ТЕСТ 3: СОВМЕСТНАЯ РАБОТА АГЕНТОВ ===")
        
        task = "Проанализируй данные о продажах [100, 150, 200, 120, 300] и создай красивый отчёт с выводами"
        
        try:
            start_time = time.time()
            result = await self.orchestrator.execute_task(task)
            execution_time = time.time() - start_time
            
            # Проверки
            has_result = result is not None
            has_analysis = any(word in str(result).lower() for word in ['анализ', 'вывод', 'тренд', 'рост'])
            has_numbers = any(num in str(result) for num in ['100', '150', '200', '120', '300'])
            reasonable_time = execution_time < 45.0
            
            success = has_result and has_analysis and has_numbers and reasonable_time
            
            details = f"({execution_time:.1f}s, анализ: {has_analysis}, данные: {has_numbers})"
            self.log_test_result("Совместная работа", success, details)
            
            if success:
                print(f"📊 Анализ найден: {has_analysis}")
                print(f"🔢 Данные использованы: {has_numbers}")
                
            return success, result, execution_time
            
        except Exception as e:
            self.log_test_result("Совместная работа", False, f"Exception: {str(e)}")
            return False, None, 0
    
    async def test_self_improvement_integration(self):
        """Тест: Интеграция с системой самообучения"""
        print("\n🔥 === ТЕСТ 4: СИСТЕМА САМООБУЧЕНИЯ ===")
        
        try:
            # Эмулируем несколько выполнений для сбора данных
            tasks = [
                "Посчитай 2+2",
                "Объясни что такое Python",
                "Создай список покупок на неделю"
            ]
            
            agent_id = "test_agent"
            
            for i, task in enumerate(tasks):
                # Эмулируем выполнение с разным качеством
                quality_score = 0.8 + (i * 0.05)  # Постепенное улучшение
                
                await self.self_learning.record_agent_execution(
                    agent_id=agent_id,
                    task_id=f"test_task_{i}",
                    input_data={"task": task},
                    output=f"Результат задачи {i+1}",
                    execution_time=1.0 + i * 0.2,
                    success=True,
                    quality_score=quality_score
                )
            
            # Получить план улучшений
            improvement_plan = await self.self_learning.get_agent_improvement_plan(agent_id)
            
            # Проверки
            has_plan = improvement_plan['status'] == 'analyzed'
            has_stats = improvement_plan['learning_statistics']['total_feedback'] == 3
            has_examples = len(improvement_plan['few_shot_examples']) > 0
            
            success = has_plan and has_stats and has_examples
            
            details = f"(план: {has_plan}, статистика: {has_stats}, примеры: {has_examples})"
            self.log_test_result("Система самообучения", success, details)
            
            if success:
                stats = improvement_plan['learning_statistics']
                print(f"📊 Feedback: {stats['total_feedback']}, средний балл: {stats['avg_score']:.2f}")
                print(f"🎯 Few-shot примеров: {len(improvement_plan['few_shot_examples'])}")
                
            return success
            
        except Exception as e:
            self.log_test_result("Система самообучения", False, f"Exception: {str(e)}")
            return False
    
    async def test_memory_persistence(self):
        """Тест: Память и персистентность"""
        print("\n🔥 === ТЕСТ 5: ПАМЯТЬ И ПЕРСИСТЕНТНОСТЬ ===")
        
        try:
            # Проверить коллективную память
            collective_memory = self.orchestrator.collective_memory
            
            # Добавить воспоминание
            memory_data = {
                "task": "Тестовая задача",
                "result": "Успешный результат",
                "agent": "test_agent",
                "context": {"test": True}
            }
            
            await collective_memory.add_memory("test_agent", memory_data)
            
            # Поиск воспоминаний
            memories = await collective_memory.search_memories("тестовая")
            
            # Проверки
            memory_added = len(memories) > 0
            memory_content = any("тестовая" in str(mem).lower() for mem in memories)
            
            success = memory_added and memory_content
            
            details = f"(воспоминаний: {len(memories)}, релевантных: {memory_content})"
            self.log_test_result("Память", success, details)
            
            if success:
                print(f"🧠 Найдено воспоминаний: {len(memories)}")
                
            return success
            
        except Exception as e:
            self.log_test_result("Память", False, f"Exception: {str(e)}")
            return False
    
    async def test_error_handling(self):
        """Тест: Обработка ошибок"""
        print("\n🔥 === ТЕСТ 6: ОБРАБОТКА ОШИБОК ===")
        
        try:
            # Задача с потенциальной ошибкой
            impossible_task = "Подели на ноль и объясни результат математически"
            
            start_time = time.time()
            result = await self.orchestrator.execute_task(impossible_task)
            execution_time = time.time() - start_time
            
            # Проверки - система должна обработать ошибку изящно
            has_result = result is not None
            not_crashed = True  # Если дошли сюда, не упали
            reasonable_time = execution_time < 30.0
            error_handled = "ошибк" in str(result).lower() or "невозможно" in str(result).lower()
            
            success = has_result and not_crashed and reasonable_time
            
            details = f"({execution_time:.1f}s, обработка ошибок: {error_handled})"
            self.log_test_result("Обработка ошибок", success, details)
            
            if success:
                print(f"🛡️ Система не упала при некорректной задаче")
                
            return success
            
        except Exception as e:
            # Неожиданное исключение - это плохо
            self.log_test_result("Обработка ошибок", False, f"Unexpected exception: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Запустить все E2E тесты"""
        print("🚀 === ЗАПУСК E2E ТЕСТОВ KITTYCORE 3.0 ===")
        print(f"🕐 Время начала: {datetime.now().strftime('%H:%M:%S')}")
        print("🎯 Цель: проверить всю систему в боевых условиях БЕЗ МОКОВ\n")
        
        overall_start = time.time()
        
        # Запускаем все тесты
        await self.test_basic_task_execution()
        await self.test_complex_task_decomposition()
        await self.test_agent_collaboration()
        await self.test_self_improvement_integration()
        await self.test_memory_persistence()
        await self.test_error_handling()
        
        overall_time = time.time() - overall_start
        
        # Финальный отчёт
        print(f"\n🏁 === ИТОГОВЫЙ ОТЧЁТ E2E ТЕСТОВ ===")
        print(f"⏱️  Общее время выполнения: {overall_time:.1f} секунд")
        print(f"📊 Всего тестов: {self.total_tests}")
        print(f"✅ Прошли: {self.passed_tests}")
        print(f"❌ Провалены: {self.failed_tests}")
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        print(f"📈 Процент успеха: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 ОТЛИЧНЫЙ РЕЗУЛЬТАТ! Система работает надёжно!")
        elif success_rate >= 60:
            print("👍 ХОРОШИЙ РЕЗУЛЬТАТ! Есть место для улучшений")
        else:
            print("⚠️ НУЖНА РАБОТА! Система требует доработки")
        
        # Получить обзор системы
        system_overview = self.self_learning.get_system_overview()
        print(f"\n🌐 СОСТОЯНИЕ СИСТЕМЫ:")
        print(f"🏥 Статус: {system_overview['system_status']}")
        print(f"📊 Здоровье: {system_overview['system_health_score']:.2f}")
        print(f"🤖 Агентов с данными: {system_overview['agents']['with_feedback']}")
        
        return success_rate >= 80

async def main():
    """Главная функция для запуска E2E тестов"""
    
    # Проверяем переменные окружения
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("⚠️ ПРЕДУПРЕЖДЕНИЕ: OPENROUTER_API_KEY не найден!")
        print("🔧 Система будет работать в ограниченном режиме")
        print()
    
    tester = KittyCoreE2ETester()
    success = await tester.run_all_tests()
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit_code = 0 if result else 1
        print(f"\n🏁 Завершение с кодом: {exit_code}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1) 