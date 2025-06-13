#!/usr/bin/env python3
"""
🌍 РЕАЛЬНЫЕ ТЕСТЫ KITTYCORE 3.0
Проверяем систему на реальных практических задачах
"""

import sys
import asyncio
from pathlib import Path
import time

# Добавляем путь к kittycore
sys.path.insert(0, str(Path(__file__).parent))

from kittycore.core.obsidian_orchestrator import solve_with_obsidian_orchestrator


class RealWorldTester:
    """Тестер реальных сценариев"""
    
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
    
    async def run_test(self, name: str, task: str, expected_files: list, expected_content: list):
        """Запускает один реальный тест"""
        print(f"\n🧪 ТЕСТ: {name}")
        print("=" * 60)
        print(f"📋 Задача: {task}")
        print()
        
        start_time = time.time()
        
        try:
            # Выполняем задачу
            result = await solve_with_obsidian_orchestrator(task)
            
            duration = time.time() - start_time
            
            print(f"✅ Статус: {result['status']}")
            print(f"⏱️ Время: {duration:.2f}с")
            print(f"🤖 Агентов: {result['agents_created']}")
            
            # Проверяем результаты
            score = self._evaluate_results(expected_files, expected_content)
            
            test_result = {
                "name": name,
                "task": task,
                "status": result['status'],
                "duration": duration,
                "agents": result['agents_created'],
                "score": score,
                "passed": score >= 0.7  # 70% для прохождения
            }
            
            self.results.append(test_result)
            self.total_tests += 1
            if test_result["passed"]:
                self.passed_tests += 1
            
            print(f"🏆 ОЦЕНКА: {score*100:.0f}% ({'✅ ПРОШЁЛ' if test_result['passed'] else '❌ ПРОВАЛ'})")
            
            return test_result
            
        except Exception as e:
            print(f"❌ ОШИБКА: {e}")
            
            test_result = {
                "name": name,
                "task": task,
                "status": "error",
                "duration": time.time() - start_time,
                "agents": 0,
                "score": 0.0,
                "passed": False,
                "error": str(e)
            }
            
            self.results.append(test_result)
            self.total_tests += 1
            
            return test_result
    
    def _evaluate_results(self, expected_files: list, expected_content: list) -> float:
        """Оценивает результаты теста"""
        print("📊 ПРОВЕРКА РЕЗУЛЬТАТОВ:")
        
        outputs_dir = Path("outputs")
        score = 0.0
        max_score = len(expected_files) + len(expected_content)
        
        # Проверяем файлы
        for expected_file in expected_files:
            file_path = outputs_dir / expected_file
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"   ✅ {expected_file} ({size} байт)")
                score += 1
            else:
                print(f"   ❌ {expected_file} - НЕ НАЙДЕН")
        
        # Проверяем содержимое
        for content_check in expected_content:
            found = False
            for file_path in outputs_dir.glob("*"):
                if file_path.is_file():
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        if content_check.lower() in content.lower():
                            print(f"   ✅ Найден контент: '{content_check}' в {file_path.name}")
                            found = True
                            break
                    except:
                        continue
            
            if found:
                score += 1
            else:
                print(f"   ❌ НЕ найден контент: '{content_check}'")
        
        return score / max_score if max_score > 0 else 0.0
    
    def print_summary(self):
        """Выводит итоговую сводку"""
        print("\n" + "="*80)
        print("🎯 ИТОГОВАЯ СВОДКА РЕАЛЬНЫХ ТЕСТОВ")
        print("="*80)
        
        print(f"📊 Всего тестов: {self.total_tests}")
        print(f"✅ Прошло: {self.passed_tests}")
        print(f"❌ Провалено: {self.total_tests - self.passed_tests}")
        print(f"🏆 Успешность: {self.passed_tests/self.total_tests*100:.1f}%")
        print()
        
        # Детали по каждому тесту
        for i, result in enumerate(self.results, 1):
            status_icon = "✅" if result["passed"] else "❌"
            print(f"{i}. {status_icon} {result['name']}")
            print(f"   📊 Оценка: {result['score']*100:.0f}%")
            print(f"   ⏱️ Время: {result['duration']:.1f}с")
            print(f"   🤖 Агентов: {result['agents']}")
            if "error" in result:
                print(f"   ❌ Ошибка: {result['error']}")
            print()
        
        # Общая оценка системы
        avg_score = sum(r["score"] for r in self.results) / len(self.results) if self.results else 0
        avg_time = sum(r["duration"] for r in self.results) / len(self.results) if self.results else 0
        
        print("🎯 ОБЩАЯ ОЦЕНКА СИСТЕМЫ:")
        print(f"   📊 Средняя оценка: {avg_score*100:.1f}%")
        print(f"   ⏱️ Среднее время: {avg_time:.1f}с")
        print(f"   🚀 Готовность к продакшену: {'✅ ДА' if avg_score >= 0.8 else '❌ НЕТ'}")


async def main():
    """Запускает все реальные тесты"""
    tester = RealWorldTester()
    
    print("🌍 РЕАЛЬНЫЕ ТЕСТЫ KITTYCORE 3.0")
    print("Проверяем систему на практических задачах")
    print("="*80)
    
    # ТЕСТ 1: Простая математика
    await tester.run_test(
        name="Калькулятор факториала",
        task="Создай Python скрипт для вычисления факториала числа с проверкой ввода",
        expected_files=["factorial.py"],
        expected_content=["factorial", "def", "import", "int(input"]
    )
    
    # ТЕСТ 2: Веб-разработка
    await tester.run_test(
        name="Форма регистрации",
        task="Создай HTML страницу с формой регистрации (имя, email, пароль) и CSS стилями",
        expected_files=["registration.html"],
        expected_content=["<form", "input", "email", "password", "css", "style"]
    )
    
    # ТЕСТ 3: Работа с данными
    await tester.run_test(
        name="JSON конфигурация",
        task="Создай JSON файл конфигурации для веб-сервера с портом, хостом и настройками логирования",
        expected_files=["config.json"],
        expected_content=["port", "host", "logging", "{", "}"]
    )
    
    # ТЕСТ 4: Алгоритмы
    await tester.run_test(
        name="Сортировка массива",
        task="Создай Python скрипт с функцией быстрой сортировки и примером использования",
        expected_files=["quicksort.py"],
        expected_content=["quicksort", "def", "pivot", "sort", "example"]
    )
    
    # ТЕСТ 5: Документация
    await tester.run_test(
        name="README файл",
        task="Создай README.md файл для проекта калькулятора с описанием, установкой и примерами",
        expected_files=["README.md"],
        expected_content=["# ", "## ", "установка", "пример", "описание"]
    )
    
    # Выводим итоги
    tester.print_summary()
    
    # Возвращаем результат для CI/CD
    return tester.passed_tests == tester.total_tests


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 