from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    project_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    llm_used: Optional[str] = None


class SessionCheckpointUpdate(BaseModel):
    checkpoint_reached: str = Field(..., min_length=1)


class SessionLog(BaseModel):
    worked_on: str = Field(..., min_length=1)
    progress: str = Field(..., min_length=1)
    decisions: List[str] = Field(default_factory=list)
    pending: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)
    next_session_briefing: str = Field(..., min_length=1)


class SessionComplete(BaseModel):
    summary: SessionLog
    llm_used: Optional[str] = None
    session_duration_minutes: Optional[int] = None
    documents_referenced: List[str] = Field(default_factory=list)


class SessionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    project_id: str
    user_id: str
    status: str
    checkpoint_reached: str
    worked_on: Optional[str] = None
    progress: Optional[str] = None
    decisions: List[str] = []
    pending: List[str] = []
    blockers: List[str] = []
    next_session_briefing: Optional[str] = None
    llm_used: Optional[str] = None
    session_duration_minutes: Optional[int] = None
    documents_referenced: List[str] = []
    created_at: datetime
    updated_at: datetime