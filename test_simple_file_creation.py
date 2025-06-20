#!/usr/bin/env python3
import asyncio
from kittycore.agents.intellectual_agent import IntellectualAgent

async def test_direct_file_creation():
    print('🔍 Тест прямого создания файла')
    
    # Создаём агента напрямую с простой задачей
    subtask = {
        "description": "создать python файл hello.py с приветствием",
        "type": "file_creation", 
        "priority": 1,
        "estimated_time": 30
    }
    
    agent = IntellectualAgent("test_agent", subtask)
    
    # Проверяем какие инструменты доступны (через tools атрибут)
    print(f'🔧 Доступные инструменты: {list(agent.tools.keys())}')
    
    result = await agent.execute_task()
    
    print(f'📊 Статус: {result.get("status", "unknown")}')
    print(f'📁 Файлы в created_files: {result.get("created_files", [])}')
    print(f'📋 Количество файлов: {len(result.get("created_files", []))}')
    
    # Проверяем что файлы существуют
    import os
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

if __name__ == '__main__':
    asyncio.run(test_direct_file_creation()) 