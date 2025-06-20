#!/usr/bin/env python3
"""
Скрипт для очистки временных файлов в проекте KittyCore 3.0
"""
import os
import glob
import re
from pathlib import Path

def find_temp_files():
    """Находит все временные файлы в проекте"""
    temp_patterns = [
        # Файлы с временными именами
        "generated_*.html",
        "файл_*.txt", 
        "файл_*.html",
        "*_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9].*",
        
        # Пустые или почти пустые файлы
        "*.html",  # Проверим размер
        "*.txt",   # Проверим размер
        "*.js",    # Проверим размер
        "*.css",   # Проверим размер
        "*.json",  # Проверим размер
        "*.py",    # Проверим размер
        "*.csv",   # Проверим размер
        "*.pdf",   # Проверим размер
        "*.md",    # Проверим размер
        
        # Тестовые файлы в корне (не в папке tests)
        "test_*.py",
        "demo_*.py",
        "check_*.py",
        
        # Медиа файлы
        "*.mp4",
        "*.avi",
        "*.mkv",
        
        # Временные конфигурационные файлы
        "config.html",
        "config.txt",
        "config.js",
        "demodata.json",
        "plan.json",
        "plan.txt",
        "results.txt",
        
        # Пустые файлы без расширения
        "*"  # Проверим размер
    ]
    
    temp_files = []
    project_root = Path(".")
    
    for pattern in temp_patterns:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                # Пропускаем важные файлы
                if should_keep_file(file_path):
                    continue
                    
                # Проверяем размер для потенциально пустых файлов
                if is_temp_by_size_or_content(file_path):
                    temp_files.append(file_path)
    
    return temp_files

def should_keep_file(file_path: Path) -> bool:
    """Проверяет, нужно ли сохранить файл"""
    keep_patterns = [
        # Основные файлы проекта
        "__init__.py",
        "setup.py", 
        "requirements.txt",
        "README.md",
        "LICENSE",
        
        # Конфигурационные файлы
        "pyproject.toml",
        "setup.cfg",
        
        # Git файлы
        ".gitignore",
        ".gitattributes"
    ]
    
    # Основные директории проекта
    keep_dirs = [
        "kittycore/",
        "agents/",
        ".git/",
        "__pycache__/",
        "obsidian-kittycore-plugin/",
        "obsidian_vault/",
        "archive_2025_01_07/"
    ]
    
    # Проверяем имя файла
    if file_path.name in keep_patterns:
        return True
        
    # Проверяем, находится ли файл в важной директории
    for keep_dir in keep_dirs:
        if str(file_path).startswith(keep_dir):
            return True
            
    return False

def is_temp_by_size_or_content(file_path: Path) -> bool:
    """Проверяет, является ли файл временным по размеру или содержимому"""
    try:
        size = file_path.stat().st_size
        
        # Пустые или очень маленькие файлы
        if size == 0:
            return True
        if size < 50 and file_path.suffix in ['.html', '.txt', '.js', '.css']:
            return True
            
        # Проверяем содержимое для подозрительных файлов
        if size < 1000:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Файлы с подозрительным содержимым
                temp_indicators = [
                    "generated_",
                    "файл_", 
                    "test result",
                    "temporary",
                    "temp file",
                    "placeholder"
                ]
                
                content_lower = content.lower()
                for indicator in temp_indicators:
                    if indicator in content_lower:
                        return True
                        
            except Exception:
                pass
                
        # Файлы по именам/паттернам
        name = file_path.name
        if re.match(r'generated_\d+', name):
            return True
        if re.match(r'файл_\d+', name):
            return True
        if name.startswith('test_') and not str(file_path).startswith('kittycore/tests/'):
            return True
        if name.startswith('demo_') and file_path.suffix == '.py':
            return True
            
    except Exception:
        pass
        
    return False

def main():
    """Основная функция очистки"""
    print("🧹 Начинаю очистку временных файлов KittyCore 3.0...")
    
    temp_files = find_temp_files()
    
    if not temp_files:
        print("✅ Временные файлы не найдены!")
        return
        
    print(f"\n📋 Найдено {len(temp_files)} временных файлов:")
    
    # Группируем по типам
    by_type = {}
    total_size = 0
    
    for file_path in temp_files:
        file_type = file_path.suffix or "без расширения"
        if file_type not in by_type:
            by_type[file_type] = []
        by_type[file_type].append(file_path)
        
        try:
            total_size += file_path.stat().st_size
        except:
            pass
    
    # Показываем статистику
    for file_type, files in sorted(by_type.items()):
        print(f"  {file_type}: {len(files)} файлов")
        
    print(f"\n💾 Общий размер: {total_size:,} байт ({total_size/1024:.1f} KB)")
    
    # Спрашиваем подтверждение
    response = input(f"\n❓ Удалить все {len(temp_files)} временных файлов? (y/N): ")
    
    if response.lower() in ['y', 'yes', 'да']:
        deleted_count = 0
        for file_path in temp_files:
            try:
                file_path.unlink()
                deleted_count += 1
                print(f"🗑️  Удалён: {file_path}")
            except Exception as e:
                print(f"❌ Ошибка удаления {file_path}: {e}")
                
        print(f"\n✅ Удалено {deleted_count} из {len(temp_files)} файлов")
        print(f"💾 Освобождено ~{total_size/1024:.1f} KB дискового пространства")
    else:
        print("❌ Очистка отменена")

if __name__ == "__main__":
    main() 