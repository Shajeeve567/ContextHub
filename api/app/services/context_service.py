from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from api.app.repositories.project_repository import get_project_by_id
from api.app.repositories.session_repository import (
    get_last_completed_session,
    get_incomplete_sessions,
)


async def get_project_context(db: AsyncSession, project_id: str, user_id: str) -> Optional[dict]:
    project = await get_project_by_id(db, project_id=project_id, user_id=user_id)
    if not project:
        return None

    incomplete_sessions = await get_incomplete_sessions(db, project_id=project_id, user_id=user_id)
    last_session = await get_last_completed_session(db, project_id=project_id, user_id=user_id)

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
