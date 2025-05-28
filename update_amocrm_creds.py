#!/usr/bin/env python3
"""
Скрипт для обновления кредов AmoCRM в базе данных
"""

import asyncio
from app.plugins.mongo_plugin import MongoPlugin

async def update_amocrm_settings():
    print('🔧 Подключение к MongoDB...')
    mongo = MongoPlugin()
    await mongo.initialize()
    
    # Новые настройки AmoCRM
    amocrm_settings = {
        'plugin_name': 'simple_amocrm',
        'base_url': 'https://ontonothing2025.amocrm.ru',
        'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjFlZTg0N2UxOGY5MzVjNjk1OGE0ZGM1MWU1YmIzMjcxOWUyMDkxZDExZjIzMjY3ODZiYTg2NTA4NTcwYTQxNTU3M2VmYjI2YzY5YmQwYTRjIn0.eyJhdWQiOiIwN2YwZmJhZi1kZGE3LTRkOWItOGEwMC0wMGFhNDZhZDY5NGUiLCJqdGkiOiIxZWU4NDdlMThmOTM1YzY5NThhNGRjNTFlNWJiMzI3MTllMjA5MWQxMWYyMzI2Nzg2YmE4NjUwODU3MGE0MTU1NzNlZmIyNmM2OWJkMGE0YyIsImlhdCI6MTc0ODQxNjE2OCwibmJmIjoxNzQ4NDE2MTY4LCJleHAiOjE5MDQxNjk2MDAsInN1YiI6IjEyMDkzNjk4IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMyMjIwODM0LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiMGZmNjlkNzAtOGJlOS00ZmY1LWFlMDctMmI3M2ZhNTdjNzFmIiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.kbfS5MGDDxOMM4lX0zI1SYkB75EXN_300ns7yKOGVgYUyB9BH0x9RLAV17tFzJTBKiVTjZv1Iv7nCNUqXsEbQpqLpX_N2ysUN0KO5FZOGbLnLMDKTlRtlAxq57FKTniQo6zQdYqNuWBFM6eBJ-02ltmga8dbM87620PhEPVvAfaqXur7q-GcLo3CV5JO5p3bm2qz8wG-IXGKbj5xFW0Ln_bn81UegIDEnNiBECKXg0Nz1yfkZnwSe0YB3O0QM0lGRbl7NCATzXUj1m4Ei4d6qxHGMKvfYYQhzcuZHB14T0n3KvUVmmtLslts0e9TBPJiHquZRvIkzCbVe6iOf5k9pQ'
    }
    
    print('💾 Сохранение настроек AmoCRM...')
    result = await mongo.save_plugin_settings(amocrm_settings)
    print(f'✅ Результат сохранения: {result}')
    
    # Проверяем что сохранилось
    print('🔍 Проверка сохраненных настроек...')
    saved = await mongo.get_plugin_settings('simple_amocrm')
    if saved:
        print(f'📋 Base URL: {saved.get("base_url", "НЕТ")}')
        print(f'📋 Токен: {saved.get("access_token", "НЕТ")[:50]}...')
        print('✅ Настройки AmoCRM успешно обновлены!')
    else:
        print('❌ Ошибка: настройки не найдены')

if __name__ == "__main__":
    asyncio.run(update_amocrm_settings()) 