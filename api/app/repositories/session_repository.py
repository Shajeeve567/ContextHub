from typing import List, Optional
from sqlalchemy.orm import Session
from api.app.models.session import Session as SessionModel
from api.app.schemas.session import SessionCreate, SessionComplete, SessionCheckpointUpdate


def create_session(db: Session, payload: SessionCreate) -> SessionModel:
    session = SessionModel(
        project_id=payload.project_id,
        user_id=payload.user_id,
        llm_used=payload.llm_used,
        status="active",
        checkpoint_reached="START",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_by_id(db: Session, session_id: str, user_id: str) -> Optional[SessionModel]:
    return (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id, SessionModel.user_id == user_id)
        .first()
    )


def list_sessions_for_project(db: Session, project_id: str, user_id: str) -> List[SessionModel]:
    return (
        db.query(SessionModel)
        .filter(SessionModel.project_id == project_id, SessionModel.user_id == user_id)
        .order_by(SessionModel.created_at.desc())
        .all()
    )


def get_last_completed_session(db: Session, project_id: str, user_id: str) -> Optional[SessionModel]:
    return (
        db.query(SessionModel)
        .filter(
            SessionModel.project_id == project_id,
            SessionModel.user_id == user_id,
            SessionModel.status == "complete",
        )
        .order_by(SessionModel.created_at.desc())
        .first()
    )


def get_incomplete_sessions(db: Session, project_id: str, user_id: str) -> List[SessionModel]:
    return (
        db.query(SessionModel)
        .filter(
            SessionModel.project_id == project_id,
            SessionModel.user_id == user_id,
            SessionModel.status == "active",
        )
        .order_by(SessionModel.created_at.asc())
        .all()
    )


def update_checkpoint(db: Session, session: SessionModel, payload: SessionCheckpointUpdate) -> SessionModel:
    session.checkpoint_reached = payload.checkpoint_reached
    db.commit()
    db.refresh(session)
    return session


def complete_session(db: Session, session: SessionModel, payload: SessionComplete) -> SessionModel:
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

    db.commit()
    db.refresh(session)
    return session


def mark_session_incomplete(db: Session, session: SessionModel) -> SessionModel:
    session.status = "incomplete"
    db.commit()
    db.refresh(session)
    return session