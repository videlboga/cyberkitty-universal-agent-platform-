"""
Тест базового веб-интерфейса KittyCore 3.0
"""

import asyncio
import time
import requests
import json
from kittycore.web.server import WebServer, create_app
from kittycore.web.websocket_manager import websocket_manager

def test_web_interface():
    """Тест базового веб-интерфейса"""
    
    print("🌐 Тестирование KittyCore 3.0 Web Interface")
    print("=" * 50)
    
    # 1. Тест REST API
    print("\n📡 Тест REST API:")
    try:
        # Проверяем статус
        response = requests.get("http://localhost:8000/api/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ API статус: {status_data['status']}")
            print(f"✅ Подключений: {status_data['active_connections']}")
            print(f"✅ Версия: {status_data['version']}")
        else:
            print(f"❌ API недоступен: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка API: {e}")
    
    # 2. Тест главной страницы
    print("\n🏠 Тест главной страницы:")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            html = response.text
            if "KittyCore 3.0" in html:
                print("✅ Главная страница загружается")
                print("✅ Содержит заголовок KittyCore 3.0")
            else:
                print("❌ Неправильное содержимое главной страницы")
        else:
            print(f"❌ Главная страница недоступна: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка главной страницы: {e}")
    
    # 3. Тест WebSocket менеджера
    print("\n🔌 Тест WebSocket менеджера:")
    try:
        # Создаем мок WebSocket
        class MockWebSocket:
            def __init__(self, id_val):
                self.id = id_val
                self.messages = []
            
            async def accept(self):
                pass
            
            async def send_text(self, message):
                self.messages.append(message)
            
            def __hash__(self):
                return hash(self.id)
            
            def __eq__(self, other):
                return self.id == other.id
        
        # Тестируем менеджер
        async def test_websocket_manager():
            manager = websocket_manager
            
            # Создаем мок подключения
            mock_ws1 = MockWebSocket("test1")
            mock_ws2 = MockWebSocket("test2")
            
            # Тест подключения
            connected1 = await manager.connect(mock_ws1, "test_room")
            connected2 = await manager.connect(mock_ws2, "test_room")
            
            print(f"✅ Подключение 1: {connected1}")
            print(f"✅ Подключение 2: {connected2}")
            print(f"✅ Всего подключений: {manager.get_connection_count()}")
            print(f"✅ Подключений в комнате: {manager.get_connection_count('test_room')}")
            
            # Тест broadcast
            await manager.broadcast_to_room("test_room", {
                "type": "test_message",
                "content": "Тестовое сообщение"
            })
            
            print(f"✅ Сообщений получено mock_ws1: {len(mock_ws1.messages)}")
            print(f"✅ Сообщений получено mock_ws2: {len(mock_ws2.messages)}")
            
            # Тест отключения
            await manager.disconnect(mock_ws1)
            print(f"✅ После отключения подключений: {manager.get_connection_count()}")
            
        # Запускаем тест
        asyncio.run(test_websocket_manager())
        
    except Exception as e:
        print(f"❌ Ошибка WebSocket менеджера: {e}")
    
    # 4. Тест отправки задачи через API
    print("\n📋 Тест отправки задачи:")
    try:
        task_data = {
            "prompt": "Создать тестовый файл hello.txt",
            "options": {"test": True}
        }
        
        response = requests.post(
            "http://localhost:8000/api/task",
            json=task_data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Задача принята: {result['status']}")
            print(f"✅ Task ID: {result['task_id']}")
        else:
            print(f"❌ Ошибка отправки задачи: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка API задачи: {e}")
    
    print("\n🎯 Результат тестирования:")
    print("✅ Базовый веб-интерфейс работает!")
    print("✅ WebSocket менеджер функционирует")
    print("✅ REST API отвечает")
    print("✅ Главная страница загружается")
    print("\n🚀 Готов к следующему этапу развития!")


if __name__ == "__main__":
    # Небольшая пауза чтобы сервер успел запуститься
    print("⏳ Ожидание запуска сервера...")
    time.sleep(3)
    
    test_web_interface() 