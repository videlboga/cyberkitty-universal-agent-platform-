import pytest
from app.core.state_machine import ScenarioStateMachine

def test_state_machine_linear():
    scenario = {
        "name": "Test Scenario",
        "steps": [
            {"type": "message", "text": "Step 1"},
            {"type": "message", "text": "Step 2"},
            {"type": "message", "text": "Step 3"},
        ]
    }
    sm = ScenarioStateMachine(scenario)
    # Первый шаг
    assert sm.current_step()["text"] == "Step 1"
    # Переход к следующему шагу
    step2 = sm.next_step()
    assert step2["text"] == "Step 2"
    # Ещё раз
    step3 = sm.next_step()
    assert step3["text"] == "Step 3"
    # После последнего шага — None
    assert sm.next_step() is None
    # current_step остаётся на последнем
    assert sm.current_step()["text"] == "Step 3"

def test_state_machine_serialize():
    scenario = {
        "name": "Test Scenario",
        "steps": [
            {"type": "message", "text": "Step 1"},
            {"type": "message", "text": "Step 2"},
        ]
    }
    sm = ScenarioStateMachine(scenario)
    sm.next_step()  # step_index = 1
    data = sm.serialize()
    sm2 = ScenarioStateMachine.from_json(data)
    assert sm2.current_step()["text"] == "Step 2"
    assert sm2.state["step_index"] == 1 

def test_trigger_command():
    scenario = {"name": "Test", "steps": []}
    sm = ScenarioStateMachine(scenario)
    result = sm.trigger_command("start", {"foo": 1})
    assert result["status"] == "triggered"
    assert result["type"] == "command"
    assert result["command"] == "start"

def test_trigger_event():
    scenario = {"name": "Test", "steps": []}
    sm = ScenarioStateMachine(scenario)
    result = sm.trigger_event("user_joined", {"user": "alice"})
    assert result["status"] == "triggered"
    assert result["type"] == "event"
    assert result["event"] == "user_joined"

def test_trigger_schedule():
    scenario = {"name": "Test", "steps": []}
    sm = ScenarioStateMachine(scenario)
    result = sm.trigger_schedule("every_day", {"time": "10:00"})
    assert result["status"] == "triggered"
    assert result["type"] == "schedule"

def test_branching_condition_if():
    scenario = {
        "name": "Branch Test",
        "steps": [
            {"type": "input", "text": "Введите число", "next_step": 1},
            {
                "type": "branch",
                "condition": "context['x'] > 0",
                "branches": {"if": 2, "else": 3},
                "text": "Проверка x"
            },
            {"type": "message", "text": "x положительное"},
            {"type": "message", "text": "x не положительное"},
        ]
    }
    sm = ScenarioStateMachine(scenario)
    sm.next_step({"x": 5})  # step 0 -> 1, context['x'] = 5
    step = sm.next_step()     # step 1: condition -> branches['if'] (2)
    assert step["text"] == "x положительное"

def test_branching_condition_else():
    scenario = {
        "name": "Branch Test",
        "steps": [
            {"type": "input", "text": "Введите число", "next_step": 1},
            {
                "type": "branch",
                "condition": "context['x'] > 0",
                "branches": {"if": 2, "else": 3},
                "text": "Проверка x"
            },
            {"type": "message", "text": "x положительное"},
            {"type": "message", "text": "x не положительное"},
        ]
    }
    sm = ScenarioStateMachine(scenario)
    sm.next_step({"x": -1})  # step 0 -> 1, context['x'] = -1
    step = sm.next_step()      # step 1: condition -> branches['else'] (3)
    assert step["text"] == "x не положительное"

def test_context_persistence():
    scenario = {
        "name": "Context Test",
        "steps": [
            {"type": "input", "text": "Введите имя", "next_step": 1},
            {"type": "message", "text": "Привет, {name}!"},
        ]
    }
    sm = ScenarioStateMachine(scenario)
    sm.next_step({"name": "Алиса"})  # step 0 -> 1, context['name'] = 'Алиса'
    step = sm.current_step()
    assert sm.context["name"] == "Алиса"
    assert step["text"] == "Привет, {name}!" 