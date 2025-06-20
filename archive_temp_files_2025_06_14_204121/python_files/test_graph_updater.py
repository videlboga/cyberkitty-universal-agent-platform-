#!/usr/bin/env python3
"""
Тест GraphUpdater - автоматическое обновление графа в реальном времени
"""

import asyncio
from pathlib import Path
from kittycore.obsidian_integration import GraphUpdater


async def test_graph_updater():
    """Тест работы GraphUpdater"""
    
    print("📊 Тест GraphUpdater - обновление графа в реальном времени")
    print("=" * 55)
    
    # Используем уже созданный vault
    vault_path = Path("./test_obsidian_vault")
    
    if not vault_path.exists():
        print(f"❌ Vault не найден: {vault_path}")
        return
    
    # Создание GraphUpdater
    graph_updater = GraphUpdater(vault_path)
    
    print(f"✅ GraphUpdater инициализирован для: {vault_path}")
    
    # Единоразовое обновление
    print("\n1️⃣ Выполняем обновление графа...")
    
    await graph_updater.update_graph(force=True)
    
    # Получение статистики
    stats = graph_updater.get_graph_stats()
    
    print(f"📊 Статистика графа:")
    print(f"  - Узлов: {stats['nodes_total']}")
    print(f"  - Связей: {stats['edges_total']}")
    print(f"  - Типы узлов: {stats['node_types']}")
    print(f"  - Типы связей: {stats['edge_types']}")
    
    # Проверяем созданный JSON
    graph_file = vault_path / "graph_data.json"
    if graph_file.exists():
        print(f"\n✅ График экспортирован: {graph_file}")
        print(f"📄 Размер файла: {graph_file.stat().st_size} байт")
        
        # Показываем небольшой превью
        import json
        with open(graph_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"🔍 Превью данных:")
        print(f"  - Узлов в JSON: {len(data.get('nodes', []))}")
        print(f"  - Связей в JSON: {len(data.get('edges', []))}")
        print(f"  - Обновлено: {data.get('metadata', {}).get('updated_at', 'неизвестно')}")
    
    print(f"\n🎉 GraphUpdater работает! Граф обновляется ✨")


if __name__ == "__main__":
    asyncio.run(test_graph_updater()) 