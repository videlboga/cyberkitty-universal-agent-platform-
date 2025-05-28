#!/usr/bin/env python3
"""
Комплексный тест всех 49 AmoCRM handlers
Проверяет что каждый handler:
1. Технически выполняется без критических ошибок
2. Функционально возвращает корректный результат
"""

import asyncio
import json
from app.core.simple_engine import create_engine

# Список всех AmoCRM handlers для тестирования
AMOCRM_HANDLERS = [
    # Базовый модуль (6 handlers)
    "amocrm_find_contact",
    "amocrm_create_contact", 
    "amocrm_find_lead",
    "amocrm_create_lead",
    "amocrm_add_note",
    "amocrm_search",
    
    # Companies модуль (8 handlers)
    "amocrm_find_company",
    "amocrm_create_company",
    "amocrm_update_company",
    "amocrm_delete_company",
    "amocrm_list_companies",
    "amocrm_add_company_contact",
    "amocrm_remove_company_contact",
    "amocrm_get_company_contacts",
    
    # Tasks модуль (8 handlers)
    "amocrm_create_task",
    "amocrm_update_task",
    "amocrm_complete_task",
    "amocrm_delete_task",
    "amocrm_list_tasks",
    "amocrm_create_event",
    "amocrm_update_event",
    "amocrm_list_events",
    
    # Advanced модуль (12 handlers)
    "amocrm_list_webhooks",
    "amocrm_create_webhook",
    "amocrm_delete_webhook",
    "amocrm_list_widgets",
    "amocrm_install_widget",
    "amocrm_uninstall_widget",
    "amocrm_list_catalogs",
    "amocrm_create_catalog",
    "amocrm_list_calls",
    "amocrm_create_call",
    "amocrm_get_account_info",
    "amocrm_get_user_info",
    
    # Admin модуль (14 handlers)
    "amocrm_list_pipelines",
    "amocrm_create_pipeline",
    "amocrm_update_pipeline",
    "amocrm_delete_pipeline",
    "amocrm_list_users",
    "amocrm_create_user",
    "amocrm_update_user",
    "amocrm_list_custom_fields",
    "amocrm_create_custom_field",
    "amocrm_update_custom_field",
    "amocrm_delete_custom_field",
    "amocrm_list_tags",
    "amocrm_create_tag",
    "amocrm_delete_tag"
]

async def test_handler(engine, handler_name: str) -> dict:
    """Тестирует один handler"""
    try:
        # Базовые параметры для тестирования
        test_params = {
            "query": "test@example.com",
            "name": "Test Contact",
            "phone": "+79991234567",
            "email": "test@example.com",
            "contact_id": "123456",
            "lead_id": "123456",
            "company_id": "123456",
            "task_id": "123456",
            "entity_type": "contacts",
            "entity_id": "123456",
            "note_text": "Test note",
            "output_var": "test_result"
        }
        
        context = {"test": True}
        
        # Выполняем handler
        result = await engine.execute_step({
            "type": "action",
            "params": {
                "action": handler_name,
                **test_params
            }
        }, context)
        
        # Ищем результат в контексте
        handler_result = None
        for key, value in result.items():
            if isinstance(value, dict) and 'success' in value:
                handler_result = value
                break
        
        if handler_result:
            return {
                "handler": handler_name,
                "technical_success": True,
                "functional_success": handler_result.get('success', False),
                "error": handler_result.get('error'),
                "result": "OK" if handler_result.get('success') else "FAIL"
            }
        else:
            return {
                "handler": handler_name,
                "technical_success": True,
                "functional_success": False,
                "error": "Нет результата в контексте",
                "result": "NO_RESULT"
            }
            
    except Exception as e:
        return {
            "handler": handler_name,
            "technical_success": False,
            "functional_success": False,
            "error": str(e),
            "result": "EXCEPTION"
        }

