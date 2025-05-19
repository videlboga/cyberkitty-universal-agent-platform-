from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class Scenario(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    scenario_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    initial_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    steps: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    bpmn_xml: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    extra: Optional[Dict[str, Any]] = None
    required_plugins: Optional[List[str]] = None

    class Config:
        from_attributes = True
        populate_by_name = True
