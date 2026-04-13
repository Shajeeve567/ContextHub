import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text, Integer
from sqlalchemy.orm import relationship

from api.app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    raw_content = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=False, default="manual_note")
    status = Column(String(20), nullable=False, default="pending")

    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


    # File data
    file_name = Column(String(255), nullable=True)        # original filename
    file_size = Column(Integer, nullable=True)            # bytes
    mime_type = Column(String(100), nullable=True)        # application/pdf
    file_path = Column(String(500), nullable=True)        # where the file is stored on disk/cloud

    chunks = relationship(
        "Chunk",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="Chunk.chunk_index",
    )