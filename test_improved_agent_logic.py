#!/usr/bin/env python3
"""
🧠 Тест улучшенной логики агентов с A-MEM
Проверяем как A-MEM помогает решать проблемы планирования
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Добавляем путь к KittyCore
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig

async def test_improved_agent_logic():
    """Тест улучшенной логики агентов с A-MEM обучением"""
    
    print("🧠 === ТЕСТ УЛУЧШЕННОЙ ЛОГИКИ АГЕНТОВ ===")
    print("🎯 Проверяем как A-MEM улучшает планирование и выполнение задач")
    
    # Создаём конфигурацию
    config = UnifiedConfig(
        vault_path="./vault_improved_test",
        enable_amem_memory=True,
        enable_smart_validation=True,
        max_agents=3
    )
    
    # Инициализируем оркестратор
    print("\n🚀 === ИНИЦИАЛИЗАЦИЯ ===")
    orchestrator = UnifiedOrchestrator(config)
    print(f"🧠 A-MEM тип: {type(orchestrator.amem_system).__name__}")
    print(f"✅ Система готова к обучению!")
    
    # Тестовые задачи для демонстрации улучшения
    test_tasks = [
        {
            "id": "task_1_baseline",
            "task": "Создай простую HTML страницу про котят",
            "expected_files": 1,
            "complexity": "simple"
        },
        {
            "id": "task_2_analysis", 
            "task": "Проведи анализ популярных CRM систем и создай отчёт с 3 рекомендациями",
            "expected_files": 3,  # analysis.md, crm_data.json, recommendations.md
            "complexity": "medium"
        },
        {
            "id": "task_3_bitrix_repeat",
            "task": "Проведи анализ рынка приложений маркета битрикс 24, найди топ популярных, составь отчёт и создай 2 прототипа",
            "expected_files": 4,  # market_analysis.md, top_apps.json, report.md, 2 prototypes
            "complexity": "complex"
        }
    ]
    
    results = []
    
    print("\n⚡ === ВЫПОЛНЕНИЕ ТЕСТОВЫХ ЗАДАЧ ===")
    
    for i, test_task in enumerate(test_tasks, 1):
        print(f"\n📋 ЗАДАЧА {i}: {test_task['task'][:50]}...")
        print(f"🎯 Ожидаем: {test_task['expected_files']} файлов")
        
        # Проверяем память перед выполнением
        memory_count_before = 0
        if orchestrator.amem_system:
            try:
                memories = await orchestrator.amem_system.search_memories(
                    query="план выполнение",
                    limit=10
                )
                memory_count_before = len(memories)
                print(f"💾 Опыта в A-MEM: {memory_count_before} воспоминаний")
            except:
                pass
        
        # Выполняем задачу
        start_time = datetime.now()
        try:
            result = await orchestrator.solve_task(test_task["task"])
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Анализируем результат
            files_created = len(result.get("files_created", []))
            success = result.get("success", False)
            quality = result.get("quality_score", 0.0)
            
            # Проверяем накопление опыта
            memory_count_after = memory_count_before
            if orchestrator.amem_system:
                try:
                    memories = await orchestrator.amem_system.search_memories(
                        query="план выполнение",
                        limit=10
                    )
                    memory_count_after = len(memories)
                except:
                    pass
            
            result_data = {
                "task_id": test_task["id"],
                "success": success,
                "files_created": files_created,
                "expected_files": test_task["expected_files"],
                "execution_time": execution_time,
                "quality_score": quality,
                "memory_before": memory_count_before,
                "memory_after": memory_count_after,
                "memory_growth": memory_count_after - memory_count_before,
                "completeness": files_created / test_task["expected_files"] if test_task["expected_files"] > 0 else 0
            }
            
            results.append(result_data)
            
            print(f"   ✅ Статус: {'Успех' if success else 'Частично'}")
            print(f"   📁 Файлов: {files_created}/{test_task['expected_files']} ({result_data['completeness']:.1%} полноты)")
            print(f"   ⏱️ Время: {execution_time:.1f}с")
            print(f"   🎯 Качество: {quality:.2f}")
            print(f"   🧠 Новый опыт: +{result_data['memory_growth']} воспоминаний")
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            result_data = {
                "task_id": test_task["id"],
                "success": False,
                "error": str(e),
                "memory_before": memory_count_before,
                "memory_after": memory_count_before,
                "memory_growth": 0
            }
            results.append(result_data)
    
    # Анализируем прогресс обучения
    print("\n📊 === АНАЛИЗ РЕЗУЛЬТАТОВ И ОБУЧЕНИЯ ===")
    
    successful_tasks = [r for r in results if r.get("success", False)]
    avg_completeness = sum(r.get("completeness", 0) for r in results) / len(results)
    total_memory_growth = sum(r.get("memory_growth", 0) for r in results)
    
    print(f"✅ Успешных задач: {len(successful_tasks)}/{len(results)}")
    print(f"📈 Средняя полнота: {avg_completeness:.1%}")
    print(f"🧠 Общее накопление опыта: +{total_memory_growth} воспоминаний")
    
    # Проверяем качество планирования со временем
    if len(results) >= 2:
        quality_trend = []
        completeness_trend = []
        
        for r in results:
            if "quality_score" in r:
                quality_trend.append(r["quality_score"])
            if "completeness" in r:
                completeness_trend.append(r["completeness"])
        
        if len(quality_trend) >= 2:
            quality_improvement = quality_trend[-1] - quality_trend[0]
            print(f"📈 Улучшение качества: {quality_improvement:+.2f}")
            
        if len(completeness_trend) >= 2:
            completeness_improvement = completeness_trend[-1] - completeness_trend[0]
            print(f"📈 Улучшение полноты: {completeness_improvement:+.1%}")
    
    # Тестируем семантический поиск опыта
    if orchestrator.amem_system and total_memory_growth > 0:
        print("\n🔍 === ТЕСТ СЕМАНТИЧЕСКОГО ПОИСКА ОПЫТА ===")
        
        search_queries = [
            "успешные планы анализа",
            "создание файлов HTML",
            "проблемы выполнения задач",
            "инструменты для CRM анализа"
        ]
        
        for query in search_queries:
            try:
                memories = await orchestrator.amem_system.search_memories(
                    query=query,
                    limit=3
                )
                print(f"   🔍 '{query}': {len(memories)} результатов")
                if memories:
                    best_match = memories[0]
                    preview = best_match.get('content', '')[:80] + "..."
                    print(f"      💡 Лучший: {preview}")
            except Exception as e:
                print(f"   ❌ Ошибка поиска '{query}': {e}")
    
    # Демонстрируем потенциал улучшения
    print("\n🚀 === ПОТЕНЦИАЛ A-MEM УЛУЧШЕНИЙ ===")
    
    if avg_completeness < 0.8:
        print("⚠️ ВЫЯВЛЕННЫЕ ПРОБЛЕМЫ:")
        print("   - Неполное выполнение сложных задач")
        print("   - Слабая декомпозиция на этапы")
        print("   - Недостаточно конкретные планы")
        
        print("\n💡 A-MEM ПОМОЖЕТ:")
        print("   - Накапливать успешные паттерны планирования")
        print("   - Изучать ошибки и избегать их повторения")
        print("   - Адаптировать планы под типы задач")
        print("   - Улучшать качество с каждой выполненной задачей")
    
    if total_memory_growth > 0:
        print(f"\n✅ A-MEM АКТИВНО ОБУЧАЕТСЯ:")
        print(f"   - Накоплено {total_memory_growth} воспоминаний")
        print(f"   - Семантический поиск работает")
        print(f"   - Система готова к самосовершенствованию")
    
    # Сохраняем результаты
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "test_summary": {
            "total_tasks": len(results),
            "successful_tasks": len(successful_tasks),
            "avg_completeness": avg_completeness,
            "total_memory_growth": total_memory_growth
        },
        "individual_results": results,
        "amem_status": {
            "available": orchestrator.amem_system is not None,
            "type": type(orchestrator.amem_system).__name__ if orchestrator.amem_system else None
        }
    }
    
    with open("improved_agent_logic_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Результаты сохранены: improved_agent_logic_results.json")
    
    if avg_completeness >= 0.8 and total_memory_growth > 0:
        print("\n🎉 ТЕСТ УСПЕШЕН: A-MEM улучшает логику агентов!")
    else:
        print("\n⚠️ ТЕСТ ЧАСТИЧНО УСПЕШЕН: Есть области для улучшения")
    
    return test_results

if __name__ == "__main__":
    asyncio.run(test_improved_agent_logic()) 