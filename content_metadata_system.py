#!/usr/bin/env python3
"""
🎯 ПРАВИЛЬНАЯ СИСТЕМА: Контент + Метаданные

Контент - для пользователя (чистый, полезный)
Метаданные - для системы (богатые, подробные)
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

@dataclass
class TaskMetadata:
    """Богатые метаданные выполнения задачи"""
    task_id: str
    original_task: str
    agent_id: str
    agent_type: str
    execution_time: float
    start_time: str
    end_time: str
    
    # LLM анализ
    llm_analysis: Dict[str, Any]
    complexity_score: float
    estimated_difficulty: str
    
    # Процесс выполнения
    steps_planned: List[str]
    steps_executed: List[Dict[str, Any]]
    tools_used: List[str]
    errors_encountered: List[str]
    
    # Качество и критика
    critiques: List[Dict[str, Any]]
    quality_score: float
    improvement_suggestions: List[str]
    
    # Системная информация
    rate_limiting_applied: bool
    cache_hit: bool
    memory_usage: Dict[str, Any]
    system_health: float
    
    # Результат
    content_file: str
    content_type: str
    content_size: int
    success: bool
    user_satisfaction_predicted: float

class ContentMetadataSystem:
    """Система разделения контента и метаданных"""
    
    def __init__(self, output_dir: str = "./outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.metadata_dir = self.output_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        
    def create_content_with_metadata(
        self, 
        task: str, 
        content: str, 
        filename: str,
        metadata: TaskMetadata
    ) -> Dict[str, str]:
        """Создаёт файл с контентом + отдельный файл с метаданными"""
        
        # 1. СОХРАНЯЕМ ЧИСТЫЙ КОНТЕНТ для пользователя
        content_path = self.output_dir / filename
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 2. СОХРАНЯЕМ БОГАТЫЕ МЕТАДАННЫЕ для системы
        metadata_filename = f"{filename}.meta.json"
        metadata_path = self.metadata_dir / metadata_filename
        
        # Обновляем метаданные
        metadata.content_file = str(content_path)
        metadata.content_size = len(content.encode('utf-8'))
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(metadata), f, indent=2, ensure_ascii=False)
        
        # 3. СОЗДАЁМ ЧЕЛОВЕКОЧИТАЕМЫЙ ОТЧЁТ
        report_filename = f"{filename}.report.md"
        report_path = self.metadata_dir / report_filename
        
        report_content = self._generate_human_report(metadata, content)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return {
            "content_file": str(content_path),
            "metadata_file": str(metadata_path),
            "report_file": str(report_path)
        }
    
    def _generate_human_report(self, metadata: TaskMetadata, content: str) -> str:
        """Генерирует человекочитаемый отчёт"""
        
        report = f"""# 📊 Отчёт выполнения задачи

## 🎯 Основная информация
- **Задача:** {metadata.original_task}
- **ID:** {metadata.task_id}
- **Агент:** {metadata.agent_id} ({metadata.agent_type})
- **Время выполнения:** {metadata.execution_time:.2f}с
- **Успех:** {'✅ Да' if metadata.success else '❌ Нет'}

## 🧠 LLM Анализ
- **Сложность:** {metadata.complexity_score:.2f} ({metadata.estimated_difficulty})
- **Анализ:** {metadata.llm_analysis.get('summary', 'Не указан')}

## 🔧 Процесс выполнения
### Запланированные шаги:
{chr(10).join(f"- {step}" for step in metadata.steps_planned)}

### Выполненные шаги:
{chr(10).join(f"- {step.get('description', 'Неизвестный шаг')}: {'✅' if step.get('success') else '❌'}" for step in metadata.steps_executed)}

### Использованные инструменты:
{', '.join(metadata.tools_used) if metadata.tools_used else 'Нет'}

## 🎭 Критика и качество
- **Оценка качества:** {metadata.quality_score:.2f}/1.0
- **Прогноз удовлетворённости пользователя:** {metadata.user_satisfaction_predicted:.2f}/1.0

