from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.app.core.database import get_db
from api.app.schemas.memory import MemoryCreate, MemoryResponse, MemorySearchResult
from api.app.services.memory_service import MemoryService

router = APIRouter(prefix="/memories", tags=["memories"])


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    payload: MemoryCreate,
    db: AsyncSession = Depends(get_db),
):
    service = MemoryService()
    return await service.create_memory(db, payload)


@router.get("", response_model=List[MemoryResponse])
async def list_memories(
    user_id: str = Query(..., min_length=1),
    memory_type: str = Query(None, max_length=30),
    project_id: str = Query(None, min_length=1),
    db: AsyncSession = Depends(get_db),
):
    from api.app.repositories import memory_repository

    if memory_type:
        return await memory_repository.get_memories_by_type(db, user_id, memory_type, project_id=project_id)
    return await memory_repository.list_memories(db, user_id, project_id=project_id)


@router.get("/search", response_model=List[MemorySearchResult])
async def search_memories(
    user_id: str = Query(..., min_length=1),
    q: str = Query(..., min_length=1),
    top_k: int = Query(default=10, ge=1, le=50),
    project_id: str = Query(None, min_length=1),
    db: AsyncSession = Depends(get_db),
):
    service = MemoryService()
    return await service.search_memories(db, user_id, q, top_k, project_id=project_id)


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_db),
):
    from api.app.repositories import memory_repository

    memory = await memory_repository.get_memory_by_id(db, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return MemoryResponse.model_validate(memory)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = MemoryService()
    deleted = await service.delete_memory(db, memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
