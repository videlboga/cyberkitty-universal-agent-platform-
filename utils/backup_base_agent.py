"""
Базовый агент для KittyCore 3.0
Теперь использует LLM для интеллектуального анализа и выполнения
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from .intellectual_agent import IntellectualAgent
# Абсолютный импорт LLMProvider
from kittycore.llm import get_llm_provider, LLMProvider

logger = logging.getLogger(__name__)


class Agent:
    """
    Базовый агент KittyCore 3.0
    Использует IntellectualAgent для LLM-ориентированного выполнения задач
    """
    
    def __init__(self, agent_id: str, name: str = None):
        self.agent_id = agent_id
        self.name = name or f"Agent_{agent_id}"
        self.intellectual_agent = IntellectualAgent()
        logger.info(f"Инициализирован {self.name}")
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Выполняет задачу используя IntellectualAgent
        """
        try:
            logger.info(f"🤖 {self} начинает работу: {task}")
            
            # Делегируем выполнение IntellectualAgent
            result = await self.intellectual_agent.execute_task(task, context or {})
            
            logger.info(f"✅ Шаг выполнен: {task}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения агента {self.name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "task": task
            }
    
    def __str__(self):
        return f"Agent({self.name})"
    
    def __repr__(self):
        return f"Agent(id={self.agent_id}, name={self.name})" 