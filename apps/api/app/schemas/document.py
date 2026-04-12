from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=255)
    raw_content: str = Field(..., min_length=1)
    source_type: str = Field(default="manual_note", min_length=1, max_length=50)

class DocumentCreateFromFile(BaseModel):
    user_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=255)

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    raw_content: str
    source_type: str
    status: str
    created_at: datetime
    updated_at: datetime


class DocumentProcessResponse(BaseModel):
    document_id: str
    chunks_created: int
    status: str