from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.app.models.project_decisions import ProjectDecision
from api.app.models.session import Session as SessionModel


_SESSION_BASE = select(SessionModel).options(selectinload(SessionModel.decision_rows))


async def create_session(
    db: AsyncSession,
    project_id: str,
    user_id: str,
    llm_used: Optional[str] = None,
) -> SessionModel:
    session = SessionModel(
        project_id=project_id,
        user_id=user_id,
        llm_used=llm_used,
        status="active",
        checkpoint_reached="START",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    result = await db.execute(_SESSION_BASE.where(SessionModel.id == session.id))
    return result.scalar_one()


async def get_session_by_id(db: AsyncSession, session_id: str, user_id: Optional[str] = None) -> Optional[SessionModel]:
    stmt = _SESSION_BASE.where(SessionModel.id == session_id)
    if user_id:
        stmt = stmt.where(SessionModel.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_sessions_for_project(db: AsyncSession, project_id: str, user_id: str) -> List[SessionModel]:
    result = await db.execute(
        _SESSION_BASE
        .where(SessionModel.project_id == project_id, SessionModel.user_id == user_id)
        .order_by(SessionModel.created_at.desc())
    )
    return list(result.scalars().all())


async def get_last_completed_session(db: AsyncSession, project_id: str, user_id: str) -> Optional[SessionModel]:
    result = await db.execute(
        _SESSION_BASE
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
        _SESSION_BASE
        .where(
            SessionModel.project_id == project_id,
            SessionModel.user_id == user_id,
            SessionModel.status == "active",
        )
        .order_by(SessionModel.created_at.asc())
    )
    return list(result.scalars().all())


async def update_checkpoint(
    db: AsyncSession,
    session: SessionModel,
    checkpoint_reached: str,
) -> SessionModel:
    session.checkpoint_reached = checkpoint_reached
    await db.commit()
    await db.refresh(session)
    result = await db.execute(_SESSION_BASE.where(SessionModel.id == session.id))
    return result.scalar_one()


async def complete_session(
    db: AsyncSession,
    session: SessionModel,
    worked_on: str,
    progress: str,
    decisions: list[str],
    pending: list[str],
    blockers: list[str],
    next_session_briefing: str,
    llm_used: Optional[str] = None,
    session_duration_minutes: Optional[int] = None,
    documents_referenced: Optional[list[str]] = None,
) -> SessionModel:
    session.status = "complete"
    session.checkpoint_reached = "COMPLETE"

    session.worked_on = worked_on
    session.progress = progress
    for idx, d in enumerate(decisions or [], start=1):
        pd = ProjectDecision(
            session_id=session.id,
            project_id=session.project_id,
            user_id=session.user_id,
            decision_text=d,
            decision_order=idx,
        )
        db.add(pd)
    session.pending = pending
    session.blockers = blockers
    session.next_session_briefing = next_session_briefing

    session.llm_used = llm_used
    session.session_duration_minutes = session_duration_minutes
    session.documents_referenced = documents_referenced or []

    await db.commit()
    await db.refresh(session)
    result = await db.execute(_SESSION_BASE.where(SessionModel.id == session.id))
    return result.scalar_one()


async def mark_session_incomplete(db: AsyncSession, session: SessionModel) -> SessionModel:
    session.status = "incomplete"
    await db.commit()
    await db.refresh(session)
    result = await db.execute(_SESSION_BASE.where(SessionModel.id == session.id))
    return result.scalar_one()