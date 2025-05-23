from pydantic import BaseModel, Field, root_validator
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal, Union

class StepBase(BaseModel):
    id: str
    type: str
    params: Optional[Dict[str, Any]] = None
    result_var: Optional[str] = None
    next_step: Optional[str] = None

class PluginActionStep(StepBase):
    type: Literal["plugin_action"]
    plugin: str
    action: str
    params: Dict[str, Any]
    result_var: str

class TelegramSendMessageStep(StepBase):
    type: Literal["telegram_send_message"]
    params: Dict[str, Any]

class BranchStep(StepBase):
    type: Literal["branch"]
    condition: str  # шаблон-условие
    true_next: str
    false_next: str

class LogStep(StepBase):
    type: Literal["log"]
    params: Dict[str, Any]

class StartStep(StepBase):
    type: Literal["start"]

class EndStep(StepBase):
    type: Literal["end"]

class SwitchScenarioStep(StepBase):
    type: Literal["switch_scenario"]
    params: Dict[str, Any]

class InputStep(StepBase):
    type: Literal["input"]
    params: Dict[str, Any]

ScenarioStep = Union[
    PluginActionStep,
    TelegramSendMessageStep, 
    BranchStep,
    LogStep,
    StartStep,
    EndStep,
    InputStep,
    SwitchScenarioStep
]

class Scenario(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    scenario_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    initial_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    steps: List[ScenarioStep] = Field(default_factory=list)
    bpmn_xml: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    extra: Optional[Dict[str, Any]] = None
    required_plugins: Optional[List[str]] = None

    class Config:
        from_attributes = True
        populate_by_name = True
