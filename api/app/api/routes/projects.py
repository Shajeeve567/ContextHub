from typing import List
from app.core.database import get_db
from app.repositories.project_repository import (
    create_project,
    get_project_by_id,
    list_projects_for_user,
    update_project,
    delete_project,
)
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_new_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    return create_project(db, payload)


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    user_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    return list_projects_for_user(db, user_id)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    user_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    project = get_project_by_id(db, project_id=project_id, user_id=user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_existing_project(
    project_id: str,
    payload: ProjectUpdate,
    user_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    project = get_project_by_id(db, project_id=project_id, user_id=user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return update_project(db, project, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_project(
    project_id: str,
    user_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    project = get_project_by_id(db, project_id=project_id, user_id=user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    delete_project(db, project)