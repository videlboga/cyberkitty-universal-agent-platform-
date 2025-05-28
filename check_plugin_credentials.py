#!/usr/bin/env python3
"""
Проверка получения кредов плагинами из MongoDB
"""

import asyncio
import sys
sys.path.append('/app')

from app.plugins.mongo_plugin import MongoPlugin
from app.core.simple_engine import create_engine

async def check_plugin_settings():
    print('🔍 Проверка настроек плагинов в MongoDB...')
    
    mongo = MongoPlugin()
    await mongo.initialize()
    
    print('\n' + '='*60)
    print('НАСТРОЙКИ В MONGODB')
    print('='*60)
    
    # Проверяем настройки AmoCRM
    amocrm_settings = await mongo._find_one('plugin_settings', {'plugin_name': 'amocrm'})
    print(f'📋 AmoCRM настройки:')
    if amocrm_settings.get('success') and amocrm_settings.get('document'):
        doc = amocrm_settings['document']
        print(f'   - base_url: {doc.get("base_url", "НЕТ")}')
        print(f'   - access_token: {"ЕСТЬ" if doc.get("access_token") else "НЕТ"}')
        print(f'   - updated_at: {doc.get("updated_at", "НЕТ")}')
    else:
        print('   ❌ Настройки не найдены')
    
    # Проверяем настройки полей AmoCRM
    amocrm_fields = await mongo._find_one('plugin_settings', {'plugin_name': 'amocrm_fields'})
    print(f'\n📋 AmoCRM поля:')
    if amocrm_fields.get('success') and amocrm_fields.get('document'):
        doc = amocrm_fields['document']
        fields_map = doc.get('fields_map', {})
        print(f'   - Количество полей: {len(fields_map)}')
        for field_name, field_data in fields_map.items():
            print(f'   - {field_name}: ID={field_data.get("id", "?")}')
    else:
        print('   ❌ Поля не найдены')
    
    # Проверяем настройки Telegram
    telegram_settings = await mongo._find_one('plugin_settings', {'plugin_name': 'telegram'})
    print(f'\n📋 Telegram настройки:')
    if telegram_settings.get('success') and telegram_settings.get('document'):
        doc = telegram_settings['document']
        print(f'   - bot_token: {"ЕСТЬ" if doc.get("bot_token") else "НЕТ"}')
        print(f'   - webhook_url: {doc.get("webhook_url", "НЕТ")}')
    else:
        print('   ❌ Настройки не найдены')
    
    # Проверяем настройки LLM
    llm_settings = await mongo._find_one('plugin_settings', {'plugin_name': 'llm'})
    print(f'\n📋 LLM настройки:')
    if llm_settings.get('success') and llm_settings.get('document'):
        doc = llm_settings['document']
        print(f'   - api_key: {"ЕСТЬ" if doc.get("api_key") else "НЕТ"}')
        print(f'   - model: {doc.get("model", "НЕТ")}')
        print(f'   - base_url: {doc.get("base_url", "НЕТ")}')
    else:
        print('   ❌ Настройки не найдены')
    
    # Показываем все настройки плагинов
    all_settings = await mongo._find('plugin_settings', {})
    print(f'\n📦 Всего настроек плагинов в БД: {len(all_settings.get("documents", []))}')
    if all_settings.get('success'):
        for setting in all_settings.get('documents', []):
            plugin_name = setting.get('plugin_name', 'unknown')
            has_sensitive = any(key in str(setting) for key in ['token', 'key', 'password'])
            print(f'  - {plugin_name}: {"🔐 есть секретные данные" if has_sensitive else "⚙️ только конфигурация"}')

async def check_plugin_loading():
    print('\n' + '='*60)
    print('ЗАГРУЗКА НАСТРОЕК ПЛАГИНАМИ')
    print('='*60)
    
    # Создаем движок с плагинами
    engine = await create_engine()
    
    # Проверяем AmoCRM плагин
    if 'simple_amocrm' in engine.plugins:
        amocrm = engine.plugins['simple_amocrm']
        print(f'\n🔧 AmoCRM плагин:')
        print(f'   - base_url: {amocrm.base_url}')
        print(f'   - access_token: {"ЕСТЬ" if amocrm.access_token else "НЕТ"}')
        print(f'   - fields_map: {len(amocrm.fields_map)} полей')
        print(f'   - configured: {bool(amocrm.base_url and amocrm.access_token)}')
    
    # Проверяем Telegram плагин
    if 'simple_telegram' in engine.plugins:
        telegram = engine.plugins['simple_telegram']
        print(f'\n📱 Telegram плагин:')
        print(f'   - bot_token: {"ЕСТЬ" if hasattr(telegram, "bot_token") and telegram.bot_token else "НЕТ"}')
        print(f'   - bot инициализирован: {hasattr(telegram, "bot") and telegram.bot is not None}')
    
    # Проверяем LLM плагин
    if 'simple_llm' in engine.plugins:
        llm = engine.plugins['simple_llm']
        print(f'\n🤖 LLM плагин:')
        print(f'   - api_key: {"ЕСТЬ" if hasattr(llm, "api_key") and llm.api_key else "НЕТ"}')
        print(f'   - model: {getattr(llm, "model", "НЕТ")}')
        print(f'   - base_url: {getattr(llm, "base_url", "НЕТ")}')

async def test_credential_reload():
    print('\n' + '='*60)
    print('ТЕСТ ПЕРЕЗАГРУЗКИ КРЕДОВ')
    print('='*60)
    
    # Создаем движок
    engine = await create_engine()
    amocrm = engine.plugins.get('simple_amocrm')
    
    if not amocrm:
        print('❌ AmoCRM плагин не найден')
        return
    
    print(f'🔧 Настройки ДО перезагрузки:')
    print(f'   - base_url: {amocrm.base_url}')
    print(f'   - access_token: {"ЕСТЬ" if amocrm.access_token else "НЕТ"}')
    
    # Принудительно перезагружаем настройки
    print(f'\n🔄 Перезагружаем настройки из БД...')
    await amocrm._load_settings_from_db()
    await amocrm._load_fields_from_db()
    
    print(f'🔧 Настройки ПОСЛЕ перезагрузки:')
    print(f'   - base_url: {amocrm.base_url}')
    print(f'   - access_token: {"ЕСТЬ" if amocrm.access_token else "НЕТ"}')
    print(f'   - fields_map: {len(amocrm.fields_map)} полей')

async def main():
    print('🚀 Проверка получения кредов плагинами из БД')
    
    try:
        await check_plugin_settings()
        await check_plugin_loading()
        await test_credential_reload()
        
        print('\n' + '='*60)
        print('✅ ИТОГ: Проверка завершена')
        print('='*60)
        
    except Exception as e:
        print(f'❌ Ошибка: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 