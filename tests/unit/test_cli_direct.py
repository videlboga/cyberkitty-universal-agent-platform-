#!/usr/bin/env python3
"""
🧪 Прямой тест CLI с системой качества
"""

import asyncio
from kittycore_cli import process_request

async def test_cli_directly():
    """Тест CLI напрямую"""
    print("🧪 ПРЯМОЙ ТЕСТ CLI")
    print("=" * 30)
    
    # Перехватываем вывод вместо печати в консоль
    import io
    import sys
    from contextlib import redirect_stdout
    
    # Тест 1: Проблемная задача
    print("🌐 ТЕСТ 1: Задача с проблемами")
    print("-" * 40)
    
    # Перехватываем вывод CLI
    output_buffer = io.StringIO()
    
    with redirect_stdout(output_buffer):
        await process_request("Сделай сайт с котятами")
    
    cli_output = output_buffer.getvalue()
    
    # Анализируем что вывел CLI
    print("📊 АНАЛИЗ ВЫВОДА CLI:")
    
    if "🚨 ОБНАРУЖЕНЫ КРИТИЧЕСКИЕ ПРОБЛЕМЫ" in cli_output:
        print("   ✅ CLI ОБНАРУЖИЛ ПРОБЛЕМЫ!")
        
        if "ЗАДАЧА СОЗДАНИЯ БЕЗ ФАЙЛОВ" in cli_output:
            print("   ✅ Обнаружена проблема: нет файлов")
        
        if "ЛЕВЫЕ ДЕЙСТВИЯ" in cli_output:
            print("   ✅ Обнаружена проблема: httpbin.org")
            
        if "🔧 АВТОКОРРЕКЦИЯ" in cli_output:
            print("   ✅ Активирована автокоррекция")
            
        print("\n🎉 СИСТЕМА КАЧЕСТВА CLI РАБОТАЕТ ОТЛИЧНО!")
        
    elif "✅ ПРОВЕРКА КАЧЕСТВА ПРОЙДЕНА" in cli_output:
        print("   ❌ CLI НЕ ОБНАРУЖИЛ ПРОБЛЕМЫ")
        print("   🐛 Система качества не работает")
        
        print("\n📝 ОТЛАДОЧНАЯ ИНФОРМАЦИЯ:")
        lines = cli_output.split('\n')
        for i, line in enumerate(lines):
            if "ПРОВЕРКА КАЧЕСТВА" in line:
                print(f"   Строка {i}: {line}")
                # Показываем контекст
                for j in range(max(0, i-3), min(len(lines), i+4)):
                    print(f"     {j}: {lines[j]}")
                break
    else:
        print("   ❓ НЕОЖИДАННЫЙ РЕЗУЛЬТАТ")
    
    # Показываем ключевые части вывода
    print(f"\n📋 КЛЮЧЕВЫЕ ЧАСТИ ВЫВОДА:")
    lines = cli_output.split('\n')
    for line in lines:
        if any(keyword in line for keyword in ['ПРОВЕРКА КАЧЕСТВА', 'КРИТИЧЕСКИЕ ПРОБЛЕМЫ', 'АВТОКОРРЕКЦИЯ', 'ЛЕВЫЕ ДЕЙСТВИЯ']):
            print(f"   {line}")

if __name__ == "__main__":
    asyncio.run(test_cli_directly()) 