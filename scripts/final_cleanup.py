#!/usr/bin/env python3
"""
Финальная очистка и анализ дублирования в KittyCore 3.0
"""
import os
import shutil
from pathlib import Path
import ast
from collections import defaultdict

class FinalCleanup:
    def __init__(self):
        self.project_root = Path(".")
        self.duplicates = defaultdict(list)
        
    def analyze_and_cleanup(self):
        """Анализ и финальная очистка"""
        print("🔍 Финальный анализ KittyCore 3.0...")
        
        # 1. Анализируем оставшиеся файлы в корне
        self._analyze_root_files()
        
        # 2. Поиск функционального дублирования
        self._find_functional_duplicates()
        
        # 3. Создаём единую структуру
        self._create_unified_structure()
        
        # 4. Итоговый отчёт
        self._final_report()
        
    def _analyze_root_files(self):
        """Анализирует файлы в корне"""
        print("\n📁 Анализирую файлы в корне...")
        
        root_files = list(self.project_root.glob("*.py"))
        
        categories = {
            "important": [],      # Важные файлы системы
            "utilities": [],      # Утилиты  
            "demos": [],         # Демо файлы
            "misc": []           # Прочее
        }
        
        for file_path in root_files:
            file_size = file_path.stat().st_size
            file_name = file_path.name.lower()
            
            # Категоризация по важности
            if any(keyword in file_name for keyword in ['main', 'app', 'server', 'bot']):
                categories["important"].append((file_path.name, file_size))
            elif any(keyword in file_name for keyword in ['fix_', 'integrate_', 'result', 'validation']):
                categories["important"].append((file_path.name, file_size))
            elif any(keyword in file_name for keyword in ['card', 'media', 'button', 'radio']):
                categories["utilities"].append((file_path.name, file_size))
            elif any(keyword in file_name for keyword in ['kot_', 'model']):
                categories["demos"].append((file_path.name, file_size))
            else:
                categories["misc"].append((file_path.name, file_size))
                
        # Выводим анализ
        for category, files in categories.items():
            if files:
                print(f"\n  📂 {category.upper()} ({len(files)} файлов):")
                for name, size in files:
                    size_kb = round(size / 1024, 1)
                    print(f"    • {name} ({size_kb} KB)")
                    
    def _find_functional_duplicates(self):
        """Ищет функциональное дублирование"""
        print("\n🔍 Ищу функциональное дублирование...")
        
        # Анализируем Python файлы
        all_py_files = []
        
        # Корень
        all_py_files.extend(self.project_root.glob("*.py"))
        
        # Подпапки
        for subdir in ['kittycore', 'agents', 'tools', 'utils', 'cli', 'demos', 'scripts', 'data']:
            subdir_path = Path(subdir)
            if subdir_path.exists():
                all_py_files.extend(subdir_path.rglob("*.py"))
                
        # Группируем по содержимому функций
        function_signatures = defaultdict(list)
        
        for file_path in all_py_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Парсим AST
                tree = ast.parse(content)
                
                # Извлекаем функции и классы
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        signature = f"func_{node.name}_{len(node.args.args)}"
                        function_signatures[signature].append(str(file_path))
                    elif isinstance(node, ast.ClassDef):
                        signature = f"class_{node.name}"
                        function_signatures[signature].append(str(file_path))
                        
            except Exception as e:
                print(f"    ⚠️  Ошибка в {file_path}: {e}")
                
        # Находим дубли
        duplicates_found = 0
        for signature, files in function_signatures.items():
            if len(files) > 1:
                # Исключаем тестовые файлы и __init__.py
                real_files = [f for f in files if not ('test_' in f or '__init__' in f)]
                if len(real_files) > 1:
                    print(f"    🔄 {signature}: {len(real_files)} копий")
                    for file_path in real_files[:3]:  # Показываем первые 3
                        print(f"      • {file_path}")
                    self.duplicates[signature] = real_files
                    duplicates_found += 1
                    
        if duplicates_found == 0:
            print("    ✅ Функциональных дублей не найдено!")
        else:
            print(f"    ⚠️  Найдено {duplicates_found} потенциальных дублей")
            
    def _create_unified_structure(self):
        """Создаёт единую структуру"""
        print("\n🏗️  Создаю единую структуру...")
        
        # Перемещаем оставшиеся файлы
        remaining_moves = {
            "kot_razmer.py": "demos/",
            "card_generator.py": "utils/",
            "cards.py": "utils/", 
            "button.py": "utils/",
            "media_processing.py": "utils/",
            "radio_pi.py": "utils/",
            "model.py": "utils/",
            "synchro_settings.py": "utils/",
            "input_validation.py": "utils/",
            "validation.py": "utils/",
            "telegram_bot.py": "cli/"
        }
        
        moved_count = 0
        for file_name, target_dir in remaining_moves.items():
            file_path = Path(file_name)
            if file_path.exists():
                target_path = Path(target_dir) / file_name
                if not target_path.exists():
                    shutil.move(str(file_path), str(target_path))
                    print(f"    🚚 {file_name} -> {target_dir}")
                    moved_count += 1
                    
        print(f"    ✅ Перемещено {moved_count} файлов")
        
    def _final_report(self):
        """Финальный отчёт"""
        print("\n" + "="*60)
        print("🎯 ФИНАЛЬНЫЙ ОТЧЁТ KITTYCORE 3.0")
        print("="*60)
        
        # Считаем файлы в корне
        root_py_files = list(self.project_root.glob("*.py"))
        print(f"\n📁 Файлов в корне: {len(root_py_files)}")
        
        if root_py_files:
            print("  ВАЖНЫЕ файлы в корне:")
            for file_path in root_py_files:
                size_kb = round(file_path.stat().st_size / 1024, 1)
                print(f"    • {file_path.name} ({size_kb} KB)")
                
        # Структура папок
        print(f"\n📂 Структура проекта:")
        folders = ['kittycore', 'agents', 'tools', 'utils', 'cli', 'demos', 'scripts', 'data']
        for folder in folders:
            folder_path = Path(folder)
            if folder_path.exists():
                py_count = len(list(folder_path.rglob("*.py")))
                print(f"    📁 {folder}/ ({py_count} файлов)")
                
        # Архивы
        archives = list(self.project_root.glob("archive_*"))
        print(f"\n📦 Архивов создано: {len(archives)}")
        
        # Рекомендации
        print(f"\n🎯 РЕКОМЕНДАЦИИ:")
        print(f"  ✅ Проект организован!")
        print(f"  📝 Создать requirements.txt")
        print(f"  📚 Обновить README.md")
        print(f"  🧪 Запустить полное тестирование")
        print(f"  🔄 Проверить работу агентов")
        
        if len(root_py_files) <= 5:
            print(f"  🏆 ОТЛИЧНО! Корень проекта чист!")
        elif len(root_py_files) <= 10:
            print(f"  👍 ХОРОШО! Корень проекта почти чист!")
        else:
            print(f"  ⚠️  ВНИМАНИЕ! Ещё много файлов в корне")

def main():
    """Основная функция"""
    cleanup = FinalCleanup()
    cleanup.analyze_and_cleanup()

if __name__ == "__main__":
    main() 