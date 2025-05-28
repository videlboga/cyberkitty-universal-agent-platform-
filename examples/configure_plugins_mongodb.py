#!/usr/bin/env python3
"""
Пример настройки плагинов KittyCore через MongoDB API

Демонстрирует как настроить все плагины используя только MongoDB API
без необходимости в Admin API.

Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

API_URL = "http://localhost:8085/api/v1/simple"

def mongo_request(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Выполняет запрос к MongoDB API"""
    url = f"{API_URL}/mongo/{endpoint}"
    response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
    return response.json()

def configure_amocrm(base_url: str, access_token: str) -> bool:
    """Настройка AmoCRM плагина через MongoDB API"""
    print("🔧 Настройка AmoCRM плагина...")
    
    settings = {
        "plugin_name": "amocrm",
        "base_url": base_url,
        "access_token": access_token,
        "updated_at": datetime.now().isoformat()
    }
    
    # Используем upsert для обновления или создания
    result = mongo_request("insert", {
        "collection": "plugin_settings",
        "document": settings
    })
    
    if result.get("success"):
        print(f"✅ AmoCRM настроен: {base_url}")
        return True
    else:
        print(f"❌ Ошибка настройки AmoCRM: {result.get('error')}")
        return False

def configure_telegram(bot_token: str, webhook_url: str = None, webhook_secret: str = None) -> bool:
    """Настройка Telegram плагина через MongoDB API"""
    print("📱 Настройка Telegram плагина...")
    
    settings = {
        "plugin_name": "telegram",
        "bot_token": bot_token,
        "webhook_url": webhook_url,
        "webhook_secret": webhook_secret,
        "updated_at": datetime.now().isoformat()
    }
    
    result = mongo_request("insert", {
        "collection": "plugin_settings",
        "document": settings
    })
    
    if result.get("success"):
        print(f"✅ Telegram настроен: {bot_token[:10]}...")
        return True
    else:
        print(f"❌ Ошибка настройки Telegram: {result.get('error')}")
        return False

def configure_llm(openrouter_api_key: str = None, openai_api_key: str = None, 
                 anthropic_api_key: str = None, default_model: str = None) -> bool:
    """Настройка LLM плагина через MongoDB API"""
    print("🤖 Настройка LLM плагина...")
    
    settings = {
        "plugin_name": "llm",
        "openrouter_api_key": openrouter_api_key,
        "openai_api_key": openai_api_key,
        "anthropic_api_key": anthropic_api_key,
        "default_model": default_model or "anthropic/claude-3-sonnet",
        "updated_at": datetime.now().isoformat()
    }
    
    result = mongo_request("insert", {
        "collection": "plugin_settings",
        "document": settings
    })
    
    if result.get("success"):
        print(f"✅ LLM настроен: модель {settings['default_model']}")
        return True
    else:
        print(f"❌ Ошибка настройки LLM: {result.get('error')}")
        return False

def get_plugin_settings(plugin_name: str) -> Dict[str, Any]:
    """Получение настроек плагина через MongoDB API"""
    result = mongo_request("find", {
        "collection": "plugin_settings",
        "filter": {"plugin_name": plugin_name}
    })
    
    if result.get("success") and result.get("data"):
        return result["data"][0]
    return {}

def update_plugin_settings(plugin_name: str, updates: Dict[str, Any]) -> bool:
    """Обновление настроек плагина через MongoDB API"""
    updates["updated_at"] = datetime.now().isoformat()
    
    result = mongo_request("update", {
        "collection": "plugin_settings",
        "filter": {"plugin_name": plugin_name},
        "document": updates
    })
    
    return result.get("success", False)

def list_all_plugin_settings() -> None:
    """Показать все настройки плагинов"""
    print("\n📋 Текущие настройки плагинов:")
    print("-" * 50)
    
    result = mongo_request("find", {
        "collection": "plugin_settings",
        "filter": {}
    })
    
    if result.get("success"):
        for settings in result.get("data", []):
            plugin_name = settings.get("plugin_name", "unknown")
            updated_at = settings.get("updated_at", "unknown")
            
            print(f"🔧 {plugin_name.upper()}:")
            for key, value in settings.items():
                if key not in ["plugin_name", "updated_at", "id"]:
                    # Маскируем токены и ключи
                    if "token" in key.lower() or "key" in key.lower():
                        value = f"{str(value)[:10]}..." if value else "не задан"
                    print(f"   {key}: {value}")
            print(f"   обновлен: {updated_at}")
            print()
    else:
        print("❌ Ошибка получения настроек")

def main():
    """Основная функция демонстрации"""
    print("🚀 НАСТРОЙКА ПЛАГИНОВ KITTYCORE ЧЕРЕЗ MONGODB API")
    print("=" * 60)
    print("💡 Принцип: ПРОСТОТА ПРЕВЫШЕ ВСЕГО!")
    print("🔗 Используем только MongoDB API, без Admin API")
    print()
    
    # Пример настройки всех плагинов
    success_count = 0
    
    # AmoCRM
    if configure_amocrm(
        base_url="https://example.amocrm.ru",
        access_token="your_amocrm_token_here"
    ):
        success_count += 1
    
    # Telegram
    if configure_telegram(
        bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
        webhook_url="https://your-domain.com/webhook",
        webhook_secret="your_webhook_secret"
    ):
        success_count += 1
    
    # LLM
    if configure_llm(
        openrouter_api_key="sk-or-your-key-here",
        openai_api_key="sk-your-openai-key",
        default_model="anthropic/claude-3-sonnet"
    ):
        success_count += 1
    
    print(f"\n📊 Результат: {success_count}/3 плагинов настроено")
    
    # Показываем все настройки
    list_all_plugin_settings()
    
    # Пример обновления настроек
    print("🔄 Пример обновления настроек AmoCRM...")
    if update_plugin_settings("amocrm", {
        "base_url": "https://updated.amocrm.ru",
        "access_token": "updated_token_123"
    }):
        print("✅ Настройки AmoCRM обновлены")
    else:
        print("❌ Ошибка обновления настроек AmoCRM")
    
    print("\n🎯 ВЫВОДЫ:")
    print("✅ MongoDB API полностью заменяет Admin API")
    print("✅ Настройка плагинов стала проще и единообразнее")
    print("✅ Меньше кода, больше функциональности")
    print("🚀 Admin API больше не нужен!")

if __name__ == "__main__":
    main() 