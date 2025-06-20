#!/usr/bin/env python3
"""
🚀 УЛУЧШЕННЫЙ ЗАПУСК АНАЛИЗА БИТРИКС24
Используем накопленные знания для получения реального результата
"""

import asyncio
import sys
import os
sys.path.append('.')

from kittycore.core.orchestrator import solve_with_orchestrator
from kittycore.core.agent_learning_system import AgentLearningSystem

async def attempt_bitrix_analysis(attempt_number: int):
    """Попытка анализа рынка Битрикс24"""
    
    print(f"\n🚀 ПОПЫТКА #{attempt_number} - АНАЛИЗ БИТРИКС24")
    print("=" * 60)
    
    # Задача с учётом накопленных знаний
    task = f"""
    ЗАДАЧА: Создать РЕАЛЬНЫЙ анализ рынка приложений Битрикс24 (попытка #{attempt_number})

    ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ:
    1. Использовать web_search для поиска РЕАЛЬНЫХ данных о Битрикс24 маркетплейсе
    2. Найти конкретные приложения и их категории (НЕ шаблоны!)
    3. Создать функциональные HTML прототипы с JavaScript
    4. Провести анализ конкурентов с конкретными примерами
    
    РЕЗУЛЬТАТ ДОЛЖЕН СОДЕРЖАТЬ:
    - Список из 15 РЕАЛЬНЫХ категорий приложений с примерами
    - Анализ 5 конкретных приложений и их UX проблем
    - 3 HTML прототипа с рабочими элементами интерфейса
    - Markdown отчёт с конкретными данными и скриншотами
    
    ИЗБЕГАТЬ:
    - Шаблонных HTML файлов без реального контента
    - Общих фраз типа "проанализировать рынок"
    - Прототипов без функциональности
    
    ИСПОЛЬЗОВАТЬ:
    - web_search для поиска данных о Битрикс24
    - code_generator для создания функциональных прототипов
    - file_manager для структурирования результатов
    """
    
    result = await solve_with_orchestrator(task)
    
    print(f"\n📊 РЕЗУЛЬТАТ ПОПЫТКИ #{attempt_number}:")
    print(f"✅ Успех: {result.get('success', False)}")
    print(f"📁 Файлов создано: {len(result.get('generated_files', []))}")
    
    # Анализируем качество результата
    quality_score = await analyze_result_quality(attempt_number)
    
    print(f"🎯 Оценка качества: {quality_score:.1f}/5.0")
    
    if quality_score >= 4.0:
        print("🎉 ОТЛИЧНО! Реальный результат получен!")
        return True, quality_score
    else:
        print("⚠️ Нужно улучшение, запускаем ещё раз...")
        return False, quality_score

async def analyze_result_quality(attempt_number: int) -> float:
    """Анализ качества созданных файлов"""
    
    files_to_check = [
        "рынок_проектов.md",
        "категории_приложений.md", 
        "прототип_1.html",
        "прототип_2.html",
        "прототип_3.html"
    ]
    
    total_score = 0
    files_found = 0
    
    for filename in files_to_check:
        if os.path.exists(filename):
            files_found += 1
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Проверяем качество контента
                score = 0
                
                # Базовые критерии (1 балл)
                if len(content) > 500:
                    score += 1
                
                # Реальный контент (2 балла)
                if any(keyword in content.lower() for keyword in [
                    "битрикс24", "bitrix24", "crm", "интеграция", "api", "приложение"
                ]):
                    score += 2
                
                # Функциональность для HTML (1 балл)
                if filename.endswith('.html') and any(keyword in content for keyword in [
                    "onclick", "function", "script", "input", "button"
                ]):
                    score += 1
                
                # Конкретные данные (1 балл)
                if any(keyword in content.lower() for keyword in [
                    "тыс. руб", "$", "процент", "пользователи", "скачиваний"
                ]):
                    score += 1
                
                total_score += min(score, 5)
                print(f"  📄 {filename}: {min(score, 5)}/5")
                
            except Exception as e:
                print(f"  ❌ Ошибка чтения {filename}: {e}")
    
    if files_found == 0:
        return 0.0
    
    return total_score / files_found

async def record_learning_after_attempt(attempt_number: int, success: bool, quality_score: float):
    """Записываем опыт обучения после попытки"""
    
    learning_system = AgentLearningSystem()
    
    if success:
        # Успешная попытка
        lesson = await learning_system.record_learning(
            agent_id="bitrix_analyzer",
            task_description=f"Анализ рынка Битрикс24 - попытка {attempt_number}",
            attempt_number=attempt_number,
            score_before=max(0, quality_score - 1),
            score_after=quality_score,
            error_patterns=[],
            successful_actions=[
                "Использовал web_search для реальных данных",
                "Создал функциональные прототипы",
                "Добавил конкретные примеры и цифры"
            ],
            failed_actions=[],
            feedback_received=f"Отличный результат! Оценка {quality_score}/5.0",
            tools_used=["web_search", "code_generator", "file_manager"]
        )
    else:
        # Неудачная попытка
        lesson = await learning_system.record_learning(
            agent_id="bitrix_analyzer", 
            task_description=f"Анализ рынка Битрикс24 - попытка {attempt_number}",
            attempt_number=attempt_number,
            score_before=0,
            score_after=quality_score,
            error_patterns=[
                "Всё ещё создаёт шаблонный контент",
                "Недостаточно реальных данных"
            ],
            successful_actions=["Создал структуру файлов"],
            failed_actions=["Не использовал web_search эффективно"],
            feedback_received=f"Нужно больше реальных данных. Оценка {quality_score}/5.0",
            tools_used=["code_generator", "file_manager"]
        )
    
    print(f"📚 Урок записан: {lesson}")

async def main():
    print("🎯 ИТЕРАТИВНОЕ УЛУЧШЕНИЕ АНАЛИЗА БИТРИКС24")
    print("Запускаем пока не получим реальный результат!")
    print("=" * 60)
    
    max_attempts = 5
    
    for attempt in range(1, max_attempts + 1):
        try:
            success, quality_score = await attempt_bitrix_analysis(attempt)
            
            # Записываем опыт обучения
            await record_learning_after_attempt(attempt, success, quality_score)
            
            if success:
                print(f"\n🎉 УСПЕХ НА ПОПЫТКЕ #{attempt}!")
                print(f"Качество: {quality_score:.1f}/5.0")
                
                # Показываем созданные файлы
                print(f"\n📁 СОЗДАННЫЕ ФАЙЛЫ:")
                for filename in os.listdir('.'):
                    if any(name in filename for name in ['рынок', 'категории', 'прототип', 'ux_анализ']):
                        size = os.path.getsize(filename)
                        print(f"  • {filename} ({size} байт)")
                
                break
            else:
                print(f"\n⏳ Попытка #{attempt} неудачна. Система обучается...")
                
                if attempt < max_attempts:
                    print(f"🔄 Запускаем попытку #{attempt + 1} с улучшенными знаниями...")
                    await asyncio.sleep(2)  # Пауза между попытками
        
        except Exception as e:
            print(f"❌ Ошибка в попытке #{attempt}: {e}")
            await asyncio.sleep(1)
    
    else:
        print(f"\n😔 Не удалось получить качественный результат за {max_attempts} попыток")
        print("Но система накопила опыт для будущих запусков!")

if __name__ == "__main__":
    asyncio.run(main()) 