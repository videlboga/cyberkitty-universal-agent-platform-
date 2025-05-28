#!/usr/bin/env python3
"""
Проверка логики работы Telegram плагина с каналами
"""

import asyncio
import sys
sys.path.append('/app')

from app.plugins.mongo_plugin import MongoPlugin
from app.core.simple_engine import create_engine

async def check_telegram_channels():
    print('🔍 Проверка логики работы Telegram плагина с каналами...')
    
    mongo = MongoPlugin()
    await mongo.initialize()
    
    print('\n' + '='*60)
    print('КАНАЛЫ И ТОКЕНЫ TELEGRAM')
    print('='*60)
    
    # Проверяем маппинги каналов
    channels_result = await mongo._find('channel_mappings', {})
    print(f'📋 Маппинги каналов:')
    if channels_result.get('success') and channels_result.get('documents'):
        for channel in channels_result['documents']:
            print(f'   - channel_id: {channel.get("channel_id", "НЕТ")}')
            print(f'     channel_type: {channel.get("channel_type", "НЕТ")}')
            print(f'     scenario_id: {channel.get("scenario_id", "НЕТ")}')
            config = channel.get('channel_config', {})
            if config.get('bot_token'):
                print(f'     bot_token: {config["bot_token"][:20]}...')
            else:
                print(f'     bot_token: НЕТ')
            print()
    else:
        print('   ❌ Маппинги каналов не найдены')
    
    print('\n' + '='*60)
    print('СОЗДАНИЕ ДВИЖКА И TELEGRAM ПЛАГИНА')
    print('='*60)
    
    # Создаем движок
    engine = await create_engine()
    print(f'📦 Движок создан: {type(engine).__name__}')
    print(f'🔧 Плагины: {list(engine.plugins.keys())}')
    
    # Проверяем Telegram плагин
    if 'simple_telegram' in engine.plugins:
        tg_plugin = engine.plugins['simple_telegram']
        print(f'✅ Telegram плагин найден')
        print(f'   - channel_id: {tg_plugin.channel_id}')
        print(f'   - bot_token установлен: {bool(tg_plugin.bot_token)}')
        if tg_plugin.bot_token:
            print(f'   - bot_token: {tg_plugin.bot_token[:20]}...')
        print(f'   - bot инициализирован: {bool(tg_plugin.bot)}')
        
        # Получаем настройки
        settings = tg_plugin.get_current_settings()
        print(f'⚙️ Настройки плагина: {settings}')
        
        # Проверяем healthcheck
        health = await tg_plugin.healthcheck()
        print(f'🏥 Healthcheck: {health}')
        
    else:
        print('❌ Telegram плагин не найден')
    
    print('\n' + '='*60)
    print('ЛОГИКА ИНИЦИАЛИЗАЦИИ ТОКЕНА')
    print('='*60)
    
    print('📝 Логика работы Telegram плагина:')
    print('1. При создании плагина:')
    print('   - Токен берется из параметра конструктора ИЛИ переменной TELEGRAM_BOT_TOKEN')
    print('   - channel_id по умолчанию = "telegram_bot"')
    print()
    print('2. При инициализации (_do_initialize):')
    print('   - Вызывается _load_settings_from_db()')
    print('   - Ищет настройки в plugin_settings с plugin_name="telegram"')
    print('   - Если найдены - обновляет bot_token')
    print('   - Если токен есть - создает Application и Bot')
    print()
    print('3. Связь с каналами:')
    print('   - Плагин НЕ автоматически привязывается к каналам')
    print('   - Каналы создаются через mongo_create_channel_mapping')
    print('   - Каждый канал может иметь свой bot_token в channel_config')
    print('   - Плагин работает с одним токеном из plugin_settings')
    print()
    print('4. Проблема:')
    print('   - Плагин не учитывает токены из channel_mappings')
    print('   - Нет логики переключения между токенами разных каналов')
    print('   - Один экземпляр плагина = один токен')

if __name__ == "__main__":
    asyncio.run(check_telegram_channels()) 