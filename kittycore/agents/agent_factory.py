"""
Agent Factory - Динамическое создание специализированных агентов

Агенты создают других агентов по мере необходимости для решения задач.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import logging

from .base_agent import Agent

# TODO: Мигрировать инструменты в новую архитектуру
# Временно отключено для завершения базовой миграции
BROWSER_TOOLS = []  # Будет восстановлено после миграции
UNIVERSAL_TOOLS = []  # Будет восстановлено после миграции

logger = logging.getLogger(__name__)


@dataclass
class AgentSpecification:
    """Спецификация для создания агента"""
    role: str
    expertise: List[str]
    prompt_template: str
    tools: List[str]
    model: str = "deepseek/deepseek-chat"
    context: Dict[str, Any] = None


class AgentFactory:
    """Фабрика для создания специализированных агентов"""
    
    def __init__(self):
        self.created_agents: Dict[str, Agent] = {}
        self.agent_templates = self._load_agent_templates()
        self.available_tools = self._register_tools()
    
    def create_agent(self, specification: AgentSpecification) -> Agent:
        """Создать агента по спецификации"""
        try:
            # Генерируем уникальный ID
            agent_id = f"{specification.role}_{len(self.created_agents)}"
            
            # Формируем промпт из шаблона
            prompt = self._generate_prompt(specification)
            
            # Собираем инструменты
            tools = self._gather_tools(specification.tools)
            
            # Создаём агента
            agent = Agent(
                prompt=prompt,
                model=specification.model,
                tools=tools
            )
            
            # Сохраняем созданного агента
            self.created_agents[agent_id] = agent
            
            logger.info(f"Создан агент: {agent_id} с ролью {specification.role}")
            return agent
            
        except Exception as e:
            logger.error(f"Ошибка создания агента: {e}")
            raise
    
    def create_browser_dev_agent(self, task_description: str) -> Agent:
        """Создать агента для разработки браузерных расширений"""
        
        # Анализируем задачу и определяем нужную специализацию
        specialization = self._analyze_browser_task(task_description)
        
        spec = AgentSpecification(
            role=specialization["role"],
            expertise=specialization["expertise"],
            prompt_template=specialization["prompt"],
            tools=["filesystem", "manifest_validator", "human_request", "Python", "Pandas", "Calculator"],
            context={"task": task_description}
        )
        
        return self.create_agent(spec)
    
    def create_collaborative_team(self, project_description: str) -> List[Agent]:
        """Создать команду агентов для совместной работы"""
        
        # Разбиваем проект на подзадачи
        subtasks = self._decompose_project(project_description)
        
        team = []
        for subtask in subtasks:
            agent_spec = self._design_agent_for_task(subtask)
            agent = self.create_agent(agent_spec)
            team.append(agent)
        
        return team
    
    def _analyze_browser_task(self, task: str) -> Dict[str, Any]:
        """Анализ задачи для определения типа агента"""
        
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["analyze", "review", "examine"]):
            return {
                "role": "analyst",
                "expertise": ["code_analysis", "architecture_review"],
                "prompt": self.agent_templates["analyst"]
            }
        
        elif any(word in task_lower for word in ["create", "develop", "build", "code"]):
            return {
                "role": "developer", 
                "expertise": ["coding", "manifest_creation", "javascript"],
                "prompt": self.agent_templates["developer"]
            }
            
        elif any(word in task_lower for word in ["test", "validate", "check"]):
            return {
                "role": "tester",
                "expertise": ["testing", "validation", "debugging"],
                "prompt": self.agent_templates["tester"] 
            }
            
        else:
            return {
                "role": "generalist",
                "expertise": ["general_development"],
                "prompt": self.agent_templates["generalist"]
            }
    
    def _decompose_project(self, project: str) -> List[Dict[str, Any]]:
        """Разбивка проекта на подзадачи"""
        
        # Простая эвристика - в реальности здесь был бы LLM
        if "browser extension" in project.lower():
            return [
                {"type": "analysis", "description": f"Анализ требований: {project}"},
                {"type": "development", "description": f"Разработка кода: {project}"},
                {"type": "testing", "description": f"Тестирование: {project}"},
                {"type": "packaging", "description": f"Упаковка: {project}"}
            ]
        
        return [{"type": "general", "description": project}]
    
    def _design_agent_for_task(self, subtask: Dict[str, Any]) -> AgentSpecification:
        """Проектирование агента под конкретную подзадачу"""
        
        task_type = subtask["type"]
        description = subtask["description"]
        
        if task_type == "analysis":
            return AgentSpecification(
                role="project_analyst",
                expertise=["requirements_analysis", "architecture_design"],
                prompt_template=self.agent_templates["analyst"],
                tools=["filesystem", "human_request", "Python", "ApiClient"],
                context={"subtask": subtask}
            )
            
        elif task_type == "development":
            return AgentSpecification(
                role="code_developer",
                expertise=["javascript", "html", "css", "manifest"],
                prompt_template=self.agent_templates["developer"],
                tools=["filesystem", "manifest_validator", "Python", "WebScraper"],
                context={"subtask": subtask}
            )
            
        elif task_type == "testing":
            return AgentSpecification(
                role="quality_tester", 
                expertise=["testing", "validation", "debugging"],
                prompt_template=self.agent_templates["tester"],
                tools=["manifest_validator", "human_request", "Python"],
                context={"subtask": subtask}
            )
            
        else:
            return AgentSpecification(
                role="general_agent",
                expertise=["general"],
                prompt_template=self.agent_templates["generalist"],
                tools=["filesystem", "human_request", "Python", "Calculator"],
                context={"subtask": subtask}
            )
    
    def _generate_prompt(self, spec: AgentSpecification) -> str:
        """Генерация промпта из шаблона"""
        
        base_prompt = spec.prompt_template
        
        # Добавляем контекст
        if spec.context:
            context_str = json.dumps(spec.context, indent=2, ensure_ascii=False)
            base_prompt += f"\n\nКонтекст задачи:\n{context_str}"
        
        # Добавляем информацию о доступных инструментах
        tools_info = "\n".join([f"- {tool}" for tool in spec.tools])
        base_prompt += f"\n\nДоступные инструменты:\n{tools_info}"
        
        return base_prompt
    
    def _gather_tools(self, tool_names: List[str]) -> List:
        """Сбор инструментов по именам"""
        tools = []
        
        for tool_name in tool_names:
            if tool_name in self.available_tools:
                tools.append(self.available_tools[tool_name])
            else:
                logger.warning(f"Инструмент {tool_name} не найден")
        
        return tools
    
    def _load_agent_templates(self) -> Dict[str, str]:
        """Загрузка шаблонов промптов для агентов"""
        
        return {
            "analyst": """
