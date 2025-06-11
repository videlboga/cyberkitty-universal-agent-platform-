#!/usr/bin/env python3
"""
🧪 Простое демо SmartValidator
============================

Демонстрация как SmartValidator отличает план от реального результата
"""

import asyncio
import os
import tempfile
import time
from agents.smart_validator import SmartValidator


async def demo_current_problem():
    """Демонстрируем текущую проблему KittyCore - план вместо результата"""
    
    print("🐱 Демо проблемы KittyCore 3.0")
    print("=" * 50)
    print("Проблема: система создает планы вместо реальных результатов")
    print("Решение: SmartValidator с LLM-оценкой конечной пользы")
    print()
    
    validator = SmartValidator()
    
    # Создаем временную папку
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # === ИМИТИРУЕМ ТЕКУЩУЮ ПРОБЛЕМУ ===
        print("📝 ТЕКУЩАЯ ПРОБЛЕМА: Создан план вместо сайта")
        print("-" * 50)
        
        # Создаем файл как это делает текущая система
        plan_file = os.path.join(temp_dir, "kittens-website.html")
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write("""
# План создания сайта с котятами

## Структура сайта
1. Главная страница
2. Галерея котят  
3. Контакты

## Необходимые элементы
- HTML разметка
- CSS стили
- Изображения котят
- JavaScript для интерактивности

## Примерный код HTML:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Котята</title>
</head>
<body>
    <h1>Добро пожаловать!</h1>
    <p>Здесь будут котята</p>
</body>
</html>
```

Этот план поможет создать красивый сайт с котятами.
""")
        
        # Имитируем результат системы
        system_result = {
            "success": True,
            "message": "Сайт с котятами создан успешно!",
            "created_files": [plan_file],
            "agent_actions": ["Создан HTML файл", "Добавлен контент о котятах"]
        }
        
        print(f"✅ Система отчиталась: {system_result['message']}")
        print(f"📁 Создан файл: {os.path.basename(plan_file)}")
        print(f"🔧 Действия: {', '.join(system_result['agent_actions'])}")
        
        # === УМНАЯ ВАЛИДАЦИЯ ===
        print(f"\n🧠 ЗАПУСК УМНОЙ ВАЛИДАЦИИ...")
        validation_start = time.time()
        
        validation = await validator.validate_result(
            original_task="Сделай сайт с котятами",
            result=system_result,
            created_files=[plan_file]
        )
        
        validation_time = time.time() - validation_start
        
        print(f"🔍 Валидация завершена за {validation_time:.2f}с")
        print()
        
        # === РЕЗУЛЬТАТЫ ВАЛИДАЦИИ ===
        print("📊 РЕЗУЛЬТАТ УМНОЙ ВАЛИДАЦИИ")
        print("-" * 50)
        print(f"🎯 Вердикт: {validation.verdict}")
        print(f"📊 Оценка качества: {validation.score:.1f}/1.0")
        print(f"💰 Польза для пользователя:")
        print(f"   {validation.user_benefit}")
        
        if validation.issues:
            print(f"\n⚠️  Найденные проблемы:")
            for issue in validation.issues:
                print(f"   • {issue}")
        
        if validation.recommendations:
            print(f"\n💡 Рекомендации:")
            for rec in validation.recommendations:
                print(f"   • {rec}")
        
        # === ИТОГОВЫЙ СТАТУС ===
        print(f"\n🎯 ИТОГОВЫЙ СТАТУС:")
        if validation.is_valid:
            print("   ✅ КАЧЕСТВО ПОДТВЕРЖДЕНО - результат готов к использованию!")
        else:
            print("   ❌ КАЧЕСТВО НЕ СООТВЕТСТВУЕТ - результат требует доработки!")
            
        print(f"\n💡 ВЫВОД:")
        print(f"   Система создала файл и отчиталась об успехе,")
        print(f"   но SmartValidator выявил что это план, а не сайт!")
        print(f"   Пользователь НЕ получил того, что просил.")
        
        # Показываем содержимое файла
        print(f"\n📄 СОДЕРЖИМОЕ СОЗДАННОГО ФАЙЛА:")
        print("-" * 50)
        with open(plan_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Показываем первые 300 символов
            preview = content[:300] + ("..." if len(content) > 300 else "")
            print(preview)


if __name__ == "__main__":
    asyncio.run(demo_current_problem())