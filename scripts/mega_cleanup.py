#!/usr/bin/env python3
"""
МЕГА-ОЧИСТКА KittyCore 3.0 - убираем ВСЕ лишние файлы из корня!
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
import re

class MegaCleanup:
    def __init__(self):
        self.project_root = Path(".")
        self.archived_count = 0
        self.moved_count = 0
        
    def mega_cleanup(self):
        """МЕГА-очистка проекта"""
        print("🚀 МЕГА-ОЧИСТКА KITTYCORE 3.0 НАЧАЛАСЬ!")
        print("=" * 60)
        
        # 1. Создаём архив для ВСЕГО мусора
        self._create_mega_archive()
        
        # 2. Архивируем временные файлы
        self._archive_temp_files()
        
        # 3. Архивируем дубли
        self._archive_duplicates()
        
        # 4. Организуем оставшиеся файлы
        self._organize_remaining_files()
        
        # 5. Финальный отчёт
        self._final_mega_report()
        
    def _create_mega_archive(self):
        """Создаёт мега-архив"""
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        self.mega_archive = Path(f"MEGA_ARCHIVE_{timestamp}")
        self.mega_archive.mkdir(exist_ok=True)
        
        # Создаём подпапки в архиве
        (self.mega_archive / "temp_files").mkdir(exist_ok=True)
        (self.mega_archive / "duplicates").mkdir(exist_ok=True)
        (self.mega_archive / "html_files").mkdir(exist_ok=True)
        (self.mega_archive / "text_files").mkdir(exist_ok=True)
        (self.mega_archive / "json_files").mkdir(exist_ok=True)
        (self.mega_archive / "other_files").mkdir(exist_ok=True)
        
        print(f"📦 Создан мега-архив: {self.mega_archive}")
        
    def _archive_temp_files(self):
        """Архивирует все временные файлы"""
        print("\n🗑️  Архивирую временные файлы...")
        
        temp_patterns = [
            "output_*.txt",
            "search_results_*.md", 
            "generated_*",
            "*_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]*",
            "*.tmp",
            "*.temp",
            "temp_*",
        ]
        
        temp_count = 0
        for pattern in temp_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    target = self.mega_archive / "temp_files" / file_path.name
                    shutil.move(str(file_path), str(target))
                    temp_count += 1
                    
        print(f"  ✅ Архивировано {temp_count} временных файлов")
        self.archived_count += temp_count
        
    def _archive_duplicates(self):
        """Архивирует дубли файлов"""
        print("\n🔄 Архивирую дубли...")
        
        # Группы дублей
        duplicate_groups = {
            "prototypes": [
                "prototip*.html", "прототип*.html", "прототип_*.html",
                "prototyp*.html", "прототипы*.html"
            ],
            "reports": [
                "otchet*.html", "отчет*.html", "отчёт*.md", 
                "report*.html", "результат*.html"
            ],
            "analysis": [
                "анализ*.html", "анализ*.txt", "анализ*.md",
                "analysis*.txt", "analyst*.py"
            ],
            "plans": [
                "plan*.html", "план*.txt", "planning*.html"
            ],
            "configs": [
                "config*.html", "config*.js", "config*.json",
                "settings*.html", "server_config*"
            ],
            "cards": [
                "card*.html", "карточки*.html", "cards*.html"
            ]
        }
        
        duplicate_count = 0
        for group_name, patterns in duplicate_groups.items():
            group_dir = self.mega_archive / "duplicates" / group_name
            group_dir.mkdir(exist_ok=True)
            
            for pattern in patterns:
                for file_path in self.project_root.glob(pattern):
                    if file_path.is_file():
                        target = group_dir / file_path.name
                        # Если файл уже есть, добавляем номер
                        counter = 1
                        while target.exists():
                            name_parts = file_path.stem, counter, file_path.suffix
                            target = group_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                            counter += 1
                            
                        shutil.move(str(file_path), str(target))
                        duplicate_count += 1
                        
        print(f"  ✅ Архивировано {duplicate_count} дублей")
        self.archived_count += duplicate_count
        
    def _organize_remaining_files(self):
        """Организует оставшиеся файлы"""
        print("\n📁 Организую оставшиеся файлы...")
        
        # Создаём папки если их нет
        folders_to_create = [
            "docs/html", "docs/markdown", "docs/text",
            "data/json", "data/csv", "data/xlsx", 
            "media/images", "media/videos",
            "configs", "examples"
        ]
        
        for folder in folders_to_create:
            Path(folder).mkdir(parents=True, exist_ok=True)
            
        # Правила организации
        organization_rules = {
            # Документация
            "docs/html": ["*.html"],
            "docs/markdown": ["*.md"],
            "docs/text": ["*.txt"],
            
            # Данные
            "data/json": ["*.json"],
            "data/csv": ["*.csv"],
            "data/xlsx": ["*.xlsx"],
            
            # Медиа
            "media/images": ["*.png", "*.jpg", "*.jpeg", "*.gif"],
            "media/videos": ["*.mp4", "*.avi", "*.mov"],
            
            # Конфигурации
            "configs": ["*.conf", "*.cfg", "nginx.conf"],
            
            # Примеры
            "examples": ["*.ipynb", "example_*", "demo_*"]
        }
        
        moved_count = 0
        for target_folder, patterns in organization_rules.items():
            for pattern in patterns:
                for file_path in self.project_root.glob(pattern):
                    if file_path.is_file() and file_path.parent == self.project_root:
                        target_path = Path(target_folder) / file_path.name
                        
                        # Проверяем коллизии
                        if target_path.exists():
                            counter = 1
                            while target_path.exists():
                                name_parts = file_path.stem, counter, file_path.suffix
                                target_path = Path(target_folder) / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                                counter += 1
                                
                        shutil.move(str(file_path), str(target_path))
                        moved_count += 1
                        
        print(f"  ✅ Перемещено {moved_count} файлов")
        self.moved_count += moved_count
        
        # Архивируем оставшиеся файлы (кроме важных)
        important_files = {
            "main.py", "README.md", "requirements.txt", 
            ".env", ".gitignore", "docker-compose.yml", "Dockerfile"
        }
        
        remaining_count = 0
        for file_path in self.project_root.glob("*"):
            if (file_path.is_file() and 
                file_path.name not in important_files and
                not file_path.name.startswith('.') and
                file_path.suffix not in ['.py']):
                
                # Определяем тип файла для архива
                if file_path.suffix == '.html':
                    target_dir = self.mega_archive / "html_files"
                elif file_path.suffix in ['.txt', '.md']:
                    target_dir = self.mega_archive / "text_files"
                elif file_path.suffix == '.json':
                    target_dir = self.mega_archive / "json_files"
                else:
                    target_dir = self.mega_archive / "other_files"
                    
                target = target_dir / file_path.name
                counter = 1
                while target.exists():
                    name_parts = file_path.stem, counter, file_path.suffix
                    target = target_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                    counter += 1
                    
                shutil.move(str(file_path), str(target))
                remaining_count += 1
                
        print(f"  ✅ Архивировано {remaining_count} оставшихся файлов")
        self.archived_count += remaining_count
        
    def _final_mega_report(self):
        """Финальный мега-отчёт"""
        print("\n" + "="*70)
        print("🎯 МЕГА-ОТЧЁТ KITTYCORE 3.0")
        print("="*70)
        
        # Считаем что осталось в корне
        root_files = []
        for file_path in self.project_root.glob("*"):
            if file_path.is_file():
                root_files.append(file_path.name)
                
        print(f"\n📦 АРХИВИРОВАНО: {self.archived_count} файлов")
        print(f"🚚 ПЕРЕМЕЩЕНО: {self.moved_count} файлов")
        print(f"📁 ОСТАЛОСЬ В КОРНЕ: {len(root_files)} файлов")
        
        if root_files:
            print("\n  📋 Файлы в корне:")
            for file_name in sorted(root_files)[:10]:
                print(f"    • {file_name}")
            if len(root_files) > 10:
                print(f"    ... и ещё {len(root_files) - 10} файлов")
                
        # Структура проекта
        print(f"\n📂 НОВАЯ СТРУКТУРА:")
        important_dirs = [
            'kittycore', 'agents', 'tools', 'utils', 'cli', 
            'demos', 'scripts', 'data', 'docs', 'media', 'configs'
        ]
        
        for dir_name in important_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                file_count = len(list(dir_path.rglob("*")))
                print(f"    📁 {dir_name}/ ({file_count} файлов)")
                
        print(f"\n🎉 РЕЗУЛЬТАТ:")
        if len(root_files) <= 10:
            print(f"  🏆 ОТЛИЧНО! Корень проекта ЧИСТ!")
        elif len(root_files) <= 20:
            print(f"  👍 ХОРОШО! Корень почти чист!")
        else:
            print(f"  ⚠️  Ещё есть работа...")
            
        print(f"\n📦 Архив создан: {self.mega_archive}")
        print(f"🔄 Можно восстановить любые файлы из архива")
        print(f"✅ МЕГА-ОЧИСТКА ЗАВЕРШЕНА!")

def main():
    """Основная функция"""
    cleanup = MegaCleanup()
    
    print("🤔 Начать МЕГА-ОЧИСТКУ KittyCore 3.0?")
    print("⚠️  ЭТО ПЕРЕМЕСТИТ СОТНИ ФАЙЛОВ В АРХИВ!")
    response = input("Продолжить? (y/N): ")
    
    if response.lower() in ['y', 'yes', 'да']:
        cleanup.mega_cleanup()
    else:
        print("❌ Мега-очистка отменена")

if __name__ == "__main__":
    main() 