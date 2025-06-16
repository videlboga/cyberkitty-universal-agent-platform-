"""
🧠 Enhanced Memory - Улучшенная система коллективной памяти

Интеграция A-MEM в существующую систему памяти KittyCore.
Заменяет примитивный VectorMemoryStore на профессиональную агентную память.

Принцип: "Один интерфейс, революционная память" 🚀
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .amem_integration import KittyCoreMemorySystem, get_enhanced_memory_system
from .memory_evolution import TeamMemoryEvolution
from .collective_memory import CollectiveMemory

logger = logging.getLogger(__name__)

class EnhancedCollectiveMemory(CollectiveMemory):
    """Улучшенная коллективная память с A-MEM поддержкой"""
    
    def __init__(self, team_id: str, vault_path: str = "obsidian_vault"):
        super().__init__(team_id)
        
        # A-MEM интеграция
        self.enhanced_memory = get_enhanced_memory_system(vault_path)
        self.memory_evolution = TeamMemoryEvolution(self.enhanced_memory)
        
        # Отслеживание использования A-MEM vs fallback
        self.amem_enabled = True
        
        logger.info(f"🧠 EnhancedCollectiveMemory инициализирована для команды: {team_id}")
    
    async def store(self, content: str, agent_id: str, tags: List[str] = None) -> str:
        """Сохранение с A-MEM эволюцией"""
        try:
            # Используем A-MEM для сохранения
            memory_id = await self.enhanced_memory.agent_remember(
                agent_id=agent_id,
                memory=content,
                context={
                    "team_id": self.team_id,
                    "category": "collective_memory",
                    "tags": tags or [],
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Также сохраняем в старом формате для совместимости
            await super().store(content, agent_id, tags)
            
            logger.info(f"📝 A-MEM сохранение: {memory_id} (агент: {agent_id})")
            return memory_id
            
        except Exception as e:
            logger.error(f"❌ Ошибка A-MEM сохранения: {e}")
            # Fallback на старую систему
            return await super().store(content, agent_id, tags)
    
    async def search(self, query: str, limit: int = 5) -> List[Any]:
        """Семантический поиск через A-MEM"""
        try:
            # Попытка поиска через A-MEM
            amem_results = await self.enhanced_memory.collective_search(
                query=query,
                team_id=self.team_id
            )
            
            if amem_results:
                # Конвертируем A-MEM результаты в старый формат
                converted_results = []
                for result in amem_results[:limit]:
                    # Имитируем TeamMemoryEntry для совместимости
                    class FakeEntry:
                        def __init__(self, data):
                            self.content = data.get('content', '')
                            self.author_agent = data.get('agent_id', 'unknown')
                            self.importance = 0.8  # высокая важность для A-MEM результатов
                            
                    converted_results.append(FakeEntry(result))
                
                logger.info(f"🔍 A-MEM поиск: {len(converted_results)} результатов")
                return converted_results
            
        except Exception as e:
            logger.error(f"❌ Ошибка A-MEM поиска: {e}")
        
        # Fallback на старую систему
        logger.info("🔄 Fallback на классический поиск")
        return await super().search(query, limit)
    
    async def evolve_memory(self) -> Dict[str, Any]:
        """Запуск эволюции памяти команды"""
        try:
            evolution_result = await self.memory_evolution.evolve_team_memory(self.team_id)
            logger.info(f"🧬 Эволюция памяти команды {self.team_id}: {evolution_result}")
            return evolution_result
            
        except Exception as e:
            logger.error(f"❌ Ошибка эволюции памяти: {e}")
            return {"status": "error", "error": str(e)}

class SmartMemoryContext:
    """Умный контекст для агентов на основе A-MEM"""
    
    def __init__(self, enhanced_memory: KittyCoreMemorySystem):
        self.enhanced_memory = enhanced_memory
    
    async def build_context_for_agent(self, agent_id: str, current_task: str, 
                                    team_id: str = None) -> str:
        """Создание умного контекста для агента"""
        try:
            # Поиск релевантного личного опыта агента
            personal_memories = await self.enhanced_memory.collective_search(
                query=current_task,
                team_id=agent_id  # личная память агента
            )
            
            # Поиск релевантного опыта команды
            team_memories = []
            if team_id:
                team_memories = await self.enhanced_memory.collective_search(
                    query=current_task,
                    team_id=team_id
                )
            
            # Построение контекста
            context_parts = ["🧠 КОНТЕКСТ ИЗ ПАМЯТИ:"]
            
            if personal_memories:
                context_parts.append("\n📝 Ваш опыт:")
                for memory in personal_memories[:2]:  # топ-2 личных
                    context_parts.append(f"• {memory.get('content', '')[:150]}...")
            
            if team_memories:
                context_parts.append("\n👥 Опыт команды:")
                for memory in team_memories[:2]:  # топ-2 командных
                    if memory.get('agent_id') != agent_id:  # исключаем собственные
                        context_parts.append(f"• {memory.get('content', '')[:150]}...")
            
            if not personal_memories and not team_memories:
                context_parts.append("\n🆕 Новая задача без предыдущего опыта.")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания контекста: {e}")
            return "🔄 Контекст недоступен (используется базовый режим)"


# === ФАБРИЧНЫЕ ФУНКЦИИ ===

def create_enhanced_collective_memory(team_id: str, 
                                    vault_path: str = "obsidian_vault") -> EnhancedCollectiveMemory:
    """Создание улучшенной коллективной памяти"""
    return EnhancedCollectiveMemory(team_id, vault_path)

def create_smart_memory_context(vault_path: str = "obsidian_vault") -> SmartMemoryContext:
    """Создание умного контекста памяти"""
    enhanced_memory = get_enhanced_memory_system(vault_path)
    return SmartMemoryContext(enhanced_memory) 