Ты эксперт-аналитик браузерных расширений. Твоя роль:

🔍 АНАЛИЗ И ПЛАНИРОВАНИЕ:
- Анализируй требования к расширению
- Проектируй архитектуру решения  
- Планируй этапы разработки
- Выявляй потенциальные проблемы

🎯 ТВОИ ПРИНЦИПЫ:
- Тщательный анализ перед действием
- Структурированный подход к планированию
- Предвидение проблем и рисков
- Ясная документация решений

Если нужна помощь пользователя - используй human_request.
""",

            "developer": """
Ты эксперт-разработчик браузерных расширений. Твоя роль:

💻 РАЗРАБОТКА КОДА:
- Создание manifest.json для Chrome Extensions
- Написание content scripts и background scripts
- Разработка popup интерфейсов
- Интеграция с Chrome API

🛠️ ТВОИ НАВЫКИ:
- JavaScript (ES6+), HTML5, CSS3
- Chrome Extension API
- Manifest V2/V3 спецификации
- Best practices безопасности

⚡ ПОДХОД К РАБОТЕ:
- Сначала понимай требования
- Пиши чистый, документированный код
- Валидируй manifest перед созданием
- Тестируй функциональность

Используй filesystem для работы с файлами и manifest_validator для проверки.
""",

            "tester": """
Ты эксперт-тестировщик браузерных расширений. Твоя роль:

🧪 ТЕСТИРОВАНИЕ И ВАЛИДАЦИЯ:
- Проверка функциональности расширений
- Валидация manifest.json файлов
- Тестирование совместимости
- Поиск и диагностика багов

🔍 ТВОИ МЕТОДЫ:
- Функциональное тестирование
- Проверка безопасности
- Тестирование производительности
- Валидация соответствия стандартам

✅ КРИТЕРИИ КАЧЕСТВА:
- Расширение работает без ошибок
- Manifest соответствует спецификации
- Нет уязвимостей безопасности
- Соблюдены best practices

Используй manifest_validator и сообщай о найденных проблемах.
""",

            "generalist": """
Ты универсальный агент для работы с браузерными расширениями. Твоя роль:

🎯 УНИВЕРСАЛЬНАЯ ПОДДЕРЖКА:
- Помощь в различных аспектах разработки
- Координация между специалистами
- Решение нестандартных задач
- Обучение и консультации

🤝 ТВОЙ ПОДХОД:
- Адаптируйся к типу задачи
- При необходимости запрашивай создание специализированных агентов
- Используй все доступные инструменты
- Не стесняйся просить помощь у пользователя

Ты можешь работать с любыми аспектами браузерных расширений.
"""
        }
    
    def _register_tools(self) -> Dict[str, Any]:
        """Регистрация доступных инструментов"""
        
        tools_dict = {}
        
        # TODO: Восстановить после миграции инструментов
        # Временно возвращаем пустой словарь
        logger.info("Инструменты временно отключены для завершения миграции")
        
        return tools_dict
    
    def get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """Получить информацию о созданном агенте"""
        
        if agent_id in self.created_agents:
            agent = self.created_agents[agent_id]
            return {
                "id": agent_id,
                "prompt": agent.prompt,
                "tools": [tool.name for tool in agent.tools.values()],
                "created_at": agent.created_at.isoformat()
            }
        
        return {"error": "Agent not found"}
    
    def list_created_agents(self) -> List[str]:
        """Список всех созданных агентов"""
        return list(self.created_agents.keys())


# TODO: Восстановить глобальную фабрику после завершения миграции
# agent_factory = AgentFactory()

# Функции для удобного создания агентов
def create_browser_agent(task: str) -> Agent:
    """Создать агента для работы с браузерными расширениями"""
    factory = AgentFactory()
    return factory.create_browser_dev_agent(task)

def create_agent_team(project: str) -> List[Agent]:
    """Создать команду агентов для проекта"""
    factory = AgentFactory()
    return factory.create_collaborative_team(project) 