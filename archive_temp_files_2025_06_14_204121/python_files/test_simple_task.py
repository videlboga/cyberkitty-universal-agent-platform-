#!/usr/bin/env python3
"""
🔧 ПРОСТОЙ ТЕСТ ИСПРАВЛЕНИЙ
Проверяем JSON парсинг и создание реального контента
"""

import asyncio
import sys
import os
sys.path.append('.')

from kittycore.core.orchestrator import solve_with_orchestrator

async def test_simple_task():
    """Простая задача для проверки исправлений"""
    
    print("🔧 ПРОСТОЙ ТЕСТ ИСПРАВЛЕНИЙ")
    print("=" * 50)
    
    # Очень простая задача
    task = "Создать HTML страницу с информацией о котятах"
    
    print(f"📋 ЗАДАЧА: {task}")
    print(f"🎯 ОЖИДАЕМ: HTML файл с реальным контентом о котятах")
    
    try:
        result = await solve_with_orchestrator(task)
        
        print(f"\n📊 РЕЗУЛЬТАТ:")
        print(f"✅ Успех: {result.get('success', False)}")
        
        # Проверяем файлы
        print(f"\n📁 СОЗДАННЫЕ ФАЙЛЫ:")
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith('.html') and 'котят' in file.lower():
                    filepath = os.path.join(root, file)
                    size = os.path.getsize(filepath)
                    print(f"  📄 {filepath} ({size} байт)")
                    
                    # Читаем содержимое
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            print(f"    🔍 Содержимое ({len(content)} символов):")
                            print(f"    {content[:200]}...")
                            
                            # Проверяем качество контента
                            if "котят" in content.lower() and len(content) > 100:
                                print(f"    ✅ Контент выглядит реальным!")
                                return True
                            else:
                                print(f"    ❌ Контент слишком простой или нерелевантный")
                                return False
                    except Exception as e:
                        print(f"    ❌ Ошибка чтения: {e}")
                        return False
        
        print(f"❌ HTML файлы с котятами не найдены")
        return False
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False

async def main():
    print("🚀 ТЕСТ ПРОСТОЙ ЗАДАЧИ")
    print("Проверяем исправления JSON парсинга и контента")
    print("=" * 60)
    
    success = await test_simple_task()
    
    print(f"\n📊 ИТОГ:")
    if success:
        print(f"🎉 ИСПРАВЛЕНИЯ РАБОТАЮТ! Система создаёт реальный контент")
    else:
        print(f"❌ НУЖНЫ ДОПОЛНИТЕЛЬНЫЕ ИСПРАВЛЕНИЯ")

if __name__ == "__main__":
    asyncio.run(main()) 