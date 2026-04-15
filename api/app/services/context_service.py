from sqlalchemy.orm import Session
from app.repositories.project_repository import get_project_by_id
from app.repositories.session_repository import (
    get_last_completed_session,
    get_incomplete_sessions,
)


def get_project_context(db: Session, project_id: str, user_id: str) -> dict:
    project = get_project_by_id(db, project_id=project_id, user_id=user_id)
    if not project:
        return None

    incomplete_sessions = get_incomplete_sessions(db, project_id=project_id, user_id=user_id)
    last_session = get_last_completed_session(db, project_id=project_id, user_id=user_id)

    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "current_goal": project.current_goal,
            "status": project.status,
        },
        "incomplete_sessions": len(incomplete_sessions) > 0,
        "incomplete_session_count": len(incomplete_sessions),
        "last_session": {
            "worked_on": last_session.worked_on,
            "progress": last_session.progress,
            "decisions": last_session.decisions,
            "pending": last_session.pending,
            "blockers": last_session.blockers,
            "next_session_briefing": last_session.next_session_briefing,
            "llm_used": last_session.llm_used,
        } if last_session else None,
    }
