import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)

    # session state
    status = Column(String(50), nullable=False, default="active")  # active, incomplete, complete
    checkpoint_reached = Column(String(50), nullable=False, default="START")

    # summary block — written by LLM at end of session
    worked_on = Column(Text, nullable=True)
    progress = Column(Text, nullable=True)
    decisions = Column(JSON, nullable=False, default=list)
    pending = Column(JSON, nullable=False, default=list)
    blockers = Column(JSON, nullable=False, default=list)
    next_session_briefing = Column(Text, nullable=True)

    # metadata block
    llm_used = Column(String(100), nullable=True)
    session_duration_minutes = Column(Integer, nullable=True)
    documents_referenced = Column(JSON, nullable=False, default=list)

    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    project = relationship("Project", back_populates="sessions")