### Критические замечания:
{chr(10).join(f"- {critique.get('summary', 'Нет описания')}" for critique in metadata.critiques)}

### Предложения по улучшению:
{chr(10).join(f"- {suggestion}" for suggestion in metadata.improvement_suggestions)}

## 🔍 Системная информация
- **Rate limiting:** {'Применён' if metadata.rate_limiting_applied else 'Не применён'}
- **Кеш:** {'Попадание' if metadata.cache_hit else 'Промах'}
- **Здоровье системы:** {metadata.system_health:.2f}/1.0
- **Использование памяти:** {metadata.memory_usage.get('peak_mb', 0):.1f} MB

## 📁 Результат
- **Файл контента:** {metadata.content_file}
- **Тип контента:** {metadata.content_type}
- **Размер:** {metadata.content_size} байт

### Превью контента:
```
{content[:200]}{'...' if len(content) > 200 else ''}
```

---
*Отчёт сгенерирован KittyCore 3.0 в {metadata.end_time}*
"""
        return report

def demonstrate_correct_approach():
    """Демонстрация правильного подхода"""
    print("🎯 ПРАВИЛЬНЫЙ ПОДХОД: Контент + Метаданные")
    print("=" * 60)
    
    system = ContentMetadataSystem()
    
    # Пример 1: Python файл
    task1 = "Создай файл hello_world.py с программой Hello World"
    content1 = 'print("Hello, World!")'
    
    metadata1 = TaskMetadata(
        task_id="task_001",
        original_task=task1,
        agent_id="python_agent",
        agent_type="CodeGenerator",
        execution_time=2.34,
        start_time="2025-01-13 14:30:00",
        end_time="2025-01-13 14:30:02",
        llm_analysis={
            "summary": "Простая задача создания Hello World программы",
            "complexity": "low",
            "estimated_time": 1.5
        },
        complexity_score=0.2,
        estimated_difficulty="easy",
        steps_planned=[
            "Создать Python код с print функцией",
            "Сохранить в файл hello_world.py"
        ],
        steps_executed=[
            {"description": "Генерация Python кода", "success": True, "time": 1.2},
            {"description": "Сохранение файла", "success": True, "time": 0.1}
        ],
        tools_used=["code_generator", "file_manager"],
        errors_encountered=[],
        critiques=[
            {
                "type": "quality",
                "score": 1.0,
                "summary": "Код соответствует требованиям",
                "details": "Простой и правильный Hello World"
            }
        ],
        quality_score=1.0,
        improvement_suggestions=[],
        rate_limiting_applied=False,
        cache_hit=False,
        memory_usage={"peak_mb": 12.5, "avg_mb": 8.2},
        system_health=0.85,
        content_file="",
        content_type="python",
        content_size=0,
        success=True,
        user_satisfaction_predicted=0.95
    )
    
    files1 = system.create_content_with_metadata(
        task1, content1, "hello_world.py", metadata1
    )
    
    print("✅ СОЗДАН PYTHON ФАЙЛ:")
    print(f"   📁 Контент: {files1['content_file']}")
    print(f"   📊 Метаданные: {files1['metadata_file']}")
    print(f"   📋 Отчёт: {files1['report_file']}")
    
    # Пример 2: HTML файл
    task2 = "Создай HTML страницу с формой регистрации"
    content2 = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Регистрация</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        form { max-width: 400px; }
        input { width: 100%; padding: 10px; margin: 10px 0; }
        button { background: #007bff; color: white; padding: 12px 20px; border: none; }
    </style>
</head>
<body>
    <h1>Регистрация пользователя</h1>
    <form>
        <input type="text" placeholder="Имя" required>
        <input type="email" placeholder="Email" required>
        <input type="password" placeholder="Пароль" required>
        <button type="submit">Зарегистрироваться</button>
    </form>
</body>
</html>'''
    
    metadata2 = TaskMetadata(
        task_id="task_002",
        original_task=task2,
        agent_id="web_agent",
        agent_type="WebDeveloper",
        execution_time=5.67,
        start_time="2025-01-13 14:31:00",
        end_time="2025-01-13 14:31:06",
        llm_analysis={
            "summary": "Создание HTML формы с базовой стилизацией",
            "complexity": "medium",
            "estimated_time": 4.0
        },
        complexity_score=0.6,
        estimated_difficulty="medium",
        steps_planned=[
            "Создать HTML структуру",
            "Добавить форму регистрации",
            "Применить CSS стили",
            "Валидировать HTML"
        ],
        steps_executed=[
            {"description": "HTML структура", "success": True, "time": 1.5},
            {"description": "Форма регистрации", "success": True, "time": 2.0},
            {"description": "CSS стилизация", "success": True, "time": 1.8},
            {"description": "Валидация", "success": True, "time": 0.37}
        ],
        tools_used=["html_generator", "css_generator", "validator"],
        errors_encountered=["Минорная ошибка в CSS отступах (исправлена)"],
        critiques=[
            {
                "type": "design",
                "score": 0.8,
                "summary": "Хороший дизайн, можно улучшить",
                "details": "Форма функциональна, стили базовые но аккуратные"
            }
        ],
        quality_score=0.85,
        improvement_suggestions=[
            "Добавить валидацию на клиенте",
            "Улучшить responsive дизайн",
            "Добавить анимации"
        ],
        rate_limiting_applied=True,
        cache_hit=False,
        memory_usage={"peak_mb": 18.3, "avg_mb": 14.7},
        system_health=0.78,
        content_file="",
        content_type="html",
        content_size=0,
        success=True,
        user_satisfaction_predicted=0.82
    )
    
    files2 = system.create_content_with_metadata(
        task2, content2, "registration_form.html", metadata2
    )
    
    print("\n✅ СОЗДАН HTML ФАЙЛ:")
    print(f"   📁 Контент: {files2['content_file']}")
    print(f"   📊 Метаданные: {files2['metadata_file']}")
    print(f"   📋 Отчёт: {files2['report_file']}")
    
    return files1, files2

def show_file_contents(files):
    """Показать содержимое созданных файлов"""
    print("\n📁 СОДЕРЖИМОЕ ФАЙЛОВ:")
    print("=" * 60)
    
    # Показываем контент
    content_file = files['content_file']
    print(f"\n💎 КОНТЕНТ ({content_file}):")
    try:
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(content[:300] + ("..." if len(content) > 300 else ""))
    except Exception as e:
        print(f"Ошибка чтения: {e}")
    
    # Показываем отчёт
    report_file = files['report_file']
    print(f"\n📋 ОТЧЁТ ({report_file}):")
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            report = f.read()
        print(report[:500] + ("..." if len(report) > 500 else ""))
    except Exception as e:
        print(f"Ошибка чтения: {e}")

def main():
    """Главная функция демонстрации"""
    print("🎯 СИСТЕМА КОНТЕНТ + МЕТАДАННЫЕ")
    print("=" * 80)
    
    print("💡 ПРИНЦИП:")
    print("• Пользователь получает ЧИСТЫЙ КОНТЕНТ")
    print("• Система получает БОГАТЫЕ МЕТАДАННЫЕ")
    print("• Отчётность НЕ МЕШАЕТ результату")
    print("• Всё структурировано и доступно")
    
    files1, files2 = demonstrate_correct_approach()
    
    print("\n" + "="*60)
    show_file_contents(files1)
    
    print("\n🎉 РЕЗУЛЬТАТ:")
    print("✅ Пользователь получил работающий код")
    print("✅ Система получила подробную аналитику")
    print("✅ Отчётность не мешает результату")
    print("✅ Всё структурировано и удобно")

if __name__ == "__main__":
    main() 