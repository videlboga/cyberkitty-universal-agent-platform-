"""
🧠 СИСТЕМА НАКОПЛЕНИЯ ЗНАНИЙ АГЕНТОВ
Агенты учатся от ошибок и накапливают опыт между попытками
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from loguru import logger

@dataclass
class LearningEntry:
    """Запись об обучении агента"""
    timestamp: str
    task_description: str
    attempt_number: int
    score_before: float
    score_after: float
    error_patterns: List[str]
    successful_actions: List[str]
    failed_actions: List[str]
    feedback_received: str
    tools_used: List[str]
    lesson_learned: str

@dataclass
class AgentKnowledge:
    """База знаний агента"""
    agent_id: str
    total_attempts: int
    successful_patterns: List[str]
    error_patterns: List[str]
    tool_preferences: Dict[str, int]  # tool_name -> success_count
    lessons_learned: List[str]
    last_updated: str

class AgentLearningSystem:
    """Система накопления знаний агентов"""
    
    def __init__(self, vault_path: str = "obsidian_vault"):
        self.vault_path = Path(vault_path)
        self.knowledge_dir = self.vault_path / "knowledge"
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        # Кэш знаний агентов
        self.agent_knowledge: Dict[str, AgentKnowledge] = {}
        
    async def record_learning(
        self,
        agent_id: str,
        task_description: str,
        attempt_number: int,
        score_before: float,
        score_after: float,
        error_patterns: List[str],
        successful_actions: List[str],
        failed_actions: List[str],
        feedback_received: str,
        tools_used: List[str]
    ) -> str:
        """Записывает опыт обучения агента"""
        
        # Анализируем урок
        lesson_learned = await self._extract_lesson(
            error_patterns, successful_actions, failed_actions, feedback_received
        )
        
        # Создаём запись
        entry = LearningEntry(
            timestamp=datetime.now().isoformat(),
            task_description=task_description,
            attempt_number=attempt_number,
            score_before=score_before,
            score_after=score_after,
            error_patterns=error_patterns,
            successful_actions=successful_actions,
            failed_actions=failed_actions,
            feedback_received=feedback_received,
            tools_used=tools_used,
            lesson_learned=lesson_learned
        )
        
        # Обновляем базу знаний агента
        await self._update_agent_knowledge(agent_id, entry)
        
        # Сохраняем в Obsidian vault
        await self._save_learning_entry(agent_id, entry)
        
        logger.info(f"🧠 Агент {agent_id} изучил урок: {lesson_learned}")
        
        return lesson_learned
    
    async def get_agent_knowledge(self, agent_id: str) -> AgentKnowledge:
        """Получает накопленные знания агента"""
        
        if agent_id not in self.agent_knowledge:
            await self._load_agent_knowledge(agent_id)
        
        return self.agent_knowledge.get(agent_id, AgentKnowledge(
            agent_id=agent_id,
            total_attempts=0,
            successful_patterns=[],
            error_patterns=[],
            tool_preferences={},
            lessons_learned=[],
            last_updated=datetime.now().isoformat()
        ))
    
    async def get_improvement_suggestions(
        self, 
        agent_id: str, 
        current_task: str,
        current_errors: List[str]
    ) -> List[str]:
        """Получает предложения по улучшению на основе накопленных знаний"""
        
        knowledge = await self.get_agent_knowledge(agent_id)
        suggestions = []
        
        # Проверяем известные ошибки
        for error in current_errors:
            for known_error in knowledge.error_patterns:
                if self._similarity(error, known_error) > 0.7:
                    suggestions.append(f"⚠️ Избегай ошибки: {known_error}")
        
        # Предлагаем успешные паттерны
        for pattern in knowledge.successful_patterns[-3:]:  # Последние 3
            suggestions.append(f"✅ Используй успешный паттерн: {pattern}")
        
        # Предлагаем лучшие инструменты
        best_tools = sorted(
            knowledge.tool_preferences.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        for tool, success_count in best_tools:
            if success_count > 1:
                suggestions.append(f"🔧 Рекомендуемый инструмент: {tool} (успехов: {success_count})")
        
        # Добавляем уроки
        for lesson in knowledge.lessons_learned[-2:]:  # Последние 2 урока
            suggestions.append(f"📚 Помни урок: {lesson}")
        
        return suggestions
    
    async def _extract_lesson(
        self,
        error_patterns: List[str],
        successful_actions: List[str],
        failed_actions: List[str],
        feedback: str
    ) -> str:
        """Извлекает урок из опыта"""
        
        if successful_actions and not error_patterns:
            return f"Успешная стратегия: {', '.join(successful_actions[:2])}"
        
        if error_patterns and failed_actions:
            return f"Избегать: {error_patterns[0]} при использовании {failed_actions[0]}"
        
        if "file_manager" in feedback and "создать" in feedback.lower():
            return "Использовать file_manager для создания файлов"
        
        if "code_generator" in feedback and "код" in feedback.lower():
            return "Использовать code_generator для генерации кода"
        
        return "Следовать конкретным инструкциям из фидбека"
    
    async def _update_agent_knowledge(self, agent_id: str, entry: LearningEntry):
        """Обновляет базу знаний агента"""
        
        knowledge = await self.get_agent_knowledge(agent_id)
        
        # Обновляем статистику
        knowledge.total_attempts += 1
        knowledge.last_updated = datetime.now().isoformat()
        
        # Добавляем паттерны
        if entry.score_after > entry.score_before:
            knowledge.successful_patterns.extend(entry.successful_actions)
            knowledge.successful_patterns = list(set(knowledge.successful_patterns))[-10:]  # Последние 10
        
        knowledge.error_patterns.extend(entry.error_patterns)
        knowledge.error_patterns = list(set(knowledge.error_patterns))[-10:]  # Последние 10
        
        # Обновляем предпочтения инструментов
        for tool in entry.tools_used:
            if entry.score_after > entry.score_before:
                knowledge.tool_preferences[tool] = knowledge.tool_preferences.get(tool, 0) + 1
        
        # Добавляем урок
        if entry.lesson_learned not in knowledge.lessons_learned:
            knowledge.lessons_learned.append(entry.lesson_learned)
            knowledge.lessons_learned = knowledge.lessons_learned[-5:]  # Последние 5 уроков
        
        # Сохраняем в кэш
        self.agent_knowledge[agent_id] = knowledge
        
        # Сохраняем в файл
        await self._save_agent_knowledge(agent_id, knowledge)
    
    async def _save_learning_entry(self, agent_id: str, entry: LearningEntry):
        """Сохраняет запись обучения в Obsidian vault"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"learning_{agent_id}_{timestamp}.md"
        filepath = self.knowledge_dir / filename
        
        content = f"""# 🧠 Обучение агента {agent_id}

## Информация о попытке
- **Задача**: {entry.task_description}
- **Попытка**: #{entry.attempt_number}
- **Время**: {entry.timestamp}

## Результаты
- **Оценка до**: {entry.score_before}/1.0
- **Оценка после**: {entry.score_after}/1.0
- **Прогресс**: {'+' if entry.score_after > entry.score_before else '-'}{abs(entry.score_after - entry.score_before):.1f}

## Анализ действий

### ✅ Успешные действия
{chr(10).join(f"- {action}" for action in entry.successful_actions) if entry.successful_actions else "- Нет"}

### ❌ Неудачные действия
{chr(10).join(f"- {action}" for action in entry.failed_actions) if entry.failed_actions else "- Нет"}

### ⚠️ Паттерны ошибок
{chr(10).join(f"- {error}" for error in entry.error_patterns) if entry.error_patterns else "- Нет"}

## 🔧 Использованные инструменты
{', '.join(entry.tools_used) if entry.tools_used else "Нет"}

## 📝 Полученный фидбек
```
{entry.feedback_received}
```

## 📚 Урок
**{entry.lesson_learned}**

---
*Генерировано AgentLearningSystem*
"""
        
        filepath.write_text(content, encoding='utf-8')
    
    async def _save_agent_knowledge(self, agent_id: str, knowledge: AgentKnowledge):
        """Сохраняет базу знаний агента"""
        
        filepath = self.knowledge_dir / f"knowledge_{agent_id}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(knowledge), f, ensure_ascii=False, indent=2)
    
    async def _load_agent_knowledge(self, agent_id: str):
        """Загружает базу знаний агента"""
        
        filepath = self.knowledge_dir / f"knowledge_{agent_id}.json"
        
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.agent_knowledge[agent_id] = AgentKnowledge(**data)
            except Exception as e:
                logger.error(f"Ошибка загрузки знаний агента {agent_id}: {e}")
    
    def _similarity(self, text1: str, text2: str) -> float:
        """Простая оценка схожести текстов"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

# Глобальный экземпляр
learning_system = AgentLearningSystem() 