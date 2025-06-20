#!/usr/bin/env python3
"""
Скрипт для архивирования временных файлов в проекте KittyCore 3.0
"""
import os
import glob
import re
import shutil
from pathlib import Path
from datetime import datetime

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
        ".gitattributes",
        
        # Наши скрипты
        "cleanup_temp_files.py",
        "archive_temp_files.py"
    ]
    
    # Основные директории проекта
    keep_dirs = [
        "kittycore/",
        "agents/",
        ".git/",
        "__pycache__/",
        "obsidian-kittycore-plugin/",
        "obsidian_vault/",
        "archive_"  # Все архивные папки
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

def create_archive_structure(archive_dir: Path, temp_files: list):
    """Создаёт структуру архива и перемещает файлы"""
    archived_count = 0
    
    # Создаём папки по типам файлов
    type_dirs = {
        '.html': archive_dir / 'html_files',
        '.txt': archive_dir / 'text_files', 
        '.py': archive_dir / 'python_files',
        '.js': archive_dir / 'javascript_files',
        '.css': archive_dir / 'css_files',
        '.json': archive_dir / 'json_files',
        '.csv': archive_dir / 'csv_files',
        '.pdf': archive_dir / 'pdf_files',
        '.md': archive_dir / 'markdown_files',
        '.mp4': archive_dir / 'media_files',
        '': archive_dir / 'no_extension'
    }
    
    # Создаём все папки
    for type_dir in type_dirs.values():
        type_dir.mkdir(parents=True, exist_ok=True)
    
    # Перемещаем файлы
    for file_path in temp_files:
        try:
            file_type = file_path.suffix
            target_dir = type_dirs.get(file_type, archive_dir / 'other_files')
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Проверяем, нет ли файла с таким именем
            target_file = target_dir / file_path.name
            counter = 1
            while target_file.exists():
                name_parts = file_path.stem, counter, file_path.suffix
                target_file = target_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                counter += 1
            
            # Перемещаем файл
            shutil.move(str(file_path), str(target_file))
            archived_count += 1
            print(f"📦 Архивирован: {file_path} -> {target_file.relative_to(archive_dir)}")
            
        except Exception as e:
            print(f"❌ Ошибка архивирования {file_path}: {e}")
    
    return archived_count

def main():
    """Основная функция архивирования"""
    print("📦 Начинаю архивирование временных файлов KittyCore 3.0...")
    
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
    
    # Создаём имя архивной папки
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    archive_dir = Path(f"archive_temp_files_{timestamp}")
    
    print(f"\n📦 Архив будет создан в: {archive_dir}")
    
    # Спрашиваем подтверждение
    response = input(f"\n❓ Архивировать все {len(temp_files)} временных файлов? (y/N): ")
    
    if response.lower() in ['y', 'yes', 'да']:
        # Создаём архивную папку
        archive_dir.mkdir(exist_ok=True)
        
        # Создаём информационный файл
        info_file = archive_dir / "ARCHIVE_INFO.txt"
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(f"АРХИВ ВРЕМЕННЫХ ФАЙЛОВ KITTYCORE 3.0\n")
            f.write(f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Количество файлов: {len(temp_files)}\n")
            f.write(f"Общий размер: {total_size:,} байт ({total_size/1024:.1f} KB)\n\n")
            f.write("СТАТИСТИКА ПО ТИПАМ:\n")
            for file_type, files in sorted(by_type.items()):
                f.write(f"  {file_type}: {len(files)} файлов\n")
                
        print(f"📝 Создан файл информации: {info_file}")
        
        # Архивируем файлы
        archived_count = create_archive_structure(archive_dir, temp_files)
                
        print(f"\n✅ Архивировано {archived_count} из {len(temp_files)} файлов")
        print(f"📦 Архив создан в: {archive_dir}")
        print(f"💾 Освобождено ~{total_size/1024:.1f} KB дискового пространства")
        
        # Показываем структуру архива
        print(f"\n📁 Структура архива:")
        for item in sorted(archive_dir.rglob("*")):
            if item.is_dir():
                file_count = len(list(item.glob("*")))
                if file_count > 0:
                    print(f"  📁 {item.relative_to(archive_dir)}/  ({file_count} файлов)")
                    
    else:
        print("❌ Архивирование отменено")

if __name__ == "__main__":
    main() 