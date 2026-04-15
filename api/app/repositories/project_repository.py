from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.app.models.project import Project
from api.app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse


async def create_project(db: AsyncSession, payload: ProjectCreate) -> Project:
    project = Project(
        user_id=payload.user_id,
        name=payload.name,
        description=payload.description,
        current_goal=payload.current_goal,
        status="active",
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def get_project_by_id(db: AsyncSession, project_id: str, user_id: str) -> Optional[Project]:
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def list_projects_for_user(db: AsyncSession, user_id: str) -> List[Project]:
    result = await db.execute(
        select(Project)
        .where(Project.user_id == user_id)
        .order_by(Project.updated_at.desc())
    )
    return list(result.scalars().all())


async def update_project(db: AsyncSession, project: Project, payload: ProjectUpdate) -> Project:
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.current_goal is not None:
        project.current_goal = payload.current_goal
    if payload.status is not None:
        project.status = payload.status
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project: Project) -> None:
    db.delete(project)
    await db.commit()