from typing import List
from api.app.core.database import get_db
from api.app.repositories.session_repository import (
    create_session,
    get_session_by_id,
    list_sessions_for_project,
    get_incomplete_sessions,
    update_checkpoint,
    complete_session,
    mark_session_incomplete,
)
from api.app.repositories.project_repository import get_project_by_id
from api.app.schemas.session import (
    SessionCreate,
    SessionComplete,
    SessionCheckpointUpdate,
    SessionResponse,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(payload: SessionCreate, db: AsyncSession = Depends(get_db)):
    project = await get_project_by_id(db, project_id=payload.project_id, user_id=payload.user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await create_session(db, payload)


@router.get("", response_model=List[SessionResponse])
async def list_project_sessions(
    project_id: str = Query(..., min_length=1),
    user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    return await list_sessions_for_project(db, project_id=project_id, user_id=user_id)


@router.get("/incomplete", response_model=List[SessionResponse])
async def check_incomplete_sessions(
    project_id: str = Query(..., min_length=1),
    user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    return await get_incomplete_sessions(db, project_id=project_id, user_id=user_id)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    session = await get_session_by_id(db, session_id=session_id, user_id=user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/{session_id}/checkpoint", response_model=SessionResponse)
async def update_session_checkpoint(
    session_id: str,
    payload: SessionCheckpointUpdate,
    user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    session = await get_session_by_id(db, session_id=session_id, user_id=user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Cannot update checkpoint on a non-active session")
    return await update_checkpoint(db, session, payload)


@router.post("/{session_id}/complete", response_model=SessionResponse)
async def complete_session_endpoint(
    session_id: str,
    payload: SessionComplete,
    user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    session = await get_session_by_id(db, session_id=session_id, user_id=user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Session is already completed or incomplete")
    return await complete_session(db, session, payload)


@router.patch("/{session_id}/abandon", response_model=SessionResponse)
async def abandon_session(
    session_id: str,
    user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    session = await get_session_by_id(db, session_id=session_id, user_id=user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Session is not active")
    return await mark_session_incomplete(db, session)