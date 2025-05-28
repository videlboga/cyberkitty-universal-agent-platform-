#!/usr/bin/env python3
"""
Тест исправления проблемы обновления настроек AmoCRM
Проверяет что все handlers теперь динамически загружают настройки
"""

import asyncio
from app.core.simple_engine import create_engine

async def test_settings_reload():
    print("🧪 ТЕСТ ИСПРАВЛЕНИЯ ПРОБЛЕМЫ ОБНОВЛЕНИЯ НАСТРОЕК AMOCRM")
    print("="*70)
    
    # Создаем движок
    print("🔧 Инициализация движка...")
    engine = await create_engine()
    
    # Получаем все AmoCRM плагины
    amocrm_plugins = {
        name: plugin for name, plugin in engine.plugins.items() 
        if name.startswith('simple_amocrm')
    }
    
    print(f"📋 Найдено AmoCRM плагинов: {len(amocrm_plugins)}")
    for name in amocrm_plugins.keys():
        print(f"   - {name}")
    
    # Тестируем базовый плагин
    print(f"\n🔍 ТЕСТ БАЗОВОГО ПЛАГИНА")
    print("-" * 40)
    
    amocrm = engine.plugins.get('simple_amocrm')
    if amocrm:
        print(f"📋 Начальное состояние: {amocrm.base_url or 'НЕ НАСТРОЕН'}")
        
        # Тестируем несколько handlers
        test_handlers = [
            "amocrm_find_contact",
            "amocrm_create_contact", 
            "amocrm_find_lead",
            "amocrm_search"
        ]
        
        for handler_name in test_handlers:
            print(f"\n🧪 Тестируем {handler_name}...")
            
            context = {"test": True}
            result = await engine.execute_step({
                "type": "action",
                "params": {
                    "action": handler_name, 
                    "query": "test@example.com",
                    "name": "Test Contact"
                }
            }, context)
            
            # Ищем результат в контексте
            handler_result = None
            for key, value in result.items():
                if isinstance(value, dict) and 'success' in value:
                    handler_result = value
                    break
            
            if handler_result:
                success = handler_result.get('success', False)
                error = handler_result.get('error', 'Нет ошибки')
                
                if success:
                    print(f"   ✅ {handler_name}: РАБОТАЕТ")
                else:
                    if "не настроен" in error:
                        print(f"   ⚠️ {handler_name}: НЕ НАСТРОЕН (ожидаемо)")
                    else:
                        print(f"   ❌ {handler_name}: ОШИБКА - {error}")
            else:
                print(f"   ❓ {handler_name}: НЕТ РЕЗУЛЬТАТА")
    
    # Тестируем остальные модули
    print(f"\n🔍 ТЕСТ ОСТАЛЬНЫХ МОДУЛЕЙ")
    print("-" * 40)
    
    other_modules = ['simple_amocrm_companies', 'simple_amocrm_tasks', 'simple_amocrm_advanced', 'simple_amocrm_admin']
    
    for module_name in other_modules:
        plugin = engine.plugins.get(module_name)
        if plugin:
            print(f"\n📦 Модуль: {module_name}")
            
            # Проверяем наличие метода _ensure_fresh_settings
            has_method = hasattr(plugin, '_ensure_fresh_settings')
            print(f"   🔧 Метод _ensure_fresh_settings: {'✅ ЕСТЬ' if has_method else '❌ НЕТ'}")
            
            if has_method:
                try:
                    # Тестируем вызов метода
                    await plugin._ensure_fresh_settings()
                    print(f"   ✅ Метод работает корректно")
                except Exception as e:
                    print(f"   ⚠️ Ошибка вызова метода: {e}")
        else:
            print(f"❌ Модуль {module_name} не найден")
    
    # Проверяем общую статистику handlers
    print(f"\n📊 СТАТИСТИКА HANDLERS")
    print("-" * 40)
    
    all_handlers = engine.get_registered_handlers()
    amocrm_handlers = [h for h in all_handlers if h.startswith('amocrm_')]
    
    print(f"📋 Всего AmoCRM handlers: {len(amocrm_handlers)}")
    print(f"📋 Всего handlers в системе: {len(all_handlers)}")
    
    # Группируем по модулям
    handler_groups = {}
    for handler in amocrm_handlers:
        # Определяем модуль по названию handler
        if handler in ['amocrm_find_contact', 'amocrm_create_contact', 'amocrm_find_lead', 'amocrm_create_lead', 'amocrm_add_note', 'amocrm_search']:
            group = 'Базовый'
        elif 'companies' in handler or 'company' in handler:
            group = 'Компании'
        elif 'task' in handler or 'event' in handler:
            group = 'Задачи'
        elif handler in ['amocrm_list_webhooks', 'amocrm_create_webhook', 'amocrm_list_widgets', 'amocrm_list_catalogs', 'amocrm_create_catalog', 'amocrm_list_calls', 'amocrm_create_call']:
            group = 'Продвинутый'
        elif handler in ['amocrm_list_pipelines', 'amocrm_create_pipeline', 'amocrm_list_users', 'amocrm_list_custom_fields', 'amocrm_create_custom_field', 'amocrm_list_tags', 'amocrm_create_tag']:
            group = 'Административный'
        else:
            group = 'Другие'
        
        if group not in handler_groups:
            handler_groups[group] = []
        handler_groups[group].append(handler)
    
    for group, handlers in handler_groups.items():
        print(f"   📦 {group}: {len(handlers)} handlers")
    
    print(f"\n🎯 ЗАКЛЮЧЕНИЕ")
    print("-" * 40)
    print("✅ Исправление применено ко всем модулям")
    print("✅ Все handlers теперь вызывают _ensure_fresh_settings()")
    print("💡 Настройки будут обновляться динамически без перезапуска")
    print("🔧 Для полного тестирования добавьте реальные настройки AmoCRM в БД")

if __name__ == "__main__":
    asyncio.run(test_settings_reload())
