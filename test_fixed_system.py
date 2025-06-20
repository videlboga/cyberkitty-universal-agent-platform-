#!/usr/bin/env python3
"""
Тест исправленной системы валидации KittyCore 3.0
"""

import asyncio
from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig

async def test_fixed_system():
    """Тест исправленной системы"""
    print("🧪 ТЕСТ ИСПРАВЛЕННОЙ СИСТЕМЫ ВАЛИДАЦИИ")
    print("=" * 50)
    
    config = UnifiedConfig()
    orchestrator = UnifiedOrchestrator(config)
    
    # Тест простой задачи
    print("📋 Тест: создай простой hello world файл")
    result = await orchestrator.solve_task('создай простой hello world файл')
    
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"⭐ Качество: {result.get('final_result', {}).get('quality_score', 0):.2f}")
    print(f"📁 Файлов создано: {len(result.get('final_result', {}).get('created_files', []))}")
    
    # Проверяем созданные файлы
    import os
    files = [f for f in os.listdir('.') if f.endswith(('.py', '.txt', '.html', '.json'))]
    print(f"🗂️  Файлы в директории: {files}")
    
    if files:
        for file in files[:3]:  # Проверяем первые 3 файла
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()[:200]
                print(f"\n📄 {file}:")
                print(f"   Размер: {len(content)} символов")
                print(f"   HTML: {'<!doctype' in content.lower() or '<html' in content.lower()}")
                print(f"   KittyCore: {'Генерировано KittyCore' in content}")
            except Exception as e:
                print(f"   ❌ Ошибка чтения: {e}")

if __name__ == "__main__":
    asyncio.run(test_fixed_system()) 