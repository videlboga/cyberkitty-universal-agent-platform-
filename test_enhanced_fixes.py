#!/usr/bin/env python3
"""
🔧 ТЕСТ ИСПРАВЛЕНИЙ ENHANCED ORCHESTRATOR
Проверяем:
1. system_tools работает
2. Детальное логирование процесса
3. Реальный контент вместо заглушек
4. LLM-based ContentFixer
"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем путь к kittycore
sys.path.insert(0, str(Path(__file__).parent))

from kittycore.core.enhanced_content_system import EnhancedOrchestratorAgent
from kittycore.core.orchestrator import OrchestratorConfig

async def test_enhanced_fixes():
    """Тест всех исправлений"""
    
    print("🔧 ТЕСТ ИСПРАВЛЕНИЙ ENHANCED ORCHESTRATOR")
    print("=" * 80)
    
    # Создаём Enhanced Orchestrator
    config = OrchestratorConfig(
        orchestrator_id="test_fixes_orchestrator",
        max_agents=3,
        timeout=60
    )
    
    orchestrator = EnhancedOrchestratorAgent(config)
    
    # Тестовые задачи
    test_tasks = [
        "Создай файл hello_world.py с кодом print('Hello, World!')",
        "Создай файл с расчётом площади кота по формуле A = π * r²",
        "Создай JSON конфигурацию для веб-сервера"
    ]
    
    print(f"📋 Тестируем {len(test_tasks)} задач")
    print()
    
    for i, task in enumerate(test_tasks, 1):
        print(f"🎯 ЗАДАЧА {i}: {task}")
        print("-" * 60)
        
        try:
            # Выполняем задачу
            result = await orchestrator.solve_task(task)
            
            print(f"✅ Статус: {result.get('status', 'unknown')}")
            print(f"📁 Файлов создано: {result.get('files_processed', 0)}")
            print(f"🔧 Улучшений: {result.get('improvements_made', 0)}")
            
            # Проверяем созданные файлы
            enhanced_files = result.get('enhanced_files', [])
            for filepath in enhanced_files:
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"📄 {filepath}: {len(content)} символов")
                    
                    # Показываем превью контента
                    preview = content[:100].replace('\n', ' ')
                    print(f"   Превью: {preview}...")
                else:
                    print(f"❌ Файл не найден: {filepath}")
            
            print()
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print()
    
    # Проверяем детальные логи
    print("🔍 ПРОВЕРКА ДЕТАЛЬНОГО ЛОГИРОВАНИЯ")
    print("-" * 60)
    
    # Проверяем что логи процесса работают
    if hasattr(orchestrator, 'process_logger'):
        process_log = orchestrator.process_logger.process_log
        print(f"📊 Записей в логе процесса: {len(process_log)}")
        
        # Показываем последние записи
        for entry in process_log[-3:]:
            print(f"   {entry.get('type', 'unknown')}: {entry.get('timestamp', 'no-time')}")
    
    # Проверяем метаданные
    metadata_dir = "outputs/metadata"
    if os.path.exists(metadata_dir):
        metadata_files = os.listdir(metadata_dir)
        print(f"📊 Файлов метаданных: {len(metadata_files)}")
        for filename in metadata_files[:3]:
            print(f"   {filename}")
    
    print()
    print("✅ ТЕСТ ЗАВЕРШЁН")

if __name__ == "__main__":
    asyncio.run(test_enhanced_fixes()) 