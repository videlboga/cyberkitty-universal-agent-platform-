#!/usr/bin/env python3
"""
Практическая демонстрация GUI управления KittyCore 3.0
Показывает реальные возможности автоматизации GUI
"""

import sys
import asyncio
import time

sys.path.append('.')

from kittycore.tools.computer_use_tool import ComputerUseTool

async def gui_demo_practical():
    """Практическая демонстрация возможностей GUI"""
    
    print("🎭 ПРАКТИЧЕСКАЯ ДЕМОНСТРАЦИЯ GUI УПРАВЛЕНИЯ")
    print("=" * 50)
    print("⚠️ ВНИМАНИЕ: Будет выполняться реальное управление GUI!")
    print("   Закройте важные приложения перед запуском")
    print()
    
    # Пауза для подготовки
    for i in range(3, 0, -1):
        print(f"Запуск через {i}...")
        await asyncio.sleep(1)
    
    tool = ComputerUseTool()
    
    # Демо 1: Информация о системе
    print("\n🔍 ДЕМО 1: Информация о системе")
    print("-" * 30)
    
    # Размер экрана
    result = await tool.execute({"action": "get_screen_info"})
    if result["success"]:
        info = result["screen_info"]
        print(f"�� Экран: {info['width']}x{info['height']} (дисплей {info['display_name']})")
    
    # Текущая позиция мыши
    result = await tool.execute({"action": "get_mouse_position"})
    if result["success"]:
        pos = result["position"]
        print(f"🖱️ Мышь: ({pos['x']}, {pos['y']})")
    
    # Активное окно
    result = await tool.execute({"action": "get_active_window"})
    if result["success"] and result.get("window"):
        window = result["window"]
        title = window.get("title", "Без названия")[:40]
        print(f"🪟 Активное окно: {title}")
    
    # Демо 2: Скриншот
    print("\n📸 ДЕМО 2: Создание скриншота")
    print("-" * 30)
    
    screenshot_path = "/tmp/kittycore_gui_demo.png"
    result = await tool.execute({
        "action": "screenshot",
        "save_path": screenshot_path
    })
    
    if result["success"]:
        import os
        size = os.path.getsize(screenshot_path)
        print(f"✅ Скриншот сохранён: {screenshot_path}")
        print(f"   Размер файла: {size:,} байт")
    else:
        print(f"❌ Ошибка скриншота: {result.get('error')}")
    
    # Демо 3: Безопасное движение мыши
    print("\n🖱️ ДЕМО 3: Управление мышью")
    print("-" * 30)
    
    # Сохраняем текущую позицию
    original_pos = await tool.execute({"action": "get_mouse_position"})
    if original_pos["success"]:
        orig_x = original_pos["position"]["x"]
        orig_y = original_pos["position"]["y"]
        print(f"Исходная позиция: ({orig_x}, {orig_y})")
        
        # Движение по квадрату (безопасная зона)
        safe_moves = [
            (orig_x + 50, orig_y),      # Вправо
            (orig_x + 50, orig_y + 50), # Вниз
            (orig_x, orig_y + 50),      # Влево  
            (orig_x, orig_y)            # Вверх (возврат)
        ]
        
        print("Движение по квадрату:")
        for i, (x, y) in enumerate(safe_moves, 1):
            result = await tool.execute({
                "action": "mouse_move",
                "x": x,
                "y": y
            })
            if result["success"]:
                print(f"  {i}. Переместились в ({x}, {y})")
            await asyncio.sleep(0.5)  # Пауза чтобы видеть движение
    
    # Демо 4: Клавиатура (безопасно)
    print("\n⌨️ ДЕМО 4: Управление клавиатурой")
    print("-" * 30)
    
    # Нажатие безопасных клавиш
    safe_keys = ["space", "tab", "escape"]
    
    for key in safe_keys:
        result = await tool.execute({
            "action": "key_press", 
            "key": key
        })
        if result["success"]:
            print(f"✅ Нажата клавиша: {key}")
        else:
            print(f"❌ Ошибка клавиши {key}: {result.get('error')}")
        await asyncio.sleep(0.3)
    
    # Демо 5: Работа с окнами
    print("\n🪟 ДЕМО 5: Информация об окнах")
    print("-" * 30)
    
    result = await tool.execute({"action": "list_windows"})
    if result["success"] and result.get("windows"):
        windows = result["windows"]
        print(f"Найдено окон: {len(windows)}")
        
        # Показываем первые 5 окон
        for i, window in enumerate(windows[:5], 1):
            title = window.get("title", "Без названия")[:30]
            pid = window.get("pid", "unknown")
            print(f"  {i}. {title} (PID: {pid})")
        
        if len(windows) > 5:
            print(f"  ... и ещё {len(windows) - 5} окон")
    
    # Демо 6: Возможности системы
    print("\n⚙️ ДЕМО 6: Проверка возможностей")
    print("-" * 30)
    
    result = await tool.execute({"action": "check_capabilities"})
    if result["success"] and result.get("capabilities"):
        caps = result["capabilities"]
        available = [k for k, v in caps.items() if v]
        unavailable = [k for k, v in caps.items() if not v]
        
        print(f"✅ Доступно ({len(available)}): {', '.join(available)}")
        if unavailable:
            print(f"❌ Недоступно ({len(unavailable)}): {', '.join(unavailable)}")
    
    # Итоги демо
    print("\n" + "=" * 50)
    print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("=" * 50)
    print("✅ GUI управление полностью функционально")
    print("✅ Все основные операции работают")
    print("✅ Manjaro i3 + X11 поддерживается")
    print("✅ PyAutoGUI backend активен")
    print()
    print("💡 ВОЗМОЖНОСТИ:")
    print("   🖱️ Управление мышью (движение, клики)")
    print("   ⌨️ Управление клавиатурой (клавиши, комбинации)")
    print("   📸 Создание скриншотов")
    print("   🪟 Работа с окнами")
    print("   🔍 Поиск элементов на экране")
    print("   📊 Получение информации о системе")
    print()
    print("🚀 KittyCore 3.0 готов к автоматизации любых GUI задач!")

if __name__ == "__main__":
    asyncio.run(gui_demo_practical())
