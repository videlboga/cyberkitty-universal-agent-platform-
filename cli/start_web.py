#!/usr/bin/env python3
"""
Launcher для KittyCore 3.0 Web Interface
"""

import sys
import os
import logging

# Добавляем путь к kittycore в PYTHONPATH
sys.path.insert(0, os.path.abspath("."))

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """Запуск веб-интерфейса"""
    print("🚀 Запуск KittyCore 3.0 Web Interface")
    print("=" * 50)
    
    try:
        from kittycore.web.server import WebServer
        
        print("✅ Модули импортированы успешно")
        
        # Создаем и запускаем сервер на порту 8001
        server = WebServer(host="0.0.0.0", port=8001)
        
        print("🌐 Сервер запускается на http://localhost:8001")
        print("📊 API документация: http://localhost:8001/api/docs")
        print("🔌 WebSocket: ws://localhost:8001/ws")
        print("\n✋ Нажмите Ctrl+C для остановки")
        
        server.run()
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь что установлены зависимости: pip install fastapi uvicorn[standard] websockets requests")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 