#!/usr/bin/env python3
"""
Проверка настроек AmoCRM в MongoDB
"""

import asyncio
from app.plugins.mongo_plugin import MongoPlugin

async def check_settings():
    print('🔍 Проверяем настройки в MongoDB...')
    mongo = MongoPlugin()
    await mongo.initialize()
    
    # Ищем настройки AmoCRM
    result = await mongo._find('plugin_settings', {'plugin_name': {'$in': ['simple_amocrm', 'amocrm']}})
    print(f'📋 Результат поиска: {result}')
    
    if result.get('success') and result.get('documents'):
        print(f'✅ Найдено {len(result["documents"])} настроек:')
        for doc in result['documents']:
            plugin_name = doc.get('plugin_name', 'НЕИЗВЕСТНО')
            base_url = doc.get('base_url', 'НЕТ URL')
            has_token = 'ЕСТЬ' if doc.get('access_token') else 'НЕТ'
            print(f'   📄 {plugin_name}: {base_url} (токен: {has_token})')
    else:
        print('❌ Настройки AmoCRM не найдены в БД')
        print('💡 Нужно добавить настройки через API или скрипт')

if __name__ == "__main__":
    asyncio.run(check_settings()) 