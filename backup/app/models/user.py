from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Dict, Any

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    # Для любых дополнительных полей
    extra: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        extra = "allow"
