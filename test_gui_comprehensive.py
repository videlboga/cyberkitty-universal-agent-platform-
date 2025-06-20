#!/usr/bin/env python3
"""
Comprehensive тест GUI управления KittyCore 3.0
Проверяет все возможности ComputerUseTool
"""

import sys
import asyncio
import time
import os
from pathlib import Path

# Добавляем путь к KittyCore
sys.path.append('.')

from kittycore.tools.computer_use_tool import ComputerUseTool

async def test_gui_comprehensive():
    """Полный тест GUI управления"""
    
    print("🖥️ COMPREHENSIVE ТЕСТ GUI УПРАВЛЕНИЯ KITTYCORE 3.0")
    print("=" * 60)
    
    tool = ComputerUseTool()
    start_time = time.time()
    
    tests = [
        # Информационные тесты
        ("test_environment", {}, "🔍 Тест среды"),
        ("get_screen_info", {}, "📺 Информация о экране"),
        ("get_mouse_position", {}, "🖱️ Позиция мыши"),
        ("check_capabilities", {}, "⚙️ Проверка возможностей"),
        
        # Скриншот
        ("screenshot", {"save_path": "/tmp/gui_test_screenshot.png"}, "📸 Скриншот"),
        
        # Движение мыши (безопасно)
        ("mouse_move", {"x": 100, "y": 100}, "🖱️ Движение мыши"),
        ("get_mouse_position", {}, "🖱️ Позиция после движения"),
        
        # Клавиатура (безопасно)
        ("key_press", {"key": "space"}, "⌨️ Нажатие пробела"),
        ("key_combination", {"keys": ["ctrl", "alt", "t"]}, "⌨️ Комбинация клавиш"),
        
        # Работа с окнами
        ("list_windows", {}, "🪟 Список окон"),
        ("get_active_window", {}, "🪟 Активное окно"),
    ]
    
    results = []
    
    for i, (action, params, description) in enumerate(tests, 1):
        print(f"\n[{i:2d}/12] {description}")
        print("-" * 40)
        
        try:
            test_start = time.time()
            result = await tool.execute({"action": action, **params})
            test_time = time.time() - test_start
            
            success = result.get("success", False)
            status = "✅ УСПЕХ" if success else "❌ ОШИБКА"
            
            print(f"Статус: {status} ({test_time:.3f}с)")
            
            # Детальная информация
            if success:
                if action == "test_environment" and result.get("details"):
                    details = result["details"]
                    print(f"  Backend: {details.get('backend', 'unknown')}")
                    print(f"  Platform: {details.get('platform', 'unknown')}")
                    print(f"  X11: {details.get('has_x11', False)}")
                    print(f"  WM: {details.get('wm_name', 'unknown')}")
                    
                elif action == "get_screen_info" and result.get("screen_info"):
                    info = result["screen_info"]
                    print(f"  Размер: {info.get('width', 0)}x{info.get('height', 0)}")
                    print(f"  Масштаб: {info.get('scale_factor', 1.0)}")
                    
                elif action == "get_mouse_position" and result.get("position"):
                    pos = result["position"]
                    print(f"  Координаты: ({pos.get('x', 0)}, {pos.get('y', 0)})")
                    
                elif action == "screenshot" and result.get("screenshot_path"):
                    path = result["screenshot_path"]
                    if os.path.exists(path):
                        size = os.path.getsize(path)
                        print(f"  Файл: {path}")
                        print(f"  Размер: {size:,} байт")
                    
                elif action == "check_capabilities" and result.get("capabilities"):
                    caps = result["capabilities"]
                    available = [k for k, v in caps.items() if v]
                    print(f"  Доступно: {', '.join(available)}")
                    
                elif action == "list_windows" and result.get("windows"):
                    windows = result["windows"]
                    print(f"  Найдено окон: {len(windows)}")
                    if windows:
                        for w in windows[:3]:  # Показываем первые 3
                            print(f"    - {w.get('title', 'Без названия')[:30]}")
                        if len(windows) > 3:
                            print(f"    ... и ещё {len(windows) - 3}")
                            
                elif action == "get_active_window" and result.get("window"):
                    window = result["window"]
                    print(f"  Активное: {window.get('title', 'Без названия')[:40]}")
                    print(f"  PID: {window.get('pid', 'unknown')}")
                    
                else:
                    # Общая информация
                    data_size = len(str(result))
                    print(f"  Данные: {data_size} символов")
            else:
                error = result.get("error", "Неизвестная ошибка")
                print(f"  Ошибка: {error}")
            
            results.append({
                "test": description,
                "action": action,
                "success": success,
                "time": test_time,
                "data_size": len(str(result))
            })
            
        except Exception as e:
            print(f"❌ ИСКЛЮЧЕНИЕ: {e}")
            results.append({
                "test": description,
                "action": action, 
                "success": False,
                "time": 0,
                "error": str(e)
            })
        
        # Небольшая пауза между тестами
        await asyncio.sleep(0.1)
    
    # Итоговая статистика
    total_time = time.time() - start_time
    successful = len([r for r in results if r["success"]])
    
    print("\n" + "=" * 60)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 60)
    print(f"✅ Успешных тестов: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    print(f"⏱️ Общее время: {total_time:.3f}с")
    print(f"⚡ Среднее время на тест: {total_time/len(results):.3f}с")
    
    # Детальные результаты
    print(f"\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
    for i, result in enumerate(results, 1):
        status = "✅" if result["success"] else "❌"
        time_str = f"{result['time']:.3f}с"
        print(f"{i:2d}. {status} {result['test']:<25} {time_str:>8}")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    if successful == len(results):
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! GUI управление работает отлично!")
    elif successful >= len(results) * 0.8:
        print("✅ Большинство функций работает. Проверьте отдельные ошибки.")
    else:
        print("⚠️ Много ошибок. Возможно нужно установить дополнительные зависимости.")
        
    failed_tests = [r for r in results if not r["success"]]
    if failed_tests:
        print(f"\n❌ ПРОБЛЕМНЫЕ ТЕСТЫ:")
        for test in failed_tests:
            print(f"  - {test['test']}: {test.get('error', 'Неизвестная ошибка')}")
    
    return successful, len(results)

if __name__ == "__main__":
    asyncio.run(test_gui_comprehensive())
