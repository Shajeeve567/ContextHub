from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class InteractionCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    user_message: str = Field(..., min_length=1)
    ai_response: str = Field(..., min_length=1)
    model_used: Optional[str] = None
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    duration_ms: Optional[int] = None


class InteractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: Optional[str] = None
    user_id: str
    user_message: str
    ai_response: str
    model_used: Optional[str] = None
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    duration_ms: Optional[int] = None
    created_at: datetime
