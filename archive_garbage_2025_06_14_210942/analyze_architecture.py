#!/usr/bin/env python3
"""
Анализ архитектуры KittyCore 3.0 и поиск дублирующегося функционала
"""
import os
import re
import ast
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple

class ArchitectureAnalyzer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.components = defaultdict(list)
        self.duplicates = defaultdict(list)
        self.imports = defaultdict(set)
        self.classes = defaultdict(list)
        self.functions = defaultdict(list)
        self.files_analyzed = []
        
    def analyze_project(self):
        """Анализирует весь проект"""
        print("🔍 Анализирую архитектуру KittyCore 3.0...")
        
        # Анализируем Python файлы
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not any(
            exclude in str(f) for exclude in [
                "__pycache__", ".venv", "venv", "archive_", 
                "node_modules", ".git"
            ]
        )]
        
        print(f"📊 Найдено {len(python_files)} Python файлов для анализа")
        
        for file_path in python_files:
            self._analyze_python_file(file_path)
            
        # Генерируем отчёт
        self._generate_report()
        
    def _analyze_python_file(self, file_path: Path):
        """Анализирует один Python файл"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.files_analyzed.append(file_path)
            
            # Парсим AST
            try:
                tree = ast.parse(content)
                self._extract_ast_info(tree, file_path)
            except SyntaxError:
                print(f"⚠️  Синтаксическая ошибка в {file_path}")
                
            # Анализируем импорты вручную (на случай проблем с AST)
            self._extract_imports_manual(content, file_path)
            
            # Классифицируем файл по архитектуре
            self._classify_file(file_path, content)
            
        except Exception as e:
            print(f"❌ Ошибка анализа {file_path}: {e}")
            
    def _extract_ast_info(self, tree: ast.AST, file_path: Path):
        """Извлекает информацию из AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self.classes[node.name].append(file_path)
            elif isinstance(node, ast.FunctionDef):
                self.functions[node.name].append(file_path)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                self._extract_import_from_node(node, file_path)
                
    def _extract_import_from_node(self, node: ast.AST, file_path: Path):
        """Извлекает импорт из AST узла"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                self.imports[file_path].add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                full_import = f"{module}.{alias.name}" if module else alias.name
                self.imports[file_path].add(full_import)
                
    def _extract_imports_manual(self, content: str, file_path: Path):
        """Извлекает импорты вручную через регулярные выражения"""
        import_patterns = [
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',
            r'^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    self.imports[file_path].add(match.group(1))
                    
    def _classify_file(self, file_path: Path, content: str):
        """Классифицирует файл по архитектурным компонентам"""
        relative_path = file_path.relative_to(self.project_root)
        path_str = str(relative_path)
        
        # Классификация по пути
        if "core/" in path_str:
            self.components["Core Components"].append(relative_path)
        elif "agents/" in path_str:
            self.components["Agent System"].append(relative_path)
        elif "tools/" in path_str:
            self.components["Tool System"].append(relative_path)
        elif "memory/" in path_str:
            self.components["Memory System"].append(relative_path)
        elif "llm/" in path_str:
            self.components["LLM Integration"].append(relative_path)
        elif "visualization/" in path_str:
            self.components["Visualization"].append(relative_path)
        elif "config/" in path_str:
            self.components["Configuration"].append(relative_path)
        elif "tests/" in path_str:
            self.components["Tests"].append(relative_path)
        elif "obsidian" in path_str:
            self.components["Obsidian Integration"].append(relative_path)
        elif "web/" in path_str:
            self.components["Web Interface"].append(relative_path)
        elif "browser" in path_str:
            self.components["Browser Tools"].append(relative_path)
        else:
            self.components["Root Level / Other"].append(relative_path)
            
        # Классификация по содержимому
        content_lower = content.lower()
        
        if "orchestrator" in content_lower:
            self.components["Orchestration Logic"].append(relative_path)
        if "agent" in content_lower and "class" in content_lower:
            self.components["Agent Classes"].append(relative_path)
        if "memory" in content_lower and ("store" in content_lower or "save" in content_lower):
            self.components["Memory Implementation"].append(relative_path)
        if "llm" in content_lower and ("openai" in content_lower or "anthropic" in content_lower):
            self.components["LLM Providers"].append(relative_path)
            
    def _find_duplicates(self):
        """Находит дублирующийся функционал"""
        print("\n🔍 Ищу дублирующийся функционал...")
        
        # Дублирующиеся классы
        for class_name, files in self.classes.items():
            if len(files) > 1:
                self.duplicates[f"Class: {class_name}"].extend(files)
                
        # Дублирующиеся функции (только важные)
        important_functions = [
            "execute", "run", "process", "create", "generate", "analyze",
            "orchestrate", "initialize", "setup", "configure", "validate"
        ]
        
        for func_name, files in self.functions.items():
            if len(files) > 1 and any(keyword in func_name.lower() for keyword in important_functions):
                self.duplicates[f"Function: {func_name}"].extend(files)
                
        # Похожие названия файлов
        file_names = defaultdict(list)
        for file_path in self.files_analyzed:
            name = file_path.stem.lower()
            # Нормализуем названия
            name = re.sub(r'[_-]', '', name)
            file_names[name].append(file_path)
            
        for name, files in file_names.items():
            if len(files) > 1:
                self.duplicates[f"Similar files: {name}"].extend(files)
                
    def _generate_report(self):
        """Генерирует отчёт об архитектуре"""
        self._find_duplicates()
        
        print("\n" + "="*80)
        print("📊 ОТЧЁТ ОБ АРХИТЕКТУРЕ KITTYCORE 3.0")
        print("="*80)
        
        # Общая статистика
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"  • Всего Python файлов: {len(self.files_analyzed)}")
        print(f"  • Всего классов: {len(self.classes)}")
        print(f"  • Всего функций: {len(self.functions)}")
        print(f"  • Архитектурных компонентов: {len(self.components)}")
        
        # Архитектурные компоненты
        print(f"\n🏗️  АРХИТЕКТУРНЫЕ КОМПОНЕНТЫ:")
        for component, files in sorted(self.components.items()):
            if files:  # Показываем только непустые компоненты
                print(f"\n  📦 {component} ({len(files)} файлов):")
                for file_path in sorted(files)[:5]:  # Показываем первые 5
                    print(f"    • {file_path}")
                if len(files) > 5:
                    print(f"    ... и ещё {len(files) - 5} файлов")
                    
        # Дублирование
        if self.duplicates:
            print(f"\n🚨 ОБНАРУЖЕНО ДУБЛИРОВАНИЕ:")
            for duplicate_type, files in self.duplicates.items():
                print(f"\n  ⚠️  {duplicate_type}:")
                for file_path in sorted(set(files)):
                    rel_path = file_path.relative_to(self.project_root) if hasattr(file_path, 'relative_to') else file_path
                    print(f"    • {rel_path}")
        else:
            print(f"\n✅ Критичных дублирований не обнаружено!")
            
        # Топ импортов
        print(f"\n📦 ТОП ИМПОРТИРУЕМЫХ МОДУЛЕЙ:")
        all_imports = []
        for imports in self.imports.values():
            all_imports.extend(imports)
        import_counter = Counter(all_imports)
        
        for module, count in import_counter.most_common(10):
            if count > 2:  # Показываем только популярные
                print(f"  • {module}: {count} раз")
                
        # Рекомендации
        self._generate_recommendations()
        
    def _generate_recommendations(self):
        """Генерирует рекомендации по улучшению архитектуры"""
        print(f"\n💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
        
        recommendations = []
        
        # Анализируем дублирование
        if len(self.duplicates) > 5:
            recommendations.append("🔄 Слишком много дублирования - нужна рефакторизация")
            
        # Анализируем распределение файлов
        root_files = len(self.components.get("Root Level / Other", []))
        if root_files > 10:
            recommendations.append(f"📁 {root_files} файлов в корне - переместить в подпапки")
            
        # Анализируем тесты
        test_files = len(self.components.get("Tests", []))
        total_files = len(self.files_analyzed)
        if test_files < total_files * 0.3:
            recommendations.append(f"🧪 Мало тестов ({test_files}/{total_files}) - добавить покрытие")
            
        # Анализируем размеры компонентов
        for component, files in self.components.items():
            if len(files) > 20:
                recommendations.append(f"📦 {component} слишком большой ({len(files)} файлов) - разделить")
                
        # Анализируем классы с одинаковыми именами
        duplicate_classes = sum(1 for files in self.classes.values() if len(files) > 1)
        if duplicate_classes > 3:
            recommendations.append(f"🏷️  {duplicate_classes} дублирующихся классов - переименовать")
            
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("  ✅ Архитектура выглядит хорошо!")
            
        # Специфичные рекомендации для KittyCore
        print(f"\n🎯 СПЕЦИФИЧНЫЕ РЕКОМЕНДАЦИИ ДЛЯ KITTYCORE 3.0:")
        print("  1. ✅ Создать единый файл-мэппер всех агентов")
        print("  2. ✅ Объединить все tool системы в unified_tools.py") 
        print("  3. ✅ Создать единый конфиг для всех LLM провайдеров")
        print("  4. ✅ Мигрировать все CLI скрипты в kittycore/cli/")
        print("  5. ✅ Объединить все системы памяти в single_memory.py")

def main():
    """Основная функция"""
    analyzer = ArchitectureAnalyzer()
    analyzer.analyze_project()
    
    # Создаём детальный отчёт в файл
    print(f"\n💾 Создаю детальный отчёт...")
    
    report_path = Path("ARCHITECTURE_ANALYSIS.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Анализ архитектуры KittyCore 3.0\n\n")
        f.write(f"Дата анализа: {Path().cwd()}\n")
        f.write(f"Всего файлов: {len(analyzer.files_analyzed)}\n\n")
        
        f.write("## Архитектурные компоненты\n\n")
        for component, files in sorted(analyzer.components.items()):
            if files:
                f.write(f"### {component} ({len(files)} файлов)\n\n")
                for file_path in sorted(files):
                    f.write(f"- `{file_path}`\n")
                f.write("\n")
                
        if analyzer.duplicates:
            f.write("## Обнаруженное дублирование\n\n")
            for duplicate_type, files in analyzer.duplicates.items():
                f.write(f"### {duplicate_type}\n\n")
                for file_path in sorted(set(files)):
                    rel_path = file_path.relative_to(analyzer.project_root) if hasattr(file_path, 'relative_to') else file_path
                    f.write(f"- `{rel_path}`\n")
                f.write("\n")
                
    print(f"📄 Детальный отчёт сохранён в: {report_path}")

if __name__ == "__main__":
    main() 