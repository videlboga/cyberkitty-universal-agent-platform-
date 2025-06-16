"""
🧬 Memory Evolution - Эволюция коллективной памяти команд агентов

Система автоматической эволюции памяти на основе A-MEM принципов.
Агенты не просто сохраняют воспоминания - они создают связи между ними,
анализируют паттерны работы команды и генерируют мета-знания.

Принцип: "Память эволюционирует, команды становятся умнее" 🧬
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class TeamPattern:
    """Паттерн работы команды агентов"""
    pattern_id: str
    team_id: str
    pattern_type: str  # "success", "failure", "optimization", "collaboration"
    description: str
    frequency: int
    confidence: float
    examples: List[str]
    created_at: datetime

@dataclass
class MemoryLink:
    """Связь между воспоминаниями"""
    link_id: str
    source_memory: str
    target_memory: str
    link_type: str  # "causal", "similar", "sequence", "contradiction"
    strength: float  # 0.0 - 1.0
    created_at: datetime

class TeamMemoryEvolution:
    """Эволюция коллективной памяти команд агентов"""
    
    def __init__(self, enhanced_memory_system=None):
        self.enhanced_memory = enhanced_memory_system
        self.team_patterns: Dict[str, List[TeamPattern]] = {}
        self.memory_links: Dict[str, List[MemoryLink]] = {}
        self.evolution_history: List[Dict[str, Any]] = []
        
        logger.info("🧬 TeamMemoryEvolution инициализирован")
    
    async def evolve_team_memory(self, team_id: str) -> Dict[str, Any]:
        """Эволюция коллективной памяти команды"""
        try:
            logger.info(f"🔄 Начинаем эволюцию памяти команды: {team_id}")
            
            # 1. Сбор воспоминаний команды
            team_memories = await self._collect_team_memories(team_id)
            
            if len(team_memories) < 3:
                logger.info(f"⏭️ Недостаточно воспоминаний для эволюции команды {team_id}")
                return {"status": "insufficient_data", "memories_count": len(team_memories)}
            
            # 2. Анализ паттернов работы команды
            patterns = await self._analyze_team_patterns(team_memories)
            
            # 3. Создание связей между воспоминаниями
            links = await self._create_memory_links(team_memories)
            
            # 4. Генерация мета-памяти команды
            meta_memory = await self._create_team_meta_memory(team_id, patterns, links)
            
            # 5. Сохранение результатов эволюции
            evolution_result = {
                "team_id": team_id,
                "memories_analyzed": len(team_memories),
                "patterns_discovered": len(patterns),
                "links_created": len(links),
                "meta_memory_id": meta_memory,
                "timestamp": datetime.now().isoformat()
            }
            
            self.evolution_history.append(evolution_result)
            logger.info(f"✅ Эволюция команды {team_id} завершена: {len(patterns)} паттернов, {len(links)} связей")
            
            return evolution_result
            
        except Exception as e:
            logger.error(f"❌ Ошибка эволюции памяти команды {team_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _collect_team_memories(self, team_id: str) -> List[Dict[str, Any]]:
        """Сбор всех воспоминаний команды"""
        if not self.enhanced_memory:
            logger.warning("⚠️ Enhanced memory system не подключена")
            return []
        
        try:
            # Поиск всех воспоминаний команды
            memories = await self.enhanced_memory.collective_search(
                query="",  # пустой запрос = все воспоминания
                team_id=team_id
            )
            
            logger.debug(f"📚 Собрано {len(memories)} воспоминаний команды {team_id}")
            return memories
            
        except Exception as e:
            logger.error(f"❌ Ошибка сбора воспоминаний: {e}")
            return []
    
    async def _analyze_team_patterns(self, memories: List[Dict[str, Any]]) -> List[TeamPattern]:
        """Анализ паттернов работы команды"""
        patterns = []
        
        try:
            # Простой анализ паттернов (можно расширить LLM)
            
            # Паттерн 1: Успешные задачи
            success_memories = [m for m in memories if 'success' in m.get('content', '').lower()]
            if len(success_memories) >= 2:
                pattern = TeamPattern(
                    pattern_id=f"success_{datetime.now().timestamp()}",
                    team_id=memories[0].get('agent_id', 'unknown').split('_')[0] if memories else 'unknown',
                    pattern_type="success",
                    description=f"Команда показывает стабильные успешные результаты ({len(success_memories)} из {len(memories)} задач)",
                    frequency=len(success_memories),
                    confidence=len(success_memories) / len(memories),
                    examples=[m.get('content', '')[:100] for m in success_memories[:3]],
                    created_at=datetime.now()
                )
                patterns.append(pattern)
            
            # Паттерн 2: Типы задач
            task_types = {}
            for memory in memories:
                tags = memory.get('tags', [])
                for tag in tags:
                    if tag not in ['agent', 'memory', 'team']:  # исключаем служебные теги
                        task_types[tag] = task_types.get(tag, 0) + 1
            
            if task_types:
                most_common = max(task_types.items(), key=lambda x: x[1])
                if most_common[1] >= 2:
                    pattern = TeamPattern(
                        pattern_id=f"specialty_{datetime.now().timestamp()}",
                        team_id=memories[0].get('agent_id', 'unknown').split('_')[0] if memories else 'unknown',
                        pattern_type="specialization",
                        description=f"Команда специализируется на задачах типа '{most_common[0]}' ({most_common[1]} задач)",
                        frequency=most_common[1],
                        confidence=most_common[1] / len(memories),
                        examples=[m.get('content', '')[:100] for m in memories if most_common[0] in m.get('tags', [])][:3],
                        created_at=datetime.now()
                    )
                    patterns.append(pattern)
            
            logger.info(f"📊 Обнаружено {len(patterns)} паттернов команды")
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа паттернов: {e}")
            return []
    
    async def _create_memory_links(self, memories: List[Dict[str, Any]]) -> List[MemoryLink]:
        """Создание связей между воспоминаниями"""
        links = []
        
        try:
            # Простое создание связей на основе похожих тегов и контента
            for i, memory1 in enumerate(memories):
                for j, memory2 in enumerate(memories[i+1:], i+1):
                    
                    # Связь по общим тегам
                    tags1 = set(memory1.get('tags', []))
                    tags2 = set(memory2.get('tags', []))
                    common_tags = tags1.intersection(tags2)
                    
                    if len(common_tags) >= 2:  # минимум 2 общих тега
                        link = MemoryLink(
                            link_id=f"link_{datetime.now().timestamp()}_{i}_{j}",
                            source_memory=memory1.get('id', ''),
                            target_memory=memory2.get('id', ''),
                            link_type="similar",
                            strength=len(common_tags) / max(len(tags1), len(tags2), 1),
                            created_at=datetime.now()
                        )
                        links.append(link)
                    
                    # Связь по времени (последовательность)
                    if abs(i - j) == 1:  # соседние по времени воспоминания
                        link = MemoryLink(
                            link_id=f"sequence_{datetime.now().timestamp()}_{i}_{j}",
                            source_memory=memory1.get('id', ''),
                            target_memory=memory2.get('id', ''),
                            link_type="sequence",
                            strength=0.7,  # средняя сила связи
                            created_at=datetime.now()
                        )
                        links.append(link)
            
            logger.info(f"🔗 Создано {len(links)} связей между воспоминаниями")
            return links
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания связей: {e}")
            return []
    
    async def _create_team_meta_memory(self, team_id: str, patterns: List[TeamPattern], 
                                     links: List[MemoryLink]) -> Optional[str]:
        """Создание мета-памяти команды"""
        try:
            if not self.enhanced_memory:
                return None
            
            # Формирование мета-памяти на основе паттернов
            meta_content_parts = [
                f"🧬 МЕТА-ПАМЯТЬ КОМАНДЫ {team_id}",
                f"Анализ от: {datetime.now().isoformat()}",
                "",
                "📊 ОБНАРУЖЕННЫЕ ПАТТЕРНЫ:"
            ]
            
            for pattern in patterns:
                meta_content_parts.extend([
                    f"• {pattern.pattern_type.upper()}: {pattern.description}",
                    f"  Уверенность: {pattern.confidence:.2f}, Частота: {pattern.frequency}"
                ])
            
            meta_content_parts.extend([
                "",
                f"🔗 СВЯЗИ МЕЖДУ ВОСПОМИНАНИЯМИ: {len(links)}",
                f"• Связи по сходству: {len([l for l in links if l.link_type == 'similar'])}",
                f"• Последовательные связи: {len([l for l in links if l.link_type == 'sequence'])}",
                "",
                "🎯 ВЫВОДЫ:",
                f"Команда {team_id} показывает {len(patterns)} различных паттернов работы.",
                f"Обнаружено {len(links)} связей между воспоминаниями, что указывает на",
                "структурированное накопление опыта и потенциал для улучшения."
            ])
            
            meta_content = "\n".join(meta_content_parts)
            
            # Сохранение мета-памяти
            meta_memory_id = await self.enhanced_memory.agent_remember(
                agent_id=f"meta_evolution_{team_id}",
                memory=meta_content,
                context={
                    "team_id": team_id,
                    "category": "team_meta_memory",
                    "patterns_count": len(patterns),
                    "links_count": len(links),
                    "evolution_timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"🧠 Мета-память команды создана: {meta_memory_id}")
            return meta_memory_id
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания мета-памяти: {e}")
            return None 