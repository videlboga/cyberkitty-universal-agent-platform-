#!/usr/bin/env python3
"""
🧠 PromptEvolution - Нейроэволюция промптов KittyCore 3.0

ФАЗА 3: Нейроэволюция промптов
Принцип: "Промпты эволюционируют как нейронные сети - лучшие паттерны выживают и размножаются"

Биологические принципы:
🧠 НЕЙРОННАЯ АДАПТАЦИЯ: Промпты адаптируются как синапсы в мозге
🔄 ЭВОЛЮЦИОННЫЕ МУТАЦИИ: Случайные изменения в тексте промптов
🎯 СЕЛЕКТИВНОЕ ДАВЛЕНИЕ: Успешные промпты доминируют
📊 ОБРАТНАЯ СВЯЗЬ: Результаты влияют на будущие промпты
🌱 НЕПРЕРЫВНАЯ ЭВОЛЮЦИЯ: Постоянное улучшение формулировок
"""

import json
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from loguru import logger

# === ЧАСТЬ 1: СТРУКТУРЫ ДАННЫХ ПРОМПТОВ ===

@dataclass
class PromptGenes:
    """🧠 Генетический код промпта - эволюционирующие элементы"""
    
    # Основная структура
    role_definition: str = ""  # Определение роли агента
    task_instructions: str = ""  # Инструкции по выполнению задач
    output_format: str = ""  # Формат вывода
    constraints: List[str] = None  # Ограничения и правила
    
    # Стилистические элементы
    tone: str = "professional"  # Тон общения (professional, friendly, technical)
    verbosity: str = "medium"  # Подробность (brief, medium, detailed)
    creativity: str = "balanced"  # Креативность (conservative, balanced, creative)
    
    # Технические аспекты
    examples: List[str] = None  # Примеры хорошего выполнения
    error_handling: str = ""  # Обработка ошибок
    quality_criteria: List[str] = None  # Критерии качества
    
    # Адаптивные элементы
    context_awareness: float = 0.5  # Учёт контекста (0.0-1.0)
    user_adaptation: float = 0.5  # Адаптация под пользователя (0.0-1.0)
    task_specialization: float = 0.5  # Специализация под задачи (0.0-1.0)
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []
        if self.examples is None:
            self.examples = []
        if self.quality_criteria is None:
            self.quality_criteria = []

@dataclass
class PromptDNA:
    """🧬 ДНК промпта - полная эволюционная информация"""
    
    prompt_id: str  # Уникальный ID промпта
    agent_type: str  # Тип агента для которого промпт
    generation: int = 0  # Поколение промпта
    parent_ids: List[str] = None  # ID родительских промптов
    birth_time: datetime = None
    
    # Генетический код
    genes: PromptGenes = None
    
    # Статистика производительности
    usage_count: int = 0  # Количество использований
    success_rate: float = 0.0  # Коэффициент успеха
    avg_quality_score: float = 0.0  # Средняя оценка качества
    avg_execution_time: float = 0.0  # Среднее время выполнения
    
    # История эволюции
    mutations_count: int = 0
    crossover_count: int = 0
    
    def __post_init__(self):
        if self.parent_ids is None:
            self.parent_ids = []
        if self.birth_time is None:
            self.birth_time = datetime.now()
        if self.genes is None:
            self.genes = PromptGenes()

@dataclass
class PromptPerformance:
    """📊 Результат выполнения с промптом"""
    
    prompt_id: str
    task_type: str
    success: bool
    quality_score: float
    execution_time: float
    timestamp: datetime
    
    # Детали выполнения
    user_feedback: Optional[str] = None
    error_details: Optional[str] = None
    output_length: int = 0
    context_relevance: float = 0.0

# === ЧАСТЬ 2: ЭВОЛЮЦИОННЫЕ ОПЕРАЦИИ ПРОМПТОВ ===

