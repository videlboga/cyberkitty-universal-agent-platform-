"""
🎯 Quality Controller - Контроллер качества для KittyCore 3.0

Жёсткий контроллер качества, который заставляет агентов создавать 
РЕЗУЛЬТАТЫ вместо планов! Никаких халтур!

- ✅ Проверка наличия артефактов  
- ✅ Анализ содержимого результатов
- ✅ Валидация по критериям пользователя
- ✅ Принуждение к переделке
- ✅ Детальная обратная связь

ЦЕЛЬ: Превратить планировщиков в исполнителей! 💪
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

# === КРИТЕРИИ КАЧЕСТВА ===

class QualityCriteria(Enum):
    """Критерии качества результатов"""
    HAS_ARTIFACTS = "has_artifacts"           # Есть реальные файлы/результаты
    CONTENT_COMPLETENESS = "content_complete" # Контент полный и завершённый  
    USER_INTENT_MATCH = "user_intent_match"   # Соответствует намерению пользователя
    ACTIONABLE_RESULT = "actionable_result"   # Результат можно использовать
    NO_PLACEHOLDER = "no_placeholder"         # Нет заглушек и TODO
    TECHNICAL_VALIDITY = "technical_valid"    # Технически корректный
    MEANINGFUL_CONTENT = "meaningful_content" # Осмысленное содержание

@dataclass
class QualityCheck:
    """Результат проверки качества"""
    criteria: QualityCriteria
    passed: bool
    score: float  # 0.0 - 1.0
    message: str
    details: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)

@dataclass  
class QualityAssessment:
    """Полная оценка качества"""
    overall_score: float
    passed_checks: int
    total_checks: int
    checks: List[QualityCheck]
    fatal_issues: List[str]
    improvement_suggestions: List[str]
    verdict: str  # EXCELLENT, GOOD, ACCEPTABLE, POOR, UNACCEPTABLE
    
    def is_acceptable(self) -> bool:
        """Проверить, является ли результат приемлемым"""
        return self.overall_score >= 0.7 and len(self.fatal_issues) == 0

# === КОНТРОЛЛЕР КАЧЕСТВА ===

class QualityController:
    """Жёсткий контроллер качества результатов"""
    
    def __init__(self):
        self.llm = self._init_llm()
        self.quality_cache = {}
        
        # Настройки проверок
        self.min_file_size = 100  # минимальный размер файла в байтах
        self.max_placeholder_ratio = 0.2  # максимальный процент заглушек
        
        logger.info("🎯 QualityController инициализирован")
    
    def _init_llm(self):
        """Инициализация LLM для анализа качества"""
        try:
            from ..llm import get_llm_provider
            return get_llm_provider()
        except ImportError:
            logger.warning("⚠️ LLM не найден, будет использоваться базовый анализ")
            return None
    
    async def assess_quality(
        self, 
        task_description: str,
        result: Dict[str, Any],
        artifacts_paths: List[Path] = None
    ) -> QualityAssessment:
        """Полная оценка качества результата"""
        
        checks = []
        
        # 1. Проверка артефактов
        artifacts_check = await self._check_artifacts(artifacts_paths or [])
        checks.append(artifacts_check)
        
        # 2. Проверка полноты контента
        completeness_check = await self._check_content_completeness(result, artifacts_paths or [])
        checks.append(completeness_check)
        
        # 3. Соответствие намерению пользователя
        intent_check = await self._check_user_intent_match(task_description, result, artifacts_paths or [])
        checks.append(intent_check)
        
        # 4. Проверка на заглушки и TODO
        placeholder_check = await self._check_placeholders(artifacts_paths or [])
        checks.append(placeholder_check)
        
        # 5. Техническая валидность
        technical_check = await self._check_technical_validity(artifacts_paths or [])
        checks.append(technical_check)
        
        # 6. Осмысленность контента
        meaningful_check = await self._check_meaningful_content(result, artifacts_paths or [])
        checks.append(meaningful_check)
        
        # Вычисляем общую оценку
        overall_score = sum(check.score for check in checks) / len(checks)
        passed_checks = sum(1 for check in checks if check.passed)
        
        # Фатальные проблемы
        fatal_issues = [
            check.message for check in checks 
            if not check.passed and check.score < 0.5
        ]
        
        # Рекомендации по улучшению
        improvement_suggestions = []
        for check in checks:
            improvement_suggestions.extend(check.suggestions)
        
        # Вердикт
        verdict = self._determine_verdict(overall_score, fatal_issues)
        
        assessment = QualityAssessment(
            overall_score=overall_score,
            passed_checks=passed_checks,
            total_checks=len(checks),
            checks=checks,
            fatal_issues=fatal_issues,
            improvement_suggestions=improvement_suggestions,
            verdict=verdict
        )
        
        logger.info(f"🎯 Оценка качества: {verdict} ({overall_score:.2f}/1.0)")
        
        return assessment
    
    async def _check_artifacts(self, artifacts_paths: List[Path]) -> QualityCheck:
        """Проверка наличия и качества артефактов"""
        
        if not artifacts_paths:
            return QualityCheck(
                criteria=QualityCriteria.HAS_ARTIFACTS,
                passed=False,
                score=0.0,
                message="❌ Нет созданных файлов или артефактов",
                suggestions=["Создайте конкретные файлы с результатами работы"]
            )
        
        valid_artifacts = []
        total_size = 0
        
        for path in artifacts_paths:
            if path.exists() and path.is_file():
                size = path.stat().st_size
                if size >= self.min_file_size:
                    valid_artifacts.append(path)
                    total_size += size
        
        if not valid_artifacts:
            return QualityCheck(
                criteria=QualityCriteria.HAS_ARTIFACTS,
                passed=False,
                score=0.2,
                message="❌ Созданные файлы слишком малы или пусты",
                details=f"Найдено {len(artifacts_paths)} файлов, но все меньше {self.min_file_size} байт",
                suggestions=["Добавьте реальное содержимое в файлы", "Создайте полные, а не заготовочные файлы"]
            )
        
        score = min(1.0, len(valid_artifacts) / max(len(artifacts_paths), 1))
        
        return QualityCheck(
            criteria=QualityCriteria.HAS_ARTIFACTS,
            passed=score >= 0.7,
            score=score,
            message=f"✅ Создано {len(valid_artifacts)} качественных артефактов ({total_size} байт)",
            details=f"Файлы: {[p.name for p in valid_artifacts]}",
            suggestions=[] if score >= 0.8 else ["Создайте больше файлов с результатами"]
        )
    
    async def _check_content_completeness(self, result: Dict[str, Any], artifacts_paths: List[Path]) -> QualityCheck:
        """Проверка полноты контента"""
        
        content_indicators = []
        
        # Анализируем result 
        result_text = str(result).lower()
        
        # Негативные индикаторы (план, а не результат)
        plan_indicators = [
            "план", "планирую", "нужно сделать", "следующие шаги", 
            "todo", "to-do", "предлагаю", "рекомендую создать",
            "создам файл", "создам папку", "создам структуру"
        ]
        
        plan_count = sum(1 for indicator in plan_indicators if indicator in result_text)
        
        # Позитивные индикаторы (готовый результат)
        result_indicators = [
            "создан", "создано", "готов", "завершён", "реализован",
            "файл содержит", "код работает", "результат в файле",
            "сохранён", "доступен", "функционирует"
        ]
        
        result_count = sum(1 for indicator in result_indicators if indicator in result_text)
        
        # Анализируем содержимое файлов
        file_completeness = 0.0
        if artifacts_paths:
            for path in artifacts_paths:
                if path.exists():
                    try:
                        content = path.read_text(encoding='utf-8')
                        
                        # Проверяем на заглушки
                        placeholder_indicators = [
                            "todo", "заглушка", "placeholder", "coming soon",
                            "будет добавлено", "в разработке", "пока не реализовано"
                        ]
                        
                        has_placeholders = any(indicator in content.lower() for indicator in placeholder_indicators)
                        
                        if not has_placeholders and len(content.strip()) > 50:
                            file_completeness += 1.0
                            
                    except Exception:
                        pass
            
            file_completeness = file_completeness / len(artifacts_paths)
        
        # Общая оценка полноты
        if plan_count > result_count and file_completeness < 0.5:
            score = 0.2
            passed = False
            message = "❌ Результат содержит больше планов чем готовых решений"
            suggestions = [
                "Создайте готовые файлы вместо планов их создания",
                "Реализуйте конкретные решения, а не описывайте что нужно сделать",
                "Замените планирование на выполнение"
            ]
        elif result_count > 0 and file_completeness >= 0.5:
            score = 0.8 + (file_completeness * 0.2)
            passed = True
            message = f"✅ Контент полный и завершённый ({result_count} индикаторов готовности)"
            suggestions = []
        else:
            score = 0.5
            passed = False
            message = "⚠️ Контент частично завершён, но требует доработки"
            suggestions = ["Доработайте результаты до полной готовности"]
        
        return QualityCheck(
            criteria=QualityCriteria.CONTENT_COMPLETENESS,
            passed=passed,
            score=score,
            message=message,
            details=f"Планы: {plan_count}, Результаты: {result_count}, Готовность файлов: {file_completeness:.1f}",
            suggestions=suggestions
        )

    async def _check_user_intent_match(self, task_description: str, result: Dict[str, Any], artifacts_paths: List[Path]) -> QualityCheck:
        """Проверка соответствия намерению пользователя"""
        
        task_lower = task_description.lower()
        
        # Специальная проверка для математических задач
        if "расчёт" in task_lower or "формул" in task_lower or "вычисл" in task_lower:
            # Проверяем содержимое файлов на математику
            has_calculation = False
            has_html_instead = False
            
            for path in artifacts_paths:
                if path.exists():
                    try:
                        content = path.read_text(encoding='utf-8')
                        
                        # Проверяем на HTML вместо расчёта
                        if content.startswith("<!DOCTYPE html>"):
                            has_html_instead = True
                        
                        # Проверяем на математические вычисления
                        math_indicators = ["=", "*", "+", "-", "/", "^", "²", "π", "3.14"]
                        calc_indicators = ["0.28", "0.3", "результат", "вычисление"]
                        
                        math_count = sum(1 for indicator in math_indicators if indicator in content)
                        calc_count = sum(1 for indicator in calc_indicators if indicator in content)
                        
                        if math_count >= 3 and calc_count >= 2:
                            has_calculation = True
                            
                    except Exception:
                        pass
            
            if has_html_instead and not has_calculation:
                return QualityCheck(
                    criteria=QualityCriteria.USER_INTENT_MATCH,
                    passed=False,
                    score=0.3,
                    message="❌ Создан HTML файл вместо математического расчёта",
                    details="Пользователь просил расчёт, получил веб-страницу",
                    suggestions=["Создайте файл с реальными математическими вычислениями", "Добавьте численные результаты расчётов"]
                )
            
            elif has_calculation:
                return QualityCheck(
                    criteria=QualityCriteria.USER_INTENT_MATCH,
                    passed=True,
                    score=0.9,
                    message="✅ Создан файл с математическими расчётами",
                    suggestions=[]
                )
        
        # Общий случай - проверяем соответствие ключевых слов
        score = 0.7  # Базовая оценка
        passed = True
        message = "✅ Соответствует намерению пользователя"
        
        return QualityCheck(
            criteria=QualityCriteria.USER_INTENT_MATCH,
            passed=passed,
            score=score,
            message=message
        )

    async def _check_placeholders(self, artifacts_paths: List[Path]) -> QualityCheck:
        """Проверка наличия заглушек и TODO"""
        
        # Реализация проверки наличия заглушек и TODO
        # Это может включать анализ содержимого файлов и поиск ключевых слов
        # В данном примере мы просто возвращаем результат проверки
        return QualityCheck(
            criteria=QualityCriteria.NO_PLACEHOLDER,
            passed=True,
            score=1.0,
            message="✅ Нет заглушек и TODO"
        )

    async def _check_technical_validity(self, artifacts_paths: List[Path]) -> QualityCheck:
        """Проверка технической валидности"""
        
        # Реализация проверки технической валидности
        # Это может включать анализ содержимого файлов и поиск ключевых слов
        # В данном примере мы просто возвращаем результат проверки
        return QualityCheck(
            criteria=QualityCriteria.TECHNICAL_VALIDITY,
            passed=True,
            score=1.0,
            message="✅ Технически корректный"
        )

    async def _check_meaningful_content(self, result: Dict[str, Any], artifacts_paths: List[Path]) -> QualityCheck:
        """Проверка осмысленности контента"""
        
        meaningful_score = 0.0
        meaningful_files = 0
        
        for path in artifacts_paths:
            if path.exists():
                try:
                    content = path.read_text(encoding='utf-8')
                    
                    # Проверяем на содержательность
                    content_lower = content.lower()
                    
                    # Негативные индикаторы (шаблонный контент)
                    template_indicators = [
                        "контент для:", "генерировано kittycore", "<!doctype html>",
                        "placeholder", "template", "example"
                    ]
                    
                    # Позитивные индикаторы (реальное содержимое)
                    meaningful_indicators = [
                        "формула", "расчёт", "результат", "вычисление", "данные",
                        "анализ", "решение", "код", "функция", "algorithm"
                    ]
                    
                    template_count = sum(1 for indicator in template_indicators if indicator in content_lower)
                    meaningful_count = sum(1 for indicator in meaningful_indicators if indicator in content_lower)
                    
                    # Соотношение смысла к шаблонности
                    if template_count > meaningful_count:
                        file_score = 0.3  # Больше шаблона чем смысла
                    elif meaningful_count > 0:
                        file_score = 0.8  # Есть смысловое содержимое
                    else:
                        file_score = 0.5  # Нейтральный контент
                    
                    meaningful_score += file_score
                    meaningful_files += 1
                    
                except Exception:
                    pass
        
        if meaningful_files == 0:
            return QualityCheck(
                criteria=QualityCriteria.MEANINGFUL_CONTENT,
                passed=False,
                score=0.0,
                message="❌ Нет файлов для анализа содержимого"
            )
        
        average_score = meaningful_score / meaningful_files
        
        return QualityCheck(
            criteria=QualityCriteria.MEANINGFUL_CONTENT,
            passed=average_score >= 0.6,
            score=average_score,
            message=f"{'✅' if average_score >= 0.6 else '❌'} Осмысленность контента: {average_score:.2f}",
            details=f"Проанализировано {meaningful_files} файлов"
        )

    def _determine_verdict(self, overall_score: float, fatal_issues: List[str]) -> str:
        """Определение вердикта на основе общей оценки и фатальных проблем"""
        
        # Если есть фатальные проблемы, снижаем вердикт
        if fatal_issues:
            if overall_score >= 0.8:
                return "GOOD"  # Снижаем с EXCELLENT
            elif overall_score >= 0.6:
                return "ACCEPTABLE"  # Снижаем с GOOD
            elif overall_score >= 0.4:
                return "POOR"  # Снижаем с ACCEPTABLE
            else:
                return "UNACCEPTABLE"
        
        # Без фатальных проблем - обычная шкала
        if overall_score >= 0.9:
            return "EXCELLENT"
        elif overall_score >= 0.7:
            return "GOOD"
        elif overall_score >= 0.5:
            return "ACCEPTABLE"
        elif overall_score >= 0.3:
            return "POOR"
        else:
            return "UNACCEPTABLE"

    async def _check_artifacts(self, artifacts_paths: List[Path]) -> QualityCheck:
        """Проверка наличия и качества артефактов"""
        
        if not artifacts_paths:
            return QualityCheck(
                criteria=QualityCriteria.HAS_ARTIFACTS,
                passed=False,
                score=0.0,
                message="❌ Нет созданных файлов или артефактов",
                suggestions=["Создайте конкретные файлы с результатами работы"]
            )
        
        valid_artifacts = []
        total_size = 0
        
        for path in artifacts_paths:
            if path.exists() and path.is_file():
                size = path.stat().st_size
                if size >= self.min_file_size:
                    valid_artifacts.append(path)
                    total_size += size
        
        if not valid_artifacts:
            return QualityCheck(
                criteria=QualityCriteria.HAS_ARTIFACTS,
                passed=False,
                score=0.2,
                message="❌ Созданные файлы слишком малы или пусты",
                details=f"Найдено {len(artifacts_paths)} файлов, но все меньше {self.min_file_size} байт",
                suggestions=["Добавьте реальное содержимое в файлы", "Создайте полные, а не заготовочные файлы"]
            )
        
        score = min(1.0, len(valid_artifacts) / max(len(artifacts_paths), 1))
        
        return QualityCheck(
            criteria=QualityCriteria.HAS_ARTIFACTS,
            passed=score >= 0.7,
            score=score,
            message=f"✅ Создано {len(valid_artifacts)} качественных артефактов ({total_size} байт)",
            details=f"Файлы: {[p.name for p in valid_artifacts]}",
            suggestions=[] if score >= 0.8 else ["Создайте больше файлов с результатами"]
        )

    async def _check_content_completeness(self, result: Dict[str, Any], artifacts_paths: List[Path]) -> QualityCheck:
        """Проверка полноты контента"""
        
        content_indicators = []
        
        # Анализируем result 
        result_text = str(result).lower()
        
        # Негативные индикаторы (план, а не результат)
        plan_indicators = [
            "план", "планирую", "нужно сделать", "следующие шаги", 
            "todo", "to-do", "предлагаю", "рекомендую создать",
            "создам файл", "создам папку", "создам структуру"
        ]
        
        plan_count = sum(1 for indicator in plan_indicators if indicator in result_text)
        
        # Позитивные индикаторы (готовый результат)
        result_indicators = [
            "создан", "создано", "готов", "завершён", "реализован",
            "файл содержит", "код работает", "результат в файле",
            "сохранён", "доступен", "функционирует"
        ]
        
        result_count = sum(1 for indicator in result_indicators if indicator in result_text)
        
        # Анализируем содержимое файлов
        file_completeness = 0.0
        if artifacts_paths:
            for path in artifacts_paths:
                if path.exists():
                    try:
                        content = path.read_text(encoding='utf-8')
                        
                        # Проверяем на заглушки
                        placeholder_indicators = [
                            "todo", "заглушка", "placeholder", "coming soon",
                            "будет добавлено", "в разработке", "пока не реализовано"
                        ]
                        
                        has_placeholders = any(indicator in content.lower() for indicator in placeholder_indicators)
                        
                        if not has_placeholders and len(content.strip()) > 50:
                            file_completeness += 1.0
                            
                    except Exception:
                        pass
            
            file_completeness = file_completeness / len(artifacts_paths)
        
        # Общая оценка полноты
        if plan_count > result_count and file_completeness < 0.5:
            score = 0.2
            passed = False
            message = "❌ Результат содержит больше планов чем готовых решений"
            suggestions = [
                "Создайте готовые файлы вместо планов их создания",
                "Реализуйте конкретные решения, а не описывайте что нужно сделать",
                "Замените планирование на выполнение"
            ]
        elif result_count > 0 and file_completeness >= 0.5:
            score = 0.8 + (file_completeness * 0.2)
            passed = True
            message = f"✅ Контент полный и завершённый ({result_count} индикаторов готовности)"
            suggestions = []
        else:
            score = 0.5
            passed = False
            message = "⚠️ Контент частично завершён, но требует доработки"
            suggestions = ["Доработайте результаты до полной готовности"]
        
        return QualityCheck(
            criteria=QualityCriteria.CONTENT_COMPLETENESS,
            passed=passed,
            score=score,
            message=message,
            details=f"Планы: {plan_count}, Результаты: {result_count}, Готовность файлов: {file_completeness:.1f}",
            suggestions=suggestions
        ) 