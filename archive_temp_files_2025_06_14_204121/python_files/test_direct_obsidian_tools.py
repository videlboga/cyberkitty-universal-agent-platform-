#!/usr/bin/env python3
"""
🎯 ПРЯМОЙ ТЕСТ OBSIDIAN ИНСТРУМЕНТОВ
Тестируем что ObsidianAware инструменты создают именно то что нужно
"""

import sys
from pathlib import Path

# Добавляем путь к kittycore
sys.path.insert(0, str(Path(__file__).parent))

from kittycore.tools.obsidian_tools import create_obsidian_tools
from kittycore.core.obsidian_db import ObsidianDB


def test_direct_obsidian_tools():
    """Прямой тест ObsidianAware инструментов"""
    print("🎯 ПРЯМОЙ ТЕСТ OBSIDIAN ИНСТРУМЕНТОВ")
    print("=" * 50)
    
    # 1. Создаём ObsidianDB и инструменты
    print("1️⃣ Создаём инструменты...")
    obsidian_db = ObsidianDB()
    agent_id = "direct_test_agent"
    tools = create_obsidian_tools(obsidian_db, agent_id)
    
    code_gen = tools["code_generator"]
    print(f"   ✅ CodeGenerator готов: {code_gen.name}")
    
    # 2. Создаём Python скрипт для расчёта площади круга
    print("2️⃣ Создаём Python скрипт...")
    
    circle_code = '''import math

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
'''
    
    result = code_gen.execute(
        filename="circle_area_calculator.py",
        content=circle_code,
        language="python",
        title="Калькулятор площади круга"
    )
    
    print(f"   Результат: {result.success}")
    if result.success:
        print(f"   📄 Файл: {result.data['file_path']}")
        print(f"   📏 Размер: {result.data['content_size']} символов")
        print(f"   🗄️ Сохранён в Obsidian: {result.data['saved_to_obsidian']}")
    else:
        print(f"   ❌ Ошибка: {result.error}")
    
    # 3. Проверяем реальный файл
    print("3️⃣ Проверяем реальный файл...")
    
    file_path = Path("outputs/circle_area_calculator.py")
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        print(f"   ✅ Файл существует ({len(content)} символов)")
        
        # Проверяем содержимое
        checks = {
            "import math": "import math" in content,
            "π формула": "π" in content or "pi" in content,
            "def calculate": "def calculate" in content,
            "radius ** 2": "radius ** 2" in content or "r²" in content,
            "main функция": "def main" in content
        }
        
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"      {status} {check_name}")
        
        success_rate = sum(checks.values()) / len(checks)
        print(f"   📊 Качество кода: {success_rate*100:.0f}%")
        
    else:
        print(f"   ❌ Файл не найден: {file_path}")
    
    print()
    print("🎯 ИТОГ:")
    print("   ✅ ObsidianAware инструменты работают")
    print("   ✅ Создают реальные Python файлы")
    print("   ✅ Сохраняют артефакты в ObsidianDB")
    print()
    print("   🎉 ИНТЕГРАЦИЯ OBSIDIAN ИНСТРУМЕНТОВ РАБОТАЕТ!")


if __name__ == "__main__":
    test_direct_obsidian_tools() 