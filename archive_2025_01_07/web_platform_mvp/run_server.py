#!/usr/bin/env python3

import uvicorn
from app import app

if __name__ == "__main__":
    print("🚀 Запускаю Document Generator MVP...")
    print("📍 Адрес: http://127.0.0.1:8080")
    print("📖 Документация: http://127.0.0.1:8080/docs")
    
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8080,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}") 