#!/usr/bin/env python3
"""
Анализ архитектуры ТОЛЬКО KittyCore 3.0 (без зависимостей)
"""
import os
import re
import ast
from pathlib import Path
from collections import defaultdict, Counter

class KittyCoreAnalyzer:
    def __init__(self):
        self.project_root = Path(".")
        self.components = defaultdict(list)
        self.duplicates = defaultdict(list)
        self.files_by_category = defaultdict(list)
        
    def analyze_project(self):
        """Анализирует проект KittyCore"""
        print("🐱 Анализирую архитектуру KittyCore 3.0...")
        
        # Находим только наши Python файлы
        python_files = []
        for file_path in self.project_root.rglob("*.py"):
            if self._is_our_file(file_path):
                python_files.append(file_path)
                
        print(f"📊 Найдено {len(python_files)} наших Python файлов")
        
        # Анализируем каждый файл
        for file_path in python_files:
            self._analyze_file(file_path)
            
        # Генерируем отчёт
        self._generate_report()
        
    def _is_our_file(self, file_path: Path) -> bool:
        """Проверяет, является ли файл нашим"""
        path_str = str(file_path)
        
        # Исключаем зависимости и временные файлы
        exclude_patterns = [
            ".venv/", "venv/", "telegram_test_env/", ".git/", 
            "node_modules/", "__pycache__/", "archive_",
            ".pytest_cache/", ".mypy_cache/"
        ]
        
        for pattern in exclude_patterns:
            if pattern in path_str:
                return False
                
        return True
        
    def _analyze_file(self, file_path: Path):
        """Анализирует один файл"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Категоризируем файл
            self._categorize_file(file_path, content)
            
        except Exception as e:
            print(f"❌ Ошибка анализа {file_path}: {e}")
            
    def _categorize_file(self, file_path: Path, content: str):
        """Категоризирует файл по функционалу"""
        relative_path = file_path.relative_to(self.project_root)
        path_str = str(relative_path)
        content_lower = content.lower()
        file_name = file_path.name.lower()
        
        # Основные компоненты KittyCore
        if path_str.startswith("kittycore/core/"):
            self.components["🧠 Core Engine"].append(relative_path)
        elif path_str.startswith("kittycore/agents/"):
            self.components["🤖 Agent System"].append(relative_path)
        elif path_str.startswith("kittycore/tools/"):
            self.components["🔧 Tool System"].append(relative_path)
        elif path_str.startswith("kittycore/memory/"):
            self.components["💾 Memory System"].append(relative_path)
        elif path_str.startswith("kittycore/llm/"):
            self.components["🧠 LLM Integration"].append(relative_path)
        elif path_str.startswith("kittycore/visualization/"):
            self.components["📊 Visualization"].append(relative_path)
        elif path_str.startswith("kittycore/config/"):
            self.components["⚙️ Configuration"].append(relative_path)
        elif path_str.startswith("kittycore/tests/"):
            self.components["🧪 Tests"].append(relative_path)
        elif "obsidian" in path_str:
            self.components["📝 Obsidian Integration"].append(relative_path)
        elif path_str.startswith("kittycore/"):
            self.components["🏠 KittyCore Root"].append(relative_path)
            
        # Бенчмарки и примеры
        elif path_str.startswith("benchmarks/"):
            self.components["📈 Benchmarks"].append(relative_path)
        elif path_str.startswith("examples/"):
            self.components["📚 Examples"].append(relative_path)
            
        # Временные и тестовые файлы в корне
        elif any(word in file_name for word in ["test_", "demo_", "check_"]):
            self.components["🧪 Root Tests/Demos"].append(relative_path)
        elif "generated_" in file_name:
            self.components["🔄 Generated Files"].append(relative_path)
        elif any(word in file_name for word in ["temp_", "tmp_", "archive_"]):
            self.components["📁 Temp Files"].append(relative_path)
            
        # Утилиты и скрипты
        elif any(word in file_name for word in ["script", "skrip", "calculation", "calculator"]):
            self.components["📝 Utility Scripts"].append(relative_path)
        elif any(word in file_name for word in ["server", "app", "main", "start"]):
            self.components["🚀 Application Entry Points"].append(relative_path)
        elif any(word in file_name for word in ["bot", "telegram"]):
            self.components["🤖 Bot Scripts"].append(relative_path)
        elif file_name.endswith("data.py") or "анализ" in file_name:
            self.components["📊 Data Analysis"].append(relative_path)
            
        # Остальные файлы в корне
        elif relative_path.parent == Path("."):
            self.components["📁 Root Level Files"].append(relative_path)
        else:
            self.components["❓ Other"].append(relative_path)
            
        # Поиск дублирующихся паттернов
        self._find_duplicates_by_name(file_path)
        
    def _find_duplicates_by_name(self, file_path: Path):
        """Ищет дублирующиеся имена файлов"""
        name = file_path.stem.lower()
        
        # Нормализуем название
        normalized_name = re.sub(r'[_\-\d]', '', name)
        
        if len(normalized_name) > 3:  # Игнорируем слишком короткие
            self.files_by_category[normalized_name].append(file_path)
            
    def _generate_report(self):
        """Генерирует отчёт"""
        print("\n" + "="*60)
        print("📊 АНАЛИЗ АРХИТЕКТУРЫ KITTYCORE 3.0")
        print("="*60)
        
        total_files = sum(len(files) for files in self.components.values())
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"  • Всего файлов проекта: {total_files}")
        
        # Компоненты по важности
        print(f"\n🏗️ АРХИТЕКТУРНЫЕ КОМПОНЕНТЫ:")
        
        # Сортируем компоненты по важности
        priority_order = [
            "🧠 Core Engine", "🤖 Agent System", "🔧 Tool System", 
            "💾 Memory System", "🧠 LLM Integration", "📊 Visualization",
            "⚙️ Configuration", "📝 Obsidian Integration", "🏠 KittyCore Root",
            "🧪 Tests", "📈 Benchmarks", "📚 Examples",
            "🚀 Application Entry Points", "🤖 Bot Scripts", 
            "📊 Data Analysis", "📝 Utility Scripts",
            "🧪 Root Tests/Demos", "📁 Root Level Files",
            "🔄 Generated Files", "📁 Temp Files", "❓ Other"
        ]
        
        for component in priority_order:
            files = self.components.get(component, [])
            if files:
                print(f"\n  {component} ({len(files)} файлов):")
                for file_path in sorted(files)[:5]:
                    print(f"    • {file_path}")
                if len(files) > 5:
                    print(f"    ... и ещё {len(files) - 5} файлов")
                    
        # Поиск дублирования
        print(f"\n🔍 АНАЛИЗ ДУБЛИРОВАНИЯ:")
        
        duplicates_found = False
        for name, files in self.files_by_category.items():
            if len(files) > 1 and len(name) > 4:  # Только значимые дубли
                duplicates_found = True
                print(f"\n  ⚠️ Похожие файлы '{name}':")
                for file_path in sorted(files):
                    print(f"    • {file_path}")
                    
        if not duplicates_found:
            print("  ✅ Значимых дублирований не найдено")
            
        # Рекомендации
        self._generate_recommendations(total_files)
        
    def _generate_recommendations(self, total_files: int):
        """Генерирует рекомендации"""
        print(f"\n💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
        
        recommendations = []
        
        # Анализируем количество файлов в корне
        root_files = len(self.components.get("📁 Root Level Files", []))
        if root_files > 10:
            recommendations.append(f"📁 {root_files} файлов в корне - организовать в папки")
            
        # Анализируем тестовые файлы в корне
        root_tests = len(self.components.get("🧪 Root Tests/Demos", []))
        if root_tests > 5:
            recommendations.append(f"🧪 {root_tests} тестов в корне - переместить в tests/")
            
        # Анализируем сгенерированные файлы
        generated = len(self.components.get("🔄 Generated Files", []))
        if generated > 0:
            recommendations.append(f"🔄 {generated} сгенерированных файлов - очистить")
            
        # Анализируем временные файлы
        temp_files = len(self.components.get("📁 Temp Files", []))
        if temp_files > 0:
            recommendations.append(f"📁 {temp_files} временных файлов - удалить")
            
        # Анализируем утилиты
        utilities = len(self.components.get("📝 Utility Scripts", []))
        if utilities > 8:
            recommendations.append(f"📝 {utilities} утилит в корне - создать utils/")
            
        # Анализируем основные компоненты
        core_files = len(self.components.get("🧠 Core Engine", []))
        if core_files == 0:
            recommendations.append("🧠 Нет файлов в Core Engine - создать основу")
            
        agent_files = len(self.components.get("🤖 Agent System", []))
        if agent_files < 3:
            recommendations.append("🤖 Мало файлов в Agent System - развить систему")
            
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("  ✅ Архитектура выглядит хорошо!")
            
        # План действий
        print(f"\n🎯 ПЛАН ДЕЙСТВИЙ:")
        print("  1. 🧹 Очистить корень от временных файлов")
        print("  2. 📁 Создать структуру папок (utils/, cli/, demos/)")
        print("  3. 🚚 Переместить файлы в соответствующие папки")
        print("  4. 🔄 Объединить дублирующийся функционал")
        print("  5. 📝 Создать единый точки входа (main.py)")

def main():
    analyzer = KittyCoreAnalyzer()
    analyzer.analyze_project()

if __name__ == "__main__":
    main() 