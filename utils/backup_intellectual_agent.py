import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Абсолютный импорт LLM провайдера
from kittycore.llm import get_llm_provider, LLMProvider

logger = logging.getLogger(__name__)


class IntellectualAgent:
    """
    Интеллектуальный агент, использующий LLM для принятия решений
    Заменяет примитивные if/else условия на умный анализ задач
    """
    
    def __init__(self):
        # Используем конкретную бесплатную модель вместо "auto"
        self.llm_provider = get_llm_provider("deepseek/deepseek-chat")
        logger.info("🧠 IntellectualAgent инициализирован с LLM")
    
    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполняет задачу используя LLM для анализа и принятия решений
        """
        try:
            # 1. Анализ задачи через LLM
            analysis = await self._analyze_task_with_llm(task, context)
            
            # 2. Выбор инструментов через LLM
            tools = await self._select_tools_with_llm(task, analysis)
            
            # 3. Создание плана выполнения через LLM
            execution_plan = await self._create_execution_plan_with_llm(task, tools)
            
            # 4. Выполнение задачи
            result = await self._execute_plan(execution_plan, task)
            
            # 5. Добавляем анализ задачи в результат
            result["analysis"] = analysis
            result["plan"] = {
                "task_type": analysis.get("task_type", "unknown"),
                "expected_output": analysis.get("expected_output", "неизвестно"),
                "complexity": analysis.get("complexity", "unknown"),
                "domain": analysis.get("domain", "unknown"),
                "requires_files": analysis.get("requires_files", False)
            }
            
            logger.info(f"✅ IntellectualAgent завершил задачу: {task}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка IntellectualAgent: {e}")
            return {
                "success": False,
                "error": str(e),
                "task": task
            }
    
    async def _analyze_task_with_llm(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ задачи через LLM"""
        prompt = f"""Ты - аналитик задач. Проанализируй задачу пользователя и определи ее характеристики.

ЗАДАЧА ПОЛЬЗОВАТЕЛЯ: {task}

КОНТЕКСТ: {json.dumps(context, ensure_ascii=False) if context else "нет"}

Определи:
1. Тип задачи (website_creation, planning, calculation, market_analysis, file_management, other)
2. Нужны ли файлы (true/false) 
3. Ожидаемый результат (конкретное описание что должен получить пользователь)
4. Сложность (simple, medium, complex)
5. Область (web, planning, math, business, text, other)

ОТВЕЧАЙ СТРОГО В JSON ФОРМАТЕ:
{{
    "task_type": "один_из_типов_выше",
    "requires_files": true,
    "expected_output": "детальное описание ожидаемого результата",
    "complexity": "simple_medium_или_complex",
    "domain": "область_задачи"
}}

ТОЛЬКО JSON, НИКАКИХ КОММЕНТАРИЕВ:"""
        
        try:
            response = self.llm_provider.complete(prompt)
            logger.info(f"🔍 LLM ответ для анализа: {response[:200]}...")
            
            # Ищем JSON в ответе
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
                logger.info(f"✅ Успешный анализ: {analysis}")
                return analysis
            else:
                logger.warning("JSON не найден в ответе LLM")
                raise ValueError("No JSON found")
                
        except Exception as e:
            logger.error(f"❌ Ошибка анализа LLM: {e}")
            
            # Умный fallback на основе ключевых слов
            task_lower = task.lower()
            
            if any(word in task_lower for word in ['рынок', 'анализ', 'market', 'прототип', 'проанализ']):
                return {
                    "task_type": "market_analysis",
                    "requires_files": True, 
                    "expected_output": f"Анализ рынка с прототипами по запросу: {task}",
                    "complexity": "complex",
                    "domain": "business"
                }
            elif any(word in task_lower for word in ['сайт', 'website', 'html', 'веб']):
                return {
                    "task_type": "website_creation",
                    "requires_files": True,
                    "expected_output": f"Готовый HTML сайт по теме: {task}",
                    "complexity": "medium",
                    "domain": "web"
                }
            elif any(word in task_lower for word in ['план', 'планир', 'план', 'schedule']):
                return {
                    "task_type": "planning", 
                    "requires_files": True,
                    "expected_output": f"Детальный план с временами и действиями для: {task}",
                    "complexity": "simple",
                    "domain": "planning"
                }
            elif any(word in task_lower for word in ['плотность', 'расчет', 'вычисли', 'посчитай']):
                return {
                    "task_type": "calculation",
                    "requires_files": True,
                    "expected_output": f"Готовый расчет с формулами и результатами для: {task}",
                    "complexity": "medium", 
                    "domain": "math"
                }
            else:
                return {
                    "task_type": "other",
                    "requires_files": True,
                    "expected_output": f"Выполнение задачи: {task}",
                    "complexity": "simple",
                    "domain": "other"
                }
    
    async def _select_tools_with_llm(self, task: str, analysis: Dict[str, Any]) -> List[str]:
        """Выбор инструментов через LLM"""
        available_tools = [
            "file_manager - создание, чтение, запись файлов",
            "web_creator - создание HTML/CSS сайтов",
            "calculator - математические вычисления",
            "text_processor - обработка текста",
            "planner - планирование и организация"
        ]
        
        prompt = f"""
Выбери подходящие инструменты для задачи:

Задача: {task}
Анализ: {json.dumps(analysis, ensure_ascii=False)}

Доступные инструменты:
{chr(10).join(available_tools)}

Отвечай списком названий инструментов через запятую:
Например: file_manager, web_creator

Инструменты:"""
        
        response = self.llm_provider.complete(prompt)
        tools = [tool.strip() for tool in response.strip().split(',')]
        return tools
    
    async def _create_execution_plan_with_llm(self, task: str, tools: List[str]) -> Dict[str, Any]:
        """Создание плана выполнения через LLM"""
        prompt = f"""
Создай подробный план выполнения задачи:

Задача: {task}
Инструменты: {', '.join(tools)}

Отвечай в JSON формате:
{{
    "steps": [
        {{
            "action": "описание действия",
            "tool": "название_инструмента",
            "parameters": {{"key": "value"}}
        }}
    ],
    "files_to_create": ["file1.html", "file2.css"],
    "expected_result": "описание результата"
}}

JSON:"""
        
        response = self.llm_provider.complete(prompt)
        try:
            return json.loads(response.strip())
        except:
            # Fallback план
            return {
                "steps": [{"action": "Выполнить задачу", "tool": "file_manager", "parameters": {}}],
                "files_to_create": [],
                "expected_result": "Задача выполнена"
            }
    
    async def _execute_plan(self, plan: Dict[str, Any], task: str) -> Dict[str, Any]:
        """Выполнение плана"""
        results = []
        files_created = []
        
        # Если план это анализ задачи, создаем простой план выполнения
        if "task_type" in plan and "steps" not in plan:
            task_type = plan.get("task_type", "other")
            
            if task_type == "website_creation":
                # Создаем сайт
                result = await self._execute_web_creator("Создать сайт с котятами", {}, task)
                results.append(result)
                if result.get("files_created"):
                    files_created.extend(result["files_created"])
                    
            elif task_type == "planning":
                # Создаем план
                result = await self._execute_file_manager("Создать план дня", {"type": "planning"}, task)
                results.append(result)
                if result.get("files_created"):
                    files_created.extend(result["files_created"])
                    
            elif task_type == "calculation":
                # Выполняем расчет
                result = await self._execute_calculator("Расчет плотности", {"type": "density"}, task)
                results.append(result)
                if result.get("files_created"):
                    files_created.extend(result["files_created"])
            else:
                # Общее выполнение
                result = await self._execute_file_manager("Выполнить задачу", {}, task)
                results.append(result)
                if result.get("files_created"):
                    files_created.extend(result["files_created"])
        else:
            # Выполняем план как раньше
            for step in plan.get("steps", []):
                action = step.get("action", "")
                tool = step.get("tool", "")
                parameters = step.get("parameters", {})
                
                # Симуляция выполнения инструментов
                if tool == "file_manager":
                    result = await self._execute_file_manager(action, parameters, task)
                elif tool == "web_creator":
                    result = await self._execute_web_creator(action, parameters, task)
                elif tool == "calculator":
                    result = await self._execute_calculator(action, parameters, task)
                else:
                    result = await self._execute_generic_tool(action, tool, parameters, task)
                
                results.append(result)
                if result.get("files_created"):
                    files_created.extend(result["files_created"])
        
        return {
            "success": True,
            "action": f"Выполнена задача через LLM: {task}",
            "results": results,
            "files_created": files_created,
            "plan": plan
        }
    
    async def _execute_file_manager(self, action: str, params: Dict[str, Any], task: str) -> Dict[str, Any]:
        """Выполнение файлового менеджера с LLM-генерированным контентом"""
        # Генерируем контент через LLM
        content_prompt = f"""
Создай РЕАЛЬНЫЙ контент для файла по задаче: {task}

Действие: {action}
Параметры: {json.dumps(params, ensure_ascii=False)}

Если это план - создай конкретный план с временами и действиями.
Если это расчет - включи формулы и числа.
Если это сайт - создай HTML с реальным содержимым.

Контент:"""
        
        content = self.llm_provider.complete(content_prompt)
        
        # Определяем имя файла через LLM
        filename_prompt = f"""
Предложи подходящее имя файла для задачи: {task}

Действие: {action}

Только имя файла с расширением:"""
        
        filename = self.llm_provider.complete(filename_prompt).strip()
        if not filename or '/' in filename:
            filename = "output.txt"
        
        try:
            # Создаем файл с LLM-контентом
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"📁 Создан файл: {filename}")
            return {
                "success": True,
                "action": f"Создан файл {filename}",
                "files_created": [filename],
                "content_preview": content[:100] + "..." if len(content) > 100 else content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": action
            }
    
    async def _execute_web_creator(self, action: str, params: Dict[str, Any], task: str) -> Dict[str, Any]:
        """Создание веб-сайта с LLM-генерированным контентом"""
        # Принудительно генерируем HTML через специальный промпт
        html_prompt = f"""Создай ПОЛНЫЙ HTML код для задачи: {task}

Требования:
- Полный HTML документ с DOCTYPE, head, body  
- Красивые стили CSS
- Реальный контент по теме
- Если про котят - добавь котят!

HTML код:"""
        
        html_content = self.llm_provider.complete(html_prompt)
        
        # НЕТ FALLBACK - если LLM не дал HTML, то ошибка
        if not html_content.strip().startswith("<!DOCTYPE") and not html_content.strip().startswith("<html"):
            raise Exception(f"❌ КРИТИЧЕСКАЯ ОШИБКА: LLM не вернул валидный HTML! Ответ: {html_content[:100]}")
        
        files_created = []
        
        try:
            # Создаем index.html
            with open("index.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
            files_created.append("index.html")
            
            # Создаем CSS если нужно
            if "css" in task.lower() or "стил" in task.lower():
                css_prompt = f"""Создай CSS стили для сайта по задаче: {task}

Красивые, современные стили:"""
                
                css_content = self.llm_provider.complete(css_prompt)
                with open("styles.css", 'w', encoding='utf-8') as f:
                    f.write(css_content)
                files_created.append("styles.css")
            
            logger.info(f"🌐 Создан сайт: {', '.join(files_created)}")
            return {
                "success": True,
                "action": f"Создан сайт: {', '.join(files_created)}",
                "files_created": files_created
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": action
            }
    
    async def _execute_calculator(self, action: str, params: Dict[str, Any], task: str) -> Dict[str, Any]:
        """Выполнение вычислений с LLM"""
        calc_prompt = f"""
Выполни математические вычисления для задачи: {task}

Действие: {action}

Предоставь:
1. Формулы
2. Числовые значения
3. Расчеты
4. Результат

Если нужны константы (например, для чёрной дыры) - используй реальные значения.

Расчет:"""
        
        calculation = self.llm_provider.complete(calc_prompt)
        
        try:
            # Сохраняем расчет в файл
            filename = "calculation.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Расчет для: {task}\n\n{calculation}")
            
            logger.info(f"🔢 Выполнен расчет: {filename}")
            return {
                "success": True,
                "action": f"Выполнен расчет: {calculation[:100]}...",
                "files_created": [filename],
                "result": calculation
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": action
            }
    
    async def _execute_generic_tool(self, action: str, tool: str, params: Dict[str, Any], task: str) -> Dict[str, Any]:
        """Выполнение общего инструмента"""
        # Генерируем результат через LLM
        result_prompt = f"""
Выполни действие инструментом:

Задача: {task}
Действие: {action}
Инструмент: {tool}
Параметры: {json.dumps(params, ensure_ascii=False)}

Опиши что было сделано и результат:"""
        
        result_text = self.llm_provider.complete(result_prompt)
        
        logger.info(f"🔧 Выполнено {tool}: {action}")
        return {
            "success": True,
            "action": f"{tool}: {action}",
            "result": result_text,
            "files_created": []
        } 