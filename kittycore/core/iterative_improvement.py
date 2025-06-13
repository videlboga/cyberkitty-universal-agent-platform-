"""
Iterative Agent Improvement - система самообучения агентов
Заменяет ContentFixer на цикл улучшения самого агента
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

from ..llm import get_llm_provider
from agents.smart_validator import ValidationResult
from kittycore.core.agent_learning_system import learning_system


@dataclass
class ImprovementFeedback:
    """Фидбек для улучшения агента"""
    issues: List[str]  # Конкретные проблемы
    recommendations: List[str]  # Рекомендации по улучшению
    approach_changes: List[str]  # Изменения в подходе
    tool_suggestions: List[str]  # Предложения по инструментам
    examples: List[str]  # Примеры правильного выполнения
    priority: str  # "critical", "high", "medium", "low"


@dataclass
class ImprovementAttempt:
    """Попытка улучшения агента"""
    attempt_number: int
    original_result: Dict[str, Any]
    validation: ValidationResult
    feedback: ImprovementFeedback
    improved_result: Optional[Dict[str, Any]] = None
    improved_validation: Optional[ValidationResult] = None
    success: bool = False


class IterativeImprovement:
    """Система итеративного улучшения агентов"""
    
    def __init__(self):
        # Используем ту же дешёвую модель для генерации фидбека
        self.llm_provider = get_llm_provider("mistralai/ministral-8b")
        self.max_attempts = 3  # Максимум попыток улучшения
        self.target_score = 0.7  # Целевая оценка качества
        logger.info("🔄 IterativeImprovement инициализирован")
    
    async def improve_agent_iteratively(self, 
                                      agent: Any,
                                      task: str,
                                      initial_result: Dict[str, Any],
                                      initial_validation: ValidationResult,
                                      smart_validator: Any) -> Tuple[Dict[str, Any], List[ImprovementAttempt]]:
        """
        Итеративно улучшает агента до достижения целевого качества
        
        Returns:
            (final_result, improvement_history)
        """
        
        logger.info(f"🔄 Начинаем итеративное улучшение агента (цель: {self.target_score:.1f})")
        
        attempts = []
        current_result = initial_result
        current_validation = initial_validation
        
        for attempt_num in range(1, self.max_attempts + 1):
            
            # Если качество достаточное - завершаем
            if current_validation.score >= self.target_score:
                logger.info(f"✅ Цель достигнута на попытке {attempt_num-1}: {current_validation.score:.1f}")
                break
            
            logger.info(f"🔄 Попытка улучшения #{attempt_num} (текущая оценка: {current_validation.score:.1f})")
            
            # 1. Генерируем фидбек для улучшения
            feedback = await self._generate_improvement_feedback(
                task, current_result, current_validation
            )
            
            # 2. Применяем улучшения к агенту
            improved_agent = await self._apply_improvements_to_agent(
                agent, feedback, task
            )
            
            # 3. Перезапускаем выполнение задачи
            try:
                improved_result = await improved_agent.execute_task()
                
                # 4. Валидируем улучшенный результат
                improved_validation = await smart_validator.validate_result(
                    original_task=task,
                    result=improved_result,
                    created_files=improved_result.get("files_created", [])
                )
                
                # 5. Записываем попытку
                attempt = ImprovementAttempt(
                    attempt_number=attempt_num,
                    original_result=current_result,
                    validation=current_validation,
                    feedback=feedback,
                    improved_result=improved_result,
                    improved_validation=improved_validation,
                    success=improved_validation.score > current_validation.score
                )
                
                attempts.append(attempt)
                
                # 6. Записываем опыт обучения
                await self._record_learning_experience(
                    agent, task, attempt_num, current_validation.score, 
                    improved_validation.score, feedback, attempt
                )
                
                # 7. Обновляем текущие результаты если есть улучшение
                if improved_validation.score > current_validation.score:
                    current_result = improved_result
                    current_validation = improved_validation
                    logger.info(f"📈 Улучшение: {current_validation.score:.1f} (+{improved_validation.score - current_validation.score:.1f})")
                else:
                    logger.warning(f"📉 Ухудшение: {improved_validation.score:.1f} (-{current_validation.score - improved_validation.score:.1f})")
                
            except Exception as e:
                logger.error(f"❌ Ошибка при улучшении агента: {e}")
                
                # Записываем неудачную попытку
                attempt = ImprovementAttempt(
                    attempt_number=attempt_num,
                    original_result=current_result,
                    validation=current_validation,
                    feedback=feedback,
                    success=False
                )
                attempts.append(attempt)
        
        # Итоговая статистика
        final_score = current_validation.score
        initial_score = initial_validation.score
        improvement = final_score - initial_score
        
        if improvement > 0:
            logger.info(f"🎯 Итеративное улучшение завершено: {initial_score:.1f} → {final_score:.1f} (+{improvement:.1f})")
        else:
            logger.warning(f"⚠️ Улучшения не достигнуты: {initial_score:.1f} → {final_score:.1f}")
        
        return current_result, attempts
    
    async def _record_learning_experience(self, 
                                        agent: Any, 
                                        task: str, 
                                        attempt_number: int,
                                        score_before: float,
                                        score_after: float,
                                        feedback: ImprovementFeedback,
                                        attempt: ImprovementAttempt):
        """Записывает опыт обучения агента"""
        
        agent_id = getattr(agent, 'agent_id', 'unknown_agent')
        
        # Извлекаем паттерны ошибок и успешные действия
        error_patterns = feedback.issues
        successful_actions = []
        failed_actions = []
        
        if attempt.success:
            successful_actions = feedback.recommendations[:2]  # Первые 2 рекомендации как успешные
        else:
            failed_actions = feedback.issues[:2]  # Первые 2 проблемы как неудачные
        
        # Записываем в систему обучения
        lesson = await learning_system.record_learning(
            agent_id=agent_id,
            task_description=task,
            attempt_number=attempt_number,
            score_before=score_before,
            score_after=score_after,
            error_patterns=error_patterns,
            successful_actions=successful_actions,
            failed_actions=failed_actions,
            feedback_received=str(feedback.recommendations),
            tools_used=feedback.tool_suggestions
        )
        
        logger.info(f"🧠 Урок записан для агента {agent_id}: {lesson}")
    
    async def _generate_improvement_feedback(self, 
                                           task: str, 
                                           result: Dict[str, Any], 
                                           validation: ValidationResult) -> ImprovementFeedback:
        """Генерирует конкретный фидбек для улучшения агента с учётом накопленных знаний"""
        
        # Получаем информацию о доступных инструментах
        available_tools = ["file_manager", "code_generator", "web_client", "system_tools"]
        
        # Получаем накопленные знания агента
        agent_id = "current_agent"  # TODO: получать реальный ID агента
        learning_suggestions = await learning_system.get_improvement_suggestions(
            agent_id=agent_id,
            current_task=task,
            current_errors=validation.issues
        )
        
        feedback_prompt = f"""
