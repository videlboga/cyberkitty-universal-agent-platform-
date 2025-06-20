#!/usr/bin/env python3
"""
🔄 Быстрый демо retry логики на простой задаче
"""

import asyncio
import sys
import os
from datetime import datetime

# Добавляем путь к KittyCore
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig

async def test_retry_demo():
    """Демо retry механизма на простой задаче"""
    
    print("🔄 === DEMO RETRY ЛОГИКИ ===")
    print("🎯 Задача: Создание нескольких файлов")
    print("🔄 Механизм: Повторение до достижения всех требований\n")
    
    # Простая но требовательная задача
    task = "Создай файл hello.py с print('Hello World'), файл config.json с настройками и файл readme.md с описанием проекта"
    
    # Создаём конфигурацию
    config = UnifiedConfig(
        vault_path="./vault_retry_demo",
        enable_amem_memory=True,
        enable_smart_validation=False,  # Отключаем для скорости
        max_agents=1
    )
    
    # Инициализируем оркестратор
    orchestrator = UnifiedOrchestrator(config)
    print(f"🧠 A-MEM: {type(orchestrator.amem_system).__name__}")
    
    # Критерии успеха - требуем все 3 файла
    success_criteria = {
        "min_files": 3,  # Ровно 3 файла
        "required_files": ["hello.py", "config.json", "readme.md"],
        "min_quality": 0.6
    }
    
    max_attempts = 3
    attempt = 1
    best_result = None
    
    while attempt <= max_attempts:
        print(f"\n🔄 === ПОПЫТКА {attempt}/{max_attempts} ===")
        start_time = datetime.now()
        
        try:
            # Проверяем A-MEM
            if orchestrator.amem_system and attempt > 1:
                try:
                    memories = await orchestrator.amem_system.search_memories("создание файлов hello config", limit=3)
                    print(f"🧠 A-MEM: {len(memories)} релевантных воспоминаний")
                    
                    if memories:
                        print("💡 Накопленный опыт:")
                        for i, memory in enumerate(memories[:1], 1):
                            preview = memory.get('content', '')[:80] + "..."
                            print(f"   {i}. {preview}")
                        
                except Exception as e:
                    print(f"⚠️ A-MEM ошибка: {e}")
            
            # Выполняем задачу
            print(f"🚀 Запуск...")
            result = await orchestrator.solve_task(task)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Анализируем результат
            files_created = result.get('files_created', [])
            quality_score = result.get('quality_score', 0.0)
            status = result.get('status', 'unknown')
            
            print(f"\n📊 === РЕЗУЛЬТАТЫ ===")
            print(f"   ⏱️ Время: {execution_time:.1f}с")
            print(f"   📁 Файлов: {len(files_created)}")
            print(f"   🎯 Качество: {quality_score:.2f}")
            print(f"   📝 Статус: {status}")
            
            if files_created:
                print(f"   📂 Файлы:")
                for file_path in files_created:
                    print(f"      - {file_path}")
            
            # Проверяем соответствие критериям
            files_count_ok = len(files_created) >= success_criteria['min_files']
            quality_ok = quality_score >= success_criteria['min_quality']
            
            # Проверяем наличие нужных файлов
            files_match = 0
            for req_file in success_criteria['required_files']:
                for created_file in files_created:
                    if req_file in created_file:
                        files_match += 1
                        break
            
            files_match_ok = files_match >= len(success_criteria['required_files'])
            
            print(f"\n🔍 === ПРОВЕРКА ===")
            print(f"   📁 Количество файлов: {len(files_created)}/{success_criteria['min_files']} {'✅' if files_count_ok else '❌'}")
            print(f"   🎯 Качество: {quality_score:.2f}/{success_criteria['min_quality']} {'✅' if quality_ok else '❌'}")
            print(f"   📝 Нужные файлы: {files_match}/{len(success_criteria['required_files'])} {'✅' if files_match_ok else '❌'}")
            
            is_success = files_count_ok and quality_ok and files_match_ok
            
            # Сохраняем лучший результат
            if best_result is None or len(files_created) > len(best_result.get('files_created', [])):
                best_result = result
            
            if is_success:
                print(f"\n🎉 === УСПЕХ НА ПОПЫТКЕ {attempt}! ===")
                print("✅ Все требования выполнены!")
                
                # Проверяем накопленный опыт
                if orchestrator.amem_system:
                    try:
                        memories = await orchestrator.amem_system.search_memories("файлы создание", limit=5)
                        print(f"🧠 A-MEM накопил: {len(memories)} воспоминаний")
                    except Exception as e:
                        print(f"⚠️ A-MEM: {e}")
                
                return result
            
            else:
                print(f"\n⚠️ === ПОПЫТКА {attempt} НЕПОЛНАЯ ===")
                
                issues = []
                if not files_count_ok:
                    issues.append(f"Мало файлов ({len(files_created)} < {success_criteria['min_files']})")
                if not quality_ok:
                    issues.append(f"Низкое качество ({quality_score:.2f} < {success_criteria['min_quality']})")
                if not files_match_ok:
                    issues.append(f"Отсутствуют нужные файлы ({files_match} из {len(success_criteria['required_files'])})")
                
                print("❌ Проблемы:")
                for issue in issues:
                    print(f"   - {issue}")
                
                if attempt < max_attempts:
                    print(f"\n🔄 Подготовка к попытке {attempt + 1}...")
                    print("💡 A-MEM сохранит опыт для улучшения")
                    await asyncio.sleep(2)
                else:
                    print(f"\n❌ === ПОПЫТКИ ИСЧЕРПАНЫ ===")
                    print("📊 Возвращаем лучший результат")
                    return best_result
        
        except Exception as e:
            print(f"\n❌ Ошибка на попытке {attempt}: {e}")
            if attempt < max_attempts:
                print(f"🔄 Попробуем ещё раз...")
                await asyncio.sleep(1)
            else:
                return {"success": False, "error": str(e)}
        
        attempt += 1
    
    print("\n❌ Цель не достигнута")
    return best_result or {"success": False}

if __name__ == "__main__":
    print("🚀 Запуск DEMO retry логики...")
    result = asyncio.run(test_retry_demo())
    
    print(f"\n🏁 === ФИНАЛЬНЫЙ РЕЗУЛЬТАТ ===")
    print(f"✅ Успех: {result.get('success', False)}")
    print(f"📁 Файлов создано: {len(result.get('files_created', []))}")
    print(f"🎯 Итоговое качество: {result.get('quality_score', 0.0):.2f}")
    print("\n🎉 Retry логика продемонстрирована!") 