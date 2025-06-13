#!/usr/bin/env python3
"""
Простой тестовый веб-сервер для диагностики
"""

import sys
import os
import traceback

# Добавляем путь к kittycore в PYTHONPATH
sys.path.insert(0, os.path.abspath("."))

def test_imports():
    """Тест импортов"""
    print("🔍 Тестирование импортов...")
    
    try:
        import fastapi
        print("✅ FastAPI импортирован")
    except Exception as e:
        print(f"❌ FastAPI: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn импортирован")
    except Exception as e:
        print(f"❌ Uvicorn: {e}")
        return False
    
    try:
        from kittycore.web.websocket_manager import WebSocketManager
        print("✅ WebSocketManager импортирован")
    except Exception as e:
        print(f"❌ WebSocketManager: {e}")
        print(f"Детали ошибки: {traceback.format_exc()}")
        return False
    
    try:
        from kittycore.web.server import WebServer, create_app
        print("✅ WebServer импортирован")
    except Exception as e:
        print(f"❌ WebServer: {e}")
        print(f"Детали ошибки: {traceback.format_exc()}")
        return False
    
    return True

def create_simple_server():
    """Создать простой сервер"""
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(title="KittyCore Test")
    
    @app.get("/")
    async def root():
        return {"message": "KittyCore 3.0 Test Server работает!"}
    
    @app.get("/test")
    async def test():
        return {"status": "ok", "test": "passed"}
    
    print("🚀 Запуск простого тестового сервера на порту 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")

def main():
    """Главная функция"""
    print("🧪 Диагностика KittyCore 3.0 Web Interface")
    print("=" * 50)
    
    # Тест импортов
    if not test_imports():
        print("❌ Проблемы с импортами!")
        sys.exit(1)
    
    print("\n✅ Все импорты успешны!")
    
    # Запуск простого сервера
    try:
        create_simple_server()
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        print(f"Детали: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 