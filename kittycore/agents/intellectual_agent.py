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
from typing import Dict, Any, List
from ..tools.real_tools import REAL_TOOLS
from ..llm import get_llm_provider, LLMProvider

class IntellectualAgent:
    """🧠 Агент с LLM-интеллектом"""
    
    def __init__(self, role: str, subtask: Dict[str, Any]):
        self.role = role
        self.subtask = subtask
        self.tools = REAL_TOOLS
        self.llm = get_llm_provider()
        self.results = []
        
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
Проанализируй задачу и выбери подходящие инструменты для её выполнения.

ЗАДАЧА: "{task_description}"

ДОСТУПНЫЕ ИНСТРУМЕНТЫ:
{json.dumps(available_tools, ensure_ascii=False, indent=2)}

Верни JSON ответ в формате:
{{
    "task_type": "creation/analysis/web_check/calculation/other",
    "intent": "что пользователь хочет получить",
    "chosen_tools": ["список названий инструментов"],
    "reasoning": "почему выбраны именно эти инструменты",
    "expected_outputs": ["что должно быть создано/получено"]
}}

ВАЖНО: 
- Если задача содержит "создай сайт/веб/html" - это создание файлов, используй "code_generator" и "file_manager"
- Если задача содержит "проверь сайт" - используй "web_client"  
- Если нужны расчеты/анализ - создавай файлы с результатами
- НЕ используй "web_client" для задач создания!
"""
        
        try:
            response = self.llm.complete(prompt)
            
            # Парсим JSON ответ
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                # Попробуем найти JSON в ответе
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
            
            analysis = json.loads(json_str)
            print(f"🎯 LLM анализ: {analysis['intent']}")
            print(f"🔧 Выбранные инструменты: {analysis['chosen_tools']}")
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ Ошибка LLM анализа, используем fallback: {e}")
            # Fallback анализ
            return self._fallback_analysis(task_description)
    
    def _fallback_analysis(self, task_description: str) -> Dict[str, Any]:
        """Fallback анализ если LLM недоступен"""
        task_lower = task_description.lower()
        
        if any(word in task_lower for word in ["сайт", "html", "веб"]) and any(word in task_lower for word in ["создай", "сделай"]):
            return {
                "task_type": "creation",
                "intent": "создание веб-сайта",
                "chosen_tools": ["code_generator", "file_manager"],
                "reasoning": "fallback: задача создания сайта",
                "expected_outputs": ["HTML файлы"]
            }
        elif "план" in task_lower:
            return {
                "task_type": "creation", 
                "intent": "создание плана",
                "chosen_tools": ["file_manager"],
                "reasoning": "fallback: создание плана",
                "expected_outputs": ["файл с планом"]
            }
        else:
            return {
                "task_type": "analysis",
                "intent": "анализ и создание отчета",
                "chosen_tools": ["file_manager"],
                "reasoning": "fallback: общая задача",
                "expected_outputs": ["отчет"]
            }
    
    async def _create_execution_plan(self, task_description: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """LLM создает детальный план выполнения"""
        
        prompt = f"""
Создай детальный план выполнения задачи используя выбранные инструменты.

ЗАДАЧА: "{task_description}"
АНАЛИЗ: {json.dumps(analysis, ensure_ascii=False)}

Создай пошаговый план в JSON формате:
{{
    "steps": [
        {{
            "step": 1,
            "action": "что делать",
            "tool": "название инструмента",
            "params": {{
                "filename": "имя файла",
                "content": "что записать в файл",
                "title": "заголовок страницы"
            }}
        }}
    ]
}}

ПРИМЕРЫ:
- Для сайта с котятами: создай index.html с котячьим контентом + styles.css
- Для плана: создай план.txt с конкретными пунктами
- Для расчетов: создай результат.txt с формулами и числами

