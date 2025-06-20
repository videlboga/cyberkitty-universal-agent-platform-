#!/usr/bin/env python3
"""
ИСПРАВЛЕННЫЙ ВИЗУАЛЬНЫЙ ТЕСТ ИНСТРУМЕНТОВ KITTYCORE 3.0 - ЧАСТЬ 1
Базовые инструменты с наглядными результатами (правильные вызовы)
"""

import sys
import asyncio
import time
import os
from pathlib import Path

sys.path.append('.')

async def test_part1_basic_tools_fixed():
    """Тест базовых инструментов с правильными вызовами"""
    
    print("🔧 ИСПРАВЛЕННЫЙ ВИЗУАЛЬНЫЙ ТЕСТ - ЧАСТЬ 1")
    print("=" * 50)
    print("📋 ТЕСТИРУЕМ: MediaTool, SuperSystemTool, APIRequest")
    print()
    
    # 1. MEDIA TOOL - обработка изображений
    print("🎨 [1/3] MEDIA TOOL - Обработка изображений")
    print("-" * 40)
    
    try:
        from kittycore.tools.media_tool import MediaTool
        media_tool = MediaTool()
        
        # Создаём тестовое изображение
        test_image_path = "/tmp/test_kittycore_image.png"
        
        # Создаём простое изображение с помощью PIL
        from PIL import Image, ImageDraw
        
        # Создаём изображение 400x300 с градиентом
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Рисуем простые фигуры
        draw.rectangle([50, 50, 150, 150], fill='red', outline='black', width=3)
        draw.ellipse([200, 50, 350, 200], fill='green', outline='blue', width=3)
        draw.text((50, 200), "KittyCore 3.0", fill='black')
        
        img.save(test_image_path)
        print(f"✅ Создано тестовое изображение: {test_image_path}")
        
        # Тест 1: Анализ файла (ПРАВИЛЬНЫЙ ВЫЗОВ)
        result = media_tool.execute("analyze_file", file_path=test_image_path)
        
        if result.success:
            file_info = result.data.get("file_info", {})
            print(f"📊 АНАЛИЗ ИЗОБРАЖЕНИЯ:")
            print(f"   Имя: {file_info.get('name', 'unknown')}")
            print(f"   Размер: {file_info.get('size_human', 'unknown')}")
            print(f"   Тип: {file_info.get('type', 'unknown')}")
            
            specific_info = result.data.get("specific_info", {})
            if specific_info:
                print(f"   Разрешение: {specific_info.get('width', 0)}x{specific_info.get('height', 0)}")
                print(f"   Формат: {specific_info.get('format', 'unknown')}")
        else:
            print(f"❌ Ошибка анализа: {result.error}")
        
        # Тест 2: Изменение размера
        resized_path = "/tmp/test_kittycore_resized.png"
        result = media_tool.execute("resize_image", 
                                  file_path=test_image_path,
                                  output_path=resized_path,
                                  width=200, height=150)
        
        if result.success:
            print(f"✅ Изображение изменено: {resized_path}")
            if os.path.exists(resized_path):
                size = os.path.getsize(resized_path)
                print(f"   Новый размер файла: {size:,} байт")
        else:
            print(f"❌ Ошибка изменения размера: {result.error}")
        
        await asyncio.sleep(0.5)
        
    except Exception as e:
        print(f"❌ ОШИБКА MediaTool: {e}")
    
    print()
    
    # 2. SUPER SYSTEM TOOL - системные операции
    print("🚀 [2/3] SUPER SYSTEM TOOL - Системные операции")
    print("-" * 40)
    
    try:
        from kittycore.tools.super_system_tool import SuperSystemTool
        system_tool = SuperSystemTool()
        
        # Тест 1: Информация о системе (ПРАВИЛЬНЫЙ ВЫЗОВ)
        result = system_tool.execute("get_system_info")
        
        if result.success:
            info = result.data
            print(f"💻 ИНФОРМАЦИЯ О СИСТЕМЕ:")
            print(f"   ОС: {info.get('platform', 'unknown')}")
            print(f"   Архитектура: {info.get('architecture', 'unknown')}")
            print(f"   Процессор: {info.get('processor', 'unknown')[:50]}...")
            
            memory = info.get('memory', {})
            if memory:
                total_gb = memory.get('total', 0) / (1024**3)
                available_gb = memory.get('available', 0) / (1024**3)
                print(f"   Память: {available_gb:.1f} ГБ доступно из {total_gb:.1f} ГБ")
        else:
            print(f"❌ Ошибка получения системной информации: {result.error}")
        
        # Тест 2: Создание файла
        test_file_path = "/tmp/kittycore_system_test.txt"
        test_content = f"KittyCore 3.0 System Test\nВремя создания: {time.strftime('%Y-%m-%d %H:%M:%S')}\nТест успешен!"
        
        result = system_tool.execute("create_file", 
                                   file_path=test_file_path,
                                   content=test_content)
        
        if result.success:
            print(f"✅ Файл создан: {test_file_path}")
            if os.path.exists(test_file_path):
                with open(test_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"   Содержимое ({len(content)} символов):")
                for line in content.split('\n')[:2]:
                    print(f"   > {line}")
        else:
            print(f"❌ Ошибка создания файла: {result.error}")
        
        # Тест 3: Выполнение команды
        result = system_tool.execute("execute_command", 
                                   command="echo 'KittyCore тест: $(date +%H:%M:%S)'")
        
        if result.success:
            output = result.data.get("stdout", "").strip()
            print(f"✅ Команда выполнена:")
            print(f"   Вывод: {output}")
        else:
            print(f"❌ Ошибка выполнения команды: {result.error}")
        
        await asyncio.sleep(0.5)
        
    except Exception as e:
        print(f"❌ ОШИБКА SuperSystemTool: {e}")
    
    print()
    
    # 3. API REQUEST TOOL - веб-запросы
    print("🌐 [3/3] API REQUEST TOOL - Веб-запросы")
    print("-" * 40)
    
    try:
        from kittycore.tools.api_request_tool import ApiRequestTool
        api_tool = ApiRequestTool()
        
        # Тест 1: GET запрос к httpbin.org
        result = api_tool.execute("get", url="https://httpbin.org/json")
        
        if result.success:
            data = result.data
            print(f"✅ GET запрос выполнен:")
            print(f"   Статус: {data.get('status_code', 'unknown')}")
            print(f"   Размер ответа: {len(str(data.get('response', {})))} символов")
            
            # Показываем часть данных
            response_data = data.get("response", {})
            if isinstance(response_data, dict):
                keys = list(response_data.keys())[:3]
                print(f"   Ключи ответа: {keys}")
        else:
            print(f"❌ Ошибка GET запроса: {result.error}")
        
        # Тест 2: POST запрос
        test_data = {
            "test": "KittyCore 3.0",
            "timestamp": str(int(time.time())),
            "message": "Тест POST запроса"
        }
        
        result = api_tool.execute("post", 
                                url="https://httpbin.org/post",
                                json_data=test_data)
        
        if result.success:
            data = result.data
            print(f"✅ POST запрос выполнен:")
            print(f"   Статус: {data.get('status_code', 'unknown')}")
            
            # Показываем отправленные данные
            response = data.get("response", {})
            sent_json = response.get("json", {})
            if sent_json:
                print(f"   Отправлено: {sent_json.get('test', 'unknown')} в {sent_json.get('timestamp', 'unknown')}")
        else:
            print(f"❌ Ошибка POST запроса: {result.error}")
        
        await asyncio.sleep(0.5)
        
    except Exception as e:
        print(f"❌ ОШИБКА APIRequestTool: {e}")
    
    # ИТОГИ ЧАСТИ 1
    print("\n" + "=" * 50)
    print("📊 ИТОГИ ЧАСТИ 1 - БАЗОВЫЕ ИНСТРУМЕНТЫ")
    print("=" * 50)
    print("🎨 MediaTool: Обработка изображений и анализ файлов")
    print("🚀 SuperSystemTool: Системная информация и файловые операции") 
    print("🌐 ApiRequestTool: GET/POST запросы и веб-интеграция")
    print()
    print("💡 Проверьте созданные файлы:")
    print(f"   📸 Тестовое изображение: /tmp/test_kittycore_image.png")
    print(f"   📸 Уменьшенное изображение: /tmp/test_kittycore_resized.png")
    print(f"   📄 Системный тест-файл: /tmp/kittycore_system_test.txt")
    print()
    print("🔄 Готов к части 2 (веб-инструменты)...")

if __name__ == "__main__":
    asyncio.run(test_part1_basic_tools_fixed())
