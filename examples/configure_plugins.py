#!/usr/bin/env python3
"""
Пример настройки плагинов KittyCore через Admin API

Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
- Все настройки через HTTP API
- Никаких переменных окружения
- Централизованное управление в БД
"""

import asyncio
import httpx
from typing import Dict, Any

# Базовый URL API
BASE_URL = "http://localhost:8000/api/v1/admin"

async def configure_telegram_plugin():
    """Настройка Telegram плагина"""
    print("🤖 Настройка Telegram плагина...")
    
    settings = {
        "bot_token": "1234567890:ABCDEF1234567890abcdef1234567890ABC",
        "webhook_url": None,
        "webhook_secret": None
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/plugins/telegram/settings",
            json=settings,
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Telegram настроен: {result['message']}")
        else:
            print(f"❌ Ошибка настройки Telegram: {response.text}")

async def configure_amocrm_plugin():
    """Настройка AmoCRM плагина"""
    print("🏢 Настройка AmoCRM плагина...")
    
    # Основные настройки
    settings = {
        "base_url": "https://example.amocrm.ru",
        "access_token": "your_access_token_here"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/plugins/amocrm/settings",
            json=settings,
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AmoCRM настроен: {result['message']}")
        else:
            print(f"❌ Ошибка настройки AmoCRM: {response.text}")
    
    # Карта полей
    fields_map = {
        "telegram_id": {
            "id": 951775,
            "name": "TG username",
            "type": "text"
        },
        "phone": {
            "id": 881883,
            "name": "Телефон",
            "type": "multiphonemail",
            "enums": [
                {"id": 881885, "value": "WORK", "sort": 1}
            ]
        },
        "email": {
            "id": 881885,
            "name": "Email",
            "type": "multiphonemail",
            "enums": [
                {"id": 881887, "value": "WORK", "sort": 1}
            ]
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/plugins/amocrm/fields",
            json={"fields_map": fields_map},
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Поля AmoCRM настроены: {result['message']}")
        else:
            print(f"❌ Ошибка настройки полей AmoCRM: {response.text}")

async def configure_llm_plugin():
    """Настройка LLM плагина"""
    print("🧠 Настройка LLM плагина...")
    
    settings = {
        "openrouter_api_key": "sk-or-v1-your-key-here",
        "openai_api_key": None,
        "anthropic_api_key": None,
        "default_model": "meta-llama/llama-3.2-3b-instruct:free"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/plugins/llm/settings",
            json=settings,
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ LLM настроен: {result['message']}")
        else:
            print(f"❌ Ошибка настройки LLM: {response.text}")

async def check_plugins_status():
    """Проверка статуса всех плагинов"""
    print("📊 Проверка статуса плагинов...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/plugins/status",
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📋 Статус плагинов ({result['total_plugins']} плагинов):")
            
            for plugin_name, plugin_info in result['plugins'].items():
                health = "✅" if plugin_info['health'] else "❌"
                configured = plugin_info.get('settings', {}).get('configured', False)
                config_status = "🔧" if configured else "⚙️"
                
                print(f"  {health} {config_status} {plugin_name}")
                
                if 'error' in plugin_info:
                    print(f"    ❌ Ошибка: {plugin_info['error']}")
                    
        else:
            print(f"❌ Ошибка получения статуса: {response.text}")

async def main():
    """Главная функция"""
    print("🚀 Настройка плагинов KittyCore через Admin API")
    print("=" * 50)
    
    try:
        # Проверяем статус до настройки
        await check_plugins_status()
        
        print("\n🔧 Начинаем настройку плагинов...")
        
        # Настраиваем плагины (закомментировано для безопасности)
        # await configure_telegram_plugin()
        # await configure_amocrm_plugin()
        # await configure_llm_plugin()
        
        print("\n⚠️ Настройка плагинов закомментирована для безопасности")
        print("💡 Раскомментируйте нужные функции и укажите реальные токены")
        
        # Проверяем статус после настройки
        print("\n📊 Финальный статус:")
        await check_plugins_status()
        
        print("\n✅ Готово!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 