#!/usr/bin/env python3
"""
Тест интеграции OrchestratorAgent с Obsidian
"""

import asyncio
import os
from pathlib import Path
from kittycore.core.orchestrator import OrchestratorAgent, OrchestratorConfig


async def test_orchestrator_obsidian():
    """Тест работы OrchestratorAgent с Obsidian интеграцией"""
    
    print("🧭 Тест OrchestratorAgent + Obsidian Integration")
    print("=" * 50)
    
    # Настройка с включенным Obsidian
    config = OrchestratorConfig(
        orchestrator_id="test_orchestrator",
        enable_obsidian=True,
        obsidian_vault_path="./test_obsidian_vault",
        max_agents=3
    )
    
    # Создание оркестратора
    orchestrator = OrchestratorAgent(config)
    
    print(f"✅ OrchestratorAgent создан с Obsidian: {config.obsidian_vault_path}")
    
    # Тест простой задачи
    print("\n1️⃣ Тестируем простую задачу...")
    
    simple_task = "Создать файл hello.txt с текстом 'Привет от KittyCore 3.0!'"
    
    try:
        result = await orchestrator.solve_task(simple_task)
        
        print(f"✅ Задача выполнена за {result.get('duration', 0):.2f}с")
        print(f"📊 Статус: {result.get('status', 'unknown')}")
        print(f"🤖 Создано агентов: {len(result.get('team', {}))}")
        
        # Показываем больше деталей
        if result.get('status') == 'error':
            print(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
            if 'execution' in result:
                execution = result['execution']
                print(f"🔍 Детали выполнения:")
                print(f"  - Результаты: {execution.get('results', [])}")
                print(f"  - Ошибки: {execution.get('errors', [])}")
        
        # Проверяем статистику Obsidian
        stats = orchestrator.get_statistics()
        if 'obsidian' in stats:
            print(f"📝 Obsidian активен: {stats['obsidian']['vault_path']}")
        
        # Проверяем что файлы создались
        vault_path = Path(config.obsidian_vault_path)
        if vault_path.exists():
            print(f"\n📂 Структура vault:")
            md_files = list(vault_path.rglob("*.md"))
            if md_files:
                for md_file in md_files:
                    print(f"  📄 {md_file.relative_to(vault_path)}")
            else:
                print("  (пусто - заметки не создались)")
        
        if result.get('status') == 'completed':
            print(f"\n🎉 Задача выполнена! Агенты + Obsidian = ❤️")
        else:
            print(f"\n⚠️  Интеграция инициализирована, но задача не выполнилась")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_orchestrator_obsidian()) 