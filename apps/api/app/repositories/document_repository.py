from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate


def create_document(db: Session, payload: DocumentCreate) -> Document:
    document = Document(
        user_id=payload.user_id,
        title=payload.title,
        raw_content=payload.raw_content,
        source_type=payload.source_type,
        status="pending",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def list_documents_for_user(db: Session, user_id: str) -> List[Document]:
    return (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .all()
    )


def get_document_by_id(db: Session, document_id: str, user_id: Optional[str] = None) -> Optional[Document]:
    query = db.query(Document).filter(Document.id == document_id)
    if user_id:
        query = query.filter(Document.user_id == user_id)
    return query.first()


def update_document_status(db: Session, document: Document, status: str) -> Document:
    document.status = status
    db.add(document)
    db.commit()
    db.refresh(document)
    return document