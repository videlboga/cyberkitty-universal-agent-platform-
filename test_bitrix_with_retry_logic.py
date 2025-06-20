#!/usr/bin/env python3
"""
🔄 Тест Битрикс24 анализа с механизмом повторного выполнения
Система будет повторять выполнение при плохих результатах до достижения цели
"""

import asyncio
import sys
import os
from datetime import datetime
import json

# Добавляем путь к KittyCore
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig

async def test_bitrix_with_retry():
    """Тест с механизмом повторного выполнения"""
    
    print("🔄 === ТЕСТ БИТРИКС24 С RETRY ЛОГИКОЙ ===")
    print("🎯 Задача: Полный анализ + 3 прототипа")
    print("🔄 Механизм: Повторное выполнение до достижения качественного результата\n")
    
    # Задача
    task = "Проведи анализ рынка приложений маркета битрикс 24, найди топ популярных, составь отчёт о том, какие там есть, насколько они сложны в реализации и какие проблемы имеют. После сделай 3 прототипа приложений на основе этого анализа - которые можно сделать быстро с улучшением UX"
    
    # Создаём конфигурацию с улучшениями
    config = UnifiedConfig(
        vault_path="./vault_bitrix_retry",
        enable_amem_memory=True,
        enable_smart_validation=True,  # Включаем валидацию для повторов
        max_agents=3
    )
    
    # Инициализируем оркестратор
    orchestrator = UnifiedOrchestrator(config)
    print(f"🧠 A-MEM: {type(orchestrator.amem_system).__name__}")
    
    # Критерии успеха
    success_criteria = {
        "min_files": 4,  # Минимум 4 файла (отчёт + 3 прототипа)
        "min_quality": 0.7,  # Минимальное качество
        "required_content": ["анализ", "прототип", "битрикс", "UX"],
        "min_total_size": 2000  # Минимальный размер контента
    }
    
    max_attempts = 3
    attempt = 1
    
    while attempt <= max_attempts:
        print(f"\n🔄 === ПОПЫТКА {attempt}/{max_attempts} ===")
        start_time = datetime.now()
        
        try:
            # Проверяем A-MEM перед выполнением
            if orchestrator.amem_system:
                try:
                    memories = await orchestrator.amem_system.search_memories("битрикс анализ прототип", limit=5)
                    print(f"🧠 A-MEM перед выполнением: {len(memories)} релевантных воспоминаний")
                    
                    if memories and attempt > 1:
                        print("💡 Используем накопленный опыт:")
                        for i, memory in enumerate(memories[:2], 1):
                            preview = memory.get('content', '')[:100] + "..."
                            print(f"   {i}. {preview}")
                        print()
                        
                except Exception as e:
                    print(f"⚠️ Ошибка чтения A-MEM: {e}")
            
            # Выполняем задачу
            print(f"🚀 Запуск выполнения...")
            result = await orchestrator.solve_task(task)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Анализируем результат
            quality_score = result.get('quality_score', 0.0)
            files_created = result.get('files_created', [])
            status = result.get('status', 'unknown')
            
            print(f"\n📊 === РЕЗУЛЬТАТЫ ПОПЫТКИ {attempt} ===")
            print(f"   ⏱️ Время: {execution_time:.1f}с")
            print(f"   📁 Файлов: {len(files_created)}")
            print(f"   🎯 Качество: {quality_score:.2f}")
            print(f"   📝 Статус: {status}")
            
            if files_created:
                print(f"   📂 Созданные файлы:")
                for file_path in files_created[:10]:  # Показываем первые 10
                    print(f"      - {file_path}")
            
            # Детальная проверка качества
            quality_check = await evaluate_result_quality(files_created, success_criteria)
            
            print(f"\n🔍 === ПРОВЕРКА КАЧЕСТВА ===")
            print(f"   📁 Файлов: {quality_check['files_count']}/{success_criteria['min_files']} ✅" if quality_check['files_count'] >= success_criteria['min_files'] else f"   📁 Файлов: {quality_check['files_count']}/{success_criteria['min_files']} ❌")
            print(f"   🎯 Качество: {quality_score:.2f}/{success_criteria['min_quality']} ✅" if quality_score >= success_criteria['min_quality'] else f"   🎯 Качество: {quality_score:.2f}/{success_criteria['min_quality']} ❌")
            print(f"   📝 Контент: {quality_check['content_size']} символов ✅" if quality_check['content_size'] >= success_criteria['min_total_size'] else f"   📝 Контент: {quality_check['content_size']} символов ❌")
            print(f"   🔑 Ключевые слова: {quality_check['keywords_found']}/{len(success_criteria['required_content'])} ✅" if quality_check['keywords_found'] >= len(success_criteria['required_content'])/2 else f"   🔑 Ключевые слова: {quality_check['keywords_found']}/{len(success_criteria['required_content'])} ❌")
            
            # Проверяем успех
            is_success = (
                quality_check['files_count'] >= success_criteria['min_files'] and
                quality_score >= success_criteria['min_quality'] and
                quality_check['content_size'] >= success_criteria['min_total_size'] and
                quality_check['keywords_found'] >= len(success_criteria['required_content'])/2
            )
            
            if is_success:
                print(f"\n🎉 === УСПЕХ НА ПОПЫТКЕ {attempt}! ===")
                print("✅ Все критерии выполнены!")
                
                # Проверяем A-MEM после успешного выполнения
                if orchestrator.amem_system:
                    try:
                        memories_after = await orchestrator.amem_system.search_memories("битрикс анализ", limit=10)
                        print(f"🧠 A-MEM после выполнения: {len(memories_after)} воспоминаний")
                        print("💡 Система накопила новый опыт для будущих задач!")
                    except Exception as e:
                        print(f"⚠️ Ошибка проверки A-MEM: {e}")
                
                return result
            
            else:
                print(f"\n⚠️ === ПОПЫТКА {attempt} НЕ УДАЛАСЬ ===")
                
                # Анализируем что пошло не так
                issues = []
                if quality_check['files_count'] < success_criteria['min_files']:
                    issues.append(f"Недостаточно файлов ({quality_check['files_count']} < {success_criteria['min_files']})")
                if quality_score < success_criteria['min_quality']:
                    issues.append(f"Низкое качество ({quality_score:.2f} < {success_criteria['min_quality']})")
                if quality_check['content_size'] < success_criteria['min_total_size']:
                    issues.append(f"Мало контента ({quality_check['content_size']} < {success_criteria['min_total_size']})")
                if quality_check['keywords_found'] < len(success_criteria['required_content'])/2:
                    issues.append(f"Отсутствуют ключевые элементы")
                
                print("❌ Проблемы:")
                for issue in issues:
                    print(f"   - {issue}")
                
                if attempt < max_attempts:
                    print(f"\n🔄 Готовимся к попытке {attempt + 1}...")
                    print("💡 A-MEM сохранит опыт этой попытки для улучшения следующей")
                    
                    # Небольшая пауза перед следующей попыткой
                    await asyncio.sleep(2)
                else:
                    print(f"\n❌ === ВСЕ {max_attempts} ПОПЫТКИ ИСЧЕРПАНЫ ===")
                    print("📊 Возвращаем лучший результат")
                    return result
        
        except Exception as e:
            print(f"\n❌ Ошибка на попытке {attempt}: {e}")
            if attempt < max_attempts:
                print(f"🔄 Попробуем ещё раз...")
                await asyncio.sleep(2)
            else:
                print("❌ Критическая ошибка, завершаем")
                return {"success": False, "error": str(e)}
        
        attempt += 1
    
    print("\n❌ Не удалось достичь целевого качества")
    return {"success": False, "attempts": max_attempts}

async def evaluate_result_quality(files_created, criteria):
    """Детальная оценка качества результата"""
    quality_data = {
        'files_count': len(files_created),
        'content_size': 0,
        'keywords_found': 0,
        'file_types': set()
    }
    
    # Проверяем содержимое файлов
    for file_path in files_created:
        try:
            # Определяем полный путь
            if not file_path.startswith('/'):
                full_path = os.path.join(os.getcwd(), file_path)
            else:
                full_path = file_path
            
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    quality_data['content_size'] += len(content)
                    
                    # Проверяем ключевые слова
                    content_lower = content.lower()
                    for keyword in criteria['required_content']:
                        if keyword.lower() in content_lower:
                            quality_data['keywords_found'] += 1
                
                # Определяем тип файла
                ext = os.path.splitext(file_path)[1]
                quality_data['file_types'].add(ext)
                
        except Exception as e:
            print(f"⚠️ Ошибка чтения файла {file_path}: {e}")
    
    return quality_data

if __name__ == "__main__":
    asyncio.run(test_bitrix_with_retry()) 