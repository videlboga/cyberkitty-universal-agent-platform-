#!/usr/bin/env python3
"""
Тест улучшенных промптов KittyCore 3.0
Проверяем что система создаёт РЕАЛЬНЫЙ контент вместо заглушек
"""

import asyncio
from kittycore.core.unified_orchestrator import UnifiedOrchestrator, UnifiedConfig

async def test_improved_prompts():
    """Тест улучшенных промптов"""
    print("🧪 ТЕСТ УЛУЧШЕННЫХ ПРОМПТОВ")
    print("=" * 50)
    
    config = UnifiedConfig()
    orchestrator = UnifiedOrchestrator(config)
    
    # Тест простой задачи с анализом рынка
    print("📋 Тест: создай анализ топ-3 CRM систем")
    result = await orchestrator.solve_task('создай анализ топ-3 CRM систем с ценами и функциями')
    
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"⭐ Качество: {result.get('final_result', {}).get('quality_score', 0):.2f}")
    print(f"📁 Файлов создано: {len(result.get('final_result', {}).get('created_files', []))}")
    
    # Проверяем созданные файлы на качество контента
    import os
    created_files = []
    for file_pattern in ['*.txt', '*.json', '*.py', '*.html']:
        import glob
        files = glob.glob(file_pattern)
        created_files.extend(files)
    
    print(f"\n🗂️  Файлы в директории: {created_files}")
    
    # Анализируем содержимое файлов
    fake_indicators = [
        'первое приложение', 'второе приложение', 'третье приложение',
        'opis первого', 'opis второго', 'первая проблема', 'вторая проблема'
    ]
    
    quality_indicators = [
        'Битрикс24', 'Salesforce', 'AmoCRM', 'HubSpot', 'Pipedrive',
        'руб/мес', '$/мес', 'рейтинг', 'пользователей', 'функции'
    ]
    
    for file_path in created_files[-5:]:  # Проверяем последние 5 файлов
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()[:200]  # Первые 200 символов
                
                # Проверяем на заглушки
                fake_count = sum(1 for indicator in fake_indicators if indicator in content)
                quality_count = sum(1 for indicator in quality_indicators if indicator in content)
                
                print(f"\n📄 {file_path}:")
                print(f"   Размер: {len(content)} символов")
                print(f"   Заглушки: {fake_count} найдено")
                print(f"   Качественный контент: {quality_count} найдено")
                
                if fake_count > 0:
                    print(f"   ❌ ОБНАРУЖЕНЫ ЗАГЛУШКИ!")
                elif quality_count > 0:
                    print(f"   ✅ КАЧЕСТВЕННЫЙ КОНТЕНТ!")
                else:
                    print(f"   ⚠️ Нейтральный контент")
                    
            except Exception as e:
                print(f"   ❌ Ошибка чтения: {e}")

if __name__ == "__main__":
    asyncio.run(test_improved_prompts()) 