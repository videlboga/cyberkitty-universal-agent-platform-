#!/usr/bin/env python3
"""
🚀 KittyCore 3.0 - Главная точка входа

Единая саморедуплицирующаяся агентная система
Obsidian-совместимое хранилище + Human-in-the-loop
"""

import sys
import asyncio
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from launcher import main

if __name__ == "__main__":
    print("🐱 KittyCore 3.0 - Саморедуплицирующаяся агентная система")
    print("Запуск через главную точку входа...")
    print()
    
    # Запускаем launcher
    asyncio.run(main())
