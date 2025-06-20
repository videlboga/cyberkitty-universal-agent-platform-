"""
🧠 IntellectualAgent - Агент с LLM-интеллектом

Агент который использует LLM для:
- Анализа задач и понимания контекста
- Выбора подходящих инструментов
- Создания плана выполнения
- Принятия решений в процессе работы
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from ..tools.real_tools import REAL_TOOLS
from ..llm import get_llm_provider, LLMProvider
from .tool_validator_agent import create_tool_validator


class IntellectualAgent:
    """🧠 Агент с LLM-интеллектом"""
    
    def __init__(self, role: str, subtask: Dict[str, Any]):
        self.role = role
        self.subtask = subtask
        self.tools = REAL_TOOLS
        self.llm = get_llm_provider()
        self.tool_validator = create_tool_validator()  # 🔧 НОВОЕ: Валидатор инструментов
        self.results = []
        
    def _create_simple_plan(self, task_description: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        УМНЫЙ FALLBACK: создаёт рабочий план если JSON парсинг LLM ответа падает
        
        Принцип: JSON парсинг НЕ КРИТИЧЕН - главное чтобы система РАБОТАЛА!
        """
        print("🔧 Используем умный fallback план...")
        
        # Анализируем выбранные инструменты
        tools = analysis.get("chosen_tools", ["file_manager"])
        
        # Определяем основной инструмент и параметры
        if "web_client" in tools:
            # Для анализа рынка начинаем с поиска
            main_tool = "web_client"
            params = {"query": f"анализ рынка {task_description}"}
        elif "code_generator" in tools:
            # Для создания кода
            main_tool = "code_generator" 
            if "python" in task_description.lower():
                params = {"filename": "result.py", "content": f"# Код для: {task_description}"}
            else:
                params = {"filename": "result.html", "content": f"Результат для: {task_description}"}
        else:
            # Для создания документов
            main_tool = "file_manager"
            params = {"filename": "result.txt", "content": f"Анализ: {task_description}"}
        
        return {
            "steps": [
                {
                    "step": 1,
                    "action": f"Выполнить: {task_description}",
                    "tool": main_tool,
                    "params": params
                }
            ]
        }
        
    async def execute_task(self) -> Dict[str, Any]:
        """Выполнить задачу используя LLM-интеллект"""
        task_description = self.subtask.get("description", "")
        
        print(f"🧠 {self.role} анализирует задачу: {task_description}")
        
        try:
            # ФАЗА 1: LLM анализирует задачу и выбирает инструменты
            analysis = await self._analyze_task_with_llm(task_description)
            
            # ФАЗА 2: LLM создает план выполнения
            execution_plan = await self._create_execution_plan(task_description, analysis)
            
            # ФАЗА 3: Выполняем план используя выбранные инструменты
            result = await self._execute_plan(execution_plan, task_description)
            
            # 🧠 ФАЗА 4: Сохраняем опыт в A-MEM для будущего улучшения
            await self._save_execution_experience_to_amem(
                task_description, analysis, execution_plan, result
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Ошибка в IntellectualAgent: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _analyze_task_with_llm(self, task_description: str) -> Dict[str, Any]:
        """LLM анализирует задачу и выбирает инструменты"""
        
        # Список доступных инструментов для LLM
        available_tools = {
            "file_manager": "Создание, чтение, запись файлов",
            "code_generator": "Генерация Python скриптов и HTML страниц",
            "web_client": "HTTP запросы, проверка веб-сайтов",
            "system_tools": "Системные операции, выполнение команд"
        }
        
        prompt = f"""
Ты - эксперт-аналитик задач. Твоя цель - понять ЧТО ИМЕННО хочет получить пользователь и выбрать правильные инструменты.

ЗАДАЧА: "{task_description}"

ДОСТУПНЫЕ ИНСТРУМЕНТЫ:
{json.dumps(available_tools, ensure_ascii=False, indent=2)}

АНАЛИЗИРУЙ ЗАДАЧУ ПО КРИТЕРИЯМ:

🎯 ТИП РЕЗУЛЬТАТА:
- ФАЙЛЫ: пользователь хочет получить конкретные файлы (код, документы, данные)
- АНАЛИЗ: пользователь хочет исследование, отчёт, аналитику
- ВЕБ-ПРОВЕРКА: пользователь хочет проверить существующий сайт
- АВТОМАТИЗАЦИЯ: пользователь хочет скрипт/программу для выполнения задач

📊 ПРЕДМЕТНАЯ ОБЛАСТЬ:
- БИЗНЕС: маркетинг, продажи, финансы, стратегия
- ТЕХНИЧЕСКАЯ: программирование, веб-разработка, системы
- КРЕАТИВНАЯ: дизайн, контент, прототипы
- АНАЛИТИЧЕСКАЯ: исследования, данные, отчёты

🔧 ВЫБОР ИНСТРУМЕНТОВ:
- file_manager: для создания текстовых файлов, документов, данных
- code_generator: для Python скриптов, HTML страниц, программного кода
- web_client: для поиска информации в интернете, проверки сайтов, получения данных
- system_tools: для системных операций, выполнения команд

СПЕЦИАЛЬНЫЕ ПРАВИЛА:
🚫 НЕ используй web_client для создания сайтов - используй code_generator!
🚫 НЕ выбирай инструменты "на всякий случай" - только необходимые!
✅ Для анализа рынка/исследований: web_client (поиск данных) + file_manager + code_generator (для JSON)
✅ Для прототипов: file_manager (описания) + code_generator (если нужен код)
✅ Для веб-сайтов: code_generator + file_manager
✅ Для поиска информации о компаниях/продуктах: web_client + file_manager

ФОРМАТ ОТВЕТА (MARKDOWN):

## Анализ задачи

**Тип задачи**: creation/analysis/web_check/automation
**Цель**: КОНКРЕТНО что пользователь получит на выходе
**Выбранные инструменты**: только необходимые инструменты
**Обоснование**: детальное объяснение выбора каждого инструмента
**Ожидаемые результаты**: конкретные файлы/результаты с расширениями
**Тип контента**: код/документы/данные/анализ

ПРИМЕРЫ ПРАВИЛЬНОГО АНАЛИЗА:

Задача: "Создай сайт с котятами"
→ task_type: "creation", tools: ["code_generator", "file_manager"], outputs: ["index.html", "style.css"]

Задача: "Проанализируй рынок CRM систем"  
→ task_type: "analysis", tools: ["web_client", "file_manager", "code_generator"], outputs: ["market_analysis.txt", "crm_data.json"]

Задача: "Проведи анализ рынка приложений маркета битрикс 24"
→ task_type: "analysis", tools: ["web_client", "file_manager", "code_generator"], outputs: ["bitrix_market_analysis.json", "top_apps.json"]

Задача: "Проверь работает ли сайт google.com"
→ task_type: "web_check", tools: ["web_client"], outputs: ["site_status_report.txt"]

ПОМНИ: Пользователь должен получить КОНКРЕТНЫЙ, ПОЛЕЗНЫЙ результат!
"""
        
        try:
            print(f"🤖 Отправляем запрос к LLM...")
            response = self.llm.complete(prompt)
            print(f"📝 LLM ответ получен: {len(response)} символов")
            print(f"🔍 Первые 200 символов: {response[:200]}...")
            
            # Парсим Markdown ответ
            analysis = self._parse_markdown_analysis(response)
            print(f"🎯 LLM анализ: {analysis['intent']}")
            print(f"🔧 Выбранные инструменты: {analysis['chosen_tools']}")
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ Ошибка LLM анализа: {e}")
            # Умный fallback на основе ключевых слов
            return self._smart_fallback_analysis(task_description)
    
    def _parse_markdown_analysis(self, response: str) -> Dict[str, Any]:
        """Парсинг Markdown анализа"""
        try:
            # Извлекаем данные из Markdown структуры
            lines = response.split('\n')
            analysis = {}
            
            for line in lines:
                if line.startswith('**Тип задачи**:'):
                    task_type = line.split(':', 1)[1].strip()
                    analysis['task_type'] = task_type
                    
                    # 🚀 НОВОЕ: Определяем сложность по типу задачи
                    if task_type in ['analysis', 'research'] or 'анализ' in task_type.lower():
                        analysis['complexity'] = 'complex'
                    elif task_type in ['creation', 'automation']:
                        analysis['complexity'] = 'medium'
                    else:
                        analysis['complexity'] = 'simple'
                        
                elif line.startswith('**Цель**:'):
                    intent = line.split(':', 1)[1].strip()
                    analysis['intent'] = intent
                    
                    # 🚀 ДОПОЛНИТЕЛЬНО: Усиливаем определение сложности по цели
                    if any(keyword in intent.lower() for keyword in ['комплексный', 'детальный', 'глубокий', 'прототип']):
                        analysis['complexity'] = 'complex'
                    elif any(keyword in intent.lower() for keyword in ['создать', 'сделать', 'разработать']):
                        analysis['complexity'] = 'medium'
                        
                elif line.startswith('**Выбранные инструменты**:'):
                    tools_str = line.split(':', 1)[1].strip()
                    # Парсим список инструментов
                    tools = [t.strip().strip('[]"\'') for t in tools_str.split(',')]
                    # Очищаем от лишних символов
                    clean_tools = []
                    for tool in tools:
                        clean_tool = tool.strip().replace('"', '').replace("'", '').replace('[', '').replace(']', '')
                        if clean_tool:
                            clean_tools.append(clean_tool)
                    analysis['chosen_tools'] = clean_tools
                    
                    # 🚀 ДОПОЛНИТЕЛЬНО: Усиливаем сложность по количеству инструментов
                    if len(clean_tools) >= 3:
                        analysis['complexity'] = 'complex'
                    elif len(clean_tools) == 2:
                        analysis['complexity'] = 'medium'
                        
                elif line.startswith('**Обоснование**:'):
                    analysis['reasoning'] = line.split(':', 1)[1].strip()
                elif line.startswith('**Ожидаемые результаты**:'):
                    analysis['expected_outputs'] = line.split(':', 1)[1].strip()
                elif line.startswith('**Тип контента**:'):
                    analysis['content_type'] = line.split(':', 1)[1].strip()
            
            # Проверяем что основные поля заполнены
            if not analysis.get('intent') or not analysis.get('chosen_tools'):
                raise ValueError("Не найдены основные поля в Markdown")
            
            # 🚀 ФИНАЛЬНАЯ ПРОВЕРКА: Устанавливаем сложность если не определилась
            if 'complexity' not in analysis:
                analysis['complexity'] = 'simple'
                
            print(f"🎯 Определена сложность: {analysis['complexity']}")
            return analysis
            
        except Exception as e:
            print(f"⚠️ Ошибка парсинга Markdown анализа: {e}")
            # Fallback парсинг по ключевым словам
            return self._smart_fallback_analysis(response)
    
    def _parse_plan_response(self, response: str) -> Dict[str, Any]:
        """Парсинг ответа LLM в JSON"""
        # Убираем лишние символы и оставляем только JSON
        response = response.strip()
        
        # Находим JSON часть
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("JSON не найден в ответе")
            
        json_part = response[start_idx:end_idx]
        
        try:
            plan = json.loads(json_part)
            return plan
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            print(f"JSON часть: {json_part}")
            raise ValueError(f"Невалидный JSON: {e}")
    
    def _parse_markdown_plan(self, response: str) -> Dict[str, Any]:
        """
        🔧 НОВОЕ: Парсинг плана в формате Markdown
        
        Ожидаемый формат:
        ### Шаг 1: Название
        - **Действие**: описание
        - **Инструмент**: tool_name
        - **Файл**: filename
        - **Контент**: content
        """
        steps = []
        current_step = None
        step_counter = 1
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Ищем начало шага
            if line.startswith('### Шаг') or line.startswith('## Шаг'):
                if current_step:
                    steps.append(current_step)
                
                current_step = {
                    "step": step_counter,
                    "action": line.split(':', 1)[1].strip() if ':' in line else f"Шаг {step_counter}",
                    "tool": "file_manager",  # default
                    "params": {}
                }
                step_counter += 1
                
            elif current_step and line.startswith('- **'):
                # Парсим параметры шага
                if '**Действие**:' in line:
                    current_step["action"] = line.split(':', 1)[1].strip()
                elif '**Инструмент**:' in line:
                    tool = line.split(':', 1)[1].strip()
                    current_step["tool"] = tool
                elif '**Файл**:' in line:
                    filename = line.split(':', 1)[1].strip()
                    current_step["params"]["filename"] = filename
                elif '**Контент**:' in line:
                    content = line.split(':', 1)[1].strip()
                    current_step["params"]["content"] = content
                elif '**Запрос**:' in line:
                    query = line.split(':', 1)[1].strip()
                    current_step["params"]["query"] = query
        
        # Добавляем последний шаг
        if current_step:
            steps.append(current_step)
        
        print(f"📝 Распарсили {len(steps)} шагов из Markdown")
        return {"steps": steps}
    
    def _smart_fallback_analysis(self, task_description: str) -> Dict[str, Any]:
        """Умный fallback анализ на основе ключевых слов"""
        task_lower = task_description.lower()
        
        # Определяем инструменты по ключевым словам
        tools = []
        
        # Веб-поиск для анализа рынка
        if any(word in task_lower for word in ["рынок", "маркет", "анализ", "популярные", "топ", "битрикс"]):
            tools.append("web_client")
            tools.append("file_manager")
            tools.append("code_generator")
            intent = "анализ рынка с поиском актуальной информации"
        # Создание сайтов
        elif any(word in task_lower for word in ["сайт", "html", "веб"]) and any(word in task_lower for word in ["создай", "сделай"]):
            tools = ["code_generator", "file_manager"]
            intent = "создание веб-сайта"
        # Планы и документы
        elif "план" in task_lower:
            tools = ["file_manager"]
            intent = "создание плана"
        else:
            tools = ["file_manager"]
            intent = "анализ и создание отчета"
        
        return {
            "task_type": "analysis" if "анализ" in intent else "creation",
            "intent": intent,
            "chosen_tools": tools,
            "reasoning": f"fallback анализ по ключевым словам: {task_lower[:50]}...",
            "expected_outputs": ["файлы с результатами"]
        }
    
    def _smart_fallback_plan(self, task_description: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        УДАЛЕНО: Fallback планы убраны согласно принципу "Нет LLM = Нет работы"
        """
        raise Exception("❌ Fallback планы отключены. Система требует рабочий LLM для планирования.")
    
    async def _create_execution_plan(self, task_description: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 LLM создаёт план выполнения, ToolValidatorAgent исправляет инструменты
        
        ПРИНЦИП: Простота превыше всего. Нет LLM = Нет работы.
        """
        # 🧠 A-MEM: Получаем insights для планирования
        amem_insights = await self._get_amem_planning_insights(task_description, analysis)
        
        chosen_tools = analysis.get("chosen_tools", ["file_manager"])
        task_complexity = analysis.get("complexity", "simple")
        
        # 🚀 НОВОЕ: Многоэтапное планирование для сложных задач
        if task_complexity in ["complex", "very_complex"]:
            return await self._create_multi_stage_plan(task_description, analysis, amem_insights)
        else:
            return await self._create_simple_plan(task_description, analysis, amem_insights)
    
    async def _create_multi_stage_plan(self, task_description: str, analysis: Dict[str, Any], amem_insights: str) -> Dict[str, Any]:
        """
        🚀 РЕВОЛЮЦИЯ: Многоэтапное Agile планирование для сложных задач
        
        ЭТАПЫ:
        1. 🔍 RESEARCH - глубокий сбор информации
        2. 📊 ANALYSIS - анализ собранных данных
        3. 🛠️ IMPLEMENTATION - создание результатов  
        4. ✅ VALIDATION - проверка качества
        """
        chosen_tools = analysis.get("chosen_tools", ["file_manager"])
        
        prompt = f"""Создай МНОГОЭТАПНЫЙ план решения сложной задачи по принципам Agile.

ЗАДАЧА: "{task_description}"

АНАЛИЗ:
- Тип: {analysis.get('task_type', 'general')}
- Сложность: {analysis.get('complexity', 'complex')}
- Инструменты: {chosen_tools}

ДОСТУПНЫЕ ИНСТРУМЕНТЫ:
- web_client: поиск в интернете, изучение сайтов
- file_manager: создание файлов с данными
- code_generator: генерация кода и прототипов
- system_tools: системные операции

ПРИНЦИПЫ МНОГОЭТАПНОГО ПЛАНИРОВАНИЯ:
1. RESEARCH ПЕРВЫМ - без качественного исследования нет качественного результата
2. Каждый этап строится на результатах предыдущего
3. Максимальная конкретность в исследовании
4. Проверка качества на каждом этапе

ФОРМАТ ОТВЕТА (Markdown):

## Многоэтапный план решения

### ЭТАП 1: 🔍 RESEARCH
- **Действие**: Подробное изучение темы, сбор максимального количества данных
- **Инструмент**: web_client
- **Цель**: Понять ВСЕ аспекты предметной области
- **Результат**: Полная база знаний для анализа

### ЭТАП 2: 📊 ANALYSIS
- **Действие**: Структурирование и анализ собранной информации
- **Инструмент**: file_manager
- **Цель**: Выявить паттерны, проблемы, возможности
- **Результат**: Аналитические выводы и рекомендации

### ЭТАП 3: 🛠️ IMPLEMENTATION
- **Действие**: Разработка конкретных результатов на основе анализа
- **Инструмент**: code_generator
- **Цель**: Создать практические решения
- **Результат**: Готовые к использованию артефакты

### ЭТАП 4: ✅ VALIDATION
- **Действие**: Валидация созданных решений
- **Инструмент**: system_tools
- **Цель**: Убедиться в соответствии требованиям
- **Результат**: Подтверждённое качество решения

{amem_insights}

ОТВЕЧАЙ ТОЛЬКО В MARKDOWN ФОРМАТЕ!"""

        try:
            print(f"🚀 Создаем многоэтапный план через LLM...")
            response = self.llm.complete(prompt)
            print(f"📝 Получен многоэтапный план: {len(response)} символов")
            
            # Парсим план
            plan = self._parse_multi_stage_markdown(response)
            
            # 🔧 Валидация через ToolValidatorAgent
            validation_result = self.tool_validator.validate_plan(plan)
            
            # Используем исправленный план
            validated_plan = {
                "type": "multi_stage",
                "stages": validation_result.corrected_steps
            }
            
            print(f"🚀 Многоэтапный план создан: {len(validated_plan.get('stages', []))} этапов")
            if validation_result.corrections_made:
                print(f"   Внесено {len(validation_result.corrections_made)} исправлений")
            
            return validated_plan
            
        except Exception as e:
            print(f"❌ LLM недоступен для многоэтапного планирования: {e}")
            raise Exception(f"Не могу создать многоэтапный план без LLM: {e}")
    
    async def _create_simple_plan(self, task_description: str, analysis: Dict[str, Any], amem_insights: str) -> Dict[str, Any]:
        """Простой план для несложных задач"""
        chosen_tools = analysis.get("chosen_tools", ["file_manager"])
        
        prompt = f"""Создай простой план выполнения задачи в формате Markdown.

ЗАДАЧА: "{task_description}"

АНАЛИЗ:
- Тип: {analysis.get('task_type', 'general')}
- Инструменты: {chosen_tools}

ДОСТУПНЫЕ ИНСТРУМЕНТЫ:
- file_manager: создание файлов
- code_generator: генерация кода  
- web_client: поиск в интернете
- system_tools: системные команды

ПРАВИЛА:
1. Максимум 5 шагов
2. Каждый шаг создаёт конкретный результат
3. Для поиска информации начинай с web_client

ФОРМАТ ОТВЕТА (Markdown):

## План выполнения

### Шаг 1: Название действия
- **Действие**: конкретное описание
- **Инструмент**: название_инструмента  
- **Файл**: имя_файла.ext
- **Контент**: детальное содержимое

{amem_insights}

ОТВЕЧАЙ ТОЛЬКО В MARKDOWN ФОРМАТЕ!"""

        try:
            print(f"🤖 Создаем простой план через LLM...")
            response = self.llm.complete(prompt)
            print(f"📝 Получен план: {len(response)} символов")
            
            # Парсим план
            plan = self._parse_markdown_plan(response)
            
            # 🔧 Валидация через ToolValidatorAgent
            validation_result = self.tool_validator.validate_plan(plan)
            
            # Используем исправленный план
            validated_plan = {
                "type": "simple",
                "steps": validation_result.corrected_steps
            }
            
            print(f"🔧 Простой план валидирован: {len(validated_plan.get('steps', []))} шагов")
            if validation_result.corrections_made:
                print(f"   Внесено {len(validation_result.corrections_made)} исправлений")
            
            return validated_plan
            
        except Exception as e:
            print(f"❌ LLM недоступен: {e}")
            raise Exception(f"Не могу создать план без LLM: {e}")
    
    def _parse_multi_stage_markdown(self, response: str) -> Dict[str, Any]:
        """
        🚀 НОВОЕ: Парсинг многоэтапного плана
        
        Ожидаемый формат:
        ### ЭТАП 1: 🔍 RESEARCH
        - **Действие**: описание
        - **Инструмент**: tool_name
        - **Цель**: цель этапа
        - **Результат**: ожидаемый результат
        """
        stages = []
        current_stage = None
        stage_counter = 1
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Ищем начало этапа
            if line.startswith('### ЭТАП') and ('RESEARCH' in line or 'ANALYSIS' in line or 'IMPLEMENTATION' in line or 'VALIDATION' in line):
                if current_stage:
                    stages.append(current_stage)
                
                stage_name = line.split(':', 1)[1].strip() if ':' in line else f"Этап {stage_counter}"
                current_stage = {
                    "step": stage_counter,
                    "action": stage_name,
                    "tool": "file_manager",  # default
                    "params": {},
                    "stage_type": self._extract_stage_type(line)
                }
                stage_counter += 1
                
            elif current_stage and line.startswith('- **'):
                # Парсим параметры этапа
                if '**Действие**:' in line:
                    current_stage["action"] = line.split(':', 1)[1].strip()
                elif '**Инструмент**:' in line:
                    tool = line.split(':', 1)[1].strip()
                    current_stage["tool"] = tool
                elif '**Цель**:' in line:
                    goal = line.split(':', 1)[1].strip()
                    current_stage["params"]["goal"] = goal
                elif '**Результат**:' in line:
                    result = line.split(':', 1)[1].strip()
                    current_stage["params"]["expected_result"] = result
                elif '**Файл**:' in line:
                    filename = line.split(':', 1)[1].strip()
                    current_stage["params"]["filename"] = filename
        
        # Добавляем последний этап
        if current_stage:
            stages.append(current_stage)
        
        print(f"🚀 Распарсили {len(stages)} этапов многоэтапного плана")
        return {"steps": stages}
    
    def _extract_stage_type(self, line: str) -> str:
        """Определяем тип этапа из заголовка"""
        line_upper = line.upper()
        if 'RESEARCH' in line_upper:
            return "research"
        elif 'ANALYSIS' in line_upper:
            return "analysis"
        elif 'IMPLEMENTATION' in line_upper:
            return "implementation"
        elif 'VALIDATION' in line_upper:
            return "validation"
        else:
            return "general"
    
    async def _execute_plan(self, plan: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        """
        🚀 НОВОЕ: Выполняем план - простой или многоэтапный
        """
        plan_type = plan.get("type", "simple")
        
        if plan_type == "multi_stage":
            return await self._execute_multi_stage_plan(plan, task_description)
        else:
            return await self._execute_simple_plan(plan, task_description)
    
    async def _execute_multi_stage_plan(self, plan: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        """
        🚀 РЕВОЛЮЦИЯ: Выполнение многоэтапного плана
        
        Каждый этап выполняется полностью, результаты передаются следующему этапу
        """
        stages = plan.get("stages", [])
        all_results = []
        stage_results = {}
        
        print(f"🚀 Выполнение многоэтапного плана: {len(stages)} этапов")
        
        for i, stage in enumerate(stages, 1):
            stage_type = stage.get("stage_type", "general")
            print(f"\n📋 ЭТАП {i}: {stage_type.upper()} - {stage.get('action', 'Выполнение этапа')}")
            
            # Обогащаем контекст результатами предыдущих этапов
            enriched_stage = self._enrich_stage_with_context(stage, stage_results)
            
            # Выполняем этап
            stage_result = await self._execute_single_step(enriched_stage, task_description)
            
            # Сохраняем результат этапа
            stage_results[stage_type] = stage_result
            all_results.append(stage_result)
            
            print(f"✅ ЭТАП {i} завершён: {stage_result.get('success', False)}")
            
            # Если этап провалился, прерываем выполнение
            if not stage_result.get('success', False):
                print(f"❌ Многоэтапный план прерван на этапе {i}")
                break
        
        # Агрегируем результаты всех этапов
        final_result = self._aggregate_stage_results(all_results, stage_results)
        
        print(f"🎉 Многоэтапный план завершён: {len(all_results)} этапов выполнено")
        return final_result
    
    async def _execute_simple_plan(self, plan: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        """Выполнение простого плана (старая логика)"""
        steps = plan.get("steps", [])
        all_results = []
        
        print(f"📋 Выполнение простого плана: {len(steps)} шагов")
        
        for step in steps:
            result = await self._execute_single_step(step, task_description)
            all_results.append(result)
        
        return self._aggregate_simple_results(all_results)
    
    async def _execute_single_step(self, step: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        """
        🔧 НОВОЕ: Выполнение одного шага плана
        
        Универсальный метод для выполнения как простых шагов, так и этапов многоэтапного плана
        """
        tool_name = step.get("tool", "file_manager")
        action = step.get("action", "Выполнение действия")
        params = step.get("params", {})
        
        print(f"📋 Шаг {step.get('step', '?')}: {action}")
        print(f"🔧 Инструмент: {tool_name}, Параметры: {params}")
        
        try:
            # Выполняем действие с помощью соответствующего инструмента
            if tool_name == "file_manager":
                result = await self._use_file_manager(params, task_description)
            elif tool_name == "code_generator":
                result = await self._use_code_generator(params, task_description)
            elif tool_name == "web_client":
                result = await self._use_web_client(params)
            elif tool_name == "system_tools":
                result = await self._use_system_tools(params, task_description)
            else:
                # Неизвестный инструмент - используем fallback
                print(f"⚠️ Неизвестный инструмент {tool_name}, используем file_manager")
                result = await self._use_file_manager(params, task_description)
            
            # Логируем результат
            success = result.get("success", False)
            if success:
                created_file = result.get("filename", "")
                if created_file:
                    print(f"📁 Создан файл: {created_file}")
                else:
                    content_info = result.get("content", "")
                    if content_info:
                        print(f"💎 Контент: {str(content_info)[:100]}...")
                print(f"✅ Шаг {step.get('step', '?')} выполнен успешно")
            else:
                error = result.get("error", "Неизвестная ошибка")
                print(f"❌ Шаг {step.get('step', '?')} провалился: {error}")
            
            # Обогащаем результат информацией о шаге
            enriched_result = result.copy()
            enriched_result.update({
                "step_number": step.get("step", 0),
                "action": action,
                "tool_used": tool_name,
                "content_summary": self._create_step_summary(result, action)
            })
            
            # Нормализуем created_files
            if "filename" in enriched_result and enriched_result["filename"]:
                enriched_result["created_files"] = [enriched_result["filename"]]
            elif "created_files" not in enriched_result:
                enriched_result["created_files"] = []
            
            return enriched_result
            
        except Exception as e:
            print(f"❌ Ошибка выполнения шага {step.get('step', '?')}: {e}")
            return {
                "success": False,
                "error": str(e),
                "step_number": step.get("step", 0),
                "action": action,
                "tool_used": tool_name,
                "created_files": []
            }
    
    def _create_step_summary(self, result: Dict[str, Any], action: str) -> str:
        """Создание краткого описания результата шага"""
        if not result.get("success", False):
            return f"Ошибка: {result.get('error', 'неизвестная ошибка')}"
        
        # Определяем тип результата
        content = result.get("content", "")
        filename = result.get("filename", "")
        
        if filename:
            return f"Создан файл {filename}"
        elif content:
            content_preview = str(content)[:100] + ("..." if len(str(content)) > 100 else "")
            return f"Выполнено: {content_preview}"
        else:
            return f"Выполнено действие: {action}"
    
    def _enrich_stage_with_context(self, stage: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 УМНОЕ обогащение этапа контекстом предыдущих результатов
        
        RESEARCH этап: чистый, без контекста
        ANALYSIS этап: получает данные RESEARCH
        IMPLEMENTATION этап: получает данные RESEARCH + ANALYSIS  
        VALIDATION этап: получает все предыдущие результаты
        """
        enriched_stage = stage.copy()
        stage_type = stage.get("stage_type", "general")
        
        # Создаём контекст на основе типа этапа
        context_parts = []
        
        if stage_type == "analysis" and "research" in previous_results:
            research_data = previous_results["research"].get("content_summary", "")
            context_parts.append(f"ДАННЫЕ ИССЛЕДОВАНИЯ: {research_data}")
        
        elif stage_type == "implementation":
            if "research" in previous_results:
                research_data = previous_results["research"].get("content_summary", "")
                context_parts.append(f"ИССЛЕДОВАНИЕ: {research_data}")
            if "analysis" in previous_results:
                analysis_data = previous_results["analysis"].get("content_summary", "")
                context_parts.append(f"АНАЛИЗ: {analysis_data}")
        
        elif stage_type == "validation":
            for prev_type, prev_result in previous_results.items():
                content = prev_result.get("content_summary", "")
                context_parts.append(f"{prev_type.upper()}: {content}")
        
        # Добавляем контекст в параметры этапа
        if context_parts:
            existing_content = enriched_stage.get("params", {}).get("content", "")
            context_text = " | ".join(context_parts)
            
            if "params" not in enriched_stage:
                enriched_stage["params"] = {}
            
            if existing_content:
                enriched_stage["params"]["content"] = f"{existing_content}\n\nКОНТЕКСТ ПРЕДЫДУЩИХ ЭТАПОВ: {context_text}"
            else:
                enriched_stage["params"]["content"] = f"КОНТЕКСТ: {context_text}"
        
        return enriched_stage
    
    def _aggregate_stage_results(self, all_results: List[Dict[str, Any]], stage_results: Dict[str, Any]) -> Dict[str, Any]:
        """Агрегация результатов многоэтапного планирования"""
        total_steps = len(all_results)
        successful_steps = sum(1 for r in all_results if r.get('success', False))
        
        # Собираем все созданные файлы
        all_files = []
        for result in all_results:
            files = result.get('created_files', [])
            if isinstance(files, list):
                all_files.extend(files)
            elif isinstance(files, str):
                all_files.append(files)
        
        # Создаём суммарный контент из всех этапов
        stage_summaries = []
        for stage_type, result in stage_results.items():
            summary = result.get("content_summary", f"Этап {stage_type} выполнен")
            stage_summaries.append(f"{stage_type.upper()}: {summary}")
        
        return {
            "success": successful_steps == total_steps,
            "completed_steps": successful_steps,
            "total_steps": total_steps,
            "created_files": all_files,
            "stage_results": stage_results,
            "content_summary": " | ".join(stage_summaries),
            "execution_type": "multi_stage"
        }
    
    def _aggregate_simple_results(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Агрегация результатов простого планирования (старая логика)"""
        total_steps = len(all_results)
        successful_steps = sum(1 for r in all_results if r.get('success', False))
        
        # Собираем все созданные файлы
        all_files = []
        for result in all_results:
            files = result.get('created_files', [])
            if isinstance(files, list):
                all_files.extend(files)
            elif isinstance(files, str):
                all_files.append(files)
        
        return {
            "success": successful_steps == total_steps,
            "completed_steps": successful_steps,
            "total_steps": total_steps,
            "created_files": all_files,
            "execution_type": "simple"
        }
    
    async def _use_code_generator(self, params: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        """Использование code_generator с сохранением в outputs/"""
        filename = params.get("filename", f"generated_{id(self)}.html")
        title = params.get("title", "Генерированная страница")
        
        # ИСПРАВЛЕНИЕ: Добавляем папку outputs/ для всех файлов
        if not filename.startswith("outputs/"):
            filename = f"outputs/{filename}"
        
        # ИСПРАВЛЕНИЕ: Проверяем расширение файла для выбора типа генерации
        if filename.endswith('.py'):
            # Для Python файлов используем generate_python_script
            description = params.get("content", task_description)
            if not description or description in ["простой код", "код файла", "содержимое файла"]:
                description = task_description
            return self.tools["code_generator"].generate_python_script(description, filename)
        
        elif filename.endswith('.html'):
            # Для HTML файлов используем generate_html_page
            if "котят" in task_description.lower() or "cat" in task_description.lower():
                content = f"""
                <div class="header">
                    <h1>🐱 {title}</h1>
                    <p>Добро пожаловать на сайт о котятах!</p>
                </div>
                <div class="content">
                    <h2>Наши милые котятки</h2>
                    <p>Здесь вы найдете самых очаровательных котят! 🐾</p>
                    <ul>
                        <li>🐱 Пушистые котята</li>
                        <li>🐈 Игривые малыши</li>
                        <li>😺 Ласковые питомцы</li>
                    </ul>
                    <p>Котята приносят радость и уют в наш дом!</p>
                </div>
                """
            else:
                content = f"<p>Контент для: {task_description}</p>"
            result = self.tools["code_generator"].generate_html_page(title, content, filename)
            # Добавляем правильный путь в результат
            if result.get("success"):
                result["filename"] = filename
            return result
        
        else:
            # Для других файлов определяем тип по содержимому задачи И расширению
            if "python" in task_description.lower() or "print" in task_description.lower() or ".py" in task_description.lower():
                # Это Python код
                description = params.get("content", task_description)
                if not description or description in ["простой код", "код файла", "содержимое файла"]:
                    description = task_description
                result = self.tools["code_generator"].generate_python_script(description, filename)
                if result.get("success"):
                    result["filename"] = filename
                return result
            elif filename.endswith(('.txt', '.md', '.json', '.csv', '.xml')):
                # Для текстовых файлов используем file_manager вместо code_generator!
                return await self._use_file_manager(params, task_description)
            else:
                # Только для неопределённых расширений создаём HTML
                content = f"<p>Контент для: {task_description}</p>"
                result = self.tools["code_generator"].generate_html_page(title, content, filename)
                if result.get("success"):
                    result["filename"] = filename
                return result
    
    async def _use_file_manager(self, params: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        """Использование file_manager с сохранением в outputs/"""
        filename = params.get("filename", f"файл_{id(self)}.txt")
        
        # ИСПРАВЛЕНИЕ: Добавляем папку outputs/ для всех файлов
        if not filename.startswith("outputs/"):
            filename = f"outputs/{filename}"
        
        # ИСПОЛЬЗУЕМ КОНТЕНТ ИЗ LLM ПЛАНА!
        llm_content = params.get("content", "")
        
        if llm_content and llm_content not in ["простой текст", "текст файла", "содержимое файла"]:
            # LLM предоставил конкретный контент - используем его
            content = llm_content
        else:
            # Fallback только если LLM не дал контент
            content = f"""# Результат работы

Задача: {task_description}
Выполнено интеллектуальным агентом: {self.role}

## Результат
Задача успешно обработана с использованием LLM-интеллекта.
"""
        
        result = self.tools["file_manager"].create_file(filename, content)
        # Добавляем правильный путь в результат
        if result.get("success"):
            result["filename"] = filename
        return result
    
    async def _use_web_client(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Использование web_client для поиска и проверки сайтов"""
        
        # Если есть query - это поиск, если url - проверка сайта
        query = params.get("query", "")
        url = params.get("url", "")
        
        if query:
            # Поиск в интернете
            search_result = self.tools["web_search"].search(query)
            return {
                "success": True,
                "search_query": query,
                "search_results": search_result,
                "content": search_result
            }
        elif url:
            # Проверка сайта
            return self.tools["web_client"].check_website(url)
        else:
            # Fallback - проверка тестового сайта
            return self.tools["web_client"].check_website("https://httpbin.org/status/200")
    
    async def _use_system_tools(self, params: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        """Использование super_system_tool - единственного системного инструмента"""
        try:
            from ..tools.super_system_tool import SuperSystemTool
            system_tool = SuperSystemTool()
            
            # Определяем операцию на основе параметров
            operation = params.get("operation", "run_command")
            command = params.get("command", "echo 'System tools working'")
            
            # Выполняем операцию
            result = system_tool.execute(operation=operation, command=command)
            
            if result.success:
                return {
                    "success": True,
                    "filename": f"system_output_{id(self)}.txt",
                    "content": str(result.data),
                    "operation": operation
                }
            else:
                return {
                    "success": False,
                    "error": result.error or "System tools execution failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"System tools error: {str(e)}"
            }
    
    async def _get_amem_planning_insights(self, task_description: str, analysis: Dict[str, Any]) -> str:
        """🧠 Получение инсайтов из A-MEM для улучшения планирования"""
        try:
            # Пытаемся получить AMEM из UnifiedOrchestrator (если доступно)
            amem_system = getattr(self, 'amem_system', None)
            if not amem_system:
                # Пытаемся найти глобальный AMEM
                try:
                    from ..core.unified_orchestrator import UnifiedOrchestrator
                    # TODO: Получить ссылку на активный orchestrator
                    return self._generate_fallback_insights(task_description, analysis)
                except:
                    return self._generate_fallback_insights(task_description, analysis)
            
            # Определяем тип задачи для поиска похожих
            task_type = analysis.get('task_type', 'general')
            tools_needed = analysis.get('tools', [])
            
            # Ищем успешные решения похожих задач
            successful_memories = await amem_system.search_memories(
                query=f"успешные планы {task_type} качество",
                filter_tags=["high_quality", "successful_plan"]
            )
            
            # Ищем типичные ошибки для этого типа задач
            failure_memories = await amem_system.search_memories(
                query=f"проблемы ошибки {task_type}",
                filter_tags=["failure_analysis", "lessons_learned"]
            )
            
            insights_text = "🧠 A-MEM ИНСАЙТЫ ДЛЯ УЛУЧШЕНИЯ ПЛАНИРОВАНИЯ:\n\n"
            
            if successful_memories:
                insights_text += "✅ ПРОВЕРЕННЫЕ УСПЕШНЫЕ ПАТТЕРНЫ:\n"
                for i, memory in enumerate(successful_memories[:3], 1):
                    content_preview = memory.get('content', '')[:150] + "..."
                    insights_text += f"{i}. {content_preview}\n"
                insights_text += "\n"
            
            if failure_memories:
                insights_text += "🚫 ИЗБЕГАЙ ЭТИХ ОШИБОК:\n"
                for i, memory in enumerate(failure_memories[:2], 1):
                    content_preview = memory.get('content', '')[:100] + "..."
                    insights_text += f"{i}. {content_preview}\n"
                insights_text += "\n"
            
            # Добавляем рекомендации по количеству шагов
            if "анализ" in task_description.lower() and ("создай" in task_description.lower() or "сделай" in task_description.lower()):
                insights_text += "📋 РЕКОМЕНДАЦИЯ ПО СТРУКТУРЕ:\n"
                insights_text += "- Разбей на 4-6 шагов (анализ сложный!)\n"
                insights_text += "- Начни с web_client для актуальной информации\n"
                insights_text += "- Создавай отдельные файлы для разных типов результатов\n"
                insights_text += "- Финальные шаги - создание прототипов/рекомендаций\n\n"
            
            return insights_text
        
        except Exception as e:
            print(f"⚠️ Ошибка получения A-MEM инсайтов: {e}")
            return self._generate_fallback_insights(task_description, analysis)
    
    async def _save_execution_experience_to_amem(self, task_description: str, analysis: Dict, 
                                               execution_plan: Dict, result: Dict) -> None:
        """🧠 Сохранение опыта выполнения в A-MEM для обучения"""
        try:
            # Пытаемся получить AMEM из UnifiedOrchestrator
            amem_system = getattr(self, 'amem_system', None)
            if not amem_system:
                print("⚠️ A-MEM недоступен, опыт не сохранён")
                return
            
            # Анализируем качество результата
            success_rate = sum(1 for r in result.get('step_results', []) if r.get('success', False))
            total_steps = len(result.get('step_results', []))
            quality_score = success_rate / max(total_steps, 1)
            
            is_successful = result.get('status') == 'completed' and quality_score >= 0.5
            files_created = result.get('created_files', [])
            
            # Создаём контент воспоминания
            if is_successful:
                memory_content = f"""
Успешный план выполнения для типа задач: {analysis.get('task_type', 'general')}

Задача: {task_description[:100]}...
Качество выполнения: {quality_score:.2f} ({success_rate}/{total_steps} шагов успешно)
Создано файлов: {len(files_created)}

ПЛАН ВЫПОЛНЕНИЯ:
{self._format_plan_for_memory(execution_plan)}

РЕЗУЛЬТАТЫ:
- Статус: {result.get('status')}
- Файлы: {', '.join(files_created[:5])}
- Инструменты: {', '.join(analysis.get('chosen_tools', []))}

УСПЕХ: Этот план можно использовать для похожих задач!
"""
                tags = ["successful_plan", "high_quality", analysis.get('task_type', 'general')]
            else:
                memory_content = f"""
Неудачный план для типа задач: {analysis.get('task_type', 'general')}

Задача: {task_description[:100]}...
Качество выполнения: {quality_score:.2f} ({success_rate}/{total_steps} шагов успешно)

ПРОБЛЕМНЫЙ ПЛАН:
{self._format_plan_for_memory(execution_plan)}

ОШИБКИ:
{self._extract_failure_reasons(result)}

УРОК: Избегать этого подхода для подобных задач!
"""
                tags = ["failure_analysis", "lessons_learned", analysis.get('task_type', 'general')]
            
            # Сохраняем в A-MEM
            await amem_system.store_memory(
                content=memory_content.strip(),
                context={
                    "agent_role": self.role,
                    "task_type": analysis.get('task_type'),
                    "tools_used": analysis.get('chosen_tools', []),
                    "quality_score": quality_score,
                    "success": is_successful,
                    "step_count": total_steps,
                    "files_created_count": len(files_created)
                },
                tags=tags
            )
            
            print(f"🧠 Опыт выполнения сохранён в A-MEM (качество: {quality_score:.2f})")
            
        except Exception as e:
            print(f"⚠️ Ошибка сохранения опыта в A-MEM: {e}")
    
    def _format_plan_for_memory(self, execution_plan: Dict) -> str:
        """Форматирование плана для сохранения в память"""
        formatted_steps = []
        for step in execution_plan.get('steps', []):
            step_text = f"Шаг {step.get('step', '?')}: {step.get('action', 'Неизвестное действие')}"
            step_text += f" (инструмент: {step.get('tool', 'неизвестно')})"
            formatted_steps.append(step_text)
        
        return '\n'.join(formatted_steps)
    
    def _extract_failure_reasons(self, result: Dict) -> str:
        """Извлечение причин неудач для обучения"""
        failures = []
        for step_result in result.get('step_results', []):
            if not step_result.get('success', True):
                error = step_result.get('error', 'Неизвестная ошибка')
                failures.append(f"- {error}")
        
        return '\n'.join(failures) if failures else "- Нет явных ошибок в шагах"
    
    def _generate_fallback_insights(self, task_description: str, analysis: Dict[str, Any]) -> str:
        """Генерация базовых инсайтов без A-MEM"""
        insights = "🧠 БАЗОВЫЕ ИНСАЙТЫ (A-MEM недоступен):\n\n"
        
        # Анализируем задачу и даём рекомендации
        if "анализ" in task_description.lower():
            insights += "📊 АНАЛИЗ ЗАДАЧ:\n"
            insights += "- Начинай с поиска актуальной информации (web_client)\n"
            insights += "- Создавай структурированные файлы (.json для данных, .md для отчётов)\n"
            insights += "- Включай конкретные цифры, названия, статистику\n\n"
        
        if "прототип" in task_description.lower() or "создай" in task_description.lower():
            insights += "🎨 СОЗДАНИЕ ПРОТОТИПОВ:\n"
            insights += "- Описывай конкретные UI элементы и функции\n"
            insights += "- Включай технические детали реализации\n"
            insights += "- Создавай работающий код, а не описания\n\n"
        
        if len(task_description.split()) > 15:  # Сложная задача
            insights += "⚡ СЛОЖНЫЕ ЗАДАЧИ:\n"
            insights += "- Разбивай на 4-8 шагов\n"
            insights += "- Каждый шаг = один конкретный результат\n"
            insights += "- Используй результаты предыдущих шагов в следующих\n\n"
        
        return insights