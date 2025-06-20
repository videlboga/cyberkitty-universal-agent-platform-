#!/usr/bin/env python3
"""
🧬 EvolutionaryAgentFactory - Эволюционная фабрика агентов KittyCore 3.0

ФАЗА 2: Эволюционная фабрика агентов
Принцип: "Агенты размножаются, наследуют лучшие черты, мутируют и эволюционируют"

Биологические принципы:
🧬 РАЗМНОЖЕНИЕ: Успешные агенты создают потомков
🧠 НАСЛЕДОВАНИЕ: Потомки получают характеристики родителей
🔄 МУТАЦИИ: Случайные изменения для адаптации
⚡ ЕСТЕСТВЕННЫЙ ОТБОР: Выживание самых эффективных
🌱 ЭВОЛЮЦИЯ: Постоянное улучшение популяции
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from loguru import logger

# === ЧАСТЬ 1: БАЗОВЫЕ СТРУКТУРЫ ДАННЫХ ===

@dataclass
class AgentGenes:
    """🧬 Генетический код агента - наследуемые характеристики"""
    
    # Основные характеристики
    agent_type: str = "general"  # Тип агента (code, web, analysis, etc.)
    specialization: List[str] = None  # Специализации агента
    
    # Производительность
    success_rate: float = 0.5  # Коэффициент успеха (0.0-1.0)
    speed_factor: float = 1.0  # Коэффициент скорости (0.5-2.0)
    quality_factor: float = 1.0  # Коэффициент качества (0.5-2.0)
    
    # Предпочтения инструментов
    preferred_tools: List[str] = None  # Любимые инструменты
    tool_efficiency: Dict[str, float] = None  # Эффективность с инструментами
    
    # Адаптивность
    learning_rate: float = 0.1  # Скорость обучения (0.01-0.5)
    mutation_resistance: float = 0.8  # Сопротивление мутациям (0.5-1.0)
    
    # Социальные характеристики
    collaboration_skill: float = 0.7  # Навык работы в команде (0.0-1.0)
    leadership_tendency: float = 0.3  # Склонность к лидерству (0.0-1.0)
    
    def __post_init__(self):
        """Инициализация значений по умолчанию"""
        if self.specialization is None:
            self.specialization = ["general"]
        if self.preferred_tools is None:
            self.preferred_tools = ["general_tools"]
        if self.tool_efficiency is None:
            self.tool_efficiency = {"general_tools": 1.0}

@dataclass
class AgentDNA:
    """🧬 ДНК агента - полная генетическая информация"""
    
    agent_id: str  # Уникальный ID агента
    generation: int = 0  # Поколение агента
    parent_ids: List[str] = None  # ID родителей
    birth_time: datetime = None  # Время создания
    
    # Генетический код
    genes: AgentGenes = None
    
    # История эволюции
    mutations_count: int = 0  # Количество мутаций
    crossover_count: int = 0  # Количество скрещиваний
    
    # Статистика жизни
    tasks_completed: int = 0  # Выполненных задач
    total_success_rate: float = 0.0  # Общий успех
    life_span: timedelta = None  # Продолжительность жизни
    
    def __post_init__(self):
        """Инициализация значений по умолчанию"""
        if self.parent_ids is None:
            self.parent_ids = []
        if self.birth_time is None:
            self.birth_time = datetime.now()
        if self.genes is None:
            self.genes = AgentGenes()

@dataclass
class EvolutionEvent:
    """🔄 Событие эволюции - запись о генетических изменениях"""
    
    event_type: str  # "birth", "mutation", "crossover", "death", "selection"
    timestamp: datetime
    agent_id: str
    
    # Детали события
    parent_ids: List[str] = None  # Для birth/crossover
    mutation_details: Dict[str, Any] = None  # Для mutation
    selection_reason: str = None  # Для selection/death
    
    # Результаты
    fitness_before: float = 0.0
    fitness_after: float = 0.0
    success_improvement: float = 0.0

@dataclass
class PopulationStats:
    """📊 Статистика популяции агентов"""
    
    # Размер популяции
    total_agents: int = 0
    active_agents: int = 0
    retired_agents: int = 0
    
    # Поколения
    max_generation: int = 0
    avg_generation: float = 0.0
    
    # Производительность
    avg_success_rate: float = 0.0
    best_success_rate: float = 0.0
    worst_success_rate: float = 1.0
    
    # Разнообразие
    unique_specializations: int = 0
    genetic_diversity: float = 0.0
    
    # Эволюция
    total_mutations: int = 0
    total_crossovers: int = 0
    evolution_events: int = 0
    
    # Здоровье популяции
    population_health: float = 0.0
    adaptation_rate: float = 0.0

# === ЧАСТЬ 2: ГЕНЕТИЧЕСКИЕ ОПЕРАЦИИ ===

class GeneticOperations:
    """🧬 Генетические операции для эволюции агентов"""
    
    def __init__(self, mutation_rate: float = 0.1, crossover_rate: float = 0.3):
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.random = random.Random()
        self.random.seed(int(time.time()))
    
    def create_initial_agent(self, agent_type: str = "general", specialization: List[str] = None) -> AgentDNA:
        """🌱 Создание начального агента (нулевое поколение)"""
        
        agent_id = f"{agent_type}_{int(time.time())}_{self.random.randint(1000, 9999)}"
        
        # Случайные начальные характеристики с небольшим разбросом
        genes = AgentGenes(
            agent_type=agent_type,
            specialization=specialization or [agent_type],
            success_rate=self.random.uniform(0.3, 0.7),  # Средний старт
            speed_factor=self.random.uniform(0.8, 1.2),
            quality_factor=self.random.uniform(0.8, 1.2),
            preferred_tools=self._generate_initial_tools(agent_type),
            tool_efficiency=self._generate_tool_efficiency(agent_type),
            learning_rate=self.random.uniform(0.05, 0.2),
            mutation_resistance=self.random.uniform(0.7, 0.9),
            collaboration_skill=self.random.uniform(0.5, 0.8),
            leadership_tendency=self.random.uniform(0.2, 0.5)
        )
        
        dna = AgentDNA(
            agent_id=agent_id,
            generation=0,
            genes=genes
        )
        
        logger.info(f"🌱 Создан начальный агент {agent_id} типа {agent_type}")
        return dna
    
    def mutate_agent(self, parent_dna: AgentDNA, mutation_strength: float = 1.0) -> AgentDNA:
        """🔄 Мутация агента - случайные изменения характеристик"""
        
        # Проверяем сопротивление мутациям
        if self.random.random() > (self.mutation_rate * mutation_strength / parent_dna.genes.mutation_resistance):
            return parent_dna  # Мутация не произошла
        
        # Создаём потомка
        child_id = f"mut_{parent_dna.agent_id}_{int(time.time())}"
        child_genes = self._copy_genes(parent_dna.genes)
        
        # Применяем мутации
        mutations = []
        
        # Мутация производительности (±10%)
        if self.random.random() < 0.7:
            old_success = child_genes.success_rate
            child_genes.success_rate = max(0.0, min(1.0, 
                child_genes.success_rate + self.random.uniform(-0.1, 0.1)))
            mutations.append(f"success_rate: {old_success:.2f} → {child_genes.success_rate:.2f}")
        
        # Мутация скорости (±20%)
        if self.random.random() < 0.5:
            old_speed = child_genes.speed_factor
            child_genes.speed_factor = max(0.5, min(2.0,
                child_genes.speed_factor + self.random.uniform(-0.2, 0.2)))
            mutations.append(f"speed_factor: {old_speed:.2f} → {child_genes.speed_factor:.2f}")
        
        # Мутация качества (±15%)
        if self.random.random() < 0.5:
            old_quality = child_genes.quality_factor
            child_genes.quality_factor = max(0.5, min(2.0,
                child_genes.quality_factor + self.random.uniform(-0.15, 0.15)))
            mutations.append(f"quality_factor: {old_quality:.2f} → {child_genes.quality_factor:.2f}")
        
        # Мутация инструментов (добавление/удаление)
        if self.random.random() < 0.3:
            self._mutate_tools(child_genes)
            mutations.append("tools_mutated")
        
        # Мутация социальных навыков
        if self.random.random() < 0.4:
            old_collab = child_genes.collaboration_skill
            child_genes.collaboration_skill = max(0.0, min(1.0,
                child_genes.collaboration_skill + self.random.uniform(-0.1, 0.1)))
            mutations.append(f"collaboration: {old_collab:.2f} → {child_genes.collaboration_skill:.2f}")
        
        # Создаём ДНК потомка
        child_dna = AgentDNA(
            agent_id=child_id,
            generation=parent_dna.generation + 1,
            parent_ids=[parent_dna.agent_id],
            genes=child_genes,
            mutations_count=parent_dna.mutations_count + 1
        )
        
        logger.info(f"🔄 Мутация {parent_dna.agent_id} → {child_id}: {', '.join(mutations)}")
        return child_dna
    
    def crossover_agents(self, parent1_dna: AgentDNA, parent2_dna: AgentDNA) -> AgentDNA:
        """🧬 Скрещивание двух агентов - наследование лучших черт"""
        
        # Создаём ID потомка
        child_id = f"cross_{parent1_dna.agent_id[:8]}_{parent2_dna.agent_id[:8]}_{int(time.time())}"
        
        # Определяем лучшего родителя по успешности
        better_parent = parent1_dna if parent1_dna.total_success_rate >= parent2_dna.total_success_rate else parent2_dna
        worse_parent = parent2_dna if better_parent == parent1_dna else parent1_dna
        
        # Наследуем характеристики (70% от лучшего, 30% от худшего)
        child_genes = AgentGenes()
        
        # Основные характеристики - от лучшего родителя
        child_genes.agent_type = better_parent.genes.agent_type
        child_genes.specialization = list(set(
            better_parent.genes.specialization + worse_parent.genes.specialization
        ))
        
        # Производительность - взвешенное среднее с уклоном к лучшему
        child_genes.success_rate = (
            better_parent.genes.success_rate * 0.7 + 
            worse_parent.genes.success_rate * 0.3
        )
        child_genes.speed_factor = (
            better_parent.genes.speed_factor * 0.6 + 
            worse_parent.genes.speed_factor * 0.4
        )
        child_genes.quality_factor = (
            better_parent.genes.quality_factor * 0.6 + 
            worse_parent.genes.quality_factor * 0.4
        )
        
        # Инструменты - объединение лучших
        child_genes.preferred_tools = self._merge_tools(
            better_parent.genes.preferred_tools,
            worse_parent.genes.preferred_tools
        )
        child_genes.tool_efficiency = self._merge_tool_efficiency(
            better_parent.genes.tool_efficiency,
            worse_parent.genes.tool_efficiency
        )
        
        # Адаптивность - среднее
        child_genes.learning_rate = (
            better_parent.genes.learning_rate + worse_parent.genes.learning_rate
        ) / 2
        child_genes.mutation_resistance = (
            better_parent.genes.mutation_resistance + worse_parent.genes.mutation_resistance
        ) / 2
        
        # Социальные навыки - лучшее из двух
        child_genes.collaboration_skill = max(
            better_parent.genes.collaboration_skill,
            worse_parent.genes.collaboration_skill
        )
        child_genes.leadership_tendency = (
            better_parent.genes.leadership_tendency + worse_parent.genes.leadership_tendency
        ) / 2
        
        # Создаём ДНК потомка
        child_dna = AgentDNA(
            agent_id=child_id,
            generation=max(parent1_dna.generation, parent2_dna.generation) + 1,
            parent_ids=[parent1_dna.agent_id, parent2_dna.agent_id],
            genes=child_genes,
            crossover_count=max(parent1_dna.crossover_count, parent2_dna.crossover_count) + 1
        )
        
        logger.info(f"🧬 Скрещивание {parent1_dna.agent_id} × {parent2_dna.agent_id} → {child_id}")
        return child_dna
    
    def calculate_fitness(self, agent_dna: AgentDNA, task_history: List[Dict] = None) -> float:
        """⚡ Расчёт приспособленности агента (fitness function)"""
        
        fitness = 0.0
        
        # Базовая приспособленность от генов (40%)
        base_fitness = (
            agent_dna.genes.success_rate * 0.5 +
            (agent_dna.genes.speed_factor - 0.5) * 0.1 +  # Скорость важна, но не критична
            (agent_dna.genes.quality_factor - 0.5) * 0.2 +  # Качество очень важно
            agent_dna.genes.collaboration_skill * 0.2
        )
        fitness += base_fitness * 0.4
        
        # Реальная производительность (60%)
        if agent_dna.total_success_rate > 0:
            performance_fitness = agent_dna.total_success_rate
            fitness += performance_fitness * 0.6
        else:
            # Если нет истории, используем генетическую предрасположенность
            fitness += agent_dna.genes.success_rate * 0.6
        
        # Бонус за опыт (больше задач = больше опыта)
        experience_bonus = min(0.1, agent_dna.tasks_completed * 0.01)
        fitness += experience_bonus
        
        # Штраф за старость (поощряем обновление популяции)
        if agent_dna.life_span:
            age_penalty = min(0.05, agent_dna.life_span.days * 0.001)
            fitness -= age_penalty
        
        return max(0.0, min(1.0, fitness))
    
    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===
    
    def _copy_genes(self, genes: AgentGenes) -> AgentGenes:
        """Глубокое копирование генов"""
        return AgentGenes(
            agent_type=genes.agent_type,
            specialization=genes.specialization.copy(),
            success_rate=genes.success_rate,
            speed_factor=genes.speed_factor,
            quality_factor=genes.quality_factor,
            preferred_tools=genes.preferred_tools.copy(),
            tool_efficiency=genes.tool_efficiency.copy(),
            learning_rate=genes.learning_rate,
            mutation_resistance=genes.mutation_resistance,
            collaboration_skill=genes.collaboration_skill,
            leadership_tendency=genes.leadership_tendency
        )
    
    def _generate_initial_tools(self, agent_type: str) -> List[str]:
        """Генерация начальных инструментов для типа агента"""
        base_tools = ["general_tools"]
        
        if agent_type == "code":
            base_tools.extend(["code_generator", "file_manager"])
        elif agent_type == "web":
            base_tools.extend(["web_search", "web_scraping"])
        elif agent_type == "analysis":
            base_tools.extend(["data_analysis", "visualization"])
        elif agent_type == "document":
            base_tools.extend(["document_tool", "file_manager"])
        
        return base_tools
    
    def _generate_tool_efficiency(self, agent_type: str) -> Dict[str, float]:
        """Генерация эффективности инструментов"""
        efficiency = {"general_tools": self.random.uniform(0.7, 1.0)}
        
        if agent_type == "code":
            efficiency.update({
                "code_generator": self.random.uniform(0.8, 1.2),
                "file_manager": self.random.uniform(0.7, 1.1)
            })
        elif agent_type == "web":
            efficiency.update({
                "web_search": self.random.uniform(0.8, 1.2),
                "web_scraping": self.random.uniform(0.7, 1.1)
            })
        
        return efficiency
    
    def _mutate_tools(self, genes: AgentGenes):
        """Мутация инструментов агента"""
        available_tools = [
            "code_generator", "web_search", "data_analysis", 
            "file_manager", "document_tool", "smart_validator"
        ]
        
        # Возможность добавить новый инструмент
        if self.random.random() < 0.5 and len(genes.preferred_tools) < 5:
            new_tool = self.random.choice([t for t in available_tools if t not in genes.preferred_tools])
            genes.preferred_tools.append(new_tool)
            genes.tool_efficiency[new_tool] = self.random.uniform(0.6, 1.0)
        
        # Возможность улучшить эффективность существующего инструмента
        if genes.preferred_tools:
            tool = self.random.choice(genes.preferred_tools)
            if tool in genes.tool_efficiency:
                old_eff = genes.tool_efficiency[tool]
                genes.tool_efficiency[tool] = max(0.3, min(1.5, 
                    old_eff + self.random.uniform(-0.1, 0.2)))
    
    def _merge_tools(self, tools1: List[str], tools2: List[str]) -> List[str]:
        """Объединение инструментов двух родителей"""
        # Берём все уникальные инструменты, ограничиваем до 6
        merged = list(set(tools1 + tools2))
        if len(merged) > 6:
            # Оставляем случайные 6 инструментов
            merged = self.random.sample(merged, 6)
        return merged
    
    def _merge_tool_efficiency(self, eff1: Dict[str, float], eff2: Dict[str, float]) -> Dict[str, float]:
        """Объединение эффективности инструментов"""
        merged = {}
        all_tools = set(eff1.keys()) | set(eff2.keys())
        
        for tool in all_tools:
            val1 = eff1.get(tool, 0.5)
            val2 = eff2.get(tool, 0.5)
            # Берём лучшее значение
            merged[tool] = max(val1, val2)
        
        return merged

# === ЧАСТЬ 3: ЭВОЛЮЦИОННАЯ ФАБРИКА ===

class EvolutionaryAgentFactory:
    """🧬 Эволюционная фабрика агентов - управление популяцией и эволюцией"""
    
    def __init__(self, storage_path: str = "./evolutionary_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Генетические операции
        self.genetics = GeneticOperations()
        
        # Популяция агентов
        self.population: Dict[str, AgentDNA] = {}
        self.active_agents: Dict[str, AgentDNA] = {}
        self.retired_agents: Dict[str, AgentDNA] = {}
        
        # История эволюции
        self.evolution_history: List[EvolutionEvent] = []
        
        # Настройки популяции
        self.max_population = 20
        self.min_population = 5
        self.retirement_age_days = 30
        
        # Загружаем существующую популяцию
        self._load_population()
        
        logger.info(f"🧬 EvolutionaryAgentFactory инициализирована")
        logger.info(f"📊 Популяция: {len(self.active_agents)} активных, {len(self.retired_agents)} в отставке")
    
    def spawn_agent(self, agent_type: str = "general", specialization: List[str] = None) -> AgentDNA:
        """🌱 Создание нового агента (размножение или начальное создание)"""
        
        # Если популяция пустая, создаём начального агента
        if not self.active_agents:
            agent_dna = self.genetics.create_initial_agent(agent_type, specialization)
            self._add_to_population(agent_dna)
            self._record_evolution_event("birth", agent_dna.agent_id, fitness_after=0.5)
            return agent_dna
        
        # Ищем лучших родителей для размножения
        candidates = self._select_breeding_candidates(agent_type)
        
        if len(candidates) >= 2:
            # Скрещивание двух лучших агентов
            parent1, parent2 = candidates[:2]
            child_dna = self.genetics.crossover_agents(parent1, parent2)
            
            # Возможная мутация потомка
            if random.random() < 0.3:
                child_dna = self.genetics.mutate_agent(child_dna)
            
            self._add_to_population(child_dna)
            self._record_evolution_event("birth", child_dna.agent_id, 
                                       parent_ids=child_dna.parent_ids,
                                       fitness_after=self.genetics.calculate_fitness(child_dna))
            
            logger.info(f"🧬 Размножение: {parent1.agent_id} × {parent2.agent_id} → {child_dna.agent_id}")
            
        elif len(candidates) == 1:
            # Мутация единственного кандидата
            parent = candidates[0]
            child_dna = self.genetics.mutate_agent(parent, mutation_strength=1.5)
            
            self._add_to_population(child_dna)
            self._record_evolution_event("birth", child_dna.agent_id,
                                       parent_ids=[parent.agent_id],
                                       fitness_after=self.genetics.calculate_fitness(child_dna))
            
            logger.info(f"🔄 Мутационное размножение: {parent.agent_id} → {child_dna.agent_id}")
            
        else:
            # Создаём нового агента с нуля
            child_dna = self.genetics.create_initial_agent(agent_type, specialization)
            self._add_to_population(child_dna)
            self._record_evolution_event("birth", child_dna.agent_id, fitness_after=0.5)
            
            logger.info(f"🌱 Новый агент: {child_dna.agent_id}")
        
        # Проверяем нужно ли сократить популяцию
        self._manage_population_size()
        
        return child_dna
    
    def update_agent_performance(self, agent_id: str, task_success: bool, task_duration: float = 0.0):
        """📊 Обновление производительности агента после выполнения задачи"""
        
        if agent_id not in self.active_agents:
            logger.warning(f"⚠️ Агент {agent_id} не найден в активной популяции")
            return
        
        agent_dna = self.active_agents[agent_id]
        
        # Обновляем статистику
        agent_dna.tasks_completed += 1
        
        # Обновляем общий success rate
        old_rate = agent_dna.total_success_rate
        new_rate = (
            (old_rate * (agent_dna.tasks_completed - 1) + (1.0 if task_success else 0.0)) 
            / agent_dna.tasks_completed
        )
        agent_dna.total_success_rate = new_rate
        
        # Обновляем генетические характеристики (обучение)
        if task_success:
            # Успех усиливает уверенность
            learning_boost = agent_dna.genes.learning_rate * 0.1
            agent_dna.genes.success_rate = min(1.0, agent_dna.genes.success_rate + learning_boost)
        else:
            # Неудача снижает уверенность, но стимулирует адаптацию
            learning_penalty = agent_dna.genes.learning_rate * 0.05
            agent_dna.genes.success_rate = max(0.0, agent_dna.genes.success_rate - learning_penalty)
        
        # Записываем событие обучения
        fitness_change = new_rate - old_rate
        if abs(fitness_change) > 0.01:  # Значимое изменение
            self._record_evolution_event("learning", agent_id,
                                       fitness_before=old_rate,
                                       fitness_after=new_rate,
                                       success_improvement=fitness_change)
        
        logger.debug(f"📊 Агент {agent_id}: задач {agent_dna.tasks_completed}, успех {new_rate:.2f}")
        
        # Сохраняем изменения
        self._save_population()
    
    def evolve_population(self, force_evolution: bool = False):
        """🌱 Принудительная эволюция популяции"""
        
        if len(self.active_agents) < 2 and not force_evolution:
            logger.info("🧬 Недостаточно агентов для эволюции")
            return
        
        logger.info("🧬 Запуск эволюции популяции...")
        
        # Сортируем агентов по приспособленности
        sorted_agents = sorted(
            self.active_agents.values(),
            key=lambda a: self.genetics.calculate_fitness(a),
            reverse=True
        )
        
        evolution_count = 0
        
        # Мутируем худших агентов
        worst_agents = sorted_agents[-len(sorted_agents)//3:] if len(sorted_agents) >= 3 else sorted_agents[-1:]
        for agent in worst_agents:
            if random.random() < 0.4:  # 40% шанс мутации
                mutated = self.genetics.mutate_agent(agent, mutation_strength=1.2)
                self._replace_agent(agent.agent_id, mutated)
                evolution_count += 1
        
        # Скрещиваем лучших агентов
        best_agents = sorted_agents[:len(sorted_agents)//2] if len(sorted_agents) >= 4 else sorted_agents[:2]
        if len(best_agents) >= 2:
            for i in range(0, len(best_agents)-1, 2):
                if random.random() < 0.3:  # 30% шанс скрещивания
                    child = self.genetics.crossover_agents(best_agents[i], best_agents[i+1])
                    # Заменяем одного из худших агентов
                    if worst_agents:
                        self._replace_agent(worst_agents[0].agent_id, child)
                        worst_agents = worst_agents[1:]  # Убираем из списка
                        evolution_count += 1
        
        logger.info(f"🧬 Эволюция завершена: {evolution_count} изменений")
        self._save_population()
    
    def get_best_agent(self, agent_type: str = None) -> Optional[AgentDNA]:
        """🏆 Получить лучшего агента (опционально по типу)"""
        
        candidates = self.active_agents.values()
        if agent_type:
            candidates = [a for a in candidates if a.genes.agent_type == agent_type]
        
        if not candidates:
            return None
        
        best_agent = max(candidates, key=lambda a: self.genetics.calculate_fitness(a))
        return best_agent
    
    def get_population_stats(self) -> PopulationStats:
        """📊 Получить статистику популяции"""
        
        active_agents = list(self.active_agents.values())
        all_agents = list(self.population.values())
        
        if not all_agents:
            return PopulationStats()
        
        # Базовая статистика
        stats = PopulationStats(
            total_agents=len(all_agents),
            active_agents=len(active_agents),
            retired_agents=len(self.retired_agents)
        )
        
        # Поколения
        generations = [a.generation for a in all_agents]
        stats.max_generation = max(generations)
        stats.avg_generation = sum(generations) / len(generations)
        
        # Производительность
        success_rates = [a.total_success_rate for a in active_agents if a.total_success_rate > 0]
        if success_rates:
            stats.avg_success_rate = sum(success_rates) / len(success_rates)
            stats.best_success_rate = max(success_rates)
            stats.worst_success_rate = min(success_rates)
        
        # Разнообразие
        specializations = set()
        for agent in active_agents:
            specializations.update(agent.genes.specialization)
        stats.unique_specializations = len(specializations)
        
        # Генетическое разнообразие (упрощённый расчёт)
        if len(active_agents) > 1:
            diversity_sum = 0
            for i, agent1 in enumerate(active_agents):
                for agent2 in active_agents[i+1:]:
                    diversity_sum += self._calculate_genetic_distance(agent1, agent2)
            stats.genetic_diversity = diversity_sum / (len(active_agents) * (len(active_agents) - 1) / 2)
        
        # Эволюция
        stats.total_mutations = sum(a.mutations_count for a in all_agents)
        stats.total_crossovers = sum(a.crossover_count for a in all_agents)
        stats.evolution_events = len(self.evolution_history)
        
        # Здоровье популяции
        stats.population_health = self._calculate_population_health(active_agents)
        
        return stats
    
    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===
    
    def _select_breeding_candidates(self, agent_type: str) -> List[AgentDNA]:
        """🎯 Выбор кандидатов для размножения"""
        
        # Фильтруем по типу если указан
        candidates = list(self.active_agents.values())
        if agent_type != "general":
            candidates = [a for a in candidates if a.genes.agent_type == agent_type or agent_type in a.genes.specialization]
        
        # Сортируем по приспособленности
        candidates.sort(key=lambda a: self.genetics.calculate_fitness(a), reverse=True)
        
        # Возвращаем лучших (максимум 3)
        return candidates[:3]
    
    def _add_to_population(self, agent_dna: AgentDNA):
        """➕ Добавить агента в популяцию"""
        self.population[agent_dna.agent_id] = agent_dna
        self.active_agents[agent_dna.agent_id] = agent_dna
    
    def _replace_agent(self, old_agent_id: str, new_agent_dna: AgentDNA):
        """🔄 Заменить агента в популяции"""
        if old_agent_id in self.active_agents:
            # Переводим старого в отставку
            old_agent = self.active_agents.pop(old_agent_id)
            self.retired_agents[old_agent_id] = old_agent
            
            # Добавляем нового
            self._add_to_population(new_agent_dna)
            
            self._record_evolution_event("replacement", new_agent_dna.agent_id,
                                       selection_reason=f"replaced_{old_agent_id}")
    
    def _manage_population_size(self):
        """⚖️ Управление размером популяции"""
        
        if len(self.active_agents) > self.max_population:
            # Удаляем худших агентов
            excess = len(self.active_agents) - self.max_population
            sorted_agents = sorted(
                self.active_agents.values(),
                key=lambda a: self.genetics.calculate_fitness(a)
            )
            
            for agent in sorted_agents[:excess]:
                self._retire_agent(agent.agent_id, "population_limit")
        
        elif len(self.active_agents) < self.min_population:
            # Создаём новых агентов
            needed = self.min_population - len(self.active_agents)
            for _ in range(needed):
                new_agent = self.genetics.create_initial_agent()
                self._add_to_population(new_agent)
                self._record_evolution_event("birth", new_agent.agent_id, 
                                           selection_reason="population_minimum",
                                           fitness_after=0.5)
    
    def _retire_agent(self, agent_id: str, reason: str):
        """🏖️ Отправить агента в отставку"""
        if agent_id in self.active_agents:
            agent = self.active_agents.pop(agent_id)
            agent.life_span = datetime.now() - agent.birth_time
            self.retired_agents[agent_id] = agent
            
            self._record_evolution_event("retirement", agent_id, selection_reason=reason)
            logger.info(f"🏖️ Агент {agent_id} отправлен в отставку: {reason}")
    
    def _record_evolution_event(self, event_type: str, agent_id: str, **kwargs):
        """📝 Записать событие эволюции"""
        event = EvolutionEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            agent_id=agent_id,
            **kwargs
        )
        self.evolution_history.append(event)
        
        # Ограничиваем историю (последние 1000 событий)
        if len(self.evolution_history) > 1000:
            self.evolution_history = self.evolution_history[-1000:]
    
    def _calculate_genetic_distance(self, agent1: AgentDNA, agent2: AgentDNA) -> float:
        """🧬 Расчёт генетического расстояния между агентами"""
        distance = 0.0
        
        # Различия в основных характеристиках
        distance += abs(agent1.genes.success_rate - agent2.genes.success_rate)
        distance += abs(agent1.genes.speed_factor - agent2.genes.speed_factor) * 0.5
        distance += abs(agent1.genes.quality_factor - agent2.genes.quality_factor) * 0.5
        distance += abs(agent1.genes.learning_rate - agent2.genes.learning_rate) * 0.3
        
        # Различия в специализациях
        spec1 = set(agent1.genes.specialization)
        spec2 = set(agent2.genes.specialization)
        spec_distance = len(spec1.symmetric_difference(spec2)) / max(len(spec1 | spec2), 1)
        distance += spec_distance * 0.3
        
        return distance
    
    def _calculate_population_health(self, agents: List[AgentDNA]) -> float:
        """💪 Расчёт здоровья популяции"""
        if not agents:
            return 0.0
        
        # Средняя приспособленность
        avg_fitness = sum(self.genetics.calculate_fitness(a) for a in agents) / len(agents)
        
        # Генетическое разнообразие
        if len(agents) > 1:
            diversity = 0.0
            for i, agent1 in enumerate(agents):
                for agent2 in agents[i+1:]:
                    diversity += self._calculate_genetic_distance(agent1, agent2)
            diversity = diversity / (len(agents) * (len(agents) - 1) / 2)
        else:
            diversity = 0.5  # Средняя оценка для одного агента
        
        # Возрастное распределение
        ages = [(datetime.now() - a.birth_time).days for a in agents]
        avg_age = sum(ages) / len(ages)
        age_health = max(0.0, 1.0 - avg_age / 60)  # Штраф за старость
        
        # Общее здоровье
        health = (avg_fitness * 0.5 + diversity * 0.3 + age_health * 0.2)
        return max(0.0, min(1.0, health))
    
    def _save_population(self):
        """💾 Сохранить популяцию на диск"""
        try:
            population_file = self.storage_path / "population.json"
            history_file = self.storage_path / "evolution_history.json"
            
            # Сохраняем популяцию
            population_data = {
                "active_agents": {k: asdict(v) for k, v in self.active_agents.items()},
                "retired_agents": {k: asdict(v) for k, v in self.retired_agents.items()},
                "settings": {
                    "max_population": self.max_population,
                    "min_population": self.min_population,
                    "retirement_age_days": self.retirement_age_days
                }
            }
            
            with open(population_file, 'w', encoding='utf-8') as f:
                json.dump(population_data, f, indent=2, default=str)
            
            # Сохраняем историю эволюции
            history_data = [asdict(event) for event in self.evolution_history[-100:]]  # Последние 100 событий
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения популяции: {e}")
    
    def _load_population(self):
        """📂 Загрузить популяцию с диска"""
        try:
            population_file = self.storage_path / "population.json"
            history_file = self.storage_path / "evolution_history.json"
            
            if population_file.exists():
                with open(population_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Загружаем агентов
                for agent_id, agent_data in data.get("active_agents", {}).items():
                    agent_dna = self._dict_to_agent_dna(agent_data)
                    self.active_agents[agent_id] = agent_dna
                    self.population[agent_id] = agent_dna
                
                for agent_id, agent_data in data.get("retired_agents", {}).items():
                    agent_dna = self._dict_to_agent_dna(agent_data)
                    self.retired_agents[agent_id] = agent_dna
                    self.population[agent_id] = agent_dna
                
                # Загружаем настройки
                settings = data.get("settings", {})
                self.max_population = settings.get("max_population", self.max_population)
                self.min_population = settings.get("min_population", self.min_population)
                self.retirement_age_days = settings.get("retirement_age_days", self.retirement_age_days)
                
                logger.info(f"📂 Загружена популяция: {len(self.active_agents)} активных агентов")
            
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                
                self.evolution_history = [self._dict_to_evolution_event(event) for event in history_data]
                logger.info(f"📂 Загружена история эволюции: {len(self.evolution_history)} событий")
                
        except Exception as e:
            logger.warning(f"⚠️ Ошибка загрузки популяции: {e}")
    
    def _dict_to_agent_dna(self, data: dict) -> AgentDNA:
        """🔄 Преобразование словаря в AgentDNA"""
        genes_data = data.get("genes", {})
        genes = AgentGenes(**genes_data)
        
        # Преобразуем строки дат обратно в datetime
        birth_time_str = data.get("birth_time")
        birth_time = datetime.fromisoformat(birth_time_str) if birth_time_str else datetime.now()
        
        life_span_str = data.get("life_span")
        life_span = timedelta(seconds=float(life_span_str)) if life_span_str else None
        
        return AgentDNA(
            agent_id=data["agent_id"],
            generation=data.get("generation", 0),
            parent_ids=data.get("parent_ids", []),
            birth_time=birth_time,
            genes=genes,
            mutations_count=data.get("mutations_count", 0),
            crossover_count=data.get("crossover_count", 0),
            tasks_completed=data.get("tasks_completed", 0),
            total_success_rate=data.get("total_success_rate", 0.0),
            life_span=life_span
        )
    
    def _dict_to_evolution_event(self, data: dict) -> EvolutionEvent:
        """🔄 Преобразование словаря в EvolutionEvent"""
        timestamp_str = data.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
        
        return EvolutionEvent(
            event_type=data["event_type"],
            timestamp=timestamp,
            agent_id=data["agent_id"],
            parent_ids=data.get("parent_ids"),
            mutation_details=data.get("mutation_details"),
            selection_reason=data.get("selection_reason"),
            fitness_before=data.get("fitness_before", 0.0),
            fitness_after=data.get("fitness_after", 0.0),
            success_improvement=data.get("success_improvement", 0.0)
        )


# === ГЛОБАЛЬНЫЕ ФУНКЦИИ ===

_global_evolutionary_factory = None

def get_evolutionary_factory(storage_path: str = "./evolutionary_storage") -> EvolutionaryAgentFactory:
    """🧬 Получить глобальный экземпляр эволюционной фабрики"""
    global _global_evolutionary_factory
    if _global_evolutionary_factory is None:
        _global_evolutionary_factory = EvolutionaryAgentFactory(storage_path)
    return _global_evolutionary_factory

def spawn_evolved_agent(agent_type: str = "general", specialization: List[str] = None) -> AgentDNA:
    """🌱 Создать эволюционного агента"""
    factory = get_evolutionary_factory()
    return factory.spawn_agent(agent_type, specialization)

def update_agent_evolution(agent_id: str, task_success: bool, task_duration: float = 0.0):
    """📊 Обновить эволюционные данные агента"""
    factory = get_evolutionary_factory()
    factory.update_agent_performance(agent_id, task_success, task_duration)

def get_evolution_stats() -> PopulationStats:
    """📈 Получить статистику эволюции"""
    factory = get_evolutionary_factory()
    return factory.get_population_stats()


if __name__ == "__main__":
    # Простой тест системы
    print("🧬 Тест EvolutionaryAgentFactory")
    
    factory = EvolutionaryAgentFactory("./test_evolution")
    
    # Создаём несколько агентов
    agent1 = factory.spawn_agent("code", ["python", "web"])
    agent2 = factory.spawn_agent("analysis", ["data", "statistics"])
    agent3 = factory.spawn_agent("web", ["frontend", "design"])
    
    print(f"Создано агентов: {len(factory.active_agents)}")
    
    # Симулируем выполнение задач
    factory.update_agent_performance(agent1.agent_id, True)
    factory.update_agent_performance(agent1.agent_id, True)
    factory.update_agent_performance(agent2.agent_id, False)
    factory.update_agent_performance(agent3.agent_id, True)
    
    # Эволюция
    factory.evolve_population(force_evolution=True)
    
    # Статистика
    stats = factory.get_population_stats()
    print(f"Статистика: {stats.active_agents} активных, поколение {stats.max_generation}")
    print(f"Лучший успех: {stats.best_success_rate:.2f}")
    print(f"Здоровье популяции: {stats.population_health:.2f}")
    
    print("✅ Тест завершён!") 