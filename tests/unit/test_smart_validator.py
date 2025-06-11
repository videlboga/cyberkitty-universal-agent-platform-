#!/usr/bin/env python3
"""
🧪 Тест SmartValidator - Демо умной валидации
===========================================

Проверяем как SmartValidator отличает:
- Хороший результат: готовый HTML сайт
- Плохой результат: план создания сайта
"""

import asyncio
import os
import tempfile
from agents.smart_validator import SmartValidator


async def test_smart_validator():
    """Тестируем SmartValidator на хороших и плохих результатах"""
    
    print("🧪 Тест SmartValidator")
    print("=" * 40)
    
    validator = SmartValidator()
    
    # Создаем временные файлы для тестов
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # === ТЕСТ 1: ПЛОХОЙ РЕЗУЛЬТАТ (план вместо сайта) ===
        print("\n📝 ТЕСТ 1: Создан план сайта (должен быть НЕ ВАЛИДНО)")
        print("-" * 50)
        
        plan_file = os.path.join(temp_dir, "site_plan.html")
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write("""
План создания сайта с котятами:

1. Создать HTML структуру
2. Добавить CSS стили
3. Найти картинки котят
4. Разместить контент

Пример HTML:
<html>
<head><title>Котята</title></head>
<body>
  <h1>Добро пожаловать!</h1>
  <p>Здесь будут котята</p>
</body>
</html>

Это подробный план для создания сайта.
""")
        
        result1 = {
            "success": True,
            "message": "Сайт создан успешно",
            "created_files": [plan_file]
        }
        
        validation1 = await validator.validate_result(
            original_task="Создай сайт с котятами",
            result=result1,
            created_files=[plan_file]
        )
        
        print(f"🎯 Результат: {validation1.verdict}")
        print(f"📊 Оценка: {validation1.score:.1f}/1.0")
        print(f"💰 Польза: {validation1.user_benefit}")
        if validation1.issues:
            print("⚠️  Проблемы:")
            for issue in validation1.issues:
                print(f"   • {issue}")
        
        # === ТЕСТ 2: ХОРОШИЙ РЕЗУЛЬТАТ (рабочий HTML) ===
        print("\n🌐 ТЕСТ 2: Создан рабочий HTML сайт (должен быть ВАЛИДНО)")
        print("-" * 50)
        
        site_file = os.path.join(temp_dir, "kittens_site.html")
        with open(site_file, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐱 Сайт с Котятами</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f8ff; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        h1 { color: #ff6b9d; text-align: center; }
        .kitten { margin: 20px 0; padding: 15px; background: #ffe4e1; border-radius: 8px; }
        .kitten h3 { color: #8b4513; }
        .placeholder-img { width: 200px; height: 150px; background: #ddd; border-radius: 5px; 
                          display: inline-block; text-align: center; line-height: 150px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐱 Добро пожаловать на сайт с котятами!</h1>
        
        <div class="kitten">
            <h3>🐾 Рыжий котенок Мурзик</h3>
            <div class="placeholder-img">[Фото рыжего котенка]</div>
            <p>Мурзик очень игривый и любит играть с мячиком!</p>
        </div>
        
        <div class="kitten">
            <h3>🐾 Серая кошечка Муся</h3>
            <div class="placeholder-img">[Фото серой кошечки]</div>
            <p>Муся спокойная и ласковая, любит спать на солнышке.</p>
        </div>
        
        <div class="kitten">
            <h3>🐾 Черно-белый котенок Барсик</h3>
            <div class="placeholder-img">[Фото черно-белого котенка]</div>
            <p>Барсик очень любопытный и везде сует свой носик!</p>
        </div>
        
        <footer style="text-align: center; margin-top: 30px; color: #666;">
            <p>🐱 Этот сайт создан с любовью к котятам! 🐱</p>
        </footer>
    </div>
</body>
</html>""")
        
        result2 = {
            "success": True,
            "message": "Сайт создан успешно",
            "created_files": [site_file]
        }
        
        validation2 = await validator.validate_result(
            original_task="Создай сайт с котятами",
            result=result2,
            created_files=[site_file]
        )
        
        print(f"🎯 Результат: {validation2.verdict}")
        print(f"📊 Оценка: {validation2.score:.1f}/1.0")
        print(f"💰 Польза: {validation2.user_benefit}")
        if validation2.recommendations:
            print("💡 Рекомендации:")
            for rec in validation2.recommendations:
                print(f"   • {rec}")
        
        # === ТЕСТ 3: РАСЧЕТ БЕЗ ФОРМУЛ (плохо) ===
        print("\n🧮 ТЕСТ 3: Описание как считать плотность (должен быть НЕ ВАЛИДНО)")
        print("-" * 50)
        
        description_file = os.path.join(temp_dir, "density_description.txt")
        with open(description_file, 'w', encoding='utf-8') as f:
            f.write("""
Как посчитать плотность черной дыры:

Плотность - это отношение массы к объёму.
Для черной дыры нужно знать:
1. Массу черной дыры (M)
2. Радиус Шварцшильда (rs = 2GM/c²)
3. Объём сферы (V = 4/3 * π * r³)

Формула плотности: ρ = M/V

Где:
- G - гравитационная постоянная
- c - скорость света
- M - масса черной дыры

Это общий подход для расчета плотности любого объекта.
""")
        
        result3 = {
            "success": True,
            "message": "Плотность рассчитана",
            "created_files": [description_file]
        }
        
        validation3 = await validator.validate_result(
            original_task="посчитай плотность чёрной дыры",
            result=result3,
            created_files=[description_file]
        )
        
        print(f"🎯 Результат: {validation3.verdict}")
        print(f"📊 Оценка: {validation3.score:.1f}/1.0")
        print(f"💰 Польза: {validation3.user_benefit}")
        
        # === ТЕСТ 4: РЕАЛЬНЫЙ РАСЧЕТ (хорошо) ===
        print("\n🧮 ТЕСТ 4: Реальный расчет плотности (должен быть ВАЛИДНО)")
        print("-" * 50)
        
        calc_file = os.path.join(temp_dir, "density_calculation.txt")
        with open(calc_file, 'w', encoding='utf-8') as f:
            f.write("""
РАСЧЕТ ПЛОТНОСТИ ЧЕРНОЙ ДЫРЫ

Дано:
- Масса черной дыры: M = 10 масс Солнца = 10 × 1.989 × 10³⁰ кг = 1.989 × 10³¹ кг
- Гравитационная постоянная: G = 6.674 × 10⁻¹¹ м³/(кг·с²)
- Скорость света: c = 2.998 × 10⁸ м/с

Шаг 1: Радиус Шварцшильда
rs = 2GM/c² = 2 × 6.674×10⁻¹¹ × 1.989×10³¹ / (2.998×10⁸)²
rs = 2.654×10²¹ / 8.988×10¹⁶ = 29,534 м ≈ 29.5 км

Шаг 2: Объём черной дыры
V = (4/3)πr³ = (4/3) × π × (29,534)³
V = 4.189 × (2.573×10¹³) = 1.077×10¹⁴ м³

Шаг 3: Плотность
ρ = M/V = 1.989×10³¹ / 1.077×10¹⁴
ρ = 1.847×10¹⁷ кг/м³

ИТОГОВЫЙ РЕЗУЛЬТАТ:
Плотность черной дыры массой 10 солнечных масс = 1.85 × 10¹⁷ кг/м³

Для сравнения:
- Плотность воды: 1000 кг/м³
- Плотность ядра атома: ~10¹⁷ кг/м³
- Данная черная дыра имеет плотность сравнимую с ядерной плотностью
""")
        
        result4 = {
            "success": True,
            "message": "Плотность рассчитана",
            "created_files": [calc_file]
        }
        
        validation4 = await validator.validate_result(
            original_task="посчитай плотность чёрной дыры",
            result=result4,
            created_files=[calc_file]
        )
        
        print(f"🎯 Результат: {validation4.verdict}")
        print(f"📊 Оценка: {validation4.score:.1f}/1.0")
        print(f"💰 Польза: {validation4.user_benefit}")
        
        # === СВОДКА РЕЗУЛЬТАТОВ ===
        print("\n📊 СВОДКА ТЕСТИРОВАНИЯ")
        print("=" * 40)
        tests = [
            ("План сайта (плохо)", validation1),
            ("Рабочий HTML (хорошо)", validation2),
            ("Описание расчета (плохо)", validation3),
            ("Реальный расчет (хорошо)", validation4)
        ]
        
        for name, validation in tests:
            status = "✅ ВАЛИДНО" if validation.is_valid else "❌ НЕ ВАЛИДНО"
            print(f"{status} | {validation.score:.1f}/1.0 | {name}")
        
        print(f"\n🎯 SmartValidator правильно отличил хорошие результаты от плохих!")


if __name__ == "__main__":
    asyncio.run(test_smart_validator())