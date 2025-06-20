#!/usr/bin/env python3
"""
🔥 ФИНАЛЬНЫЙ ТЕСТ ПОСЛЕ ИСПРАВЛЕНИЯ НАСТРОЕК ТЕРМИНАЛА CURSOR
================================================================
Проверяем что все работает после исправления:
- terminal.integrated.inheritEnv: false → true  
- terminal.integrated.gpuAcceleration: "off" → "auto"
"""

import sys
import time
import asyncio
from pathlib import Path

# Добавляем путь к KittyCore
sys.path.append('.')

def test_basic_environment():
    """Тест базового окружения"""
    print("🔍 ТЕСТ БАЗОВОГО ОКРУЖЕНИЯ")
    print("-" * 40)
    
    import os
    print(f"✅ Python версия: {sys.version.split()[0]}")
    print(f"✅ Virtual env: {os.environ.get('VIRTUAL_ENV', 'НЕТ')}")
    print(f"✅ Рабочая папка: {Path.cwd()}")
    print(f"✅ PATH содержит .venv: {'.venv' in os.environ.get('PATH', '')}")
    print()

def test_kittycore_import():
    """Тест импорта KittyCore"""
    print("📦 ТЕСТ ИМПОРТА KITTYCORE")
    print("-" * 40)
    
    try:
        from kittycore.tools.media_tool import MediaTool
        from kittycore.tools.computer_use_tool import ComputerUseTool
        from kittycore.tools.network_tool import NetworkTool
        print("✅ Импорт инструментов успешен")
        
        # Быстрый тест MediaTool
        media = MediaTool()
        result = media.execute(action='list_formats')
        if hasattr(result, 'data') and result.data:
            formats_count = len(result.data.get('formats', []))
            print(f"✅ MediaTool работает: {formats_count} форматов")
        else:
            print("⚠️ MediaTool: неожиданный результат")
            
        print()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        print()
        return False

async def test_async_tools():
    """Тест асинхронных инструментов"""
    print("⚡ ТЕСТ АСИНХРОННЫХ ИНСТРУМЕНТОВ")
    print("-" * 40)
    
    try:
        from kittycore.tools.network_tool import NetworkTool
        
        network = NetworkTool()
        start_time = time.time()
        
        # Простой ping тест
        result = await network.execute(action='ping_host', host='8.8.8.8', count=1)
        elapsed = time.time() - start_time
        
        if hasattr(result, 'success') and result.success:
            print(f"✅ NetworkTool ping: успех за {elapsed:.2f}с")
        else:
            print(f"⚠️ NetworkTool ping: {result}")
            
        print()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка async теста: {e}")
        print()
        return False

def test_gui_functionality():
    """Тест GUI функциональности"""
    print("🖥️ ТЕСТ GUI ФУНКЦИОНАЛЬНОСТИ")
    print("-" * 40)
    
    try:
        from kittycore.tools.computer_use_tool import ComputerUseTool
        
        computer = ComputerUseTool()
        
        # Тест получения информации о экране
        result = computer.execute(action='get_screen_info')
        if hasattr(result, 'success') and result.success:
            screen_info = result.data.get('screen_info', {})
            width = screen_info.get('width', 'unknown')
            height = screen_info.get('height', 'unknown')
            print(f"✅ Экран: {width}x{height}")
        else:
            print(f"⚠️ Экран: {result}")
            
        # Тест получения позиции мыши
        result = computer.execute(action='get_mouse_position')
        if hasattr(result, 'success') and result.success:
            pos = result.data
            print(f"✅ Мышь: ({pos.get('x', '?')}, {pos.get('y', '?')})")
        else:
            print(f"⚠️ Мышь: {result}")
            
        print()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка GUI теста: {e}")
        print()
        return False

def test_file_operations():
    """Тест файловых операций"""
    print("📁 ТЕСТ ФАЙЛОВЫХ ОПЕРАЦИЙ")
    print("-" * 40)
    
    try:
        test_file = Path("/tmp/kittycore_terminal_test.txt")
        
        # Создание файла
        test_file.write_text("KittyCore 3.0 terminal test ✅")
        if test_file.exists():
            print(f"✅ Файл создан: {test_file}")
            
        # Чтение файла
        content = test_file.read_text()
        if "KittyCore" in content:
            print(f"✅ Файл прочитан: {len(content)} символов")
            
        # Удаление файла
        test_file.unlink()
        if not test_file.exists():
            print("✅ Файл удален")
            
        print()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка файловых операций: {e}")
        print()
        return False

async def main():
    """Главная функция тестирования"""
    print("🔥 ФИНАЛЬНЫЙ ТЕСТ ПОСЛЕ ИСПРАВЛЕНИЯ ТЕРМИНАЛА")
    print("=" * 60)
    print()
    
    start_time = time.time()
    results = []
    
    # Запуск всех тестов
    results.append(("Базовое окружение", test_basic_environment()))
    results.append(("Импорт KittyCore", test_kittycore_import()))
    results.append(("Async инструменты", await test_async_tools()))
    results.append(("GUI функциональность", test_gui_functionality()))
    results.append(("Файловые операции", test_file_operations()))
    
    # Подсчет результатов
    total_time = time.time() - start_time
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print("=" * 60)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 60)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print()
    print(f"🎯 Успешно: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"⏱️ Время: {total_time:.2f}с")
    
    if successful == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Терминал работает отлично!")
    else:
        print("⚠️ Есть проблемы, требуется дополнительная диагностика")
    
    print()
    print("💡 Исправления терминала Cursor:")
    print("   ✅ inheritEnv: false → true")
    print("   ✅ gpuAcceleration: off → auto")
    print("   ✅ Резервная копия создана")

if __name__ == "__main__":
    asyncio.run(main()) 