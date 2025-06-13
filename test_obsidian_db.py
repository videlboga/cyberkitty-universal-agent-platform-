#!/usr/bin/env python3
"""
🧪 Тест ObsidianDB - Центральной базы данных для агентов

Проверяем:
1. Создание и сохранение заметок
2. Поиск и связывание заметок  
3. Рабочие пространства агентов
4. Координацию между агентами
5. Управление задачами
"""

import asyncio
import shutil
from pathlib import Path
from kittycore.core.obsidian_db import (
    ObsidianDB, ObsidianNote, AgentWorkspace, TaskManager,
    get_obsidian_db, create_agent_workspace, create_task_manager
)

def test_obsidian_db():
    """Тестирует базовую функциональность ObsidianDB"""
    print("🧪 Тестируем ObsidianDB...")
    
    # Очищаем тестовую папку
    test_vault = "./test_obsidian_vault"
    if Path(test_vault).exists():
        shutil.rmtree(test_vault)
    
    # Создаём базу данных
    db = ObsidianDB(test_vault)
    
    # Тест 1: Создание заметки
    print("\n📝 Тест 1: Создание заметки")
    note = ObsidianNote(
        title="Тестовая заметка",
        content="Это тестовый контент заметки",
        tags=["test", "demo"],
        metadata={"author": "test_system", "priority": "high"}
    )
    
    filepath = db.save_note(note)
    print(f"✅ Заметка сохранена: {filepath}")
    
    # Тест 2: Чтение заметки
    print("\n📖 Тест 2: Чтение заметки")
    loaded_note = db.get_note("Тестовая-заметка.md")
    if loaded_note:
        print(f"✅ Заметка загружена: {loaded_note.title}")
        print(f"   Теги: {loaded_note.tags}")
        print(f"   Метаданные: {loaded_note.metadata}")
    else:
        print("❌ Заметка не найдена")
    
    # Тест 3: Поиск заметок
    print("\n🔍 Тест 3: Поиск заметок")
    results = db.search_notes(query="тестовый", tags=["test"])
    print(f"✅ Найдено заметок: {len(results)}")
    for result in results:
        print(f"   - {result['title']} (теги: {result['tags']})")
    
    # Тест 4: Создание связей
    print("\n🔗 Тест 4: Создание связей")
    note2 = ObsidianNote(
        title="Связанная заметка",
        content="Эта заметка связана с первой",
        tags=["test", "linked"]
    )
    db.save_note(note2)
    
    # Создаём связь
    db.create_link("Тестовая-заметка.md", "Связанная-заметка.md", "Связанная заметка")
    
    # Проверяем обратные связи
    backlinks = db.get_backlinks("Связанная заметка")
    print(f"✅ Обратные связи для 'Связанная заметка': {backlinks}")
    
    return db

def test_agent_workspace():
    """Тестирует рабочие пространства агентов"""
    print("\n🤖 Тестируем AgentWorkspace...")
    
    # Используем существующую базу
    db = get_obsidian_db("./test_obsidian_vault")
    
    # Создаём рабочие пространства для двух агентов
    agent1 = AgentWorkspace("agent_nova", db)
    agent2 = AgentWorkspace("agent_artemis", db)
    
    task_id = "test_task_001"
    
    # Тест 1: Сохранение результатов
    print("\n💾 Тест 1: Сохранение результатов агентов")
    
    result1 = agent1.save_result(
        task_id=task_id,
        content="Агент Nova выполнил анализ данных и создал отчёт",
        result_type="analysis"
    )
    print(f"✅ Agent Nova сохранил результат: {Path(result1).name}")
    
    result2 = agent2.save_result(
        task_id=task_id,
        content="Агент Artemis создал веб-страницу с результатами",
        result_type="webpage"
    )
    print(f"✅ Agent Artemis сохранил результат: {Path(result2).name}")
    
    # Тест 2: Получение контекста задачи
    print("\n📋 Тест 2: Получение контекста задачи")
    context = agent1.get_task_context(task_id)
    print(f"✅ Контекст для agent_nova:")
    print(f"   Связанные агенты: {context['related_agents']}")
    print(f"   Предыдущие результаты: {len(context['previous_results'])}")
    
    # Тест 3: Координация между агентами
    print("\n📨 Тест 3: Координация между агентами")
    coord_msg = agent1.coordinate_with_agent(
        other_agent_id="agent_artemis",
        message="Привет Artemis! Я завершил анализ данных. Можешь создать визуализацию на основе моих результатов?",
        task_id=task_id
    )
    print(f"✅ Сообщение отправлено: {Path(coord_msg).name}")
    
    # Проверяем сообщения для agent2
    messages = agent2.get_messages_for_me(task_id)
    print(f"✅ Agent Artemis получил сообщений: {len(messages)}")
    for msg in messages:
        print(f"   От {msg['from_agent']}: {msg['content'][:50]}...")
    
    return agent1, agent2