Ты эксперт по улучшению AI агентов. Проанализируй неудачное выполнение задачи и дай КОНКРЕТНЫЕ рекомендации.

ЗАДАЧА: {task}

РЕЗУЛЬТАТ АГЕНТА: {result.get('output', 'Нет вывода')}

ПРОБЛЕМЫ ВАЛИДАЦИИ:
- Оценка: {validation.score:.1f}/1.0  
- Проблемы: {', '.join(validation.issues)}
- Рекомендации: {', '.join(validation.recommendations)}

ДОСТУПНЫЕ ИНСТРУМЕНТЫ: {', '.join(available_tools)}

НАКОПЛЕННЫЕ ЗНАНИЯ АГЕНТА:
{chr(10).join(learning_suggestions) if learning_suggestions else "- Нет накопленного опыта"}

АНАЛИЗИРУЙ И ОТВЕЧАЙ ТОЛЬКО В JSON:
{{
    "issues": [
        "Конкретная техническая проблема (например: 'Агент использовал неправильный инструмент X')",
        "Другая конкретная проблема"
    ],
    "recommendations": [
        "Конкретная рекомендация с названием инструмента (например: 'Использовать file_manager для создания файла area.txt')",
        "Другая конкретная рекомендация"
    ],
    "approach_changes": [
        "Конкретное изменение подхода (например: 'Вместо создания отчёта создать рабочий Python файл')",
        "Другое изменение"
    ],
    "tool_suggestions": [
        "file_manager - для создания файлов с расчётами",
        "code_generator - для создания Python скриптов"
    ],
    "examples": [
        "Создать файл area.py с кодом: import math; r=5; area=math.pi*r**2; print(f'Площадь: {{area:.2f}}')",
        "Использовать file_manager с параметрами: filename='area.txt', content='A = π * r² = 78.54'"
    ],
    "priority": "critical"
}}

