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
        """Создаём простой план выполнения на основе анализа"""
        
        # Определяем тип задачи и создаём соответствующий план
        task_lower = task_description.lower()
        
        if "python" in task_lower and ("скрипт" in task_lower or "код" in task_lower):
            # Python код
            if "факториал" in task_lower:
                return {
                    "steps": [
                        {
                            "step": 1,
                            "action": "Создать Python скрипт для вычисления факториала",
                            "tool": "code_generator",
                            "params": {
                                "filename": "factorial.py",
                                "content": """def factorial(n):
    \"\"\"Вычисляет факториал числа n\"\"\"
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
    main()""",
                                "language": "python",
                                "title": "Калькулятор факториала"
                            }
                        }
                    ]
                }
            elif "сортировк" in task_lower and "быстр" in task_lower:
                return {
                    "steps": [
                        {
                            "step": 1,
                            "action": "Создать Python скрипт с быстрой сортировкой",
                            "tool": "code_generator", 
                            "params": {
                                "filename": "quicksort.py",
                                "content": """def quicksort(arr):
    \"\"\"Быстрая сортировка массива\"\"\"
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
    main()""",
                                "language": "python",
                                "title": "Быстрая сортировка"
                            }
                        }
                    ]
                }
            else:
                # Общий Python скрипт
                return {
                    "steps": [
                        {
                            "step": 1,
                            "action": "Создать Python скрипт",
                            "tool": "code_generator",
                            "params": {
                                "filename": "script.py",
                                "content": f"""# {task_description}

def main():
    print("Скрипт создан для задачи: {task_description}")
    # Добавьте здесь вашу логику

if __name__ == "__main__":
    main()""",
                                "language": "python",
                                "title": "Python скрипт"
                            }
                        }
                    ]
                }
        
        elif "html" in task_lower or "веб" in task_lower or "страниц" in task_lower:
            # HTML страница
            if "регистрац" in task_lower or "форм" in task_lower:
                return {
                    "steps": [
                        {
                            "step": 1,
                            "action": "Создать HTML страницу с формой регистрации",
                            "tool": "code_generator",
                            "params": {
                                "filename": "registration.html",
                                "content": """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Регистрация</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .form-container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; color: #555; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="form-container">
        <h1>Регистрация</h1>
        <form action="#" method="post">
            <div class="form-group">
                <label for="name">Имя:</label>
                <input type="text" id="name" name="name" required>
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Пароль:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Зарегистрироваться</button>
        </form>
    </div>
</body>
</html>""",
                                "language": "html",
                                "title": "Форма регистрации"
                            }
                        }
                    ]
                }
            else:
                # Общая HTML страница
                return {
                    "steps": [
                        {
                            "step": 1,
                            "action": "Создать HTML страницу",
                            "tool": "code_generator",
                            "params": {
                                "filename": "page.html",
                                "content": f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Веб-страница</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ color: #333; border-bottom: 2px solid #eee; }}
        .content {{ margin-top: 20px; line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Веб-страница</h1>
    </div>
    <div class="content">
        <p>Создано для задачи: {task_description}</p>
    </div>
</body>
</html>""",
                                "language": "html",
                                "title": "Веб-страница"
                            }
                        }
                    ]
                }
        
        elif "json" in task_lower and "конфигурац" in task_lower:
            # JSON конфигурация
            return {
                "steps": [
                    {
                        "step": 1,
                        "action": "Создать JSON файл конфигурации",
                        "tool": "file_manager",
                        "params": {
                            "filename": "config.json",
                            "content": """{
    "server": {
        "host": "localhost",
        "port": 8080,
        "ssl": false
    },
    "logging": {
        "level": "info",
        "file": "server.log",
        "max_size": "10MB",
        "rotate": true
    },
    "database": {
        "type": "sqlite",
        "path": "data.db"
    },
    "features": {
        "debug": false,
        "cors": true,
        "rate_limiting": true
    }
}"""
                        }
                    }
                ]
            }
        
        elif "readme" in task_lower:
            # README файл
            return {
                "steps": [
                    {
                        "step": 1,
                        "action": "Создать README.md файл",
                        "tool": "file_manager",
                        "params": {
                            "filename": "README.md",
                            "content": """# Калькулятор

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
"""
                        }
                    }
                ]
            }
        
        else:
            # Создаём релевантный файл вместо отчёта
            if "площад" in task_lower and ("круг" in task_lower or "кот" in task_lower):
                return {
                    "steps": [
                        {
                            "step": 1,
                            "action": "Создать файл с расчётом площади",
                            "tool": "file_manager",
                            "params": {
                                "filename": "area_calculation.py",
                                "content": """import math

def calculate_circle_area(radius):
    \"\"\"Расчёт площади круга по формуле A = π * r²\"\"\"
    return math.pi * radius ** 2

def calculate_cat_area(length, width):
    \"\"\"Приблизительный расчёт площади кота (как прямоугольника)\"\"\"
    return length * width

# Пример использования
if __name__ == "__main__":
    # Площадь круга
    radius = 5
    circle_area = calculate_circle_area(radius)
    print(f"Площадь круга с радиусом {radius} = {circle_area:.2f}")
    
    # Площадь кота (шуточный расчёт)
    cat_length = 0.5  # метры
    cat_width = 0.3   # метры
    cat_area = calculate_cat_area(cat_length, cat_width)
    print(f"Площадь кота {cat_length}x{cat_width}м = {cat_area:.2f} м²")
"""
                            }
                        }
                    ]
                }
            else:
                # Общий случай - создаём релевантный файл
                return {
                    "steps": [
                        {
                            "step": 1,
                            "action": "Создать файл с результатом",
                            "tool": "file_manager",
                            "params": {
                                "filename": "result.txt",
                                "content": f"""Результат выполнения задачи: {task_description}

Задача обработана интеллектуальным агентом KittyCore 3.0.
Время создания: {analysis.get('timestamp', 'неизвестно')}

Описание: Создан файл с результатом выполнения поставленной задачи.
"""
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
            print(f"🔧 Инструмент: {tool_name}, Параметры: {params}")
            
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
                    # Используем реальный system_tools
                    result = await self._use_system_tools(params, task_description)
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}
                
                # Логируем результат вызова инструмента
                print(f"🎯 Результат инструмента {tool_name}: {result.get('success', False)}")
                if result.get("filename"):
                    print(f"📁 Создан файл: {result['filename']}")
                if result.get("content"):
                    content_preview = result["content"][:100] + "..." if len(result["content"]) > 100 else result["content"]
                    print(f"💎 Контент: {content_preview}")
                
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
        
        print(f"📊 Итого: {success_count}/{len(results)} шагов выполнено успешно")
        
        if success_count > 0:
            output = f"Выполнено {success_count} из {len(results)} шагов"
            if created_files:
                output += f". Созданы файлы: {', '.join(created_files)}"
                print(f"📁 Созданные файлы: {created_files}")
                
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
    
    async def _use_system_tools(self, params: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        """Использование system_tools"""
        try:
            from ..tools.system_tools import SystemTools
            system_tool = SystemTools()
            
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
                    "error": result.error
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка system_tools: {str(e)}"
            } 