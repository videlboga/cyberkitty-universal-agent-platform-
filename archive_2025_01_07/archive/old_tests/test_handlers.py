#!/usr/bin/env python3

import asyncio
import sys
import os

# Добавляем путь к приложению
sys.path.insert(0, '/app')

from app.core.simple_engine import create_engine

async def test_handlers():
    try:
        engine = await create_engine()
        amocrm_plugin = engine.plugins.get('simple_amocrm')
        
        if amocrm_plugin:
            handlers = amocrm_plugin.register_handlers()
            print(f"AmoCRM handlers ({len(handlers)}):")
            for handler in sorted(handlers.keys()):
                print(f"  - {handler}")
        else:
            print("AmoCRM plugin not found")
            
        print(f"\nВсе handlers в движке ({len(engine.handlers)}):")
        amocrm_handlers = [h for h in engine.handlers.keys() if h.startswith('amocrm_')]
        for handler in sorted(amocrm_handlers):
            print(f"  - {handler}")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_handlers()) 