#!/usr/bin/env python3
import asyncio
import kittycore
import os

async def test_files_count():
    print('🔍 Тест подсчёта файлов после исправления')
    
    orchestrator = kittycore.create_orchestrator()
    result = await orchestrator.solve_task('создать python файл hello.py с приветствием')
    
    print(f'📊 Статус: {result.get("status", "unknown")}')
    print(f'📁 Файлы в created_files: {result.get("created_files", [])}')
    print(f'📋 Количество файлов: {len(result.get("created_files", []))}')
    
    # Проверяем что файлы действительно существуют
    files = result.get('created_files', [])
    existing_files = 0
    
    print('\n📂 Проверка существования файлов:')
    for file_path in files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f'   ✅ {file_path} существует ({size} байт)')
            existing_files += 1
        else:
            print(f'   ❌ {file_path} не найден')
    
    print(f'\n📊 ИТОГ:')
    print(f'   📁 Заявлено файлов: {len(files)}')
    print(f'   ✅ Существует файлов: {existing_files}')
    print(f'   🎯 Соответствие: {"✅ ДА" if len(files) == existing_files else "❌ НЕТ"}')
    
    # Дополнительно: проверим что в outputs/ действительно есть файлы  
    outputs_files = []
    if os.path.exists('outputs'):
        outputs_files = [f for f in os.listdir('outputs') if f.endswith('.py')]
        print(f'   📁 Python файлов в outputs/: {len(outputs_files)}')
        for f in outputs_files[-3:]:  # Показываем последние 3
            print(f'      📄 {f}')

if __name__ == '__main__':
    asyncio.run(test_files_count()) 