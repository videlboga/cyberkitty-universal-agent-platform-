"""
🧠 CollectiveMemory - Коллективная память для команд агентов KittyCore 3.0

Ключевые особенности:
- Общая память между агентами команды  
- Синхронизация состояния команды
- Кросс-агентные воспоминания
- Коллективное обучение

Принцип: "Агенты команды думают вместе" 🚀
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime 

@dataclass
class TeamMemoryEntry:
    """Запись в коллективной памяти команды"""
    id: str
    content: str
    author_agent: str
    team_id: str
    timestamp: datetime
    tags: List[str]
    importance: float = 0.5 

class CollectiveMemory:
    """Коллективная память команды агентов"""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.memories: Dict[str, TeamMemoryEntry] = {}
        self.agent_contributions: Dict[str, int] = {} 

    async def store(self, content: str, agent_id: str, tags: List[str] = None) -> str:
        """Сохранить воспоминание от агента"""
        entry_id = f"{agent_id}_{len(self.memories)}"
        entry = TeamMemoryEntry(
            id=entry_id,
            content=content,
            author_agent=agent_id, 
            team_id=self.team_id,
            timestamp=datetime.now(),
            tags=tags or []
        )
        self.memories[entry_id] = entry
        self.agent_contributions[agent_id] = self.agent_contributions.get(agent_id, 0) + 1
        return entry_id 

    async def search(self, query: str, limit: int = 5) -> List[TeamMemoryEntry]:
        """Поиск в коллективной памяти"""
        results = []
        for memory in self.memories.values():
            if query.lower() in memory.content.lower():
                results.append(memory)
        
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:limit]

    async def add_memory(self, agent_id: str, memory_data: Dict[str, Any]) -> str:
        """Добавить память (псевдоним для store для совместимости с тестами)"""
        content = memory_data.get("task", "") + " " + memory_data.get("result", "")
        tags = ["память", "тест"]
        return await self.store(content, agent_id, tags)

    async def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Поиск воспоминаний (псевдоним для search для совместимости)"""
        memories = await self.search(query, limit)
        return [{"content": m.content, "agent": m.author_agent, "timestamp": m.timestamp} for m in memories] 

    def get_team_stats(self) -> Dict[str, Any]:
        """Статистика коллективной памяти команды"""
        return {
            "team_id": self.team_id,
            "total_memories": len(self.memories),
            "agents_count": len(self.agent_contributions),
            "agent_contributions": self.agent_contributions,
            "avg_importance": sum(m.importance for m in self.memories.values()) / max(1, len(self.memories))
        } 