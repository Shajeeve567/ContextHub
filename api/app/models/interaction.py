import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from api.app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(String(36), nullable=False, index=True)

    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)

    model_used = Column(String(100), nullable=True)
    tokens_in = Column(Integer, nullable=True)
    tokens_out = Column(Integer, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    session = relationship("Session", back_populates="interactions")
