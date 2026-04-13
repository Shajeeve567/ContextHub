from typing import List

from pydantic import BaseModel, Field


class MemoryQueryRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    chunk_index: int
    chunk_text: str
    score: float


class MemoryQueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[RetrievedChunk]