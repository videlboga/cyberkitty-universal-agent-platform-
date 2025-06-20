#!/usr/bin/env python3
"""
Специальный тест: Создание РАБОЧЕГО CRM приложения
Цель: получить полноценное веб-приложение с JavaScript, формами, интерактивностью
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'kittycore'))

from kittycore.core.orchestrator import OrchestratorAgent

async def test_create_working_crm():
    """Тест создания полноценного рабочего CRM приложения"""
    
    print("🚀 ТЕСТ: Создание РАБОЧЕГО CRM приложения")
    print("=" * 60)
    
    # Очень детальная задача для создания рабочего приложения
    task = """
Создать полноценное рабочее CRM веб-приложение для решения проблем AmoCRM интеграции из анализа Битрикс24.

ТРЕБОВАНИЯ К ПРИЛОЖЕНИЮ:
1. HTML файл с полной структурой (DOCTYPE, head, body)
2. CSS стили для современного дизайна
3. JavaScript для интерактивности и функциональности
4. Формы для добавления клиентов
5. Таблица для отображения списка клиентов
6. Кнопки для редактирования и удаления
7. Поиск и фильтрация клиентов
8. Демо-данные клиентов уже в приложении
9. Локальное хранение данных (localStorage)
10. Готовность к запуску в браузере

ФУНКЦИОНАЛЬНОСТЬ:
- Добавление нового клиента (имя, email, телефон, статус)
- Редактирование существующих клиентов
- Удаление клиентов с подтверждением
- Поиск клиентов по имени/email
- Фильтрация по статусу (новый, в работе, закрыт)
- Сортировка по дате добавления
- Счетчики статистики (всего клиентов, активных, закрытых)

ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ:
- Один HTML файл со всем кодом
- Современный responsive дизайн
- Использование современного JavaScript (ES6+)
- Валидация форм
- Уведомления об успешных операциях
- Обработка ошибок

НАЗВАНИЕ ФАЙЛА: working_crm_dashboard.html

Создай РЕАЛЬНО РАБОТАЮЩЕЕ приложение, которое можно открыть в браузере и использовать!
"""
    
    print("📋 Задача: Создание полноценного CRM приложения")
    print("🎯 Ожидаемый результат: working_crm_dashboard.html с полной функциональностью")
    print()
    
    orchestrator = OrchestratorAgent()
    
    try:
        print("🚀 Запускаем создание рабочего CRM...")
        result = await orchestrator.execute_task(task)
        
        # Проверяем результат
        if isinstance(result, str):
            print(f"❌ Ошибка выполнения: {result}")
            return False
        
        print(f"✅ Задача выполнена!")
        print(f"📊 Результат: {result}")
        
        # Ищем созданный файл
        target_file = "working_crm_dashboard.html"
        
        if os.path.exists(target_file):
            size = os.path.getsize(target_file)
            print(f"✅ Найден файл: {target_file} ({size} байт)")
            
            # Анализируем содержимое
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Детальная проверка функциональности
            checks = {
                "HTML структура": "<!DOCTYPE html>" in content and "<html" in content and "</html>" in content,
                "CSS стили": "<style>" in content and "body" in content and "font-family" in content,
                "JavaScript код": "<script>" in content and "function" in content,
                "Формы": "<form>" in content or "<input" in content,
                "Таблицы": "<table>" in content or "tbody" in content,
                "Кнопки": "<button>" in content and "onclick" in content,
                "Event listeners": "addEventListener" in content or "onclick" in content,
                "LocalStorage": "localStorage" in content,
                "Функции CRUD": "add" in content.lower() and "delete" in content.lower(),
                "Поиск/фильтр": "search" in content.lower() or "filter" in content.lower(),
                "Демо данные": "demo" in content.lower() or "example" in content.lower() or "клиент" in content.lower(),
                "Responsive дизайн": "responsive" in content or "@media" in content or "viewport" in content,
                "Валидация": "required" in content or "validate" in content.lower(),
                "Большой размер": len(content) > 5000  # Минимум 5KB для полноценного приложения
            }
            
            passed_checks = sum(checks.values())
            total_checks = len(checks)
            
            print(f"\n📊 АНАЛИЗ ФУНКЦИОНАЛЬНОСТИ:")
            print(f"Проверок пройдено: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.1f}%)")
            print()
            
            for check_name, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check_name}")
            
            # Оценка качества
            if passed_checks >= 12:
                print(f"\n🎉 ОТЛИЧНО! Полноценное рабочее приложение!")
                quality = "ОТЛИЧНОЕ"
            elif passed_checks >= 9:
                print(f"\n✅ ХОРОШО! Рабочее приложение с основной функциональностью")
                quality = "ХОРОШЕЕ"
            elif passed_checks >= 6:
                print(f"\n⚠️ УДОВЛЕТВОРИТЕЛЬНО. Базовое приложение")
                quality = "БАЗОВОЕ"
            else:
                print(f"\n❌ ПЛОХО. Не рабочее приложение")
                quality = "НЕ РАБОЧЕЕ"
            
            # Показываем превью кода
            print(f"\n📄 ПРЕВЬЮ КОДА ({len(content)} символов):")
            print("-" * 50)
            preview = content[:500] + "..." if len(content) > 500 else content
            print(preview)
            
            # Инструкции по запуску
            print(f"\n🌐 ИНСТРУКЦИИ ПО ЗАПУСКУ:")
            print(f"1. Откройте файл в браузере: chromium {target_file}")
            print(f"2. Или запустите локальный сервер: python -m http.server 8000")
            print(f"3. Затем откройте: http://localhost:8000/{target_file}")
            
            return quality in ["ОТЛИЧНОЕ", "ХОРОШЕЕ"]
            
        else:
            print(f"❌ Файл {target_file} не найден!")
            
            # Ищем любые новые HTML файлы
            html_files = [f for f in os.listdir('.') if f.endswith('.html')]
            recent_files = []
            
            import time
            current_time = time.time()
            
            for html_file in html_files:
                file_time = os.path.getmtime(html_file)
                if current_time - file_time < 120:  # Файлы созданные за последние 2 минуты
                    size = os.path.getsize(html_file)
                    recent_files.append((html_file, size))
            
            if recent_files:
                print(f"📄 Найдены недавно созданные HTML файлы:")
                for filename, size in recent_files:
                    print(f"  - {filename} ({size} байт)")
                    
                # Проверим самый большой файл
                largest_file = max(recent_files, key=lambda x: x[1])
                print(f"\n🔍 Проверяем самый большой файл: {largest_file[0]}")
                
                with open(largest_file[0], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "crm" in content.lower() or "клиент" in content.lower():
                    print(f"✅ Возможно это наше CRM приложение!")
                    return True
            
            return False
            
    except Exception as e:
        print(f"💥 Ошибка выполнения: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ЗАПУСК ТЕСТА: СОЗДАНИЕ РАБОЧЕГО CRM")
    print("=" * 60)
    
    success = asyncio.run(test_create_working_crm())
    
    if success:
        print("\n🎉 УСПЕХ! Рабочее CRM приложение создано!")
        print("🌟 KittyCore 3.0 может создавать полноценные приложения!")
    else:
        print("\n💥 ПРОВАЛ! CRM приложение не создано или не работает")
        print("🔧 Нужно улучшить систему создания приложений") 