ТРЕБОВАНИЯ:
1. НЕ используй общие фразы типа "улучшить качество"
2. Называй КОНКРЕТНЫЕ инструменты из списка: {', '.join(available_tools)}
3. Давай РАБОЧИЕ примеры кода
4. Указывай ТОЧНЫЕ параметры для инструментов

JSON:"""
        
        try:
            response = self.llm_provider.complete(feedback_prompt)
            logger.debug(f"🔍 LLM ответ для фидбека: {response[:200]}...")
            
            feedback_data = self._parse_feedback_response(response)
            
            if not feedback_data:
                logger.warning("⚠️ LLM не вернул валидный JSON, используем fallback")
                return self._create_fallback_feedback(validation)
            
            feedback = ImprovementFeedback(
                issues=feedback_data.get("issues", []),
                recommendations=feedback_data.get("recommendations", []),
                approach_changes=feedback_data.get("approach_changes", []),
                tool_suggestions=feedback_data.get("tool_suggestions", []),
                examples=feedback_data.get("examples", []),
                priority=feedback_data.get("priority", "medium")
            )
            
            logger.info(f"🧠 LLM фидбек: {len(feedback.recommendations)} рекомендаций, {len(feedback.examples)} примеров")
            return feedback
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации фидбека: {e}")
            logger.info("🔄 Используем улучшенный fallback фидбек")
            return self._create_fallback_feedback(validation)
    
    def _parse_feedback_response(self, response: str) -> Dict[str, Any]:
        """Парсит ответ LLM с фидбеком"""
        
        try:
            import json
            
            # Извлекаем JSON из ответа
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("JSON не найден в ответе")
                
        except Exception as e:
            logger.warning(f"Ошибка парсинга фидбека: {e}")
            return {}
    
    def _create_fallback_feedback(self, validation: ValidationResult) -> ImprovementFeedback:
        """Создаёт конкретный фидбек если LLM не сработал"""
        
        # Анализируем проблемы валидации для создания конкретного фидбека
        issues = validation.issues or ["Результат не соответствует задаче"]
        
        # Создаём конкретные рекомендации на основе проблем
        concrete_recommendations = []
        concrete_tools = []
        concrete_examples = []
        
        for issue in issues:
            if "файл" in issue.lower() and "не создан" in issue.lower():
                concrete_recommendations.append("Использовать file_manager для создания файла с результатами")
                concrete_tools.append("file_manager - для создания файлов")
                concrete_examples.append("file_manager с параметрами: filename='result.txt', content='Готовый результат'")
            
            if "код" in issue.lower() or "скрипт" in issue.lower():
                concrete_recommendations.append("Использовать code_generator для создания Python скрипта")
                concrete_tools.append("code_generator - для генерации кода")
                concrete_examples.append("code_generator с параметрами: filename='script.py', language='python'")
        
        # Если нет конкретных рекомендаций, добавляем базовые
        if not concrete_recommendations:
            concrete_recommendations = [
                "Использовать file_manager для создания файла с результатом",
                "Проверить что файл действительно создаётся"
            ]
            concrete_tools = [
                "file_manager - для создания файлов",
                "system_tools - для проверки результатов"
            ]
            concrete_examples = [
                "file_manager: filename='output.txt', content='Конкретный результат'",
                "Создать файл с реальными данными, а не планом"
            ]
        
        return ImprovementFeedback(
            issues=issues,
            recommendations=concrete_recommendations,
            approach_changes=[
                "Создавать реальные файлы вместо планов",
                "Использовать конкретные инструменты для выполнения задачи"
            ],
            tool_suggestions=concrete_tools,
            examples=concrete_examples,
            priority="high"
        )
    
    async def _apply_improvements_to_agent(self, 
                                         agent: Any, 
                                         feedback: ImprovementFeedback,
                                         task: str) -> Any:
        """Применяет улучшения к агенту"""
        
        # Создаём улучшенные инструкции для агента
        improvement_instructions = self._create_improvement_instructions(feedback, task)
        
        # Обновляем агента с новыми инструкциями
        improved_agent = self._clone_agent_with_improvements(agent, improvement_instructions)
        
        logger.info(f"🔧 Агент улучшен с {len(feedback.recommendations)} рекомендациями")
        
        return improved_agent
    
    def _create_improvement_instructions(self, 
                                       feedback: ImprovementFeedback, 
                                       task: str) -> str:
        """Создаёт улучшенные инструкции для агента"""
        
        instructions = f"""
