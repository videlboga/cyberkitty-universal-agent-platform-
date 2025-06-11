#!/usr/bin/env python3
"""
🐱 KittyCore 3.0 CLI со SmartValidator
=====================================

Интерактивный CLI с умной LLM-валидацией результатов:
- Оценка с позиции конечной пользы для пользователя
- "Получил ли пользователь то, что просил?"
- Честная оценка готовности результата к использованию
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Добавляем kittycore в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from kittycore.core.orchestrator import OrchestratorAgent
from agents.smart_validator import SmartValidator, validate_task_result
from kittycore.visualization.mermaid_generator import generate_mermaid_workflow


def print_banner():
    """Красивый баннер"""
    print("\n🐱 KittyCore 3.0 CLI - SmartValidator Edition")
    print("=" * 50)
    print("Отправь запрос и получи УМНО ПРОВЕРЕННОЕ решение!")
    print("🧠 Система качества: LLM-валидация конечной пользы")
    print("Введи 'exit' для выхода")


def collect_created_files(directory: str = ".") -> list:
    """Собирает список недавно созданных файлов"""
    try:
        current_time = time.time()
        recent_files = []
        
        for root, dirs, files in os.walk(directory):
            # Пропускаем скрытые папки и системные
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    # Файлы созданные за последние 10 секунд
                    if current_time - os.path.getctime(file_path) < 10:
                        recent_files.append(file_path)
                except:
                    continue
        
        return recent_files
    except Exception:
        return []


async def main():
    """Основная функция CLI"""
    print_banner()
    
    orchestrator = OrchestratorAgent()
    smart_validator = SmartValidator()
    
    while True:
        try:
            user_input = input("💬 Твой запрос: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'выход']:
                print("👋 До свидания!")
                break
                
            if not user_input:
                continue
            
            print(f"\n🔍 Обрабатываю запрос: {user_input}")
            print("=" * 50)
            
            # Засекаем время выполнения
            start_time = time.time()
            
            # Собираем файлы до выполнения
            files_before = set(collect_created_files())
            
            # Выполняем задачу
            result = await orchestrator.process_request(user_input)
            
            execution_time = time.time() - start_time
            
            # Собираем новые файлы
            files_after = set(collect_created_files())
            new_files = list(files_after - files_before)
            
            # Базовый отчет
            print(f"✅ Задача решена за {execution_time:.2f}с")
            print(f"📊 Сложность: {result.get('complexity', 'неизвестно')}")
            print(f"👥 Команда: {result.get('team_size', 0)} агентов")
            
            if result.get('decomposition'):
                print("📋 План решения:")
                for i, task in enumerate(result['decomposition'], 1):
                    print(f"   {i}. {task}")
            
            # Визуализация workflow
            if result.get('workflow_graph'):
                print("📈 Workflow:")
                mermaid_code = generate_mermaid_workflow(result['workflow_graph'])
                print(mermaid_code)
            
            # 🧠 УМНАЯ ВАЛИДАЦИЯ КАЧЕСТВА
            print("\n🧠 ЗАПУСК УМНОЙ ВАЛИДАЦИИ...")
            validation_start = time.time()
            
            validation_result = await smart_validator.validate_result(
                original_task=user_input,
                result=result,
                created_files=new_files
            )
            
            validation_time = time.time() - validation_start
            
            # Отчет по валидации
            print(f"\n🔍 ВАЛИДАЦИЯ ЗАВЕРШЕНА ({validation_time:.2f}с)")
            print(f"📊 Оценка качества: {validation_result.score:.1f}/1.0")
            print(f"🎯 {validation_result.verdict}")
            print(f"💰 Польза для пользователя: {validation_result.user_benefit}")
            
            if validation_result.issues:
                print("⚠️  Найденные проблемы:")
                for issue in validation_result.issues:
                    print(f"   • {issue}")
            
            if validation_result.recommendations:
                print("💡 Рекомендации:")
                for rec in validation_result.recommendations:
                    print(f"   • {rec}")
            
            # Статус с учетом валидации
            if validation_result.is_valid:
                print("\n✅ КАЧЕСТВО ПОДТВЕРЖДЕНО - результат готов к использованию!")
            else:
                print("\n❌ КАЧЕСТВО НЕ СООТВЕТСТВУЕТ - результат требует доработки!")
            
            # Информация о файлах
            if new_files:
                print(f"\n📁 СОЗДАННЫЕ ФАЙЛЫ ({len(new_files)}):")
                for file_path in new_files:
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    print(f"   📄 {file_path} ({file_size} байт)")
            else:
                print("\n📁 СОЗДАННЫЕ ФАЙЛЫ:")
                print("   (файлы не создавались)")
            
            # Дополнительная информация
            if result.get('agent_actions'):
                print("\n🔧 ВЫПОЛНЕННЫЕ ДЕЙСТВИЯ:")
                for action in result['agent_actions']:
                    print(f"   ✅ {action}")
            
            # Коллективная память
            if hasattr(orchestrator, 'collective_memory') and orchestrator.collective_memory:
                memory_stats = orchestrator.collective_memory.get_memory_stats()
                print(f"\n🧠 КОЛЛЕКТИВНАЯ ПАМЯТЬ:")
                print(f"   📝 Записей: {memory_stats.get('total_entries', 0)}")
                print(f"   👥 Агентов: {memory_stats.get('agents_count', 0)}")
            
            # Самообучение
            if hasattr(orchestrator, 'self_improvement') and orchestrator.self_improvement:
                improvement_stats = orchestrator.self_improvement.get_performance_stats()
                print(f"\n🚀 САМООБУЧЕНИЕ:")
                print(f"   📊 Всего задач: {improvement_stats.get('total_tasks', 0)}")
                print(f"   ⚡ Средняя эффективность: {improvement_stats.get('avg_efficiency', 0.0):.2f}")
            
            print("=" * 50)
            
        except KeyboardInterrupt:
            print("\n\n👋 Программа прервана пользователем")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            print(f"🔍 Подробности: {traceback.format_exc()}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!") 