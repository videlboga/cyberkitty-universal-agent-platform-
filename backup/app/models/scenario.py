from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class Scenario(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    bpmn_xml: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    extra: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        extra = "allow"
