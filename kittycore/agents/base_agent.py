"""
Базовый класс агента для KittyCore 3.0

Простой, мощный, расширяемый.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Iterator, Union
from dataclasses import dataclass
from datetime import datetime

try:
    from ..memory import Memory
    from ..tools import Tool  # Это tools папка, а не файл
    from ..llm import LLMProvider
    from ..config import Config
except ImportError:
    # Fallback для случаев когда модуль запускается отдельно
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from memory import Memory
    from tools import Tool  # Это tools папка
    from llm import LLMProvider
    from config import Config

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Конфигурация агента"""
    name: str = "agent"
    model: str = "auto"
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 30
    memory_type: str = "simple"
    log_level: str = "INFO"


class Agent:
    """
    Простой, но мощный AI агент
    
    Основные принципы:
    - Простота использования (3 строки для старта)
    - Мощность и гибкость для сложных задач
    - Расширяемость через tools и memory
    """
    
    def __init__(
        self,
        prompt: str,
        model: str = "deepseek/deepseek-chat",  # Используем бесплатную модель DeepSeek
        tools: Optional[List[Tool]] = None,
        memory: Optional[Memory] = None,
        config: Optional[AgentConfig] = None
    ):
        """
        Создать агента
        
        Args:
            prompt: Системный промпт агента
            model: Модель LLM ("auto", "deepseek/deepseek-chat", "anthropic/claude-3.5-sonnet", etc.)
            tools: Список инструментов
            memory: Система памяти
            config: Дополнительная конфигурация
        
        Examples:
            # Простой агент
            agent = Agent("You are a helpful assistant")
            
            # Агент с инструментами
            agent = Agent(
                "You are a search assistant",
                tools=[WebSearchTool(), DatabaseTool()]
            )
            
            # Продвинутый агент
            agent = Agent(
                "You are a customer support agent",
                model="gpt-4o",
                tools=[EmailTool(), CRMTool()],
                memory=PersistentMemory(db_path="agent_memory.db")
            )
        """
        # Загружаем переменные окружения для OpenRouter
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # dotenv не обязательна
        
        self.prompt = prompt
        self.config = config or AgentConfig()
        self.created_at = datetime.now()
        
        # Инициализируем компоненты
        self.llm = self._init_llm(model)
        self.memory = memory or Memory()
        self.tools = {tool.name: tool for tool in (tools or [])}
        
        # Состояние агента
        self.conversation_history = []
        self.context = {}
        
        logger.info(f"Создан агент '{self.config.name}' с моделью {model}")
    
    async def run(self, input_text: str, context: Optional[Dict] = None) -> str:
        """
        Выполнить задачу и вернуть результат
        
        Args:
            input_text: Входной текст/запрос
            context: Дополнительный контекст
            
        Returns:
            Ответ агента
        """
        try:
            # Используем IntellectualAgent для реального выполнения
            from .intellectual_agent import IntellectualAgent
            
            subtask = {
                "description": input_text,
                "type": "general"
            }
            
            intellectual_agent = IntellectualAgent(self.config.name, subtask)
            result = await intellectual_agent.execute_task()
            
            if result.get("status") == "completed":
                return result.get("output", "Задача выполнена")
            else:
                return f"Ошибка: {result.get('error', 'Неизвестная ошибка')}"
            
        except Exception as e:
            logger.error(f"Ошибка выполнения агента: {e}")
            return f"Извините, произошла ошибка: {str(e)}"
    
    def stream(self, input_text: str, context: Optional[Dict] = None) -> Iterator[str]:
        """
        Стриминг ответов агента
        
        Args:
            input_text: Входной текст
            context: Дополнительный контекст
            
        Yields:
            Части ответа агента
        """
        try:
            if context:
                self.context.update(context)
                
            full_prompt = self._build_prompt(input_text)
            
            # Стриминг от LLM
            for chunk in self.llm.stream(full_prompt):
                yield chunk
                
        except Exception as e:
            logger.error(f"Ошибка стриминга: {e}")
            yield f"Ошибка: {str(e)}"
    
    def add_tool(self, tool: Tool) -> None:
        """Добавить инструмент к агенту"""
        self.tools[tool.name] = tool
        logger.info(f"Добавлен инструмент: {tool.name}")
    
    def remove_tool(self, tool_name: str) -> None:
        """Удалить инструмент"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Удален инструмент: {tool_name}")
    
    def get_memory_summary(self) -> str:
        """Получить краткую сводку памяти"""
        return self.memory.get_summary()
    
    def reset_memory(self) -> None:
        """Очистить память агента"""
        self.memory.clear()
        self.conversation_history = []
        self.context = {}
        logger.info("Память агента очищена")
    
    def export_state(self) -> Dict[str, Any]:
        """Экспортировать состояние агента"""
        return {
            "prompt": self.prompt,
            "config": self.config.__dict__,
            "tools": list(self.tools.keys()),
            "memory_summary": self.memory.get_summary(),
            "created_at": self.created_at.isoformat(),
            "conversation_count": len(self.conversation_history)
        }
    
    def _init_llm(self, model: str) -> LLMProvider:
        """Инициализировать LLM провайдер"""
        try:
            from ..llm import get_llm_provider, LLMConfig
            config = LLMConfig(model=model)
            return get_llm_provider(model, config)
        except ImportError:
            # Fallback - создаём простой провайдер
            logger.warning("LLM модуль не найден, используется локальный провайдер")
            return SimpleLocalLLMProvider()
    
    def _build_prompt(self, input_text: str) -> str:
        """Построить полный промпт для LLM"""
        parts = [
            f"System: {self.prompt}",
            "",
        ]
        
        # Добавляем информацию об инструментах
        if self.tools:
            tools_info = "\n".join([
                f"- {name}: {tool.description}" 
                for name, tool in self.tools.items()
            ])
            parts.extend([
                "Available tools:",
                tools_info,
                ""
            ])
        
        # Добавляем контекст из памяти
        if self.memory.has_relevant_context(input_text):
            context = self.memory.get_relevant_context(input_text)
            parts.extend([
                "Relevant context:",
                context,
                ""
            ])
        
        # Добавляем историю (последние 5 сообщений)
        if self.conversation_history:
            recent_history = self.conversation_history[-5:]
            for entry in recent_history:
                parts.extend([
                    f"User: {entry['user']}",
                    f"Assistant: {entry['assistant']}",
                    ""
                ])
        
        # Добавляем текущий запрос
        parts.append(f"User: {input_text}")
        parts.append("Assistant:")
        
        return "\n".join(parts)
    
    def _get_llm_response(self, prompt: str) -> str:
        """Получить ответ от LLM"""
        return self.llm.complete(
            prompt,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
    
    def _has_tool_calls(self, response: str) -> bool:
        """Проверить есть ли в ответе вызовы инструментов"""
        # Простая проверка на наличие паттернов вызова инструментов
        return any(f"[{tool_name}]" in response for tool_name in self.tools.keys())
    
    def _execute_tools(self, response: str) -> str:
        """Выполнить инструменты из ответа"""
        # Упрощенная реализация - в production должна быть более сложная
        for tool_name, tool in self.tools.items():
            if f"[{tool_name}]" in response:
                try:
                    result = tool.execute()
                    response = response.replace(f"[{tool_name}]", str(result))
                except Exception as e:
                    response = response.replace(
                        f"[{tool_name}]", 
                        f"Error executing {tool_name}: {e}"
                    )
        return response
    
    def _save_to_memory(self, user_input: str, agent_response: str) -> None:
        """Сохранить диалог в память"""
        # Сохраняем в историю разговоров
        self.conversation_history.append({
            "user": user_input,
            "assistant": agent_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Сохраняем в долгосрочную память
        self.memory.store(user_input, agent_response, self.context)


class SimpleLocalLLMProvider:
    """Простой локальный LLM провайдер для fallback"""
    
    def complete(self, prompt: str, **kwargs) -> str:
        """Анализ промпта и генерация ответа"""
        prompt_lower = prompt.lower()
        
        # Анализ задач
        if "система:" in prompt_lower and any(word in prompt_lower for word in ["анализ", "задача"]):
            return "Проанализировал задачу. Определил сложность и требования к выполнению."
            
        # Планирование
        elif "план" in prompt_lower or "этап" in prompt_lower:
            return """План выполнения:
1. Анализ требований
2. Выбор подходящих инструментов
3. Реализация решения
4. Проверка результата"""
            
        # Создание контента
        elif any(word in prompt_lower for word in ["создать", "написать", "генерировать"]):
            if "python" in prompt_lower:
                return "Создам Python скрипт с необходимой функциональностью"
            elif "html" in prompt_lower:
                return "Создам HTML страницу с современным дизайном"
            elif "файл" in prompt_lower:
                return "Создам файл с требуемым содержимым"
            else:
                return "Создам необходимый контент согласно требованиям"
                
        # Общий ответ
        else:
            return f"Обрабатываю задачу: {prompt[:100]}..."
    
    def stream(self, prompt: str, **kwargs) -> Iterator[str]:
        response = self.complete(prompt, **kwargs)
        for word in response.split():
            yield word + " " 