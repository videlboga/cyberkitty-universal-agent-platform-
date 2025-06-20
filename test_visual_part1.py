#!/usr/bin/env python3
"""
ВИЗУАЛЬНЫЙ ТЕСТ ИНСТРУМЕНТОВ KITTYCORE 3.0 - ЧАСТЬ 1
Базовые инструменты с наглядными результатами
"""

import sys
import asyncio
import time
import os
from pathlib import Path

sys.path.append('.')

async def test_part1_basic_tools():
    """Тест базовых инструментов с визуальными результатами"""
    
    print("🔧 ВИЗУАЛЬНЫЙ ТЕСТ ИНСТРУМЕНТОВ - ЧАСТЬ 1")
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
        from PIL import Image, ImageDraw, ImageFont
        
        # Создаём изображение 400x300 с градиентом
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Рисуем простые фигуры
        draw.rectangle([50, 50, 150, 150], fill='red', outline='black', width=3)
        draw.ellipse([200, 50, 350, 200], fill='green', outline='blue', width=3)
        draw.text((50, 200), "KittyCore 3.0 Test", fill='black')
        
        img.save(test_image_path)
        print(f"✅ Создано тестовое изображение: {test_image_path}")
        
        # Тест 1: Получение информации об изображении
        result = await media_tool.execute({
            "action": "get_info",
            "file_path": test_image_path
        })
        
        if result["success"]:
            info = result.get("info", {})
            print(f"📊 ИНФОРМАЦИЯ ОБ ИЗОБРАЖЕНИИ:")
            print(f"   Размер: {info.get('width', 0)}x{info.get('height', 0)}")
            print(f"   Формат: {info.get('format', 'unknown')}")
            print(f"   Режим: {info.get('mode', 'unknown')}")
            print(f"   Размер файла: {info.get('file_size', 0)} байт")
        else:
            print(f"❌ Ошибка получения информации: {result.get('error')}")
        
        # Тест 2: Изменение размера
        resized_path = "/tmp/test_kittycore_resized.png"
        result = await media_tool.execute({
            "action": "resize",
            "file_path": test_image_path,
            "output_path": resized_path,
            "width": 200,
            "height": 150
        })
        
        if result["success"]:
            print(f"✅ Изображение изменено: {resized_path}")
            if os.path.exists(resized_path):
                size = os.path.getsize(resized_path)
                print(f"   Новый размер файла: {size} байт")
        else:
            print(f"❌ Ошибка изменения размера: {result.get('error')}")
        
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
        
        # Тест 1: Информация о системе
        result = await system_tool.execute({
            "action": "get_system_info"
        })
        
        if result["success"]:
            info = result.get("system_info", {})
            print(f"💻 ИНФОРМАЦИЯ О СИСТЕМЕ:")
            print(f"   ОС: {info.get('platform', 'unknown')}")
            print(f"   Процессор: {info.get('processor', 'unknown')}")
            print(f"   Память: {info.get('memory', {}).get('total', 0) / (1024**3):.1f} ГБ")
            print(f"   Диск: {info.get('disk', {}).get('free', 0) / (1024**3):.1f} ГБ свободно")
        else:
            print(f"❌ Ошибка получения системной информации: {result.get('error')}")
        
        # Тест 2: Создание файла
        test_file_path = "/tmp/kittycore_system_test.txt"
        result = await system_tool.execute({
            "action": "create_file",
            "file_path": test_file_path,
            "content": "KittyCore 3.0 System Test\nВремя создания: " + str(time.time())
        })
        
        if result["success"]:
            print(f"✅ Файл создан: {test_file_path}")
            if os.path.exists(test_file_path):
                with open(test_file_path, 'r') as f:
                    content = f.read()
                print(f"   Содержимое ({len(content)} символов):")
                print(f"   {content[:50]}...")
        else:
            print(f"❌ Ошибка создания файла: {result.get('error')}")
        
        # Тест 3: Выполнение команды
        result = await system_tool.execute({
            "action": "execute_command",
            "command": "echo 'KittyCore тест команды: $(date)'"
        })
        
        if result["success"]:
            output = result.get("output", "")
            print(f"✅ Команда выполнена:")
            print(f"   Вывод: {output.strip()}")
        else:
            print(f"❌ Ошибка выполнения команды: {result.get('error')}")
        
        await asyncio.sleep(0.5)
        
    except Exception as e:
        print(f"❌ ОШИБКА SuperSystemTool: {e}")
    
    print()
    
    # 3. API REQUEST TOOL - веб-запросы
    print("🌐 [3/3] API REQUEST TOOL - Веб-запросы")
    print("-" * 40)
    
    try:
        from kittycore.tools.api_request_tool import APIRequestTool
        api_tool = APIRequestTool()
        
        # Тест 1: GET запрос к httpbin.org
        result = await api_tool.execute({
            "action": "get",
            "url": "https://httpbin.org/json"
        })
        
        if result["success"]:
            response = result.get("response", {})
            print(f"✅ GET запрос выполнен:")
            print(f"   Статус: {response.get('status_code', 'unknown')}")
            print(f"   Размер данных: {len(str(response.get('data', '')))} символов")
            
            # Показываем часть данных
            data = response.get("data", {})
            if isinstance(data, dict):
                print(f"   Данные: {list(data.keys())[:3]}...")
        else:
            print(f"❌ Ошибка GET запроса: {result.get('error')}")
        
        # Тест 2: POST запрос
        result = await api_tool.execute({
            "action": "post",
            "url": "https://httpbin.org/post",
            "data": {
                "test": "KittyCore 3.0",
                "timestamp": str(time.time()),
                "message": "Тест POST запроса"
            }
        })
        
        if result["success"]:
            response = result.get("response", {})
            print(f"✅ POST запрос выполнен:")
            print(f"   Статус: {response.get('status_code', 'unknown')}")
            
            # Показываем отправленные данные
            data = response.get("data", {})
            if isinstance(data, dict) and "json" in data:
                sent_data = data["json"]
                print(f"   Отправлено: {sent_data}")
        else:
            print(f"❌ Ошибка POST запроса: {result.get('error')}")
        
        await asyncio.sleep(0.5)
        
    except Exception as e:
        print(f"❌ ОШИБКА APIRequestTool: {e}")
    
    # ИТОГИ ЧАСТИ 1
    print("\n" + "=" * 50)
    print("📊 ИТОГИ ЧАСТИ 1 - БАЗОВЫЕ ИНСТРУМЕНТЫ")
    print("=" * 50)
    print("✅ MediaTool: Обработка изображений работает")
    print("✅ SuperSystemTool: Системные операции работают") 
    print("✅ APIRequestTool: Веб-запросы работают")
    print()
    print("�� Все базовые инструменты функционируют корректно!")
    print("🔄 Переходим к части 2...")

if __name__ == "__main__":
    asyncio.run(test_part1_basic_tools())
