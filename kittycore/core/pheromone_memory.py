#!/usr/bin/env python3
"""
🐜 Pheromone Memory System - Феромонная память как у муравьёв

Агенты оставляют "феромонные следы" успешных решений.
Система накапливает коллективный опыт и автоматически оптимизирует выбор подходов.

Принцип: "Успешные пути становятся сильнее, неудачные - слабеют" 🐜
"""

import json
import time
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PheromoneTrail:
    """Феромонный след для конкретного решения"""
    
    trail_id: str
    task_type: str          # тип задачи (coding, analysis, design, etc.)
    solution_pattern: str   # паттерн решения
    strength: float         # сила феромона (0.0 - 1.0)
    success_count: int      # количество успешных использований
    failure_count: int      # количество неудачных использований
    last_used: datetime     # когда последний раз использовался
    created_at: datetime    # когда создан
    
    @property
    def success_rate(self) -> float:
        """Процент успешности"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
    
    @property
    def is_expired(self) -> bool:
        """Проверка на устаревание (не использовался > 7 дней)"""
        return (datetime.now() - self.last_used).days > 7

@dataclass 
class TaskPheromones:
    """Феромоны для конкретного типа задач"""
    
    task_type: str
    trails: Dict[str, PheromoneTrail]  # solution_pattern -> trail
    total_attempts: int = 0
    successful_attempts: int = 0
    
    @property
    def overall_success_rate(self) -> float:
        """Общий процент успешности для типа задач"""
        return self.successful_attempts / self.total_attempts if self.total_attempts > 0 else 0.0
    
    def get_strongest_trails(self, limit: int = 3) -> List[PheromoneTrail]:
        """Получить самые сильные феромонные следы"""
        sorted_trails = sorted(
            self.trails.values(),
            key=lambda t: t.strength * t.success_rate,
            reverse=True
        )
        return sorted_trails[:limit]

@dataclass
class AgentPheromones:
    """Феромоны для комбинаций агентов"""
    
    agent_combination: str  # например "CodeAgent+AnalysisAgent"
    task_types: List[str]   # типы задач где эта комбинация работает
    strength: float
    usage_count: int
    success_rate: float
    last_used: datetime

class PheromoneMemorySystem:
    """Феромонная память системы - как у муравьёв"""
    
    def __init__(self, storage_path: str = "pheromone_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Основные хранилища феромонов
        self.task_pheromones: Dict[str, TaskPheromones] = {}
        self.agent_pheromones: Dict[str, AgentPheromones] = {}
        self.tool_pheromones: Dict[str, Dict[str, float]] = {}
        
        # Настройки системы
        self.evaporation_rate = 0.1  # скорость испарения феромонов
        self.reinforcement_factor = 1.5  # усиление при успехе
        self.min_strength = 0.1  # минимальная сила феромона
        
        logger.info("🐜 PheromoneMemorySystem инициализирован")
        self._load_pheromones()
    
    def record_solution_success(self, task_type: str, solution_pattern: str, 
                              agent_combination: str, tools_used: List[str], 
                              success: bool) -> None:
        """Записать результат использования решения"""
        
        try:
            # 1. Обновить феромоны задач
            self._update_task_pheromones(task_type, solution_pattern, success)
            
            # 2. Обновить феромоны агентов
            self._update_agent_pheromones(agent_combination, task_type, success)
            
            # 3. Обновить феромоны инструментов
            self._update_tool_pheromones(tools_used, task_type, success)
            
            logger.info(f"🐜 Записан феромонный след: {task_type} -> {solution_pattern} (success={success})")
            
        except Exception as e:
            logger.error(f"❌ Ошибка записи феромонного следа: {e}")
    
    def get_best_solution_patterns(self, task_type: str, limit: int = 3) -> List[str]:
        """Получить лучшие паттерны решений для типа задач"""
        
        if task_type not in self.task_pheromones:
            logger.info(f"⚠️ Нет феромонных данных для типа задач: {task_type}")
            return []
        
        strongest_trails = self.task_pheromones[task_type].get_strongest_trails(limit)
        patterns = [trail.solution_pattern for trail in strongest_trails]
        
        logger.debug(f"🎯 Лучшие паттерны для {task_type}: {patterns}")
        return patterns
    
    def _update_task_pheromones(self, task_type: str, solution_pattern: str, success: bool) -> None:
        """Обновить феромоны для типа задач"""
        
        # Создать TaskPheromones если не существует
        if task_type not in self.task_pheromones:
            self.task_pheromones[task_type] = TaskPheromones(
                task_type=task_type,
                trails={}
            )
        
        task_pheromones = self.task_pheromones[task_type]
        task_pheromones.total_attempts += 1
        
        if success:
            task_pheromones.successful_attempts += 1
        
        # Создать или обновить след
        if solution_pattern not in task_pheromones.trails:
            # Создать новый след
            trail_id = f"{task_type}_{solution_pattern}_{int(time.time())}"
            task_pheromones.trails[solution_pattern] = PheromoneTrail(
                trail_id=trail_id,
                task_type=task_type,
                solution_pattern=solution_pattern,
                strength=0.5,  # начальная сила
                success_count=1 if success else 0,
                failure_count=0 if success else 1,
                last_used=datetime.now(),
                created_at=datetime.now()
            )
        else:
            # Обновить существующий след
            trail = task_pheromones.trails[solution_pattern]
            trail.last_used = datetime.now()
            
            if success:
                trail.success_count += 1
                # Усилить феромон при успехе
                trail.strength = min(1.0, trail.strength * self.reinforcement_factor)
            else:
                trail.failure_count += 1
                # Ослабить феромон при неудаче
                trail.strength = max(self.min_strength, trail.strength * (1 - self.evaporation_rate))
    
    def _update_agent_pheromones(self, agent_combination: str, task_type: str, success: bool) -> None:
        """Обновить феромоны для комбинации агентов"""
        
        if agent_combination not in self.agent_pheromones:
            self.agent_pheromones[agent_combination] = AgentPheromones(
                agent_combination=agent_combination,
                task_types=[task_type],
                strength=0.5,
                usage_count=1,
                success_rate=1.0 if success else 0.0,
                last_used=datetime.now()
            )
        else:
            agent_pheromone = self.agent_pheromones[agent_combination]
            agent_pheromone.usage_count += 1
            agent_pheromone.last_used = datetime.now()
            
            # Добавить тип задач если новый
            if task_type not in agent_pheromone.task_types:
                agent_pheromone.task_types.append(task_type)
            
            # Обновить success_rate
            if success:
                agent_pheromone.success_rate = (
                    agent_pheromone.success_rate * (agent_pheromone.usage_count - 1) + 1.0
                ) / agent_pheromone.usage_count
                agent_pheromone.strength = min(1.0, agent_pheromone.strength * self.reinforcement_factor)
            else:
                agent_pheromone.success_rate = (
                    agent_pheromone.success_rate * (agent_pheromone.usage_count - 1)
                ) / agent_pheromone.usage_count
                agent_pheromone.strength = max(self.min_strength, agent_pheromone.strength * (1 - self.evaporation_rate))
    
    def _update_tool_pheromones(self, tools_used: List[str], task_type: str, success: bool) -> None:
        """Обновить феромоны для инструментов"""
        
        if task_type not in self.tool_pheromones:
            self.tool_pheromones[task_type] = {}
        
        for tool in tools_used:
            if tool not in self.tool_pheromones[task_type]:
                self.tool_pheromones[task_type][tool] = 0.5
            
            if success:
                # Усилить феромон инструмента при успехе
                self.tool_pheromones[task_type][tool] = min(
                    1.0, 
                    self.tool_pheromones[task_type][tool] * self.reinforcement_factor
                )
            else:
                # Ослабить феромон инструмента при неудаче
                self.tool_pheromones[task_type][tool] = max(
                    self.min_strength,
                    self.tool_pheromones[task_type][tool] * (1 - self.evaporation_rate)
                )
    
    def get_best_agent_combination(self, task_type: str) -> Optional[str]:
        """Получить лучшую комбинацию агентов для типа задач"""
        
        best_combination = None
        best_score = 0.0
        
        for combination, pheromone in self.agent_pheromones.items():
            if task_type in pheromone.task_types:
                score = pheromone.strength * pheromone.success_rate
                if score > best_score:
                    best_score = score
                    best_combination = combination
        
        logger.debug(f"🎯 Лучшая комбинация агентов для {task_type}: {best_combination} (score={best_score:.2f})")
        return best_combination
    
    def get_best_tools(self, task_type: str, limit: int = 5) -> List[str]:
        """Получить лучшие инструменты для типа задач"""
        
        if task_type not in self.tool_pheromones:
            logger.info(f"⚠️ Нет данных об инструментах для типа задач: {task_type}")
            return []
        
        # Сортировать инструменты по силе феромона
        sorted_tools = sorted(
            self.tool_pheromones[task_type].items(),
            key=lambda x: x[1],  # сортировать по силе феромона
            reverse=True
        )
        
        best_tools = [tool for tool, strength in sorted_tools[:limit]]
        logger.debug(f"🎯 Лучшие инструменты для {task_type}: {best_tools}")
        return best_tools
    
    def evaporate_pheromones(self) -> None:
        """Испарение феромонов (вызывать периодически)"""
        
        try:
            evaporated_count = 0
            
            # Испарение феромонов задач
            for task_type, task_pheromones in self.task_pheromones.items():
                trails_to_remove = []
                
                for pattern, trail in task_pheromones.trails.items():
                    # Испарить феромон
                    trail.strength *= (1 - self.evaporation_rate)
                    
                    # Удалить слабые или устаревшие следы
                    if trail.strength < self.min_strength or trail.is_expired:
                        trails_to_remove.append(pattern)
                        evaporated_count += 1
                
                for pattern in trails_to_remove:
                    del task_pheromones.trails[pattern]
            
            # Испарение феромонов агентов
            agents_to_remove = []
            for combination, pheromone in self.agent_pheromones.items():
                pheromone.strength *= (1 - self.evaporation_rate)
                
                # Удалить слабые агентные комбинации
                if pheromone.strength < self.min_strength:
                    agents_to_remove.append(combination)
                    evaporated_count += 1
            
            for combination in agents_to_remove:
                del self.agent_pheromones[combination]
            
            # Испарение феромонов инструментов
            for task_type, tools in self.tool_pheromones.items():
                tools_to_remove = []
                for tool, strength in tools.items():
                    new_strength = strength * (1 - self.evaporation_rate)
                    if new_strength < self.min_strength:
                        tools_to_remove.append(tool)
                        evaporated_count += 1
                    else:
                        tools[tool] = new_strength
                
                for tool in tools_to_remove:
                    del tools[tool]
            
            if evaporated_count > 0:
                logger.info(f"💨 Испарено {evaporated_count} слабых феромонных следов")
                
        except Exception as e:
            logger.error(f"❌ Ошибка испарения феромонов: {e}")
    
    def _save_pheromones(self) -> None:
        """Сохранить феромоны в файл"""
        
        try:
            data = {
                'task_pheromones': {},
                'agent_pheromones': {},
                'tool_pheromones': self.tool_pheromones,
                'saved_at': datetime.now().isoformat()
            }
            
            # Сериализовать задачные феромоны
            for task_type, task_pheromones in self.task_pheromones.items():
                data['task_pheromones'][task_type] = {
                    'task_type': task_pheromones.task_type,
                    'total_attempts': task_pheromones.total_attempts,
                    'successful_attempts': task_pheromones.successful_attempts,
                    'trails': {}
                }
                
                for pattern, trail in task_pheromones.trails.items():
                    data['task_pheromones'][task_type]['trails'][pattern] = {
                        'trail_id': trail.trail_id,
                        'task_type': trail.task_type,
                        'solution_pattern': trail.solution_pattern,
                        'strength': trail.strength,
                        'success_count': trail.success_count,
                        'failure_count': trail.failure_count,
                        'last_used': trail.last_used.isoformat(),
                        'created_at': trail.created_at.isoformat()
                    }
            
            # Сериализовать агентные феромоны
            for combination, pheromone in self.agent_pheromones.items():
                data['agent_pheromones'][combination] = {
                    'agent_combination': pheromone.agent_combination,
                    'task_types': pheromone.task_types,
                    'strength': pheromone.strength,
                    'usage_count': pheromone.usage_count,
                    'success_rate': pheromone.success_rate,
                    'last_used': pheromone.last_used.isoformat()
                }
            
            # Сохранить в файл
            save_path = self.storage_path / "pheromones.json"
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"💾 Феромоны сохранены: {save_path}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения феромонов: {e}")
    
    def _load_pheromones(self) -> None:
        """Загрузить феромоны из файла"""
        
        try:
            load_path = self.storage_path / "pheromones.json"
            
            if not load_path.exists():
                logger.info("📂 Файл феромонов не найден, начинаем с пустой памяти")
                return
            
            with open(load_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Загрузить задачные феромоны
            for task_type, task_data in data.get('task_pheromones', {}).items():
                trails = {}
                for pattern, trail_data in task_data.get('trails', {}).items():
                    trails[pattern] = PheromoneTrail(
                        trail_id=trail_data['trail_id'],
                        task_type=trail_data['task_type'],
                        solution_pattern=trail_data['solution_pattern'],
                        strength=trail_data['strength'],
                        success_count=trail_data['success_count'],
                        failure_count=trail_data['failure_count'],
                        last_used=datetime.fromisoformat(trail_data['last_used']),
                        created_at=datetime.fromisoformat(trail_data['created_at'])
                    )
                
                self.task_pheromones[task_type] = TaskPheromones(
                    task_type=task_data['task_type'],
                    trails=trails,
                    total_attempts=task_data['total_attempts'],
                    successful_attempts=task_data['successful_attempts']
                )
            
            # Загрузить агентные феромоны
            for combination, pheromone_data in data.get('agent_pheromones', {}).items():
                self.agent_pheromones[combination] = AgentPheromones(
                    agent_combination=pheromone_data['agent_combination'],
                    task_types=pheromone_data['task_types'],
                    strength=pheromone_data['strength'],
                    usage_count=pheromone_data['usage_count'],
                    success_rate=pheromone_data['success_rate'],
                    last_used=datetime.fromisoformat(pheromone_data['last_used'])
                )
            
            # Загрузить инструментальные феромоны
            self.tool_pheromones = data.get('tool_pheromones', {})
            
            logger.info(f"📂 Загружены феромоны: {len(self.task_pheromones)} типов задач, {len(self.agent_pheromones)} комбинаций агентов")
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки феромонов: {e}")
    
    def get_pheromone_statistics(self) -> Dict[str, Any]:
        """Получить статистику феромонной системы"""
        
        stats = {
            'task_types': len(self.task_pheromones),
            'agent_combinations': len(self.agent_pheromones),
            'total_trails': sum(len(tp.trails) for tp in self.task_pheromones.values()),
            'strongest_trails': [],
            'best_agents': [],
            'system_health': 0.0
        }
        
        # Найти самые сильные следы
        all_trails = []
        for task_pheromones in self.task_pheromones.values():
            all_trails.extend(task_pheromones.trails.values())
        
        strongest_trails = sorted(all_trails, key=lambda t: t.strength * t.success_rate, reverse=True)[:5]
        stats['strongest_trails'] = [
            {
                'task_type': trail.task_type,
                'solution_pattern': trail.solution_pattern,
                'strength': trail.strength,
                'success_rate': trail.success_rate,
                'usage_count': trail.success_count + trail.failure_count
            }
            for trail in strongest_trails
        ]
        
        # Найти лучших агентов
        best_agents = sorted(
            self.agent_pheromones.values(),
            key=lambda a: a.strength * a.success_rate,
            reverse=True
        )[:5]
        
        stats['best_agents'] = [
            {
                'combination': agent.agent_combination,
                'strength': agent.strength,
                'success_rate': agent.success_rate,
                'usage_count': agent.usage_count,
                'task_types': agent.task_types
            }
            for agent in best_agents
        ]
        
        # Оценить здоровье системы
        if stats['total_trails'] > 0:
            avg_strength = sum(trail.strength for trails in self.task_pheromones.values() for trail in trails.trails.values()) / stats['total_trails']
            stats['system_health'] = min(1.0, avg_strength * (stats['total_trails'] / 10))  # нормализация
        
        return stats
    
    def __del__(self):
        """Деструктор - сохранить феромоны при завершении"""
        try:
            self._save_pheromones()
        except:
            pass  # Игнорировать ошибки при завершении


# === ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР ФЕРОМОННОЙ СИСТЕМЫ ===
_global_pheromone_system: Optional[PheromoneMemorySystem] = None

def get_pheromone_system() -> PheromoneMemorySystem:
    """Получить глобальный экземпляр феромонной системы"""
    global _global_pheromone_system
    
    if _global_pheromone_system is None:
        _global_pheromone_system = PheromoneMemorySystem()
        logger.info("🐜 Создан глобальный экземпляр PheromoneMemorySystem")
    
    return _global_pheromone_system

def record_agent_success(task_type: str, solution_pattern: str, 
                        agent_combination: str, tools_used: List[str], 
                        success: bool) -> None:
    """Удобная функция для записи успеха агента в глобальную феромонную систему"""
    
    pheromone_system = get_pheromone_system()
    pheromone_system.record_solution_success(
        task_type=task_type,
        solution_pattern=solution_pattern,
        agent_combination=agent_combination,
        tools_used=tools_used,
        success=success
    )

def get_optimal_approach(task_type: str) -> Dict[str, Any]:
    """Получить оптимальный подход для типа задач на основе феромонов"""
    
    pheromone_system = get_pheromone_system()
    
    return {
        'task_type': task_type,
        'best_solution_patterns': pheromone_system.get_best_solution_patterns(task_type),
        'best_agent_combination': pheromone_system.get_best_agent_combination(task_type),
        'best_tools': pheromone_system.get_best_tools(task_type),
        'confidence': _calculate_confidence(task_type, pheromone_system)
    }

def _calculate_confidence(task_type: str, pheromone_system: PheromoneMemorySystem) -> float:
    """Рассчитать уверенность в рекомендациях для типа задач"""
    
    if task_type not in pheromone_system.task_pheromones:
        return 0.0
    
    task_pheromones = pheromone_system.task_pheromones[task_type]
    
    # Уверенность основана на количестве попыток и проценте успеха
    if task_pheromones.total_attempts == 0:
        return 0.0
    
    # Нормализованная уверенность (больше попыток = больше уверенности)
    attempt_confidence = min(1.0, task_pheromones.total_attempts / 10)
    success_confidence = task_pheromones.overall_success_rate
    
    return (attempt_confidence + success_confidence) / 2


if __name__ == "__main__":
    # Простой тест системы
    logging.basicConfig(level=logging.INFO)
    
    print("🐜 Тест PheromoneMemorySystem")
    
    # Создать систему
    pheromone_system = PheromoneMemorySystem("test_pheromone_storage")
    
    # Симуляция работы агентов
    test_scenarios = [
        ("coding", "python_script", "CodeAgent", ["code_generator", "file_manager"], True),
        ("coding", "python_script", "CodeAgent", ["code_generator", "file_manager"], True),
        ("coding", "web_scraping", "CodeAgent+WebAgent", ["web_scraping", "data_analysis"], False),
        ("analysis", "data_analysis", "AnalysisAgent", ["data_analysis", "visualization"], True),
        ("coding", "python_script", "CodeAgent", ["code_generator", "file_manager"], True),
    ]
    
    print("\n📊 Записываем результаты агентов...")
    for task_type, pattern, agents, tools, success in test_scenarios:
        pheromone_system.record_solution_success(task_type, pattern, agents, tools, success)
        print(f"  {task_type} -> {pattern} ({'✅' if success else '❌'})")
    
    print("\n🎯 Получаем рекомендации...")
    
    # Тест рекомендаций для coding
    coding_approach = get_optimal_approach("coding")
    print(f"Coding: {coding_approach}")
    
    # Тест рекомендаций для analysis  
    analysis_approach = get_optimal_approach("analysis")
    print(f"Analysis: {analysis_approach}")
    
    # Статистика системы
    stats = pheromone_system.get_pheromone_statistics()
    print(f"\n📈 Статистика системы:")
    print(f"  Типов задач: {stats['task_types']}")
    print(f"  Комбинаций агентов: {stats['agent_combinations']}")
    print(f"  Всего следов: {stats['total_trails']}")
    print(f"  Здоровье системы: {stats['system_health']:.2f}")
    
    print("\n✅ Тест завершён!") 