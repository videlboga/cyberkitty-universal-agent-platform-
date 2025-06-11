"""
🐱 ValidatorKitty - Интеллектуальный валидатор результатов
Анализирует запросы, создает образы ожидаемых результатов и валидирует выполнение
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from loguru import logger

# from core.memory_management import MemoryManager


@dataclass
class ResultExpectation:
    """Образ ожидаемого результата"""
    task_type: str  # тип задачи: creation, analysis, calculation, etc.
    expected_files: List[str]  # ожидаемые файлы
    expected_content: List[str]  # ожидаемый контент
    quality_criteria: List[str]  # критерии качества
    success_indicators: List[str]  # индикаторы успеха
    user_approved: bool = False  # подтвержден пользователем


@dataclass  
class ValidationResult:
    """Результат валидации"""
    is_valid: bool
    issues: List[str]
    recommendations: List[str]
    retry_needed: bool = False


class ValidatorKitty:
    """🐱 Интеллектуальный валидатор-котейка"""
    
    def __init__(self, memory_manager=None):
        self.memory = memory_manager
        self.llm_provider = None  # Будем использовать LLM для анализа
        
    async def analyze_request(self, user_request: str) -> ResultExpectation:
        """
        ФАЗА 1: Анализ запроса и создание образа результата
        """
        logger.info(f"🔍 ValidatorKitty анализирует запрос: {user_request}")
        
        # Пока без LLM - создаем простой анализ
        return self._create_expectation_from_request(user_request)
    
    def _create_expectation_from_request(self, request: str) -> ResultExpectation:
        """Создание образа результата на основе анализа запроса"""
        request_lower = request.lower()
        
        # Определяем тип задачи
        if any(word in request_lower for word in ['сайт', 'страниц', 'html', 'веб']):
            return ResultExpectation(
                task_type="website_creation",
                expected_files=["index.html", "styles.css"],
                expected_content=[
                    "HTML структура сайта",
                    "CSS стили для оформления", 
                    "Контент соответствующий теме (котята/etc)",
                    "Работающие HTML теги",
                    "Заголовки и тексты по теме"
                ],
                quality_criteria=[
                    "Файлы должны содержать релевантный контент",
                    "HTML должен быть валидным", 
                    "CSS должен быть подключен",
                    "Контент должен соответствовать запросу"
                ],
                success_indicators=[
                    "Созданы HTML/CSS файлы",
                    "В контенте присутствует тема запроса",
                    "Файлы можно открыть в браузере"
                ]
            )
            
        elif any(word in request_lower for word in ['план', 'планир', 'завтра', 'дела']):
            return ResultExpectation(
                task_type="planning",
                expected_files=["план.txt", "план.md"],
                expected_content=[
                    "Конкретные пункты плана",
                    "Временные рамки", 
                    "Приоритеты задач",
                    "Структурированный список дел"
                ],
                quality_criteria=[
                    "План должен содержать конкретные пункты",
                    "Должны быть указаны временные рамки",
                    "Пункты должны быть реалистичными"
                ],
                success_indicators=[
                    "Создан файл с планом",
                    "В плане есть конкретные пункты дел",
                    "Указаны временные рамки"
                ]
            )
            
        elif any(word in request_lower for word in ['посчита', 'расчет', 'плотност', 'формул']):
            return ResultExpectation(
                task_type="calculation", 
                expected_files=["расчет.txt", "результат.txt"],
                expected_content=[
                    "Математические формулы",
                    "Численные значения и расчеты",
                    "Единицы измерения",
                    "Пошаговые вычисления",
                    "Конечный результат с цифрами"
                ],
                quality_criteria=[
                    "Должны присутствовать формулы",
                    "Должны быть численные расчеты", 
                    "Результат должен быть в числах",
                    "Должны быть указаны единицы измерения"
                ],
                success_indicators=[
                    "Файл содержит формулы",
                    "Есть численные значения",
                    "Присутствуют единицы измерения",
                    "Расчет логически завершен"
                ]
            )
            
        else:
            return ResultExpectation(
                task_type="general",
                expected_files=["результат.txt"],
                expected_content=[
                    "Содержимое релевантное запросу",
                    "Конкретная информация по теме",
                    "Структурированный ответ"
                ],
                quality_criteria=[
                    "Результат должен соответствовать запросу",
                    "Информация должна быть полезной",
                    "Ответ должен быть структурированным"
                ],
                success_indicators=[
                    "Создан файл с результатом",
                    "Содержимое соответствует запросу"
                ]
            )
    
    def format_expectation_for_user(self, expectation: ResultExpectation) -> str:
        """
        ФАЗА 2: Форматирование образа результата для показа пользователю
        """
        return f"""
🎯 ОБРАЗ ОЖИДАЕМОГО РЕЗУЛЬТАТА
========================================
📝 Тип задачи: {expectation.task_type}

📁 Ожидаемые файлы:
{chr(10).join([f"   📄 {file}" for file in expectation.expected_files])}

📋 Ожидаемый контент:
{chr(10).join([f"   ✅ {content}" for content in expectation.expected_content])}

