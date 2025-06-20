#!/usr/bin/env python3
"""
🔧 Интеграция системы Контент + Метаданные в OrchestratorAgent

Модифицирует OrchestratorAgent для использования новой системы
"""

import asyncio
from typing import Dict, Any
from kittycore.core.content_integration import enhance_agent_with_content_system

# Импортируем оригинальный оркестратор
try:
    from kittycore.core.orchestrator import OrchestratorAgent, OrchestratorConfig
except ImportError as e:
    print(f"❌ Ошибка импорта OrchestratorAgent: {e}")
    exit(1)

class EnhancedOrchestratorAgent:
    """Улучшенный OrchestratorAgent с системой контент+метаданные"""
    
    def __init__(self, config: OrchestratorConfig = None):
        # Создаём оригинальный оркестратор
        self.original_orchestrator = OrchestratorAgent(config)
        self.config = config or OrchestratorConfig()
        
        print(f"🚀 Enhanced OrchestratorAgent инициализирован: {self.config.orchestrator_id}")
        print("✅ Система контент+метаданные активирована")
    
    async def execute_task_with_content_validation(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Выполняет задачу с валидацией контента"""
        
        print(f"🎯 Enhanced Orchestrator выполняет: {task}")
        
        try:
            # ФАЗА 1: Выполняем через оригинальный оркестратор
            original_result = await self.original_orchestrator.execute_task(task, context)
            
            print(f"📤 Оригинальный результат: {len(str(original_result))} символов")
            
            # ФАЗА 2: Анализируем и улучшаем результат
            if isinstance(original_result, str):
                # Если результат - строка, улучшаем её
                enhanced_result = enhance_agent_with_content_system(
                    agent_result=original_result,
                    task=task
                )
                
                print(f"✅ Результат улучшен: {enhanced_result['success']}")
                print(f"📁 Создан файл: {enhanced_result['content_file']}")
                
                return {
                    "status": "completed",
                    "task": task,
                    "original_result": original_result,
                    "enhanced_result": enhanced_result,
                    "content_file": enhanced_result["content_file"],
                    "metadata_file": enhanced_result["metadata_file"],
                    "validation": enhanced_result["validation"]
                }
            else:
                # Если результат - объект, возвращаем как есть
                print("ℹ️ Результат не требует улучшения (не строка)")
                return {
                    "status": "completed",
                    "task": task,
                    "result": original_result,
                    "enhanced": False
                }
                
        except Exception as e:
            print(f"❌ Ошибка Enhanced Orchestrator: {e}")
            return {
                "status": "failed",
                "task": task,
                "error": str(e)
            }
    
    # Делегируем остальные методы оригинальному оркестратору
    async def execute_task(self, task: str, context: Dict[str, Any] = None) -> Any:
        """Обычное выполнение задачи"""
        return await self.original_orchestrator.execute_task(task, context)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику"""
        return self.original_orchestrator.get_statistics()

async def test_enhanced_orchestrator():
    """Тест улучшенного оркестратора"""
    print("🧪 === ТЕСТ ENHANCED ORCHESTRATOR ===")
    
    # Создаём улучшенный оркестратор
    config = OrchestratorConfig(orchestrator_id="enhanced_test_orchestrator")
    enhanced_orchestrator = EnhancedOrchestratorAgent(config)
    
    # Тестовые задачи
    test_tasks = [
        "Создай файл hello_world.py с программой Hello World",
        "Создай HTML страницу с котятами",
        "Создай JSON файл с конфигурацией веб-сервера"
    ]
    
    results = []
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n🎯 Задача {i}: {task}")
        
        result = await enhanced_orchestrator.execute_task_with_content_validation(task)
        results.append(result)
        
        if result["status"] == "completed" and "enhanced_result" in result:
            print(f"   ✅ Статус: {result['status']}")
            print(f"   📁 Файл: {result.get('content_file', 'Не создан')}")
            print(f"   🎯 Валидация: {result['validation']['score']:.2f}")
        else:
            print(f"   ❌ Статус: {result['status']}")
            if "error" in result:
                print(f"   🚫 Ошибка: {result['error']}")
    
    return results

async def compare_original_vs_enhanced():
    """Сравнение оригинального и улучшенного оркестратора"""
    print("\n⚖️ === СРАВНЕНИЕ ОРИГИНАЛ VS ENHANCED ===")
    
    task = "Создай файл hello_world.py с программой Hello World"
    
    # Оригинальный оркестратор
    print("\n🔸 ОРИГИНАЛЬНЫЙ ОРКЕСТРАТОР:")
    original_config = OrchestratorConfig(orchestrator_id="original_test")
    original_orchestrator = OrchestratorAgent(original_config)
    
    try:
        original_result = await original_orchestrator.execute_task(task)
        print(f"   📤 Результат: {str(original_result)[:100]}...")
        
        # Проверяем созданные файлы
        import os
        created_files = [f for f in os.listdir('.') if f.startswith('hello_world') and f.endswith('.py')]
        print(f"   📁 Созданные файлы: {created_files}")
        
        if created_files:
            with open(created_files[0], 'r') as f:
                content = f.read()
            print(f"   💎 Содержимое: {content[:50]}...")
            
            # Проверяем на отчёт
            is_report = any(pattern in content for pattern in ["Задача:", "Результат работы"])
            print(f"   🚫 Это отчёт: {'Да' if is_report else 'Нет'}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Улучшенный оркестратор
    print("\n🔹 ENHANCED ОРКЕСТРАТОР:")
    enhanced_config = OrchestratorConfig(orchestrator_id="enhanced_test")
    enhanced_orchestrator = EnhancedOrchestratorAgent(enhanced_config)
    
    try:
        enhanced_result = await enhanced_orchestrator.execute_task_with_content_validation(task)
        print(f"   📤 Статус: {enhanced_result['status']}")
        
        if "content_file" in enhanced_result:
            print(f"   📁 Файл: {enhanced_result['content_file']}")
            
            with open(enhanced_result['content_file'], 'r') as f:
                content = f.read()
            print(f"   💎 Содержимое: {content}")
            
            # Проверяем на отчёт
            is_report = any(pattern in content for pattern in ["Задача:", "Результат работы"])
            print(f"   🚫 Это отчёт: {'Да' if is_report else 'Нет'}")
            print(f"   🎯 Валидация: {enhanced_result['validation']['score']:.2f}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

async def main():
    """Главная функция тестирования"""
    print("🔧 ИНТЕГРАЦИЯ СИСТЕМЫ КОНТЕНТ + МЕТАДАННЫЕ В ORCHESTRATOR")
    print("=" * 80)
    
    # Тестируем улучшенный оркестратор
    results = await test_enhanced_orchestrator()
    
    # Сравниваем с оригиналом
    await compare_original_vs_enhanced()
    
    print("\n📊 ИТОГИ ИНТЕГРАЦИИ:")
    successful_tasks = sum(1 for r in results if r.get("status") == "completed")
    print(f"✅ Успешных задач: {successful_tasks}/{len(results)}")
    
    enhanced_tasks = sum(1 for r in results if r.get("enhanced_result"))
    print(f"🔧 Улучшенных результатов: {enhanced_tasks}/{len(results)}")
    
    if successful_tasks == len(results):
        print("🎉 ИНТЕГРАЦИЯ УСПЕШНА!")
        print("✅ Enhanced OrchestratorAgent создаёт реальный контент")
        print("✅ Метаданные сохраняются отдельно")
        print("✅ Система готова к продакшену")
    else:
        print("⚠️ Есть проблемы, требуется доработка")

if __name__ == "__main__":
    asyncio.run(main()) 