#!/usr/bin/env python3
"""
🎨 ОТЛАДКА: media_tool
"""

import time
import json
import tempfile
import os
from PIL import Image

try:
    from kittycore.tools.media_tool import MediaTool
    IMPORT_OK = True
    print("✅ Импорт media_tool успешен")
except ImportError as e:
    print(f"❌ ИМПОРТ ОШИБКА: {e}")
    IMPORT_OK = False

def test_get_info():
    """Тест получения информации об инструменте"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📋 Тестирую информацию об инструменте...")
    tool = MediaTool()
    
    result = tool.execute("get_info")
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            if isinstance(data, dict):
                capabilities = data.get('capabilities', {})
                print(f"🛠️ Возможности: {list(capabilities.keys()) if isinstance(capabilities, dict) else 'не dict'}")
    
    return result

def test_list_formats():
    """Тест получения списка поддерживаемых форматов"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📄 Тестирую список форматов...")
    tool = MediaTool()
    
    result = tool.execute("list_formats")
    
    print(f"📊 Результат: {type(result)}")
    if hasattr(result, 'success'):
        print(f"✅ Success: {result.success}")
        if result.success and hasattr(result, 'data'):
            data = result.data
            if isinstance(data, dict):
                image_formats = data.get('image_formats', [])
                print(f"🖼️ Форматов изображений: {len(image_formats)}")
    
    return result

def test_analyze_image():
    """Тест анализа изображения"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n🖼️ Тестирую анализ изображения...")
    tool = MediaTool()
    
    # Создаем простое тестовое изображение
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
        temp_path = f.name
        
        # Создаем простое изображение 100x50 пикселей
        img = Image.new('RGB', (100, 50), color='red')
        img.save(temp_path, 'PNG')
    
    try:
        result = tool.execute("analyze_file", file_path=temp_path)
        
        print(f"📊 Результат: {type(result)}")
        if hasattr(result, 'success'):
            print(f"✅ Success: {result.success}")
            if result.success and hasattr(result, 'data'):
                data = result.data
                if isinstance(data, dict):
                    file_info = data.get('file_info', {})
                    if isinstance(file_info, dict):
                        size_bytes = file_info.get('size_bytes', 0)
                        file_type = file_info.get('type', 'UNKNOWN')
                        print(f"🖼️ Изображение: {size_bytes} байт, тип: {file_type}")
        
        return result
        
    finally:
        # Удаляем временный файл
        try:
            os.unlink(temp_path)
        except:
            pass

def test_extract_metadata():
    """Тест извлечения метаданных"""
    if not IMPORT_OK:
        return "IMPORT_ERROR"
    
    print("\n📋 Тестирую извлечение метаданных...")
    tool = MediaTool()
    
    # Создаем изображение с метаданными
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
        temp_path = f.name
        
        # Создаем изображение и сохраняем как JPEG
        img = Image.new('RGB', (200, 100), color='blue')
        img.save(temp_path, 'JPEG', quality=85)
    
    try:
        result = tool.execute("extract_metadata", file_path=temp_path)
        
        print(f"📊 Результат: {type(result)}")
        if hasattr(result, 'success'):
            print(f"✅ Success: {result.success}")
            if result.success and hasattr(result, 'data'):
                data = result.data
                if isinstance(data, dict):
                    metadata = data.get('metadata', {})
                    print(f"📋 Метаданные: {list(metadata.keys()) if isinstance(metadata, dict) else 'не dict'}")
        
        return result
        
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

def is_result_honest(result, test_name):
    """Проверка честности результата"""
    if not result:
        print(f"❌ {test_name}: Пустой результат")
        return False
    
    # Проверяем базовую структуру ToolResult
    if not hasattr(result, 'success'):
        print(f"❌ {test_name}: Результат не ToolResult")
        return False
    
    success = result.success
    if not success:
        print(f"❌ {test_name}: success=False")
        if hasattr(result, 'error'):
            print(f"   Ошибка: {result.error}")
        return False
    
    # Конвертируем в строку для анализа
    data_str = str(result.data) if hasattr(result, 'data') else str(result)
    data_size = len(data_str)
    
    # Проверка на фейковые паттерны
    fake_patterns = [
        "media_tool: успешно",
        "демо изображение",
        "заглушка медиа"
    ]
    
    for pattern in fake_patterns:
        if pattern.lower() in data_str.lower():
            print(f"❌ {test_name}: Найден фейковый паттерн: {pattern}")
            return False
    
    # Проверка на реальные признаки обработки медиа
    media_indicators = [
        "image", "video", "audio", "metadata", "size", "format", "width", "height",
        "capabilities", "PIL", "bytes", "formats", "type", "изображение"
    ]
    
    has_media_data = any(indicator.lower() in data_str.lower() for indicator in media_indicators)
    
    if not has_media_data:
        print(f"❌ {test_name}: Нет признаков реальной обработки медиа")
        return False
    
    if data_size < 40:
        print(f"❌ {test_name}: Слишком маленький результат ({data_size} байт)")
        return False
    
    print(f"✅ {test_name}: ЧЕСТНЫЙ результат ({data_size} байт)")
    return True

def main():
    print("🎨 ОТЛАДКА: media_tool")
    
    if not IMPORT_OK:
        return
    
    results = {}
    
    # Тесты (все синхронные)
    tests = [
        ("get_info", test_get_info),
        ("list_formats", test_list_formats),
        ("analyze_image", test_analyze_image),
        ("extract_metadata", test_extract_metadata)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*30}")
        print(f"ТЕСТ: {test_name}")
        try:
            result = test_func()
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
    main() 