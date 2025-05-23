from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List

class Agent(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = None
    scenario_id: Optional[str] = None
    plugins: Optional[List[str]] = Field(default_factory=list)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    initial_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    extra: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        extra = "allow"