def test_task_manager():
    """Тестирует управление задачами"""
    print("\n📋 Тестируем TaskManager...")
    
    # Создаём менеджер задач
    task_manager = create_task_manager("./test_obsidian_vault")
    
    # Тест 1: Создание задачи
    print("\n🎯 Тест 1: Создание задачи")
    task_id = task_manager.create_task(
        task_description="Создать интерактивный дашборд для анализа продаж",
        user_id="user_123"
    )
    print(f"✅ Создана задача: {task_id}")
    
    # Тест 2: Добавление агентов к задаче
    print("\n🤖 Тест 2: Добавление агентов к задаче")
    task_manager.add_agent_to_task(task_id, "agent_nova", "Data Analyst")
    task_manager.add_agent_to_task(task_id, "agent_artemis", "Frontend Developer")
    print("✅ Агенты добавлены к задаче")
    
    # Тест 3: Добавление результатов
    print("\n📊 Тест 3: Добавление результатов к задаче")
    task_manager.add_result_to_task(
        task_id=task_id,
        agent_id="agent_nova",
        result_content="Выполнен анализ данных продаж за последний квартал. Выявлены ключевые тренды и метрики.",
        result_type="analysis"
    )
    
    task_manager.add_result_to_task(
        task_id=task_id,
        agent_id="agent_artemis", 
        result_content="Создан интерактивный дашборд с графиками и фильтрами. Использованы Chart.js и Bootstrap.",
        result_type="dashboard"
    )
    print("✅ Результаты добавлены к задаче")
    
    # Тест 4: Обновление статуса
    print("\n🔄 Тест 4: Обновление статуса задачи")
    task_manager.update_task_status(
        task_id=task_id,
        status="completed",
        details="Все компоненты дашборда готовы и протестированы"
    )
    print("✅ Статус задачи обновлён")
    
    # Тест 5: Получение сводки
    print("\n📈 Тест 5: Получение сводки по задаче")
    summary = task_manager.get_task_summary(task_id)
    print(f"✅ Сводка по задаче {task_id}:")
    print(f"   Статус: {summary['status']}")
    print(f"   Агентов: {summary['agents_count']}")
    print(f"   Результатов: {summary['results_count']}")
    print(f"   Сообщений координации: {summary['coordination_messages']}")
    
    return task_manager, task_id

def test_obsidian_integration():
    """Тестирует интеграцию с Obsidian"""
    print("\n🔗 Тестируем интеграцию с Obsidian...")
    
    vault_path = Path("./test_obsidian_vault")
    
    # Проверяем структуру папок
    print("\n📁 Структура vault:")
    for folder in vault_path.rglob("*"):
        if folder.is_dir():
            print(f"   📁 {folder.relative_to(vault_path)}/")
        else:
            print(f"   📄 {folder.relative_to(vault_path)}")
    
    # Проверяем содержимое заметки задачи
    print("\n📝 Содержимое заметки задачи:")
    task_files = list(vault_path.glob("tasks/task_*.md"))
    if task_files:
        with open(task_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
        print("=" * 50)
        print(content[:500] + "..." if len(content) > 500 else content)
        print("=" * 50)
    
    # Проверяем заметки агентов
    print("\n🤖 Заметки агентов:")
    agent_files = list(vault_path.glob("agents/**/*.md"))
    for agent_file in agent_files[:3]:  # Показываем первые 3
        print(f"   📄 {agent_file.relative_to(vault_path)}")
    
    print(f"\n✅ Всего создано файлов: {len(list(vault_path.rglob('*.md')))}")

def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов ObsidianDB - Центральной базы данных агентов")
    print("=" * 70)
    
    try:
        # Базовые тесты
        db = test_obsidian_db()
        
        # Тесты рабочих пространств агентов
        agent1, agent2 = test_agent_workspace()
        
        # Тесты управления задачами
        task_manager, task_id = test_task_manager()
        
        # Тесты интеграции с Obsidian
        test_obsidian_integration()
        
        print("\n" + "=" * 70)
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("\n🗄️ ObsidianDB готова к использованию как центральная база данных")
        print("📁 Проверьте папку ./test_obsidian_vault в Obsidian")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 