class PromptEvolutionEngine:
    """🧠 Движок эволюции промптов"""
    
    def __init__(self, storage_path: str = "./prompt_evolution_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Популяция промптов
        self.prompt_population: Dict[str, PromptDNA] = {}
        self.performance_history: List[PromptPerformance] = []
        
        # Настройки эволюции
        self.mutation_rate = 0.15
        self.crossover_rate = 0.25
        self.max_population = 50
        self.min_population = 10
        
        # Шаблоны для мутаций
        self.mutation_templates = self._load_mutation_templates()
        
        # Загружаем существующие промпты
        self._load_prompt_population()
        
        logger.info(f"🧠 PromptEvolutionEngine инициализирован")
        logger.info(f"📊 Популяция промптов: {len(self.prompt_population)}")
    
    def create_initial_prompt(self, agent_type: str, task_domain: str = "general") -> PromptDNA:
        """🌱 Создание начального промпта для типа агента"""
        
        prompt_id = f"prompt_{agent_type}_{int(datetime.now().timestamp())}_{random.randint(1000, 9999)}"
        
        # Базовые шаблоны для разных типов агентов
        base_templates = {
            "code": {
                "role_definition": "Ты опытный программист, специализирующийся на создании качественного кода.",
                "task_instructions": "Анализируй задачу, создавай чистый код с комментариями, тестируй решение.",
                "output_format": "Предоставь готовый к использованию код с пояснениями.",
                "constraints": ["Используй лучшие практики программирования", "Добавляй комментарии к сложным участкам"],
                "quality_criteria": ["Читаемость кода", "Производительность", "Надёжность"]
            },
            "web": {
                "role_definition": "Ты веб-разработчик с экспертизой в создании современных веб-приложений.",
                "task_instructions": "Создавай responsive дизайн, используй современные технологии, обеспечивай UX.",
                "output_format": "Предоставь HTML/CSS/JS код с объяснением архитектурных решений.",
                "constraints": ["Совместимость с браузерами", "Мобильная адаптивность"],
                "quality_criteria": ["Пользовательский опыт", "Производительность загрузки", "Доступность"]
            },
            "analysis": {
                "role_definition": "Ты аналитик данных, специализирующийся на извлечении инсайтов из информации.",
                "task_instructions": "Анализируй данные, выявляй паттерны, делай обоснованные выводы.",
                "output_format": "Предоставь структурированный анализ с визуализацией и рекомендациями.",
                "constraints": ["Объективность анализа", "Статистическая значимость"],
                "quality_criteria": ["Точность выводов", "Полнота анализа", "Практическая ценность"]
            },
            "general": {
                "role_definition": "Ты универсальный помощник, способный решать разнообразные задачи.",
                "task_instructions": "Анализируй задачу, выбирай оптимальный подход, выполняй качественно.",
                "output_format": "Предоставь результат в наиболее подходящем формате для задачи.",
                "constraints": ["Адаптация под тип задачи", "Ясность изложения"],
                "quality_criteria": ["Соответствие требованиям", "Полнота решения", "Понятность"]
            }
        }
        
        template = base_templates.get(agent_type, base_templates["general"])
        
        # Создаём гены промпта
        genes = PromptGenes(
            role_definition=template["role_definition"],
            task_instructions=template["task_instructions"],
            output_format=template["output_format"],
            constraints=template["constraints"].copy(),
            examples=[],
            error_handling="При возникновении ошибок, анализируй причину и предлагай альтернативные решения.",
            quality_criteria=template["quality_criteria"].copy(),
            tone="professional",
            verbosity="medium",
            creativity="balanced",
            context_awareness=random.uniform(0.4, 0.6),
            user_adaptation=random.uniform(0.4, 0.6),
            task_specialization=random.uniform(0.4, 0.6)
        )
        
        # Создаём ДНК промпта
        prompt_dna = PromptDNA(
            prompt_id=prompt_id,
            agent_type=agent_type,
            generation=0,
            genes=genes
        )
        
        # Добавляем в популяцию
        self.prompt_population[prompt_id] = prompt_dna
        self._save_prompt_population()
        
        logger.info(f"🌱 Создан начальный промпт {prompt_id} для агента {agent_type}")
        return prompt_dna
    
    def mutate_prompt(self, prompt_dna: PromptDNA, mutation_strength: float = 1.0) -> PromptDNA:
        """🔄 Мутация промпта для адаптации"""
        
        # Создаём копию промпта
        mutated_genes = PromptGenes(
            role_definition=prompt_dna.genes.role_definition,
            task_instructions=prompt_dna.genes.task_instructions,
            output_format=prompt_dna.genes.output_format,
            constraints=prompt_dna.genes.constraints.copy(),
            examples=prompt_dna.genes.examples.copy(),
            error_handling=prompt_dna.genes.error_handling,
            quality_criteria=prompt_dna.genes.quality_criteria.copy(),
            tone=prompt_dna.genes.tone,
            verbosity=prompt_dna.genes.verbosity,
            creativity=prompt_dna.genes.creativity,
            context_awareness=prompt_dna.genes.context_awareness,
            user_adaptation=prompt_dna.genes.user_adaptation,
            task_specialization=prompt_dna.genes.task_specialization
        )
        
        mutations_applied = []
        
        # Мутация текстовых элементов
        if random.random() < self.mutation_rate * mutation_strength:
            # Мутация определения роли
            mutated_genes.role_definition = self._mutate_text(
                mutated_genes.role_definition, "role", prompt_dna.agent_type
            )
            mutations_applied.append("role_definition")
        
        if random.random() < self.mutation_rate * mutation_strength:
            # Мутация инструкций
            mutated_genes.task_instructions = self._mutate_text(
                mutated_genes.task_instructions, "instructions", prompt_dna.agent_type
            )
            mutations_applied.append("task_instructions")
        
        if random.random() < self.mutation_rate * mutation_strength:
            # Мутация формата вывода
            mutated_genes.output_format = self._mutate_text(
                mutated_genes.output_format, "output", prompt_dna.agent_type
            )
            mutations_applied.append("output_format")
        
        # Мутация стилистических элементов
        if random.random() < self.mutation_rate * mutation_strength:
            tones = ["professional", "friendly", "technical", "creative", "formal"]
            mutated_genes.tone = random.choice([t for t in tones if t != mutated_genes.tone])
            mutations_applied.append("tone")
        
        if random.random() < self.mutation_rate * mutation_strength:
            verbosities = ["brief", "medium", "detailed", "comprehensive"]
            mutated_genes.verbosity = random.choice([v for v in verbosities if v != mutated_genes.verbosity])
            mutations_applied.append("verbosity")
        
        if random.random() < self.mutation_rate * mutation_strength:
            creativities = ["conservative", "balanced", "creative", "innovative"]
            mutated_genes.creativity = random.choice([c for c in creativities if c != mutated_genes.creativity])
            mutations_applied.append("creativity")
        
        # Мутация численных параметров
        if random.random() < self.mutation_rate * mutation_strength:
            delta = random.uniform(-0.2, 0.2) * mutation_strength
            mutated_genes.context_awareness = max(0.0, min(1.0, mutated_genes.context_awareness + delta))
            mutations_applied.append("context_awareness")
        
        if random.random() < self.mutation_rate * mutation_strength:
            delta = random.uniform(-0.2, 0.2) * mutation_strength
            mutated_genes.user_adaptation = max(0.0, min(1.0, mutated_genes.user_adaptation + delta))
            mutations_applied.append("user_adaptation")
        
        if random.random() < self.mutation_rate * mutation_strength:
            delta = random.uniform(-0.2, 0.2) * mutation_strength
            mutated_genes.task_specialization = max(0.0, min(1.0, mutated_genes.task_specialization + delta))
            mutations_applied.append("task_specialization")
        
        # Мутация ограничений и критериев
        if random.random() < self.mutation_rate * mutation_strength * 0.5:
            # Добавляем новое ограничение
            new_constraint = self._generate_constraint(prompt_dna.agent_type)
            if new_constraint and new_constraint not in mutated_genes.constraints:
                mutated_genes.constraints.append(new_constraint)
                mutations_applied.append("add_constraint")
        
        if random.random() < self.mutation_rate * mutation_strength * 0.3 and len(mutated_genes.constraints) > 1:
            # Удаляем случайное ограничение
            mutated_genes.constraints.pop(random.randint(0, len(mutated_genes.constraints) - 1))
            mutations_applied.append("remove_constraint")
        
        # Создаём новый промпт
        mutated_id = f"mut_{prompt_dna.prompt_id}_{int(datetime.now().timestamp())}"
        mutated_prompt = PromptDNA(
            prompt_id=mutated_id,
            agent_type=prompt_dna.agent_type,
            generation=prompt_dna.generation + 1,
            parent_ids=[prompt_dna.prompt_id],
            genes=mutated_genes,
            mutations_count=prompt_dna.mutations_count + 1
        )
        
        # Добавляем в популяцию
        self.prompt_population[mutated_id] = mutated_prompt
        
        logger.info(f"🔄 Мутация {prompt_dna.prompt_id} → {mutated_id}: {', '.join(mutations_applied)}")
        return mutated_prompt
    
    def crossover_prompts(self, parent1: PromptDNA, parent2: PromptDNA) -> PromptDNA:
        """🧬 Скрещивание двух промптов"""
        
        # Создаём гибридные гены
        hybrid_genes = PromptGenes()
        
        # Выбираем лучшие элементы от каждого родителя
        if parent1.success_rate > parent2.success_rate:
            stronger_parent, weaker_parent = parent1, parent2
        else:
            stronger_parent, weaker_parent = parent2, parent1
        
        # Основные элементы - от более успешного родителя
        hybrid_genes.role_definition = stronger_parent.genes.role_definition
        hybrid_genes.task_instructions = stronger_parent.genes.task_instructions
        
        # Формат вывода - комбинируем
        if random.random() < 0.5:
            hybrid_genes.output_format = stronger_parent.genes.output_format
        else:
            hybrid_genes.output_format = weaker_parent.genes.output_format
        
        # Ограничения - объединяем уникальные
        all_constraints = stronger_parent.genes.constraints + weaker_parent.genes.constraints
        hybrid_genes.constraints = list(set(all_constraints))  # Убираем дубликаты
        
        # Примеры - объединяем лучшие
        all_examples = stronger_parent.genes.examples + weaker_parent.genes.examples
        hybrid_genes.examples = list(set(all_examples))[:5]  # Максимум 5 примеров
        
        # Критерии качества - объединяем
        all_criteria = stronger_parent.genes.quality_criteria + weaker_parent.genes.quality_criteria
        hybrid_genes.quality_criteria = list(set(all_criteria))
        
        # Обработка ошибок - от лучшего
        hybrid_genes.error_handling = stronger_parent.genes.error_handling
        
        # Стилистические элементы - случайный выбор
        hybrid_genes.tone = random.choice([parent1.genes.tone, parent2.genes.tone])
        hybrid_genes.verbosity = random.choice([parent1.genes.verbosity, parent2.genes.verbosity])
        hybrid_genes.creativity = random.choice([parent1.genes.creativity, parent2.genes.creativity])
        
        # Численные параметры - среднее значение с вариацией
        hybrid_genes.context_awareness = (parent1.genes.context_awareness + parent2.genes.context_awareness) / 2
        hybrid_genes.user_adaptation = (parent1.genes.user_adaptation + parent2.genes.user_adaptation) / 2
        hybrid_genes.task_specialization = (parent1.genes.task_specialization + parent2.genes.task_specialization) / 2
        
        # Добавляем небольшую случайную вариацию
        hybrid_genes.context_awareness += random.uniform(-0.1, 0.1)
        hybrid_genes.user_adaptation += random.uniform(-0.1, 0.1)
        hybrid_genes.task_specialization += random.uniform(-0.1, 0.1)
        
        # Ограничиваем значения
        hybrid_genes.context_awareness = max(0.0, min(1.0, hybrid_genes.context_awareness))
        hybrid_genes.user_adaptation = max(0.0, min(1.0, hybrid_genes.user_adaptation))
        hybrid_genes.task_specialization = max(0.0, min(1.0, hybrid_genes.task_specialization))
        
        # Создаём гибридный промпт
        hybrid_id = f"cross_{parent1.agent_type}_{int(datetime.now().timestamp())}_{random.randint(100, 999)}"
        hybrid_prompt = PromptDNA(
            prompt_id=hybrid_id,
            agent_type=parent1.agent_type,  # Тип от первого родителя
            generation=max(parent1.generation, parent2.generation) + 1,
            parent_ids=[parent1.prompt_id, parent2.prompt_id],
            genes=hybrid_genes,
            crossover_count=max(parent1.crossover_count, parent2.crossover_count) + 1
        )
        
        # Добавляем в популяцию
        self.prompt_population[hybrid_id] = hybrid_prompt
        
        logger.info(f"🧬 Скрещивание {parent1.prompt_id} × {parent2.prompt_id} → {hybrid_id}")
        return hybrid_prompt
    
    def _mutate_text(self, original_text: str, text_type: str, agent_type: str) -> str:
        """✏️ Мутация текстового элемента промпта"""
        
        # Простые мутации - добавление модификаторов
        modifiers = {
            "role": [
                "опытный", "экспертный", "профессиональный", "высококвалифицированный",
                "креативный", "инновационный", "детальный", "эффективный"
            ],
            "instructions": [
                "тщательно", "детально", "системно", "последовательно",
                "креативно", "эффективно", "качественно", "профессионально"
            ],
            "output": [
                "структурированный", "подробный", "качественный", "понятный",
                "практичный", "готовый к использованию", "оптимизированный"
            ]
        }
        
        mutation_type = random.choice(["add_modifier", "replace_word", "add_clause"])
        
        if mutation_type == "add_modifier" and text_type in modifiers:
            # Добавляем модификатор
            modifier = random.choice(modifiers[text_type])
            if modifier not in original_text.lower():
                # Вставляем модификатор в подходящее место
                words = original_text.split()
                if len(words) > 2:
                    insert_pos = random.randint(1, min(3, len(words) - 1))
                    words.insert(insert_pos, modifier)
                    return " ".join(words)
        
        elif mutation_type == "replace_word":
            # Заменяем ключевые слова синонимами
            synonyms = {
                "создавай": ["разрабатывай", "формируй", "генерируй", "производи"],
                "анализируй": ["исследуй", "изучай", "рассматривай", "оценивай"],
                "качественный": ["высококачественный", "отличный", "превосходный", "профессиональный"],
                "эффективный": ["результативный", "продуктивный", "оптимальный", "успешный"]
            }
            
            for word, replacements in synonyms.items():
                if word in original_text.lower():
                    replacement = random.choice(replacements)
                    return original_text.replace(word, replacement)
        
        elif mutation_type == "add_clause":
            # Добавляем полезную фразу
            additional_clauses = {
                "role": [
                    ", учитывающий современные тенденции",
                    ", ориентированный на качество",
                    ", с глубоким пониманием предметной области"
                ],
                "instructions": [
                    " Обеспечь высокое качество результата.",
                    " Учитывай лучшие практики.",
                    " Проверяй корректность решения."
                ],
                "output": [
                    " с детальными пояснениями",
                    " готовый к практическому применению",
                    " с примерами использования"
                ]
            }
            
            if text_type in additional_clauses:
                clause = random.choice(additional_clauses[text_type])
                return original_text + clause
        
        return original_text  # Если мутация не применилась
    
    def _generate_constraint(self, agent_type: str) -> Optional[str]:
        """🎯 Генерация нового ограничения для агента"""
        
        constraints_pool = {
            "code": [
                "Следуй принципам SOLID",
                "Используй type hints в Python",
                "Добавляй docstrings к функциям",
                "Обрабатывай исключения корректно",
                "Оптимизируй производительность"
            ],
            "web": [
                "Обеспечь accessibility (a11y)",
                "Используй семантичную разметку",
                "Оптимизируй для SEO",
                "Поддерживай Progressive Web App",
                "Минимизируй размер ресурсов"
            ],
            "analysis": [
                "Проверяй статистическую значимость",
                "Документируй источники данных",
                "Валидируй входные данные",
                "Предоставляй доверительные интервалы",
                "Учитывай возможные искажения"
            ],
            "general": [
                "Проверяй актуальность информации",
                "Структурируй ответ логично",
                "Приводи конкретные примеры",
                "Учитывай контекст задачи",
                "Предлагай альтернативные решения"
            ]
        }
        
        pool = constraints_pool.get(agent_type, constraints_pool["general"])
        return random.choice(pool) if pool else None
    
    # === ЧАСТЬ 4A: ОСНОВНЫЕ МЕТОДЫ УПРАВЛЕНИЯ ===
    
    def record_prompt_performance(self, prompt_id: str, task_type: str, success: bool, 
                                quality_score: float, execution_time: float, **kwargs):
        """📊 Записать результат использования промпта"""
        
        if prompt_id not in self.prompt_population:
            logger.warning(f"⚠️ Промпт {prompt_id} не найден в популяции")
            return
        
        # Записываем результат
        performance = PromptPerformance(
            prompt_id=prompt_id,
            task_type=task_type,
            success=success,
            quality_score=quality_score,
            execution_time=execution_time,
            timestamp=datetime.now(),
            **kwargs
        )
        
        self.performance_history.append(performance)
        
        # Обновляем статистику промпта
        prompt = self.prompt_population[prompt_id]
        prompt.usage_count += 1
        
        # Обновляем success rate
        old_success = prompt.success_rate
        new_success = (old_success * (prompt.usage_count - 1) + (1.0 if success else 0.0)) / prompt.usage_count
        prompt.success_rate = new_success
        
        # Обновляем среднюю оценку качества
        old_quality = prompt.avg_quality_score
        new_quality = (old_quality * (prompt.usage_count - 1) + quality_score) / prompt.usage_count
        prompt.avg_quality_score = new_quality
        
        # Обновляем среднее время выполнения
        old_time = prompt.avg_execution_time
        new_time = (old_time * (prompt.usage_count - 1) + execution_time) / prompt.usage_count
        prompt.avg_execution_time = new_time
        
        logger.debug(f"📊 Промпт {prompt_id}: использований {prompt.usage_count}, успех {new_success:.2f}")
        
        # Сохраняем изменения
        self._save_prompt_population()
    
    def get_best_prompt(self, agent_type: str, task_type: str = None) -> Optional[PromptDNA]:
        """🏆 Получить лучший промпт для агента"""
        
        # Фильтруем по типу агента
        candidates = [p for p in self.prompt_population.values() if p.agent_type == agent_type]
        
        if not candidates:
            # Создаём новый промпт если нет подходящих
            return self.create_initial_prompt(agent_type)
        
        # Сортируем по качеству (комбинируем success rate и quality score)
        def prompt_fitness(prompt: PromptDNA) -> float:
            if prompt.usage_count == 0:
                return 0.5  # Нейтральная оценка для неиспользованных
            
            # Комбинируем метрики
            fitness = (
                prompt.success_rate * 0.4 +
                prompt.avg_quality_score * 0.4 +
                (1.0 - min(prompt.avg_execution_time / 60.0, 1.0)) * 0.2  # Штраф за долгое выполнение
            )
            
            # Бонус за больше использований (но не слишком большой)
            usage_bonus = min(prompt.usage_count / 10.0, 0.1)
            fitness += usage_bonus
            
            return fitness
        
        best_prompt = max(candidates, key=prompt_fitness)
        return best_prompt
    
    def evolve_prompts(self, agent_type: str = None):
        """🌱 Эволюция популяции промптов"""
        
        # Фильтруем по типу агента если указан
        if agent_type:
            population = {k: v for k, v in self.prompt_population.items() if v.agent_type == agent_type}
        else:
            population = self.prompt_population
        
        if len(population) < 2:
            logger.info("🧠 Недостаточно промптов для эволюции")
            return
        
        logger.info(f"🧠 Запуск эволюции промптов (популяция: {len(population)})")
        
        # Сортируем по приспособленности
        sorted_prompts = sorted(population.values(), key=self._calculate_prompt_fitness, reverse=True)
        
        evolution_count = 0
        
        # Мутируем худшие промпты (нижние 30%)
        worst_count = max(1, len(sorted_prompts) // 3)
        worst_prompts = sorted_prompts[-worst_count:]
        
        for prompt in worst_prompts:
            if random.random() < 0.4:  # 40% шанс мутации
                mutated = self.mutate_prompt(prompt, mutation_strength=1.2)
                evolution_count += 1
        
        # Скрещиваем лучшие промпты (верхние 50%)
        best_count = max(2, len(sorted_prompts) // 2)
        best_prompts = sorted_prompts[:best_count]
        
        if len(best_prompts) >= 2:
            for i in range(0, len(best_prompts) - 1, 2):
                if random.random() < 0.3:  # 30% шанс скрещивания
                    child = self.crossover_prompts(best_prompts[i], best_prompts[i + 1])
                    evolution_count += 1
        
        # Управляем размером популяции
        self._manage_prompt_population_size()
        
        logger.info(f"🧠 Эволюция промптов завершена: {evolution_count} изменений")
        self._save_prompt_population()
    
    def _calculate_prompt_fitness(self, prompt: PromptDNA) -> float:
        """💪 Расчёт приспособленности промпта"""
        
        if prompt.usage_count == 0:
            return 0.5  # Средняя оценка для неиспользованных
        
        # Базовая приспособленность
        fitness = (
            prompt.success_rate * 0.5 +           # Успешность
            prompt.avg_quality_score * 0.3 +      # Качество
            min(prompt.usage_count / 20.0, 0.2)   # Опыт использования (макс 0.2)
        )
        
        # Штраф за медленное выполнение
        time_penalty = min(prompt.avg_execution_time / 120.0, 0.1)  # Макс штраф 0.1
        fitness -= time_penalty
        
        # Бонус за новизну (молодые промпты получают небольшой бонус)
        age_days = (datetime.now() - prompt.birth_time).days
        if age_days < 7:  # Неделя
            fitness += 0.05
        
        return max(0.0, min(1.0, fitness))
    
    def _manage_prompt_population_size(self):
        """📊 Управление размером популяции"""
        
        if len(self.prompt_population) <= self.max_population:
            return
        
        # Сортируем промпты по эффективности
        prompts_by_fitness = sorted(
            self.prompt_population.values(),
            key=self._calculate_prompt_fitness,
            reverse=True
        )
        
        # Оставляем только лучших
        survivors = prompts_by_fitness[:self.max_population]
        
        # Обновляем популяцию
        self.prompt_population = {prompt.prompt_id: prompt for prompt in survivors}
        
        logger.info(f"📊 Популяция промптов сокращена до {len(self.prompt_population)}")
    
    def get_population_stats(self) -> Dict[str, Any]:
        """📊 Получить статистику популяции промптов"""
        
        if not self.prompt_population:
            return {
                'population_size': 0,
                'avg_success': 0.0,
                'max_generation': 0,
                'total_mutations': 0,
                'total_crossovers': 0,
                'agent_types': []
            }
        
        prompts = list(self.prompt_population.values())
        
        # Базовая статистика
        population_size = len(prompts)
        avg_success = sum(p.success_rate for p in prompts) / population_size if prompts else 0.0
        max_generation = max(p.generation for p in prompts) if prompts else 0
        total_mutations = sum(p.mutations_count for p in prompts)
        total_crossovers = sum(p.crossover_count for p in prompts)
        
        # Типы агентов
        agent_types = list(set(p.agent_type for p in prompts))
        
        return {
            'population_size': population_size,
            'avg_success': avg_success,
            'max_generation': max_generation,
            'total_mutations': total_mutations,
            'total_crossovers': total_crossovers,
            'agent_types': agent_types
        }
    
    def _load_mutation_templates(self) -> Dict[str, List[str]]:
        """📚 Загрузка шаблонов для мутаций"""
        return {
            "role_enhancers": ["экспертный", "профессиональный", "опытный", "квалифицированный"],
            "instruction_modifiers": ["тщательно", "системно", "качественно", "эффективно"],
            "output_enhancers": ["структурированный", "детальный", "практичный", "готовый к использованию"]
        }
    
    def _save_prompt_population(self):
        """💾 Сохранение популяции промптов"""
        try:
            population_file = self.storage_path / "prompt_population.json"
            history_file = self.storage_path / "performance_history.json"
            
            # Сохраняем популяцию
            population_data = {k: asdict(v) for k, v in self.prompt_population.items()}
            with open(population_file, 'w', encoding='utf-8') as f:
                json.dump(population_data, f, indent=2, default=str)
            
            # Сохраняем историю (последние 500 записей)
            recent_history = self.performance_history[-500:]
            history_data = [asdict(h) for h in recent_history]
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения популяции промптов: {e}")
    
    def _load_prompt_population(self):
        """📂 Загрузка популяции промптов"""
        try:
            population_file = self.storage_path / "prompt_population.json"
            if population_file.exists():
                with open(population_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for prompt_id, prompt_data in data.items():
                    prompt_dna = self._dict_to_prompt_dna(prompt_data)
                    self.prompt_population[prompt_id] = prompt_dna
                
                logger.info(f"📂 Загружено {len(self.prompt_population)} промптов")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка загрузки популяции промптов: {e}")
    
    def _dict_to_prompt_dna(self, data: dict) -> PromptDNA:
        """🔄 Преобразование словаря в PromptDNA"""
        genes_data = data.get("genes", {})
        genes = PromptGenes(**genes_data)
        
        birth_time_str = data.get("birth_time")
        birth_time = datetime.fromisoformat(birth_time_str) if birth_time_str else datetime.now()
        
        return PromptDNA(
            prompt_id=data["prompt_id"],
            agent_type=data["agent_type"],
            generation=data.get("generation", 0),
            parent_ids=data.get("parent_ids", []),
            birth_time=birth_time,
            genes=genes,
            usage_count=data.get("usage_count", 0),
            success_rate=data.get("success_rate", 0.0),
            avg_quality_score=data.get("avg_quality_score", 0.0),
            avg_execution_time=data.get("avg_execution_time", 0.0),
            mutations_count=data.get("mutations_count", 0),
            crossover_count=data.get("crossover_count", 0)
        )


# === ГЛОБАЛЬНЫЕ ФУНКЦИИ ===

_global_prompt_engine = None

def get_prompt_evolution_engine(storage_path: str = "./prompt_evolution_storage") -> PromptEvolutionEngine:
    """🧠 Получить глобальный экземпляр движка эволюции промптов"""
    global _global_prompt_engine
    if _global_prompt_engine is None:
        _global_prompt_engine = PromptEvolutionEngine(storage_path)
    return _global_prompt_engine

def get_evolved_prompt(agent_type: str, task_type: str = None) -> PromptDNA:
    """🎯 Получить эволюционный промпт для агента"""
    engine = get_prompt_evolution_engine()
    return engine.get_best_prompt(agent_type, task_type)

def record_prompt_usage(prompt_id: str, task_type: str, success: bool, quality_score: float, execution_time: float):
    """📊 Записать использование промпта"""
    engine = get_prompt_evolution_engine()
    engine.record_prompt_performance(prompt_id, task_type, success, quality_score, execution_time)

def evolve_all_prompts():
    """🌱 Запустить эволюцию всех промптов"""
    engine = get_prompt_evolution_engine()
    engine.evolve_prompts()

def generate_prompt_text(prompt_dna: PromptDNA) -> str:
    """📝 Генерация финального текста промпта из ДНК"""
    
    genes = prompt_dna.genes
    
    # Формируем основную структуру промпта
    prompt_parts = []
    
    # Определение роли
    if genes.role_definition:
        prompt_parts.append(f"**Роль:** {genes.role_definition}")
    
    # Инструкции по выполнению
    if genes.task_instructions:
        tone_modifier = {
            "professional": "профессионально",
            "friendly": "дружелюбно", 
            "technical": "технически точно",
            "creative": "креативно",
            "formal": "формально"
        }.get(genes.tone, "")
        
        verbosity_modifier = {
            "brief": "Будь краток.",
            "medium": "Предоставь достаточно деталей.",
            "detailed": "Будь подробным.",
            "comprehensive": "Предоставь исчерпывающую информацию."
        }.get(genes.verbosity, "")
        
        instruction_text = genes.task_instructions
        if tone_modifier:
            instruction_text += f" Работай {tone_modifier}."
        if verbosity_modifier:
            instruction_text += f" {verbosity_modifier}"
            
        prompt_parts.append(f"**Задача:** {instruction_text}")
    
    # Формат вывода
    if genes.output_format:
        prompt_parts.append(f"**Формат ответа:** {genes.output_format}")
    
    # Ограничения
    if genes.constraints:
        constraints_text = "\n".join([f"- {constraint}" for constraint in genes.constraints])
        prompt_parts.append(f"**Ограничения:**\n{constraints_text}")
    
    # Критерии качества
    if genes.quality_criteria:
        criteria_text = "\n".join([f"- {criterion}" for criterion in genes.quality_criteria])
        prompt_parts.append(f"**Критерии качества:**\n{criteria_text}")
    
    # Примеры (если есть)
    if genes.examples:
        examples_text = "\n".join([f"- {example}" for example in genes.examples[:3]])  # Максимум 3 примера
        prompt_parts.append(f"**Примеры:**\n{examples_text}")
    
    # Обработка ошибок
    if genes.error_handling:
        prompt_parts.append(f"**При ошибках:** {genes.error_handling}")
    
    # Адаптивные элементы
    adaptive_instructions = []
    
    if genes.context_awareness > 0.7:
        adaptive_instructions.append("Внимательно учитывай контекст задачи.")
    
    if genes.user_adaptation > 0.7:
        adaptive_instructions.append("Адаптируй стиль под потребности пользователя.")
    
    if genes.task_specialization > 0.7:
        adaptive_instructions.append("Специализируйся под конкретный тип задачи.")
    
    if adaptive_instructions:
        prompt_parts.append(f"**Дополнительно:** {' '.join(adaptive_instructions)}")
    
    # Собираем финальный промпт
    final_prompt = "\n\n".join(prompt_parts)
    
    return final_prompt


if __name__ == "__main__":
    # Простой тест системы эволюции промптов
    print("🧠 Тест PromptEvolutionEngine")
    
    engine = PromptEvolutionEngine("./test_prompt_evolution")
    
    # Создаём промпты для разных типов агентов
    code_prompt = engine.create_initial_prompt("code")
    web_prompt = engine.create_initial_prompt("web")
    analysis_prompt = engine.create_initial_prompt("analysis")
    
    print(f"Создано промптов: {len(engine.prompt_population)}")
    
    # Симулируем использование промптов
    engine.record_prompt_performance(code_prompt.prompt_id, "programming", True, 0.8, 15.0)
    engine.record_prompt_performance(code_prompt.prompt_id, "programming", True, 0.9, 12.0)
    engine.record_prompt_performance(web_prompt.prompt_id, "web_development", False, 0.4, 25.0)
    engine.record_prompt_performance(analysis_prompt.prompt_id, "data_analysis", True, 0.7, 20.0)
    
    print(f"Code промпт: использований {code_prompt.usage_count}, успех {code_prompt.success_rate:.2f}")
    
    # Эволюция
    engine.evolve_prompts()
    
    # Получаем лучший промпт
    best_code_prompt = engine.get_best_prompt("code")
    print(f"Лучший code промпт: {best_code_prompt.prompt_id}, поколение {best_code_prompt.generation}")
    
    # Генерируем текст промпта
    prompt_text = generate_prompt_text(best_code_prompt)
    print(f"Длина промпта: {len(prompt_text)} символов")
    
    print("✅ Тест завершён!") 