🎯 Критерии качества:
{chr(10).join([f"   🔍 {criteria}" for criteria in expectation.quality_criteria])}

✅ Индикаторы успеха:
{chr(10).join([f"   🚀 {indicator}" for indicator in expectation.success_indicators])}

========================================
❓ Это соответствует твоим ожиданиям? (да/нет/уточни)
"""
    
    async def validate_results(self, expectation: ResultExpectation, 
                             created_files: List[str], 
                             step_results: Dict[str, Any]) -> ValidationResult:
        """
        ФАЗА 5: Валидация результатов против образа
        """
        logger.info(f"🔍 ValidatorKitty валидирует результаты против образа")
        
        issues = []
        recommendations = []
        
        # 1. Проверка создания файлов
        if expectation.expected_files:
            for expected_file in expectation.expected_files:
                if not any(expected_file.split('.')[0] in created_file for created_file in created_files):
                    issues.append(f"❌ Не создан ожидаемый файл типа: {expected_file}")
                    recommendations.append(f"Создать файл {expected_file}")
        
        # 2. Проверка контента файлов
        content_issues = await self._validate_file_content(created_files, expectation)
        issues.extend(content_issues)
        
        # 3. Проверка качества
        quality_issues = self._validate_quality_criteria(step_results, expectation)
        issues.extend(quality_issues)
        
        # 4. Проверка индикаторов успеха
        success_issues = self._validate_success_indicators(created_files, step_results, expectation)
        issues.extend(success_issues)
        
        is_valid = len(issues) == 0
        retry_needed = len(issues) > 0
        
        if issues:
            recommendations.extend([
                "🔄 Перезапустить задачу с реальными инструментами",
                "🎯 Сфокусироваться на создании релевантного контента",
                "📝 Убедиться что результат соответствует запросу"
            ])
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            recommendations=recommendations,
            retry_needed=retry_needed
        )
    
    async def _validate_file_content(self, created_files: List[str], expectation: ResultExpectation) -> List[str]:
        """Валидация содержимого файлов"""
        issues = []
        
        for file_path in created_files:
            try:
                # Читаем содержимое файла
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Для сайтов проверяем HTML контент
                if expectation.task_type == "website_creation":
                    if "котят" not in content.lower() and "cat" not in content.lower():
                        issues.append(f"❌ Файл {file_path}: нет контента о котятах")
                    if len(content) < 200:
                        issues.append(f"❌ Файл {file_path}: слишком мало контента")
                        
                # Для планов проверяем наличие конкретных пунктов
                elif expectation.task_type == "planning":
                    if "план" not in content.lower():
                        issues.append(f"❌ Файл {file_path}: нет самого плана")
                    if content.count('\n') < 3:  # Мало строк = мало пунктов
                        issues.append(f"❌ Файл {file_path}: слишком короткий план")
                        
                # Для расчетов проверяем формулы и числа
                elif expectation.task_type == "calculation":
                    has_numbers = any(char.isdigit() for char in content)
                    has_formula_chars = any(char in content for char in ['=', '+', '-', '*', '/', '^'])
                    
                    if not has_numbers:
                        issues.append(f"❌ Файл {file_path}: нет численных расчетов")
                    if not has_formula_chars:
                        issues.append(f"❌ Файл {file_path}: нет формул или математических операций")
                        
            except Exception as e:
                issues.append(f"❌ Ошибка чтения файла {file_path}: {e}")
                
        return issues
    
    def _validate_quality_criteria(self, step_results: Dict[str, Any], expectation: ResultExpectation) -> List[str]:
        """Валидация критериев качества"""
        issues = []
        
        # Проверяем что агенты не делали левые действия
        results_text = " ".join([str(result.get('result', '')) for result in step_results.values()])
        
        if "httpbin.org" in results_text:
            issues.append("❌ Агенты проверяли httpbin.org вместо реальной работы")
            
        return issues
    
    def _validate_success_indicators(self, created_files: List[str], step_results: Dict[str, Any], 
                                   expectation: ResultExpectation) -> List[str]:
        """Валидация индикаторов успеха"""
        issues = []
        
        # Основной индикатор - были ли созданы файлы для задач создания
        if expectation.task_type in ["website_creation", "planning", "calculation"]:
            if not created_files:
                issues.append("❌ Не создано ни одного файла для задачи создания")
                
        return issues
    
    def format_validation_result(self, result: ValidationResult) -> str:
        """Форматирование результата валидации"""
        if result.is_valid:
            return """
✅ ВАЛИДАЦИЯ ПРОЙДЕНА УСПЕШНО!
🎉 Результат соответствует ожиданиям
"""
        else:
            issues_text = "\n".join([f"   {issue}" for issue in result.issues])
            recommendations_text = "\n".join([f"   {rec}" for rec in result.recommendations])
            
            return f"""
❌ ВАЛИДАЦИЯ НЕ ПРОЙДЕНА
🚨 Обнаружены проблемы:
{issues_text}

🔧 Рекомендации:
{recommendations_text}

{'🔄 ТРЕБУЕТСЯ ДОРАБОТКА' if result.retry_needed else ''}
""" 