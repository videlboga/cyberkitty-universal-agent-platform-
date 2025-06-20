#!/usr/bin/env python3
"""
🖥️ ОТЛАДКА: computer_use_tool
"""

import asyncio
import time
import json

try:
    from kittycore.tools.computer_use_tool import ComputerUseTool
    IMPORT_OK = True
    print("✅ Импорт computer_use_tool успешен")
except ImportError as e:
    print(f"❌ ИМПОРТ ОШИБКА: {e}")
    IMPORT_OK = False

async def test_environment_info():
    """Тест получения информации о среде"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🖥️ Тестирую информацию о среде...")
    tool = ComputerUseTool()
    
    # ВАЖНО: ComputerUseTool асинхронный
    result = await tool.execute({
        'action': 'test_environment'
    })
    
    print(f"📊 Результат: {type(result)}")
    if isinstance(result, dict):
        success = result.get('success', False)
        print(f"✅ Success: {success}")
        
        if success:
            data = result.get('details', {})
            if isinstance(data, dict):
                # Проверяем ключевую информацию о среде
                env_fields = ['platform', 'backend', 'has_display', 'window_manager']
                found_fields = [field for field in env_fields if field in data]
                print(f"🔑 Найдено полей среды: {len(found_fields)}/{len(env_fields)}")
                
                if 'platform' in data:
                    print(f"   Platform: {data['platform']}")
                if 'backend' in data:
                    print(f"   Backend: {data['backend']}")
        else:
            error = result.get('error_message', 'НЕИЗВЕСТНО')
            print(f"❌ Ошибка: {error}")
    
    return result

async def test_capabilities():
    """Тест проверки возможностей инструмента"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🔧 Тестирую возможности инструмента...")
    tool = ComputerUseTool()
    
    result = await tool.execute({
        'action': 'check_capabilities'
    })
    
    print(f"📊 Результат: {type(result)}")
    if isinstance(result, dict):
        success = result.get('success', False)
        print(f"✅ Success: {success}")
        
        if success:
            details = result.get('details', {})
            if isinstance(details, dict):
                capabilities = details.get('capabilities', {})
                print(f"🛠️ Возможности: {list(capabilities.keys()) if isinstance(capabilities, dict) else 'не dict'}")
    
    return result

async def test_screen_info():
    """Тест получения информации об экране"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📺 Тестирую информацию об экране...")
    tool = ComputerUseTool()
    
    result = await tool.execute({
        'action': 'get_screen_info'
    })
    
    print(f"📊 Результат: {type(result)}")
    if isinstance(result, dict):
        success = result.get('success', False)
        print(f"✅ Success: {success}")
        
        if success:
            details = result.get('details', {})
            if isinstance(details, dict):
                screen_info = details.get('screen_info', {})
                if isinstance(screen_info, dict):
                    width = screen_info.get('width', 'НЕТ')
                    height = screen_info.get('height', 'НЕТ')
                    print(f"📺 Разрешение: {width}x{height}")
    
    return result

async def test_mouse_position():
    """Тест получения позиции мыши"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🖱️ Тестирую позицию мыши...")
    tool = ComputerUseTool()
    
    result = await tool.execute({
        'action': 'get_mouse_position'
    })
    
    print(f"📊 Результат: {type(result)}")
    if isinstance(result, dict):
        success = result.get('success', False)
        print(f"✅ Success: {success}")
        
        if success:
            details = result.get('details', {})
            if isinstance(details, dict):
                position = details.get('position', {})
                if isinstance(position, dict):
                    x = position.get('x', 'НЕТ')
                    y = position.get('y', 'НЕТ')
                    print(f"🖱️ Позиция мыши: ({x}, {y})")
    
    return result

def is_result_honest(result, test_name):
    """Проверка честности результата"""
    if not result:
        print(f"❌ {test_name}: Пустой результат")
        return False
    
    if not isinstance(result, dict):
        print(f"❌ {test_name}: Результат не словарь")
        return False
    
    success = result.get('success', False)
    if not success:
        print(f"❌ {test_name}: success=False")
        error = result.get('error_message', 'НЕИЗВЕСТНО')
        print(f"   Ошибка: {error}")
        return False
    
    data_str = str(result)
    data_size = len(data_str)
    
    # Проверка на фейковые паттерны
    fake_patterns = [
        "computer_use: успешно",
        "демо gui",
        "заглушка экрана"
    ]
    
    for pattern in fake_patterns:
        if pattern.lower() in data_str.lower():
            print(f"❌ {test_name}: Найден фейковый паттерн: {pattern}")
            return False
    
    # Проверка на реальные признаки GUI автоматизации
    gui_indicators = [
        "screen", "mouse", "keyboard", "window", "display", "backend", 
        "platform", "width", "height", "position", "x11", "capabilities"
    ]
    
    has_gui_data = any(indicator.lower() in data_str.lower() for indicator in gui_indicators)
    
    if not has_gui_data:
        print(f"❌ {test_name}: Нет признаков реальной GUI автоматизации")
        return False
    
    if data_size < 50:
        print(f"❌ {test_name}: Слишком маленький результат ({data_size} байт)")
        return False
    
    print(f"✅ {test_name}: ЧЕСТНЫЙ результат ({data_size} байт)")
    return True

async def main():
    print("🖥️ ОТЛАДКА: computer_use_tool")
    
    if not IMPORT_OK:
        return
    
    results = {}
    
    # Тесты (все асинхронные, без GUI операций)
    tests = [
        ("environment_info", test_environment_info),
        ("capabilities", test_capabilities),
        ("screen_info", test_screen_info),
        ("mouse_position", test_mouse_position)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*30}")
        print(f"ТЕСТ: {test_name}")
        try:
            result = await test_func()
            results[test_name] = is_result_honest(result, test_name)
        except Exception as e:
            print(f"❌ ТЕСТ ОШИБКА: {e}")
            results[test_name] = False
    
    # Итоги
    print(f"\n{'='*50}")
    print("📊 ИТОГИ:")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Всего тестов: {total_tests}")
    print(f"Прошло тестов: {passed_tests}")
    print(f"Процент успеха: {success_rate:.1f}%")
    
    for test_name, success in results.items():
        status = "✅ ПРОШЕЛ" if success else "❌ ПРОВАЛЕН"
        print(f"  {test_name}: {status}")
    
    print(f"\n📊 Статус: {'✅ РАБОТАЕТ' if success_rate >= 75 else '❌ НЕ РАБОТАЕТ'}")

if __name__ == "__main__":
    asyncio.run(main()) 