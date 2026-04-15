from typing import List
from api.app.core.database import get_db
from api.app.repositories.project_repository import (
    create_project,
    get_project_by_id,
    list_projects_for_user,
    update_project,
    delete_project,
)
from api.app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_new_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db)):
    return await create_project(db, payload)


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    return await list_projects_for_user(db, user_id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project_by_id(db, project_id=project_id, user_id=user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_existing_project(
    project_id: str,
    payload: ProjectUpdate,
    user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project_by_id(db, project_id=project_id, user_id=user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await update_project(db, project, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_project(
    project_id: str,
    user_id: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project_by_id(db, project_id=project_id, user_id=user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await delete_project(db, project)