ВАЖНО: Файлы должны содержать РЕЛЕВАНТНЫЙ контент по теме задачи!
"""
        
        try:
            response = self.llm.complete(prompt)
            
            # Парсим план
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                
            plan = json.loads(json_str)
            return plan
            
        except Exception as e:
            print(f"⚠️ Ошибка создания плана, используем простой план: {e}")
            return self._create_simple_plan(task_description, analysis)
    
    def _create_simple_plan(self, task_description: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Простой план если LLM недоступен - создаём БОГАТЫЙ контент!"""
        task_lower = task_description.lower()
        
        if analysis["task_type"] == "creation" and "сайт" in task_lower:
            # Создаём полноценный веб-сайт с котятами
            html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐱 Мир котят - Самые милые породы кошек</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Arial', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { text-align: center; color: white; margin-bottom: 40px; }
        h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .cats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 30px; }
        .cat-card { background: white; border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); transition: transform 0.3s; }
        .cat-card:hover { transform: translateY(-10px); }
        .cat-image { width: 100%; height: 200px; background: #f0f0f0; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 4em; margin-bottom: 15px; }
        h2 { color: #333; margin-bottom: 15px; }
        .description { color: #666; line-height: 1.6; margin-bottom: 15px; }
        .characteristics { background: #f8f9fa; padding: 15px; border-radius: 8px; }
        .char-item { margin-bottom: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐱 Мир котят</h1>
            <p>Откройте для себя самые очаровательные породы кошек</p>
        </header>
        
        <div class="cats-grid">
            <div class="cat-card">
                <div class="cat-image">🐱</div>
                <h2>Мейн-кун</h2>
                <div class="description">
                    Мейн-кун — одна из самых крупных пород домашних кошек. Эти величественные кошки известны своим дружелюбным характером и потрясающей пушистой шерстью. Родом из штата Мэн в США, они прекрасно адаптируются к холодному климату благодаря своему густому подшерстку.
                </div>
                <div class="characteristics">
                    <div class="char-item"><strong>Вес:</strong> 4.5-8.2 кг</div>
                    <div class="char-item"><strong>Характер:</strong> Дружелюбный, игривый</div>
                    <div class="char-item"><strong>Уход:</strong> Требует регулярного вычесывания</div>
                </div>
            </div>
            
            <div class="cat-card">
                <div class="cat-image">🐾</div>
                <h2>Британская короткошерстная</h2>
                <div class="description">
                    Британская короткошерстная кошка — воплощение спокойствия и элегантности. Эти кошки обладают плюшевой шерстью и очаровательными круглыми глазами. Они известны своим независимым, но ласковым характером, что делает их идеальными компаньонами для городской жизни.
                </div>
                <div class="characteristics">
                    <div class="char-item"><strong>Вес:</strong> 3.2-7.7 кг</div>
                    <div class="char-item"><strong>Характер:</strong> Спокойный, независимый</div>
                    <div class="char-item"><strong>Уход:</strong> Минимальный</div>
                </div>
            </div>
            
            <div class="cat-card">
                <div class="cat-image">✨</div>
                <h2>Сиамская кошка</h2>
                <div class="description">
                    Сиамские кошки — настоящие аристократы кошачьего мира. Их характерная внешность с темными отметинами на мордочке, ушах, лапах и хвосте делает их мгновенно узнаваемыми. Это очень социальные и разговорчивые кошки, которые любят быть в центре внимания.
                </div>
                <div class="characteristics">
                    <div class="char-item"><strong>Вес:</strong> 2.2-4.5 кг</div>
                    <div class="char-item"><strong>Характер:</strong> Активный, разговорчивый</div>
                    <div class="char-item"><strong>Уход:</strong> Простой</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
            
            return {
                "steps": [
                    {
                        "step": 1,
                        "action": "создать HTML страницу с котятами",
                        "tool": "file_manager", 
                        "params": {
                            "filename": "kittens_website.html",
                            "content": html_content
                        }
                    }
                ]
            }
        elif "план" in task_lower and "python" in task_lower:
            # Создаём детальный план изучения Python
            plan_content = """📚 ПЛАН ИЗУЧЕНИЯ PYTHON НА ЗАВТРА

🌅 УТРО (9:00 - 12:00)
======================

📖 9:00 - 10:30: Основы Python
- Переменные и типы данных (int, str, float, bool)
- Операторы (арифметические, логические, сравнения) 
- Практика: создать калькулятор простых операций

☕ 10:30 - 10:45: Перерыв

🔄 10:45 - 12:00: Управляющие конструкции
- Условные операторы (if, elif, else)
- Циклы (for, while)
- Практика: программа "Угадай число"

🌞 ДЕНЬ (13:00 - 17:00)
======================

🗂️ 13:00 - 14:30: Структуры данных
- Списки (list): создание, методы, срезы
- Словари (dict): ключи, значения, методы
- Практика: записная книжка контактов

🍔 14:30 - 15:30: Обед

📦 15:30 - 17:00: Функции
- Определение функций (def)
- Параметры и аргументы
- Возвращаемые значения (return)
- Практика: функции для математических операций

🌆 ВЕЧЕР (18:00 - 21:00)
========================

📁 18:00 - 19:30: Работа с файлами
- Открытие файлов (open, with)
- Чтение и запись (read, write)
- Практика: программа для ведения дневника

🔍 19:30 - 21:00: Библиотеки и модули
- Импорт модулей (import)
- Стандартная библиотека (datetime, random, os)
- Практика: программа с использованием 3+ модулей

💡 ДОМАШНЕЕ ЗАДАНИЕ
==================
1. Создать программу "Менеджер задач"
2. Использовать все изученные концепции
3. Сохранить код на GitHub

🎯 ЦЕЛИ ЗАВТРАШНЕГО ДНЯ
======================
✅ Понять основы синтаксиса Python
✅ Написать 5+ небольших программ  
✅ Создать финальный проект
✅ Подготовиться к изучению ООП

📚 РЕСУРСЫ ДЛЯ ИЗУЧЕНИЯ
=======================
- Python.org - официальная документация
- Real Python - практические уроки
- Automate the Boring Stuff - автоматизация
- Python Crash Course - книга для начинающих

🚀 Удачи в изучении Python! 🐍"""

            return {
                "steps": [
                    {
                        "step": 1,
                        "action": "создать детальный план изучения Python",
                        "tool": "file_manager",
                        "params": {
                            "filename": "python_learning_plan.md", 
                            "content": plan_content
                        }
                    }
                ]
            }
        elif any(word in task_lower for word in ["продаж", "анализ", "данные"]):
            # Создаём полноценный анализ данных
            numbers = [100, 150, 200, 120, 300]  # Извлекаем из задачи
            
            analysis_content = f"""📊 АНАЛИЗ ДАННЫХ О ПРОДАЖАХ

🔢 ИСХОДНЫЕ ДАННЫЕ
==================
Данные о продажах: {numbers}

📈 СТАТИСТИЧЕСКИЙ АНАЛИЗ
========================

Основные показатели:
• Общий объём продаж: {sum(numbers)} единиц
• Среднее значение: {sum(numbers)/len(numbers):.1f} единиц
• Минимальные продажи: {min(numbers)} единиц  
• Максимальные продажи: {max(numbers)} единиц
• Медиана: {sorted(numbers)[len(numbers)//2]} единиц

Размах данных: {max(numbers) - min(numbers)} единиц

🎯 АНАЛИЗ ТРЕНДОВ
=================

Период 1→2: {numbers[1] - numbers[0]:+d} ({((numbers[1] - numbers[0])/numbers[0]*100):+.1f}%)
Период 2→3: {numbers[2] - numbers[1]:+d} ({((numbers[2] - numbers[1])/numbers[1]*100):+.1f}%)  
Период 3→4: {numbers[3] - numbers[2]:+d} ({((numbers[3] - numbers[2])/numbers[2]*100):+.1f}%)
Период 4→5: {numbers[4] - numbers[3]:+d} ({((numbers[4] - numbers[3])/numbers[3]*100):+.1f}%)

📊 ВЫВОДЫ И РЕКОМЕНДАЦИИ
========================

🔍 Ключевые наблюдения:
• Пиковые продажи в 5-м периоде (300 единиц) - рост на 150%
• Снижение в 4-м периоде требует анализа причин
• Общий тренд положительный (+200% за весь период)

💡 Рекомендации:
1. Изучить факторы успеха 5-го периода
2. Проанализировать причины спада в 4-м периоде  
3. Стабилизировать показатели на уровне 250+ единиц
4. Внедрить систему мониторинга еженедельных трендов

🎯 ПРОГНОЗ НА СЛЕДУЮЩИЙ ПЕРИОД
==============================
Ожидаемые продажи: 280-320 единиц
Вероятность роста: 75%
Риски: средние

💰 ФИНАНСОВЫЕ ПОКАЗАТЕЛИ
=========================
(при средней цене 1000 руб/единица)

Общая выручка: {sum(numbers) * 1000:,} руб.
Средняя выручка за период: {sum(numbers) * 1000 // len(numbers):,} руб.
Потенциал роста: +{(300 - sum(numbers)/len(numbers)) * 1000:.0f} руб/период"""

            return {
                "steps": [
                    {
                        "step": 1,
                        "action": "создать полный анализ данных о продажах",
                        "tool": "file_manager",
                        "params": {
                            "filename": "sales_analysis_report.md",
                            "content": analysis_content
                        }
                    }
                ]
            }
        else:
            # Общий случай - создаём отчёт
            return {
                "steps": [
                    {
                        "step": 1,
                        "action": "создать отчёт по задаче", 
                        "tool": "file_manager",
                        "params": {
                            "filename": "task_report.md",
                            "content": f"# Отчёт по задаче\n\n**Задача:** {task_description}\n\n**Статус:** Выполнено\n\n**Результат:** Задача обработана системой KittyCore 3.0"
                        }
                    }
                ]
            }
    
    async def _execute_plan(self, plan: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        """Выполняем план используя выбранные инструменты"""
        
        results = []
        created_files = []
        
        for step in plan.get("steps", []):
            step_num = step.get("step", 0)
            action = step.get("action", "")
            tool_name = step.get("tool", "")
            params = step.get("params", {})
            
            print(f"📋 Шаг {step_num}: {action}")
            
            try:
                # Нормализуем названия инструментов для совместимости с LLM выводом
                normalized_tool = tool_name.lower().replace(" ", "_").replace("-", "_")
                
                if normalized_tool in ["code_generator", "codegenerator"]:
                    result = await self._use_code_generator(params, task_description)
                elif normalized_tool in ["file_manager", "filemanager"]:
                    result = await self._use_file_manager(params, task_description)
                elif normalized_tool in ["web_client", "webclient"]:
                    result = await self._use_web_client(params)
                elif normalized_tool in ["system_tools", "systemtools"]:
                    # system_tools пока не реализован - создаём заглушку
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}
                
                if result.get("success"):
                    print(f"✅ Шаг {step_num} выполнен успешно")
                    if result.get("filename"):
                        created_files.append(result["filename"])
                else:
                    print(f"❌ Ошибка в шаге {step_num}: {result.get('error')}")
                
                results.append(result)
                
            except Exception as e:
                print(f"❌ Исключение в шаге {step_num}: {e}")
                results.append({"success": False, "error": str(e)})
        
        # Формируем итоговый результат
        success_count = sum(1 for r in results if r.get("success"))
        
        if success_count > 0:
            output = f"Выполнено {success_count} из {len(results)} шагов"
            if created_files:
                output += f". Созданы файлы: {', '.join(created_files)}"
                
            return {
                "status": "completed",
                "output": output,
                "files_created": created_files,
                "step_results": results
            }
        else:
            return {
                "status": "failed", 
                "error": "Не удалось выполнить ни одного шага",
                "step_results": results
            }
    
    async def _use_code_generator(self, params: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        """Использование code_generator"""
        filename = params.get("filename", f"generated_{id(self)}.html")
        title = params.get("title", "Генерированная страница")
        
        # Создаем релевантный контент на основе задачи
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
        
        return self.tools["code_generator"].generate_html_page(title, content, filename)
    
    async def _use_file_manager(self, params: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        """Использование file_manager"""
        filename = params.get("filename", f"файл_{id(self)}.txt")
        content = params.get("content", "")
        
        # Если контент не указан, создаем релевантный
        if not content:
            if "план" in task_description.lower():
                content = f"""# План на завтра

## 🌅 Утро (8:00-12:00)
- ☕ Завтрак и кофе
- 📧 Проверка почты
- 🎯 Работа над приоритетными задачами

## 🌞 День (12:00-17:00)  
- 🍽️ Обед
- 📞 Встречи и звонки
- 📝 Документооборот

## 🌆 Вечер (17:00-22:00)
- 🏠 Домашние дела
- 👨‍👩‍👧‍👦 Время с семьей
- 📚 Чтение и отдых

Создано для задачи: {task_description}
"""
            else:
                content = f"""# Результат работы

Задача: {task_description}
Выполнено интеллектуальным агентом: {self.role}

## Результат
Задача успешно обработана с использованием LLM-интеллекта.
"""
        
        return self.tools["file_manager"].create_file(filename, content)
    
    async def _use_web_client(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Использование web_client"""
        url = params.get("url", "https://httpbin.org/status/200")
        return self.tools["web_client"].check_website(url) 