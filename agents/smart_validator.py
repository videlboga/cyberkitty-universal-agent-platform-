"""
🧠 SmartValidator - Умный LLM-валидатор качества результатов

Оценивает результаты с позиции конечной пользы для пользователя:
- "Работающий код, выполняющий поставленную задачу"
- "Файл с реальным контентом, решающим проблему" 
- "Результат который можно использовать немедленно"
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from kittycore.llm import get_llm_provider

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Результат умной валидации"""
    is_valid: bool
    score: float  # 0.0 - 1.0
    user_benefit: str  # Польза для пользователя
    issues: List[str]  # Найденные проблемы
    recommendations: List[str]  # Рекомендации по улучшению
    verdict: str  # Итоговый вердикт


class SmartValidator:
    """
    Умный валидатор использующий LLM для оценки качества результатов
    """
    
    def __init__(self):
        # Используем дешёвый Ministral 8B для валидации ($0.20/M vs $2.00/M)
        self.llm_provider = get_llm_provider("mistralai/ministral-8b")
        logger.info("🧠 SmartValidator инициализирован с дешёвым Ministral 8B")
    
    async def validate_result(self, 
                            original_task: str, 
                            result: Dict[str, Any],
                            created_files: List[str] = None) -> ValidationResult:
        """
        Умная валидация результата с позиции конечной пользы
        """
        try:
            created_files = created_files or []
            
            # 1. Анализируем файлы если они есть
            files_content = {}
            for file_path in created_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Ограничиваем размер для LLM
                            files_content[file_path] = content[:2000] + ("..." if len(content) > 2000 else "")
                    except Exception as e:
                        files_content[file_path] = f"Ошибка чтения файла: {e}"
            
            # 2. Угадываем задачу если она неизвестна
            task_to_validate = original_task
            if not original_task or original_task in ["неизвестно", "unknown", ""]:
                logger.info("🔮 Исходная задача неизвестна, пытаемся угадать...")
                task_to_validate = await self._guess_original_task(files_content)
            
            # 3. Создаем промпт для LLM валидации
            validation_prompt = self._create_validation_prompt(
                task_to_validate, result, files_content
            )
            
            # 4. Получаем оценку от LLM
            llm_response = self.llm_provider.complete(validation_prompt)
            
            # 5. Парсим ответ LLM
            validation_result = self._parse_llm_response(llm_response)
            
            logger.info(f"🔍 Валидация завершена: {validation_result.verdict}")
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА SmartValidator: {e}")
            # Без fallback - если LLM не работает, система должна знать об этом
            raise Exception(f"❌ SmartValidator НЕ МОЖЕТ работать без LLM: {e}")
    
    def _create_validation_prompt(self, 
                                original_task: str, 
                                result: Dict[str, Any], 
                                files_content: Dict[str, str]) -> str:
        """Создает промпт для LLM валидации"""
        
        prompt = f"""Ты умный валидатор качества результатов. Твоя задача - оценить, получил ли пользователь РЕАЛЬНУЮ ПОЛЬЗУ от выполнения задачи.

ИСХОДНАЯ ЗАДАЧА ПОЛЬЗОВАТЕЛЯ:
{original_task}

РЕЗУЛЬТАТ СИСТЕМЫ:
{json.dumps(result, ensure_ascii=False, indent=2)}

СОЗДАННЫЕ ФАЙЛЫ:
"""
        
        if files_content:
            for file_path, content in files_content.items():
                prompt += f"\n=== {file_path} ===\n{content}\n"
        else:
            prompt += "Файлы не созданы.\n"
        
        prompt += """
КРИТЕРИИ ОЦЕНКИ:
1. КОНЕЧНАЯ ПОЛЬЗА: Может ли пользователь использовать результат ПРЯМО СЕЙЧАС?
2. СООТВЕТСТВИЕ ЗАДАЧЕ: Решает ли результат именно поставленную задачу?
3. РАБОЧИЙ РЕЗУЛЬТАТ: Это готовый к использованию продукт или заготовка/план?

ПРИМЕРЫ ОЦЕНКИ:
- Задача "Создай сайт" + Файл с планом создания = ❌ НЕ ВАЛИДНО (план ≠ сайт)
- Задача "Создай сайт" + Рабочий HTML файл = ✅ ВАЛИДНО (готовый сайт)
- Задача "Посчитай плотность" + Файл с формулами и числами = ✅ ВАЛИДНО (расчет готов)
- Задача "Посчитай плотность" + Файл с описанием как считать = ❌ НЕ ВАЛИДНО (инструкция ≠ расчет)

ОТВЕЧАЙ В JSON ФОРМАТЕ:
{
    "is_valid": true/false,
    "score": 0.8,
    "user_benefit": "Описание конкретной пользы для пользователя",
    "issues": ["Список найденных проблем"],
    "recommendations": ["Рекомендации по улучшению"],
    "verdict": "Краткий итоговый вердикт"
}

JSON ОТВЕТ:"""
        
        return prompt
    
    def _parse_llm_response(self, llm_response: str) -> ValidationResult:
        """Парсит ответ LLM в ValidationResult"""
        try:
            # Пытаемся извлечь JSON из ответа
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                parsed = json.loads(json_str)
                
                return ValidationResult(
                    is_valid=parsed.get('is_valid', False),
                    score=float(parsed.get('score', 0.0)),
                    user_benefit=parsed.get('user_benefit', 'Польза не определена'),
                    issues=parsed.get('issues', []),
                    recommendations=parsed.get('recommendations', []),
                    verdict=parsed.get('verdict', 'Вердикт не определен')
                )
            else:
                # Если JSON не найден, парсим как текст
                return self._parse_text_response(llm_response)
                
        except Exception as e:
            logger.warning(f"Ошибка парсинга JSON ответа LLM: {e}")
            return self._parse_text_response(llm_response)
    
    def _parse_text_response(self, response: str) -> ValidationResult:
        """Парсит текстовый ответ LLM"""
        response_lower = response.lower()
        
        # Простая эвристика для определения валидности
        is_valid = any(word in response_lower for word in [
            'валидно', 'готов', 'рабочий', 'можно использовать', 'выполнено'
        ]) and not any(word in response_lower for word in [
            'не валидно', 'план', 'инструкция', 'описание как', 'не готов'
        ])
        
        score = 0.8 if is_valid else 0.2
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            user_benefit=f"Автоанализ: {'Результат пригоден к использованию' if is_valid else 'Результат требует доработки'}",
            issues=[] if is_valid else ["LLM не смог четко оценить результат"],
            recommendations=["Улучшить промпт валидации"] if not is_valid else [],
            verdict=f"{'✅ ВАЛИДНО' if is_valid else '❌ НЕ ВАЛИДНО'} (автоанализ)"
        )

    async def _guess_original_task(self, files_content: Dict[str, str]) -> str:
        """Угадывает исходную задачу по содержимому файлов"""
        try:
            if not files_content:
                return "неизвестная задача"
            
            # Собираем всё содержимое для анализа
            combined_content = ""
            for file_path, content in files_content.items():
                combined_content += f"\n=== {file_path} ===\n{content}\n"
            
            # Промпт для угадывания задачи
            guess_prompt = f"""Проанализируй содержимое файлов и угадай какую задачу просил пользователь.

СОДЕРЖИМОЕ ФАЙЛОВ:
{combined_content[:1500]}

Отвечай одной короткой фразой - какую задачу скорее всего просил пользователь:

ПРИМЕРЫ ОТВЕТОВ:
- "создай сайт с котятами"
- "посчитай плотность черной дыры"  
- "составь план на день"
- "напиши код для расчета"
- "создай веб-приложение"

УГАДАННАЯ ЗАДАЧА:"""

            # Запрос к LLM
            llm_response = self.llm_provider.complete(guess_prompt)
            guessed_task = llm_response.strip().strip('"').lower()
            
            logger.info(f"🔮 Угадана задача: {guessed_task}")
            return guessed_task
            
        except Exception as e:
            logger.warning(f"Не удалось угадать задачу: {e}")
            return "неизвестная задача"





async def validate_task_result(task: str, 
                             result: Dict[str, Any], 
                             files: List[str] = None) -> ValidationResult:
    """
    Быстрая функция для валидации результата задачи
    """
    validator = SmartValidator()
    return await validator.validate_result(task, result, files)