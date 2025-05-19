import json
from loguru import logger
import os
from typing import Any, Dict, Optional, List, Callable

os.makedirs("logs", exist_ok=True)
logger.add("logs/events.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)
logger.add("logs/debug_state_machine.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip", serialize=True)

class ScenarioStateMachine:
    """
    State machine для сценариев с поддержкой условий, ветвлений и пользовательского контекста.
    - Каждый шаг может содержать:
        - type, text, ... (любые поля)
        - condition: выражение (str) для перехода (например, "context['x'] > 0")
        - branches: dict {"if": step_index, "else": step_index} для ветвлений
        - next_step: явный индекс следующего шага
    - context: dict, доступен во всех шагах, может изменяться
    """
    def __init__(self, scenario: Dict[str, Any], context: Dict[str, Any], executor: Any):
        self.scenario_name = scenario.get("name", "Unknown Scenario")
        self.steps: List[Dict[str, Any]] = scenario.get("steps", [])
        self.initial_context = context.copy() # Копируем, чтобы избежать изменения извне
        self.context = context.copy() # Рабочий контекст, который будет меняться
        self.executor = executor
        self.current_step_index = 0
        self.is_finished = False
        self.error: Optional[str] = None

        # === НАЧАЛО ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===
        logger.info(f"[STATE_MACHINE DEBUG] __init__ called. Scenario: {self.scenario_name}")
        logger.info(f"[STATE_MACHINE DEBUG] __init__ received context: {json.dumps(context, indent=2, default=str)}")
        logger.info(f"[STATE_MACHINE DEBUG] __init__ self.context after copy: {json.dumps(self.context, indent=2, default=str)}")
        # === КОНЕЦ ИЗМЕНЕНИЯ ДЛЯ ДЕБАГА ===

        logger.info(f"{{\'event\': \'init_state_machine\', \'scenario\': \'{self.scenario_name}\', \'state\': {{\'step_index\': self.current_step_index}}, \'context_via_json_dumps\': {json.dumps(self.context, default=str)}}}")

    def current_step(self):
        idx = self.current_step_index
        if 0 <= idx < len(self.steps):
            return self.steps[idx]
        return None

    def next_step(self, input_data: Optional[Dict[str, Any]] = None):
        idx = self.current_step_index
        step = self.current_step()
        # Обновляем context, если input_data есть
        if input_data:
            logger.debug(f"Обновляем контекст с input_data: {input_data}")
            self.context.update(input_data)
        
        # Проверяем условие (condition) и ветвления (branches)
        if step:
            logger.debug(f"Текущий шаг: {step.get('id', idx)}, тип: {step.get('type')}")
            
            # Обработка ветвлений нового формата (type: branch)
            if step.get("type") == "branch":
                logger.debug(f"Обрабатываем шаг типа 'branch'")
                branches_list = step.get("branches", [])
                
                if branches_list:
                    logger.debug(f"Список ветвлений: {branches_list}")
                    for branch in branches_list:
                        condition = branch.get("condition")
                        next_step_id = branch.get("next_step")
                        
                        logger.debug(f"Проверяем условие: {condition}")
                        if condition == "default":
                            logger.debug("Найдено условие 'default', используем его")
                            # Найти индекс шага по ID
                            for i, s in enumerate(self.steps):
                                if s.get("id") == next_step_id:
                                    self.current_step_index = i
                                    logger.debug(f"Переход к шагу {next_step_id} (индекс {i})")
                                    return self.steps[i]
                        else:
                            try:
                                # Подготавливаем контекст для eval
                                eval_context = {}
                                # Копируем все переменные из self.context в корневой уровень
                                for key, value in self.context.items():
                                    eval_context[key] = value
                                
                                # Логируем типы переменных для отладки
                                logger.debug(f"Типы переменных в контексте:")
                                for key, value in eval_context.items():
                                    logger.debug(f"  {key}: {type(value).__name__} = {value}")
                                
                                # Выполняем условие с подготовленным контекстом
                                logger.debug(f"Выполняем условие: {condition} с контекстом: {eval_context}")
                                result = eval(condition, {"__builtins__": {}}, eval_context)
                                logger.debug(f"Результат условия: {result}")
                                
                                if result:
                                    # Найти индекс шага по ID
                                    for i, s in enumerate(self.steps):
                                        if s.get("id") == next_step_id:
                                            self.current_step_index = i
                                            logger.debug(f"Условие истинно, переход к шагу {next_step_id} (индекс {i})")
                                            return self.steps[i]
                            except Exception as e:
                                logger.error({"event": "condition_eval_error", "error": str(e), "condition": condition, "step": step.get("id", idx)})
                                logger.debug(f"Ошибка при вычислении условия '{condition}': {e}")
                    
                    # Если ни одно условие не сработало, используем условие по умолчанию
                    for branch in branches_list:
                        if branch.get("condition") == "default":
                            next_step_id = branch.get("next_step")
                            for i, s in enumerate(self.steps):
                                if s.get("id") == next_step_id:
                                    self.current_step_index = i
                                    logger.debug(f"Используем условие по умолчанию, переход к шагу {next_step_id} (индекс {i})")
                                    return self.steps[i]
            
            # Обработка старого формата ветвлений
            cond = step.get("condition")
            branches = step.get("branches")
            next_step = step.get("next_step")
            
            if cond and branches:
                logger.debug(f"Обрабатываем условие в старом формате: {cond}")
                try:
                    # Безопасное преобразование типов для сравнения
                    def safe_eval(expr, context):
                        # Создаем безопасную среду для выполнения выражения
                        safe_globals = {"__builtins__": {}}
                        
                        # Функция для безопасного сравнения значений разных типов
                        def safe_compare(a, b, op):
                            # Пытаемся привести оба значения к одному типу
                            try:
                                # Если оба значения можно преобразовать в числа, делаем это
                                a_float = float(a) if isinstance(a, (int, float, str)) and str(a).strip() else 0
                                b_float = float(b) if isinstance(b, (int, float, str)) and str(b).strip() else 0
                                
                                if op == "==":
                                    return a_float == b_float
                                elif op == "!=":
                                    return a_float != b_float
                                elif op == "<":
                                    return a_float < b_float
                                elif op == "<=":
                                    return a_float <= b_float
                                elif op == ">":
                                    return a_float > b_float
                                elif op == ">=":
                                    return a_float >= b_float
                            except (ValueError, TypeError):
                                # Если не удалось преобразовать в числа, сравниваем как строки
                                a_str = str(a)
                                b_str = str(b)
                                
                                if op == "==":
                                    return a_str == b_str
                                elif op == "!=":
                                    return a_str != b_str
                                elif op == "<":
                                    return a_str < b_str
                                elif op == "<=":
                                    return a_str <= b_str
                                elif op == ">":
                                    return a_str > b_str
                                elif op == ">=":
                                    return a_str >= b_str
                        
                        # Модифицируем контекст для безопасного выполнения
                        safe_context = {}
                        for key, value in context.items():
                            safe_context[key] = value
                        
                        # Добавляем функцию безопасного сравнения в контекст
                        safe_context["safe_compare"] = safe_compare
                        
                        # Заменяем операторы сравнения на вызовы safe_compare
                        if "<=" in expr:
                            parts = expr.split("<=")
                            if len(parts) == 2:
                                left = parts[0].strip()
                                right = parts[1].strip()
                                if left.startswith("context[") and right.startswith("context["):
                                    left_key = left[8:-1].strip('"\'')
                                    right_key = right[8:-1].strip('"\'')
                                    return safe_compare(context.get(left_key), context.get(right_key), "<=")
                                elif left.startswith("context["):
                                    left_key = left[8:-1].strip('"\'')
                                    return safe_compare(context.get(left_key), eval(right, safe_globals, safe_context), "<=")
                                elif right.startswith("context["):
                                    right_key = right[8:-1].strip('"\'')
                                    return safe_compare(eval(left, safe_globals, safe_context), context.get(right_key), "<=")
                        
                        # Если не удалось обработать выражение специальным образом, 
                        # используем стандартный eval с безопасным контекстом
                        return eval(expr, safe_globals, safe_context)
                    
                    # Вычисляем условие с безопасным преобразованием типов
                    result = safe_eval(cond, self.context)
                    
                    # Определяем следующий шаг на основе результата условия
                    if result:
                        next_step_index = branches.get("true")
                        if next_step_index is not None:
                            self.current_step_index = next_step_index
                            logger.info({"event": "branch_true", "condition": cond, "next_step": next_step_index})
                            return self.steps[next_step_index] if 0 <= next_step_index < len(self.steps) else None
                    else:
                        next_step_index = branches.get("false")
                        if next_step_index is not None:
                            self.current_step_index = next_step_index
                            logger.info({"event": "branch_false", "condition": cond, "next_step": next_step_index})
                            return self.steps[next_step_index] if 0 <= next_step_index < len(self.steps) else None
                except Exception as e:
                    # Логируем ошибку при вычислении условия
                    logger.error({"event": "condition_eval_error", "error": str(e), "step_index": idx})
            
            # Обработка next_step (явный переход)
            if next_step is not None:
                logger.debug(f"Используем явный переход к шагу: {next_step}")
                # Проверяем, является ли next_step строкой (ID) или числом (индекс)
                if isinstance(next_step, str):
                    # Ищем шаг по ID
                    for i, s in enumerate(self.steps):
                        if s.get("id") == next_step:
                            self.current_step_index = i
                            logger.debug(f"Найден шаг с ID {next_step} (индекс {i})")
                            return self.steps[i]
                    logger.debug(f"Шаг с ID {next_step} не найден")
                elif 0 <= next_step < len(self.steps):
                    self.current_step_index = next_step
                    logger.info({"event": "next_step_explicit", "to": next_step, "context": self.context})
                    logger.debug(f"Переход к шагу по индексу {next_step}")
                    return self.steps[next_step]
        
        # По умолчанию — линейный переход
        if idx + 1 < len(self.steps):
            self.current_step_index = idx + 1
            logger.info({"event": "next_step_linear", "to": self.current_step_index, "context": self.context})
            logger.debug(f"Линейный переход к следующему шагу {idx + 1}")
            return self.steps[self.current_step_index]
        
        logger.info({"event": "end_of_scenario", "context": self.context})
        logger.debug("Достигнут конец сценария")
        return None

    def serialize(self):
        return json.dumps({"scenario": self.scenario_name, "state": {"step_index": self.current_step_index}, "context": self.context})

    @classmethod
    def from_json(cls, data):
        obj = json.loads(data)
        return cls(obj["scenario"], obj["state"]["context"], None)

    def trigger_command(self, command, data=None):
        """Обработка триггера on_command (заглушка)"""
        logger.info({"event": "trigger_command", "command": command, "data": data})
        return {"status": "triggered", "type": "command", "command": command}

    def trigger_event(self, event, data=None):
        """Обработка триггера on_event (заглушка)"""
        logger.info({"event": "trigger_event", "event_name": event, "data": data})
        return {"status": "triggered", "type": "event", "event": event}

    def trigger_schedule(self, schedule, data=None):
        """Обработка триггера on_schedule (заглушка)"""
        logger.info({"event": "trigger_schedule", "schedule": schedule, "data": data})
        return {"status": "triggered", "type": "schedule", "schedule": schedule} 