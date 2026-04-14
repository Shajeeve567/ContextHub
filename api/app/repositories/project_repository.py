from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse


def create_project(db: Session, payload: ProjectCreate) -> Project:
    project = Project(
        user_id=payload.user_id,
        name=payload.name,
        description=payload.description,
        current_goal=payload.current_goal,
        status="active",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project_by_id(db: Session, project_id: str, user_id: str) -> Optional[Project]:
    return (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == user_id)
        .first()
    )


def list_projects_for_user(db: Session, user_id: str) -> List[Project]:
    return (
        db.query(Project)
        .filter(Project.user_id == user_id)
        .order_by(Project.updated_at.desc())
        .all()
    )


def update_project(db: Session, project: Project, payload: ProjectUpdate) -> Project:
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.current_goal is not None:
        project.current_goal = payload.current_goal
    if payload.status is not None:
        project.status = payload.status
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()