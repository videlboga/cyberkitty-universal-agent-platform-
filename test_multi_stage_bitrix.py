#!/usr/bin/env python3
"""
🚀 ТЕСТ МНОГОЭТАПНОГО ПЛАНИРОВАНИЯ KITTYCORE 3.0

Проверяем революционную систему Agile планирования для анализа рынка Битрикс24
"""

import asyncio
import json
from datetime import datetime
from kittycore.agents.intellectual_agent import IntellectualAgent

async def test_multi_stage_bitrix_analysis():
    """Тест многоэтапного анализа рынка Битрикс24"""
    
    print("🚀 === ТЕСТ МНОГОЭТАПНОГО ПЛАНИРОВАНИЯ KITTYCORE 3.0 ===")
    print("🎯 Задача: Глубокий анализ рынка приложений Битрикс24 с Agile подходом")
    print()
    
    # Задача с высокой сложностью для активации многоэтапного планирования
    task_description = """Проведи комплексный анализ рынка приложений Битрикс24. 
    
ТРЕБОВАНИЯ:
1. Исследуй реальные приложения в маркетплейсе (не сам Битрикс24)
2. Найди топ-10 популярных сторонних приложений
3. Проанализируй их функционал, цены, отзывы пользователей
4. Оцени сложность разработки аналогичных решений  
5. Выяви основные проблемы пользователей в отзывах
6. Создай 3 КОНКРЕТНЫХ прототипа новых приложений с улучшенным UX
7. Каждый прототип должен решать реальную проблему пользователей
8. Добавь техническое описание реализации прототипов"""
    
    # Создаём агента
    subtask = {
        "description": task_description,
        "complexity": "complex",  # Принудительно устанавливаем высокую сложность
        "expected_output": "Детальный анализ + 3 работающих прототипа"
    }
    
    agent = IntellectualAgent(role="market_analyst", subtask=subtask)
    
    print("🧠 === АНАЛИЗ ЗАДАЧИ ===")
    
    # Анализируем задачу
    analysis = await agent._analyze_task_with_llm(task_description)
    
    # 🚀 ПРИНУДИТЕЛЬНО устанавливаем высокую сложность для теста
    analysis['complexity'] = 'complex'  # Форсируем многоэтапное планирование
    
    print(f"📊 Тип задачи: {analysis.get('task_type', 'unknown')}")
    print(f"📊 Сложность: {analysis.get('complexity', 'unknown')} (принудительно установлена)")
    print(f"🔧 Инструменты: {analysis.get('chosen_tools', [])}")
    print()
    
    print("🚀 === СОЗДАНИЕ МНОГОЭТАПНОГО ПЛАНА ===")
    
    # Создаём план
    plan = await agent._create_execution_plan(task_description, analysis)
    plan_type = plan.get("type", "unknown")
    
    if plan_type == "multi_stage":
        stages = plan.get("stages", [])
        print(f"🎉 МНОГОЭТАПНЫЙ ПЛАН создан: {len(stages)} этапов")
        
        for i, stage in enumerate(stages, 1):
            stage_type = stage.get("stage_type", "unknown")
            action = stage.get("action", "Неизвестное действие")
            tool = stage.get("tool", "unknown")
            print(f"   ЭТАП {i}: {stage_type.upper()} | {action[:50]}... | {tool}")
    else:
        print(f"⚠️  Создан план типа: {plan_type}")
    
    print()
    print("⚡ === ВЫПОЛНЕНИЕ ПЛАНА ===")
    
    # Выполняем план
    start_time = datetime.now()
    result = await agent._execute_plan(plan, task_description)
    end_time = datetime.now()
    
    execution_time = (end_time - start_time).total_seconds()
    
    print()
    print("📊 === РЕЗУЛЬТАТЫ ВЫПОЛНЕНИЯ ===")
    print(f"✅ Успешность: {result.get('success', False)}")
    print(f"⏱️  Время выполнения: {execution_time:.2f}с")
    print(f"📋 Тип выполнения: {result.get('execution_type', 'unknown')}")
    
    if result.get('execution_type') == 'multi_stage':
        stage_results = result.get('stage_results', {})
        print(f"🚀 Этапов выполнено: {len(stage_results)}")
        
        for stage_type, stage_result in stage_results.items():
            success = stage_result.get('success', False)
            files = stage_result.get('created_files', [])
            print(f"   {stage_type.upper()}: {'✅' if success else '❌'} ({len(files)} файлов)")
    
    # Файлы
    created_files = result.get('created_files', [])
    print(f"📁 Создано файлов: {len(created_files)}")
    
    if created_files:
        print("\n📄 === СОЗДАННЫЕ ФАЙЛЫ ===")
        for i, file_path in enumerate(created_files[:10], 1):  # Показываем первые 10
            print(f"   {i}. {file_path}")
        
        if len(created_files) > 10:
            print(f"   ... и ещё {len(created_files) - 10} файлов")
    
    # Анализ качества контента
    print()
    print("🔍 === АНАЛИЗ КАЧЕСТВА РЕЗУЛЬТАТОВ ===")
    
    avg_quality = 0
    if created_files:
        # Проверяем несколько ключевых файлов
        import os
        quality_score = 0
        total_checks = 0
        
        for file_path in created_files[:5]:  # Проверяем первые 5 файлов
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    total_checks += 1
                    file_score = 0
                    
                    # Проверяем качество контента
                    if len(content) > 100:  # Достаточный объём
                        file_score += 1
                    
                    if any(keyword in content.lower() for keyword in ['битрикс', 'приложение', 'маркет']):
                        file_score += 1  # Релевантность теме
                    
                    if any(keyword in content.lower() for keyword in ['цена', 'рейтинг', 'пользователи']):
                        file_score += 1  # Конкретные данные
                    
                    quality_score += file_score / 3  # Нормализуем к 0-1
                    
                    print(f"   📄 {os.path.basename(file_path)}: {file_score}/3 баллов ({len(content)} символов)")
                
                except Exception as e:
                    print(f"   ❌ Ошибка чтения {file_path}: {e}")
        
        if total_checks > 0:
            avg_quality = quality_score / total_checks
            print(f"\n🎯 Средняя оценка качества: {avg_quality:.2f}/1.0")
            
            if avg_quality >= 0.8:
                print("🏆 ОТЛИЧНОЕ качество результатов!")
            elif avg_quality >= 0.6:
                print("✅ ХОРОШЕЕ качество результатов")
            elif avg_quality >= 0.4:
                print("⚠️  СРЕДНЕЕ качество результатов")
            else:
                print("❌ НИЗКОЕ качество результатов")
    
    print()
    print("🎊 === ИТОГОВАЯ ОЦЕНКА МНОГОЭТАПНОГО ПЛАНИРОВАНИЯ ===")
    
    if plan_type == "multi_stage" and result.get('success'):
        print("🚀 РЕВОЛЮЦИОННЫЙ УСПЕХ!")
        print("✅ Многоэтапное планирование работает")
        print("✅ Agile подход реализован")
        print("✅ Качественные результаты получены")
    elif plan_type == "multi_stage":
        print("🔧 ЧАСТИЧНЫЙ УСПЕХ")
        print("✅ Многоэтапное планирование активировано")
        print("❌ Выполнение имеет проблемы")
    else:
        print("⚠️  ОБЫЧНОЕ ПЛАНИРОВАНИЕ")
        print("❌ Многоэтапный план не создался")
        print("💡 Возможно, сложность задачи определена неверно")
    
    # Сохраняем детальный отчёт
    report = {
        "timestamp": datetime.now().isoformat(),
        "task": task_description,
        "analysis": analysis,
        "plan_type": plan_type,
        "execution_result": result,
        "execution_time": execution_time,
        "created_files": created_files,
        "quality_assessment": {
            "avg_quality": avg_quality,
            "total_files": len(created_files),
            "plan_type_success": plan_type == "multi_stage"
        }
    }
    
    with open("multi_stage_test_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Детальный отчёт сохранён: multi_stage_test_results.json")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_multi_stage_bitrix_analysis()) 