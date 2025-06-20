#!/usr/bin/env python3
"""
Анализатор дублирования функционала в KittyCore 3.0
Ищет дубли классов, функций и логики на уровне кода
"""
import os
import ast
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Any
import difflib

class CodeDuplicateAnalyzer:
    def __init__(self):
        self.project_root = Path(".")
        self.duplicates = defaultdict(list)
        self.class_signatures = defaultdict(list)
        self.function_signatures = defaultdict(list)
        self.code_blocks = defaultdict(list)
        self.import_patterns = defaultdict(list)
        
    def analyze_duplicates(self):
        """Основной анализ дублирования"""
        print("🔍 АНАЛИЗ ДУБЛИРОВАНИЯ ФУНКЦИОНАЛА KITTYCORE 3.0")
        print("=" * 60)
        
        # 1. Собираем все Python файлы
        python_files = self._collect_python_files()
        print(f"📁 Найдено {len(python_files)} Python файлов для анализа")
        
        # 2. Анализируем каждый файл
        for file_path in python_files:
            self._analyze_file(file_path)
            
        # 3. Ищем дубли
        self._find_class_duplicates()
        self._find_function_duplicates()
        self._find_code_block_duplicates()
        self._find_import_duplicates()
        
        # 4. Генерируем отчёт
        self._generate_report()
        
    def _collect_python_files(self):
        """Собирает все Python файлы проекта"""
        python_files = []
        
        # Основные директории для анализа
        dirs_to_analyze = [
            "kittycore", "utils", "cli", "demos", "scripts", 
            "data", "agents", "tools"
        ]
        
        for dir_name in dirs_to_analyze:
            dir_path = Path(dir_name)
            if dir_path.exists():
                python_files.extend(dir_path.rglob("*.py"))
                
        # Добавляем файлы из корня
        python_files.extend(self.project_root.glob("*.py"))
        
        # Фильтруем системные файлы
        filtered_files = []
        for file_path in python_files:
            if not any(skip in str(file_path) for skip in [
                "__pycache__", ".venv", "venv", ".git", 
                "test_", "_test", "archive_"
            ]):
                filtered_files.append(file_path)
                
        return filtered_files
        
    def _analyze_file(self, file_path: Path):
        """Анализирует один файл"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Парсим AST
            tree = ast.parse(content)
            
            # Анализируем импорты
            self._extract_imports(tree, file_path)
            
            # Анализируем классы и функции
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._extract_class_signature(node, file_path)
                elif isinstance(node, ast.FunctionDef):
                    self._extract_function_signature(node, file_path)
                    
            # Анализируем блоки кода
            self._extract_code_blocks(content, file_path)
            
        except Exception as e:
            print(f"    ⚠️  Ошибка в {file_path}: {e}")
            
    def _extract_imports(self, tree: ast.AST, file_path: Path):
        """Извлекает паттерны импортов"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"from {module} import {alias.name}")
                    
        if imports:
            import_signature = "|".join(sorted(imports))
            self.import_patterns[import_signature].append(str(file_path))
            
    def _extract_class_signature(self, node: ast.ClassDef, file_path: Path):
        """Извлекает сигнатуру класса"""
        # Базовые классы
        bases = [self._get_node_name(base) for base in node.bases]
        
        # Методы класса
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                args = [arg.arg for arg in item.args.args]
                methods.append(f"{item.name}({','.join(args)})")
                
        # Атрибуты класса
        attributes = []
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
                        
        signature = {
            'name': node.name,
            'bases': bases,
            'methods': sorted(methods),
            'attributes': sorted(attributes),
            'method_count': len(methods),
            'file': str(file_path)
        }
        
        # Создаём ключ для поиска дублей
        key = f"{node.name}|{len(methods)}|{len(attributes)}"
        self.class_signatures[key].append(signature)
        
    def _extract_function_signature(self, node: ast.FunctionDef, file_path: Path):
        """Извлекает сигнатуру функции"""
        # Аргументы функции
        args = [arg.arg for arg in node.args.args]
        
        # Возвращаемые значения (если есть аннотации)
        returns = self._get_node_name(node.returns) if node.returns else None
        
        # Вызовы функций внутри
        function_calls = []
        for item in ast.walk(node):
            if isinstance(item, ast.Call):
                func_name = self._get_node_name(item.func)
                if func_name:
                    function_calls.append(func_name)
                    
        signature = {
            'name': node.name,
            'args': args,
            'arg_count': len(args),
            'returns': returns,
            'calls': sorted(set(function_calls)),
            'call_count': len(set(function_calls)),
            'file': str(file_path)
        }
        
        # Создаём ключ для поиска дублей
        key = f"{node.name}|{len(args)}"
        self.function_signatures[key].append(signature)
        
    def _extract_code_blocks(self, content: str, file_path: Path):
        """Извлекает блоки кода для поиска дублей"""
        lines = content.split('\n')
        
        # Ищем блоки кода (функции, классы)
        current_block = []
        block_type = None
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
                
            # Определяем начало блока
            if stripped.startswith(('def ', 'class ', 'async def ')):
                if current_block and len(current_block) > 3:
                    block_hash = hashlib.md5('\n'.join(current_block).encode()).hexdigest()
                    self.code_blocks[block_hash].append({
                        'file': str(file_path),
                        'type': block_type,
                        'lines': len(current_block),
                        'content': '\n'.join(current_block[:5])  # Первые 5 строк
                    })
                    
                current_block = [stripped]
                block_type = 'function' if 'def ' in stripped else 'class'
                indent_level = len(line) - len(line.lstrip())
            else:
                if current_block:
                    current_block.append(stripped)
                    
        # Последний блок
        if current_block and len(current_block) > 3:
            block_hash = hashlib.md5('\n'.join(current_block).encode()).hexdigest()
            self.code_blocks[block_hash].append({
                'file': str(file_path),
                'type': block_type,
                'lines': len(current_block),
                'content': '\n'.join(current_block[:5])
            })
            
    def _get_node_name(self, node):
        """Получает имя узла AST"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return None
        
    def _find_class_duplicates(self):
        """Ищет дублирующиеся классы"""
        print("\n🔍 Анализирую дублирование классов...")
        
        class_duplicates = 0
        for key, signatures in self.class_signatures.items():
            if len(signatures) > 1:
                # Проверяем реальное сходство
                similar_classes = self._find_similar_classes(signatures)
                if len(similar_classes) > 1:
                    class_duplicates += 1
                    print(f"\n  🔄 Дублирующиеся классы '{signatures[0]['name']}':")
                    for sig in similar_classes:
                        print(f"    • {sig['file']} ({sig['method_count']} методов)")
                        
        if class_duplicates == 0:
            print("    ✅ Дублирующихся классов не найдено")
        else:
            print(f"    ⚠️  Найдено {class_duplicates} групп дублирующихся классов")
            
    def _find_function_duplicates(self):
        """Ищет дублирующиеся функции"""
        print("\n🔍 Анализирую дублирование функций...")
        
        function_duplicates = 0
        for key, signatures in self.function_signatures.items():
            if len(signatures) > 1:
                # Группируем по схожести
                similar_functions = self._find_similar_functions(signatures)
                if len(similar_functions) > 1:
                    function_duplicates += 1
                    print(f"\n  🔄 Дублирующиеся функции '{signatures[0]['name']}':")
                    for sig in similar_functions:
                        calls_info = f", вызывает {sig['call_count']} функций" if sig['call_count'] > 0 else ""
                        print(f"    • {sig['file']} ({sig['arg_count']} аргументов{calls_info})")
                        
        if function_duplicates == 0:
            print("    ✅ Дублирующихся функций не найдено")
        else:
            print(f"    ⚠️  Найдено {function_duplicates} групп дублирующихся функций")
            
    def _find_code_block_duplicates(self):
        """Ищет дублирующиеся блоки кода"""
        print("\n🔍 Анализирую дублирование блоков кода...")
        
        block_duplicates = 0
        for block_hash, blocks in self.code_blocks.items():
            if len(blocks) > 1:
                block_duplicates += 1
                print(f"\n  🔄 Идентичные блоки кода ({blocks[0]['lines']} строк):")
                for block in blocks:
                    print(f"    • {block['file']} ({block['type']})")
                    
        if block_duplicates == 0:
            print("    ✅ Идентичных блоков кода не найдено")
        else:
            print(f"    ⚠️  Найдено {block_duplicates} групп идентичных блоков")
            
    def _find_import_duplicates(self):
        """Ищет дублирующиеся паттерны импортов"""
        print("\n🔍 Анализирую паттерны импортов...")
        
        import_duplicates = 0
        for import_sig, files in self.import_patterns.items():
            if len(files) > 1:
                import_count = len(import_sig.split('|'))
                if import_count > 3:  # Только значимые паттерны
                    import_duplicates += 1
                    print(f"\n  🔄 Одинаковые импорты ({import_count} импортов):")
                    for file_path in files:
                        print(f"    • {file_path}")
                        
        if import_duplicates == 0:
            print("    ✅ Значимых дублей импортов не найдено")
        else:
            print(f"    ⚠️  Найдено {import_duplicates} групп одинаковых импортов")
            
    def _find_similar_classes(self, signatures: List[Dict]) -> List[Dict]:
        """Находит действительно похожие классы"""
        similar = []
        for sig in signatures:
            # Исключаем тестовые файлы и backup
            if not any(skip in sig['file'] for skip in ['test_', 'backup_', 'archive_']):
                similar.append(sig)
        return similar
        
    def _find_similar_functions(self, signatures: List[Dict]) -> List[Dict]:
        """Находит действительно похожие функции"""
        similar = []
        for sig in signatures:
            # Исключаем тестовые файлы, backup и системные функции
            if (not any(skip in sig['file'] for skip in ['test_', 'backup_', 'archive_']) and
                sig['name'] not in ['__init__', '__str__', '__repr__', 'main']):
                similar.append(sig)
        return similar
        
    def _generate_report(self):
        """Генерирует итоговый отчёт"""
        print("\n" + "="*70)
        print("📊 ОТЧЁТ О ДУБЛИРОВАНИИ ФУНКЦИОНАЛА")
        print("="*70)
        
        # Статистика
        total_classes = sum(len(sigs) for sigs in self.class_signatures.values())
        total_functions = sum(len(sigs) for sigs in self.function_signatures.values())
        total_blocks = sum(len(blocks) for blocks in self.code_blocks.values())
        
        print(f"\n📈 СТАТИСТИКА:")
        print(f"  • Классов проанализировано: {total_classes}")
        print(f"  • Функций проанализировано: {total_functions}")
        print(f"  • Блоков кода проанализировано: {total_blocks}")
        
        # Рекомендации
        print(f"\n🎯 РЕКОМЕНДАЦИИ:")
        
        duplicate_classes = sum(1 for sigs in self.class_signatures.values() 
                              if len(self._find_similar_classes(sigs)) > 1)
        duplicate_functions = sum(1 for sigs in self.function_signatures.values() 
                                if len(self._find_similar_functions(sigs)) > 1)
        duplicate_blocks = sum(1 for blocks in self.code_blocks.values() if len(blocks) > 1)
        
        if duplicate_classes == 0 and duplicate_functions == 0 and duplicate_blocks == 0:
            print("  🏆 ОТЛИЧНО! Значимого дублирования функционала не найдено!")
            print("  ✅ Код хорошо организован и не содержит дублей")
        else:
            if duplicate_classes > 0:
                print(f"  🔄 Объединить {duplicate_classes} групп дублирующихся классов")
            if duplicate_functions > 0:
                print(f"  🔄 Рефакторить {duplicate_functions} групп дублирующихся функций")
            if duplicate_blocks > 0:
                print(f"  🔄 Вынести {duplicate_blocks} общих блоков в утилиты")
                
        print(f"\n✅ Анализ дублирования завершён!")

def main():
    """Основная функция"""
    analyzer = CodeDuplicateAnalyzer()
    analyzer.analyze_duplicates()

if __name__ == "__main__":
    main() 