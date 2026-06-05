from pydantic import BaseModel
from datetime import datetime
import uuid

class RuleBase(BaseModel):
    rule_type: str
    rule_value: str
    is_active: bool

class RuleResponse(RuleBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RuleValueUpdate(BaseModel):
    rule_value: str

class RuleToggleResponse(BaseModel):
    id: uuid.UUID
    is_active: bool
    message: str