async def test_all_handlers():
    """Тестирует все AmoCRM handlers"""
    print("🧪 КОМПЛЕКСНЫЙ ТЕСТ ВСЕХ AMOCRM HANDLERS")
    print("="*70)
    
    # Создаем движок
    print("🔧 Инициализация движка...")
    engine = await create_engine()
    
    # Получаем зарегистрированные handlers
    all_handlers = engine.get_registered_handlers()
    amocrm_handlers_found = [h for h in all_handlers if h.startswith('amocrm_')]
    
    print(f"📋 Найдено AmoCRM handlers: {len(amocrm_handlers_found)}")
    print(f"📋 Ожидалось handlers: {len(AMOCRM_HANDLERS)}")
    
    # Проверяем какие handlers отсутствуют
    missing_handlers = set(AMOCRM_HANDLERS) - set(amocrm_handlers_found)
    if missing_handlers:
        print(f"⚠️ Отсутствующие handlers: {missing_handlers}")
    
    # Тестируем все найденные handlers
    results = []
    
    print(f"\n🔍 ТЕСТИРОВАНИЕ {len(amocrm_handlers_found)} HANDLERS")
    print("-" * 70)
    
    for i, handler_name in enumerate(amocrm_handlers_found, 1):
        print(f"🧪 [{i:2d}/{len(amocrm_handlers_found)}] Тестируем {handler_name}...")
        
        result = await test_handler(engine, handler_name)
        results.append(result)
        
        # Показываем результат
        status = "✅" if result["technical_success"] else "❌"
        func_status = "✅" if result["functional_success"] else "⚠️"
        
        print(f"   {status} Технически: {'OK' if result['technical_success'] else 'FAIL'}")
        print(f"   {func_status} Функционально: {result['result']}")
        
        if result["error"] and "не настроен" not in result["error"]:
            print(f"   🔍 Ошибка: {result['error'][:100]}...")
    
    # Статистика
    print(f"\n📊 СТАТИСТИКА ТЕСТИРОВАНИЯ")
    print("-" * 70)
    
    technical_success = sum(1 for r in results if r["technical_success"])
    functional_success = sum(1 for r in results if r["functional_success"])
    
    print(f"📋 Всего протестировано: {len(results)}")
    print(f"✅ Технически успешных: {technical_success}/{len(results)} ({technical_success/len(results)*100:.1f}%)")
    print(f"🎯 Функционально успешных: {functional_success}/{len(results)} ({functional_success/len(results)*100:.1f}%)")
    
    # Группировка по результатам
    by_result = {}
    for result in results:
        key = result["result"]
        if key not in by_result:
            by_result[key] = []
        by_result[key].append(result["handler"])
    
    print(f"\n📈 ГРУППИРОВКА ПО РЕЗУЛЬТАТАМ:")
    for result_type, handlers in by_result.items():
        print(f"   {result_type}: {len(handlers)} handlers")
        if len(handlers) <= 10:  # Показываем только если не слишком много
            for handler in handlers:
                print(f"     - {handler}")
    
    # Анализ ошибок
    print(f"\n🔍 АНАЛИЗ ОШИБОК:")
    error_types = {}
    for result in results:
        if result["error"]:
            error_key = result["error"][:50] + "..." if len(result["error"]) > 50 else result["error"]
            if error_key not in error_types:
                error_types[error_key] = []
            error_types[error_key].append(result["handler"])
    
    for error, handlers in error_types.items():
        print(f"   📄 {error}: {len(handlers)} handlers")
    
    print(f"\n🎯 ЗАКЛЮЧЕНИЕ")
    print("-" * 70)
    
    if technical_success == len(results):
        print("✅ Все handlers технически работают корректно")
    else:
        print(f"⚠️ {len(results) - technical_success} handlers имеют технические проблемы")
    
    if functional_success > 0:
        print(f"✅ {functional_success} handlers функционально работают")
    else:
        print("⚠️ Ни один handler не работает функционально (нужны настройки)")
    
    print("💡 Для полного функционального тестирования добавьте настройки AmoCRM в БД")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_all_handlers()) 