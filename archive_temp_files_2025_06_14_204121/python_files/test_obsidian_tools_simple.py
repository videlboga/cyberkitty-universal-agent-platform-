#!/usr/bin/env python3
"""
🧪 ПРОСТОЙ ТЕСТ OBSIDIAN ИНСТРУМЕНТОВ
Проверяем что ObsidianAware инструменты работают
"""

import sys
from pathlib import Path

# Добавляем путь к kittycore
sys.path.insert(0, str(Path(__file__).parent))

from kittycore.tools.obsidian_tools import ObsidianAwareCodeGenerator, ObsidianAwareFileManager
from kittycore.core.obsidian_db import ObsidianDB


def test_obsidian_tools():
    """Тестируем ObsidianAware инструменты"""
    print("🧪 ТЕСТ OBSIDIAN ИНСТРУМЕНТОВ")
    print("=" * 50)
    
    # 1. Создаём ObsidianDB
    print("1️⃣ Создаём ObsidianDB...")
    obsidian_db = ObsidianDB()
    
    # 2. Создаём инструменты
    print("2️⃣ Создаём инструменты...")
    agent_id = "test_agent_001"
    
    code_gen = ObsidianAwareCodeGenerator(obsidian_db, agent_id)
    file_mgr = ObsidianAwareFileManager(obsidian_db, agent_id)
    
    print(f"   ✅ CodeGenerator: {code_gen.name}")
    print(f"   ✅ FileManager: {file_mgr.name}")
    
    # 3. Тестируем создание кода
    print("3️⃣ Тестируем создание кода...")
    result = code_gen.execute(
        filename="test_hello.py",
        content='print("Hello from ObsidianAware tool!")',
        language="python",
        title="Тестовый скрипт"
    )
    
    print(f"   Результат: {result.success}")
    if result.success:
        print(f"   Файл: {result.data['file_path']}")
        print(f"   Размер: {result.data['content_size']} символов")
        print(f"   Сохранён в Obsidian: {result.data['saved_to_obsidian']}")
    else:
        print(f"   ❌ Ошибка: {result.error}")
    
    # 4. Тестируем файловый менеджер
    print("4️⃣ Тестируем файловый менеджер...")
    result2 = file_mgr.execute(
        action="create",
        filename="test_data.txt",
        content="Тестовые данные от ObsidianAware FileManager"
    )
    
    print(f"   Результат: {result2.success}")
    if result2.success:
        print(f"   Файл: {result2.data['file_path']}")
        print(f"   Залогировано в Obsidian: {result2.data['logged_to_obsidian']}")
    else:
        print(f"   ❌ Ошибка: {result2.error}")
    
    # 5. Проверяем что файлы реально созданы
    print("5️⃣ Проверяем реальные файлы...")
    
    outputs_dir = Path("outputs")
    if outputs_dir.exists():
        files = list(outputs_dir.glob("*"))
        print(f"   📁 Найдено файлов в outputs/: {len(files)}")
        for f in files[-3:]:  # Последние 3 файла
            print(f"      - {f.name} ({f.stat().st_size} байт)")
    else:
        print("   ❌ Папка outputs/ не найдена")
    
    # 6. Проверяем ObsidianDB
    print("6️⃣ Проверяем ObsidianDB...")
    try:
        vault_path = obsidian_db.vault_path
        if vault_path.exists():
            agent_folder = vault_path / "agents" / agent_id
            if agent_folder.exists():
                notes = list(agent_folder.rglob("*.md"))
                print(f"   📝 Найдено заметок агента: {len(notes)}")
                for note in notes[-2:]:  # Последние 2 заметки
                    print(f"      - {note.name}")
            else:
                print(f"   ⚠️ Папка агента не найдена: {agent_folder}")
        else:
            print(f"   ⚠️ Vault не найден: {vault_path}")
    except Exception as e:
        print(f"   ❌ Ошибка проверки vault: {e}")
    
    print("\n🎯 ИТОГ:")
    print(f"   ✅ Инструменты созданы")
    print(f"   ✅ Код генерируется: {result.success}")
    print(f"   ✅ Файлы создаются: {result2.success}")
    print(f"   📊 Интеграция с Obsidian: частично работает")


if __name__ == "__main__":
    test_obsidian_tools() 