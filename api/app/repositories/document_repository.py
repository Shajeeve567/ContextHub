from typing import List, Optional

from sqlalchemy.orm import Session

from api.app.models.document import Document
from api.app.schemas.document import DocumentCreate, DocumentCreateFromFile


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


def create_document_from_files(db: Session, user_id, title, raw_content, file_name, file_size, mime_type, file_path) -> Document:
    document = Document(
        user_id=user_id,
        title=title,
        raw_content=raw_content,
        source_type="pdf_upload",
        status="pending",
        file_name=file_name,
        file_size=file_size,
        mime_type=mime_type,
        file_path=file_path,
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