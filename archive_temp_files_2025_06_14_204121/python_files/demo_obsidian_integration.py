#!/usr/bin/env python3
"""
Демонстрация интеграции KittyCore 3.0 с Obsidian
"""

import asyncio
import os
from pathlib import Path
from kittycore.obsidian_integration import ObsidianAdapter, ObsidianConfig


async def demo_obsidian_integration():
    """Демонстрация возможностей интеграции с Obsidian"""
    
    print("🚀 Демонстрация KittyCore 3.0 + Obsidian Integration")
    print("=" * 50)
    
    # Настройка vault (используем временную папку для демо)
    demo_vault = Path("./demo_vault")
    
    config = ObsidianConfig(
        vault_path=str(demo_vault),
        notes_folder="KittyCore",
        auto_link=True,
        execute_code=True
    )
    
    # Инициализация адаптера
    adapter = ObsidianAdapter(config)
    
    print(f"📁 Создан демо-vault: {demo_vault}")
    
    # 1. Создание заметки агента
    print("\n1️⃣ Создание заметки агента Nova...")
    
    agent_data = {
        "description": "Специалист по анализу данных и машинному обучению",
        "type": "analytical",
        "capabilities": ["data_analysis", "machine_learning", "visualization"],
        "tasks_completed": 15,
        "success_rate": 92.3
    }
    
    nova_note = await adapter.create_agent_note("Nova", agent_data)
    print(f"✅ Создана заметка агента: {nova_note}")
    
    # 2. Создание заметки задачи
    print("\n2️⃣ Создание заметки задачи...")
    
    task_data = {
        "title": "Анализ пользовательского поведения",
        "description": "Анализ логов пользователей для выявления паттернов",
        "status": "in_progress",
        "priority": "high",
        "assigned_agents": ["Nova"],
        "type": "analysis",
        "code": """
import pandas as pd
import matplotlib.pyplot as plt

# Загрузка данных
data = pd.read_csv('user_logs.csv')
print(f"Загружено {len(data)} записей")

# Анализ активности по часам
hourly_activity = data.groupby('hour').size()
print("Активность по часам:")
print(hourly_activity)

# Визуализация
plt.figure(figsize=(10, 6))
hourly_activity.plot(kind='bar')
plt.title('Активность пользователей по часам')
plt.show()
"""
    }
    
    task_note = await adapter.create_task_note("TASK-001", task_data)
    print(f"✅ Создана заметка задачи: {task_note}")
    
    # 3. Создание заметки результата
    print("\n3️⃣ Создание заметки результата...")
    
    result_data = {
        "title": "Результаты анализа пользовательского поведения",
        "description": "Обнаружены пики активности в 9:00 и 18:00",
        "status": "completed",
        "success": True,
        "quality_score": 8.5,
        "execution_time": "00:05:23",
        "output": """Загружено 10000 записей
Активность по часам:
9    1200
12   800
15   900
18   1500
21   600""",
        "files": ["user_activity_chart.png"],
        "reviewed_by": "Artemis-Agent",
        "review_status": "approved"
    }
    
    result_note = await adapter.create_result_note("TASK-001", "Nova", result_data)
    print(f"✅ Создана заметка результата: {result_note}")
    
    # 4. Создание итогового отчёта
    print("\n4️⃣ Создание итогового отчёта...")
    
    report_data = {
        "title": "Отчёт по анализу пользовательского поведения",
        "summary": "Успешно выявлены паттерны активности пользователей",
        "overall_success": True,
        "overall_quality": 8.5,
        "execution_time": "00:05:23",
        "agents": [
            {"name": "Nova", "tasks_completed": 1, "success_rate": 100}
        ],
        "conclusions": "Рекомендуется увеличить серверные мощности в часы пик"
    }
    
    report_note = await adapter.create_report_note("TASK-001", report_data)
    print(f"✅ Создан итоговый отчёт: {report_note}")
    
    # 5. Получение данных графа
    print("\n5️⃣ Получение данных графа связей...")
    
    graph_data = await adapter.get_graph_data()
    nodes_count = len(graph_data.get("nodes", []))
    edges_count = len(graph_data.get("edges", []))
    
    print(f"📊 Граф содержит {nodes_count} узлов и {edges_count} связей")
    
    # 6. Демонстрация структуры vault
    print("\n6️⃣ Структура созданного vault:")
    print_directory_tree(demo_vault)
    
    print("\n🎉 Демонстрация завершена!")
    print(f"📂 Все файлы сохранены в: {demo_vault}")
    print("💡 Откройте папку в Obsidian чтобы увидеть граф связей!")


def print_directory_tree(path: Path, prefix: str = ""):
    """Печать дерева директорий"""
    if not path.exists():
        return
        
    items = sorted(path.iterdir())
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item.name}")
        
        if item.is_dir():
            extension = "    " if is_last else "│   "
            print_directory_tree(item, prefix + extension)


if __name__ == "__main__":
    asyncio.run(demo_obsidian_integration()) 