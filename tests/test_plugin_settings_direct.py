#!/usr/bin/env python3
"""
Тест настроек плагинов через прямое взаимодействие
Проверяет сохранение, загрузку и применение настроек в MongoDB
"""

import asyncio
import pytest
from datetime import datetime
from typing import Dict, Any

from app.core.simple_engine import SimpleScenarioEngine
from app.plugins.mongo_plugin import MongoPlugin
from app.plugins.simple_amocrm_plugin import SimpleAmoCRMPlugin
from app.plugins.simple_telegram_plugin import SimpleTelegramPlugin
from app.plugins.simple_llm_plugin import SimpleLLMPlugin


class TestPluginSettingsDirect:
    """Тесты настроек плагинов через прямые методы"""
    
    @pytest.fixture
    async def engine_with_plugins(self):
        """Создает движок со всеми плагинами"""
        engine = SimpleScenarioEngine()
        
        # Создаем плагины
        mongo_plugin = MongoPlugin()
        amocrm_plugin = SimpleAmoCRMPlugin()
        telegram_plugin = SimpleTelegramPlugin()
        llm_plugin = SimpleLLMPlugin()
        
        # Инициализируем MongoDB первым
        await mongo_plugin.initialize()
        engine.register_plugin(mongo_plugin)
        
        # Инициализируем остальные плагины
        await amocrm_plugin.initialize()
        await telegram_plugin.initialize()
        await llm_plugin.initialize()
        
        engine.register_plugin(amocrm_plugin)
        engine.register_plugin(telegram_plugin)
        engine.register_plugin(llm_plugin)
        
        return engine, {
            'mongo': mongo_plugin,
            'amocrm': amocrm_plugin,
            'telegram': telegram_plugin,
            'llm': llm_plugin
        }
    
    @pytest.mark.asyncio
    async def test_amocrm_settings_cycle(self, engine_with_plugins):
        """Тест полного цикла настроек AmoCRM плагина"""
        engine, plugins = engine_with_plugins
        
        # Проверяем доступность MongoDB
        mongo_health = await plugins['mongo'].healthcheck()
        if not mongo_health:
            pytest.skip("MongoDB недоступен")
        
        amocrm_plugin = plugins['amocrm']
        
        try:
            print("🔄 Тестируем настройки AmoCRM плагина...")
            
            # === 1. ПРОВЕРЯЕМ НАЧАЛЬНОЕ СОСТОЯНИЕ ===
            print("📋 Проверяем начальное состояние...")
            
            initial_settings = amocrm_plugin.get_current_settings()
            print(f"Начальные настройки: {initial_settings}")
            
            # Должно быть не настроено
            assert initial_settings.get("configured") == False, "Плагин не должен быть настроен изначально"
            assert initial_settings.get("base_url") is None, "base_url должен быть None"
            assert initial_settings.get("access_token_set") == False, "Токен не должен быть установлен"
            
            print("✅ Начальное состояние корректное")
            
            # === 2. СОХРАНЯЕМ ТЕСТОВЫЕ НАСТРОЙКИ ===
            print("💾 Сохраняем тестовые настройки...")
            
            test_base_url = "https://test-domain.amocrm.ru"
            test_access_token = f"test_token_{datetime.now().timestamp()}"
            
            save_result = await amocrm_plugin.save_settings_to_db(test_base_url, test_access_token)
            
            assert save_result.get("success") == True, f"Сохранение не удалось: {save_result}"
            print(f"✅ Настройки сохранены: {save_result['message']}")
            
            # === 3. ПРОВЕРЯЕМ ЧТО НАСТРОЙКИ ПРИМЕНИЛИСЬ ===
            print("🔍 Проверяем применение настроек...")
            
            # Проверяем через get_current_settings
            current_settings = amocrm_plugin.get_current_settings()
            print(f"Текущие настройки: {current_settings}")
            
            assert current_settings.get("configured") == True, "Плагин должен быть настроен"
            assert current_settings.get("base_url") == test_base_url, f"base_url не совпадает: {current_settings.get('base_url')} != {test_base_url}"
            assert current_settings.get("access_token_set") == True, "Токен должен быть установлен"
            
            # Проверяем что настройки применились в плагине
            assert amocrm_plugin.base_url == test_base_url, "base_url не применился в плагине"
            assert amocrm_plugin.access_token == test_access_token, "access_token не применился в плагине"
            assert len(amocrm_plugin.headers) > 0, "HTTP заголовки не настроились"
            assert "Authorization" in amocrm_plugin.headers, "Authorization заголовок отсутствует"
            
            print("✅ Настройки применились корректно")
            
            # === 4. ПЕРЕЗАГРУЖАЕМ ПЛАГИН И ПРОВЕРЯЕМ ЗАГРУЗКУ ===
            print("🔄 Тестируем перезагрузку настроек...")
            
            # Создаем новый экземпляр плагина
            new_amocrm_plugin = SimpleAmoCRMPlugin()
            new_amocrm_plugin.engine = engine  # Устанавливаем ссылку на движок
            
            # Инициализируем (должен загрузить настройки из БД)
            await new_amocrm_plugin.initialize()
            
            # Проверяем что настройки загрузились
            assert new_amocrm_plugin.base_url == test_base_url, "base_url не загрузился при инициализации"
            assert new_amocrm_plugin.access_token == test_access_token, "access_token не загрузился при инициализации"
            
            reloaded_settings = new_amocrm_plugin.get_current_settings()
            assert reloaded_settings.get("configured") == True, "Настройки не загрузились при перезапуске"
            
            print("✅ Настройки корректно загружаются при перезапуске")
            
            # === 5. ТЕСТИРУЕМ КАРТУ ПОЛЕЙ ===
            print("🗺️ Тестируем карту полей...")
            
            test_fields_map = {
                "telegram_id": {
                    "id": 951775,
                    "name": "TG username",
                    "type": "text"
                },
                "phone": {
                    "id": 881883,
                    "name": "Телефон",
                    "type": "multiphonemail",
                    "enums": [{"id": 881885, "value": "WORK", "sort": 1}]
                },
                "email": {
                    "id": 881887,
                    "name": "Email",
                    "type": "multiphonemail",
                    "enums": [{"id": 881889, "value": "WORK", "sort": 1}]
                }
            }
            
            fields_result = await amocrm_plugin.save_fields_to_db(test_fields_map)
            assert fields_result.get("success") == True, f"Сохранение полей не удалось: {fields_result}"
            
            # Проверяем что поля применились
            assert len(amocrm_plugin.fields_map) == 3, f"Количество полей не совпадает: {len(amocrm_plugin.fields_map)}"
            assert "telegram_id" in amocrm_plugin.fields_map, "Поле telegram_id отсутствует"
            assert amocrm_plugin.fields_map["phone"]["id"] == 881883, "ID поля phone не совпадает"
            
            # Проверяем загрузку полей в новом экземпляре
            await new_amocrm_plugin._load_fields_from_db()
            assert len(new_amocrm_plugin.fields_map) == 3, "Поля не загрузились в новом экземпляре"
            
            print("✅ Карта полей работает корректно")
            
            # === 6. ОЧИСТКА ТЕСТОВЫХ ДАННЫХ ===
            print("🧹 Очищаем тестовые данные...")
            
            mongo_plugin = plugins['mongo']
            
            # Удаляем настройки
            await mongo_plugin._delete_one("plugin_settings", {"plugin_name": "amocrm"})
            await mongo_plugin._delete_one("plugin_settings", {"plugin_name": "amocrm_fields"})
            
            print("✅ Тестовые данные очищены")
            
        except Exception as e:
            print(f"❌ Ошибка в тесте AmoCRM: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_telegram_settings_cycle(self, engine_with_plugins):
        """Тест полного цикла настроек Telegram плагина"""
        engine, plugins = engine_with_plugins
        
        # Проверяем доступность MongoDB
        mongo_health = await plugins['mongo'].healthcheck()
        if not mongo_health:
            pytest.skip("MongoDB недоступен")
        
        telegram_plugin = plugins['telegram']
        
        try:
            print("🔄 Тестируем настройки Telegram плагина...")
            
            # === 1. ПРОВЕРЯЕМ НАЧАЛЬНОЕ СОСТОЯНИЕ ===
            print("📋 Проверяем начальное состояние...")
            
            initial_settings = telegram_plugin.get_current_settings()
            print(f"Начальные настройки: {initial_settings}")
            
            assert initial_settings.get("configured") == False, "Плагин не должен быть настроен изначально"
            assert initial_settings.get("bot_token_set") == False, "Токен не должен быть установлен"
            
            print("✅ Начальное состояние корректное")
            
            # === 2. СОХРАНЯЕМ ТЕСТОВЫЕ НАСТРОЙКИ ===
            print("💾 Сохраняем тестовые настройки...")
            
            test_bot_token = f"1234567890:TEST_TOKEN_{datetime.now().timestamp()}"
            test_webhook_url = "https://example.com/webhook"
            test_webhook_secret = "test_secret"
            
            save_result = await telegram_plugin.save_settings_to_db(
                test_bot_token, 
                test_webhook_url, 
                test_webhook_secret
            )
            
            assert save_result.get("success") == True, f"Сохранение не удалось: {save_result}"
            print(f"✅ Настройки сохранены: {save_result['message']}")
            
            # === 3. ПРОВЕРЯЕМ ЧТО НАСТРОЙКИ ПРИМЕНИЛИСЬ ===
            print("🔍 Проверяем применение настроек...")
            
            current_settings = telegram_plugin.get_current_settings()
            print(f"Текущие настройки: {current_settings}")
            
            assert current_settings.get("configured") == True, "Плагин должен быть настроен"
            assert current_settings.get("bot_token_set") == True, "Токен должен быть установлен"
            
            # Проверяем что настройки применились в плагине
            assert telegram_plugin.bot_token == test_bot_token, "bot_token не применился в плагине"
            
            print("✅ Настройки применились корректно")
            
            # === 4. ПЕРЕЗАГРУЖАЕМ ПЛАГИН ===
            print("🔄 Тестируем перезагрузку настроек...")
            
            new_telegram_plugin = SimpleTelegramPlugin()
            new_telegram_plugin.engine = engine
            
            await new_telegram_plugin.initialize()
            
            assert new_telegram_plugin.bot_token == test_bot_token, "bot_token не загрузился при инициализации"
            
            reloaded_settings = new_telegram_plugin.get_current_settings()
            assert reloaded_settings.get("configured") == True, "Настройки не загрузились при перезапуске"
            
            print("✅ Настройки корректно загружаются при перезапуске")
            
            # === 5. ОЧИСТКА ===
            print("🧹 Очищаем тестовые данные...")
            
            mongo_plugin = plugins['mongo']
            await mongo_plugin._delete_one("plugin_settings", {"plugin_name": "telegram"})
            
            print("✅ Тестовые данные очищены")
            
        except Exception as e:
            print(f"❌ Ошибка в тесте Telegram: {e}")
            raise


if __name__ == "__main__":
    async def run_tests():
        """Запуск тестов"""
        print("🚀 Запуск тестов настроек плагинов...")
        
        test_instance = TestPluginSettingsDirect()
        
        # Создаем движок с плагинами
        engine = SimpleScenarioEngine()
        
        mongo_plugin = MongoPlugin()
        amocrm_plugin = SimpleAmoCRMPlugin()
        telegram_plugin = SimpleTelegramPlugin()
        llm_plugin = SimpleLLMPlugin()
        
        try:
            # Инициализируем плагины
            await mongo_plugin.initialize()
            engine.register_plugin(mongo_plugin)
            
            await amocrm_plugin.initialize()
            await telegram_plugin.initialize()
            await llm_plugin.initialize()
            
            engine.register_plugin(amocrm_plugin)
            engine.register_plugin(telegram_plugin)
            engine.register_plugin(llm_plugin)
            
            plugins = {
                'mongo': mongo_plugin,
                'amocrm': amocrm_plugin,
                'telegram': telegram_plugin,
                'llm': llm_plugin
            }
            
            print("\n=== ТЕСТ НАСТРОЕК AMOCRM ===")
            await test_instance.test_amocrm_settings_cycle((engine, plugins))
            
            print("\n=== ТЕСТ НАСТРОЕК TELEGRAM ===")
            await test_instance.test_telegram_settings_cycle((engine, plugins))
            
            print("\n✅ Все тесты настроек плагинов прошли успешно!")
            
        except Exception as e:
            print(f"\n❌ Тесты не прошли: {e}")
            raise
    
    asyncio.run(run_tests()) 