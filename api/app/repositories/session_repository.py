from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.app.models.session import Session as SessionModel
from api.app.schemas.session import SessionCreate, SessionComplete, SessionCheckpointUpdate


async def create_session(db: AsyncSession, payload: SessionCreate) -> SessionModel:
    session = SessionModel(
        project_id=payload.project_id,
        user_id=payload.user_id,
        llm_used=payload.llm_used,
        status="active",
        checkpoint_reached="START",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session_by_id(db: AsyncSession, session_id: str, user_id: str) -> Optional[SessionModel]:
    result = await db.execute(
        select(SessionModel).where(SessionModel.id == session_id, SessionModel.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def list_sessions_for_project(db: AsyncSession, project_id: str, user_id: str) -> List[SessionModel]:
    result = await db.execute(
        select(SessionModel)
        .where(SessionModel.project_id == project_id, SessionModel.user_id == user_id)
        .order_by(SessionModel.created_at.desc())
    )
    return list(result.scalars().all())


async def get_last_completed_session(db: AsyncSession, project_id: str, user_id: str) -> Optional[SessionModel]:
    result = await db.execute(
        select(SessionModel)
        .where(
            SessionModel.project_id == project_id,
            SessionModel.user_id == user_id,
            SessionModel.status == "complete",
        )
        .order_by(SessionModel.created_at.desc())
        .limit(1)
    )
    return result.scalars().first()

async def get_incomplete_sessions(db: AsyncSession, project_id: str, user_id: str) -> List[SessionModel]:
    result = await db.execute(
        select(SessionModel)
        .where(
            SessionModel.project_id == project_id,
            SessionModel.user_id == user_id,
            SessionModel.status == "active",
        )
        .order_by(SessionModel.created_at.asc())
    )
    return list(result.scalars().all())


async def update_checkpoint(db: AsyncSession, session: SessionModel, payload: SessionCheckpointUpdate) -> SessionModel:
    session.checkpoint_reached = payload.checkpoint_reached
    await db.commit()
    await db.refresh(session)
    return session


async def complete_session(db: AsyncSession, session: SessionModel, payload: SessionComplete) -> SessionModel:
    session.status = "complete"
    session.checkpoint_reached = "COMPLETE"

    session.worked_on = payload.summary.worked_on
    session.progress = payload.summary.progress
    session.decisions = payload.summary.decisions
    session.pending = payload.summary.pending
    session.blockers = payload.summary.blockers
    session.next_session_briefing = payload.summary.next_session_briefing

    session.llm_used = payload.llm_used
    session.session_duration_minutes = payload.session_duration_minutes
    session.documents_referenced = payload.documents_referenced

    await db.commit()
    await db.refresh(session)
    return session


async def mark_session_incomplete(db: AsyncSession, session: SessionModel) -> SessionModel:
    session.status = "incomplete"
    await db.commit()
    await db.refresh(session)
    return session