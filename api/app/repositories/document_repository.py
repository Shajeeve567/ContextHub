from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.app.models.document import Document
from api.app.schemas.document import DocumentCreate, DocumentCreateFromFile


async def create_document(db: AsyncSession, payload: DocumentCreate) -> Document:
    document = Document(
        user_id=payload.user_id,
        title=payload.title,
        raw_content=payload.raw_content,
        source_type=payload.source_type,
        status="pending",
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


async def create_document_from_files(db: AsyncSession, user_id, title, raw_content, file_name, file_size, mime_type, file_path) -> Document:
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
    await db.commit()
    await db.refresh(document)
    return document


async def list_documents_for_user(db: AsyncSession, user_id: str) -> List[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())


async def get_document_by_id(db: AsyncSession, document_id: str, user_id: Optional[str] = None) -> Optional[Document]:
    statement = select(Document).where(Document.id == document_id)
    if user_id:
        statement = statement.where(Document.user_id == user_id)

    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def update_document_status(db: AsyncSession, document: Document, status: str) -> Document:
    document.status = status
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document