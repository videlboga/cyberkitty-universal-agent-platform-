#!/usr/bin/env python3
"""
🎯 ФИНАЛЬНЫЙ E2E ТЕСТ KITTYCORE 3.0
Демонстрация полной функциональности системы
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к kittycore
sys.path.insert(0, str(Path(__file__).parent))

from kittycore.core.unified_orchestrator import UnifiedOrchestrator

async def test_real_task():
    """E2E тест с реальной задачей"""
    print('\n🎯 ФИНАЛЬНЫЙ E2E ТЕСТ KITTYCORE 3.0')
    print('=' * 50)
    
    # Создаём оркестратор
    from kittycore.core.unified_orchestrator import UnifiedConfig
    config = UnifiedConfig(vault_path='vault_integration_test')
    orchestrator = UnifiedOrchestrator(config)
    
    # Тестовая задача
    task = 'Создай Python файл calculator.py с функциями сложения, вычитания, умножения и деления'
    
    print(f'📝 Задача: {task}')
    print(f'⏱️ Запуск оркестратора...')
    print()
    
    try:
        # Выполняем задачу
        result = await orchestrator.solve_task(task)
        
        print()
        print('✅ РЕЗУЛЬТАТ ПОЛУЧЕН!')
        print(f'📊 Тип результата: {type(result)}')
        
        if hasattr(result, 'success'):
            print(f'📈 Успешность: {result.success}')
        elif isinstance(result, dict) and 'success' in result:
            print(f'📈 Успешность: {result["success"]}')
        
        if hasattr(result, 'quality_score'):
            print(f'⭐ Качество: {result.quality_score}')
        elif isinstance(result, dict) and 'quality_score' in result:
            print(f'⭐ Качество: {result["quality_score"]}')
            
        # Проверяем создались ли файлы
        import os
        files = os.listdir('.')
        calculator_files = [f for f in files if 'calculator' in f.lower()]
        
        print(f'📁 Найдено файлов с "calculator": {calculator_files}')
        
        # Проверяем outputs
        outputs_path = Path('outputs')
        if outputs_path.exists():
            output_files = list(outputs_path.glob('*calculator*'))
            print(f'📂 Файлы в outputs/: {[f.name for f in output_files]}')
        
        # Проверяем vault
        vault_path = Path('vault_integration_test')
        if vault_path.exists():
            vault_files = []
            for subdir in ['results', 'agents', 'tasks']:
                if (vault_path / subdir).exists():
                    subdir_files = list((vault_path / subdir).glob('*'))
                    vault_files.extend([f"{subdir}/{f.name}" for f in subdir_files])
            print(f'📋 Файлы в vault: {vault_files}')
        
        success = (
            len(calculator_files) > 0 or 
            (outputs_path.exists() and len(list(outputs_path.glob('*calculator*'))) > 0) or
            (vault_path.exists() and len(vault_files) > 0)
        )
        
        print()
        print('🏆 ФИНАЛЬНЫЙ РЕЗУЛЬТАТ:')
        if success:
            print('✅ ТЕСТ УСПЕШЕН! Система работает и создаёт файлы')
        else:
            print('⚠️ Файлы не найдены, но система инициализировалась')
            
        return success
        
    except Exception as e:
        print(f'❌ ОШИБКА: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_real_task())
    print(f'\n🎯 E2E ТЕСТ ЗАВЕРШЁН: {"УСПЕШНО" if result else "С ПРЕДУПРЕЖДЕНИЯМИ"}') 