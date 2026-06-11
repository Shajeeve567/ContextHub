from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class MemoryCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    memory_type: str = Field(..., min_length=1, max_length=30)
    content: str = Field(..., min_length=1)
    importance: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str = Field(default="extraction", max_length=50)
    meta_json: dict[str, Any] = Field(default_factory=dict)


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    session_id: Optional[str] = None
    memory_type: str
    content: str
    importance: float
    source: str
    access_count: int
    last_accessed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    meta_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class MemorySearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    content: str
    memory_type: str
    importance: float
    score: float
    created_at: datetime
