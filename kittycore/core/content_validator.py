"""
ContentValidator - проверяет и исправляет результаты агентов
Решает проблему "отчёты вместо контента"
"""

import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

class ContentValidator:
    """Валидатор контента - проверяет что агенты создали то что просили"""
    
    def __init__(self, outputs_dir: str = "outputs"):
        self.outputs_dir = Path(outputs_dir)
        self.outputs_dir.mkdir(exist_ok=True)
        
    def validate_task_result(self, task_description: str, created_files: List[str]) -> Dict[str, Any]:
        """Проверяет соответствие результата задаче"""
        
        # Анализируем что должно было быть создано
        expected = self._analyze_expected_output(task_description)
        
        # Проверяем что реально создано
        actual = self._analyze_actual_output(created_files)
        
        # Сравниваем и выдаём оценку
        validation_result = self._compare_expected_vs_actual(expected, actual, task_description)
        
        return validation_result
    
    def _analyze_expected_output(self, task_description: str) -> Dict[str, Any]:
        """Анализирует что должно быть создано по описанию задачи"""
        task_lower = task_description.lower()
        
        expected = {
            "file_type": None,
            "filename_pattern": None,
            "content_requirements": [],
            "language": None
        }
        
        # Определяем тип файла
        if "python" in task_lower and "скрипт" in task_lower:
            expected["file_type"] = "python"
            expected["language"] = "python"
            
            if "факториал" in task_lower:
                expected["filename_pattern"] = "factorial.py"
                expected["content_requirements"] = ["def factorial", "return", "if", "main"]
            elif "сортировк" in task_lower and "быстр" in task_lower:
                expected["filename_pattern"] = "quicksort.py"
                expected["content_requirements"] = ["def quicksort", "pivot", "left", "right"]
                
        elif "html" in task_lower or "страниц" in task_lower:
            expected["file_type"] = "html"
            expected["language"] = "html"
            
            if "регистрац" in task_lower or "форм" in task_lower:
                expected["filename_pattern"] = "registration.html"
                expected["content_requirements"] = ["<form", "input", "email", "password"]
                
        elif "json" in task_lower and "конфигурац" in task_lower:
            expected["file_type"] = "json"
            expected["filename_pattern"] = "config.json"
            expected["content_requirements"] = ["port", "host", "logging", "{", "}"]
            
        elif "readme" in task_lower:
            expected["file_type"] = "markdown"
            expected["filename_pattern"] = "README.md"
            expected["content_requirements"] = ["# ", "## ", "установка", "пример", "описание"]
            
        return expected
    
    def _analyze_actual_output(self, created_files: List[str]) -> Dict[str, Any]:
        """Анализирует что реально создано"""
        actual = {
            "files": [],
            "content_found": [],
            "file_types": []
        }
        
        for file_path in created_files:
            if os.path.exists(file_path):
                actual["files"].append(file_path)
                
                # Определяем тип файла
                if file_path.endswith('.py'):
                    actual["file_types"].append("python")
                elif file_path.endswith('.html'):
                    actual["file_types"].append("html")
                elif file_path.endswith('.json'):
                    actual["file_types"].append("json")
                elif file_path.endswith('.md'):
                    actual["file_types"].append("markdown")
                    
                # Читаем содержимое
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        actual["content_found"].extend(self._extract_content_features(content))
                except Exception as e:
                    print(f"❌ Ошибка чтения {file_path}: {e}")
                    
        return actual
    
    def _extract_content_features(self, content: str) -> List[str]:
        """Извлекает ключевые особенности контента"""
        features = []
        
        # Python особенности
        if "def " in content:
            features.append("def")
        if "import " in content:
            features.append("import")
        if "return " in content:
            features.append("return")
        if "factorial" in content.lower():
            features.append("factorial")
        if "quicksort" in content.lower():
            features.append("quicksort")
        if "pivot" in content.lower():
            features.append("pivot")
            
        # HTML особенности
        if "<form" in content:
            features.append("<form")
        if "input" in content:
            features.append("input")
        if "email" in content:
            features.append("email")
        if "password" in content:
            features.append("password")
            
        # JSON особенности
        if "port" in content:
            features.append("port")
        if "host" in content:
            features.append("host")
        if "logging" in content:
            features.append("logging")
        if "{" in content:
            features.append("{")
        if "}" in content:
            features.append("}")
            
        # Markdown особенности
        if "# " in content:
            features.append("# ")
        if "## " in content:
            features.append("## ")
        if "установка" in content.lower():
            features.append("установка")
        if "пример" in content.lower():
            features.append("пример")
        if "описание" in content.lower():
            features.append("описание")
            
        return features
    
    def _compare_expected_vs_actual(self, expected: Dict, actual: Dict, task_description: str) -> Dict[str, Any]:
        """Сравнивает ожидаемое и фактическое"""
        
        score = 0
        max_score = 0
        issues = []
        
        # Проверяем тип файла
        max_score += 20
        if expected["file_type"] in actual["file_types"]:
            score += 20
        else:
            issues.append(f"Неправильный тип файла. Ожидался: {expected['file_type']}, найдены: {actual['file_types']}")
            
        # Проверяем имя файла
        max_score += 30
        if expected["filename_pattern"]:
            found_correct_name = any(expected["filename_pattern"] in f for f in actual["files"])
            if found_correct_name:
                score += 30
            else:
                issues.append(f"Неправильное имя файла. Ожидалось: {expected['filename_pattern']}, найдены: {actual['files']}")
                
        # Проверяем содержимое
        max_score += 50
        content_score = 0
        for requirement in expected["content_requirements"]:
            if requirement in actual["content_found"]:
                content_score += 10
            else:
                issues.append(f"Отсутствует обязательный контент: {requirement}")
                
        score += min(content_score, 50)
        
        # Вычисляем процент
        percentage = (score / max_score * 100) if max_score > 0 else 0
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
            "passed": percentage >= 70,
            "issues": issues,
            "expected": expected,
            "actual": actual,
            "task_description": task_description
        }
    
    def fix_content_issues(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Исправляет найденные проблемы с контентом"""
        
        if validation_result["passed"]:
            return {"status": "no_fix_needed", "message": "Контент корректный"}
            
        expected = validation_result["expected"]
        task_description = validation_result["task_description"]
        
        # Создаём правильный файл
        if expected["filename_pattern"]:
            correct_content = self._generate_correct_content(expected, task_description)
            
            if correct_content:
                file_path = self.outputs_dir / expected["filename_pattern"]
                
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(correct_content)
                        
                    return {
                        "status": "fixed",
                        "message": f"Создан правильный файл: {file_path}",
                        "file_path": str(file_path),
                        "content_length": len(correct_content)
                    }
                except Exception as e:
                    return {"status": "error", "message": f"Ошибка создания файла: {e}"}
                    
        return {"status": "cannot_fix", "message": "Не удалось определить как исправить"}
    
    def _generate_correct_content(self, expected: Dict, task_description: str) -> Optional[str]:
        """Генерирует правильный контент для файла"""
        
        if expected["filename_pattern"] == "factorial.py":
            return '''def factorial(n):
    """Вычисляет факториал числа n"""
    if n < 0:
        return None  # Факториал не определен для отрицательных чисел
    elif n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

def main():
    try:
        num = int(input("Введите число для вычисления факториала: "))
        if num < 0:
            print("Ошибка: Факториал не определен для отрицательных чисел")
        else:
            result = factorial(num)
            print(f"Факториал {num} = {result}")
    except ValueError:
        print("Ошибка: Пожалуйста, введите корректное целое число")

if __name__ == "__main__":
    main()'''
    
        elif expected["filename_pattern"] == "quicksort.py":
            return '''def quicksort(arr):
    """Быстрая сортировка массива"""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

def main():
    # Пример использования
    test_array = [64, 34, 25, 12, 22, 11, 90]
    print(f"Исходный массив: {test_array}")
    
    sorted_array = quicksort(test_array.copy())
    print(f"Отсортированный массив: {sorted_array}")
    
    # Интерактивный ввод
    try:
        user_input = input("Введите числа через пробел: ")
        user_array = [int(x) for x in user_input.split()]
        sorted_user = quicksort(user_array)
        print(f"Ваш отсортированный массив: {sorted_user}")
    except ValueError:
        print("Ошибка: Введите корректные числа через пробел")

if __name__ == "__main__":
    main()'''
    
        elif expected["filename_pattern"] == "README.md":
            return '''# Калькулятор

Простой калькулятор для математических вычислений.

## Описание

Этот проект представляет собой калькулятор с базовой функциональностью для выполнения арифметических операций.

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/username/calculator.git
   cd calculator
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Использование

### Пример 1: Базовые операции
```python
from calculator import Calculator

calc = Calculator()
result = calc.add(5, 3)
print(f"5 + 3 = {result}")
```

### Пример 2: Сложные вычисления
```python
result = calc.multiply(calc.add(2, 3), 4)
print(f"(2 + 3) * 4 = {result}")
```

## Функции

- ✅ Сложение
- ✅ Вычитание  
- ✅ Умножение
- ✅ Деление
- ✅ Возведение в степень

## Требования

- Python 3.7+
- NumPy (для сложных вычислений)

## Лицензия

MIT License
'''
        
        return None 