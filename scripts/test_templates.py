#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование продвинутого резолвера шаблонов.

Демонстрирует все возможности нового TemplateResolver:
- {variable} - простые переменные
- {{variable}} - Django/Jinja2 стиль
- {user.name} - вложенные объекты
- {items[0]} - элементы массивов
- {current_timestamp} - специальные переменные
"""

import sys
import os

# Добавляем корневую папку проекта в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.template_resolver import template_resolver


def test_template_resolution():
    """Тестирует все возможности резолвера шаблонов."""
    
    print("🧪 ТЕСТИРОВАНИЕ ПРОДВИНУТОГО РЕЗОЛВЕРА ШАБЛОНОВ")
    print("=" * 60)
    
    # Подготавливаем тестовый контекст
    context = {
        "user_id": "12345",
        "chat_id": "67890", 
        "name": "Андрей",
        "age": 25,
        "user": {
            "name": "Иван",
            "email": "ivan@example.com",
            "profile": {
                "city": "Москва",
                "country": "Россия"
            }
        },
        "items": [
            {"name": "Первый", "price": 100},
            {"name": "Второй", "price": 200},
            {"name": "Третий", "price": 300}
        ],
        "telegram_data": {
            "chat_id": "648981358",
            "username": "Like_a_duck"
        }
    }
    
    # Список тестовых шаблонов
    test_templates = [
        # === ПРОСТЫЕ ПЕРЕМЕННЫЕ ===
        "{user_id}",
        "{name}",
        "Привет, {name}! Твой ID: {user_id}",
        
        # === DJANGO/JINJA2 СТИЛЬ ===
        "{{user_id}}",
        "{{name}}",
        "Привет, {{name}}! Твой возраст: {{age}}",
        
        # === ВЛОЖЕННЫЕ ОБЪЕКТЫ ===
        "{user.name}",
        "{user.email}",
        "{user.profile.city}",
        "{user.profile.country}",
        "Пользователь {{user.name}} из города {{user.profile.city}}",
        
        # === МАССИВЫ ===
        "{items[0].name}",
        "{items[1].price}",
        "{items[2].name}",
        "Первый товар: {{items[0].name}} за {{items[0].price}} руб.",
        
        # === СПЕЦИАЛЬНЫЕ ПЕРЕМЕННЫЕ ===
        "{current_timestamp}",
        "{current_date}",
        "{current_time}",
        "Сообщение от {current_datetime}",
        
        # === КОМБИНИРОВАННЫЕ ===
        "Привет, {user.name}! Сегодня {current_date}, товар {{items[0].name}} стоит {items[0].price}",
        
        # === TELEGRAM СПЕЦИФИКА ===
        "{telegram_data.chat_id}",
        "{telegram_data.username}",
        "Telegram: chat_id={{telegram_data.chat_id}}, username={telegram_data.username}",
        
        # === ОШИБОЧНЫЕ (ДОЛЖНЫ ОСТАТЬСЯ КАК ЕСТЬ) ===
        "{nonexistent}",
        "{user.nonexistent}",
        "{items[10].name}",
        "{{missing_var}}",
    ]
    
    print(f"📋 Тестируем {len(test_templates)} шаблонов")
    print()
    
    success_count = 0
    error_count = 0
    
    for i, template in enumerate(test_templates, 1):
        print(f"📝 Тест {i:2d}: {template}")
        
        # Тестируем через основной метод
        result = template_resolver.test_resolution(template, context)
        
        if result["success"]:
            if result["changed"]:
                print(f"    ✅ Результат: {result['resolved']}")
                success_count += 1
            else:
                print(f"    ➡️  Без изменений: {result['resolved']}")
                success_count += 1
        else:
            print(f"    ❌ Ошибка: {result['error']}")
            error_count += 1
        
        print()
    
    print("=" * 60)
    print(f"📊 ИТОГИ ТЕСТИРОВАНИЯ:")
    print(f"✅ Успешно: {success_count}")
    print(f"❌ Ошибок: {error_count}")
    print(f"📋 Всего: {len(test_templates)}")
    
    # Тестируем глубокое разрешение
    print("\n🔍 ТЕСТИРОВАНИЕ ГЛУБОКОГО РАЗРЕШЕНИЯ")
    print("=" * 60)
    
    complex_data = {
        "message": "Привет, {user.name}!",
        "buttons": [
            {"text": "Товар: {items[0].name}", "callback": "item_0"},
            {"text": "Цена: {{items[1].price}} руб", "callback": "item_1"}
        ],
        "metadata": {
            "user_id": "{user_id}",
            "timestamp": "{current_timestamp}",
            "source": "Telegram chat {{telegram_data.chat_id}}"
        }
    }
    
    print("Исходные данные:")
    import json
    print(json.dumps(complex_data, ensure_ascii=False, indent=2))
    
    resolved_data = template_resolver.resolve_deep(complex_data, context)
    
    print("\nРазрешенные данные:")
    print(json.dumps(resolved_data, ensure_ascii=False, indent=2))


def test_edge_cases():
    """Тестирует граничные случаи."""
    
    print("\n🧪 ТЕСТИРОВАНИЕ ГРАНИЧНЫХ СЛУЧАЕВ")
    print("=" * 60)
    
    edge_cases = [
        # Пустые значения
        ("", {}),
        ("{}", {"": "empty_key"}),
        
        # Различные типы данных
        ("{number}", {"number": 42}),
        ("{boolean}", {"boolean": True}),
        ("{none_value}", {"none_value": None}),
        ("{list_value}", {"list_value": [1, 2, 3]}),
        
        # Сложная навигация
        ("{data.items[0].nested.deep.value}", {
            "data": {
                "items": [
                    {"nested": {"deep": {"value": "Найдено!"}}}
                ]
            }
        }),
        
        # Смешанные форматы
        ("{{simple}} and {complex.nested}", {
            "simple": "Простое",
            "complex": {"nested": "Сложное"}
        })
    ]
    
    for template, context in edge_cases:
        print(f"📝 Шаблон: '{template}'")
        print(f"    Контекст: {context}")
        
        result = template_resolver.resolve(template, context)
        print(f"    ✅ Результат: '{result}'")
        print()


if __name__ == "__main__":
    test_template_resolution()
    test_edge_cases()
    
    print("\n🎯 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("Новый TemplateResolver поддерживает все современные форматы шаблонов.") 