УЛУЧШЕННЫЕ ИНСТРУКЦИИ ДЛЯ ВЫПОЛНЕНИЯ ЗАДАЧИ:

ЗАДАЧА: {task}

КРИТИЧЕСКИЕ ПРОБЛЕМЫ ПРЕДЫДУЩЕЙ ПОПЫТКИ:
{chr(10).join([f"- {issue}" for issue in feedback.issues])}

ОБЯЗАТЕЛЬНЫЕ УЛУЧШЕНИЯ:
{chr(10).join([f"- {rec}" for rec in feedback.recommendations])}

ИЗМЕНЕНИЯ В ПОДХОДЕ:
{chr(10).join([f"- {change}" for change in feedback.approach_changes])}

РЕКОМЕНДУЕМЫЕ ИНСТРУМЕНТЫ:
{chr(10).join([f"- {tool}" for tool in feedback.tool_suggestions])}

ПРИМЕРЫ ПРАВИЛЬНОГО ВЫПОЛНЕНИЯ:
{chr(10).join([f"- {example}" for example in feedback.examples])}

ПРИОРИТЕТ: {feedback.priority.upper()}

ВАЖНО: 
1. Создавай ГОТОВЫЙ К ИСПОЛЬЗОВАНИЮ результат, а не планы или описания
2. Используй правильные инструменты для создания файлов
3. Проверяй что результат действительно решает поставленную задачу
4. Создавай рабочий контент, который пользователь может сразу использовать
"""
        
        return instructions
    
    def _clone_agent_with_improvements(self, original_agent: Any, improvements: str) -> Any:
        """Клонирует агента с улучшениями"""
        
        try:
            # Создаём копию агента с правильными параметрами
            improved_agent = type(original_agent)(
                role=getattr(original_agent, 'role', 'improved_agent'),
                subtask=getattr(original_agent, 'subtask', {'description': 'improved_task'})
            )
            
            # Добавляем улучшенные инструкции в subtask
            if hasattr(improved_agent, 'subtask') and isinstance(improved_agent.subtask, dict):
                # Добавляем улучшения в описание задачи
                original_description = improved_agent.subtask.get('description', '')
                improved_agent.subtask['description'] = improvements + "\n\n" + original_description
                improved_agent.subtask['improvement_instructions'] = improvements
            
            # Копируем инструменты
            if hasattr(original_agent, 'tools'):
                improved_agent.tools = getattr(original_agent, 'tools', [])
            
            # Копируем LLM провайдер
            if hasattr(original_agent, 'llm'):
                improved_agent.llm = getattr(original_agent, 'llm', None)
            
            return improved_agent
            
        except Exception as e:
            logger.error(f"❌ Ошибка клонирования агента: {e}")
            return original_agent


# Быстрая функция для итеративного улучшения
async def improve_agent_result(agent: Any,
                             task: str, 
                             bad_result: Dict[str, Any],
                             validation: ValidationResult,
                             smart_validator: Any) -> Tuple[Dict[str, Any], List[ImprovementAttempt]]:
    """
    Быстрая функция для итеративного улучшения агента
    """
    improver = IterativeImprovement()
    return await improver.improve_agent_iteratively(
        agent, task, bad_result, validation, smart_validator
    ) 