#!/usr/bin/env python3
"""
🎯 ФИНАЛЬНЫЙ ТЕСТ ИНТЕГРАЦИИ OBSIDIAN
Проверяем что ObsidianOrchestrator создаёт РЕАЛЬНЫЕ файлы И сохраняет в vault
"""

import sys
import asyncio
from pathlib import Path

# Добавляем путь к kittycore
sys.path.insert(0, str(Path(__file__).parent))

from kittycore.core.obsidian_orchestrator import solve_with_obsidian_orchestrator


async def test_obsidian_integration():
    """Тестируем полную интеграцию ObsidianOrchestrator"""
    print("🎯 ФИНАЛЬНЫЙ ТЕСТ ИНТЕГРАЦИИ OBSIDIAN")
    print("=" * 60)
    
    # Задача для тестирования
    test_task = "Создай Python скрипт для расчёта площади круга по формуле A = π * r²"
    
    print(f"📋 Задача: {test_task}")
    print()
    
    try:
        # Выполняем задачу через ObsidianOrchestrator
        print("🚀 Запускаем ObsidianOrchestrator...")
        result = await solve_with_obsidian_orchestrator(test_task)
        
        print(f"✅ Статус: {result['status']}")
        print(f"⏱️ Время: {result['duration']:.2f}с")
        print(f"🤖 Агентов создано: {result['agents_created']}")
        print(f"📁 Vault: {result['vault_path']}")
        print()
        
        # Проверяем реальные файлы
        print("📂 ПРОВЕРКА РЕАЛЬНЫХ ФАЙЛОВ:")
        outputs_dir = Path("outputs")
        if outputs_dir.exists():
            files = list(outputs_dir.glob("*.py"))
            print(f"   🐍 Python файлов: {len(files)}")
            
            for py_file in files[-3:]:  # Последние 3 файла
                content = py_file.read_text(encoding='utf-8')
                print(f"   📄 {py_file.name} ({len(content)} символов)")
                
                # Проверяем что это реальный код, а не отчёт
                if "import" in content or "def " in content or "print(" in content:
                    print(f"      ✅ Содержит реальный Python код")
                    
                    # Проверяем формулу площади круга
                    if "π" in content or "pi" in content or "3.14" in content:
                        print(f"      ✅ Содержит формулу площади круга")
                    else:
                        print(f"      ⚠️ Не содержит формулу площади круга")
                else:
                    print(f"      ❌ НЕ содержит реальный код")
        else:
            print("   ❌ Папка outputs/ не найдена")
        
        print()
        
        # Проверяем ObsidianDB vault
        print("🗄️ ПРОВЕРКА OBSIDIAN VAULT:")
        vault_path = Path(result['vault_path'])
        if vault_path.exists():
            # Заметки агентов
            agent_notes = list(vault_path.glob("agents/**/*.md"))
            print(f"   📝 Заметок агентов: {len(agent_notes)}")
            
            # Артефакты
            artifact_notes = list(vault_path.glob("system/*artifact*.md"))
            print(f"   💎 Артефактов: {len(artifact_notes)}")
            
            # Проверяем последний артефакт
            if artifact_notes:
                latest_artifact = max(artifact_notes, key=lambda x: x.stat().st_mtime)
                content = latest_artifact.read_text(encoding='utf-8')
                print(f"   📄 Последний артефакт: {latest_artifact.name}")
                
                if "```python" in content and ("π" in content or "pi" in content):
                    print(f"      ✅ Содержит Python код с формулой")
                else:
                    print(f"      ⚠️ Не содержит ожидаемый код")
            
            # Системные заметки
            system_notes = list(vault_path.glob("system/*.md"))
            print(f"   🔧 Системных заметок: {len(system_notes)}")
            
        else:
            print(f"   ❌ Vault не найден: {vault_path}")
        
        print()
        
        # Проверяем результаты агентов
        print("🤖 РЕЗУЛЬТАТЫ АГЕНТОВ:")
        obsidian_results = result.get('obsidian_results', {})
        agent_results = obsidian_results.get('agent_results', [])
        
        print(f"   📊 Результатов агентов: {len(agent_results)}")
        
        for i, agent_result in enumerate(agent_results[-2:], 1):  # Последние 2
            agent_id = agent_result.get('agent_id', 'unknown')
            result_type = agent_result.get('result_type', 'unknown')
            content = agent_result.get('content', '')
            
            print(f"   {i}. Агент {agent_id} ({result_type})")
            
            # Проверяем что агент создал реальный контент
            if len(content) > 100:
                print(f"      ✅ Содержательный результат ({len(content)} символов)")
                
                if "```python" in content or "def " in content:
                    print(f"      ✅ Содержит Python код")
                else:
                    print(f"      ⚠️ Не содержит Python код")
            else:
                print(f"      ❌ Слишком короткий результат ({len(content)} символов)")
        
        print()
        
        # Итоговая оценка
        print("🎯 ИТОГОВАЯ ОЦЕНКА:")
        
        # Критерии успеха
        real_files_created = len(list(Path("outputs").glob("*.py"))) > 0 if Path("outputs").exists() else False
        vault_has_artifacts = len(list(vault_path.glob("system/*artifact*.md"))) > 0 if vault_path.exists() else False
        agents_produced_results = len(agent_results) > 0
        
        success_score = sum([real_files_created, vault_has_artifacts, agents_produced_results])
        
        print(f"   📄 Реальные файлы созданы: {'✅' if real_files_created else '❌'}")
        print(f"   🗄️ Артефакты в vault: {'✅' if vault_has_artifacts else '❌'}")
        print(f"   🤖 Агенты дали результаты: {'✅' if agents_produced_results else '❌'}")
        print()
        print(f"   🏆 ОЦЕНКА: {success_score}/3 ({success_score/3*100:.0f}%)")
        
        if success_score == 3:
            print("   🎉 ПОЛНЫЙ УСПЕХ! Интеграция работает идеально!")
        elif success_score == 2:
            print("   ✅ ХОРОШО! Интеграция работает с небольшими проблемами")
        elif success_score == 1:
            print("   ⚠️ ЧАСТИЧНО! Интеграция работает, но есть проблемы")
        else:
            print("   ❌ ПРОВАЛ! Интеграция не работает")
        
        return success_score == 3
        
    except Exception as e:
        print(f"❌ ОШИБКА ТЕСТА: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_obsidian_integration())
    exit(0 if success else 1) 