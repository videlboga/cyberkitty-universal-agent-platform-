#!/usr/bin/env python3
"""
Умная организация файлов в проекте KittyCore 3.0
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

class KittyCoreOrganizer:
    def __init__(self):
        self.project_root = Path(".")
        self.moved_files = []
        self.archived_files = []
        
    def organize_project(self):
        """Организует весь проект"""
        print("🧹 Начинаю организацию KittyCore 3.0...")
        
        # 1. Создаём архив для мусора
        self._archive_garbage()
        
        # 2. Создаём структуру папок
        self._create_folder_structure()
        
        # 3. Перемещаем файлы по папкам
        self._organize_files()
        
        # 4. Исправляем дублирование
        self._fix_duplicates()
        
        # 5. Отчёт
        self._generate_report()
        
    def _archive_garbage(self):
        """Архивирует мусорные файлы"""
        print("\n📦 Архивирую мусорные файлы...")
        
        # Создаём архивную папку
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        archive_dir = Path(f"archive_garbage_{timestamp}")
        archive_dir.mkdir(exist_ok=True)
        
        # Паттерны мусорных файлов
        garbage_patterns = [
            "generated_script_*.py",
            "cleanup_temp_files.py",
            "analyze_architecture.py", 
            "analyze_kittycore_only.py",
            "archive_temp_files.py"
        ]
        
        garbage_files = []
        for pattern in garbage_patterns:
            garbage_files.extend(self.project_root.glob(pattern))
            
        for file_path in garbage_files:
            if file_path.exists():
                target = archive_dir / file_path.name
                shutil.move(str(file_path), str(target))
                self.archived_files.append(file_path.name)
                print(f"  📦 {file_path.name} -> архив")
                
        print(f"✅ Архивировано {len(self.archived_files)} мусорных файлов")
        
    def _create_folder_structure(self):
        """Создаёт структуру папок"""
        print("\n📁 Создаю структуру папок...")
        
        folders_to_create = [
            "utils",           # Утилиты и скрипты
            "cli",            # CLI интерфейсы  
            "demos",          # Демо и примеры
            "scripts",        # Автоматизация
            "data",           # Файлы данных
            "outputs/temp",   # Временные результаты
            "workspace/temp", # Рабочее пространство
            "docs",           # Документация
        ]
        
        for folder in folders_to_create:
            folder_path = Path(folder)
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"  📁 Создана папка: {folder}")
            
    def _organize_files(self):
        """Организует файлы по папкам"""
        print("\n🚚 Перемещаю файлы по папкам...")
        
        # Правила перемещения файлов
        move_rules = {
            # Утилиты и вычисления
            "utils": [
                "*calculation*.py", "*calculator*.py", "*area*.py", 
                "*factorial*.py", "*sort*.py", "*volume*.py",
                "radius*.py", "*алгоритм*.py", "фактория.py",
                "sphere_volume.py", "quick_sort*.py", "fast_sort*.py"
            ],
            
            # CLI интерфейсы
            "cli": [
                "*_cli*.py", "kittycore_cli*.py", "*server*.py",
                "app.py", "start_web.py", "simple_web_server.py"
            ],
            
            # Демо и тестовые файлы
            "demos": [
                "check_*.py", "hello_world*.py", "intro_to_python.py",
                "real_hello.py", "biblioteka.py", "qr_*.py"
            ],
            
            # Скрипты автоматизации  
            "scripts": [
                "*script*.py", "*skrip*.py", "converter.py",
                "structure.py", "organize_project.py"
            ],
            
            # Файлы данных и анализа
            "data": [
                "*data*.py", "*анализ*.py", "analyst.py", 
                "*analyze*.py", "категории*.py", "результат.py",
                "api_data.py", "crm_data.py"
            ],
        }
        
        # Перемещаем файлы
        for target_folder, patterns in move_rules.items():
            for pattern in patterns:
                for file_path in self.project_root.glob(pattern):
                    if file_path.is_file() and file_path.parent == self.project_root:
                        target_path = Path(target_folder) / file_path.name
                        
                        # Проверяем, нет ли файла с таким именем
                        if target_path.exists():
                            counter = 1
                            while target_path.exists():
                                name_parts = file_path.stem, counter, file_path.suffix
                                target_path = Path(target_folder) / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                                counter += 1
                                
                        shutil.move(str(file_path), str(target_path))
                        self.moved_files.append((file_path.name, target_folder))
                        print(f"  🚚 {file_path.name} -> {target_folder}/")
                        
    def _fix_duplicates(self):
        """Исправляет дублирование файлов"""
        print("\n🔄 Исправляю дублирование...")
        
        # Дублирующиеся агенты
        duplicate_agents = [
            ("agents/base_agent.py", "kittycore/agents/base_agent.py"),
            ("agents/intellectual_agent.py", "kittycore/agents/intellectual_agent.py")
        ]
        
        for old_path, main_path in duplicate_agents:
            old_file = Path(old_path)
            main_file = Path(main_path)
            
            if old_file.exists() and main_file.exists():
                # Проверяем, одинаковые ли файлы
                if old_file.stat().st_size != main_file.stat().st_size:
                    print(f"  ⚠️  {old_path} и {main_path} отличаются!")
                    backup_name = f"backup_{old_file.name}"
                    shutil.move(str(old_file), str(Path("utils") / backup_name))
                    print(f"  🔄 {old_path} -> utils/{backup_name}")
                else:
                    old_file.unlink()
                    print(f"  🗑️  Удалён дубль: {old_path}")
                    
        # Дублирующиеся tools
        duplicate_tools = [
            ("tools/system_tools.py", "kittycore/tools/system_tools.py")
        ]
        
        for old_path, main_path in duplicate_tools:
            old_file = Path(old_path)
            if old_file.exists():
                shutil.move(str(old_file), str(Path("utils") / old_file.name))
                print(f"  🔄 {old_path} -> utils/")
                
    def _generate_report(self):
        """Генерирует отчёт об организации"""
        print("\n" + "="*50)
        print("📊 ОТЧЁТ ОБ ОРГАНИЗАЦИИ KITTYCORE 3.0")
        print("="*50)
        
        print(f"\n📦 Архивировано: {len(self.archived_files)} файлов")
        for file_name in self.archived_files:
            print(f"  • {file_name}")
            
        print(f"\n🚚 Перемещено: {len(self.moved_files)} файлов")
        by_folder = {}
        for file_name, folder in self.moved_files:
            if folder not in by_folder:
                by_folder[folder] = []
            by_folder[folder].append(file_name)
            
        for folder, files in by_folder.items():
            print(f"\n  📁 {folder}/ ({len(files)} файлов):")
            for file_name in files[:3]:
                print(f"    • {file_name}")
            if len(files) > 3:
                print(f"    ... и ещё {len(files) - 3} файлов")
                
        # Проверяем, что осталось в корне
        remaining_files = []
        for file_path in self.project_root.glob("*.py"):
            if file_path.is_file():
                remaining_files.append(file_path.name)
                
        print(f"\n📁 Осталось в корне: {len(remaining_files)} файлов")
        for file_name in remaining_files[:5]:
            print(f"  • {file_name}")
        if len(remaining_files) > 5:
            print(f"  ... и ещё {len(remaining_files) - 5} файлов")
            
        print(f"\n✅ Организация завершена!")
        print(f"🎯 Следующие шаги:")
        print(f"  1. 📝 Создать единый main.py")
        print(f"  2. 📚 Обновить README.md")
        print(f"  3. 🧪 Запустить тесты")

def main():
    """Основная функция"""
    organizer = KittyCoreOrganizer()
    
    print("🤔 Начать организацию проекта KittyCore 3.0?")
    response = input("Это переместит файлы по папкам. Продолжить? (y/N): ")
    
    if response.lower() in ['y', 'yes', 'да']:
        organizer.organize_project()
    else:
        print("❌ Организация отменена")

if __name__ == "__main__":
    main() 