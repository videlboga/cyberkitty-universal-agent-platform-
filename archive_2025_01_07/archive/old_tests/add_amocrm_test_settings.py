#!/usr/bin/env python3
"""
Скрипт для добавления тестовых настроек AmoCRM в MongoDB
Это позволит протестировать исправление проблемы обновления настроек
"""

import asyncio
import json
from datetime import datetime

async def add_test_settings():
    """Добавляет тестовые настройки AmoCRM в БД"""
    print("🔧 ДОБАВЛЕНИЕ ТЕСТОВЫХ НАСТРОЕК AMOCRM")
    print("="*50)
    
    try:
        # Импортируем MongoDB плагин
        from app.plugins.mongo_plugin import MongoPlugin
        
        # Инициализируем MongoDB
        print("📊 Подключение к MongoDB...")
        mongo = MongoPlugin()
        await mongo.initialize()
        
        # Тестовые настройки AmoCRM
        test_settings = {
            "plugin_name": "simple_amocrm",
            "base_url": "https://test-reload.amocrm.ru",
            "access_token": "test_token_dynamic_reload_12345",
            "updated_at": datetime.now().isoformat(),
            "test_mode": True,
            "description": "Тестовые настройки для проверки динамической перезагрузки"
        }
        
        print("💾 Сохранение тестовых настроек...")
        print(f"   📄 URL: {test_settings['base_url']}")
        print(f"   🔑 Token: {test_settings['access_token'][:20]}...")
        
        # Сохраняем настройки (используем upsert)
        result = await mongo._update_one(
            "plugin_settings",
            {"plugin_name": "simple_amocrm"},
            {"$set": test_settings},
            upsert=True
        )
        
        if result.get("success"):
            print("✅ Тестовые настройки успешно сохранены!")
            
            # Проверяем что сохранилось
            print("\n🔍 Проверка сохраненных настроек...")
            check_result = await mongo._find_one("plugin_settings", {"plugin_name": "simple_amocrm"})
            
            if check_result.get("success") and check_result.get("document"):
                saved_settings = check_result["document"]
                print(f"   ✅ URL: {saved_settings.get('base_url')}")
                print(f"   ✅ Token: {saved_settings.get('access_token', '')[:20]}...")
                print(f"   ✅ Обновлено: {saved_settings.get('updated_at')}")
            else:
                print("   ❌ Не удалось проверить сохраненные настройки")
                
        else:
            print(f"❌ Ошибка сохранения: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    print("\n💡 Теперь можно тестировать динамическую перезагрузку настроек!")
    print("🧪 Запустите: python test_amocrm_settings_fix.py")
    return True

async def remove_test_settings():
    """Удаляет тестовые настройки"""
    print("\n🧹 УДАЛЕНИЕ ТЕСТОВЫХ НАСТРОЕК")
    print("="*40)
    
    try:
        from app.plugins.mongo_plugin import MongoPlugin
        
        mongo = MongoPlugin()
        await mongo.initialize()
        
        result = await mongo._delete_one("plugin_settings", {"plugin_name": "simple_amocrm"})
        
        if result.get("success"):
            print("✅ Тестовые настройки удалены")
        else:
            print(f"❌ Ошибка удаления: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Ошибка удаления: {e}")

async def main():
    """Основная функция"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "remove":
        await remove_test_settings()
    else:
        await add_test_settings()

if __name__ == "__main__":
    asyncio.run(main()) 