import json
from loguru import logger
import os
from typing import Any, Dict, Optional

os.makedirs("logs", exist_ok=True)
logger.add("logs/events.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip", serialize=True)

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
    def __init__(self, scenario: Dict[str, Any], state: Optional[Dict[str, Any]] = None, context: Optional[Dict[str, Any]] = None):
        self.scenario = scenario
        self.steps = scenario.get("steps", [])
        self.state = state or {"step_index": 0}
        self.context = context or {}
        logger.info({"event": "init_state_machine", "scenario": scenario.get("name"), "state": self.state, "context": self.context})

    def current_step(self):
        idx = self.state.get("step_index", 0)
        if 0 <= idx < len(self.steps):
            return self.steps[idx]
        return None

    def next_step(self, input_data: Optional[Dict[str, Any]] = None):
        idx = self.state.get("step_index", 0)
        step = self.current_step()
        # Обновляем context, если input_data есть
        if input_data:
            self.context.update(input_data)
        # Проверяем условие (condition) и ветвления (branches)
        if step:
            cond = step.get("condition")
            branches = step.get("branches")
            next_step = step.get("next_step")
            if cond and branches:
                try:
                    # Безопасно: только context доступен
                    result = eval(cond, {"context": self.context})
                except Exception as e:
                    logger.error({"event": "condition_eval_error", "error": str(e), "step": idx})
                    result = False
                branch_key = "if" if result else "else"
                next_idx = branches.get(branch_key)
                if next_idx is not None and 0 <= next_idx < len(self.steps):
                    self.state["step_index"] = next_idx
                    logger.info({"event": "branch", "result": result, "to": next_idx, "context": self.context})
                    return self.steps[next_idx]
            elif next_step is not None:
                if 0 <= next_step < len(self.steps):
                    self.state["step_index"] = next_step
                    logger.info({"event": "next_step_explicit", "to": next_step, "context": self.context})
                    return self.steps[next_step]
        # По умолчанию — линейный переход
        if idx + 1 < len(self.steps):
            self.state["step_index"] = idx + 1
            logger.info({"event": "next_step_linear", "to": self.state["step_index"], "context": self.context})
            return self.steps[self.state["step_index"]]
        logger.info({"event": "end_of_scenario", "context": self.context})
        return None

    def serialize(self):
        return json.dumps({"scenario": self.scenario, "state": self.state, "context": self.context})

    @classmethod
    def from_json(cls, data):
        obj = json.loads(data)
        return cls(obj["scenario"], obj["state"], obj.get("context"))

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