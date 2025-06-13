---
created: 2025-06-13T18:54:45.677709
updated: 2025-06-13T18:54:45.677896
tags: [direct_test_agent, code, artifact]
agent_id: direct_test_agent
artifact_type: code
original_filename: circle_area_calculator_20250613_185445.md
created_timestamp: 20250613_185445
folder: agents/direct_test_agent/artifacts
---

# direct_test_agent - code - circle_area_calculator_20250613_185445.md

# Созданный файл: circle_area_calculator.py

**Агент:** direct_test_agent
**Время:** 2025-06-13 18:54:45
**Язык:** python
**Размер:** 699 символов

## Содержимое файла

```python
import math

def calculate_circle_area(radius):
    """Расчёт площади круга по формуле A = π * r²"""
    area = math.pi * radius ** 2
    return area

def main():
    print("🔵 Калькулятор площади круга")
    print("Формула: A = π * r²")
    
    try:
        radius = float(input("Введите радиус круга: "))
        if radius <= 0:
            print("❌ Радиус должен быть положительным числом")
            return
        
        area = calculate_circle_area(radius)
        print(f"📊 Площадь круга с радиусом {radius} = {area:.2f}")
        print(f"📐 π ≈ {math.pi:.6f}")
        
    except ValueError:
        print("❌ Пожалуйста, введите корректное число")

if __name__ == "__main__":
    main()

```

## Путь к файлу
- Относительный: `outputs/circle_area_calculator.py`
- Абсолютный: `/home/cyberkitty/Project/kittycore/outputs/circle_area_calculator.py`

## Метаданные
- Создан агентом: direct_test_agent
- Тип: код
- Статус: готов к использованию
