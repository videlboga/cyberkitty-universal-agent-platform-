#!/usr/bin/env python3
"""
ИНДИВИДУАЛЬНЫЙ ТЕСТ КАЖДОГО ИНСТРУМЕНТА
Простая проверка каждого инструмента отдельно
"""

import sys
import time
sys.path.append('.')

def test_media_tool():
    """Тест MediaTool"""
    print("🎨 ТЕСТ MEDIA TOOL")
    print("-" * 30)
    
    try:
        from kittycore.tools.media_tool import MediaTool
        tool = MediaTool()
        
        # Простой тест - список форматов
        result = tool.execute("list_formats")
        
        if result.success:
            formats = result.data
            print(f"✅ MediaTool работает!")
            print(f"   Поддерживаемые форматы: {len(formats.get('image_formats', []))} изображений")
            print(f"   Возможности: {list(formats.get('capabilities', {}).keys())}")
        else:
            print(f"❌ Ошибка: {result.error}")
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
    
    print()

def test_super_system_tool():
    """Тест SuperSystemTool"""
    print("🚀 ТЕСТ SUPER SYSTEM TOOL")
    print("-" * 30)
    
    try:
        from kittycore.tools.super_system_tool import SuperSystemTool
        tool = SuperSystemTool()
        
        # Простой тест - выполнение команды
        result = tool.execute("execute_command", command="echo 'KittyCore тест'")
        
        if result.success:
            output = result.data.get("stdout", "").strip()
            print(f"✅ SuperSystemTool работает!")
            print(f"   Команда выполнена: {output}")
            print(f"   Код возврата: {result.data.get('returncode', 'unknown')}")
        else:
            print(f"❌ Ошибка: {result.error}")
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
    
    print()

def test_api_request_tool():
    """Тест ApiRequestTool"""
    print("🌐 ТЕСТ API REQUEST TOOL")
    print("-" * 30)
    
    try:
        from kittycore.tools.api_request_tool import ApiRequestTool
        tool = ApiRequestTool()
        
        # Простой тест - GET запрос
        result = tool.execute("get", url="https://httpbin.org/uuid")
        
        if result.success:
            status = result.data.get("status_code", "unknown")
            print(f"✅ ApiRequestTool работает!")
            print(f"   HTTP статус: {status}")
            print(f"   Размер ответа: {len(str(result.data))} символов")
            
            # Показываем UUID из ответа
            response = result.data.get("response", {})
            if "uuid" in response:
                print(f"   UUID: {response['uuid'][:8]}...")
        else:
            print(f"❌ Ошибка: {result.error}")
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
    
    print()

def test_network_tool():
    """Тест NetworkTool"""
    print("🌐 ТЕСТ NETWORK TOOL")
    print("-" * 30)
    
    try:
        from kittycore.tools.network_tool import NetworkTool
        tool = NetworkTool()
        
        # Простой тест - ping
        result = tool.execute("ping_host", host="8.8.8.8", count=2)
        
        if result.success:
            ping_data = result.data
            print(f"✅ NetworkTool работает!")
            print(f"   Ping 8.8.8.8: {ping_data.get('success', False)}")
            print(f"   Среднее время: {ping_data.get('avg_time', 0):.1f}мс")
        else:
            print(f"❌ Ошибка: {result.error}")
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
    
    print()

def test_security_tool():
    """Тест SecurityTool"""
    print("🔒 ТЕСТ SECURITY TOOL")
    print("-" * 30)
    
    try:
        from kittycore.tools.security_tool import SecurityTool
        tool = SecurityTool()
        
        # Простой тест - анализ пароля
        result = tool.execute("analyze_password", password="TestPassword123!")
        
        if result.success:
            analysis = result.data
            print(f"✅ SecurityTool работает!")
            print(f"   Сила пароля: {analysis.get('strength', 'unknown')}")
            print(f"   Оценка: {analysis.get('score', 0)}/100")
        else:
            print(f"❌ Ошибка: {result.error}")
            
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
    
    print()

if __name__ == "__main__":
    print("🧪 ИНДИВИДУАЛЬНЫЙ ТЕСТ ИНСТРУМЕНТОВ KITTYCORE 3.0")
    print("=" * 55)
    print()
    
    # Тестируем каждый инструмент отдельно
    test_media_tool()
    test_super_system_tool()
    test_api_request_tool()
    test_network_tool()
    test_security_tool()
    
    print("=" * 55)
    print("✅ Индивидуальное тестирование завершено!")
    print("📊 Проверьте результаты выше для каждого инструмента")
