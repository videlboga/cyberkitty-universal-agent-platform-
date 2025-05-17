#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска сервера локально с настройками из .env.local
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import uvicorn

# Загружаем переменные окружения
ENV_LOCAL = Path('.env.local')
ENV_DEFAULT = Path('.env')

# Сначала загружаем основной .env
if ENV_DEFAULT.exists():
    load_dotenv(ENV_DEFAULT)
    print(f"Загружены настройки из {ENV_DEFAULT}")

# Затем переопределяем локальными настройками
if ENV_LOCAL.exists():
    load_dotenv(ENV_LOCAL, override=True)
    print(f"Загружены локальные настройки из {ENV_LOCAL}")
else:
    print(f"Файл {ENV_LOCAL} не найден, используются только основные настройки")

# Проверяем, что MONGO_URI теперь указывает на localhost
mongo_uri = os.getenv("MONGO_URI", "")
if "localhost" not in mongo_uri:
    print(f"ВНИМАНИЕ: MONGO_URI не содержит localhost: {mongo_uri}")
    print("Возможно, локальные настройки не были загружены корректно")
    response = input("Продолжить запуск? (y/n): ")
    if response.lower() != 'y':
        sys.exit(1)
else:
    print(f"MONGO_URI настроен на локальное подключение: {mongo_uri}")

if __name__ == "__main__":
    # Запускаем приложение
    print("Запуск локального сервера...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True) 