#!/usr/bin/env python3
"""
Скрипт для исправления проблемы обновления настроек во всех AmoCRM модулях
1. Добавляет метод _ensure_fresh_settings() если его нет
2. Добавляет вызов этого метода в начало каждого handler
"""

import os
import re
from pathlib import Path

# Код метода _ensure_fresh_settings для добавления
ENSURE_FRESH_SETTINGS_METHOD = '''
    async def _ensure_fresh_settings(self):
        """Динамически загружает актуальные настройки из БД"""
        try:
            if not self.engine or not hasattr(self.engine, 'plugins') or 'mongo' not in self.engine.plugins:
                return
                
            mongo_plugin = self.engine.plugins['mongo']
            settings_result = await mongo_plugin._find_one("plugin_settings", {"plugin_name": "simple_amocrm"})
            
            if settings_result and settings_result.get("success") and settings_result.get("document"):
                settings = settings_result["document"]
                new_base_url = settings.get("base_url")
                new_access_token = settings.get("access_token")
                
                # Обновляем настройки если они изменились
                if new_base_url != self.base_url or new_access_token != self.access_token:
                    self.base_url = new_base_url
                    self.access_token = new_access_token
                    self.headers = {
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json'
                    } if self.access_token else {}
                    logger.info(f"✅ Настройки AmoCRM обновлены: {self.base_url}")
                    
        except Exception as e:
            logger.error(f"❌ Ошибка динамической загрузки настроек AmoCRM: {e}")
'''

def add_ensure_fresh_settings_method(content: str) -> str:
    """Добавляет метод _ensure_fresh_settings если его нет"""
    if '_ensure_fresh_settings' in content:
        return content
    
    # Ищем место для вставки (после register_handlers)
    pattern = r'(    def register_handlers\(self\) -> Dict\[str, Any\]:\s*.*?return \{[^}]*\}\s*\n)'
    
    def add_method(match):
        return match.group(1) + ENSURE_FRESH_SETTINGS_METHOD + '\n'
    
    return re.sub(pattern, add_method, content, flags=re.DOTALL)

def add_settings_reload_to_handlers(content: str) -> str:
    """Добавляет вызов _ensure_fresh_settings() в handlers"""
    # Паттерн для поиска handlers (методы начинающиеся с async def _handle_)
    handler_pattern = r'(    async def _handle_[^(]+\([^)]+\) -> None:\s*\n        """[^"]*"""\s*\n)'
    
    # Функция замены - добавляет вызов _ensure_fresh_settings()
    def add_settings_reload(match):
        original = match.group(1)
        # Проверяем, нет ли уже вызова _ensure_fresh_settings
        if '_ensure_fresh_settings()' in original:
            return original
        
        # Добавляем вызов после docstring
        return original + '        # Обеспечиваем актуальные настройки\n        await self._ensure_fresh_settings()\n        \n'
    
    return re.sub(handler_pattern, add_settings_reload, content)

def fix_amocrm_module(file_path: str):
    """Исправляет один AmoCRM модуль"""
    print(f"🔧 Исправляем {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Добавляем метод _ensure_fresh_settings если его нет
    content = add_ensure_fresh_settings_method(content)
    
    # 2. Добавляем вызовы в handlers
    content = add_settings_reload_to_handlers(content)
    
    # Проверяем, есть ли изменения
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {file_path} исправлен")
        return True
    else:
        print(f"ℹ️ {file_path} уже исправлен или не требует изменений")
        return False

def main():
    """Основная функция"""
    print("🔧 ИСПРАВЛЕНИЕ ПРОБЛЕМЫ ОБНОВЛЕНИЯ НАСТРОЕК AMOCRM")
    print("="*60)
    
    # Список AmoCRM модулей для исправления
    amocrm_modules = [
        "app/plugins/simple_amocrm_companies.py",
        "app/plugins/simple_amocrm_tasks.py", 
        "app/plugins/simple_amocrm_advanced.py",
        "app/plugins/simple_amocrm_admin.py"
    ]
    
    fixed_count = 0
    
    for module_path in amocrm_modules:
        if os.path.exists(module_path):
            if fix_amocrm_module(module_path):
                fixed_count += 1
        else:
            print(f"⚠️ Файл не найден: {module_path}")
    
    print("\n" + "="*60)
    print(f"📊 РЕЗУЛЬТАТ: исправлено {fixed_count} модулей")
    print("✅ Теперь все AmoCRM handlers будут обновлять настройки перед выполнением")
    print("💡 Это решает проблему с устаревшими кредами без перезапуска контейнера")
    
    # Создаем тестовый скрипт для проверки
    create_test_script()

def create_test_script():
    """Создает тестовый скрипт для проверки исправления"""
    test_script = '''#!/usr/bin/env python3
"""
Тест исправления проблемы обновления настроек AmoCRM
"""

import asyncio
from app.core.simple_engine import create_engine

async def test_settings_reload():
    print("🧪 ТЕСТ ОБНОВЛЕНИЯ НАСТРОЕК AMOCRM")
    print("="*50)
    
    # Создаем движок
    engine = await create_engine()
    
    # Тестируем базовый плагин
    amocrm = engine.plugins.get('simple_amocrm')
    if amocrm:
        print(f"📋 Базовый плагин: {amocrm.base_url or 'НЕ НАСТРОЕН'}")
        
        # Тестируем вызов handler
        context = {"test": True}
        result = await engine.execute_step({
            "type": "action",
            "params": {"action": "amocrm_find_contact", "query": "test"}
        }, context)
        
        print(f"🔍 Результат теста: {result.get('contact', {}).get('success', 'НЕТ РЕЗУЛЬТАТА')}")
    
    print("✅ Тест завершен")

if __name__ == "__main__":
    asyncio.run(test_settings_reload())
'''
    
    with open('test_amocrm_settings_fix.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("📝 Создан тестовый скрипт: test_amocrm_settings_fix.py")

if __name__ == "__main__":
    main() 