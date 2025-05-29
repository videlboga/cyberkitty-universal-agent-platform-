#!/usr/bin/env python3
"""
Тест AmoCRM плагина внутри Docker контейнера
"""

import asyncio
import sys
sys.path.append('/app')

from app.core.simple_engine import create_engine

async def test():
    print('🧪 Тест создания движка с плагинами...')
    
    try:
        engine = await create_engine()
        print(f'📦 Зарегистрированные плагины: {engine.get_registered_plugins()}')
        print(f'🔧 Количество обработчиков: {len(engine.get_registered_handlers())}')
        
        # Проверяем AmoCRM плагин
        if 'simple_amocrm' in engine.plugins:
            amocrm = engine.plugins['simple_amocrm']
            print(f'✅ AmoCRM плагин найден')
            settings = amocrm.get_current_settings()
            print(f'⚙️ Настройки: {settings}')
            health = await amocrm.healthcheck()
            print(f'🏥 Healthcheck: {health}')
            
            # Проверяем обработчики
            handlers = amocrm.register_handlers()
            print(f'🔧 Обработчики AmoCRM: {list(handlers.keys())}')
        else:
            print('❌ AmoCRM плагин не найден')
            
    except Exception as e:
        print(f'❌ Ошибка: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test()) 