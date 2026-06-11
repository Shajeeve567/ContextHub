from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class UserPreferenceUpdate(BaseModel):
    preferences: dict[str, Any] = Field(..., description="User preferences as key-value pairs")


class UserPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    preferences: dict[str, Any]
    created_at: datetime
    updated_at: datetime
