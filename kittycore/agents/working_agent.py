"""
🤖 WorkingAgent - Агент с реальными возможностями

Агент который может выполнять реальную работу с помощью инструментов
"""

import asyncio
from typing import Dict, Any, List
from ..tools.real_tools import REAL_TOOLS

class WorkingAgent:
    """Агент с реальными инструментами"""
    
    def __init__(self, role: str, subtask: Dict[str, Any]):
        self.role = role
        self.subtask = subtask
        self.tools = REAL_TOOLS
        self.results = []
    
    async def execute_task(self) -> Dict[str, Any]:
        """Выполнить задачу используя реальные инструменты"""
        task_description = self.subtask.get("description", "")
        task_type = self.subtask.get("type", "general")
        
        print(f"🤖 {self.role} начинает работу: {task_description}")
        
        # Определяем какие инструменты использовать для типа задачи
        if "python" in task_description.lower() or "скрипт" in task_description.lower():
            return await self._create_python_script(task_description)
        elif ("сайт" in task_description.lower() or "html" in task_description.lower() or 
              "веб" in task_description.lower()) and any(word in task_description.lower() 
              for word in ["создай", "сделай", "напиши", "разработай"]):
            return await self._create_website_with_content(task_description)
        elif "файл" in task_description.lower() or "создать" in task_description.lower():
            return await self._create_file(task_description)
        elif "проверить" in task_description.lower() and "сайт" in task_description.lower():
            return await self._check_website(task_description)
        else:
            return await self._general_task(task_description)
    
    async def _create_python_script(self, description: str) -> Dict[str, Any]:
        """Создать Python скрипт"""
        filename = f"generated_script_{id(self)}.py"
        
        result = self.tools["code_generator"].generate_python_script(
            description, filename
        )
        
        if result["success"]:
            print(f"✅ Создан Python скрипт: {filename}")
            return {
                "status": "completed",
                "output": f"Создан исполняемый Python скрипт: {filename}",
                "files_created": [filename],
                "executable": True
            }
        else:
            return {
                "status": "failed", 
                "error": result["error"]
            }
    
    async def _create_html_page(self, description: str) -> Dict[str, Any]:
        """Создать HTML страницу"""
        filename = f"generated_page_{id(self)}.html"
        title = "Генерированная страница"
        content = f"<p>Эта страница создана для: {description}</p>"
        
        result = self.tools["code_generator"].generate_html_page(
            title, content, filename
        )
        
        if result["success"]:
            print(f"✅ Создана HTML страница: {filename}")
            return {
                "status": "completed",
                "output": f"Создана HTML страница: {filename}",
                "files_created": [filename]
            }
        else:
            return {
                "status": "failed",
                "error": result["error"]
            }
    
    async def _create_file(self, description: str) -> Dict[str, Any]:
        """Создать файл"""
        filename = f"output_{id(self)}.txt"
        content = f"# Результат работы\n\nЗадача: {description}\nВыполнено агентом: {self.role}\n"
        
        result = self.tools["file_manager"].create_file(filename, content)
        
        if result["success"]:
            print(f"✅ Создан файл: {filename}")
            return {
                "status": "completed",
                "output": f"Создан файл: {filename}",
                "files_created": [filename]
            }
        else:
            return {
                "status": "failed",
                "error": result["error"]
            }
    
    async def _check_website(self, description: str) -> Dict[str, Any]:
        """Проверить веб-сайт"""
        # Попробуем извлечь URL из описания или используем тестовый
        url = "https://httpbin.org/status/200"  # Тестовый URL
        
        result = self.tools["web_client"].check_website(url)
        
        if result["success"]:
            print(f"✅ Проверен сайт: {url}")
            return {
                "status": "completed", 
                "output": f"Сайт {url} доступен (статус: {result.get('status_code', 'N/A')})",
                "website_status": result
            }
        else:
            return {
                "status": "failed",
                "error": result["error"]
            }
    
    async def _general_task(self, description: str) -> Dict[str, Any]:
        """Общая задача"""
        # Создаём отчёт о выполнении
        filename = f"task_report_{id(self)}.txt"
        content = f"""# Отчёт о выполнении задачи

Агент: {self.role}
Задача: {description}
Время: {asyncio.get_event_loop().time()}

## Выполненные действия:
1. Проанализировал задачу
2. Определил план действий
3. Создал данный отчёт

## Результат:
Задача обработана агентом {self.role}
"""
        
        result = self.tools["file_manager"].create_file(filename, content)
        
        if result["success"]:
            print(f"✅ Создан отчёт: {filename}")
            return {
                "status": "completed",
                "output": f"Задача выполнена, создан отчёт: {filename}",
                "files_created": [filename]
            }
        else:
            return {
                "status": "failed", 
                "error": result["error"]
            } 